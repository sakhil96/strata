from __future__ import annotations

import json
import logging
import os
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response

from .backend import get_backend
from .routes import answers, catalogue, operations
from .security import BASE_HEADERS, PageHashes, RateLimiter, content_security_policy

WEB_OUT = Path(os.getenv("SCM_WEB_OUT", Path(__file__).resolve().parent.parent / "web" / "out"))


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {"ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"), "level": record.levelname,
                 "logger": record.name, "event": record.getMessage()}
        for key in ("request_id", "method", "path", "status", "latency_ms", "user", "mode"):
            if hasattr(record, key):
                entry[key] = getattr(record, key)
        return json.dumps(entry)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger("strata")
    root.handlers = [handler]
    root.setLevel(os.getenv("SCM_LOG_LEVEL", "INFO"))
    root.propagate = False


configure_logging()
log = logging.getLogger("strata.api")

app = FastAPI(title="STRATA API", version="1.0.0",
              description="Governed supply chain metrics. Every answer carries its definition, query hash, "
                          "the SEMANTIC_VIEW() SQL that ran, its lineage and the role it ran under.")
app.state.limiter = RateLimiter(per_minute=int(os.getenv("SCM_RATE_PER_MINUTE", "60")))
app.state.default_role = os.getenv("SCM_DEFAULT_ROLE", "EXECUTIVE_ROLE")
app.state.backend_mode = os.getenv("SCM_BACKEND", "local")
pages = PageHashes(WEB_OUT)


@app.middleware("http")
async def envelope(request: Request, call_next):
    request.state.request_id = request.headers.get("x-request-id", uuid.uuid4().hex[:12])[:32]
    started = time.perf_counter()
    try:
        response: Response = await call_next(request)
    except Exception:
        log.exception("unhandled_error", extra={"request_id": request.state.request_id, "path": request.url.path})
        response = JSONResponse(status_code=500, content={
            "error": "internal_error",
            "message": "Something failed on our side. Quote this request id when you report it.",
            "request_id": request.state.request_id})
    for header, value in BASE_HEADERS.items():
        response.headers.setdefault(header, value)
    response.headers.setdefault("Content-Security-Policy", content_security_policy())
    response.headers["X-Request-ID"] = request.state.request_id
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    log.info("request", extra={"request_id": request.state.request_id, "method": request.method,
                               "path": request.url.path, "status": response.status_code,
                               "latency_ms": int((time.perf_counter() - started) * 1000)})
    return response


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc: RequestValidationError):
    problems = [{"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"error": "invalid_request", "problems": problems,
                                                  "request_id": request.state.request_id})


@app.exception_handler(HTTPException)
async def http_problem(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, headers=exc.headers,
                        content={"error": "request_refused", "message": exc.detail,
                                 "request_id": request.state.request_id})


for module in (answers, catalogue, operations):
    app.include_router(module.router, prefix="/api")


@app.get("/health", tags=["probes"], summary="Readiness: the backend can answer")
def readiness():
    try:
        return get_backend().health()
    except Exception as exc:
        log.warning("not_ready", extra={"mode": app.state.backend_mode})
        return JSONResponse(status_code=503, content={"status": "not_ready", "reason": exc.__class__.__name__})


@app.get("/live", tags=["probes"], summary="Liveness: the process is serving")
def liveness():
    return {"status": "alive"}


@app.get("/{path:path}", include_in_schema=False)
def static_page(path: str):
    if not WEB_OUT.exists():
        return JSONResponse(status_code=404, content={"error": "no_front_end",
                                                      "message": "Build the front end with `make web`."})
    root = WEB_OUT.resolve()
    target = (root / path).resolve()
    if root not in target.parents and target != root:
        return JSONResponse(status_code=404, content={"error": "not_found"})
    for candidate in (target, target.with_suffix(".html"), target / "index.html"):
        if candidate.is_file():
            response = FileResponse(candidate)
            if candidate.suffix == ".html":
                response.headers["Content-Security-Policy"] = content_security_policy(pages.for_path(candidate))
                response.headers["Cache-Control"] = "no-cache"
            elif "/_next/static/" in str(candidate):
                response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
            return response
    missing = root / "404.html"
    if missing.is_file():
        response = FileResponse(missing, status_code=404)
        response.headers["Content-Security-Policy"] = content_security_policy(pages.for_path(missing))
        return response
    return JSONResponse(status_code=404, content={"error": "not_found"})
