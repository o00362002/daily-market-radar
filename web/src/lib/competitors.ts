import registry from '../../../config/competitor_registry.json';

type CompetitorEntry = {
  id: string;
  name: string;
  aliases: string[];
  priority: string;
};

type CompetitorRegistry = {
  groups: {
    taiwan_retailops_products: CompetitorEntry[];
    global_platforms: CompetitorEntry[];
    social_and_content: CompetitorEntry[];
  };
};

const typedRegistry = registry as CompetitorRegistry;

export const productCompetitorTerms = [
  ...typedRegistry.groups.taiwan_retailops_products,
  ...typedRegistry.groups.global_platforms,
].flatMap((entry) => [entry.name, ...entry.aliases]);

export const socialCompetitorTerms = typedRegistry.groups.social_and_content.flatMap(
  (entry) => [entry.name, ...entry.aliases],
);

const itemText = (item: any) => [
  item.headline,
  item.today_delta,
  item.taiwan_implication,
  item.primary_domain,
  ...(item.uncertainties ?? []),
].filter(Boolean).join(' ').toLowerCase();

const matchesTerms = (item: any, terms: string[]) => {
  const text = itemText(item);
  return terms.some((term) => text.includes(term.toLowerCase()));
};

export const projectCompetitorItems = (items: any[]) => {
  const product = items.filter((item) => matchesTerms(item, productCompetitorTerms));
  const social = items.filter(
    (item) => matchesTerms(item, socialCompetitorTerms) && !product.includes(item),
  );
  const sort = (rows: any[]) => [...rows].sort((a, b) =>
    (b.importance_score - a.importance_score)
    || (b.potential_score - a.potential_score)
    || (b.confidence_score - a.confidence_score)
    || String(a.item_id).localeCompare(String(b.item_id)),
  );
  return { product: sort(product), social: sort(social) };
};

export const competitorRegistry = typedRegistry;
