# OfferOps

OfferOps is a small portfolio project for managing a job search like a product and data system.

The goal is to grow this project over 8 weeks while learning:
- async Python
- FastAPI
- PostgreSQL
- RAG
- dbt
- Kafka
- Spark
- Docker, Kubernetes, and Terraform basics

## Week 1 focus

Week 1 is intentionally small:
- set up the OfferOps project
- collect sample job-posting data
- practice Python async basics
- build a simple parsing script

## Starter structure

- `api/`: backend application code
- `data/`: local seed data and processed outputs
- `docs/`: architecture notes, decisions, and screenshots
- `infra/`: future Docker, Kubernetes, and Terraform files
- `scripts/`: one-off utilities such as parsing and ingestion
- `tests/`: test files

## First milestone

By the end of week 1, this project should contain:
- a small dataset of saved job descriptions
- a Python script that parses those files into JSON
- a short note on sync vs async behavior
