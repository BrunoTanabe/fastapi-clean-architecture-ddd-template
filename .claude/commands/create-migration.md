---
description: Generates, reviews, and applies an Alembic schema migration — verifies the model is registered in migrations/env.py, runs autogenerate, walks a review checklist over the generated revision, then upgrades. Use right after an ORM model was added or changed, or when the user asks to create a migration or apply a schema change. For inserting data, use create-seed-migration.
argument-hint: "[message]"
allowed-tools: Read, Edit, Glob, Grep, Bash(uv run *), Bash(ls *)
---

<arguments>$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/create-migration/SKILL.md
