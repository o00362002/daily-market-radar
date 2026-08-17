from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

from radar.adapters.transport import HttpRequest, HttpTransport
from radar.contracts.report import CoverageGapV2, SourceFailureV1
from radar.domain.models import Document
from radar.ports.sources import (
    CredentialsStatusV1,
    RateLimitPolicy,
    RetryPolicy,
    SourceFetchRequest,
    SourceFetchResult,
    SourceHealthV1,
)
from radar.schemas.measurement import MeasurementRegistry, MeasurementSource


@dataclass(frozen=True)
class _BlsObservation:
    metric_id: str
    series_id: str
    value: float
    year: int
    period: str
    period_name: str


@dataclass(frozen=True)
class StructuredMeasurementSourceAdapter:
    registry: MeasurementRegistry
    transport: HttpTransport
    timeout_seconds: int = 12
    adapter_id: str = "structured_measurements"
    source_id: str = "measurement_registry"
    retry_policy: RetryPolicy = RetryPolicy(max_attempts=2, backoff_seconds=0.5)
    rate_limit_policy: RateLimitPolicy = RateLimitPolicy(requests_per_minute=60)

    def credentials_status(self) -> CredentialsStatusV1:
        return CredentialsStatusV1(True)

    def health_check(self) -> SourceHealthV1:
        if not self.registry.sources:
            return SourceHealthV1("empty", "measurement registry has no configured sources")
        return SourceHealthV1("healthy", f"{len(self.registry.sources)} structured measurement sources configured")

    def fetch(self, request: SourceFetchRequest) -> SourceFetchResult:
        del request
        documents: list[Document] = []
        failures: list[SourceFailureV1] = []
        gaps: list[CoverageGapV2] = []
        checked: list[str] = []
        integration: list[tuple[str, str]] = []
        remaining_gaps: list[str] = []

        for source in self.registry.sources:
            checked.append(source.source_id)
            try:
                if source.adapter == "bls_productivity":
                    documents.append(self._fetch_bls(source))
                elif source.adapter == "defillama_protocol":
                    documents.append(self._fetch_defillama(source))
                elif source.adapter == "hyperliquid_perp":
                    documents.append(self._fetch_hyperliquid_perp(source))
                else:
                    raise ValueError(f"unsupported measurement adapter: {source.adapter}")
                integration.append((source.source_id, "checked"))
            except Exception as exc:
                reason = f"{type(exc).__name__}: {exc}"
                failures.append(
                    SourceFailureV1(
                        source_id=source.source_id,
                        reason=reason[:500],
                        channel=source.adapter,
                    )
                )
                integration.append((source.source_id, "failed"))
                message = f"structured measurement source failed: {source.source_id} ({reason[:180]})"
                remaining_gaps.append(message)
                gaps.append(
                    CoverageGapV2(
                        domain=source.primary_domain,
                        macro_region=source.macro_region,
                        language=source.language,
                        source_role="measurement",
                        channel=source.adapter,
                        time_window="latest_release",
                        reason="measurement_source_failed",
                        message=message,
                    )
                )

        return SourceFetchResult(
            documents=tuple(documents),
            coverage_gaps=tuple(gaps),
            degradation_reasons=("structured_measurement_source_failure",) if failures else (),
            sources_checked=tuple(checked),
            failures=tuple(failures),
            registry_checked=True,
            integration_status=tuple(integration),
            remaining_gaps=tuple(remaining_gaps),
        )

    @staticmethod
    def normalize(result: SourceFetchResult) -> list[Document]:
        return list(result.documents)

    def _fetch_bls(self, source: MeasurementSource) -> Document:
        fetched_at = datetime.now(timezone.utc).isoformat()
        observations: list[_BlsObservation] = []
        for metric_id, series_id in source.series:
            url = f"{source.api_base.rstrip('/')}/{series_id}"
            response = self.transport.fetch(
                HttpRequest(
                    url=url,
                    headers={"Accept": "application/json"},
                    timeout_seconds=self.timeout_seconds,
                )
            )
            if not 200 <= response.status < 300:
                raise ValueError(f"BLS HTTP {response.status} for {series_id}")
            observations.append(_parse_bls_latest(metric_id, series_id, response.body))

        periods = {(row.year, row.period) for row in observations}
        if len(periods) != 1:
            raise ValueError(f"BLS productivity series are not aligned to one latest quarter: {sorted(periods)}")
        observation_year, observation_period = next(iter(periods))
        period_name = observations[0].period_name
        facts: dict[str, object] = {"source_roles": list(source.source_roles)}
        facts.update({row.metric_id: row.value for row in observations})
        directions = [_bls_direction_phrase(row.metric_id, row.value) for row in observations]
        values = ", ".join(f"{row.metric_id}={row.value:.2f}%" for row in observations)
        series_trace = ", ".join(f"{row.metric_id}={row.series_id}" for row in observations)

        return Document.fixture(
            source_id=source.source_id,
            url=source.canonical_url,
            title="BLS " + "; ".join(directions),
            language=source.language,
            macro_region=source.macro_region,
            published_at=_bls_period_date(observation_year, observation_period),
            fetched_at=fetched_at,
            entities=["U.S. Bureau of Labor Statistics"],
            action="measures",
            object="nonfarm business productivity wages and labor share",
            location="United States",
            primary_domain=source.primary_domain,
            lane="indicator_only",
            facts=facts,
            summary=(
                f"{period_name} {observation_year} BLS nonfarm business measurements: "
                f"{'; '.join(directions)}. Values: {values}. Series: {series_trace}."
            ),
        )

    def _fetch_defillama(self, source: MeasurementSource) -> Document:
        fetched_at = datetime.now(timezone.utc).isoformat()
        endpoints = source.endpoint_map()
        tvl = _fetch_json(self.transport, source.api_base, endpoints["tvl"], self.timeout_seconds)
        fees = _fetch_json(self.transport, source.api_base, endpoints["fees"], self.timeout_seconds)
        revenue = _fetch_json(self.transport, source.api_base, endpoints["revenue"], self.timeout_seconds)

        tvl_value = _as_number(tvl, "tvl")
        fees_value = _dimension_total24h(fees, source.protocol)
        revenue_value = _dimension_total24h(revenue, source.protocol)
        return Document.fixture(
            source_id=source.source_id,
            url=source.canonical_url,
            title=f"DefiLlama {source.protocol} TVL fees and revenue measurement snapshot",
            language=source.language,
            macro_region=source.macro_region,
            published_at=fetched_at,
            fetched_at=fetched_at,
            entities=[source.protocol],
            action="measures",
            object="protocol tvl fees revenue",
            location="Global",
            primary_domain=source.primary_domain,
            lane="indicator_only",
            facts={
                "source_roles": list(source.source_roles),
                "tvl_usd": tvl_value,
                "fees_usd_24h": fees_value,
                "revenue_usd_24h": revenue_value,
            },
            summary=(
                f"Structured DefiLlama snapshot for {source.protocol}: "
                f"TVL ${tvl_value:,.0f}; 24h fees ${fees_value:,.0f}; "
                f"24h revenue ${revenue_value:,.0f}."
            ),
        )

    def _fetch_hyperliquid_perp(self, source: MeasurementSource) -> Document:
        fetched_at = datetime.now(timezone.utc).isoformat()
        payload = _fetch_post_json(
            self.transport,
            source.api_base,
            {"type": "metaAndAssetCtxs"},
            self.timeout_seconds,
        )
        volume_usd_24h, oi_usd, weighted_funding, asset_count = _hyperliquid_perp_totals(payload)
        return Document.fixture(
            source_id=source.source_id,
            url=source.canonical_url,
            title="Hyperliquid perpetual DEX 24h volume open interest and current funding snapshot",
            language=source.language,
            macro_region=source.macro_region,
            published_at=fetched_at,
            fetched_at=fetched_at,
            entities=["Hyperliquid"],
            action="measures",
            object="perpetual dex volume open interest funding rate",
            location="Global",
            primary_domain=source.primary_domain,
            lane="indicator_only",
            facts={
                "source_roles": list(source.source_roles),
                "volume_usd_24h": volume_usd_24h,
                "oi_usd": oi_usd,
                "funding_rate_oi_weighted": weighted_funding,
                "count_perp_assets": float(asset_count),
            },
            summary=(
                "Official Hyperliquid metaAndAssetCtxs snapshot across "
                f"{asset_count} perpetual assets: 24h notional volume ${volume_usd_24h:,.0f}; "
                f"open interest notional ${oi_usd:,.0f}; OI-weighted current funding rate "
                f"{weighted_funding:.8f}."
            ),
        )


