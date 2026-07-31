---
description: Creates or extends the {Module}UseCases class in application/use_cases.py — Protocol collaborators on the constructor, the 3-branch try/except, business-rule checks, the UNSET merge for partial updates, cache-aside policy, and SharedUseCases notifications. Use when the user asks to add a use case, add business logic, orchestrate a new operation, or wire the application layer of an endpoint.
argument-hint: "<module> <operation>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

<arguments module="$0" operation="$1">$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/create-use-case/SKILL.md
