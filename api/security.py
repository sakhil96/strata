from __future__ import annotations

import base64
import hashlib
import re
import threading
import time
from collections import OrderedDict
from pathlib import Path

from fastapi import HTTPException, Request

USER_HEADER = "sf-context-current-user"
INLINE_SCRIPT = re.compile(rb"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.S)
BASE_HEADERS = {
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
}


def content_security_policy(script_hashes: tuple[str, ...] = ()) -> str:
    # Next's static export inlines its flight data; we allow exactly those script bodies by hash.
    # React renders style attributes for motion; attributes may be inline, style elements may not.
    scripts = " ".join(["'self'", *(f"'sha256-{h}'" for h in script_hashes)])
    return ("default-src 'self'; "
            f"script-src {scripts}; "
            "style-src 'self'; style-src-attr 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; "
            "object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; "
            "upgrade-insecure-requests")


def inline_script_hashes(html: bytes) -> tuple[str, ...]:
    return tuple(sorted({base64.b64encode(hashlib.sha256(body).digest()).decode()
                         for body in INLINE_SCRIPT.findall(html) if body.strip()}))


class PageHashes:
    def __init__(self, root: Path):
        self.root = root
        self._cache: dict[Path, tuple[float, tuple[str, ...]]] = {}

    def for_path(self, path: Path) -> tuple[str, ...]:
        mtime = path.stat().st_mtime
        hit = self._cache.get(path)
        if not hit or hit[0] != mtime:
            hit = (mtime, inline_script_hashes(path.read_bytes()))
            self._cache[path] = hit
        return hit[1]


class RateLimiter:
    """Sliding window per signed-in user; bounded so a flood of identities cannot grow it."""

    def __init__(self, per_minute: int = 60, max_keys: int = 10_000):
        self.per_minute = per_minute
        self.max_keys = max_keys
        self._hits: OrderedDict[str, list[float]] = OrderedDict()
        self._lock = threading.Lock()

    def check(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            hits = [t for t in self._hits.pop(key, []) if now - t < 60]
            if len(hits) >= self.per_minute:
                self._hits[key] = hits
                raise HTTPException(status_code=429, detail="Too many requests from this user; wait a minute and retry.",
                                    headers={"Retry-After": str(int(60 - (now - hits[0])) + 1)})
            hits.append(now)
            self._hits[key] = hits
            while len(self._hits) > self.max_keys:
                self._hits.popitem(last=False)


def caller_identity(request: Request) -> str:
    user = request.headers.get(USER_HEADER)
    if user and re.fullmatch(r"[A-Za-z0-9_.@$-]{1,128}", user):
        return user.upper()
    return "LOCAL_DEVELOPER" if request.app.state.backend_mode == "local" else "ANONYMOUS"
