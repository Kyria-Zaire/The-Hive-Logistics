from __future__ import annotations

import psycopg

from schema_manifest import (
    BUSINESS_TABLES,
    COLUMN_MANIFEST,
    EXPECTED_CHECK_NAMES,
    EXPECTED_COLUMN_COUNT,
    EXPECTED_INDEXES,
    EXPECTED_PRIMARY_KEYS,
    EXPECTED_UNIQUE,
    IDENTITY_COLUMNS,
)

EXPECTED_FOREIGN_KEYS = {
    "fk_quote_request_details_lead_id_leads": (
        "quote_request_details",
        "lead_id",
        "leads",
        "id",
    ),
    "fk_contact_message_details_lead_id_leads": (
        "contact_message_details",
        "lead_id",
        "leads",
        "id",
    ),
    "fk_idempotency_records_lead_id_leads": (
        "idempotency_records",
        "lead_id",
        "leads",
        "id",
    ),
    "fk_notification_jobs_lead_id_leads": (
        "notification_jobs",
        "lead_id",
        "leads",
        "id",
    ),
}


def _fetch_columns(conn: psycopg.Connection) -> dict[tuple[str, str], dict[str, object]]:
    rows = conn.execute(
        """
        SELECT table_name, column_name, ordinal_position, udt_name,
               character_maximum_length, is_nullable, column_default,
               is_identity, identity_generation
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = ANY(%s)
        ORDER BY table_name, ordinal_position
        """,
        (list(BUSINESS_TABLES),),
    ).fetchall()
    result: dict[tuple[str, str], dict[str, object]] = {}
    for row in rows:
        key = (row[0], row[1])
        result[key] = {
            "ordinal_position": row[2],
            "udt_name": row[3],
            "char_max": row[4],
            "nullable": row[5] == "YES",
            "default": row[6],
            "is_identity": row[7] == "YES",
            "identity_generation": row[8],
        }
    return result


def assert_column_manifest_exact(conn: psycopg.Connection) -> None:
    actual = _fetch_columns(conn)
    assert len(actual) == EXPECTED_COLUMN_COUNT

    expected_keys = {(spec.table, spec.name) for spec in COLUMN_MANIFEST}
    assert set(actual.keys()) == expected_keys

    for spec in COLUMN_MANIFEST:
        col = actual[(spec.table, spec.name)]
        assert col["udt_name"] == spec.udt_name, (spec.table, spec.name, col["udt_name"])
        assert col["char_max"] == spec.char_max_length
        assert col["nullable"] == spec.nullable
        if spec.has_server_default:
            assert col["default"] is not None, (spec.table, spec.name)
        else:
            assert col["default"] is None, (spec.table, spec.name)
        if spec.identity:
            assert col["is_identity"] is True
            assert col["identity_generation"] == "ALWAYS"
        else:
            assert col["is_identity"] is False

    assert {
        (spec.table, spec.name) for spec in COLUMN_MANIFEST if spec.identity
    } == IDENTITY_COLUMNS


