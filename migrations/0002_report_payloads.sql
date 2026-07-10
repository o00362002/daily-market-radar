create table if not exists report_payloads (
  report_id text primary key,
  run_id text not null,
  payload_json text not null
);

create index if not exists idx_report_payloads_run_id
  on report_payloads(run_id);

create table if not exists coverage_gaps (
  gap_id text primary key,
  run_id text not null,
  gap_json text not null
);

create index if not exists idx_coverage_gaps_run_id
  on coverage_gaps(run_id);
