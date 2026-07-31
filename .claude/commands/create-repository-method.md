---
description: Adds a repository method to a module — the Protocol signature in application/interfaces.py and the Postgres implementation in infrastructure/repositories.py, interface first. Use when the user asks to add a repository method, implement a database query, add a CRUD operation, or wire persistence for a new use case.
argument-hint: "<module> <method>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

<arguments module="$0" method="$1">$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/create-repository-method/SKILL.md
