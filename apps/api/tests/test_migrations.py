from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import psycopg
import pytest
from alembic import command
from alembic.config import Config

from migration_catalog import assert_catalog_matches_data_model
from migration_db import (
    assert_safe_to_drop,
    temporary_migration_database,
)
from thl_api.alembic_config import configure_alembic_database_url

API_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_TABLES = frozenset(
    {
        "leads",
        "quote_request_details",
        "contact_message_details",
        "idempotency_records",
        "notification_jobs",
        "rate_limit_buckets",
    }
)

EXPECTED_ENUMS: dict[str, list[str]] = {
    "lead_type_enum": ["quote", "contact"],
    "lead_operational_status_enum": ["received"],
    "service_type_enum": [
        "convoyage_premium",
        "fleet_coordination",
        "automotive_logistics",
        "vehicle_preparation",
    ],
    "timing_kind_enum": ["exact_date", "period"],
    "vehicle_category_enum": [
        "city_sedan",
        "suv_4x4",
        "premium_sport",
        "light_commercial",
        "classic_collector",
        "other",
    ],
    "contact_preference_enum": ["email", "phone", "no_preference"],
    "contact_subject_enum": ["information", "quote", "partnership", "other"],
    "idempotency_scope_enum": ["quote_requests", "contact_messages"],
    "notification_kind_enum": ["internal_email"],
    "notification_status_enum": [
        "pending",
        "processing",
        "retry_scheduled",
        "sent",
        "failed_terminal",
    ],
    "rate_limit_scope_enum": ["quote_requests", "contact_messages"],
}

ACCEPTED_AT = datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC)
VALID_REFERENCE = "THL-20260115-01234567"
VALID_DIGEST = "a" * 64


def _expect_check_violation(conn: psycopg.Connection, sql: str, params: tuple[object, ...]) -> None:
    with pytest.raises(psycopg.errors.CheckViolation):
        conn.execute(sql, params)
        conn.commit()
    conn.rollback()


def _alembic_config(database_url: str) -> Config:
    cfg = Config(str(API_ROOT / "alembic.ini"))
    configure_alembic_database_url(cfg, database_url)
    return cfg


