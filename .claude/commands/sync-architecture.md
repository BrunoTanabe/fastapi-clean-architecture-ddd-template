---
description: Detects drift between the project code and the documentation under .claude/ — CLAUDE.md, architecture.md, the reference files, the plugin skills, and the command wrappers — then updates the docs surgically. Use after refactoring shared base types, adopting a new pattern, adding or renaming a module, bumping Python, or when the user says the docs are out of date.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git log *), Bash(ls *)
disable-model-invocation: true
---

<arguments>$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/sync-architecture/SKILL.md
