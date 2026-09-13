"""create lead data model (DATA-MODEL v0.1.4)

Revision ID: 0001_create_lead_data_model
Revises:
Create Date: 2026-09-13

Schéma autonome : aucune importation des modèles applicatifs THL.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_create_lead_data_model"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_PUBLIC_REFERENCE_PATTERN = r"^THL-[0-9]{8}-[0-9A-HJKMNP-TV-Z]{8}$"
_PHONE_PATTERN = r"^[+0-9().\s-]+$"
_HEX64 = r"^[0-9a-f]{64}$"

_ENUM_DEFINITIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("lead_type_enum", ("quote", "contact")),
    ("lead_operational_status_enum", ("received",)),
    (
        "service_type_enum",
        (
            "convoyage_premium",
            "fleet_coordination",
            "automotive_logistics",
            "vehicle_preparation",
        ),
    ),
    ("timing_kind_enum", ("exact_date", "period")),
    (
        "vehicle_category_enum",
        (
            "city_sedan",
            "suv_4x4",
            "premium_sport",
            "light_commercial",
            "classic_collector",
            "other",
        ),
    ),
    ("contact_preference_enum", ("email", "phone", "no_preference")),
    ("contact_subject_enum", ("information", "quote", "partnership", "other")),
    ("idempotency_scope_enum", ("quote_requests", "contact_messages")),
    ("notification_kind_enum", ("internal_email",)),
    (
        "notification_status_enum",
        (
            "pending",
            "processing",
            "retry_scheduled",
            "sent",
            "failed_terminal",
        ),
    ),
    ("rate_limit_scope_enum", ("quote_requests", "contact_messages")),
)


def _enum(name: str, *values: str) -> postgresql.ENUM:
    return postgresql.ENUM(*values, name=name, create_type=False)


def _create_enums(bind: sa.engine.Connection) -> None:
    for enum_name, values in _ENUM_DEFINITIONS:
        sa.Enum(*values, name=enum_name).create(bind, checkfirst=False)


def _drop_enums(bind: sa.engine.Connection) -> None:
    for enum_name, values in reversed(_ENUM_DEFINITIONS):
        sa.Enum(*values, name=enum_name).drop(bind, checkfirst=False)


def upgrade() -> None:
    bind = op.get_bind()
    _create_enums(bind)

    op.create_table(
        "leads",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("public_reference", sa.String(length=21), nullable=False),
        sa.Column("lead_type", _enum("lead_type_enum", "quote", "contact"), nullable=False),
        sa.Column("first_name", sa.String(length=80), nullable=False),
        sa.Column("last_name", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("company", sa.String(length=160), nullable=True),
        sa.Column("privacy_acknowledgement", sa.Boolean(), nullable=False),
        sa.Column("privacy_policy_version", sa.String(length=64), nullable=False),
        sa.Column("privacy_acknowledged_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "operational_status",
            _enum("lead_operational_status_enum", "received"),
            nullable=False,
            server_default=sa.text("'received'::lead_operational_status_enum"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_leads"),
        sa.UniqueConstraint("public_reference", name="uq_leads_public_reference"),
        sa.CheckConstraint(
            f"public_reference ~ '{_PUBLIC_REFERENCE_PATTERN}'",
            name="chk_leads_public_reference_format",
        ),
        sa.CheckConstraint(
            "char_length(first_name) BETWEEN 1 AND 80",
            name="chk_leads_first_name_length",
        ),
        sa.CheckConstraint(
            "char_length(last_name) BETWEEN 1 AND 80",
            name="chk_leads_last_name_length",
        ),
        sa.CheckConstraint(
            "char_length(email) BETWEEN 1 AND 254",
            name="chk_leads_email_length",
        ),
        sa.CheckConstraint(
            "company IS NULL OR char_length(company) <= 160",
            name="chk_leads_company_length",
        ),
        sa.CheckConstraint(
            "privacy_acknowledgement IS TRUE",
            name="chk_leads_privacy_ack",
        ),
        sa.CheckConstraint(
            "char_length(privacy_policy_version) BETWEEN 1 AND 64",
            name="chk_leads_privacy_policy_version_length",
        ),
        sa.CheckConstraint(
            "(lead_type <> 'quote') OR (phone IS NOT NULL AND "
            f"char_length(phone) BETWEEN 6 AND 32 AND phone ~ '{_PHONE_PATTERN}')",
            name="chk_leads_phone_quote",
        ),
        sa.CheckConstraint(
            "(lead_type <> 'contact') OR (phone IS NULL OR "
            f"(char_length(phone) BETWEEN 6 AND 32 AND phone ~ '{_PHONE_PATTERN}'))",
            name="chk_leads_phone_contact",
        ),
    )
    op.create_index("idx_leads_created_at", "leads", ["created_at"], unique=False)
    op.create_index(
        "idx_leads_lead_type_created_at",
        "leads",
        ["lead_type", "created_at"],
        unique=False,
    )

    op.create_table(
        "quote_request_details",
        sa.Column("lead_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "service",
            _enum(
                "service_type_enum",
                "convoyage_premium",
                "fleet_coordination",
                "automotive_logistics",
                "vehicle_preparation",
            ),
            nullable=False,
        ),
        sa.Column("departure_city", sa.String(length=120), nullable=False),
        sa.Column("departure_postal_code", sa.String(length=12), nullable=False),
        sa.Column("arrival_city", sa.String(length=120), nullable=False),
        sa.Column("arrival_postal_code", sa.String(length=12), nullable=False),
        sa.Column(
            "timing_kind",
            _enum("timing_kind_enum", "exact_date", "period"),
            nullable=False,
        ),
        sa.Column("exact_date", sa.Date(), nullable=True),
        sa.Column("period_text", sa.String(length=500), nullable=True),
        sa.Column(
            "vehicle_category",
            _enum(
                "vehicle_category_enum",
                "city_sedan",
                "suv_4x4",
                "premium_sport",
                "light_commercial",
                "classic_collector",
                "other",
            ),
            nullable=False,
        ),
        sa.Column("vehicle_category_other_detail", sa.String(length=200), nullable=True),
        sa.Column("vehicle_make", sa.String(length=80), nullable=False),
        sa.Column("vehicle_model", sa.String(length=80), nullable=False),
        sa.Column("vehicle_rolling", sa.Boolean(), nullable=False),
        sa.Column("special_constraints", sa.Text(), nullable=True),
        sa.Column("additional_message", sa.Text(), nullable=True),
        sa.Column(
            "contact_preference",
            _enum("contact_preference_enum", "email", "phone", "no_preference"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("lead_id", name="pk_quote_request_details"),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_quote_request_details_lead_id_leads",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "char_length(departure_city) BETWEEN 1 AND 120",
            name="chk_quote_departure_city_length",
        ),
        sa.CheckConstraint(
            "char_length(departure_postal_code) BETWEEN 4 AND 12",
            name="chk_quote_departure_postal_length",
        ),
        sa.CheckConstraint(
            "char_length(arrival_city) BETWEEN 1 AND 120",
            name="chk_quote_arrival_city_length",
        ),
        sa.CheckConstraint(
            "char_length(arrival_postal_code) BETWEEN 4 AND 12",
            name="chk_quote_arrival_postal_length",
        ),
        sa.CheckConstraint(
            "(timing_kind <> 'exact_date') OR "
            "(exact_date IS NOT NULL AND period_text IS NULL)",
            name="chk_quote_timing_exact_date",
        ),
        sa.CheckConstraint(
            "(timing_kind <> 'period') OR "
            "(period_text IS NOT NULL AND char_length(period_text) BETWEEN 3 AND 500 "
            "AND exact_date IS NULL)",
            name="chk_quote_timing_period",
        ),
        sa.CheckConstraint(
            "(vehicle_category <> 'other') OR "
            "(vehicle_category_other_detail IS NOT NULL AND "
            "char_length(vehicle_category_other_detail) BETWEEN 2 AND 200)",
            name="chk_quote_vehicle_other",
        ),
        sa.CheckConstraint(
            "(vehicle_category = 'other') OR (vehicle_category_other_detail IS NULL)",
            name="chk_quote_vehicle_other_absent",
        ),
        sa.CheckConstraint(
            "char_length(vehicle_make) BETWEEN 1 AND 80",
            name="chk_quote_vehicle_make_length",
        ),
        sa.CheckConstraint(
            "char_length(vehicle_model) BETWEEN 1 AND 80",
            name="chk_quote_vehicle_model_length",
        ),
        sa.CheckConstraint(
            "special_constraints IS NULL OR char_length(special_constraints) <= 2000",
            name="chk_quote_special_constraints_length",
        ),
        sa.CheckConstraint(
            "additional_message IS NULL OR char_length(additional_message) <= 4000",
            name="chk_quote_additional_message_length",
        ),
    )

    op.create_table(
        "contact_message_details",
        sa.Column("lead_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "subject",
            _enum("contact_subject_enum", "information", "quote", "partnership", "other"),
            nullable=False,
        ),
        sa.Column("message", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("lead_id", name="pk_contact_message_details"),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_contact_message_details_lead_id_leads",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "char_length(message) BETWEEN 10 AND 8000",
            name="chk_contact_message_length",
        ),
    )

    op.create_table(
        "idempotency_records",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column(
            "scope",
            _enum("idempotency_scope_enum", "quote_requests", "contact_messages"),
            nullable=False,
        ),
        sa.Column("key_digest", sa.CHAR(length=64), nullable=False),
        sa.Column("key_version", sa.SmallInteger(), nullable=False),
        sa.Column("fingerprint_key_version", sa.SmallInteger(), nullable=False),
        sa.Column("fingerprint_algo_version", sa.SmallInteger(), nullable=False),
        sa.Column("payload_fingerprint", sa.CHAR(length=64), nullable=False),
        sa.Column("lead_id", sa.BigInteger(), nullable=False),
        sa.Column("response_body", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "original_status_code",
            sa.SmallInteger(),
            nullable=False,
            server_default=sa.text("201"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_idempotency_records"),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_idempotency_records_lead_id_leads",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("scope", "key_digest", name="uq_idempotency_scope_key_digest"),
        sa.CheckConstraint(
            f"key_digest ~ '{_HEX64}'",
            name="chk_idempotency_key_digest_hex",
        ),
        sa.CheckConstraint(
            f"payload_fingerprint ~ '{_HEX64}'",
            name="chk_idempotency_payload_fingerprint_hex",
        ),
        sa.CheckConstraint(
            "original_status_code = 201",
            name="chk_idempotency_original_status",
        ),
        sa.CheckConstraint(
            "(response_body - 'public_reference' - 'status' - 'created_at') = '{}'::jsonb "
            "AND (response_body->>'status') = 'received'",
            name="chk_idempotency_response_body_shape",
        ),
    )
    op.create_index(
        "idx_idempotency_expires_at",
        "idempotency_records",
        ["expires_at"],
        unique=False,
    )

    op.create_table(
        "notification_jobs",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("lead_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "notification_kind",
            _enum("notification_kind_enum", "internal_email"),
            nullable=False,
        ),
        sa.Column(
            "status",
            _enum(
                "notification_status_enum",
                "pending",
                "processing",
                "retry_scheduled",
                "sent",
                "failed_terminal",
            ),
            nullable=False,
        ),
        sa.Column(
            "attempt_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "max_attempts",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("5"),
        ),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("lock_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locked_by", sa.String(length=64), nullable=True),
        sa.Column("provider_message_id", sa.String(length=128), nullable=True),
        sa.Column("last_error_code", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_notification_jobs"),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_notification_jobs_lead_id_leads",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "lead_id",
            "notification_kind",
            name="uq_notification_jobs_lead_kind",
        ),
        sa.CheckConstraint("attempt_count >= 0", name="chk_notification_attempt_count_nonneg"),
        sa.CheckConstraint("max_attempts >= 1", name="chk_notification_max_attempts_positive"),
        sa.CheckConstraint(
            "(status NOT IN ('pending', 'retry_scheduled')) OR (next_attempt_at IS NOT NULL)",
            name="chk_notification_pending_retry_next",
        ),
        sa.CheckConstraint(
            "(status <> 'sent') OR (next_attempt_at IS NULL)",
            name="chk_notification_sent_no_next",
        ),
        sa.CheckConstraint(
            "(status <> 'failed_terminal') OR (next_attempt_at IS NULL)",
            name="chk_notification_failed_terminal_no_next",
        ),
        sa.CheckConstraint(
            "(status <> 'processing') OR "
            "(locked_at IS NOT NULL AND lock_expires_at IS NOT NULL AND locked_by IS NOT NULL)",
            name="chk_notification_processing_lock",
        ),
        sa.CheckConstraint(
            "(status = 'processing') OR "
            "(locked_at IS NULL AND lock_expires_at IS NULL AND locked_by IS NULL)",
            name="chk_notification_non_processing_unlocked",
        ),
    )
    op.create_index(
        "idx_notification_jobs_claim",
        "notification_jobs",
        ["next_attempt_at", "id"],
        unique=False,
        postgresql_where=sa.text("status IN ('pending', 'retry_scheduled')"),
    )
    op.create_index(
        "idx_notification_jobs_reclaim",
        "notification_jobs",
        ["lock_expires_at", "id"],
        unique=False,
        postgresql_where=sa.text("status = 'processing'"),
    )

    op.create_table(
        "rate_limit_buckets",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column(
            "scope",
            _enum("rate_limit_scope_enum", "quote_requests", "contact_messages"),
            nullable=False,
        ),
        sa.Column("subject_digest", sa.CHAR(length=64), nullable=False),
        sa.Column("key_version", sa.SmallInteger(), nullable=False),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("request_count", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_rate_limit_buckets"),
        sa.UniqueConstraint(
            "scope",
            "subject_digest",
            "window_started_at",
            name="uq_rate_limit_bucket_window",
        ),
        sa.CheckConstraint(
            f"subject_digest ~ '{_HEX64}'",
            name="chk_rate_limit_subject_digest_hex",
        ),
        sa.CheckConstraint(
            "request_count >= 0",
            name="chk_rate_limit_request_count_nonneg",
        ),
    )
    op.create_index(
        "idx_rate_limit_expires_at",
        "rate_limit_buckets",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    bind = op.get_bind()
    op.drop_index("idx_rate_limit_expires_at", table_name="rate_limit_buckets")
    op.drop_table("rate_limit_buckets")
    op.drop_index("idx_notification_jobs_reclaim", table_name="notification_jobs")
    op.drop_index("idx_notification_jobs_claim", table_name="notification_jobs")
    op.drop_table("notification_jobs")
    op.drop_index("idx_idempotency_expires_at", table_name="idempotency_records")
    op.drop_table("idempotency_records")
    op.drop_table("contact_message_details")
    op.drop_table("quote_request_details")
    op.drop_index("idx_leads_lead_type_created_at", table_name="leads")
    op.drop_index("idx_leads_created_at", table_name="leads")
    op.drop_table("leads")
    _drop_enums(bind)
