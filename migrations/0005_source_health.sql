-- PR C: durable source health, one row per source with the latest observation.

create table if not exists source_health (
  source_id text primary key,
  status text not null,
  checked_at text not null,
  last_success_at text not null default '',
  last_item_at text not null default '',
  consecutive_failures integer not null default 0,
  response_count integer not null default 0,
  latency_ms integer not null default 0,
  failure_reason text not null default '',
  retry_at text not null default ''
);

create index if not exists idx_source_health_status
  on source_health(status, checked_at);
