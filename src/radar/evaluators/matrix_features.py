"""Feature dictionaries for deterministic Retail/Crypto/structural evaluation.

Keep broad concepts phrase-oriented. Generic words such as ``ai``, ``content``,
``job``, ``income``, ``middle``, ``platform``, ``community``, ``margin`` and
``power`` caused semantic leakage in production backtests.
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

STRUCTURAL_FEATURES: dict[str, dict[str, set[str]]] = {
    "k_shaped_ai_productivity_economy": {
        "support": {"productivity gain", "automation", "layoff", "efficiency gain", "生產力提升", "自動化", "裁員"},
        "counter": {"broad wage growth", "real wage growth", "inclusive growth", "普遍加薪", "實質薪資成長", "包容性成長"},
    },
    "ai_bubble_overinvestment": {
        "support": {"ai capex", "capital expenditure", "overinvestment", "ai valuation", "ai bubble", "資本支出", "過度投資", "AI 泡沫", "AI 估值"},
        "counter": {"ai revenue", "paid adoption", "profitable ai", "ai cash flow", "AI 營收", "付費採用", "AI 獲利", "AI 現金流"},
    },
    "brand_market_polarization_and_true_vs_fake_segmentation": {
        "support": {"premium segment", "luxury market", "value segment", "market polarization", "customer segmentation", "高端客群", "精品市場", "低價客群", "市場兩極", "客群分眾"},
        "counter": {"mid-market recovery", "middle market recovery", "broad-based brand growth", "中間層回升", "中價市場回升", "品牌普遍成長"},
    },
}

STRUCTURAL_COMPONENTS: dict[str, tuple[tuple[str, str, set[str], set[str]], ...]] = {
    "k_shaped_ai_productivity_economy": (
        ("labor_market", "勞動力與就業環境", {"layoff", "layoffs", "unemployment", "employment growth", "裁員", "失業率", "就業成長"}, {"broad hiring", "broad employment growth", "普遍招聘", "廣泛就業成長"}),
        ("wage_income", "薪資與所得分配", {"real wage", "wage growth", "salary growth", "household income", "labor income", "實質薪資", "薪資成長", "家庭所得", "勞動所得"}, {"real wage growth", "broad wage growth", "實質薪資成長", "普遍薪資成長"}),
        ("productivity_sharing", "生產力與利益分享", {"productivity gain", "automation", "efficiency gain", "生產力提升", "自動化", "效率提升"}, {"shared productivity gains", "inclusive productivity gains", "生產力利益共享", "包容性生產力成長"}),
        ("firm_size_gap", "大企業與中小企業落差", {"large firm", "large enterprise", "small business gap", "sme gap", "大企業", "中小企業落差"}, {"sme adoption", "small business adoption", "中小企業採用"}),
        ("consumption_polarization", "消費分化與中間層壓力", {"premium consumption", "value segment", "mid-market pressure", "consumer spending", "高端消費", "低價客群", "中價壓力", "消費支出"}, {"broad consumption growth", "middle market recovery", "廣泛消費成長", "中間層回升"}),
    ),
    "ai_bubble_overinvestment": (
        ("capex_revenue", "資本支出與 AI 營收", {"ai capex", "capital expenditure", "data center capex", "資本支出", "資料中心資本支出"}, {"ai revenue growth", "cloud ai revenue", "AI 營收成長", "雲端 AI 營收"}),
        ("financing_debt", "資料中心融資與債務", {"data center debt", "ai financing", "project finance", "lease commitment", "資料中心債務", "AI 融資", "專案融資", "租賃承諾"}, {"free cash flow", "operating cash flow", "自由現金流", "營運現金流"}),
        ("utilization_roi", "使用率與企業 ROI", {"data center utilization", "ai utilization", "ai roi", "enterprise ai adoption", "使用率", "AI 投資報酬", "企業 AI 採用"}, {"paid ai adoption", "proven ai roi", "付費 AI 採用", "已驗證 AI 投報"}),
        ("pricing_margin", "價格競爭與推理毛利", {"ai price competition", "inference margin", "inference cost", "AI 價格競爭", "推理毛利", "推理成本"}, {"ai margin expansion", "inference margin expansion", "AI 毛利擴張", "推理毛利擴張"}),
        ("valuation_power", "估值、電力與基礎設施壓力", {"ai valuation", "ai bubble", "data center power", "gpu shortage", "AI 估值", "AI 泡沫", "資料中心電力", "GPU 短缺"}, {"profitable ai", "ai cash flow", "AI 獲利", "AI 現金流"}),
    ),
    "brand_market_polarization_and_true_vs_fake_segmentation": (
        ("brand_tiers", "品牌層級與市場集中", {"premium segment", "luxury market", "market share", "精品市場", "高端客群", "市占率"}, {"mid-market recovery", "中價市場回升"}),
        ("mid_market_pressure", "中價位、折扣與關店壓力", {"mid-market", "markdown", "store closure", "中價位", "折扣壓力", "撤店", "關店"}, {"full-price sales", "full-price sell-through", "正價銷售", "正價售罄"}),
        ("niche_strength", "小眾品牌與社群韌性", {"niche brand", "brand community", "brand identity", "小眾品牌", "品牌社群", "品牌認同"}, {"generic brand", "brand commoditization", "同質化品牌"}),
        ("channel_attention", "平台流量、通路與注意力", {"retail platform", "marketplace traffic", "recommendation algorithm", "referral traffic", "零售平台", "電商流量", "推薦演算法", "導購流量"}, {"product discovery tools", "商品發現工具"}),
        ("true_vs_fake_segmentation", "真分眾與假分眾", {"customer segmentation", "personalized assortment", "customer persona", "客群分眾", "個人化選品", "客群輪廓"}, {"repeat purchase", "sell-through", "repurchase rate", "回購", "售罄", "回購率"}),
    ),
}
