from __future__ import annotations

import ipaddress


def _is_valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return False
    return True


def _is_trusted(
    hop: str,
    trusted_networks: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...],
) -> bool:
    if not _is_valid_ip(hop):
        return False
    address = ipaddress.ip_address(hop)
    return any(address in network for network in trusted_networks)


def client_ip_for_rate_limit(
    *,
    direct_host: str | None,
    forwarded_for: str | None,
    trusted_networks: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...],
) -> str:
    if not direct_host or not _is_valid_ip(direct_host):
        return "127.0.0.1"

    if not trusted_networks or not forwarded_for:
        return direct_host

    if not _is_trusted(direct_host, trusted_networks):
        return direct_host

    xff_hops = [part.strip() for part in forwarded_for.split(",") if part.strip()]
    chain: list[str] = [direct_host]
    for hop in reversed(xff_hops):
        if hop != chain[-1]:
            chain.append(hop)

    for hop in chain:
        if not _is_trusted(hop, trusted_networks):
            return hop

    if xff_hops and _is_valid_ip(xff_hops[0]):
        return xff_hops[0]
    return direct_host
