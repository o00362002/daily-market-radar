create table if not exists document_payloads (
  document_id text primary key,
  canonical_url text not null,
  content_hash text not null,
  fetched_at text not null,
  payload_json text not null
);

create index if not exists idx_document_payloads_canonical_url
  on document_payloads(canonical_url, fetched_at);

create index if not exists idx_document_payloads_content_hash
  on document_payloads(content_hash, fetched_at);

create table if not exists event_documents (
  event_id text not null,
  document_id text not null,
  primary key(event_id, document_id)
);

create index if not exists idx_event_documents_document_id
  on event_documents(document_id);

create table if not exists event_deltas (
  delta_id text primary key,
  event_id text not null,
  observed_at text not null,
  delta_json text not null
);

create index if not exists idx_event_deltas_event_id
  on event_deltas(event_id, observed_at);

create table if not exists indicator_observations (
  indicator_id text not null,
  observation_date text not null,
  payload_json text not null,
  primary key(indicator_id, observation_date)
);

create table if not exists state_entries (
  state_key text primary key,
  value_blob blob not null,
  updated_at text not null
);
