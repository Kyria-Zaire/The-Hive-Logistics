from __future__ import annotations

import ipaddress


def client_ip_for_rate_limit(
    *,
    direct_host: str | None,
    forwarded_for: str | None,
    trusted_proxy_enabled: bool,
) -> str:
    if trusted_proxy_enabled and forwarded_for:
        parts = [part.strip() for part in forwarded_for.split(",") if part.strip()]
        if parts:
            candidate = parts[0]
            if _is_valid_ip(candidate):
                return candidate
    if direct_host and _is_valid_ip(direct_host):
        return direct_host
    return "unknown"


def _is_valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return False
    return True
