// Display-name mappings for machine ids. Fallbacks keep unknown ids readable,
// so schema additions never break pages — they just render prettified ids.

export const DOMAIN_LABELS: Record<string, { zh: string; en: string }> = {
  global_markets_macro: { zh: '全球市場宏觀', en: 'Macro' },
  ai_agents_applications: { zh: 'AI 代理與應用', en: 'Agents' },
  crypto_rwa_agent_payments: { zh: '加密與代理支付', en: 'Crypto' },
  retail_consumer_fashion: { zh: '零售消費時尚', en: 'Retail' },
  science_technology_industry: { zh: '科技產業', en: 'Sci-Tech' },
};

const prettify = (id: string) => id.replaceAll('_', ' ');

export const domainLabel = (id: string | undefined | null) =>
  (id && DOMAIN_LABELS[id]?.zh) || (id ? prettify(id) : '未分類');

export const domainLabelEn = (id: string | undefined | null) =>
  (id && DOMAIN_LABELS[id]?.en) || '';

export const MATRIX_LABELS: Record<string, string> = {
  // Retail matrix
  channel_offline_department_store_mall_street: '實體通路：百貨、商場、街邊',
  channel_online_marketplace_social_commerce: '線上通路：電商平台、社群電商',
  cost_pressure: '成本壓力',
  inventory_markdown_mid_price_pressure: '庫存、折扣與中價位壓力',
  membership_crm_loyalty_retail_media: '會員、CRM 與零售媒體',
  product_fashion_style_assortment_material_fit_category: '商品：風格、組合、材質、版型',
  social_commerce_content_discovery_ai_referral: '社群商務、內容發現與 AI 導流',
  taiwan_retail_commercial_district_department_store_brand: '台灣零售：商圈、百貨、品牌',
  true_vs_fake_segmentation: '真偽分眾 True vs Fake',
  // Crypto matrix
  btc_eth_sol_market_structure: 'BTC / ETH / SOL 市場結構',
  etf_flows: 'ETF 資金流',
  perp_dex_volume_oi_funding: '永續 DEX：成交量、OI、資金費率',
  regulation_policy: '監管與政策',
  rwa_tokenized_assets: 'RWA 代幣化資產',
  stablecoin_supply_and_dry_powder: '穩定幣供給與場外資金',
  taiwan_crypto_fixed_sources: '台灣加密固定來源',
  tvl_fees_revenue: 'TVL、手續費與協議收入',
  // Structural indicators
  k_shaped_ai_productivity_economy: 'K 型 AI 生產力經濟',
  ai_bubble_overinvestment: 'AI 泡沫與過度投資',
  brand_market_polarization_and_true_vs_fake_segmentation: '品牌兩極化與真偽分眾',
};

export const matrixLabel = (key: string) => MATRIX_LABELS[key] ?? prettify(key);
