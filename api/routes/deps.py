from __future__ import annotations

import json
import os
import uuid
from functools import cache

from fastapi import HTTPException, Request

from ..backend import PERSONAS, Caller, get_backend
from ..security import caller_identity


@cache
def user_personas() -> dict[str, str]:
    """Signed-in user to persona role, from SCM_USER_PERSONAS (JSON). A user listed here always answers
    as that persona, whatever the dial sends; users not listed choose with the dial."""
    mapping = json.loads(os.getenv("SCM_USER_PERSONAS", "{}"))
    unknown = {r for r in mapping.values() if r not in PERSONAS}
    if unknown:
        raise RuntimeError(f"SCM_USER_PERSONAS maps to roles the service cannot assume: {sorted(unknown)}")
    return {u.upper(): r for u, r in mapping.items()}


def pinned_persona(request: Request) -> str | None:
    return user_personas().get(caller_identity(request))


def caller(request: Request, persona: str | None = None) -> Caller:
    role = pinned_persona(request) or persona or request.headers.get("x-persona") or request.app.state.default_role
    if role not in PERSONAS:
        raise HTTPException(status_code=422, detail=f"persona must be one of {', '.join(PERSONAS)}")
    request.app.state.limiter.check(caller_identity(request))
    return Caller(caller_identity(request), role, getattr(request.state, "request_id", uuid.uuid4().hex[:12]))


def backend():
    return get_backend()
