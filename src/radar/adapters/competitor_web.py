from __future__ import annotations

import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any

from radar.adapters.transport import HttpRequest, HttpTransport, conditional_headers
from radar.contracts.report import CompetitorAuditV1, CompetitorCheckV1, CompetitorSourceCheckV1
from radar.ports.competitors import CompetitorMonitorResult
from radar.ports.publishing import StateStore
from radar.schemas.competitor import CompetitorMonitoringRegistry, CompetitorSourceSpec, CompetitorTarget


_STATE_VERSION = "competitor-monitor-state/v1"
_MAX_EXCERPT_CHARS = 320
_MAX_SHINGLES = 6000


@dataclass(frozen=True)
class _ParsedPage:
    title: str
    visible_text: str
    content_hash: str
    shingles: frozenset[str]


class OfficialCompetitorMonitor:
    """Checks fixed official pages and compares stable visible-content fingerprints.

    The first successful run establishes a baseline. Later runs use conditional HTTP
    requests plus shingle similarity, so a rotating timestamp or tiny navigation edit
    does not automatically become a competitive update.
    """

    def __init__(
        self,
        *,
        registry: CompetitorMonitoringRegistry,
        transport: HttpTransport,
        state_store: StateStore,
    ) -> None:
        self._registry = registry
        self._transport = transport
        self._state_store = state_store

    def run(self, report_date: str, checked_at: str) -> CompetitorMonitorResult:
        del report_date  # the checked timestamp and report contract carry the date boundary
        previous_state = self._load_state()
        previous_sources: dict[str, dict[str, Any]] = dict(previous_state.get("sources", {}))
        next_sources = dict(previous_sources)

        futures = {}
        source_results: dict[tuple[str, str], tuple[CompetitorSourceCheckV1, dict[str, Any] | None]] = {}
        with ThreadPoolExecutor(max_workers=self._registry.max_workers) as executor:
            for target in self._registry.targets:
                for source in target.sources:
                    key = self._state_source_key(target.competitor_id, source.source_id)
                    future = executor.submit(
                        self._check_source,
                        target,
                        source,
                        previous_sources.get(key),
                        checked_at,
                    )
                    futures[future] = (target.competitor_id, source.source_id, key)
            for future in as_completed(futures):
                competitor_id, source_id, key = futures[future]
                check, snapshot = future.result()
                source_results[(competitor_id, source_id)] = (check, snapshot)
                if snapshot is not None:
                    next_sources[key] = snapshot

        checks = [
            self._target_check(
                target,
                [source_results[(target.competitor_id, source.source_id)][0] for source in target.sources],
                checked_at,
            )
            for target in self._registry.targets
        ]
        audit = self._audit(checks, checked_at)
        state_value = (
            json.dumps(
                {
                    "version": _STATE_VERSION,
                    "registry_version": self._registry.competitor_registry_version,
                    "source_registry_version": self._registry.source_registry_version,
                    "updated_at": checked_at,
                    "sources": next_sources,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode("utf-8")
        return CompetitorMonitorResult(
            audit=audit,
            state_key=self._registry.state_key,
            state_value=state_value,
        )

    def _check_source(
        self,
        target: CompetitorTarget,
        source: CompetitorSourceSpec,
        previous: dict[str, Any] | None,
        checked_at: str,
    ) -> tuple[CompetitorSourceCheckV1, dict[str, Any] | None]:
        previous = previous or {}
        headers = conditional_headers(
            str(previous.get("etag") or "") or None,
            str(previous.get("last_modified") or "") or None,
        )
        try:
            response = self._transport.fetch(
                HttpRequest(
                    url=source.url,
                    headers=headers,
                    timeout_seconds=self._registry.timeout_seconds,
                )
            )
            if response.not_modified:
                check = CompetitorSourceCheckV1(
                    source_id=source.source_id,
                    url=source.url,
                    channel=source.channel,
                    status="not_modified",
                    checked_at=checked_at,
                    http_status=response.status,
                    etag=response.header("ETag") or str(previous.get("etag") or ""),
                    last_modified=response.header("Last-Modified") or str(previous.get("last_modified") or ""),
                    content_hash=str(previous.get("content_hash") or ""),
                    previous_content_hash=str(previous.get("content_hash") or ""),
                    material_change=False,
                    similarity=1.0,
                    title=str(previous.get("title") or target.name),
                    excerpt=str(previous.get("excerpt") or ""),
                    error="",
                )
                return check, {**previous, "checked_at": checked_at}
            if not 200 <= response.status < 300:
                raise ValueError(f"unexpected HTTP status {response.status}")

            page = _parse_page(response.body)
            if len(page.visible_text) < self._registry.minimum_visible_characters:
                raise ValueError(
                    f"visible content too short ({len(page.visible_text)} chars); possible block or empty page"
                )

            previous_hash = str(previous.get("content_hash") or "")
            previous_shingles = frozenset(str(value) for value in previous.get("shingles", []))
            similarity = _jaccard(previous_shingles, page.shingles) if previous_shingles else None
            previous_length = int(previous.get("text_length") or 0)
            length_delta = (
                abs(len(page.visible_text) - previous_length) / max(len(page.visible_text), previous_length, 1)
                if previous_length
                else 0.0
            )
            material_change = bool(
                previous_hash
                and page.content_hash != previous_hash
                and (
                    similarity is None
                    or similarity < source.material_similarity_threshold
                    or length_delta > 0.08
                )
            )
            excerpt = page.visible_text[:_MAX_EXCERPT_CHARS]
            snapshot = {
                "competitor_id": target.competitor_id,
                "source_id": source.source_id,
                "url": source.url,
                "channel": source.channel,
                "checked_at": checked_at,
                "etag": response.header("ETag"),
                "last_modified": response.header("Last-Modified"),
                "content_hash": page.content_hash,
                "text_length": len(page.visible_text),
                "shingles": sorted(page.shingles)[:_MAX_SHINGLES],
                "title": page.title or target.name,
                "excerpt": excerpt,
            }
            return (
                CompetitorSourceCheckV1(
                    source_id=source.source_id,
                    url=source.url,
                    channel=source.channel,
                    status="checked",
                    checked_at=checked_at,
                    http_status=response.status,
                    etag=response.header("ETag"),
                    last_modified=response.header("Last-Modified"),
                    content_hash=page.content_hash,
                    previous_content_hash=previous_hash,
                    material_change=material_change,
                    similarity=similarity,
                    title=page.title or target.name,
                    excerpt=excerpt,
                    error="",
                ),
                snapshot,
            )
        except Exception as exc:  # adapter boundary: one vendor must not stop the daily run
            return (
                CompetitorSourceCheckV1(
                    source_id=source.source_id,
                    url=source.url,
                    channel=source.channel,
                    status="failed",
                    checked_at=checked_at,
                    http_status=None,
                    etag=str(previous.get("etag") or ""),
                    last_modified=str(previous.get("last_modified") or ""),
                    content_hash=str(previous.get("content_hash") or ""),
                    previous_content_hash=str(previous.get("content_hash") or ""),
                    material_change=False,
                    similarity=None,
                    title=str(previous.get("title") or target.name),
                    excerpt=str(previous.get("excerpt") or ""),
                    error=str(exc)[:500],
                ),
                None,
            )

    @staticmethod
    def _target_check(
        target: CompetitorTarget,
        source_checks: list[CompetitorSourceCheckV1],
        checked_at: str,
    ) -> CompetitorCheckV1:
        successful = [check for check in source_checks if check.status != "failed"]
        failed = [check for check in source_checks if check.status == "failed"]
        changed = [check for check in successful if check.material_change]
        baseline = [
            check
            for check in successful
            if check.status == "checked" and not check.previous_content_hash
        ]

        if not successful:
            status = "failed"
            summary = f"{target.name} 的 {len(failed)} 個固定官方來源全部檢查失敗。"
        elif failed:
            status = "partial"
            summary = (
                f"{target.name} 已成功檢查 {len(successful)} 個官方來源，"
                f"另有 {len(failed)} 個失敗；"
                + (f"其中 {len(changed)} 個出現材料變化。" if changed else "未在成功來源中發現材料變化。")
            )
        elif changed:
            status = "updated"
            summary = f"{target.name} 有 {len(changed)} 個官方來源出現材料變化。"
        elif baseline:
            status = "baseline"
            summary = f"{target.name} 已成功建立 {len(successful)} 個官方來源的內容基準。"
        else:
            status = "checked_no_major_update"
            summary = f"{target.name} 已檢查 {len(successful)} 個官方來源，未發現達到材料門檻的更新。"

        return CompetitorCheckV1(
            competitor_id=target.competitor_id,
            group=target.group,
            name=target.name,
            market=target.market,
            relationship=target.relationship,
            priority=target.priority,
            status=status,
            checked_at=checked_at,
            successful_source_count=len(successful),
            failed_source_count=len(failed),
            fresh_material_delta=bool(changed),
            summary=summary,
            source_checks=source_checks,
        )

    def _audit(self, checks: list[CompetitorCheckV1], checked_at: str) -> CompetitorAuditV1:
        checked = [check for check in checks if check.status in {"baseline", "checked_no_major_update", "updated", "partial"}]
        updated = [check for check in checks if check.fresh_material_delta]
        baseline = [check for check in checks if check.status == "baseline"]
        partial = [check for check in checks if check.status == "partial"]
        failed = [check for check in checks if check.status == "failed"]
        not_executed = [check for check in checks if check.status == "not_executed"]
        return CompetitorAuditV1(
            registry_version=self._registry.competitor_registry_version,
            source_registry_version=self._registry.source_registry_version,
            checked_at=checked_at,
            fixed_target_count=len(checks),
            checked_target_count=len(checked),
            updated_target_count=len(updated),
            baseline_target_count=len(baseline),
            partial_target_count=len(partial),
            failed_target_count=len(failed),
            not_executed_target_count=len(not_executed),
            checked_ids=[check.competitor_id for check in checked],
            updated_ids=[check.competitor_id for check in updated],
            baseline_ids=[check.competitor_id for check in baseline],
            partial_ids=[check.competitor_id for check in partial],
            failed_ids=[check.competitor_id for check in failed],
            not_executed_ids=[check.competitor_id for check in not_executed],
            checks=checks,
        )

    def _load_state(self) -> dict[str, Any]:
        raw = self._state_store.load(self._registry.state_key)
        if not raw:
            return {"version": _STATE_VERSION, "sources": {}}
        try:
            state = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {"version": _STATE_VERSION, "sources": {}}
        if state.get("version") != _STATE_VERSION or not isinstance(state.get("sources"), dict):
            return {"version": _STATE_VERSION, "sources": {}}
        return state

    @staticmethod
    def _state_source_key(competitor_id: str, source_id: str) -> str:
        return f"{competitor_id}/{source_id}"


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._in_title = False
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag in {"script", "style", "noscript", "svg", "template"}:
            self._skip_depth += 1
        if tag == "title" and self._skip_depth == 0:
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag in {"script", "style", "noscript", "svg", "template"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        value = data.strip()
        if not value:
            return
        self.text_parts.append(value)
        if self._in_title:
            self.title_parts.append(value)


def _parse_page(body: bytes) -> _ParsedPage:
    text = body.decode("utf-8", errors="replace")
    parser = _VisibleTextParser()
    parser.feed(text)
    visible = re.sub(r"\s+", " ", " ".join(parser.text_parts)).strip()
    title = re.sub(r"\s+", " ", " ".join(parser.title_parts)).strip()
    normalized = visible.lower()
    content_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return _ParsedPage(
        title=title,
        visible_text=visible,
        content_hash=content_hash,
        shingles=_shingles(normalized),
    )


def _shingles(text: str, width: int = 5) -> frozenset[str]:
    tokens = re.findall(r"[a-z0-9]+|[\u3400-\u9fff]", text)
    if not tokens:
        return frozenset()
    if len(tokens) < width:
        return frozenset({hashlib.sha1(" ".join(tokens).encode("utf-8")).hexdigest()[:16]})
    values = {
        hashlib.sha1(" ".join(tokens[index : index + width]).encode("utf-8")).hexdigest()[:16]
        for index in range(len(tokens) - width + 1)
    }
    return frozenset(sorted(values)[:_MAX_SHINGLES])


def _jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    union = left | right
    if not union:
        return 1.0
    return len(left & right) / len(union)
