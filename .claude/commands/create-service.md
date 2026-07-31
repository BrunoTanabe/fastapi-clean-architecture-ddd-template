---
description: Creates a service for a module — an I{Name}Service Protocol in application/interfaces.py, its implementation in infrastructure/services.py, and the DI factory, for wrapping an external system or a stateful in-process component such as email, storage, queues, token generation, or real-time delivery. Use when the user asks to add a service, integrate an external system, or put infrastructure logic behind a Protocol.
argument-hint: "<module> <ServiceName>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

<arguments module="$0" service="$1">$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/create-service/SKILL.md
