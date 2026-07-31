---
description: Adds OpenAPI documentation to a module — the router_docs dict carrying the prefix, tag, and standard error responses, plus one {action}_docs dict per endpoint with summary, description, status code, response model, and examples. Use when the user asks to add OpenAPI docs, document an endpoint, or populate presentation/docs.py.
argument-hint: "<module> [endpoint]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

<arguments module="$0" endpoint="$1">$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/create-docs/SKILL.md
