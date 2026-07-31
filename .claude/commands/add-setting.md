---
description: Adds a configuration value across every place it must appear — .env.example, .env, the typed field in app/core/settings.py, any validator or computed_field, and docker-compose when a container needs it. Use when the user asks to add an env var, a setting, a feature flag, a timeout, or configuration for a new integration.
argument-hint: "<SETTING_NAME>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

<arguments>$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/add-setting/SKILL.md
