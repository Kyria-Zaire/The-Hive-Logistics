from __future__ import annotations

import ipaddress


def client_ip_for_rate_limit(
    *,
    direct_host: str | None,
    forwarded_for: str | None,
    trusted_networks: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...],
) -> str:
    if trusted_networks and forwarded_for and direct_host and _is_valid_ip(direct_host):
        peer = ipaddress.ip_address(direct_host)
        if any(peer in network for network in trusted_networks):
            parts = [part.strip() for part in forwarded_for.split(",") if part.strip()]
            if parts:
                candidate = parts[0]
                if _is_valid_ip(candidate):
                    return candidate
    if direct_host and _is_valid_ip(direct_host):
        return direct_host
    return "0.0.0.0"


def _is_valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return False
    return True