def assert_constraints_exact(conn: psycopg.Connection) -> None:
    pk_rows = conn.execute(
        """
        SELECT tc.table_name, tc.constraint_name
        FROM information_schema.table_constraints tc
        WHERE tc.table_schema = 'public'
          AND tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_name = ANY(%s)
        """,
        (list(BUSINESS_TABLES),),
    ).fetchall()
    assert {row[0]: row[1] for row in pk_rows} == EXPECTED_PRIMARY_KEYS

    fk_rows = conn.execute(
        """
        SELECT tc.constraint_name, tc.table_name, kcu.column_name,
               ccu.table_name AS ref_table, ccu.column_name AS ref_column,
               rc.delete_rule
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON kcu.constraint_name = tc.constraint_name
         AND kcu.table_schema = tc.table_schema
        JOIN information_schema.constraint_column_usage ccu
          ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema = tc.table_schema
        JOIN information_schema.referential_constraints rc
          ON rc.constraint_name = tc.constraint_name
         AND rc.constraint_schema = tc.table_schema
        WHERE tc.table_schema = 'public'
          AND tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_name = ANY(%s)
        ORDER BY tc.constraint_name
        """,
        (list(BUSINESS_TABLES),),
    ).fetchall()
    assert len(fk_rows) == len(EXPECTED_FOREIGN_KEYS)
    for name, table, column, ref_table, ref_column, delete_rule in fk_rows:
        assert delete_rule == "RESTRICT"
        assert EXPECTED_FOREIGN_KEYS[name] == (table, column, ref_table, ref_column)

    unique_rows = conn.execute(
        """
        SELECT c.conname, t.relname,
               array_agg(a.attname ORDER BY u.ordinality) AS cols
        FROM pg_constraint c
        JOIN pg_class t ON t.oid = c.conrelid
        JOIN pg_namespace n ON n.oid = t.relnamespace
        JOIN LATERAL unnest(c.conkey) WITH ORDINALITY AS u(attnum, ordinality) ON true
        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = u.attnum
        WHERE n.nspname = 'public'
          AND c.contype = 'u'
          AND t.relname = ANY(%s)
        GROUP BY c.conname, t.relname
        ORDER BY c.conname
        """,
        (list(BUSINESS_TABLES),),
    ).fetchall()
    assert len(unique_rows) == len(EXPECTED_UNIQUE)
    for name, table, cols in unique_rows:
        col_tuple = tuple(cols) if isinstance(cols, list) else tuple(cols)
        assert EXPECTED_UNIQUE[name] == (table, col_tuple)

    check_rows = conn.execute(
        """
        SELECT c.conname
        FROM pg_constraint c
        JOIN pg_class t ON t.oid = c.conrelid
        JOIN pg_namespace n ON n.oid = t.relnamespace
        WHERE c.contype = 'c'
          AND n.nspname = 'public'
          AND t.relname = ANY(%s)
        ORDER BY c.conname
        """,
        (list(BUSINESS_TABLES),),
    ).fetchall()
    check_names = {row[0] for row in check_rows}
    assert check_names == set(EXPECTED_CHECK_NAMES)


def _fetch_business_indexes(conn: psycopg.Connection) -> dict[str, dict[str, object]]:
    rows = conn.execute(
        """
        SELECT
            ic.relname AS index_name,
            tbl.relname AS table_name,
            ix.indisunique AS is_unique,
            pg_get_expr(ix.indpred, ix.indrelid) AS predicate,
            (
                SELECT array_agg(a.attname ORDER BY u.ordinality)
                FROM unnest(ix.indkey) WITH ORDINALITY AS u(attnum, ordinality)
                JOIN pg_attribute a
                  ON a.attrelid = ix.indrelid
                 AND a.attnum = u.attnum
                WHERE u.attnum > 0
            ) AS columns
        FROM pg_index ix
        JOIN pg_class ic ON ic.oid = ix.indexrelid
        JOIN pg_class tbl ON tbl.oid = ix.indrelid
        JOIN pg_namespace ns ON ns.oid = tbl.relnamespace
        WHERE ns.nspname = 'public'
          AND ic.relname LIKE 'idx_%'
        ORDER BY ic.relname
        """
    ).fetchall()
    return {
        row[0]: {
            "table": row[1],
            "unique": row[2],
            "predicate": row[3],
            "columns": list(row[4]) if row[4] is not None else [],
        }
        for row in rows
    }


def assert_indexes_exact(conn: psycopg.Connection) -> None:
    indexes = _fetch_business_indexes(conn)
    assert set(indexes.keys()) == set(EXPECTED_INDEXES.keys())
    for name, spec in EXPECTED_INDEXES.items():
        idx = indexes[name]
        assert idx["table"] == spec["table"]
        assert idx["columns"] == list(spec["columns"])
        assert idx["unique"] is spec["unique"]
        predicate = idx["predicate"]
        if not spec["predicate_contains"] and not spec["predicate_excludes"]:
            assert predicate is None
            continue
        assert predicate is not None
        lowered = predicate.lower()
        for token in spec["predicate_contains"]:
            assert token in lowered, (name, predicate)
        for token in spec["predicate_excludes"]:
            assert token not in lowered, (name, predicate)


def assert_catalog_matches_data_model(conn: psycopg.Connection) -> None:
    assert_column_manifest_exact(conn)
    assert_constraints_exact(conn)
    assert_indexes_exact(conn)

    trigger_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM pg_trigger
        WHERE NOT tgisinternal
          AND tgrelid IN (
            SELECT oid FROM pg_class
            WHERE relnamespace = 'public'::regnamespace AND relkind = 'r'
          )
        """
    ).fetchone()[0]
    assert trigger_count == 0
