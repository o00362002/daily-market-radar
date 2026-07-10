// Build-time data access over the immutable web artifacts. Tolerant of missing
// artifacts so a bare `astro build` never crashes; CI exports fixtures first.
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import type {
  DomainIndexV1,
  ReportsYearIndexV1,
  TaiwanIndexV1,
  TrendSeriesV1,
  WebManifestV1,
} from '../generated/web-types';

const here = fileURLToPath(new URL('.', import.meta.url));
export const ARTIFACTS_DIR =
  process.env.RADAR_ARTIFACTS_DIR || resolve(here, '../../../artifacts/web/v1');

function readJson<T>(relative: string): T | null {
  const path = resolve(ARTIFACTS_DIR, relative);
  if (!existsSync(path)) return null;
  return JSON.parse(readFileSync(path, 'utf8')) as T;
}

export function getManifest(): WebManifestV1 | null {
  return readJson<WebManifestV1>('manifest.json');
}

export function getLatestReport(): Record<string, unknown> | null {
  return readJson<Record<string, unknown>>('latest.json');
}

export function getReportsYear(year: string): ReportsYearIndexV1 | null {
  return readJson<ReportsYearIndexV1>(`indexes/reports/${year}.json`);
}

export function getFullByPath(path: string): Record<string, unknown> | null {
  return readJson<Record<string, unknown>>(path);
}

export function getTrend(indicatorId: string): TrendSeriesV1 | null {
  return readJson<TrendSeriesV1>(`indexes/trends/${indicatorId}.json`);
}

export function getTaiwan(year: string): TaiwanIndexV1 | null {
  return readJson<TaiwanIndexV1>(`indexes/taiwan/${year}.json`);
}

export function getDomainIndex(domain: string, year: string): DomainIndexV1 | null {
  return readJson<DomainIndexV1>(`indexes/domains/${domain}/${year}.json`);
}

export function listYears(): string[] {
  const manifest = getManifest();
  return manifest ? manifest.years : [];
}

export function allReportEntries() {
  return listYears()
    .flatMap((year) => getReportsYear(year)?.entries ?? [])
    .sort((a, b) => (a.date < b.date ? 1 : -1));
}

export function listDomainDirs(): string[] {
  const dir = resolve(ARTIFACTS_DIR, 'indexes/domains');
  if (!existsSync(dir)) return [];
  return readdirSync(dir);
}
