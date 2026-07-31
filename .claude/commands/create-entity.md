---
description: Creates a domain entity dataclass extending BaseEntity with __post_init__ validation, plus the companion {Entity}List and {Entity}Pagination dataclasses and the {Entity}SortField enum for paginated modules. Use when the user asks to add a domain entity, model a domain object, or add pure-Python types under domain/. For a standalone value object use create-value-object.
argument-hint: "<module> <EntityName>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

<arguments module="$0" entity="$1">$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/create-entity/SKILL.md
