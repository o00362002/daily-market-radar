from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True)
class UrlPolicy:
    allow_internal_hosts: set[str]
    allowed_schemes: set[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.allowed_schemes is None:
            object.__setattr__(self, "allowed_schemes", {"http", "https"})

    def is_allowed(self, url: str) -> bool:
        parts = urlsplit(url)
        if parts.scheme not in self.allowed_schemes:
            return False
        host = parts.hostname
        if not host:
            return False
        if host in self.allow_internal_hosts:
            return True
        if "." not in host:
            return False
        if host in {"localhost", "0.0.0.0"}:
            return False
        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            return True
        return not (
            ip.is_loopback
            or ip.is_private
            or ip.is_link_local
            or ip.is_reserved
            or ip == ipaddress.ip_address("169.254.169.254")
        )

    def validate_redirect_chain(self, urls: list[str]) -> bool:
        return all(self.is_allowed(url) for url in urls)


def validate_response_size(size_bytes: int, max_bytes: int) -> None:
    if size_bytes > max_bytes:
        raise ValueError(f"response too large: {size_bytes} > {max_bytes}")


class AdapterError(RuntimeError):
    pass