def _run_alembic(database_url: str, *args: str) -> None:
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    env["THL_ENV"] = "dev"
    result = subprocess.run(
        ["uv", "run", "alembic", *args],
        cwd=API_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        msg = f"alembic {' '.join(args)} failed:\n{result.stdout}\n{result.stderr}"
        raise AssertionError(msg)


@pytest.fixture
def migrated_db(monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setenv("THL_ENV", "dev")
    with temporary_migration_database() as temp:
        monkeypatch.setenv("DATABASE_URL", temp.database_url)
        command.upgrade(_alembic_config(temp.database_url), "head")
        yield temp.database_url


@pytest.mark.migrations
def test_migration_lifecycle_and_schema(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("THL_ENV", "dev")
    with temporary_migration_database() as temp:
        db_url = temp.database_url
        monkeypatch.setenv("DATABASE_URL", db_url)
        cfg = _alembic_config(db_url)

        command.upgrade(cfg, "head")
        sync_url = db_url.replace("postgresql+psycopg://", "postgresql://", 1)
        with psycopg.connect(sync_url) as conn:
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
                )
            } - {"alembic_version"}
            assert tables == EXPECTED_TABLES

            enum_rows = conn.execute(
                """
                SELECT t.typname, array_agg(e.enumlabel ORDER BY e.enumsortorder)
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                WHERE t.typname LIKE '%_enum'
                GROUP BY t.typname
                ORDER BY t.typname
                """
            ).fetchall()
            enums = {name: list(labels) for name, labels in enum_rows}
            assert enums == EXPECTED_ENUMS

            identity_cols = conn.execute(
                """
                SELECT table_name, column_name, is_identity
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND is_identity = 'YES'
                ORDER BY table_name, column_name
                """
            ).fetchall()
            assert {row[0] for row in identity_cols} == {
                "leads",
                "idempotency_records",
                "notification_jobs",
                "rate_limit_buckets",
            }

            jsonb_cols = conn.execute(
                """
                SELECT table_name, column_name, udt_name
                FROM information_schema.columns
                WHERE table_schema = 'public' AND udt_name = 'jsonb'
                """
            ).fetchall()
            assert jsonb_cols == [("idempotency_records", "response_body", "jsonb")]

            trigger_count = conn.execute(
                """
                SELECT COUNT(*)
                FROM pg_trigger
                WHERE NOT tgisinternal AND tgrelid IN (
                    SELECT oid FROM pg_class WHERE relnamespace = 'public'::regnamespace
                )
                """
            ).fetchone()[0]
            assert trigger_count == 0

            partial_indexes = conn.execute(
                """
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                  AND indexdef LIKE '%WHERE%'
                ORDER BY indexname
                """
            ).fetchall()
            partial_names = {row[0] for row in partial_indexes}
            assert partial_names == {
                "idx_notification_jobs_claim",
                "idx_notification_jobs_reclaim",
            }

            assert_catalog_matches_data_model(conn)

        _run_alembic(db_url, "check")

        command.downgrade(cfg, "base")
        with psycopg.connect(sync_url) as conn:
            remaining = {
                row[0]
                for row in conn.execute(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
                )
            } - {"alembic_version"}
            assert remaining == set()
            enum_remaining = conn.execute(
                """
                SELECT t.typname
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE n.nspname = 'public'
                  AND t.typtype = 'e'
                  AND t.typname ~ '_enum$'
                """
            ).fetchall()
            assert enum_remaining == []

        command.upgrade(cfg, "head")
        with psycopg.connect(sync_url) as conn:
            tables_after = {
                row[0]
                for row in conn.execute(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
                )
            } - {"alembic_version"}
            assert tables_after == EXPECTED_TABLES

    with temporary_migration_database() as second_temp:
        monkeypatch.setenv("DATABASE_URL", second_temp.database_url)
        command.upgrade(_alembic_config(second_temp.database_url), "head")


@pytest.mark.migrations
def test_temp_database_guard_rejects_non_prefixed_drop() -> None:
    with pytest.raises(RuntimeError, match="Refusing DROP"):
        assert_safe_to_drop("thl_dev")


def _insert_lead(conn: psycopg.Connection, *, reference: str = VALID_REFERENCE) -> int:
    row = conn.execute(
        """
        INSERT INTO leads (
            public_reference, lead_type, first_name, last_name, email, phone,
            privacy_acknowledgement, privacy_policy_version, privacy_acknowledged_at,
            created_at, updated_at
        ) VALUES (
            %s, 'quote', 'Ada', 'Lovelace', 'ada@example.com', '+33123456789',
            TRUE, 'v1', %s, %s, %s
        ) RETURNING id
        """,
        (reference, ACCEPTED_AT, ACCEPTED_AT, ACCEPTED_AT),
    ).fetchone()
    assert row is not None
    return int(row[0])


@pytest.mark.migrations
@pytest.mark.parametrize(
    ("sql", "params"),
    [
        (
            """
            INSERT INTO leads (
                public_reference, lead_type, first_name, last_name, email, phone,
                privacy_acknowledgement, privacy_policy_version, privacy_acknowledged_at,
                created_at, updated_at
            ) VALUES (
                'INVALID-REF', 'quote', 'A', 'B', 'a@b.co', '+33123456789',
                TRUE, 'v1', %s, %s, %s
            )
            """,
            (ACCEPTED_AT, ACCEPTED_AT, ACCEPTED_AT),
        ),
        (
            """
            INSERT INTO leads (
                public_reference, lead_type, first_name, last_name, email, phone,
                privacy_acknowledgement, privacy_policy_version, privacy_acknowledged_at,
                created_at, updated_at
            ) VALUES (
                'THL-20260115-01234568', 'quote', 'A', 'B', 'a@b.co', NULL,
                TRUE, 'v1', %s, %s, %s
            )
            """,
            (ACCEPTED_AT, ACCEPTED_AT, ACCEPTED_AT),
        ),
        (
            """
            INSERT INTO leads (
                public_reference, lead_type, first_name, last_name, email,
                privacy_acknowledgement, privacy_policy_version, privacy_acknowledged_at,
                created_at, updated_at
            ) VALUES (
                'THL-20260115-01234569', 'contact', 'A', 'B', 'a@b.co',
                FALSE, 'v1', %s, %s, %s
            )
            """,
            (ACCEPTED_AT, ACCEPTED_AT, ACCEPTED_AT),
        ),
    ],
    ids=["invalid_public_reference", "quote_without_phone", "privacy_not_acknowledged"],
)
def test_lead_check_constraints(
    migrated_db: str,
    sql: str,
    params: tuple[object, ...],
) -> None:
    sync_url = migrated_db.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(sync_url) as conn:
        _expect_check_violation(conn, sql, params)


@pytest.mark.migrations
def test_quote_timing_and_vehicle_checks(migrated_db: str) -> None:
    sync_url = migrated_db.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(sync_url) as conn:
        lead_id = _insert_lead(conn)
        conn.commit()
        base_cols = (
            lead_id,
            "convoyage_premium",
            "Paris",
            "75001",
            "Lyon",
            "69001",
        )
        _expect_check_violation(
            conn,
            """
            INSERT INTO quote_request_details (
                lead_id, service, departure_city, departure_postal_code,
                arrival_city, arrival_postal_code, timing_kind, exact_date, period_text,
                vehicle_category, vehicle_make, vehicle_model, vehicle_rolling
            ) VALUES (%s, %s, %s, %s, %s, %s, 'exact_date', NULL, 'conflict',
                'city_sedan', 'Make', 'Model', TRUE)
            """,
            base_cols,
        )
        _expect_check_violation(
            conn,
            """
            INSERT INTO quote_request_details (
                lead_id, service, departure_city, departure_postal_code,
                arrival_city, arrival_postal_code, timing_kind,
                vehicle_category, vehicle_make, vehicle_model, vehicle_rolling
            ) VALUES (%s, %s, %s, %s, %s, %s, 'period', 'city_sedan', 'Make', 'Model', TRUE)
            """,
            base_cols,
        )
        _expect_check_violation(
            conn,
            """
            INSERT INTO quote_request_details (
                lead_id, service, departure_city, departure_postal_code,
                arrival_city, arrival_postal_code, timing_kind, period_text,
                vehicle_category, vehicle_make, vehicle_model, vehicle_rolling
            ) VALUES (%s, %s, %s, %s, %s, %s, 'period', 'ok period', 'other', 'Make', 'Model', TRUE)
            """,
            base_cols,
        )
        _expect_check_violation(
            conn,
            """
            INSERT INTO quote_request_details (
                lead_id, service, departure_city, departure_postal_code,
                arrival_city, arrival_postal_code, timing_kind, period_text,
                vehicle_category, vehicle_category_other_detail,
                vehicle_make, vehicle_model, vehicle_rolling
            ) VALUES (
                %s, %s, %s, %s, %s, %s, 'period', 'ok period', 'city_sedan', 'extra',
                'Make', 'Model', TRUE
            )
            """,
            base_cols,
        )


@pytest.mark.migrations
def test_idempotency_and_rate_limit_checks(migrated_db: str) -> None:
    sync_url = migrated_db.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(sync_url) as conn:
        lead_id = _insert_lead(conn)
        conn.commit()
        body = {
            "public_reference": VALID_REFERENCE,
            "status": "received",
            "created_at": ACCEPTED_AT.isoformat(),
        }
        _expect_check_violation(
            conn,
            """
            INSERT INTO idempotency_records (
                scope, key_digest, key_version, fingerprint_key_version,
                fingerprint_algo_version, payload_fingerprint, lead_id, response_body,
                original_status_code, created_at, expires_at
            ) VALUES (
                'quote_requests', 'ZZZZ', 1, 1, 1, %s, %s, %s::jsonb, 201, %s, %s
            )
            """,
            (VALID_DIGEST, lead_id, json.dumps(body), ACCEPTED_AT, ACCEPTED_AT),
        )
        _expect_check_violation(
            conn,
            """
            INSERT INTO idempotency_records (
                scope, key_digest, key_version, fingerprint_key_version,
                fingerprint_algo_version, payload_fingerprint, lead_id, response_body,
                original_status_code, created_at, expires_at
            ) VALUES (
                'quote_requests', %s, 1, 1, 1, %s, %s,
                %s::jsonb, 201, %s, %s
            )
            """,
            (
                VALID_DIGEST,
                VALID_DIGEST,
                lead_id,
                json.dumps({**body, "extra": "x"}),
                ACCEPTED_AT,
                ACCEPTED_AT,
            ),
        )
        _expect_check_violation(
            conn,
            """
            INSERT INTO idempotency_records (
                scope, key_digest, key_version, fingerprint_key_version,
                fingerprint_algo_version, payload_fingerprint, lead_id, response_body,
                original_status_code, created_at, expires_at
            ) VALUES (
                'quote_requests', %s, 1, 1, 1, %s, %s, %s::jsonb, 200, %s, %s
            )
            """,
            (
                VALID_DIGEST,
                VALID_DIGEST,
                lead_id,
                json.dumps(body),
                ACCEPTED_AT,
                ACCEPTED_AT,
            ),
        )
        _expect_check_violation(
            conn,
            """
            INSERT INTO rate_limit_buckets (
                scope, subject_digest, key_version, window_started_at,
                request_count, expires_at, created_at, updated_at
            ) VALUES (
                'quote_requests', %s, 1, %s, -1, %s, %s, %s
            )
            """,
            (VALID_DIGEST, ACCEPTED_AT, ACCEPTED_AT, ACCEPTED_AT, ACCEPTED_AT),
        )


@pytest.mark.migrations
def test_notification_state_checks(migrated_db: str) -> None:
    sync_url = migrated_db.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(sync_url) as conn:
        lead_id = _insert_lead(conn)
        conn.commit()
        _expect_check_violation(
            conn,
            """
            INSERT INTO notification_jobs (
                lead_id, notification_kind, status, attempt_count, max_attempts,
                next_attempt_at, created_at, updated_at
            ) VALUES (
                %s, 'internal_email', 'processing', 0, 5, NULL, %s, %s
            )
            """,
            (lead_id, ACCEPTED_AT, ACCEPTED_AT),
        )


@pytest.mark.migrations
def test_server_defaults_applied_on_insert(migrated_db: str) -> None:
    sync_url = migrated_db.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(sync_url) as conn:
        lead_row = conn.execute(
            """
            INSERT INTO leads (
                public_reference, lead_type, first_name, last_name, email, phone,
                privacy_acknowledgement, privacy_policy_version, privacy_acknowledged_at,
                created_at, updated_at
            ) VALUES (
                'THL-20260115-01234570', 'quote', 'Ada', 'Lovelace', 'ada@example.com',
                '+33123456789', TRUE, 'v1', %s, %s, %s
            ) RETURNING id, operational_status::text
            """,
            (ACCEPTED_AT, ACCEPTED_AT, ACCEPTED_AT),
        ).fetchone()
        assert lead_row is not None
        lead_id = int(lead_row[0])
        assert lead_row[1] == "received"

        body = {
            "public_reference": "THL-20260115-01234570",
            "status": "received",
            "created_at": ACCEPTED_AT.isoformat(),
        }
        idem_row = conn.execute(
            """
            INSERT INTO idempotency_records (
                scope, key_digest, key_version, fingerprint_key_version,
                fingerprint_algo_version, payload_fingerprint, lead_id, response_body,
                created_at, expires_at
            ) VALUES (
                'quote_requests', %s, 1, 1, 1, %s, %s, %s::jsonb, %s, %s
            ) RETURNING original_status_code
            """,
            (
                VALID_DIGEST,
                VALID_DIGEST,
                lead_id,
                json.dumps(body),
                ACCEPTED_AT,
                ACCEPTED_AT,
            ),
        ).fetchone()
        assert idem_row is not None
        assert int(idem_row[0]) == 201

        job_row = conn.execute(
            """
            INSERT INTO notification_jobs (
                lead_id, notification_kind, status, next_attempt_at, created_at, updated_at
            ) VALUES (
                %s, 'internal_email', 'pending', %s, %s, %s
            ) RETURNING attempt_count, max_attempts
            """,
            (lead_id, ACCEPTED_AT, ACCEPTED_AT, ACCEPTED_AT),
        ).fetchone()
        assert job_row is not None
        assert int(job_row[0]) == 0
        assert int(job_row[1]) == 5
        conn.commit()


@pytest.mark.migrations
def test_models_repr_contains_no_pii() -> None:
    from thl_api.models.enums import LeadOperationalStatus, LeadType
    from thl_api.models.lead import Lead

    lead = Lead(
        id=1,
        public_reference=VALID_REFERENCE,
        lead_type=LeadType.quote,
        first_name="Secret",
        last_name="Person",
        email="secret@example.com",
        phone="+33123456789",
        company=None,
        privacy_acknowledgement=True,
        privacy_policy_version="v1",
        privacy_acknowledged_at=ACCEPTED_AT,
        operational_status=LeadOperationalStatus.received,
        created_at=ACCEPTED_AT,
        updated_at=ACCEPTED_AT,
    )
    text = repr(lead)
    assert "Secret" not in text
    assert "secret@example.com" not in text
