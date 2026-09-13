from __future__ import annotations

from enum import StrEnum

from sqlalchemy.dialects.postgresql import ENUM

# Valeurs alignées sur docs/architecture/DATA-MODEL.md v0.1.4 et OpenAPI.


class LeadType(StrEnum):
    quote = "quote"
    contact = "contact"


class LeadOperationalStatus(StrEnum):
    received = "received"


class ServiceType(StrEnum):
    convoyage_premium = "convoyage_premium"
    fleet_coordination = "fleet_coordination"
    automotive_logistics = "automotive_logistics"
    vehicle_preparation = "vehicle_preparation"


class TimingKind(StrEnum):
    exact_date = "exact_date"
    period = "period"


class VehicleCategory(StrEnum):
    city_sedan = "city_sedan"
    suv_4x4 = "suv_4x4"
    premium_sport = "premium_sport"
    light_commercial = "light_commercial"
    classic_collector = "classic_collector"
    other = "other"


class ContactPreference(StrEnum):
    email = "email"
    phone = "phone"
    no_preference = "no_preference"


class ContactSubject(StrEnum):
    information = "information"
    quote = "quote"
    partnership = "partnership"
    other = "other"


class IdempotencyScope(StrEnum):
    quote_requests = "quote_requests"
    contact_messages = "contact_messages"


class NotificationKind(StrEnum):
    internal_email = "internal_email"


class NotificationStatus(StrEnum):
    pending = "pending"
    processing = "processing"
    retry_scheduled = "retry_scheduled"
    sent = "sent"
    failed_terminal = "failed_terminal"


class RateLimitScope(StrEnum):
    quote_requests = "quote_requests"
    contact_messages = "contact_messages"


lead_type_enum = ENUM(LeadType, name="lead_type_enum", create_type=False)
lead_operational_status_enum = ENUM(
    LeadOperationalStatus,
    name="lead_operational_status_enum",
    create_type=False,
)
service_type_enum = ENUM(ServiceType, name="service_type_enum", create_type=False)
timing_kind_enum = ENUM(TimingKind, name="timing_kind_enum", create_type=False)
vehicle_category_enum = ENUM(
    VehicleCategory,
    name="vehicle_category_enum",
    create_type=False,
)
contact_preference_enum = ENUM(
    ContactPreference,
    name="contact_preference_enum",
    create_type=False,
)
contact_subject_enum = ENUM(ContactSubject, name="contact_subject_enum", create_type=False)
idempotency_scope_enum = ENUM(
    IdempotencyScope,
    name="idempotency_scope_enum",
    create_type=False,
)
notification_kind_enum = ENUM(
    NotificationKind,
    name="notification_kind_enum",
    create_type=False,
)
notification_status_enum = ENUM(
    NotificationStatus,
    name="notification_status_enum",
    create_type=False,
)
rate_limit_scope_enum = ENUM(RateLimitScope, name="rate_limit_scope_enum", create_type=False)

POSTGRES_ENUM_TYPES: tuple[ENUM, ...] = (
    lead_type_enum,
    lead_operational_status_enum,
    service_type_enum,
    timing_kind_enum,
    vehicle_category_enum,
    contact_preference_enum,
    contact_subject_enum,
    idempotency_scope_enum,
    notification_kind_enum,
    notification_status_enum,
    rate_limit_scope_enum,
)
