# Reference — Security and Authentication

Nested JWTs, the `authenticate_*` dependencies, API keys, and the allowlist tiers. Everything here
lives in `app/core/security.py` and `app/core/settings.py`.

## Contents

- [Token design](#token-design)
- [Key material](#key-material)
- [The authentication chain](#the-authentication-chain)
- [Router dependencies](#router-dependencies)
- [The allowlist tiers](#the-allowlist-tiers)
- [Registering an endpoint](#registering-an-endpoint)
- [Path-rule matching](#path-rule-matching)
- [WebSocket authentication](#websocket-authentication)
- [API-key authentication](#api-key-authentication)
- [Password hashing](#password-hashing)
- [Settings](#settings)

## Token design

Tokens are **nested JWTs**: a JWS signed with Ed25519, wrapped inside a JWE encrypted with
ECDH-ES + A256GCM (`jwcrypto`). Signing proves authenticity; the outer encryption keeps claims
opaque to the client.

They travel in **cookies**, never `Authorization` headers, alongside a device-id cookie issued by
`DeviceIdMiddleware`. HMAC-SHA256 fingerprints of each token's `jti` are stored in the database
(`AuthenticationModel` → `RefreshTokenModel` → `AccessTokenModel`) so tokens can be revoked and
tampering detected without storing the token itself.

`_token_fingerprint(material, namespace)` produces those fingerprints; `hash_tokens` applies them
across an `Authentication`. The `previous_hashed_jti` field on both token entities supports
rotation — the prior fingerprint stays valid briefly so an in-flight request is not killed by a
concurrent refresh.

The `TokenType` enum (`authentication/domain/enums.py`) has one member: `BEARER = "Bearer"`.

## Key material

Signing (Ed25519) and encryption (X25519) key pairs load from PEM files under `secrets/keys/`,
paths configured by `JWT_SIGNING_*_KEY_PATH` and `JWT_ENCRYPTION_*_KEY_PATH`. Private keys are
password-protected with `JWT_SIGNING_KEY_PASSWORD` / `JWT_ENCRYPTION_KEY_PASSWORD`.

`settings.generate_authentication_keys()` creates any missing pair on first boot when
`JWT_AUTO_GENERATE_KEYS` is true. The keys are exposed as `cached_property` JWK objects
(`JWT_SIGNING_PRIVATE_KEY`, `JWT_SIGNING_PUBLIC_KEY`, `JWT_ENCRYPTION_PRIVATE_KEY`,
`JWT_ENCRYPTION_PUBLIC_KEY`), so a key rotation requires a process restart.

Never log, serialize, or cache key material or a raw token.

## The authentication chain

```
Authentication            one row per (user, user_agent, device) triple
└── RefreshToken          rotated on refresh; revocable
    └── AccessToken       short-lived; carries the role as `permission`
```

`Authentication` also records request provenance — `ip_address`, `user_agent`, `device`,
`location`, `accept_language`, `accept_encoding`, `origin`, `referer` — normalized in
`__post_init__`. Its behaviour methods (`create_tokens`, `renew_tokens`, `refresh_access_token`,
`revoke`) own token lifecycle transitions; the use case orchestrates, the entity mutates.

The composite unique constraint on `(user_id, user_agent, device)` means one live authentication
per user per device. Logging in again from the same device renews rather than duplicates.

## Router dependencies

```python
from typing import Annotated

from fastapi import Depends

from app.core.security import (
    authenticate_user,
    authenticate_manager,
    authenticate_admin,
    no_authentication,
)
from app.modules.authentication.domain.entities import Authentication


authentication: Annotated[Authentication, Depends(authenticate_user)]     # any authenticated user
authentication: Annotated[Authentication, Depends(authenticate_manager)]  # manager or above
authentication: Annotated[Authentication, Depends(authenticate_admin)]    # admin only
_: Annotated[None, Depends(no_authentication)]                            # public endpoint
```

| Dependency | Returns | Used by |
|------------|---------|---------|
| `no_authentication` | `None` | Public endpoints; still checks `SECURITY_NO_AUTH_PATHS` |
| `authenticate_user` | `Authentication` | Any authenticated role |
| `authenticate_manager` | `Authentication` | Manager and admin |
| `authenticate_admin` | `Authentication` | Admin only |
| `authenticate_refresh` | `Authentication` | `PATCH /api/v1/authentication/refresh` — reads the refresh cookie |
| `authenticate_logout` | `Authentication` | `DELETE /api/v1/authentication/logout` — tolerates partially expired state |
| `authenticate_websocket` | `Authentication` | WebSocket handshake |
| `authenticate_api_key` | `Authentication` | `X-API-Key` header flow |

**Handlers inject `Authentication`, never `User`.** Read the actor as `authentication.user`.
Passing `User` directly would lose the session, device, and role-at-issue context that the
allowlist check and audit logging depend on.

Even `no_authentication` enforces an allowlist: a public endpoint missing from
`SECURITY_NO_AUTH_PATHS` raises `UserHasNotPermissionException`. There is no unguarded route.

## The allowlist tiers

Role tiers are enforced **twice** — once by the dependency and once by the path allowlist. Both
must agree or the endpoint returns 403 with a valid token.

```python
SECURITY_NO_AUTH_PATHS            # public
SECURITY_USER_ALLOWED_PATHS       # = NO_AUTH + user paths
SECURITY_MANAGER_ALLOWED_PATHS    # = USER + manager paths
SECURITY_ADMIN_ALLOWED_PATHS      # = MANAGER + admin paths
SECURITY_API_KEY_ALLOWED_PATHS    # independent; currently empty
```

Each tier spreads the previous one (`*self.SECURITY_USER_ALLOWED_PATHS, ...`), so a path is
declared once at its lowest permitted role. `_has_access_to_endpoint` picks the tier from the
role — `None` → no-auth, `ADMIN` → admin, `MANAGER` → manager, anything else → user — and the
API-key tier is checked separately by `_has_access_to_api_key_endpoint`.

## Registering an endpoint

Add **both** slash forms of every rule to the tier matching the route's `authenticate_*`
dependency:

```python
# KEY
_path_rule("/api/v1/key/", "POST"),
_path_rule("/api/v1/key", "POST"),
_path_rule("/api/v1/key/{id}/rotate/", "PATCH"),
_path_rule("/api/v1/key/{id}/rotate", "PATCH"),
```

Rules are grouped by module under an uppercase comment, matching the double-route decorators on
the handler. Forgetting the trailing-slash variant is the single most common cause of "works in
Swagger, 403 from the client".

`_path_rule(endpoint, method)` returns a read-only `MappingProxyType` — the tuples are immutable
by design.

## Path-rule matching

`_match_path_rules` compares the method first, then converts the rule into a regex by replacing
`{param}` with a named group that matches any non-slash run:

```
"/api/v1/key/{id}/rotate/"  →  "^/api/v1/key/(?P<id>[^/]+)/rotate/$"
```

Consequences:

- A parameter cannot span a `/`. A path parameter containing a slash will not match.
- Matching is exact — no prefix or wildcard rules.
- The method comparison is case-sensitive and uppercase.

All three access-check helpers return `False` on any internal error rather than raising, so a
malformed rule fails closed.

## WebSocket authentication

`authenticate_websocket` runs a different order of checks:

1. Validate the connection's `Origin` header against `settings.SECURITY_ALLOW_ORIGINS`, raising
   the shared `OriginNotAllowedException` on mismatch. `CORSMiddleware` does **not** cover the WS
   handshake, so this guard has to live in the dependency.
2. Read the access token and device from cookies.
3. Decode the nested JWT and load the authentication.
4. Confirm the session role matches the stored token permission.

WebSocket paths are not listed in the HTTP allowlist tiers — `authenticate_websocket` is the
whole check. The exception is the decoy `GET /api/v1/websocket/connect` used to document the
channel in OpenAPI, which does appear in `SECURITY_NO_AUTH_PATHS`.

## API-key authentication

Fully implemented and wired to the `key` module. `SECURITY_API_KEY_ALLOWED_PATHS` returns an empty
tuple today, which means no endpoint has opted in — adding paths there enables the mechanism.

- `api_key_header = APIKeyHeader(name=settings.AUTH_API_KEY_NAME, ...)` — the `X-API-Key` header,
  declared in the OpenAPI schema as `AUTH_API_KEY_SCHEME_NAME`.
- `generate_api_key(key: Key) -> Key` — builds a raw key from `API_KEY_ENTROPY_BYTES` of entropy,
  sets `prefix`, `last_four`, and the HMAC-SHA256 `hashed_key`, and puts the raw value in the
  transient `plain_key` field.
- `verify_api_key(plain_key, hashed_key) -> bool` — recomputes the fingerprint and compares with
  `hmac.compare_digest` (constant time).
- `_resolve_api_key` — reads the header, checks the cache, falls back to the repository, and
  distinguishes missing / invalid / revoked / expired via `ApiKeyNotProvidedException`,
  `ApiKeyInvalidException`, `ApiKeyRevokedException`, `ApiKeyExpiredException`.

**The raw key is returned exactly once**, in the create and rotate responses. It is never
persisted, never logged, and never cached — `Key.plain_key` is transient and must not appear in
`entity_cache_mapper`. This is why `PostgresKeyRepository.get_key_by_hashed_key` omits the
`is_active` filter: the auth path has to tell a revoked key from a nonexistent one.

## Password hashing

`hash_password` / `verify_password` wrap `pwdlib` with Argon2. Passwords are hashed in the
application layer; the `User` entity carries the transient `password` alongside the persisted
`hashed_password`, the same transient/persisted split `Key` uses for `plain_key` / `hashed_key`.

## Settings

| Group | Keys |
|-------|------|
| JWT | `JWT_ISSUER`, `JWT_AUDIENCE`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`, `JWT_REFRESH_TOKEN_EXPIRE_DAYS`, `JWT_HASH_FINGERPRINT`, `JWT_AUTO_GENERATE_KEYS`, `JWT_KEYS_DIR`, `JWT_*_KEY_PATH`, `JWT_*_KEY_PASSWORD` |
| Cookies | `COOKIES_MAX_AGE_SECONDS`, `COOKIES_TOKEN_TYPE_KEY`, `COOKIES_ACCESS_TOKEN_KEY`/`_PATH`, `COOKIES_REFRESH_TOKEN_KEY`/`_PATH`, `COOKIES_DEVICE_KEY`, `COOKIES_DOMAIN`, `COOKIES_SAME_SITE` |
| API key | `API_KEY_PREFIX`, `API_KEY_HASH_FINGERPRINT`, `API_KEY_ENTROPY_BYTES` |
| Auth schemes | `AUTH_BEARER_TOKEN_SCHEME_NAME`/`_DESCRIPTION`, `AUTH_API_KEY_NAME`, `AUTH_API_KEY_SCHEME_NAME`, `AUTH_API_KEY_DESCRIPTION` |
| Security | `SECURITY_ALLOW_ORIGINS`, `SECURITY_ALLOW_HEADERS`, `SECURITY_ALLOW_METHODS`, `SECURITY_EMAIL_ALLOWED_DOMAINS`, `SECURITY_ADMIN_EMAIL`, `SECURITY_ADMIN_PASSWORD` |

`COOKIES_ACCESS_TOKEN_MAX_AGE` and `COOKIES_REFRESH_TOKEN_MAX_AGE` are computed from the JWT
expiry settings — set the expiry, not the cookie age.
