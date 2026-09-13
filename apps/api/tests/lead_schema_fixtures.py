from __future__ import annotations

from typing import Any

VALID_IDEMPOTENCY_KEY = "550e8400-e29b-41d4-a716-446655440000"

QUOTE_MINIMAL: dict[str, Any] = {
    "turnstile_token": "1234567890",
    "honeypot": "",
    "privacy_acknowledgement": True,
    "first_name": "Ada",
    "last_name": "Lovelace",
    "email": "ada@example.com",
    "phone": "+33 1 23 45 67 89",
    "service": "convoyage_premium",
    "departure_city": "Paris",
    "departure_postal_code": "75001",
    "arrival_city": "Lyon",
    "arrival_postal_code": "69001",
    "preferred_timing": {"kind": "exact_date", "exact_date": "2026-10-01"},
    "vehicle_category": "city_sedan",
    "vehicle_make": "Peugeot",
    "vehicle_model": "308",
    "vehicle_rolling": True,
}

QUOTE_OTHER: dict[str, Any] = {
    **QUOTE_MINIMAL,
    "vehicle_category": "other",
    "vehicle_category_other_detail": "Camionnette aménagée",
}

QUOTE_PERIOD_FULL: dict[str, Any] = {
    **QUOTE_MINIMAL,
    "preferred_timing": {"kind": "period", "period_text": "Semaine 42 2026"},
    "company": "ACME",
    "special_constraints": "Accès contraint",
    "additional_message": "Merci",
    "contact_preference": "email",
}

CONTACT_MINIMAL: dict[str, Any] = {
    "turnstile_token": "1234567890",
    "honeypot": "",
    "privacy_acknowledgement": True,
    "first_name": "Ada",
    "last_name": "Lovelace",
    "email": "ada@example.com",
    "subject": "information",
    "message": "Bonjour, une question.",
}

CONTACT_FULL: dict[str, Any] = {
    **CONTACT_MINIMAL,
    "phone": "+33 6 12 34 56 78",
    "company": "ACME",
}
