import registry from '../../../config/competitor_registry.json';

export type CompetitorGroupKey =
  | 'global_direct_retail_action_systems'
  | 'global_adjacent_execution_platforms'
  | 'taiwan_adjacent_retail_platforms'
  | 'global_enabling_platform_threats'
  | 'social_and_content';

export type CompetitorEntry = {
  id: string;
  name: string;
  aliases: string[];
  requires_any?: string[];
  priority: 'high' | 'medium' | 'low';
  market: 'global' | 'taiwan' | 'mixed';
  relationship: 'direct' | 'adjacent' | 'enabling' | 'content';
  focus?: string;
  official_urls?: string[];
};

export type CompetitorMatch = CompetitorEntry & {
  group: CompetitorGroupKey;
  matched_terms: string[];
  matched_context_terms: string[];
};

type CompetitorRegistry = {
  group_order: CompetitorGroupKey[];
  groups: Record<CompetitorGroupKey, CompetitorEntry[]>;
};

const typedRegistry = registry as unknown as CompetitorRegistry;

export const competitorGroupMeta: Record<CompetitorGroupKey, {
  zh: string;
  en: string;
  badge: string;
  description: string;
}> = {
  global_direct_retail_action_systems: {
    zh: '海外直接 Retail Action 系統',
    en: 'Direct Action Systems',
    badge: '直接競品',
    description: '以營運訊號或自然交代轉 Action、追蹤、證據、Outcome 與改善為產品中心。',
  },
  global_adjacent_execution_platforms: {
    zh: '海外相鄰前線執行平台',
    en: 'Adjacent Execution',
    badge: '相鄰平台',
    description: '前線任務、溝通、巡檢、學習或流程編排已接近 Action Layer，但產品中心不完全相同。',
  },
  taiwan_adjacent_retail_platforms: {
    zh: '台灣相鄰零售平台',
    en: 'Taiwan Adjacent',
    badge: '在地威脅',
    description: '已掌握台灣品牌、交易、會員、POS、ERP 或庫存資料，需追蹤是否向營運執行層擴張。',
  },
  global_enabling_platform_threats: {
    zh: '通用 Agent／執行基礎設施',
    en: 'Enabling Platforms',
    badge: '底座威脅',
    description: '只有在明確進入零售營運 Action、工作流或前線執行情境時才列入，不追一般 AI 與雲端新聞。',
  },
  social_and_content: {
    zh: '內容與定位競品',
    en: 'Content Competition',
    badge: '內容競品',
    description: '追蹤與「門市營運 × 數據 × AI」高度重疊的內容定位、受眾與產品導流。',
  },
};

export const competitorGroupOrder = typedRegistry.group_order;

const normalize = (value: unknown) => String(value ?? '').normalize('NFKC').toLowerCase();
const escapeRegExp = (value: string) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

const termMatches = (text: string, rawTerm: string) => {
  const term = normalize(rawTerm).trim();
  if (!term) return false;
  if (/^[\x00-\x7F]+$/.test(term)) {
    const pattern = escapeRegExp(term).replace(/\s+/g, '\\s+');
    return new RegExp(`(^|[^a-z0-9])${pattern}([^a-z0-9]|$)`, 'i').test(text);
  }
  return text.includes(term);
};

// Competitor identity must come from factual event text. Taiwan implication,
// uncertainties and next-watch are analytical projections and cannot classify identity.
const itemFactText = (item: any) => normalize([
  item.headline,
  item.today_delta,
].filter(Boolean).join(' '));

const itemHeadlineText = (item: any) => normalize(item.headline);

const entryGroups = competitorGroupOrder.map((group) => [group, typedRegistry.groups[group]] as const);

export const competitorMatches = (item: any): CompetitorMatch[] => {
  const text = itemFactText(item);
  return entryGroups.flatMap(([group, entries]) => entries.flatMap((entry) => {
    const matched_terms = [entry.name, ...entry.aliases]
      .filter((term) => termMatches(text, term));
    if (!matched_terms.length) return [];

    const matched_context_terms = (entry.requires_any ?? [])
      .filter((term) => termMatches(text, term));
    if ((entry.requires_any?.length ?? 0) > 0 && matched_context_terms.length === 0) return [];

    return [{ ...entry, group, matched_terms, matched_context_terms }];
  }));
};

const primaryGroupFor = (item: any, matches: CompetitorMatch[]): CompetitorGroupKey | null => {
  const headline = itemHeadlineText(item);
  return competitorGroupOrder.find((group) => matches.some((match) =>
    match.group === group && match.matched_terms.some((term) => termMatches(headline, term)),
  )) ?? competitorGroupOrder.find((group) => matches.some((match) => match.group === group)) ?? null;
};

const withMatches = (item: any) => {
  const competitor_matches = competitorMatches(item);
  return {
    ...item,
    competitor_matches,
    competitor_group: primaryGroupFor(item, competitor_matches),
  };
};

const sort = (rows: any[]) => [...rows].sort((a, b) =>
  (b.importance_score - a.importance_score)
  || (b.potential_score - a.potential_score)
  || (b.confidence_score - a.confidence_score)
  || String(a.item_id).localeCompare(String(b.item_id)),
);

export const projectCompetitorItems = (items: any[]) => {
  const projected = items.map(withMatches).filter((item) => item.competitor_group);
  const byGroup = Object.fromEntries(competitorGroupOrder.map((group) => [
    group,
    sort(projected.filter((item) => item.competitor_group === group)),
  ])) as Record<CompetitorGroupKey, any[]>;

  const product = sort(competitorGroupOrder
    .filter((group) => group !== 'social_and_content')
    .flatMap((group) => byGroup[group]));
  const social = byGroup.social_and_content;

  return { product, social, byGroup };
};

// Compatibility helper for older consumers. Geography is no longer the primary
// taxonomy, so global contains direct, adjacent and enabling groups.
export const splitProductItems = (product: any[]) => ({
  taiwan: product.filter((item) => item.competitor_group === 'taiwan_adjacent_retail_platforms'),
  global: product.filter((item) => item.competitor_group !== 'taiwan_adjacent_retail_platforms'),
});

export const competitorRegistry = typedRegistry;
