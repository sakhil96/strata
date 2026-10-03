"""The API as SPCS would present it to a browser, for a laptop pointed at a dev account.

SPCS ingress signs the caller in and adds Sf-Context-Current-User; locally nothing does, so this
adds it from SCM_PREVIEW_USER. The persona the dial starts on is SCM_DEFAULT_ROLE."""

from __future__ import annotations

import os

from api.main import app as strata
from api.security import USER_HEADER

USER = os.getenv("SCM_PREVIEW_USER", "PREVIEW_PLANNER").encode()


async def app(scope, receive, send):
    if scope["type"] == "http":
        headers = [(k, v) for k, v in scope["headers"] if k != USER_HEADER.encode()]
        scope = {**scope, "headers": [*headers, (USER_HEADER.encode(), USER)]}
    await strata(scope, receive, send)
