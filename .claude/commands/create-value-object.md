---
description: Creates a domain value object — a plain class with _normalize, _validate, __str__, and __eq__ that raises DomainError on invalid input — and places it in the owning module or in shared/ according to the reuse rule. Use when the user asks to add a value object, wrap a primitive with validation, or extract a validated concept such as an email, phone, name, slug, or currency amount out of an entity.
argument-hint: "<module> <ValueObjectName>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

<arguments module="$0" value_object="$1">$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/create-value-object/SKILL.md
