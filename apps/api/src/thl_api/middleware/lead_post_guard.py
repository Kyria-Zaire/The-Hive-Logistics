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


async def _read_body_from_receive(request: Request, limit: int) -> bytes | None:
    body = bytearray()
    more_body = True
    while more_body:
        message = await request.receive()
        if message["type"] == "http.disconnect":
            break
        chunk = message.get("body", b"")
        if chunk:
            body.extend(chunk)
            if len(body) > limit:
                return None
        more_body = message.get("more_body", False)
    return bytes(body)


def _replay_request_body(request: Request, body: bytes) -> None:
    sent = False

    async def receive() -> dict[str, object]:
        nonlocal sent
        if sent:
            return {"type": "http.request", "body": b"", "more_body": False}
        sent = True
        return {"type": "http.request", "body": body, "more_body": False}

    request._receive = receive  # noqa: SLF001
    request._body = body  # noqa: SLF001
    request._stream_consumed = False  # noqa: SLF001


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

        content_length_raw = request.headers.get("content-length")
        if content_length_raw is not None:
            try:
                declared = int(content_length_raw)
            except ValueError:
                declared = None
            if declared is not None and declared > MAX_LEAD_BODY_BYTES:
                return problem_response(
                    request,
                    status=413,
                    problem_type=PAYLOAD_TOO_LARGE,
                    title="Payload trop volumineux",
                    code="PAYLOAD_TOO_LARGE",
                )

        body = await _read_body_from_receive(request, MAX_LEAD_BODY_BYTES)
        if body is None:
            return problem_response(
                request,
                status=413,
                problem_type=PAYLOAD_TOO_LARGE,
                title="Payload trop volumineux",
                code="PAYLOAD_TOO_LARGE",
            )

        if not body:
            return problem_response(
                request,
                status=400,
                problem_type=MALFORMED_REQUEST,
                title="Requête invalide",
                code="MALFORMED_REQUEST",
                detail="La requête n'a pas pu être lue.",
            )

        try:
            body.decode("utf-8")
        except UnicodeDecodeError:
            return problem_response(
                request,
                status=400,
                problem_type=MALFORMED_REQUEST,
                title="Requête invalide",
                code="MALFORMED_REQUEST",
                detail="La requête n'a pas pu être lue.",
            )

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

        _replay_request_body(request, body)
        return await call_next(request)
