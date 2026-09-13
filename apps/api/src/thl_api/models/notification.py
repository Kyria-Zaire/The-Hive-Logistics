from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from thl_api.models.base import Base
from thl_api.models.enums import (
    NotificationKind,
    NotificationStatus,
    notification_kind_enum,
    notification_status_enum,
)


class NotificationJob(Base):
    __tablename__ = "notification_jobs"
    __table_args__ = (
        UniqueConstraint(
            "lead_id",
            "notification_kind",
            name="uq_notification_jobs_lead_kind",
        ),
        CheckConstraint("attempt_count >= 0", name="chk_notification_attempt_count_nonneg"),
        CheckConstraint("max_attempts >= 1", name="chk_notification_max_attempts_positive"),
        CheckConstraint(
            "(status NOT IN ('pending', 'retry_scheduled')) OR (next_attempt_at IS NOT NULL)",
            name="chk_notification_pending_retry_next",
        ),
        CheckConstraint(
            "(status <> 'sent') OR (next_attempt_at IS NULL)",
            name="chk_notification_sent_no_next",
        ),
        CheckConstraint(
            "(status <> 'failed_terminal') OR (next_attempt_at IS NULL)",
            name="chk_notification_failed_terminal_no_next",
        ),
        CheckConstraint(
            "(status <> 'processing') OR "
            "(locked_at IS NOT NULL AND lock_expires_at IS NOT NULL AND locked_by IS NOT NULL)",
            name="chk_notification_processing_lock",
        ),
        CheckConstraint(
            "(status = 'processing') OR "
            "(locked_at IS NULL AND lock_expires_at IS NULL AND locked_by IS NULL)",
            name="chk_notification_non_processing_unlocked",
        ),
        Index(
            "idx_notification_jobs_claim",
            "next_attempt_at",
            "id",
            postgresql_where=text("status IN ('pending', 'retry_scheduled')"),
        ),
        Index(
            "idx_notification_jobs_reclaim",
            "lock_expires_at",
            "id",
            postgresql_where=text("status = 'processing'"),
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )
    lead_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("leads.id", ondelete="RESTRICT"),
        nullable=False,
    )
    notification_kind: Mapped[NotificationKind] = mapped_column(
        notification_kind_enum,
        nullable=False,
    )
    status: Mapped[NotificationStatus] = mapped_column(
        notification_status_enum,
        nullable=False,
    )
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default="5")
    next_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    lock_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    locked_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return f"NotificationJob(id={self.id!r}, status={self.status!r})"
