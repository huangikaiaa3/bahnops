create table if not exists station (
    id bigint generated always as identity primary key,
    eva_number text not null unique,
    name text not null,
    created_at timestamptz not null default now()
);

create table if not exists poll_target (
    id bigint generated always as identity primary key,
    station_id bigint not null references station(id),
    target_type text not null,
    poll_interval_seconds integer not null,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (station_id, target_type)
);

create table if not exists service (
    id bigint generated always as identity primary key,
    service_run_uid text not null unique,
    category text,
    number text,
    line text,
    display_name text,
    first_seen_at timestamptz not null default now()
);

create table if not exists poll_run (
    id bigint generated always as identity primary key,
    poll_target_id bigint not null references poll_target(id),
    started_at timestamptz not null,
    finished_at timestamptz,
    status text not null,
    services_seen integer not null default 0,
    error_message text
);

create table if not exists service_observation (
    id bigint generated always as identity primary key,
    poll_run_id bigint not null references poll_run(id),
    service_id bigint not null references service(id),
    observation_uid text not null unique,
    stop_sequence integer not null,
    observed_at timestamptz not null,
    planned_arrival text,
    current_arrival text,
    planned_departure text,
    current_departure text,
    planned_arrival_platform text,
    planned_departure_platform text,
    current_arrival_platform text,
    current_departure_platform text,
    planned_arrival_path jsonb not null default '[]'::jsonb,
    planned_departure_path jsonb not null default '[]'::jsonb,
    current_arrival_path jsonb not null default '[]'::jsonb,
    current_departure_path jsonb not null default '[]'::jsonb,
    raw_snapshot jsonb
);

create table if not exists service_state_current (
    service_id bigint primary key references service(id),
    latest_poll_run_id bigint not null references poll_run(id),
    last_seen_at timestamptz not null,
    current_arrival text,
    current_departure text,
    current_arrival_platform text,
    current_departure_platform text,
    is_cancelled boolean not null default false
);

create table if not exists service_state_event (
    id bigint generated always as identity primary key,
    service_id bigint not null references service(id),
    poll_run_id bigint not null references poll_run(id),
    event_time timestamptz not null,
    event_type text not null,
    old_value text,
    new_value text
);

create index if not exists idx_poll_run_poll_target_id
    on poll_run (poll_target_id);

create index if not exists idx_service_observation_poll_run_id
    on service_observation (poll_run_id);

create index if not exists idx_service_observation_service_id
    on service_observation (service_id);

create index if not exists idx_service_observation_stop_sequence
    on service_observation (stop_sequence);

create index if not exists idx_service_state_event_service_id
    on service_state_event (service_id);

create index if not exists idx_service_state_event_poll_run_id
    on service_state_event (poll_run_id);

create index if not exists idx_service_display_lookup
    on service (category, number, line);
