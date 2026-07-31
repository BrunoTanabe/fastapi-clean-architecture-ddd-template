---
description: Creates Pydantic v2 request and response schemas in presentation/schemas.py with full Field and ConfigDict declarations, plus the {Entity}PaginationParams class for list endpoints. Use when the user asks to add a schema, create request or response models, add a Pydantic model, or define the HTTP contract of an endpoint.
argument-hint: "<module> <action>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

<arguments module="$0" action="$1">$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/create-schema/SKILL.md
