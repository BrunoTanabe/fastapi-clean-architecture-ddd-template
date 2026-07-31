---
description: Creates one complete endpoint across every layer of an existing module — schema, mapper, Protocol signature, repository method, use case, cache wiring, OpenAPI docs, router handler — and registers both path forms in the security allowlist. Use when the user asks to add an endpoint, create a CRUD operation, or wire a route end to end.
argument-hint: "<module> <operation>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

<arguments module="$0" operation="$1">$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/create-endpoint/SKILL.md
