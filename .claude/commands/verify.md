---
description: Smoke-checks freshly scaffolded or edited code — runs ruff, confirms the app graph imports, checks module and allowlist registration, and optionally boots the app. Read-only; reports findings with real command output and offers fixes without applying them. Use right after scaffolding a module or endpoint, or when the user asks to verify or sanity-check a change.
argument-hint: "[module]"
allowed-tools: Read, Glob, Grep, Bash(uv run *), Bash(ls *), Bash(git status *)
disable-model-invocation: true
---

<arguments>$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/verify/SKILL.md
