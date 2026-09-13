# ruff: noqa: E501
from __future__ import annotations

from dataclasses import dataclass

EXPECTED_PRIMARY_KEYS = {
    "leads": "pk_leads",
    "quote_request_details": "pk_quote_request_details",
    "contact_message_details": "pk_contact_message_details",
    "idempotency_records": "pk_idempotency_records",
    "notification_jobs": "pk_notification_jobs",
    "rate_limit_buckets": "pk_rate_limit_buckets",
}

BUSINESS_TABLES = (
    "leads",
    "quote_request_details",
    "contact_message_details",
    "idempotency_records",
    "notification_jobs",
    "rate_limit_buckets",
)

EXPECTED_CHECK_NAMES = frozenset(
    {
        "chk_leads_public_reference_format",
        "chk_leads_first_name_length",
        "chk_leads_last_name_length",
        "chk_leads_email_length",
        "chk_leads_company_length",
        "chk_leads_privacy_ack",
        "chk_leads_privacy_policy_version_length",
        "chk_leads_phone_quote",
        "chk_leads_phone_contact",
        "chk_quote_departure_city_length",
        "chk_quote_departure_postal_length",
        "chk_quote_arrival_city_length",
        "chk_quote_arrival_postal_length",
        "chk_quote_timing_exact_date",
        "chk_quote_timing_period",
        "chk_quote_vehicle_other",
        "chk_quote_vehicle_other_absent",
        "chk_quote_vehicle_make_length",
        "chk_quote_vehicle_model_length",
        "chk_quote_special_constraints_length",
        "chk_quote_additional_message_length",
        "chk_contact_message_length",
        "chk_idempotency_key_digest_hex",
        "chk_idempotency_payload_fingerprint_hex",
        "chk_idempotency_original_status",
        "chk_idempotency_response_body_shape",
        "chk_notification_attempt_count_nonneg",
        "chk_notification_max_attempts_positive",
        "chk_notification_pending_retry_next",
        "chk_notification_sent_no_next",
        "chk_notification_failed_terminal_no_next",
        "chk_notification_processing_lock",
        "chk_notification_non_processing_unlocked",
        "chk_rate_limit_subject_digest_hex",
        "chk_rate_limit_request_count_nonneg",
    }
)

EXPECTED_UNIQUE = {
    "uq_leads_public_reference": ("leads", ("public_reference",)),
    "uq_idempotency_scope_key_digest": (
        "idempotency_records",
        ("scope", "key_digest"),
    ),
    "uq_notification_jobs_lead_kind": (
        "notification_jobs",
        ("lead_id", "notification_kind"),
    ),
    "uq_rate_limit_bucket_window": (
        "rate_limit_buckets",
        ("scope", "subject_digest", "window_started_at"),
    ),
}

EXPECTED_INDEXES = {
    "idx_leads_created_at": {
        "table": "leads",
        "columns": ("created_at",),
        "unique": False,
        "predicate_contains": (),
        "predicate_excludes": (),
    },
    "idx_leads_lead_type_created_at": {
        "table": "leads",
        "columns": ("lead_type", "created_at"),
        "unique": False,
        "predicate_contains": (),
        "predicate_excludes": (),
    },
    "idx_idempotency_expires_at": {
        "table": "idempotency_records",
        "columns": ("expires_at",),
        "unique": False,
        "predicate_contains": (),
        "predicate_excludes": (),
    },
    "idx_notification_jobs_claim": {
        "table": "notification_jobs",
        "columns": ("next_attempt_at", "id"),
        "unique": False,
        "predicate_contains": ("pending", "retry_scheduled"),
        "predicate_excludes": ("failed_terminal", "'sent'"),
    },
    "idx_notification_jobs_reclaim": {
        "table": "notification_jobs",
        "columns": ("lock_expires_at", "id"),
        "unique": False,
        "predicate_contains": ("processing",),
        "predicate_excludes": ("pending", "retry_scheduled"),
    },
    "idx_rate_limit_expires_at": {
        "table": "rate_limit_buckets",
        "columns": ("expires_at",),
        "unique": False,
        "predicate_contains": (),
        "predicate_excludes": (),
    },
}

IDENTITY_COLUMNS = frozenset(
    {
        ("leads", "id"),
        ("idempotency_records", "id"),
        ("notification_jobs", "id"),
        ("rate_limit_buckets", "id"),
    }
)


@dataclass(frozen=True)
class ColumnSpec:
    table: str
    name: str
    udt_name: str
    char_max_length: int | None
    nullable: bool
    has_server_default: bool
    identity: bool


