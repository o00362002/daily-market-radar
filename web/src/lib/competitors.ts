import registry from '../../../config/competitor_registry.json';

type CompetitorEntry = {
  id: string;
  name: string;
  aliases: string[];
  priority: string;
};

export type CompetitorMatch = CompetitorEntry & {
  group: 'taiwan_retailops_products' | 'global_platforms' | 'social_and_content';
  matched_terms: string[];
};

type CompetitorRegistry = {
  groups: {
    taiwan_retailops_products: CompetitorEntry[];
    global_platforms: CompetitorEntry[];
    social_and_content: CompetitorEntry[];
  };
};

const typedRegistry = registry as CompetitorRegistry;

export const taiwanProductTerms = typedRegistry.groups.taiwan_retailops_products.flatMap(
  (entry) => [entry.name, ...entry.aliases],
);

export const globalPlatformTerms = typedRegistry.groups.global_platforms.flatMap(
  (entry) => [entry.name, ...entry.aliases],
);

const itemText = (item: any) => [
  item.headline,
  item.today_delta,
  item.taiwan_implication,
  item.primary_domain,
  ...(item.uncertainties ?? []),
].filter(Boolean).join(' ').toLowerCase();

const entryGroups = [
  ['taiwan_retailops_products', typedRegistry.groups.taiwan_retailops_products],
  ['global_platforms', typedRegistry.groups.global_platforms],
  ['social_and_content', typedRegistry.groups.social_and_content],
] as const;

export const competitorMatches = (item: any): CompetitorMatch[] => {
  const text = itemText(item);
  return entryGroups.flatMap(([group, entries]) => entries.flatMap((entry) => {
    const matched_terms = [entry.name, ...entry.aliases].filter((term) => text.includes(term.toLowerCase()));
    return matched_terms.length ? [{ ...entry, group, matched_terms }] : [];
  }));
};

const withMatches = (item: any) => ({ ...item, competitor_matches: competitorMatches(item) });

export const projectCompetitorItems = (items: any[]) => {
  const projected = items.map(withMatches);
  const product = projected.filter((item) => item.competitor_matches.some((match: CompetitorMatch) => match.group !== 'social_and_content'));
  const social = projected.filter(
    (item) => item.competitor_matches.some((match: CompetitorMatch) => match.group === 'social_and_content') && !product.includes(item),
  );
  const sort = (rows: any[]) => [...rows].sort((a, b) =>
    (b.importance_score - a.importance_score)
    || (b.potential_score - a.potential_score)
    || (b.confidence_score - a.confidence_score)
    || String(a.item_id).localeCompare(String(b.item_id)),
  );
  return { product: sort(product), social: sort(social) };
};

// Finer split of the product lane, for the competitors page: Taiwan RetailOps
// products vs global platforms (an item matching both counts as Taiwan-first).
export const splitProductItems = (product: any[]) => {
  const taiwan = product.filter((item) => item.competitor_matches?.some((match: CompetitorMatch) => match.group === 'taiwan_retailops_products'));
  const global = product.filter((item) => !taiwan.includes(item));
  return { taiwan, global };
};

export const competitorRegistry = typedRegistry;
