"""Registry-driven generic JSON API adapter.

First version supports GET + JSON, page and cursor pagination, bearer-token and
query-token auth, dotted item paths and field mapping, and graceful degradation
when the configured credential env var is absent.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from radar.adapters.base import AdapterError
from radar.adapters.transport import HttpRequest, HttpTransport


@dataclass(frozen=True)
class JsonApiConfig:
    source_id: str
    endpoint: str
    method: str = "GET"
    query_params: Mapping[str, str] = field(default_factory=dict)
    secret_env: str = ""
    auth_style: str = "none"  # none | bearer | query
    auth_query_param: str = "apikey"
    pagination: str = "none"  # none | page | cursor
    page_param: str = "page"
    page_size_param: str = "page_size"
    page_size: int = 50
    max_pages: int = 5
    cursor_param: str = "cursor"
    next_cursor_path: str = "next_cursor"
    item_path: str = "items"
    field_mapping: Mapping[str, str] = field(default_factory=dict)
    rate_limit_per_minute: int | None = None
    domain_mapping: str = "ai_agents_applications"


@dataclass(frozen=True)
class JsonApiResult:
    items: tuple[dict[str, Any], ...]
    pages_fetched: int
    available: bool
    degradation_reason: str = ""


def _dig(payload: Any, dotted: str) -> Any:
    node = payload
    if not dotted:
        return node
    for part in dotted.split("."):
        if isinstance(node, Mapping) and part in node:
            node = node[part]
        else:
            return None
    return node


def _map_item(raw: Mapping[str, Any], mapping: Mapping[str, str]) -> dict[str, Any]:
    if not mapping:
        return dict(raw)
    return {target: _dig(raw, source) for target, source in mapping.items()}


class GenericJsonApiAdapter:
    def __init__(
        self,
        transport: HttpTransport,
        config: JsonApiConfig,
        *,
        credential_lookup: Callable[[str], str | None],
    ) -> None:
        self._transport = transport
        self._config = config
        self._credential_lookup = credential_lookup

    def fetch(self) -> JsonApiResult:
        token = self._credential_lookup(self._config.secret_env) if self._config.secret_env else ""
        if self._config.auth_style != "none" and self._config.secret_env and not token:
            return JsonApiResult(
                items=(),
                pages_fetched=0,
                available=False,
                degradation_reason=f"credential_unavailable:{self._config.secret_env}",
            )

        items: list[dict[str, Any]] = []
        pages = 0
        cursor: str | None = None
        page_number = 1
        for _ in range(self._config.max_pages):
            url, headers = self._build_request(token, page_number, cursor)
            response = self._transport.fetch(HttpRequest(url=url, method=self._config.method, headers=headers))
            if response.content_type and "json" not in response.content_type:
                raise AdapterError(f"expected json, got {response.content_type}")
            payload = json.loads(response.body.decode("utf-8") or "{}")
            raw_items = _dig(payload, self._config.item_path) or []
            if not isinstance(raw_items, list):
                raise AdapterError(f"item_path did not resolve to a list: {self._config.item_path}")
            items.extend(_map_item(item, self._config.field_mapping) for item in raw_items if isinstance(item, Mapping))
            pages += 1

            if self._config.pagination == "none" or not raw_items:
                break
            if self._config.pagination == "page":
                page_number += 1
            elif self._config.pagination == "cursor":
                cursor = _dig(payload, self._config.next_cursor_path)
                if not cursor:
                    break
        return JsonApiResult(items=tuple(items), pages_fetched=pages, available=True)

    def _build_request(self, token: str, page_number: int, cursor: str | None) -> tuple[str, dict[str, str]]:
        from urllib.parse import urlencode, urlsplit, urlunsplit

        params: dict[str, str] = dict(self._config.query_params)
        headers: dict[str, str] = {"Accept": "application/json"}
        if self._config.auth_style == "bearer" and token:
            headers["Authorization"] = f"Bearer {token}"
        elif self._config.auth_style == "query" and token:
            params[self._config.auth_query_param] = token

        if self._config.pagination == "page":
            params[self._config.page_param] = str(page_number)
            params[self._config.page_size_param] = str(self._config.page_size)
        elif self._config.pagination == "cursor" and cursor:
            params[self._config.cursor_param] = str(cursor)

        parts = urlsplit(self._config.endpoint)
        existing = dict(_parse_query(parts.query))
        existing.update(params)
        url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(existing), parts.fragment))
        return url, headers


def _parse_query(query: str) -> list[tuple[str, str]]:
    from urllib.parse import parse_qsl

    return parse_qsl(query, keep_blank_values=True)
