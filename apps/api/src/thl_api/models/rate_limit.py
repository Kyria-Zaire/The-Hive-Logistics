from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    CHAR,
    BigInteger,
    CheckConstraint,
    DateTime,
    Identity,
    Index,
    Integer,
    SmallInteger,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from thl_api.models.base import Base
from thl_api.models.enums import RateLimitScope, rate_limit_scope_enum

_HEX64 = r"^[0-9a-f]{64}$"


class RateLimitBucket(Base):
    __tablename__ = "rate_limit_buckets"
    __table_args__ = (
        UniqueConstraint(
            "scope",
            "subject_digest",
            "window_started_at",
            name="uq_rate_limit_bucket_window",
        ),
        CheckConstraint(
            f"subject_digest ~ '{_HEX64}'",
            name="chk_rate_limit_subject_digest_hex",
        ),
        CheckConstraint(
            "request_count >= 0",
            name="chk_rate_limit_request_count_nonneg",
        ),
        Index("idx_rate_limit_expires_at", "expires_at"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )
    scope: Mapped[RateLimitScope] = mapped_column(rate_limit_scope_enum, nullable=False)
    subject_digest: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    key_version: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    window_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    request_count: Mapped[int] = mapped_column(Integer, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return f"RateLimitBucket(id={self.id!r}, scope={self.scope!r})"
