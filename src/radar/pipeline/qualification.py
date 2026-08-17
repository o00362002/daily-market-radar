from __future__ import annotations

from dataclasses import dataclass

from radar.domain.models import Event
from radar.domain.potential import assess_event
from radar.domain.text_matching import matching_terms, normalize_for_matching


REPORT_ANCHOR_TERMS: dict[str, tuple[str, ...]] = {
    "global_markets_macro": (
        "inflation", "interest rate", "yield", "bond", "currency", "dollar", "yen", "yuan", "euro",
        "rupee", "oil", "crude", "gold", "energy", "tariff", "trade", "export", "import", "sanction",
        "supply chain", "central bank", "federal reserve", "ecb", "bank of japan", "world bank", "imf",
        "gdp", "economy", "economic", "unemployment", "wage", "layoff", "job cuts", "debt", "budget",
        "credit", "loan", "ipo", "earnings", "revenue", "profit", "loss", "sales", "market cap",
        "stock market", "stocks", "shares", "fund", "etf", "investment", "investor", "merger",
        "acquisition", "manufacturing", "factory", "production", "capacity", "semiconductor", "chip",
        "bitcoin", "crypto", "retail", "consumer",
        "關稅", "通膨", "利率", "殖利率", "債券", "匯率", "美元", "日圓", "人民幣", "歐元",
        "原油", "油價", "黃金", "能源", "貿易", "出口", "進口", "制裁", "供應鏈", "央行",
        "聯準會", "經濟", "景氣", "失業", "薪資", "裁員", "債務", "預算", "信貸", "貸款",
        "上市", "財報", "營收", "獲利", "虧損", "銷售", "市值", "股市", "股票", "資金",
        "基金", "投資", "併購", "收購", "製造", "工廠", "產能", "半導體", "晶片", "比特幣",
        "加密", "零售", "消費",
    ),
    "ai_agents_applications": (
        "artificial intelligence", "ai", "agent", "agentic", "llm", "model", "chatbot", "copilot",
        "automation", "openai", "anthropic", "claude", "gemini", "gpt", "machine learning",
        "人工智慧", "生成式", "模型", "代理", "自動化", "聊天機器人", "機器學習", "大模型",
    ),
    "crypto_rwa_agent_payments": (
        "bitcoin", "btc", "ethereum", "eth", "solana", "crypto", "blockchain", "token", "stablecoin",
        "rwa", "defi", "dex", "web3", "加密", "區塊鏈", "代幣", "穩定幣", "鏈上", "虛擬資產",
        "比特幣", "以太坊", "索拉納",
    ),
    "retail_consumer_fashion": (
        "retail", "consumer", "fashion", "brand", "store", "mall", "department store", "ecommerce",
        "e-commerce", "marketplace", "shopping", "apparel", "commerce", "pos", "inventory",
        "merchandising", "零售", "消費", "服飾", "品牌", "門市", "商場", "百貨", "電商", "購物",
        "社群商務", "庫存", "補貨", "會員",
    ),
    "science_technology_industry": (
        "robot", "robotics", "semiconductor", "chip", "biotech", "quantum", "space", "battery",
        "material", "industrial", "cybersecurity", "vulnerability", "software", "hardware", "cloud",
        "data center", "server", "network", "機器人", "半導體", "晶片", "生技", "量子", "太空",
        "電池", "材料", "工業", "資安", "漏洞", "軟體", "硬體", "雲端", "資料中心", "伺服器", "網路",
    ),
}

HIGH_IMPACT_CHANGE_TERMS: tuple[str, ...] = (
    "launch", "release", "rollout", "deploy", "adopt", "adoption", "funding", "acquire", "acquisition",
    "merge", "merger", "regulation", "regulatory", "tariff", "sanction", "earnings", "revenue", "profit",
    "loss", "price", "cost", "outage", "breach", "vulnerability", "contract", "order", "investment",
    "layoff", "hiring", "production", "capacity", "supply", "demand", "sales", "shutdown", "fine",
    "wage change", "wage changes",
    "推出", "發布", "上線", "部署", "導入", "採用", "募資", "收購", "併購", "監管", "關稅", "制裁",
    "財報", "營收", "獲利", "虧損", "價格", "成本", "中斷", "漏洞", "合約", "訂單", "投資", "裁員",
    "招聘", "產能", "供應", "需求", "銷售", "停產", "罰款", "薪資變化", "薪資調整",
)

