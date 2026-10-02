from __future__ import annotations

import uuid

from fastapi import HTTPException, Request

from ..backend import PERSONAS, Caller, get_backend
from ..security import caller_identity


def caller(request: Request, persona: str | None = None) -> Caller:
    role = persona or request.headers.get("x-persona") or request.app.state.default_role
    if role not in PERSONAS:
        raise HTTPException(status_code=422, detail=f"persona must be one of {', '.join(PERSONAS)}")
    request.app.state.limiter.check(caller_identity(request))
    return Caller(caller_identity(request), role, getattr(request.state, "request_id", uuid.uuid4().hex[:12]))


def backend():
    return get_backend()