COLUMN_MANIFEST: tuple[ColumnSpec, ...] = (
    ColumnSpec("leads", "id", "int8", None, False, False, True),
    ColumnSpec("leads", "public_reference", "varchar", 21, False, False, False),
    ColumnSpec("leads", "lead_type", "lead_type_enum", None, False, False, False),
    ColumnSpec("leads", "first_name", "varchar", 80, False, False, False),
    ColumnSpec("leads", "last_name", "varchar", 80, False, False, False),
    ColumnSpec("leads", "email", "varchar", 254, False, False, False),
    ColumnSpec("leads", "phone", "varchar", 32, True, False, False),
    ColumnSpec("leads", "company", "varchar", 160, True, False, False),
    ColumnSpec("leads", "privacy_acknowledgement", "bool", None, False, False, False),
    ColumnSpec("leads", "privacy_policy_version", "varchar", 64, False, False, False),
    ColumnSpec("leads", "privacy_acknowledged_at", "timestamptz", None, False, False, False),
    ColumnSpec(
        "leads", "operational_status", "lead_operational_status_enum", None, False, True, False
    ),
    ColumnSpec("leads", "created_at", "timestamptz", None, False, False, False),
    ColumnSpec("leads", "updated_at", "timestamptz", None, False, False, False),
    ColumnSpec("quote_request_details", "lead_id", "int8", None, False, False, False),
    ColumnSpec("quote_request_details", "service", "service_type_enum", None, False, False, False),
    ColumnSpec("quote_request_details", "departure_city", "varchar", 120, False, False, False),
    ColumnSpec(
        "quote_request_details", "departure_postal_code", "varchar", 12, False, False, False
    ),
    ColumnSpec("quote_request_details", "arrival_city", "varchar", 120, False, False, False),
    ColumnSpec("quote_request_details", "arrival_postal_code", "varchar", 12, False, False, False),
    ColumnSpec(
        "quote_request_details", "timing_kind", "timing_kind_enum", None, False, False, False
    ),
    ColumnSpec("quote_request_details", "exact_date", "date", None, True, False, False),
    ColumnSpec("quote_request_details", "period_text", "varchar", 500, True, False, False),
    ColumnSpec(
        "quote_request_details",
        "vehicle_category",
        "vehicle_category_enum",
        None,
        False,
        False,
        False,
    ),
    ColumnSpec(
        "quote_request_details", "vehicle_category_other_detail", "varchar", 200, True, False, False
    ),
    ColumnSpec("quote_request_details", "vehicle_make", "varchar", 80, False, False, False),
    ColumnSpec("quote_request_details", "vehicle_model", "varchar", 80, False, False, False),
    ColumnSpec("quote_request_details", "vehicle_rolling", "bool", None, False, False, False),
    ColumnSpec("quote_request_details", "special_constraints", "text", None, True, False, False),
    ColumnSpec("quote_request_details", "additional_message", "text", None, True, False, False),
    ColumnSpec(
        "quote_request_details",
        "contact_preference",
        "contact_preference_enum",
        None,
        True,
        False,
        False,
    ),
    ColumnSpec("contact_message_details", "lead_id", "int8", None, False, False, False),
    ColumnSpec(
        "contact_message_details", "subject", "contact_subject_enum", None, False, False, False
    ),
    ColumnSpec("contact_message_details", "message", "text", None, False, False, False),
    ColumnSpec("idempotency_records", "id", "int8", None, False, False, True),
    ColumnSpec("idempotency_records", "scope", "idempotency_scope_enum", None, False, False, False),
    ColumnSpec("idempotency_records", "key_digest", "bpchar", 64, False, False, False),
    ColumnSpec("idempotency_records", "key_version", "int2", None, False, False, False),
    ColumnSpec("idempotency_records", "fingerprint_key_version", "int2", None, False, False, False),
    ColumnSpec(
        "idempotency_records", "fingerprint_algo_version", "int2", None, False, False, False
    ),
    ColumnSpec("idempotency_records", "payload_fingerprint", "bpchar", 64, False, False, False),
    ColumnSpec("idempotency_records", "lead_id", "int8", None, False, False, False),
    ColumnSpec("idempotency_records", "response_body", "jsonb", None, False, False, False),
    ColumnSpec("idempotency_records", "original_status_code", "int2", None, False, True, False),
    ColumnSpec("idempotency_records", "created_at", "timestamptz", None, False, False, False),
    ColumnSpec("idempotency_records", "expires_at", "timestamptz", None, False, False, False),
    ColumnSpec("notification_jobs", "id", "int8", None, False, False, True),
    ColumnSpec("notification_jobs", "lead_id", "int8", None, False, False, False),
    ColumnSpec(
        "notification_jobs",
        "notification_kind",
        "notification_kind_enum",
        None,
        False,
        False,
        False,
    ),
    ColumnSpec(
        "notification_jobs", "status", "notification_status_enum", None, False, False, False
    ),
    ColumnSpec("notification_jobs", "attempt_count", "int4", None, False, True, False),
    ColumnSpec("notification_jobs", "max_attempts", "int4", None, False, True, False),
    ColumnSpec("notification_jobs", "next_attempt_at", "timestamptz", None, True, False, False),
    ColumnSpec("notification_jobs", "locked_at", "timestamptz", None, True, False, False),
    ColumnSpec("notification_jobs", "lock_expires_at", "timestamptz", None, True, False, False),
    ColumnSpec("notification_jobs", "locked_by", "varchar", 64, True, False, False),
    ColumnSpec("notification_jobs", "provider_message_id", "varchar", 128, True, False, False),
    ColumnSpec("notification_jobs", "last_error_code", "varchar", 64, True, False, False),
    ColumnSpec("notification_jobs", "created_at", "timestamptz", None, False, False, False),
    ColumnSpec("notification_jobs", "updated_at", "timestamptz", None, False, False, False),
    ColumnSpec("rate_limit_buckets", "id", "int8", None, False, False, True),
    ColumnSpec("rate_limit_buckets", "scope", "rate_limit_scope_enum", None, False, False, False),
    ColumnSpec("rate_limit_buckets", "subject_digest", "bpchar", 64, False, False, False),
    ColumnSpec("rate_limit_buckets", "key_version", "int2", None, False, False, False),
    ColumnSpec("rate_limit_buckets", "window_started_at", "timestamptz", None, False, False, False),
    ColumnSpec("rate_limit_buckets", "request_count", "int4", None, False, False, False),
    ColumnSpec("rate_limit_buckets", "expires_at", "timestamptz", None, False, False, False),
    ColumnSpec("rate_limit_buckets", "created_at", "timestamptz", None, False, False, False),
    ColumnSpec("rate_limit_buckets", "updated_at", "timestamptz", None, False, False, False),
)

EXPECTED_COLUMN_COUNT = len(COLUMN_MANIFEST)
