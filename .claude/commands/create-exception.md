---
description: Creates module exception classes in application/exceptions.py — the generic {Module}Exception returning HTTP 500 plus one specific StandardException subclass per business rule, each mapped to a ResponseMessages constant and the right HTTP status. Use when the user asks to add an exception, an error case, a not-found or conflict error, or when a new business rule needs its own failure response.
argument-hint: "<module> <ExceptionName>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

<arguments module="$0" exception="$1">$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/create-exception/SKILL.md
