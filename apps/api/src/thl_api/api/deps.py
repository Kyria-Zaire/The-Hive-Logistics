from __future__ import annotations

from thl_api.config import get_settings
from thl_api.services.lead_submission import LeadSubmissionService
from thl_api.turnstile.httpx_client import HttpxTurnstileVerifier


def get_lead_submission_service() -> LeadSubmissionService:
    settings = get_settings()
    verifier = HttpxTurnstileVerifier(
        secret=settings.turnstile_secret_key or "",
        expected_hostname=settings.turnstile_expected_hostname or "",
    )
    return LeadSubmissionService(settings=settings, turnstile=verifier)
