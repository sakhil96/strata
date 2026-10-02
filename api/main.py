"""STRATA API — FastAPI application serving the governed supply chain ontology.

Serves both the API endpoints and the Next.js static export from a single container.
"""

from __future__ import annotations

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes.ask import router as ask_router
from .routes.query import router as query_router
from .routes.meta import router as meta_router
from .routes.glossary import router as glossary_router
from .routes.lineage import router as lineage_router
from .routes.audit import router as audit_router
from .routes.eval_report import router as eval_router
from .routes.health import router as health_router
from .security import add_security_headers, RateLimiter

logger = logging.getLogger("strata.api")

rate_limiter = RateLimiter(requests_per_minute=60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("strata_api_starting")
    yield
    logger.info("strata_api_stopping")


app = FastAPI(
    title="STRATA API",
    description="Governed supply chain ontology API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOWED_ORIGIN", "*")],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    start = time.time()

    rate_limiter.check(request)

    response: Response = await call_next(request)
    latency_ms = int((time.time() - start) * 1000)

    add_security_headers(response)
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "latency_ms": latency_ms,
        },
    )
    return response


app.include_router(ask_router, prefix="/api")
app.include_router(query_router, prefix="/api")
app.include_router(meta_router, prefix="/api")
app.include_router(glossary_router, prefix="/api")
app.include_router(lineage_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(eval_router, prefix="/api")
app.include_router(health_router)

# Serve Next.js static export
static_dir = Path(__file__).resolve().parent.parent / "web" / "out"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
