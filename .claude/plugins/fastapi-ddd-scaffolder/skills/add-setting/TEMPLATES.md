# Setting Templates

## Contents

- [.env.example and .env](#envexample-and-env)
- [Typed field](#typed-field)
- [List field](#list-field)
- [Enum field with validator](#enum-field-with-validator)
- [Optional field with a default](#optional-field-with-a-default)
- [Computed field](#computed-field)
- [docker-compose entry](#docker-compose-entry)
- [Consuming a setting](#consuming-a-setting)

## .env.example and .env

Same key, same group, same order in both. `.env.example` carries an empty or obviously fake value;
`.env` carries the real one.

```bash
# .env.example
# REDIS
REDIS_HOST=
REDIS_PORT=
REDIS_MAX_CONNECTIONS=
REDIS_CACHE_VERSION=
```

```bash
# .env
# REDIS
REDIS_HOST=cache
REDIS_PORT=6379
REDIS_MAX_CONNECTIONS=50
REDIS_CACHE_VERSION=1
```

Values may be quoted or bare — the `strip_quotes` validator removes surrounding quotes from every
string.

Never put a real credential in `.env.example`. `SECURITY_ADMIN_PASSWORD=` with no value is correct;
a working password is a leak the moment the repository is public.

## Typed field

In the matching uppercase group in `app/core/settings.py`:

```python
class Settings(BaseSettings):
    # REDIS
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_SSL: bool
    REDIS_MAX_CONNECTIONS: int
```

No default means required: pydantic-settings raises a `ValidationError` at construction naming the
missing key. That is the behaviour you want — a required setting silently defaulting to something
plausible is how environments drift.

`int` and `bool` are coerced from the string in the file. `bool` accepts `true`/`false`, `1`/`0`,
`yes`/`no` in any case.

## List field

```python
    SECURITY_ALLOW_ORIGINS: list[str]
    SECURITY_EMAIL_ALLOWED_DOMAINS: list[str]
```

pydantic-settings parses a JSON array from the environment:

```bash
SECURITY_ALLOW_ORIGINS='["http://localhost:3000","https://app.example.com"]'
SECURITY_EMAIL_ALLOWED_DOMAINS='[]'
```

An empty list is meaningful — `SECURITY_EMAIL_ALLOWED_DOMAINS=[]` disables the domain allowlist in
`Email`, rather than rejecting everything.

## Enum field with validator

The enum lives in `shared/domain/enums.py`; the validator turns the raw string into a member and
produces a clear error otherwise. Reference: `COOKIES_SAME_SITE`.

```python
    COOKIES_SAME_SITE: CookieSameSite


    @field_validator("COOKIES_SAME_SITE", mode="before")
    @classmethod
    def validate_cookies_same_site(cls, v):
        if isinstance(v, CookieSameSite):
            return v

        if isinstance(v, str):
            value = v.strip().strip('"').strip("'").lower()
            try:
                return CookieSameSite(value)
            except ValueError:
                pass

        raise ValueError(
            "Invalid COOKIES_SAME_SITE. Allowed values: 'lax', 'strict', 'none'."
        )
```

The `isinstance` check first lets the field be set programmatically in a test without going through
the string path. The error message lists the allowed values — that is what makes a startup failure
self-explanatory.

## Optional field with a default

Only for values that genuinely have a safe universal default, or that are unused in some
environments.

```python
    # NGROK
    NGROK_AUTH_TOKEN: str = ""
```

`env_ignore_empty=True` in `model_config` means an empty value in `.env` falls back to the default
rather than becoming an empty string, so an optional key can be left blank.

## Computed field

For anything derived. Compute it once here instead of at every call site.

```python
    @computed_field
    @cached_property
    def REDIS_NAMESPACE(self) -> str:  # noqa
        # Every cache key hangs off this namespace. Bumping REDIS_CACHE_VERSION
        # makes the previous generation unreachable, so entries written in an old
        # payload format are never read back: they simply expire by ttl.
        return f"{self.REDIS_KEY_PREFIX}:v{self.REDIS_CACHE_VERSION}"
```

```python
    @computed_field
    @cached_property
    def COOKIES_ACCESS_TOKEN_MAX_AGE(self) -> int:  # noqa
        return self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
```

Decorator order is fixed: `@computed_field` above `@cached_property`. The `# noqa` silences the
naming warning on the uppercase method name.

`cached_property` computes once per process, so a computed setting cannot change while the app
runs. That is correct for a URL or a namespace; it is wrong for anything that must be re-read.

A computed field that reads a file — like the JWT key properties — raises on first access, not at
construction. Print it explicitly when verifying.

## docker-compose entry

Only when a container consumes the value. Compose reads `.env` from the project root
automatically, so pass the value through rather than duplicating it:

```yaml
  cache:
    command: >
      redis-server
      --requirepass "${REDIS_PASSWORD}"
      --maxmemory ${REDIS_MAX_MEMORY}
    environment:
      - "REDIS_PASSWORD=${REDIS_PASSWORD}"
    ports:
      - "${REDIS_PORT}:6379"
```

The `api` service mounts the project directory, so it reads `.env` directly and needs no
`environment` entry for an application setting.

Some keys exist only for compose and never appear in `Settings` — `REDIS_MAX_MEMORY`,
`PGADMIN_EMAIL`, `REDISINSIGHT_PORT`. They still belong in `.env.example`.

## Consuming a setting

```python
from app.core.settings import settings

timeout = settings.REDIS_SOCKET_TIMEOUT_SECONDS
```

Always through `settings`. Never `os.environ`, never `os.getenv`, and never re-instantiate
`Settings()` — the module-level `settings` instance is the single source, and its
`cached_property` values are computed against it.
