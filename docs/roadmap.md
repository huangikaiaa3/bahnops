# BahnOps Roadmap

## Core idea

Build one transit monitoring system that grows week by week instead of creating disconnected practice apps.

## System definition

BahnOps is a live Deutsche Bahn train-status platform that:

1. fetches planned and current train data from the DB API
2. normalizes that data into a stable internal model
3. stores current state and historical changes in PostgreSQL
4. serves live and historical views through FastAPI
5. later emits internal change events through Kafka
6. later models analytics with dbt and batch analysis with Spark

## Product scope

The first useful version should let you:
- track a few stations, trains, or one S-Bahn line
- view scheduled versus current times
- detect delays, platform changes, and cancellations
- inspect recent history for a tracked service

## Architecture path

1. Async polling against the Deutsche Bahn API
2. Response normalization and validation
3. Persistence of current state and historical events
4. Backend API for boards, tracked services, and history
5. Lightweight frontend for live views
6. Event pipeline for train-state changes
7. Analytics and batch processing over historical data

## Weekly milestones

### Week 1

Focus:
- confirm DB API access and the target endpoints
- practice Python async basics in the context of polling
- fetch live DB data for one station target
- normalize planned board data and current change data into an internal model

Expected outputs:
- a working fetch script for one station target
- a normalized station snapshot artifact
- notes on endpoint choice and the role of `plan` vs `fchg`

### Week 2

Focus:
- design the first PostgreSQL schema
- store poll runs and normalized service observations
- separate current state from historical records
- define identifier boundaries between train labels, service runs, and stop observations

### Week 3

Focus:
- build FastAPI read endpoints on top of stored data
- expose station board and service detail views

### Later weeks

Focus:
- improve polling robustness and configuration
- add Kafka-based change events
- add analytics modeling with dbt and Spark

## Non-goals right now

- scraping websites
- supporting every route from day one
- heavy cloud deployment early
- overbuilding the frontend before the backend is useful
