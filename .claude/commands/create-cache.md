---
description: Adds Redis cache-aside caching to a module — the I{Entity}Cache Protocol, the Redis{Entity}Cache implementation with namespaced keys and tombstone invalidation, the entity_cache_mapper and cache_entity_mapper serializers, the DI factory, and the read-through and invalidate calls in the use case. Use when the user asks to add a cache, cache an entity, speed up a lookup, or wire Redis into a module.
argument-hint: "<module> <EntityName> [operation]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

<arguments module="$0" entity="$1" operation="$2">$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/create-cache/SKILL.md
