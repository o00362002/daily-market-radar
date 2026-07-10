"""Deterministic, feature-traced evaluators for the fixed report matrices.

Every observation carries a feature trace (``data_checked``) that explains why a
cell was scored the way it was. No cell ever receives a fixed production score:
when the deterministic evidence is absent the cell is ``insufficient`` and no
trend is fabricated.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from radar.contracts.report import MatrixObservationV1, StructuralIndicatorObservationV1
from radar.domain.models import Event, normalize_text

# Retail matrix key -> (canonical metric namespaces, keyword triggers).
_RETAIL_FEATURES: dict[str, tuple[set[str], set[str]]] = {
    "cost_pressure": ({"cost", "margin", "price"}, {"cost", "margin", "inflation", "成本", "毛利"}),
    "channel_offline_department_store_mall_street": ({"traffic", "sales"}, {"store", "mall", "department", "門市", "百貨", "商圈"}),
    "channel_online_marketplace_social_commerce": ({"traffic", "sales"}, {"marketplace", "ecommerce", "online", "電商", "網購", "直播"}),
    "product_fashion_style_assortment_material_fit_category": ({"assortment"}, {"fashion", "style", "assortment", "category", "款式", "品類", "選品"}),
    "inventory_markdown_mid_price_pressure": ({"inventory", "price"}, {"inventory", "markdown", "discount", "庫存", "折扣", "降價"}),
    "membership_crm_loyalty_retail_media": ({"membership"}, {"membership", "loyalty", "crm", "會員", "忠誠"}),
    "social_commerce_content_discovery_ai_referral": ({"traffic"}, {"social", "content", "referral", "ai", "社群", "內容"}),
    "true_vs_fake_segmentation": (set(), {"premium", "value", "polarization", "分眾", "兩極"}),
    "taiwan_retail_commercial_district_department_store_brand": (set(), {"taiwan", "台灣", "台北", "百貨", "商圈"}),
}

# Crypto matrix key -> (canonical metric namespaces, keyword triggers).
_CRYPTO_FEATURES: dict[str, tuple[set[str], set[str]]] = {
    "btc_eth_sol_market_structure": ({"price", "volume"}, {"btc", "eth", "sol", "bitcoin", "ethereum", "solana"}),
    "etf_flows": ({"flow"}, {"etf", "inflow", "outflow"}),
    "stablecoin_supply_and_dry_powder": ({"supply"}, {"stablecoin", "usdt", "usdc", "穩定幣"}),
    "rwa_tokenized_assets": ({"amount"}, {"rwa", "tokenized", "tokenization", "代幣化"}),
    "perp_dex_volume_oi_funding": ({"oi", "volume", "funding"}, {"perp", "dex", "open interest", "funding"}),
    "tvl_fees_revenue": ({"tvl", "fees", "revenue"}, {"tvl", "fees", "revenue", "手續費"}),
    "regulation_policy": (set(), {"regulation", "sec", "policy", "監管", "法規"}),
    "taiwan_crypto_fixed_sources": (set(), {"taiwan", "台灣", "金管會", "vasp"}),
}

_STRUCTURAL_FEATURES: dict[str, dict[str, set[str]]] = {
    "k_shaped_ai_productivity_economy": {
        "support": {"productivity", "automation", "layoff", "efficiency", "生產力", "自動化", "裁員"},
        "counter": {"broad wage", "inclusive", "shared", "普遍加薪", "共享"},
    },
    "ai_bubble_overinvestment": {
        "support": {"capex", "overinvestment", "valuation", "bubble", "資本支出", "泡沫", "估值"},
        "counter": {"profitable", "revenue", "adoption", "獲利", "營收落地"},
    },
    "brand_market_polarization_and_true_vs_fake_segmentation": {
        "support": {"premium", "luxury", "value", "polarization", "分眾", "兩極", "精品"},
        "counter": {"mid-market", "middle", "均衡", "中間層回升"},
    },
}


def _event_text(event: Event) -> str:
    parts: list[str] = []
    for document in event.documents:
        parts.extend([document.title, document.action, document.object, document.summary, " ".join(document.entities)])
    return normalize_text(" ".join(parts))


def _event_metrics(event: Event) -> set[str]:
    return {
        metric.split("_", 1)[0]
        for document in event.documents
        for metric in document.facts
        if metric != "source_roles"
    }


def _keyword_hit(text: str, keywords: set[str]) -> list[str]:
    return sorted(keyword for keyword in keywords if keyword in text)


def _evaluate_matrix(
    events: list[Event],
    keys: list[str],
    features: dict[str, tuple[set[str], set[str]]],
    domain: str,
    empty_gap: str,
) -> dict[str, MatrixObservationV1]:
    observations: dict[str, MatrixObservationV1] = {}
    for key in keys:
        namespaces, keywords = features.get(key, (set(), set()))
        signal_ids: list[str] = []
        data_checked: list[str] = []
        for event in events:
            text = _event_text(event)
            metric_hits = sorted(_event_metrics(event) & namespaces)
            keyword_hits = _keyword_hit(text, keywords)
            if metric_hits or keyword_hits:
                signal_ids.append(event.event_id)
                data_checked.extend(f"metric:{name}" for name in metric_hits)
                data_checked.extend(f"keyword:{name}" for name in keyword_hits)
        if signal_ids:
            observations[key] = MatrixObservationV1(
                status="observed",
                signal_ids=sorted(set(signal_ids)),
                data_checked=sorted(set(data_checked)),
                gap="",
            )
        else:
            observations[key] = MatrixObservationV1(
                status="insufficient",
                signal_ids=[],
                data_checked=[],
                gap=empty_gap,
            )
    return observations


def evaluate_retail_matrix(events: list[Event], keys: list[str]) -> dict[str, MatrixObservationV1]:
    return _evaluate_matrix(
        events,
        keys,
        _RETAIL_FEATURES,
        "retail_consumer_fashion",
        "no retail measurement or keyword evidence in this run",
    )


def evaluate_crypto_matrix(events: list[Event], keys: list[str]) -> dict[str, MatrixObservationV1]:
    return _evaluate_matrix(
        events,
        keys,
        _CRYPTO_FEATURES,
        "crypto_rwa_agent_payments",
        "no crypto measurement or keyword evidence in this run",
    )


def _observation_date(observation: StructuralIndicatorObservationV1) -> datetime:
    parsed = datetime.fromisoformat(observation.observation_date.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def rolling_summary(
    observations: list[StructuralIndicatorObservationV1],
    *,
    as_of: str,
) -> dict[str, dict[str, float | int | str]]:
    """Aggregate stored observations into current / 7d / 30d / 90d windows.

    Only real observations feed the windows; an empty window is reported as
    ``insufficient`` rather than a fabricated trend.
    """

    as_of_dt = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
    if as_of_dt.tzinfo is None:
        as_of_dt = as_of_dt.replace(tzinfo=timezone.utc)
    ordered = sorted(observations, key=_observation_date)

    def window(days: int | None) -> dict[str, float | int | str]:
        if days is None:
            scoped = ordered[-1:]
        else:
            start = as_of_dt - timedelta(days=days)
            scoped = [obs for obs in ordered if start <= _observation_date(obs) <= as_of_dt]
        rated = [obs for obs in scoped if obs.direction != "insufficient"]
        if not rated:
            return {"status": "insufficient", "observations": len(scoped), "avg_support": 0, "avg_counter": 0}
        return {
            "status": "observed",
            "observations": len(rated),
            "avg_support": round(sum(obs.support_score for obs in rated) / len(rated), 2),
            "avg_counter": round(sum(obs.counter_score for obs in rated) / len(rated), 2),
        }

    return {
        "current": window(None),
        "rolling_7d": window(7),
        "rolling_30d": window(30),
        "rolling_90d": window(90),
    }


def evaluate_structural_indicators(
    events: list[Event],
    indicator_ids: list[str],
    *,
    observation_date: str,
) -> list[StructuralIndicatorObservationV1]:
    observations: list[StructuralIndicatorObservationV1] = []
    for indicator_id in indicator_ids:
        features = _STRUCTURAL_FEATURES.get(indicator_id, {"support": set(), "counter": set()})
        support_ids: list[str] = []
        counter_ids: list[str] = []
        checked: list[str] = []
        for event in events:
            text = _event_text(event)
            support_hits = _keyword_hit(text, features["support"])
            counter_hits = _keyword_hit(text, features["counter"])
            if support_hits:
                support_ids.append(event.event_id)
                checked.extend(f"support:{name}" for name in support_hits)
            if counter_hits:
                counter_ids.append(event.event_id)
                checked.extend(f"counter:{name}" for name in counter_hits)

        if not support_ids and not counter_ids:
            observations.append(
                StructuralIndicatorObservationV1(
                    indicator_id=indicator_id,
                    observation_date=observation_date,
                    direction="insufficient",
                    support_score=0,
                    counter_score=0,
                    confidence="insufficient",
                    supporting_signal_ids=[],
                    counter_signal_ids=[],
                    missing_data=["no supporting or counter evidence observed this run"],
                    one_sentence_read="Insufficient verified evidence for a directional update.",
                    next_verification=["run indicator-specific evidence checks"],
                    evaluation_mode="deterministic",
                )
            )
            continue

        support_score = min(100, 20 * len(set(support_ids)))
        counter_score = min(100, 20 * len(set(counter_ids)))
        direction = "supporting" if support_score > counter_score else "counter" if counter_score > support_score else "mixed"
        observations.append(
            StructuralIndicatorObservationV1(
                indicator_id=indicator_id,
                observation_date=observation_date,
                direction=direction,
                support_score=support_score,
                counter_score=counter_score,
                confidence=min(100, support_score + counter_score),
                supporting_signal_ids=sorted(set(support_ids)),
                counter_signal_ids=sorted(set(counter_ids)),
                missing_data=[],
                one_sentence_read=f"Deterministic keyword evidence leans {direction} for this indicator.",
                next_verification=["confirm with structured measurement facts and independent sources"],
                evaluation_mode="deterministic",
            )
        )
    return observations
