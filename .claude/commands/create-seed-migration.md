---
description: Creates a hand-written Alembic data-seed revision that inserts reference rows with raw SQL and bound parameters, with a downgrade that removes exactly those rows. Use when the user asks to seed data, insert default rows, add a default admin or lookup values, or write a data migration. For schema changes, use create-migration.
argument-hint: "<what-to-seed>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *), Bash(ls *)
---

<arguments>$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/create-seed-migration/SKILL.md
