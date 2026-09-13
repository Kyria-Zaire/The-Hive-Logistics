from __future__ import annotations

import json
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from thl_api.problems import (
    MALFORMED_REQUEST,
    PAYLOAD_TOO_LARGE,
    UNSUPPORTED_MEDIA,
    problem_response,
)

MAX_LEAD_BODY_BYTES = 65_536
_LEAD_POST_PATHS = frozenset({"/api/v1/quote-requests", "/api/v1/contact-messages"})


class LeadPostGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.method != "POST" or request.url.path not in _LEAD_POST_PATHS:
            return await call_next(request)

        content_type = request.headers.get("content-type", "")
        media = content_type.split(";", maxsplit=1)[0].strip().lower()
        if media != "application/json":
            return problem_response(
                request,
                status=415,
                problem_type=UNSUPPORTED_MEDIA,
                title="Type de contenu non supporté",
                code="UNSUPPORTED_MEDIA_TYPE",
                detail="Content-Type application/json requis.",
            )

        body = await request.body()
        if len(body) > MAX_LEAD_BODY_BYTES:
            return problem_response(
                request,
                status=413,
                problem_type=PAYLOAD_TOO_LARGE,
                title="Payload trop volumineux",
                code="PAYLOAD_TOO_LARGE",
            )

        if body:
            try:
                json.loads(body)
            except json.JSONDecodeError:
                return problem_response(
                    request,
                    status=400,
                    problem_type=MALFORMED_REQUEST,
                    title="Requête invalide",
                    code="MALFORMED_REQUEST",
                    detail="La requête n'a pas pu être lue.",
                )

        return await call_next(request)
