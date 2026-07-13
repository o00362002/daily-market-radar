"""Deterministic, feature-traced evaluators for the fixed report matrices.

Every observation carries a feature trace (``data_checked``) that explains why a
cell was scored the way it was. No cell ever receives a fixed production score:
when the deterministic evidence is absent the cell is ``insufficient`` and no
trend is fabricated.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from radar.contracts.report import (
    MatrixObservationV1,
    StructuralIndicatorComponentV1,
    StructuralIndicatorEvidenceV1,
    StructuralIndicatorObservationV1,
)
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

# Component-level evidence is deliberately explicit.  The three structural
# indicators are conclusions; these components are the observable dimensions
# that explain how the conclusion was reached.
_STRUCTURAL_COMPONENTS: dict[str, tuple[tuple[str, str, set[str], set[str]], ...]] = {
    "k_shaped_ai_productivity_economy": (
        ("labor_market", "勞動力與就業環境", {"layoff", "hiring", "job", "裁員", "招聘", "就業"}, {"broad hiring", "普遍招聘"}),
        ("wage_income", "薪資與所得分配", {"wage", "income", "salary", "薪資", "所得"}, {"real wage growth", "實質薪資成長"}),
        ("productivity_sharing", "生產力與利益分享", {"productivity", "automation", "efficiency", "生產力", "自動化", "效率"}, {"shared", "共享", "inclusive"}),
        ("firm_size_gap", "大企業與中小企業落差", {"large firm", "platform", "moat", "大企業", "平台", "護城河"}, {"sme adoption", "中小企業採用"}),
        ("consumption_polarization", "消費分化與中間層壓力", {"premium", "value", "middle", "consumer", "高端", "低價", "中間層", "消費"}, {"broad consumption", "廣泛消費"}),
    ),
    "ai_bubble_overinvestment": (
        ("capex_revenue", "資本支出與 AI 營收", {"capex", "capital expenditure", "資本支出", "營收"}, {"revenue growth", "營收成長"}),
        ("financing_debt", "資料中心融資與債務", {"debt", "financing", "project finance", "債務", "融資"}, {"cash flow", "營運現金流"}),
        ("utilization_roi", "使用率與企業 ROI", {"utilization", "roi", "adoption", "使用率", "投資報酬", "採用"}, {"paid adoption", "付費採用"}),
        ("pricing_margin", "價格競爭與推理毛利", {"price competition", "margin", "inference", "價格競爭", "毛利", "推理成本"}, {"margin expansion", "毛利擴張"}),
        ("valuation_power", "估值、電力與基礎設施壓力", {"valuation", "bubble", "power", "gpu", "估值", "泡沫", "電力", "GPU"}, {"profitable", "獲利"}),
    ),
    "brand_market_polarization_and_true_vs_fake_segmentation": (
        ("brand_tiers", "品牌層級與市場集中", {"premium", "luxury", "share", "精品", "高端", "市占"}, {"mid-market recovery", "中間層回升"}),
        ("mid_market_pressure", "中價位、折扣與關店壓力", {"mid-market", "discount", "closure", "中價位", "折扣", "撤店", "關店"}, {"full price", "正價"}),
        ("niche_strength", "小眾品牌與社群韌性", {"niche", "community", "identity", "小眾", "社群", "身份"}, {"generic", "同質化"}),
        ("channel_attention", "平台流量、通路與注意力", {"platform", "marketplace", "algorithm", "traffic", "平台", "電商", "演算法", "流量"}, {"discovery tools", "發現工具"}),
        ("true_vs_fake_segmentation", "真分眾與假分眾", {"segmentation", "personalization", "persona", "分眾", "個人化", "人群"}, {"repeat", "sell-through", "回購", "售罄"}),
    ),
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


def _event_evidence(event: Event, *, direction: str, hits: list[str]) -> StructuralIndicatorEvidenceV1:
    document = event.documents[0]
    summary = document.summary.strip() or f"{document.action or '事件'}：{document.object or document.title}。"
    return StructuralIndicatorEvidenceV1(
        event_id=event.event_id,
        headline=document.title,
        summary=f"{summary}（命中：{'、'.join(hits)}）",
        direction=direction,
    )


def _component_observations(
    events: list[Event],
    indicator_id: str,
) -> list[StructuralIndicatorComponentV1]:
    rows: list[StructuralIndicatorComponentV1] = []
    for component_id, label, support_keywords, counter_keywords in _STRUCTURAL_COMPONENTS.get(indicator_id, ()):
        support_events: list[Event] = []
        counter_events: list[Event] = []
        evidence: list[StructuralIndicatorEvidenceV1] = []
        for event in events:
            text = _event_text(event)
            support_hits = _keyword_hit(text, support_keywords)
            counter_hits = _keyword_hit(text, counter_keywords)
            if support_hits:
                support_events.append(event)
                evidence.append(_event_evidence(event, direction="toward", hits=support_hits))
            if counter_hits:
                counter_events.append(event)
                evidence.append(_event_evidence(event, direction="against", hits=counter_hits))
        support_score = min(100, 25 * len({event.event_id for event in support_events}))
        counter_score = min(100, 25 * len({event.event_id for event in counter_events}))
        if not evidence:
            direction = "insufficient"
            score = 0
            missing_data = ["本次沒有足夠新聞或量化資料支撐此細分指標。"]
        else:
            direction = "toward" if support_score > counter_score else "against" if counter_score > support_score else "mixed"
            score = max(0, min(100, round(50 + (support_score - counter_score) / 2)))
            missing_data = []
        rows.append(
            StructuralIndicatorComponentV1(
                component_id=component_id,
                label=label,
                direction=direction,
                score=score,
                support_score=support_score,
                counter_score=counter_score,
                evidence=evidence,
                missing_data=missing_data,
            )
        )
    return rows


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
                    components=_component_observations(events, indicator_id),
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
                components=_component_observations(events, indicator_id),
            )
        )
    return observations
