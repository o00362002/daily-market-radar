"""Feature dictionaries for deterministic Retail/Crypto/structural evaluation.

Retail and Crypto matrices use domain + typed feature matching. Structural indicators
are stricter: a candidate phrase is only scoreable after domain relevance,
proposition-entailment and measurement-evidence gates have all passed.
"""

RETAIL_FEATURES: dict[str, tuple[set[str], set[str]]] = {
    "cost_pressure": ({"cost", "margin", "price"}, {"cost pressure", "margin pressure", "inflation", "成本壓力", "毛利壓力"}),
    "channel_offline_department_store_mall_street": ({"traffic", "sales"}, {"store traffic", "mall traffic", "department store", "門市來客", "百貨", "商圈"}),
    "channel_online_marketplace_social_commerce": ({"traffic", "sales"}, {"marketplace", "ecommerce", "online sales", "social commerce", "電商", "網購", "直播電商"}),
    "product_fashion_style_assortment_material_fit_category": ({"assortment"}, {"fashion", "assortment", "product category", "material", "fit", "款式", "品類", "選品", "材質", "版型"}),
    "inventory_markdown_mid_price_pressure": ({"inventory", "price"}, {"inventory", "markdown", "discount", "mid-market", "庫存", "折扣", "降價", "中價位"}),
    "membership_crm_loyalty_retail_media": ({"membership"}, {"membership", "loyalty", "crm", "retail media", "會員", "忠誠", "零售媒體"}),
    "social_commerce_content_discovery_ai_referral": ({"traffic"}, {"social commerce", "content discovery", "ai referral", "ai shopping", "社群導購", "內容發現", "AI 導購"}),
    "true_vs_fake_segmentation": (set(), {"premium segment", "value segment", "market polarization", "customer segmentation", "高端客群", "低價客群", "市場兩極", "客群分眾"}),
    "taiwan_retail_commercial_district_department_store_brand": (set(), {"taiwan retail", "台灣零售", "台北百貨", "百貨", "商圈"}),
}

CRYPTO_FEATURES: dict[str, tuple[set[str], set[str]]] = {
    "btc_eth_sol_market_structure": ({"price", "volume"}, {"btc", "eth", "sol", "bitcoin", "ethereum", "solana"}),
    "etf_flows": ({"flow"}, {"bitcoin etf", "ethereum etf", "crypto etf", "etf inflow", "etf outflow"}),
    "stablecoin_supply_and_dry_powder": ({"supply"}, {"stablecoin", "usdt", "usdc", "穩定幣"}),
    "rwa_tokenized_assets": ({"amount"}, {"rwa", "tokenized asset", "tokenized securities", "tokenization", "代幣化資產", "代幣化證券"}),
    "perp_dex_volume_oi_funding": ({"oi", "volume", "funding"}, {"perp dex", "perpetual dex", "open interest", "funding rate", "永續合約", "資金費率"}),
    "tvl_fees_revenue": ({"tvl", "fees", "revenue"}, {"tvl", "protocol fees", "protocol revenue", "協議手續費", "協議收入"}),
    "regulation_policy": (set(), {"crypto regulation", "digital asset regulation", "virtual asset regulation", "vasp", "加密監管", "虛擬資產法規", "虛擬資產服務法"}),
    "taiwan_crypto_fixed_sources": (set(), {"taiwan crypto", "taiwan vasp", "台灣虛擬資產", "金管會", "vasp"}),
}