def _fetch_json(transport: HttpTransport, api_base: str, path: str, timeout_seconds: int) -> Any:
    response = transport.fetch(
        HttpRequest(
            url=urljoin(api_base.rstrip("/") + "/", path.lstrip("/")),
            headers={"Accept": "application/json"},
            timeout_seconds=timeout_seconds,
        )
    )
    if not 200 <= response.status < 300:
        raise ValueError(f"measurement HTTP {response.status}: {path}")
    return json.loads(response.body.decode("utf-8"))


def _fetch_post_json(
    transport: HttpTransport,
    url: str,
    payload: dict[str, object],
    timeout_seconds: int,
) -> Any:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    response = transport.fetch(
        HttpRequest(
            url=url,
            method="POST",
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout_seconds=timeout_seconds,
            body=body,
        )
    )
    if not 200 <= response.status < 300:
        raise ValueError(f"measurement HTTP {response.status}: {url}")
    return json.loads(response.body.decode("utf-8"))


def _parse_bls_latest(metric_id: str, series_id: str, body: bytes) -> _BlsObservation:
    payload = json.loads(body.decode("utf-8"))
    if payload.get("status") != "REQUEST_SUCCEEDED":
        raise ValueError(f"BLS request failed for {series_id}: {payload.get('message')}")
    rows = payload.get("Results", {}).get("series", [])
    if not rows:
        raise ValueError(f"BLS returned no series for {series_id}")
    data = rows[0].get("data", [])
    quarterly = [row for row in data if str(row.get("period", "")).startswith("Q")]
    if not quarterly:
        raise ValueError(f"BLS returned no quarterly observations for {series_id}")
    latest = max(
        quarterly,
        key=lambda row: (int(row["year"]), int(str(row["period"])[1:])),
    )
    return _BlsObservation(
        metric_id=metric_id,
        series_id=series_id,
        value=float(latest["value"]),
        year=int(latest["year"]),
        period=str(latest["period"]),
        period_name=str(latest.get("periodName") or latest["period"]),
    )


