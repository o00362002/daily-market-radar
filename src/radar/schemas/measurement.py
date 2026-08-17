from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


@dataclass(frozen=True)
class MeasurementSource:
    source_id: str
    name: str
    adapter: str
    canonical_url: str
    api_base: str
    primary_domain: str
    macro_region: str
    language: str
    source_roles: tuple[str, ...]
    series: tuple[tuple[str, str], ...] = ()
    protocol: str = ""
    endpoints: tuple[tuple[str, str], ...] = ()

    def series_map(self) -> dict[str, str]:
        return dict(self.series)

    def endpoint_map(self) -> dict[str, str]:
        return dict(self.endpoints)


@dataclass(frozen=True)
class MeasurementRegistry:
    version: str
    sources: tuple[MeasurementSource, ...] = field(default_factory=tuple)

    @classmethod
    def from_file(cls, path: Path) -> "MeasurementRegistry":
        payload = json.loads(path.read_text(encoding="utf-8"))
        sources = tuple(
            MeasurementSource(
                source_id=str(row["source_id"]),
                name=str(row["name"]),
                adapter=str(row["adapter"]),
                canonical_url=str(row["canonical_url"]),
                api_base=str(row["api_base"]),
                primary_domain=str(row["primary_domain"]),
                macro_region=str(row["macro_region"]),
                language=str(row["language"]),
                source_roles=tuple(str(value) for value in row.get("source_roles", ())),
                series=tuple(
                    sorted((str(key), str(value)) for key, value in row.get("series", {}).items())
                ),
                protocol=str(row.get("protocol", "")),
                endpoints=tuple(
                    sorted((str(key), str(value)) for key, value in row.get("endpoints", {}).items())
                ),
            )
            for row in payload.get("sources", ())
        )
        registry = cls(version=str(payload["version"]), sources=sources)
        registry.validate()
        return registry

    def validate(self) -> None:
        if not self.version:
            raise ValueError("measurement registry version is required")
        ids = [source.source_id for source in self.sources]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate measurement source_id")
        for source in self.sources:
            if not source.source_id or not source.name:
                raise ValueError("measurement source identity is required")
            for url in (source.canonical_url, source.api_base):
                parts = urlsplit(url)
                if parts.scheme != "https" or not parts.netloc:
                    raise ValueError(f"invalid measurement source URL: {url}")
            if source.adapter == "bls_productivity":
                if not source.series:
                    raise ValueError("BLS measurement source requires series mapping")
                for metric_id, series_id in source.series:
                    if not metric_id.startswith(("rate_", "ratio_", "index_", "amount_")):
                        raise ValueError(f"BLS metric is not canonical: {metric_id}")
                    if not series_id.startswith("PRS"):
                        raise ValueError(f"unexpected BLS productivity series id: {series_id}")
            elif source.adapter == "defillama_protocol":
                if not source.protocol:
                    raise ValueError("DefiLlama measurement source requires protocol")
                endpoints = source.endpoint_map()
                if not {"tvl", "fees", "revenue"}.issubset(endpoints):
                    raise ValueError("DefiLlama source requires tvl, fees and revenue endpoints")
                if any(not path.startswith("/") for path in endpoints.values()):
                    raise ValueError("DefiLlama endpoint paths must be relative to api_base")
            elif source.adapter == "hyperliquid_perp":
                parts = urlsplit(source.api_base)
                if parts.netloc != "api.hyperliquid.xyz" or parts.path.rstrip("/") != "/info":
                    raise ValueError("Hyperliquid perp source must use the official /info endpoint")
                if "official" not in source.source_roles or "exchange" not in source.source_roles:
                    raise ValueError("Hyperliquid perp source must retain official exchange source roles")
            elif source.adapter == "farside_etf":
                parts = urlsplit(source.canonical_url)
                if parts.netloc != "farside.co.uk" or parts.path.rstrip("/") != "/btc":
                    raise ValueError("Farside ETF source must use the fixed Bitcoin flow table")
                if not {"specialist", "data"}.issubset(set(source.source_roles)):
                    raise ValueError("Farside ETF source must retain specialist data roles")
            elif source.adapter == "fsc_vasp_law":
                parts = urlsplit(source.canonical_url)
                query = parse_qs(parts.query)
                if parts.netloc != "law.fsc.gov.tw" or query.get("id") != ["GL004301"]:
                    raise ValueError("FSC VASP source must use the fixed official law record")
                required_roles = {"official", "regulator", "government"}
                if source.macro_region != "Taiwan" or not required_roles.issubset(source.source_roles):
                    raise ValueError("FSC VASP source must retain Taiwan official regulator roles")
            else:
                raise ValueError(f"unknown measurement adapter: {source.adapter}")
