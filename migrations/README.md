# ALEMBIC MIGRATIONS

## 1. Alembic Migrations Main Commands

- Initialize alembic migrations:
```bash
alembic init alembic
```

- Auto-generate a new migration:
```bash
alembic revision --autogenerate -m "migration_message"
```

- Apply the latest migrations to the database:
```bash
alembic upgrade head
```

- Set the revision as head:
```bash
alembic stamp head
```

- Check the current revision:
```bash
alembic current
```

- Reset migrations to anyone revision:
```bash
alembic stamp head --purge
```

- Set the revision as base:
```bash
alembic stamp base
```

- Downgrade the database to the previous migration:
```bash
alembic downgrade -1
```

## 1.1 Commands to initialize Alembic Management in Homolog and Production Environments (Only in the first time)

- 1° Set the revision as head:
```bash
alembic stamp head
```

- 2° Check the current revision:
```bash
alembic current
```

## 1.2 Commands to upgrade migrations in Homolog and Production Environments

- 1° Apply the latest migrations to the database:
```bash
alembic upgrade head
```

- 2° Check the current revision:
```bash
alembic current
```