GLOBAL_MACRO_TRANSMISSION_TERMS: tuple[str, ...] = (
    "oil", "crude", "energy", "tariff", "trade", "export", "import", "sanction", "supply chain",
    "inflation", "interest rate", "yield", "bond", "currency", "dollar", "gold", "gdp", "economy",
    "unemployment", "wage", "debt", "credit", "earnings", "revenue", "profit", "price", "market",
    "stock", "fund", "investment", "manufacturing", "factory", "production", "capacity", "semiconductor",
    "bitcoin", "crypto", "consumer", "retail",
    "原油", "油價", "能源", "關稅", "貿易", "出口", "進口", "制裁", "供應鏈", "通膨", "利率",
    "殖利率", "債券", "匯率", "美元", "黃金", "經濟", "景氣", "失業", "薪資", "債務", "信貸",
    "財報", "營收", "獲利", "價格", "市場", "股市", "股票", "基金", "投資", "製造", "工廠",
    "產能", "半導體", "比特幣", "加密", "消費", "零售",
)


@dataclass(frozen=True)
class ReportQualification:
    qualified: bool
    reason: str
    anchor_terms: tuple[str, ...] = ()
    change_terms: tuple[str, ...] = ()


def assess_report_qualification(event: Event) -> ReportQualification:
    if not event.documents:
        return ReportQualification(False, "event_has_no_documents")
    if all(document.lane == "indicator_only" for document in event.documents):
        return ReportQualification(False, "indicator_only_measurement")

    potential = assess_event(event)
    if potential.lane == "potential":
        return ReportQualification(True, "content_qualified_potential")

    anchor_hits: list[str] = []
    impact_hits: list[str] = []
    transmission_hits: list[str] = []
    has_measurements = False
    source_ids: set[str] = set()
    domains: set[str] = set()

    for document in event.documents:
        text = normalize_for_matching(" ".join(part for part in (document.title, document.summary) if part))
        domain = document.primary_domain
        domains.add(domain)
        source_ids.add(document.source_id)
        anchor_hits.extend(matching_terms(text, REPORT_ANCHOR_TERMS.get(domain, ())))
        impact_hits.extend(matching_terms(text, HIGH_IMPACT_CHANGE_TERMS))
        if domain == "global_markets_macro":
            transmission_hits.extend(matching_terms(text, GLOBAL_MACRO_TRANSMISSION_TERMS))
        has_measurements = has_measurements or bool(document.facts.measurements)

    anchors = tuple(dict.fromkeys(anchor_hits))
    impacts = tuple(dict.fromkeys(impact_hits))
    transmissions = tuple(dict.fromkeys(transmission_hits))
    macro_only = domains == {"global_markets_macro"}
    has_transmission = bool(transmissions) if macro_only else True

    explicit_impact = bool(anchors and impacts and has_transmission)
    corroborated = len(source_ids) >= 2 and explicit_impact
    structured = has_measurements and bool(domains)

    if explicit_impact:
        return ReportQualification(True, "major_has_explicit_transmission_and_change", anchors, impacts)
    if corroborated:
        return ReportQualification(True, "major_is_independently_corroborated", anchors, impacts)
    if structured:
        return ReportQualification(True, "major_has_structured_measurement", anchors, impacts)
    if macro_only and anchors and impacts and not transmissions:
        return ReportQualification(False, "macro_story_has_no_economic_transmission", anchors, impacts)
    return ReportQualification(False, "generic_or_low_materiality_feed_story", anchors, impacts)
