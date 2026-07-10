"""HTTP transport seam shared by every network source adapter.

Adapters depend on the ``HttpTransport`` protocol, never on urllib/requests
directly, so they are fully unit-testable offline with a fake transport. The real
implementation enforces a bounded response size, an SSRF allow/deny policy on the
initial URL and on every redirect hop, a hard redirect cap, and conditional
requests (ETag / Last-Modified).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol, runtime_checkable

from radar.adapters.base import AdapterError, UrlPolicy, validate_response_size


DEFAULT_MAX_BYTES = 5_000_000
DEFAULT_MAX_REDIRECTS = 5
DEFAULT_TIMEOUT_SECONDS = 12
USER_AGENT = "daily-market-radar/0.2 (+https://github.com/o00362002/daily-market-radar)"


@dataclass(frozen=True)
class HttpRequest:
    url: str
    method: str = "GET"
    headers: Mapping[str, str] = field(default_factory=dict)
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS


@dataclass(frozen=True)
class HttpResponse:
    status: int
    url: str
    headers: Mapping[str, str]
    body: bytes
    from_cache: bool = False

    def header(self, name: str) -> str:
        lowered = name.lower()
        for key, value in self.headers.items():
            if key.lower() == lowered:
                return value
        return ""

    @property
    def not_modified(self) -> bool:
        return self.status == 304

    @property
    def content_type(self) -> str:
        return self.header("Content-Type").split(";", 1)[0].strip().lower()


@runtime_checkable
class HttpTransport(Protocol):
    def fetch(self, request: HttpRequest) -> HttpResponse: ...


def conditional_headers(etag: str | None, last_modified: str | None) -> dict[str, str]:
    headers: dict[str, str] = {}
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified
    return headers


class UrllibHttpTransport:
    """Real transport. Registry URLs only; redirects are re-validated per hop."""

    def __init__(
        self,
        *,
        policy: UrlPolicy | None = None,
        max_bytes: int = DEFAULT_MAX_BYTES,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
    ) -> None:
        self._policy = policy or UrlPolicy(allow_internal_hosts=set())
        self._max_bytes = max_bytes
        self._max_redirects = max_redirects

    def fetch(self, request: HttpRequest) -> HttpResponse:
        # Imported lazily so importing this module never pulls urllib into
        # adapters that are constructed with a fake transport.
        import urllib.error
        import urllib.request

        if not self._policy.is_allowed(request.url):
            raise AdapterError(f"blocked by url policy: {request.url}")

        redirect_chain = [request.url]
        opener = urllib.request.build_opener(_NoRedirect())
        current = request.url
        headers = {"User-Agent": USER_AGENT, **dict(request.headers)}
        for _ in range(self._max_redirects + 1):
            raw = urllib.request.Request(current, method=request.method, headers=headers)
            try:
                with opener.open(raw, timeout=request.timeout_seconds) as response:
                    body = response.read(self._max_bytes + 1)
                    validate_response_size(len(body), self._max_bytes)
                    return HttpResponse(
                        status=response.status,
                        url=current,
                        headers=dict(response.headers.items()),
                        body=body,
                    )
            except urllib.error.HTTPError as exc:
                if exc.code == 304:
                    return HttpResponse(status=304, url=current, headers=dict(exc.headers.items()), body=b"")
                if exc.code in {301, 302, 303, 307, 308}:
                    location = exc.headers.get("Location", "")
                    if not location:
                        raise AdapterError(f"redirect without location: {current}") from exc
                    current = _resolve(current, location)
                    redirect_chain.append(current)
                    if not self._policy.validate_redirect_chain(redirect_chain):
                        raise AdapterError(f"redirect blocked by url policy: {current}") from exc
                    continue
                raise AdapterError(f"http error {exc.code}: {current}") from exc
        raise AdapterError(f"too many redirects: {request.url}")


class _NoRedirect:
    """urllib handler that surfaces redirects as HTTPError so we re-check each hop."""

    def http_error_302(self, req, fp, code, msg, headers):  # noqa: D401,ANN001
        import urllib.error

        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302


def _resolve(base: str, location: str) -> str:
    from urllib.parse import urljoin

    return urljoin(base, location)
