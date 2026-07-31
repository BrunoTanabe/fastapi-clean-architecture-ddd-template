---
description: Audits modules against the project's architectural conventions — layer boundaries, the three error-handling shapes, naming, mapper completeness, cache rules, and registration — reporting every violation with a file and line citation, then fixing with permission. Use when the user asks to check standards, audit the architecture, run a compliance pass, or sanity-check before a release.
argument-hint: "[module|all]"
allowed-tools: Read, Edit, Glob, Grep, Bash(uv run *), Bash(ls *)
disable-model-invocation: true
---

<arguments>$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/check-standards/SKILL.md
