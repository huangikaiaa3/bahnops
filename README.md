# BahnOps

BahnOps is a live Deutsche Bahn transit data project built to grow over 8 weeks.

The system fetches planned and live train data from the Deutsche Bahn API, normalizes it, stores current and historical state in PostgreSQL, and exposes that data through a backend service and later a small frontend.

## What this project is for

BahnOps is meant to help you learn, in one connected system:
- async Python
- API-driven ingestion
- FastAPI
- PostgreSQL
- Kafka
- dbt
- Spark
- Docker, Kubernetes, and Terraform basics

## Core product

The product goal is a service that can:
- track specific stations, trains, or S-Bahn lines
- show planned and current arrival or departure status
- show delays, platform changes, and cancellations
- store recent and historical status changes
- later surface reliability analytics

## Week 1 focus

Week 1 is intentionally about the ingestion foundation:
- confirm DB API access and the target endpoints
- practice Python async basics
- fetch live DB data for one station or one train target
- normalize the API response into your own internal shape

## Starter structure

- `api/`: FastAPI service code
- `data/fixtures/`: small saved payloads or test fixtures
- `data/snapshots/`: scratch outputs and exported local snapshots
- `docs/`: architecture notes, API notes, and milestones
- `infra/`: Docker, Kubernetes, and Terraform files later on
- `scripts/`: polling, normalization, and utility scripts
- `tests/`: unit and integration tests

## First milestone

By the end of week 1, this project should contain:
- a working script that fetches live DB API data
- a normalized representation of station or service data
- notes on the endpoints you chose and why
- one async exercise that compares sync and async request patterns