def _bls_direction_phrase(metric_id: str, value: float) -> str:
    if metric_id == "rate_labor_productivity_yoy":
        return "productivity gain" if value >= 0 else "productivity decline"
    if metric_id == "rate_real_hourly_compensation_yoy":
        return "real wage growth" if value >= 0 else "real wage decline"
    if metric_id == "rate_labor_share_yoy":
        return "labor share growth" if value >= 0 else "labor share decline"
    return f"{metric_id} {'growth' if value >= 0 else 'decline'}"


def _bls_period_date(year: int, period: str) -> str:
    quarter = int(period[1:])
    month_day = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}[quarter]
    return datetime(year, month_day[0], month_day[1], tzinfo=timezone.utc).isoformat()


def _as_number(payload: Any, label: str) -> float:
    if isinstance(payload, bool):
        raise ValueError(f"{label} response is boolean")
    if isinstance(payload, (int, float)):
        return float(payload)
    if isinstance(payload, str):
        return float(payload)
    if isinstance(payload, dict):
        for key in (label, "value", "total", "tvl"):
            value = payload.get(key)
            if isinstance(value, (int, float, str)) and not isinstance(value, bool):
                return float(value)
    raise ValueError(f"cannot extract numeric {label} measurement")


def _dimension_total24h(payload: Any, protocol: str) -> float:
    if isinstance(payload, dict):
        direct = payload.get("total24h")
        if isinstance(direct, (int, float, str)) and not isinstance(direct, bool):
            return float(direct)
        for row in payload.get("protocols", []) if isinstance(payload.get("protocols"), list) else []:
            if str(row.get("slug", row.get("name", ""))).lower() == protocol.lower():
                value = row.get("total24h")
                if isinstance(value, (int, float, str)) and not isinstance(value, bool):
                    return float(value)
    raise ValueError(f"cannot extract DefiLlama total24h for {protocol}")


def _hyperliquid_perp_totals(payload: Any) -> tuple[float, float, float, int]:
    if not isinstance(payload, list) or len(payload) != 2:
        raise ValueError("Hyperliquid metaAndAssetCtxs response must be [meta, assetCtxs]")
    meta, contexts = payload
    universe = meta.get("universe", []) if isinstance(meta, dict) else []
    if not isinstance(universe, list) or not isinstance(contexts, list) or len(universe) != len(contexts):
        raise ValueError("Hyperliquid universe and asset contexts are not aligned")

    volume_total = 0.0
    oi_notional_total = 0.0
    funding_weighted_sum = 0.0
    measured_assets = 0
    for asset, context in zip(universe, contexts):
        if not isinstance(asset, dict) or not isinstance(context, dict):
            continue
        try:
            mark_px = float(context.get("markPx") or 0)
            open_interest = float(context.get("openInterest") or 0)
            funding = float(context.get("funding") or 0)
            day_notional_volume = float(context.get("dayNtlVlm") or 0)
        except (TypeError, ValueError):
            continue
        if mark_px < 0 or open_interest < 0 or day_notional_volume < 0:
            raise ValueError(f"negative Hyperliquid market measurement for {asset.get('name', '?')}")
        oi_notional = mark_px * open_interest
        volume_total += day_notional_volume
        oi_notional_total += oi_notional
        funding_weighted_sum += funding * oi_notional
        measured_assets += 1

    if measured_assets == 0 or oi_notional_total <= 0:
        raise ValueError("Hyperliquid returned no usable perpetual asset measurements")
    return (
        volume_total,
        oi_notional_total,
        funding_weighted_sum / oi_notional_total,
        measured_assets,
    )
