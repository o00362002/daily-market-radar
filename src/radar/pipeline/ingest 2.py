from __future__ import annotations

from radar.domain.models import Document


def ingest_fixture_documents() -> list[Document]:
    rows = [
        ("openai_news", "https://openai.com/news/agent-runtime", "OpenAI launches agent runtime", "en", "North America", "ai_agents_applications", "OpenAI", "launches", "agent runtime", "US", "top_down"),
        ("twse", "https://www.twse.com.tw/news/etf", "TWSE reports ETF flow update", "zh-Hant", "Taiwan", "global_markets_macro", "TWSE", "reports", "ETF flows", "Taiwan", "top_down"),
        ("nikkei", "https://example.jp/robots", "Japanese robot startup pilots retail assistant", "ja", "East Asia", "science_technology_industry", "RobotCo", "pilots", "retail assistant", "Japan", "bottom_up"),
        ("eu_policy", "https://example.eu/policy", "EU regulator opens AI procurement sandbox", "en", "Europe", "policy_geopolitics", "EU regulator", "opens", "AI procurement sandbox", "Europe", "top_down"),
        ("coindesk", "https://www.coindesk.com/rwa", "Bank pilots tokenized settlement", "en", "North America", "crypto_rwa_agent_payments", "Bank", "pilots", "tokenized settlement", "US", "bottom_up"),
        ("retail_dive", "https://www.retaildive.com/news/store-format", "Retailer tests neighborhood store format", "en", "North America", "retail_consumer_fashion", "Retailer", "tests", "neighborhood store format", "US", "bottom_up"),
        ("bls", "https://www.bls.gov/news", "Labor data shows wage pressure easing", "en", "North America", "labor_demographics_consumption_pressure", "BLS", "reports", "wage pressure", "US", "top_down"),
    ]
    return [
        Document.fixture(
            source_id=source_id,
            url=url,
            title=title,
            language=language,
            macro_region=region,
            primary_domain=domain,
            entities=[entity],
            action=action,
            object=obj,
            location=location,
            lane=lane,
        )
        for source_id, url, title, language, region, domain, entity, action, obj, location, lane in rows
    ]
