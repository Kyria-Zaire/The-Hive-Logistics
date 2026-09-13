from __future__ import annotations

import re
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

CORRELATION_HEADER = "X-Correlation-Id"
CORRELATION_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
MAX_CORRELATION_LENGTH = 64


def resolve_correlation_id(raw: str | None) -> str:
    if raw is None:
        return str(uuid.uuid4())
    if len(raw) > MAX_CORRELATION_LENGTH:
        return str(uuid.uuid4())
    if not CORRELATION_PATTERN.fullmatch(raw):
        return str(uuid.uuid4())
    return raw


def read_correlation_header(request: Request) -> str | None:
    values = request.headers.getlist(CORRELATION_HEADER)
    if len(values) != 1:
        return None
    return values[0]


class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        correlation_id = resolve_correlation_id(read_correlation_header(request))
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers[CORRELATION_HEADER] = correlation_id
        return response
