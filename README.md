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

## Current capabilities

The project currently includes:
- a FastAPI service skeleton with a health endpoint
- async practice scripts for sync vs async comparison
- a live Deutsche Bahn fetch script for one station target
- a normalized station snapshot that merges planned board data with current change data
- a local PostgreSQL setup through Docker Compose

## Planned roadmap

The project is evolving in stages:
- ingestion and normalization first
- persistence and history in PostgreSQL next
- FastAPI read endpoints after storage is in place
- eventing with Kafka later
- analytics with dbt and Spark later

Detailed milestone notes live in [docs/roadmap.md](/Users/wixx3r/Documents/BahnOps/bahnops/docs/roadmap.md:1).

## Repo structure

- `api/`: FastAPI service code
- `data/fixtures/`: small saved payloads or test fixtures
- `data/snapshots/`: scratch outputs and exported local snapshots
- `docs/`: architecture notes, API notes, and milestones
- `infra/`: Docker, Kubernetes, and Terraform files later on
- `scripts/`: polling, normalization, and utility scripts
- `tests/`: unit and integration tests

## Local setup

1. Create and activate a local virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Create a local `.env` file based on `.env.example`.
4. Follow [infra/README.md](/Users/wixx3r/Documents/BahnOps/bahnops/infra/README.md:1) to start local PostgreSQL and apply the initial schema.
5. Run the fetch prototype from `scripts/fetch_db_board.py`.

## Local PostgreSQL

Week 2 uses a lightweight local PostgreSQL setup through Docker Compose.

See [infra/README.md](/Users/wixx3r/Documents/BahnOps/bahnops/infra/README.md:1) for the detailed Postgres setup, validation, and schema commands.
