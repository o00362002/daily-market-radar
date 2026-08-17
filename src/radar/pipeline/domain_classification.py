from __future__ import annotations

from dataclasses import dataclass, replace

from radar.domain.models import Document, normalize_text
from radar.domain.text_matching import contains_term


CANONICAL_DOMAIN_RULES: dict[str, tuple[str, ...]] = {
    "global_markets_macro": (
        "market", "stock", "bond", "rate", "yield", "dollar", "gold", "oil", "etf", "fund flow",
        "inflation", "wage", "unemployment", "labor", "geopolitic", "policy", "tariff", "supply chain",
        "市場", "股票", "債券", "利率", "美元", "黃金", "原油", "資金流", "通膨", "薪資", "失業", "政策", "供應鏈",
    ),
    "ai_agents_applications": (
        "artificial intelligence", "ai", "agent", "llm", "model", "generative", "copilot", "automation",
        "saas", "enterprise ai", "cloud ai", "人工智慧", "生成式", "模型", "代理", "自動化", "企業導入", "聊天機器人",
    ),
    "crypto_rwa_agent_payments": (
        "bitcoin", "btc", "ethereum", "eth", "solana", "crypto", "blockchain", "token", "stablecoin", "rwa",
        "defi", "dex", "wallet", "defillama", "on-chain", "onchain", "代幣", "加密", "區塊鏈", "穩定幣", "代幣化", "鏈上", "虛擬資產",
    ),
    "retail_consumer_fashion": (
        "retail", "consumer", "fashion", "brand", "store", "mall", "department store", "ecommerce", "marketplace",
        "shopping", "apparel", "commerce", "零售", "消費", "服飾", "品牌", "門市", "商場", "百貨", "電商", "購物", "社群商務",
    ),
    "science_technology_industry": (
        "science", "technology", "robot", "robotics", "semiconductor", "chip", "biotech", "quantum", "space",
        "battery", "materials", "industrial", "科技", "機器人", "半導體", "晶片", "生技", "量子", "太空", "電池", "材料", "工業",
    ),
}

# A few words are valid signals in-domain but are too polysemous to carry the
# same weight as an explicit domain anchor. They remain recall candidates; the
# source prior or additional context must break ties before they can override a
# different source domain.
AMBIGUOUS_DOMAIN_TERMS: dict[str, frozenset[str]] = {
    "global_markets_macro": frozenset({"market", "policy"}),
    "ai_agents_applications": frozenset({"agent", "model", "automation", "saas"}),
    "crypto_rwa_agent_payments": frozenset({"token", "wallet"}),
    "retail_consumer_fashion": frozenset({"consumer", "brand", "store", "shopping", "commerce"}),
    "science_technology_industry": frozenset({"technology", "materials", "industrial"}),
}

# Phrase-level exclusions prevent a valid word from becoming evidence for the
# wrong proposition. This is intentionally narrow: each rule blocks only the
# ambiguous term, not the whole document, so other explicit anchors still win.
TERM_CONTEXT_EXCLUSIONS: dict[tuple[str, str], tuple[str, ...]] = {
    ("crypto_rwa_agent_payments", "token"): (
        "access token",
        "api token",
        "context token",
        "context window token",
        "design token",
        "session token",
        "token budget",
        "token count",
        "token limit",
        "token usage",
    ),
    ("retail_consumer_fashion", "retail"): (
        "retail investor",
        "retail investors",
        "retail trader",
        "retail traders",
    ),
    ("retail_consumer_fashion", "store"): (
        "app store",
        "application store",
        "data store",
        "object store",
        "play store",
        "store of value",
    ),
    ("retail_consumer_fashion", "consumer"): (
        "consumer confidence",
        "consumer price",
        "consumer prices",
        "consumer price index",
    ),
    ("retail_consumer_fashion", "brand"): ("brand new",),
    ("retail_consumer_fashion", "commerce"): (
        "commerce department",
        "department of commerce",
    ),
}

DOMAIN_ALIASES = {
    "policy_geopolitics": "global_markets_macro",
    "labor_demographics_consumption_pressure": "global_markets_macro",
}


@dataclass(frozen=True)
class DomainClassification:
    domain: str
    score: int
    matched_terms: tuple[str, ...]
    source_prior_used: bool


def _document_text(document: Document) -> tuple[str, str]:
    title = normalize_text(document.title)
    body = normalize_text(
        " ".join(
            [
                document.summary,
                document.action,
                document.object,
                document.location,
                " ".join(document.entities),
            ]
        )
    )
    return title, body


def _term_allowed(domain: str, term: str, text: str) -> bool:
    exclusions = TERM_CONTEXT_EXCLUSIONS.get((domain, term), ())
    return not any(contains_term(text, phrase) for phrase in exclusions)


def _matched_terms(domain: str, text: str, terms: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        term
        for term in terms
        if contains_term(text, term) and _term_allowed(domain, term, text)
    )


def _term_weight(domain: str, term: str, *, in_title: bool) -> int:
    ambiguous = term in AMBIGUOUS_DOMAIN_TERMS.get(domain, frozenset())
    if in_title:
        return 2 if ambiguous else 4
    return 1


def classify_document_domain(
    document: Document,
    *,
    canonical_domains: tuple[str, ...] | list[str] | None = None,
    domain_aliases: dict[str, str] | None = None,
) -> DomainClassification:
    allowed = tuple(canonical_domains or CANONICAL_DOMAIN_RULES)
    aliases = domain_aliases or DOMAIN_ALIASES
    source_domain = aliases.get(document.primary_domain, document.primary_domain)
    title, body = _document_text(document)
    ranked: list[tuple[int, str, tuple[str, ...]]] = []
    for domain in allowed:
        terms = CANONICAL_DOMAIN_RULES.get(domain, ())
        title_hits = _matched_terms(domain, title, terms)
        body_hits = tuple(
            term
            for term in _matched_terms(domain, body, terms)
            if term not in title_hits
        )
        source_prior = 2 if source_domain == domain else 0
        score = (
            sum(_term_weight(domain, term, in_title=True) for term in title_hits)
            + sum(_term_weight(domain, term, in_title=False) for term in body_hits)
            + source_prior
        )
        ranked.append((score, domain, title_hits + body_hits))
    ranked.sort(key=lambda row: (-row[0], 0 if row[1] == source_domain else 1, row[1]))
    score, domain, hits = ranked[0]
    if score < 4 and source_domain in allowed:
        return DomainClassification(source_domain, 2, (), True)
    return DomainClassification(domain, score, hits, domain == source_domain and not hits)


def classify_documents(
    documents: list[Document],
    *,
    canonical_domains: tuple[str, ...] | list[str] | None = None,
    domain_aliases: dict[str, str] | None = None,
) -> list[Document]:
    return [
        replace(
            document,
            primary_domain=classify_document_domain(
                document,
                canonical_domains=canonical_domains,
                domain_aliases=domain_aliases,
            ).domain,
        )
        for document in documents
    ]
