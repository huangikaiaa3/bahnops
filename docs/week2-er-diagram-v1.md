# Week 2 ER Diagram v1

This is the first high-level entity relationship diagram for BahnOps Week 2.

It captures:
- shared polling targets
- future multi-user subscriptions
- poll runs and observed services
- current state and historical service events

```mermaid
erDiagram
    user ||--o{ tracked_target : "owns"
    tracked_target }o--|| poll_target : "subscribes to"

    station ||--o{ poll_target : "is polled as"
    poll_target ||--o{ poll_run : "produces"

    poll_run ||--o{ service_observation : "captures"
    service ||--o{ service_observation : "appears in"

    service ||--|| service_state_current : "has latest state"
    service ||--o{ service_state_event : "has history"

    user {
        bigint id PK
        text external_key
        text display_name
        timestamptz created_at
    }

    station {
        bigint id PK
        text eva_number UK
        text name
        timestamptz created_at
    }

    poll_target {
        bigint id PK
        bigint station_id FK
        text target_type
        text board_mode
        integer poll_interval_seconds
        boolean is_active
        timestamptz created_at
        timestamptz updated_at
    }

    tracked_target {
        bigint id PK
        bigint user_id FK
        bigint poll_target_id FK
        text label
        boolean is_active
        timestamptz created_at
        timestamptz updated_at
    }

    poll_run {
        bigint id PK
        bigint poll_target_id FK
        timestamptz started_at
        timestamptz finished_at
        text status
        integer services_seen
        text error_message
    }

    service {
        bigint id PK
        text service_uid UK
        text category
        text number
        text line
        text display_name
        timestamptz first_seen_at
    }

    service_observation {
        bigint id PK
        bigint poll_run_id FK
        bigint service_id FK
        timestamptz observed_at
        text planned_arrival
        text current_arrival
        text planned_departure
        text current_departure
        text planned_arrival_platform
        text planned_departure_platform
        text current_arrival_platform
        text current_departure_platform
        jsonb raw_snapshot
    }

    service_state_current {
        bigint service_id PK, FK
        bigint latest_poll_run_id FK
        timestamptz last_seen_at
        text current_arrival
        text current_departure
        text current_arrival_platform
        text current_departure_platform
        boolean is_cancelled
    }

    service_state_event {
        bigint id PK
        bigint service_id FK
        bigint poll_run_id FK
        timestamptz event_time
        text event_type
        text old_value
        text new_value
    }
```

## Notes

- `poll_target` defines the shared scope that the system polls.
- `tracked_target` is the subscription layer that can later belong to a user.
- `poll_run` belongs to the shared `poll_target`, not to an individual user.
- `service_observation` stores what was seen in each poll.
- `service_state_current` stores the latest known state for quick reads.
- `service_state_event` stores meaningful historical changes.
