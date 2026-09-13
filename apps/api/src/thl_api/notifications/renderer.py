from __future__ import annotations

import html
from datetime import datetime

from thl_api.models.enums import NotificationKind
from thl_api.notifications.contracts import (
    ContactLeadSnapshot,
    LeadSnapshot,
    OutboundEmail,
    QuoteLeadSnapshot,
    deterministic_message_id,
    provider_dedup_key,
)


def _format_received_at(value: datetime) -> str:
    return value.astimezone().strftime("%Y-%m-%d %H:%M %Z")


def _contact_subject(public_reference: str) -> str:
    return f"[THL] Nouveau message de contact — {public_reference}"


def _quote_subject(public_reference: str) -> str:
    return f"[THL] Nouvelle demande de devis — {public_reference}"


def _text_block(lines: list[str]) -> str:
    return "\n".join(lines) + "\n"


def render_contact(
    snapshot: ContactLeadSnapshot,
    *,
    to_address: str,
    from_address: str,
) -> OutboundEmail:
    ref = snapshot.public_reference
    dedup = provider_dedup_key(ref, NotificationKind.internal_email)
    subject = _contact_subject(ref)
    text_lines = [
        "THE HIVE LOGISTICS — Nouveau message de contact",
        "",
        f"Référence : {ref}",
        f"Reçu le : {_format_received_at(snapshot.received_at)}",
        "",
        f"Nom : {snapshot.first_name} {snapshot.last_name}",
        f"Email : {snapshot.email}",
    ]
    if snapshot.phone:
        text_lines.append(f"Téléphone : {snapshot.phone}")
    if snapshot.company:
        text_lines.append(f"Entreprise : {snapshot.company}")
    text_lines.extend(
        [
            f"Sujet : {snapshot.subject}",
            "",
            "Message :",
            snapshot.message,
        ]
    )
    html_parts = [
        "<p><strong>THE HIVE LOGISTICS</strong> — Nouveau message de contact</p>",
        f"<p>Référence : {html.escape(ref)}</p>",
        f"<p>Reçu le : {html.escape(_format_received_at(snapshot.received_at))}</p>",
        f"<p>Nom : {html.escape(snapshot.first_name)} {html.escape(snapshot.last_name)}</p>",
        f"<p>Email : {html.escape(snapshot.email)}</p>",
    ]
    if snapshot.phone:
        html_parts.append(f"<p>Téléphone : {html.escape(snapshot.phone)}</p>")
    if snapshot.company:
        html_parts.append(f"<p>Entreprise : {html.escape(snapshot.company)}</p>")
    html_parts.append(f"<p>Sujet : {html.escape(snapshot.subject)}</p>")
    html_parts.append(f"<p>Message :</p><pre>{html.escape(snapshot.message)}</pre>")
    return OutboundEmail(
        from_address=from_address,
        to_address=to_address,
        subject=subject,
        text_body=_text_block(text_lines),
        html_body="\n".join(html_parts),
        message_id=deterministic_message_id(dedup),
        dedup_key=dedup,
    )


def render_quote(
    snapshot: QuoteLeadSnapshot,
    *,
    to_address: str,
    from_address: str,
) -> OutboundEmail:
    ref = snapshot.public_reference
    dedup = provider_dedup_key(ref, NotificationKind.internal_email)
    subject = _quote_subject(ref)
    text_lines = [
        "THE HIVE LOGISTICS — Nouvelle demande de devis",
        "",
        f"Référence : {ref}",
        f"Reçu le : {_format_received_at(snapshot.received_at)}",
        "",
        f"Nom : {snapshot.first_name} {snapshot.last_name}",
        f"Email : {snapshot.email}",
    ]
    if snapshot.phone:
        text_lines.append(f"Téléphone : {snapshot.phone}")
    if snapshot.company:
        text_lines.append(f"Entreprise : {snapshot.company}")
    text_lines.extend(
        [
            f"Service : {snapshot.service}",
            f"Départ : {snapshot.departure_city} ({snapshot.departure_postal_code})",
            f"Arrivée : {snapshot.arrival_city} ({snapshot.arrival_postal_code})",
            f"Date ou période : {snapshot.timing_label}",
            f"Catégorie véhicule : {snapshot.vehicle_category}",
            f"Véhicule : {snapshot.vehicle_make} {snapshot.vehicle_model}",
            f"Roulant : {'oui' if snapshot.vehicle_rolling else 'non'}",
        ]
    )
    if snapshot.special_constraints:
        text_lines.append(f"Contraintes : {snapshot.special_constraints}")
    if snapshot.additional_message:
        text_lines.append(f"Message : {snapshot.additional_message}")
    if snapshot.contact_preference:
        text_lines.append(f"Préférence de contact : {snapshot.contact_preference}")

    html_parts = [
        "<p><strong>THE HIVE LOGISTICS</strong> — Nouvelle demande de devis</p>",
        f"<p>Référence : {html.escape(ref)}</p>",
        f"<p>Reçu le : {html.escape(_format_received_at(snapshot.received_at))}</p>",
        f"<p>Nom : {html.escape(snapshot.first_name)} {html.escape(snapshot.last_name)}</p>",
        f"<p>Email : {html.escape(snapshot.email)}</p>",
    ]
    if snapshot.phone:
        html_parts.append(f"<p>Téléphone : {html.escape(snapshot.phone)}</p>")
    if snapshot.company:
        html_parts.append(f"<p>Entreprise : {html.escape(snapshot.company)}</p>")
    html_parts.extend(
        [
            f"<p>Service : {html.escape(snapshot.service)}</p>",
            f"<p>Départ : {html.escape(snapshot.departure_city)} "
            f"({html.escape(snapshot.departure_postal_code)})</p>",
            f"<p>Arrivée : {html.escape(snapshot.arrival_city)} "
            f"({html.escape(snapshot.arrival_postal_code)})</p>",
            f"<p>Date ou période : {html.escape(snapshot.timing_label)}</p>",
            f"<p>Catégorie véhicule : {html.escape(snapshot.vehicle_category)}</p>",
            f"<p>Véhicule : {html.escape(snapshot.vehicle_make)} "
            f"{html.escape(snapshot.vehicle_model)}</p>",
            f"<p>Roulant : {'oui' if snapshot.vehicle_rolling else 'non'}</p>",
        ]
    )
    if snapshot.special_constraints:
        html_parts.append(f"<p>Contraintes : {html.escape(snapshot.special_constraints)}</p>")
    if snapshot.additional_message:
        html_parts.append(f"<p>Message : {html.escape(snapshot.additional_message)}</p>")
    if snapshot.contact_preference:
        html_parts.append(
            f"<p>Préférence de contact : {html.escape(snapshot.contact_preference)}</p>"
        )
    return OutboundEmail(
        from_address=from_address,
        to_address=to_address,
        subject=subject,
        text_body=_text_block(text_lines),
        html_body="\n".join(html_parts),
        message_id=deterministic_message_id(dedup),
        dedup_key=dedup,
    )


def render_email(
    snapshot: LeadSnapshot,
    *,
    to_address: str,
    from_address: str,
) -> OutboundEmail:
    if isinstance(snapshot, ContactLeadSnapshot):
        return render_contact(snapshot, to_address=to_address, from_address=from_address)
    return render_quote(snapshot, to_address=to_address, from_address=from_address)


def subject_for_snapshot(snapshot: LeadSnapshot) -> str:
    ref = snapshot.public_reference
    if isinstance(snapshot, ContactLeadSnapshot):
        return _contact_subject(ref)
    return _quote_subject(ref)
