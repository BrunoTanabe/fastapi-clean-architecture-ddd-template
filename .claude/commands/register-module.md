---
description: Wires a completed module into the application — the router import and entry in app/app.py, the OpenAPI tag in custom_openapi, and both slash forms of every endpoint in the matching SECURITY_*_ALLOWED_PATHS tier. Use when the user asks to register a module, wire up a router, or when a new endpoint returns 403 with a valid token.
argument-hint: "<module>"
allowed-tools: Read, Edit, Glob, Grep, Bash(uv run *), Bash(ls *)
---

<arguments>$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/register-module/SKILL.md
