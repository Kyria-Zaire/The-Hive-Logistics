from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    CHAR,
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    SmallInteger,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from thl_api.models.base import Base
from thl_api.models.enums import IdempotencyScope, idempotency_scope_enum

_HEX64 = r"^[0-9a-f]{64}$"


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    __table_args__ = (
        UniqueConstraint("scope", "key_digest", name="uq_idempotency_scope_key_digest"),
        CheckConstraint(
            f"key_digest ~ '{_HEX64}'",
            name="chk_idempotency_key_digest_hex",
        ),
        CheckConstraint(
            f"payload_fingerprint ~ '{_HEX64}'",
            name="chk_idempotency_payload_fingerprint_hex",
        ),
        CheckConstraint(
            "original_status_code = 201",
            name="chk_idempotency_original_status",
        ),
        CheckConstraint(
            "(response_body - 'public_reference' - 'status' - 'created_at') = '{}'::jsonb "
            "AND (response_body->>'status') = 'received'",
            name="chk_idempotency_response_body_shape",
        ),
        Index("idx_idempotency_expires_at", "expires_at"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )
    scope: Mapped[IdempotencyScope] = mapped_column(idempotency_scope_enum, nullable=False)
    key_digest: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    key_version: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    fingerprint_key_version: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    fingerprint_algo_version: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    payload_fingerprint: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    lead_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("leads.id", ondelete="RESTRICT"),
        nullable=False,
    )
    response_body: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    original_status_code: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        server_default="201",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return f"IdempotencyRecord(id={self.id!r}, scope={self.scope!r})"