# Candidate phrases only. These no longer score directly; matrices.py requires every
# event to pass STRUCTURAL_COMPONENT_GATES before it can become support/counter evidence.
STRUCTURAL_COMPONENTS: dict[str, tuple[tuple[str, str, set[str], set[str]], ...]] = {
    "k_shaped_ai_productivity_economy": (
        (
            "labor_market",
            "勞動力與就業環境",
            {"layoff", "layoffs", "job cuts", "hiring freeze", "unemployment rises", "entry-level jobs decline", "裁員", "凍結招聘", "失業率上升", "初階職缺下降"},
            {"broad hiring", "broad employment growth", "ai-augmented hiring", "普遍招聘", "廣泛就業成長", "AI 協作職缺成長"},
        ),
        (
            "wage_income",
            "薪資與所得分配",
            {"real wage decline", "real wages fall", "wage stagnation", "labor share decline", "household income decline", "實質薪資下降", "薪資停滯", "勞動份額下降", "家庭所得下降"},
            {"real wage growth", "broad wage growth", "labor share growth", "實質薪資成長", "普遍薪資成長", "勞動份額上升"},
        ),
        (
            "productivity_sharing",
            "生產力與利益分享",
            {"productivity gain", "automation", "efficiency gain", "生產力提升", "自動化", "效率提升"},
            {"shared productivity gains", "inclusive productivity gains", "productivity lowers prices", "生產力利益共享", "包容性生產力成長", "生產力帶動降價"},
        ),
        (
            "firm_size_gap",
            "大企業與中小企業落差",
            {"large-firm advantage", "large enterprise advantage", "small business gap", "sme gap", "ai adoption concentrated in large firms", "大企業優勢", "中小企業落差", "AI 採用集中大型企業"},
            {"sme ai adoption", "small business ai adoption", "sme margin improvement", "中小企業 AI 採用", "中小企業毛利改善"},
        ),
        (
            "consumption_polarization",
            "消費分化與中間層壓力",
            {"premium consumption", "value segment", "mid-market pressure", "premium and value outperform", "高端消費", "低價客群", "中價壓力", "高低價優於中價"},
            {"broad consumption growth", "middle market recovery", "廣泛消費成長", "中間層回升"},
        ),
    ),
    "ai_bubble_overinvestment": (
        (
            "capex_revenue",
            "資本支出與 AI 營收",
            {"ai capex", "capital expenditure", "data center capex", "資本支出", "資料中心資本支出"},
            {"ai revenue growth", "cloud ai revenue", "AI 營收成長", "雲端 AI 營收"},
        ),
        (
            "financing_debt",
            "資料中心融資與債務",
            {"data center debt", "ai financing", "project finance", "lease commitment", "資料中心債務", "AI 融資", "專案融資", "租賃承諾"},
            {"free cash flow", "operating cash flow", "自由現金流", "營運現金流"},
        ),
        (
            "utilization_roi",
            "使用率與企業 ROI",
            {"low data center utilization", "unused ai capacity", "weak ai roi", "pilot fatigue", "ai renewal weakness", "低資料中心使用率", "閒置 AI 算力", "AI 投報不佳", "AI 試點疲勞", "AI 續約疲弱"},
            {"high data center utilization", "paid ai adoption", "proven ai roi", "ai renewal growth", "高資料中心使用率", "付費 AI 採用", "已驗證 AI 投報", "AI 續約成長"},
        ),
        (
            "pricing_margin",
            "價格競爭與推理毛利",
            {"ai price competition", "inference margin pressure", "inference cost", "margin compression", "AI 價格競爭", "推理毛利壓力", "推理成本", "毛利壓縮"},
            {"ai margin expansion", "inference margin expansion", "AI 毛利擴張", "推理毛利擴張"},
        ),
        (
            "valuation_power",
            "估值、電力與基礎設施壓力",
            {"ai valuation", "ai bubble", "data center power", "gpu shortage", "AI 估值", "AI 泡沫", "資料中心電力", "GPU 短缺"},
            {"profitable ai", "ai cash flow", "AI 獲利", "AI 現金流"},
        ),
    ),
    "brand_market_polarization_and_true_vs_fake_segmentation": (
        (
            "brand_tiers",
            "品牌層級與市場集中",
            {"premium segment", "luxury market", "brand market share", "market share gain", "share concentration", "精品市場", "高端客群", "品牌市占", "市占提升", "市占集中"},
            {"mid-market recovery", "middle market recovery", "broad-based brand growth", "中價市場回升", "中間品牌回升", "品牌普遍成長"},
        ),
        (
            "mid_market_pressure",
            "中價位、折扣與關店壓力",
            {"mid-market", "markdown", "store closure", "discount pressure", "中價位", "折扣壓力", "撤店", "關店"},
            {"full-price sales", "full-price sell-through", "mid-market recovery", "正價銷售", "正價售罄", "中價市場回升"},
        ),
        (
            "niche_strength",
            "小眾品牌與社群韌性",
            {"niche brand", "brand community", "brand identity", "小眾品牌", "品牌社群", "品牌認同"},
            {"generic brand", "brand commoditization", "同質化品牌"},
        ),
        (
            "channel_attention",
            "平台流量、通路與注意力",
            {"retail platform", "marketplace traffic", "recommendation algorithm", "referral traffic", "零售平台", "電商流量", "推薦演算法", "導購流量"},
            {"discovery democratization", "lower customer acquisition cost", "發現工具普及", "獲客成本下降"},
        ),
        (
            "true_vs_fake_segmentation",
            "真分眾與假分眾",
            {"personalized assortment", "segment-specific product", "segment-specific merchandising", "客群差異選品", "分眾商品", "分眾陳列"},
            {"same product different copy", "click lift without repeat", "personalization improves repeat rate", "同商品只換文案", "點擊提升但回購未改善", "個人化提升回購率"},
        ),
    ),
}

