# Infra

This folder now starts being used in Week 2 for local PostgreSQL.

Current contents:
- [docker-compose.yml](/Users/wixx3r/Documents/BahnOps/bahnops/infra/docker-compose.yml:1): local PostgreSQL container setup
- [postgres/init/001_init.sql](/Users/wixx3r/Documents/BahnOps/bahnops/infra/postgres/init/001_init.sql:1): first Week 2 schema

Validate the Compose configuration:

```bash
docker compose --env-file .env -f infra/docker-compose.yml config
```

Start PostgreSQL:

```bash
docker compose --env-file .env -f infra/docker-compose.yml up -d
```

Check the Python connection:

```bash
python3 scripts/check_postgres.py
```

Apply the initial schema:

```bash
docker exec -i bahnops-postgres psql -U <postgres-user> -d <postgres-db> < infra/postgres/init/001_init.sql
```

Confirm the tables exist:

```bash
docker exec -it bahnops-postgres psql -U <postgres-user> -d <postgres-db> -c "\\dt"
```

Later weeks can still expand this folder with:
- `Dockerfile`
- `k8s/`
- `terraform/`
