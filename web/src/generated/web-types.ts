// AUTO-GENERATED from schemas/web.schema.json — do not edit by hand.

export interface WebManifestV1 {
  schema_version: string;
  generated_at: string;
  latest_date: string;
  latest_full_path: string;
  report_count: number;
  report_dates: string[];
  domains: string[];
  indicator_ids: string[];
  years: string[];
}

export interface ReportSummaryV1 {
  date: string;
  run_id: string;
  profile: string;
  status: string;
  evaluation_mode: string;
  is_fixture: boolean;
  degradation_reasons: string[];
  major_count: number;
  potential_count: number;
  taiwan_count: number;
  coverage_gap_count: number;
  retail_observed: number;
  crypto_observed: number;
  structural_directional: number;
  content_hash: string;
}

export interface ReportIndexEntryV1 {
  date: string;
  run_id: string;
  status: string;
  evaluation_mode: string;
  is_fixture: boolean;
  major_count: number;
  potential_count: number;
  taiwan_count: number;
  summary_path: string;
  full_path: string;
}

export interface ReportsYearIndexV1 {
  year: string;
  entries: ReportIndexEntryV1[];
}

export interface DomainIndexV1 {
  domain: string;
  year: string;
  entries: ReportIndexEntryV1[];
}

export interface TaiwanIndexEntryV1 {
  date: string;
  run_id: string;
  taiwan_count: number;
  summary_path: string;
}

export interface TaiwanIndexV1 {
  year: string;
  entries: TaiwanIndexEntryV1[];
}

export interface TrendPointV1 {
  date: string;
  direction: string;
  support_score: number;
  counter_score: number;
  confidence: string;
}

export interface TrendSeriesV1 {
  indicator_id: string;
  points: TrendPointV1[];
}

export interface LegacyReportEntryV1 {
  date: string;
  slug: string;
  title: string;
  variant: string;
  source_path: string;
  markdown_path: string;
  content_hash: string;
}

export interface LegacyReportIndexV1 {
  year: string;
  entries: LegacyReportEntryV1[];
}