_AI_CONTEXT = {
    "ai",
    "artificial intelligence",
    "generative ai",
    "automation",
    "machine learning",
    "data center",
    "datacenter",
    "gpu",
    "hbm",
    "inference",
    "cloud ai",
    "人工智慧",
    "生成式 ai",
    "自動化",
    "資料中心",
    "推理",
}
_RETAIL_BRAND_CONTEXT = {
    "retail",
    "retailer",
    "brand",
    "consumer",
    "fashion",
    "apparel",
    "store",
    "mall",
    "department store",
    "marketplace",
    "commerce",
    "零售",
    "品牌",
    "消費",
    "服飾",
    "門市",
    "百貨",
    "電商",
}

# Gate shape:
# - domains: at least one event document must belong to an allowed canonical domain.
# - support_all / counter_all: every group must contribute at least one phrase hit.
# - measurement_namespaces: accepted canonical numeric fact namespaces. When none
#   match, the candidate phrase itself must be locally quantified in source text.
STRUCTURAL_COMPONENT_GATES: dict[str, dict[str, dict[str, object]]] = {
    "k_shaped_ai_productivity_economy": {
        "labor_market": {
            "domains": {"global_markets_macro", "ai_agents_applications"},
            "support_all": (
                _AI_CONTEXT | {"productivity", "生產力"},
                {"layoff", "layoffs", "job cuts", "hiring freeze", "unemployment", "employment", "jobs", "裁員", "凍結招聘", "失業", "就業", "職缺"},
            ),
            "counter_all": ({"hiring", "employment growth", "jobs", "招聘", "就業成長", "職缺"},),
            "measurement_namespaces": {"count", "rate", "hiring", "ratio"},
        },
        "wage_income": {
            "domains": {"global_markets_macro", "ai_agents_applications"},
            "support_all": (
                {"real wage", "wage", "labor share", "household income", "實質薪資", "薪資", "勞動份額", "家庭所得"},
                {"decline", "fall", "stagnation", "down", "下降", "下滑", "停滯"},
            ),
            "counter_all": (
                {"real wage", "wage", "labor share", "實質薪資", "薪資", "勞動份額"},
                {"growth", "rise", "up", "成長", "上升", "增加"},
            ),
            "measurement_namespaces": {"rate", "ratio", "index", "amount"},
        },
        "productivity_sharing": {
            "domains": {"global_markets_macro", "ai_agents_applications"},
            "support_all": (
                {"productivity", "automation", "efficiency", "生產力", "自動化", "效率"},
                {"real wage decline", "wage stagnation", "labor share decline", "layoff", "headcount reduction", "without wage growth", "實質薪資下降", "薪資停滯", "勞動份額下降", "裁員", "人力縮減", "薪資未成長"},
            ),
            "counter_all": (
                {"productivity", "生產力"},
                {"shared", "inclusive", "wage growth", "lower prices", "共享", "包容", "薪資成長", "價格下降"},
            ),
            "measurement_namespaces": {"rate", "ratio", "index", "count"},
        },
        "firm_size_gap": {
            "domains": {"global_markets_macro", "ai_agents_applications"},
            "support_all": (
                {"large firm", "large enterprise", "small business", "sme", "大企業", "大型企業", "中小企業"},
                {"gap", "advantage", "concentrated", "concentration", "落差", "優勢", "集中"},
            ),
            "counter_all": (
                {"small business", "sme", "中小企業"},
                {"ai adoption", "margin improvement", "survival", "AI 採用", "毛利改善", "存活"},
            ),
            "measurement_namespaces": {"adoption", "margin", "revenue", "ratio", "count"},
        },
        "consumption_polarization": {
            "domains": {"global_markets_macro", "retail_consumer_fashion"},
            "support_all": (
                {"premium", "luxury", "value segment", "high-end", "高端", "精品", "低價", "價值型"},
                {"mid-market", "middle", "pressure", "weak", "outperform", "中價", "中間層", "壓力", "疲弱", "優於"},
            ),
            "counter_all": (
                {"consumption", "middle market", "consumer", "消費", "中價市場", "消費者"},
                {"broad growth", "recovery", "廣泛成長", "回升"},
            ),
            "measurement_namespaces": {"sales", "price", "rate", "index", "amount"},
        },
    },
    "ai_bubble_overinvestment": {
        "capex_revenue": {
            "domains": {"ai_agents_applications", "science_technology_industry", "global_markets_macro"},
            "support_all": (_AI_CONTEXT, {"capex", "capital expenditure", "investment", "資本支出", "投資"}),
            "counter_all": (_AI_CONTEXT, {"revenue", "sales", "營收", "收入"}),
            "measurement_namespaces": {"amount", "revenue", "cost", "sales", "ratio"},
        },
        "financing_debt": {
            "domains": {"ai_agents_applications", "science_technology_industry", "global_markets_macro"},
            "support_all": (_AI_CONTEXT, {"debt", "financing", "project finance", "lease", "債務", "融資", "租賃"}),
            "counter_all": (_AI_CONTEXT, {"free cash flow", "operating cash flow", "現金流"}),
            "measurement_namespaces": {"amount", "rate", "ratio", "cost"},
        },
        "utilization_roi": {
            "domains": {"ai_agents_applications", "science_technology_industry", "global_markets_macro"},
            "support_all": (_AI_CONTEXT, {"low utilization", "unused", "weak roi", "pilot fatigue", "renewal weakness", "低使用率", "閒置", "投報不佳", "試點疲勞", "續約疲弱"}),
            "counter_all": (_AI_CONTEXT, {"high utilization", "paid adoption", "proven roi", "renewal growth", "高使用率", "付費採用", "已驗證投報", "續約成長"}),
            "measurement_namespaces": {"rate", "ratio", "adoption", "revenue", "count"},
        },
        "pricing_margin": {
            "domains": {"ai_agents_applications", "science_technology_industry", "global_markets_macro"},
            "support_all": (_AI_CONTEXT, {"price competition", "margin pressure", "margin compression", "inference cost", "價格競爭", "毛利壓力", "毛利壓縮", "推理成本"}),
            "counter_all": (_AI_CONTEXT, {"margin expansion", "margin growth", "毛利擴張", "毛利成長"}),
            "measurement_namespaces": {"price", "margin", "cost", "rate", "ratio"},
        },
        "valuation_power": {
            "domains": {"ai_agents_applications", "science_technology_industry", "global_markets_macro"},
            "support_all": (_AI_CONTEXT, {"valuation", "bubble", "power", "shortage", "估值", "泡沫", "電力", "短缺"}),
            "counter_all": (_AI_CONTEXT, {"profitable", "cash flow", "profit", "獲利", "現金流"}),
            "measurement_namespaces": {"price", "ratio", "amount", "cost", "revenue"},
        },
    },
    "brand_market_polarization_and_true_vs_fake_segmentation": {
        "brand_tiers": {
            "domains": {"retail_consumer_fashion"},
            "support_all": (_RETAIL_BRAND_CONTEXT, {"premium", "luxury", "market share", "share concentration", "高端", "精品", "市占", "集中"}),
            "counter_all": (_RETAIL_BRAND_CONTEXT, {"mid-market recovery", "broad-based growth", "中價市場回升", "品牌普遍成長"}),
            "measurement_namespaces": {"market", "sales", "margin", "ratio", "revenue"},
        },
        "mid_market_pressure": {
            "domains": {"retail_consumer_fashion"},
            "support_all": (_RETAIL_BRAND_CONTEXT, {"mid-market", "markdown", "discount", "store closure", "中價", "折扣", "關店", "撤店"}),
            "counter_all": (_RETAIL_BRAND_CONTEXT, {"full-price", "sell-through", "recovery", "正價", "售罄", "回升"}),
            "measurement_namespaces": {"price", "sales", "inventory", "count", "margin", "rate"},
        },
        "niche_strength": {
            "domains": {"retail_consumer_fashion"},
            "support_all": (_RETAIL_BRAND_CONTEXT, {"niche", "community", "brand identity", "小眾", "社群", "品牌認同"}),
            "counter_all": (_RETAIL_BRAND_CONTEXT, {"generic brand", "commoditization", "同質化"}),
            "measurement_namespaces": {"sales", "membership", "rate", "margin", "revenue"},
        },
        "channel_attention": {
            "domains": {"retail_consumer_fashion"},
            "support_all": (_RETAIL_BRAND_CONTEXT, {"traffic", "algorithm", "referral", "platform", "流量", "演算法", "導購", "平台"}),
            "counter_all": (_RETAIL_BRAND_CONTEXT, {"discovery democratization", "lower customer acquisition cost", "發現工具普及", "獲客成本下降"}),
            "measurement_namespaces": {"traffic", "sales", "rate", "cost"},
        },
        "true_vs_fake_segmentation": {
            "domains": {"retail_consumer_fashion"},
            "support_all": (
                {"segment", "segmentation", "personalized", "分眾", "個人化"},
                {"assortment", "product", "merchandising", "channel", "pricing", "選品", "商品", "陳列", "通路", "定價"},
            ),
            "counter_all": (
                {"segment", "segmentation", "personalization", "persona", "分眾", "個人化", "客群"},
                {"same product", "copy", "click", "repeat rate", "sell-through", "同商品", "文案", "點擊", "回購率", "售罄"},
            ),
            "measurement_namespaces": {"sales", "membership", "rate", "margin", "traffic"},
        },
    },
}
