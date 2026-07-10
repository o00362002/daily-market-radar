-- PR B: durable event-resolution match provenance.
-- Every cross-day match decision (including unresolved matches) is recorded so
-- audits can explain why a current event was or was not merged with prior state.

create table if not exists event_matches (
  match_id text primary key,
  current_event_id text not null,
  prior_event_id text,
  strategy text not null,
  confidence real not null,
  observed_at text not null,
  match_json text not null
);

create index if not exists idx_event_matches_current_event
  on event_matches(current_event_id, observed_at);

create index if not exists idx_event_matches_strategy
  on event_matches(strategy, observed_at);
