---
description: Creates a SQLAlchemy ORM model extending BaseModel in infrastructure/models.py — columns with name and comment, enum columns, foreign keys, relationships, constraints and indexes — then registers it in migrations/env.py so Alembic autogenerate can see it. Use when the user asks to add a database model, create an ORM model, add a table, or persist an entity.
argument-hint: "<module> <EntityName>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

<arguments module="$0" entity="$1">$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/create-model/SKILL.md
