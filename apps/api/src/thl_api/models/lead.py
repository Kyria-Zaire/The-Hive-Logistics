from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from thl_api.models.base import Base
from thl_api.models.enums import (
    ContactPreference,
    ContactSubject,
    LeadOperationalStatus,
    LeadType,
    ServiceType,
    TimingKind,
    VehicleCategory,
    contact_preference_enum,
    contact_subject_enum,
    lead_operational_status_enum,
    lead_type_enum,
    service_type_enum,
    timing_kind_enum,
    vehicle_category_enum,
)

_PUBLIC_REFERENCE_PATTERN = r"^THL-[0-9]{8}-[0-9A-HJKMNP-TV-Z]{8}$"
_PHONE_PATTERN = r"^[+0-9().\s-]+$"


class Lead(Base):
    __tablename__ = "leads"
    __table_args__ = (
        UniqueConstraint("public_reference", name="uq_leads_public_reference"),
        CheckConstraint(
            f"public_reference ~ '{_PUBLIC_REFERENCE_PATTERN}'",
            name="chk_leads_public_reference_format",
        ),
        CheckConstraint(
            "char_length(first_name) BETWEEN 1 AND 80",
            name="chk_leads_first_name_length",
        ),
        CheckConstraint(
            "char_length(last_name) BETWEEN 1 AND 80",
            name="chk_leads_last_name_length",
        ),
        CheckConstraint(
            "char_length(email) BETWEEN 1 AND 254",
            name="chk_leads_email_length",
        ),
        CheckConstraint(
            "company IS NULL OR char_length(company) <= 160",
            name="chk_leads_company_length",
        ),
        CheckConstraint(
            "privacy_acknowledgement IS TRUE",
            name="chk_leads_privacy_ack",
        ),
        CheckConstraint(
            "char_length(privacy_policy_version) BETWEEN 1 AND 64",
            name="chk_leads_privacy_policy_version_length",
        ),
        CheckConstraint(
            "(lead_type <> 'quote') OR (phone IS NOT NULL AND "
            f"char_length(phone) BETWEEN 6 AND 32 AND phone ~ '{_PHONE_PATTERN}')",
            name="chk_leads_phone_quote",
        ),
        CheckConstraint(
            "(lead_type <> 'contact') OR (phone IS NULL OR "
            f"(char_length(phone) BETWEEN 6 AND 32 AND phone ~ '{_PHONE_PATTERN}'))",
            name="chk_leads_phone_contact",
        ),
        Index("idx_leads_created_at", "created_at"),
        Index("idx_leads_lead_type_created_at", "lead_type", "created_at"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )
    public_reference: Mapped[str] = mapped_column(String(21), nullable=False)
    lead_type: Mapped[LeadType] = mapped_column(lead_type_enum, nullable=False)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    company: Mapped[str | None] = mapped_column(String(160), nullable=True)
    privacy_acknowledgement: Mapped[bool] = mapped_column(Boolean, nullable=False)
    privacy_policy_version: Mapped[str] = mapped_column(String(64), nullable=False)
    operational_status: Mapped[LeadOperationalStatus] = mapped_column(
        lead_operational_status_enum,
        nullable=False,
        server_default=text("'received'::lead_operational_status_enum"),
    )
    privacy_acknowledged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    quote_details: Mapped[QuoteRequestDetail | None] = relationship(
        back_populates="lead",
        uselist=False,
    )
    contact_details: Mapped[ContactMessageDetail | None] = relationship(
        back_populates="lead",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"Lead(id={self.id!r}, lead_type={self.lead_type!r})"


class QuoteRequestDetail(Base):
    __tablename__ = "quote_request_details"
    __table_args__ = (
        CheckConstraint(
            "char_length(departure_city) BETWEEN 1 AND 120",
            name="chk_quote_departure_city_length",
        ),
        CheckConstraint(
            "char_length(departure_postal_code) BETWEEN 4 AND 12",
            name="chk_quote_departure_postal_length",
        ),
        CheckConstraint(
            "char_length(arrival_city) BETWEEN 1 AND 120",
            name="chk_quote_arrival_city_length",
        ),
        CheckConstraint(
            "char_length(arrival_postal_code) BETWEEN 4 AND 12",
            name="chk_quote_arrival_postal_length",
        ),
        CheckConstraint(
            "(timing_kind <> 'exact_date') OR "
            "(exact_date IS NOT NULL AND period_text IS NULL)",
            name="chk_quote_timing_exact_date",
        ),
        CheckConstraint(
            "(timing_kind <> 'period') OR "
            "(period_text IS NOT NULL AND char_length(period_text) BETWEEN 3 AND 500 "
            "AND exact_date IS NULL)",
            name="chk_quote_timing_period",
        ),
        CheckConstraint(
            "(vehicle_category <> 'other') OR "
            "(vehicle_category_other_detail IS NOT NULL AND "
            "char_length(vehicle_category_other_detail) BETWEEN 2 AND 200)",
            name="chk_quote_vehicle_other",
        ),
        CheckConstraint(
            "(vehicle_category = 'other') OR (vehicle_category_other_detail IS NULL)",
            name="chk_quote_vehicle_other_absent",
        ),
        CheckConstraint(
            "char_length(vehicle_make) BETWEEN 1 AND 80",
            name="chk_quote_vehicle_make_length",
        ),
        CheckConstraint(
            "char_length(vehicle_model) BETWEEN 1 AND 80",
            name="chk_quote_vehicle_model_length",
        ),
        CheckConstraint(
            "special_constraints IS NULL OR char_length(special_constraints) <= 2000",
            name="chk_quote_special_constraints_length",
        ),
        CheckConstraint(
            "additional_message IS NULL OR char_length(additional_message) <= 4000",
            name="chk_quote_additional_message_length",
        ),
    )

    lead_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("leads.id", ondelete="RESTRICT"),
        primary_key=True,
    )
    service: Mapped[ServiceType] = mapped_column(service_type_enum, nullable=False)
    departure_city: Mapped[str] = mapped_column(String(120), nullable=False)
    departure_postal_code: Mapped[str] = mapped_column(String(12), nullable=False)
    arrival_city: Mapped[str] = mapped_column(String(120), nullable=False)
    arrival_postal_code: Mapped[str] = mapped_column(String(12), nullable=False)
    timing_kind: Mapped[TimingKind] = mapped_column(timing_kind_enum, nullable=False)
    exact_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    vehicle_category: Mapped[VehicleCategory] = mapped_column(
        vehicle_category_enum,
        nullable=False,
    )
    vehicle_category_other_detail: Mapped[str | None] = mapped_column(String(200), nullable=True)
    vehicle_make: Mapped[str] = mapped_column(String(80), nullable=False)
    vehicle_model: Mapped[str] = mapped_column(String(80), nullable=False)
    vehicle_rolling: Mapped[bool] = mapped_column(Boolean, nullable=False)
    special_constraints: Mapped[str | None] = mapped_column(Text, nullable=True)
    additional_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_preference: Mapped[ContactPreference | None] = mapped_column(
        contact_preference_enum,
        nullable=True,
    )

    lead: Mapped[Lead] = relationship(back_populates="quote_details")

    def __repr__(self) -> str:
        return f"QuoteRequestDetail(lead_id={self.lead_id!r})"


class ContactMessageDetail(Base):
    __tablename__ = "contact_message_details"
    __table_args__ = (
        CheckConstraint(
            "char_length(message) BETWEEN 10 AND 8000",
            name="chk_contact_message_length",
        ),
    )

    lead_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("leads.id", ondelete="RESTRICT"),
        primary_key=True,
    )
    subject: Mapped[ContactSubject] = mapped_column(contact_subject_enum, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    lead: Mapped[Lead] = relationship(back_populates="contact_details")

    def __repr__(self) -> str:
        return f"ContactMessageDetail(lead_id={self.lead_id!r})"
