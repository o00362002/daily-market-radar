create table if not exists sources (
  source_id text primary key,
  canonical_url text not null unique,
  enabled boolean not null
);

create table if not exists fetch_runs (
  run_id text primary key,
  started_at text not null,
  finished_at text,
  status text not null
);

create table if not exists documents (
  document_id text primary key,
  source_id text not null,
  url text not null,
  title text not null,
  published_at text not null,
  fetched_at text not null
);

create table if not exists events (
  event_id text primary key,
  first_seen_at text not null,
  last_seen_at text not null,
  last_material_delta_at text not null,
  status text not null
);

create table if not exists signals (
  signal_id text primary key,
  event_id text not null,
  lifecycle text not null,
  next_check_at text not null
);

create table if not exists reports (
  report_id text primary key,
  run_id text not null,
  profile text not null,
  rendered_at text not null
);
