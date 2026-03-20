# sunholo/auth

## When to use this package
Use when your API needs key-based authentication. Provides SHA-256 hashing with constant-time comparison (prevents timing attacks) and bearer token extraction from HTTP headers. Pure functions — no effects required.

## Quick start
```ailang
import pkg/sunholo/auth/keys (validateKeyHash, hashKey)
import pkg/sunholo/auth/bearer (extractBearer)

-- Hash a key for storage (never store raw keys)
let storedHash = hashKey("dp_a1b2c3d4e5f6...")

-- Validate incoming key against stored hash
let valid = validateKeyHash(userKey, storedHash)

-- Extract bearer token from Authorization header
match extractBearer(authHeader) {
  Some(token) => -- use token
  None => -- no bearer token present
}
```

## Exported functions

| Function | Module | Signature | Description |
|----------|--------|-----------|-------------|
| `validateKeyHash` | auth/keys | `(string, string) -> bool` | Compare key's SHA-256 against stored hash (constant-time) |
| `hashKey` | auth/keys | `string -> string` | SHA-256 hex hash for storage |
| `isValidKeyFormat` | auth/keys | `(string, int, string) -> bool` | Check prefix + minimum length |
| `extractBearer` | auth/bearer | `string -> Option[string]` | Extract token from "Bearer ..." header |
| `hasBearer` | auth/bearer | `string -> bool` | Check if bearer prefix present |

## Common patterns
- Store `hashKey(rawKey)` in your database, never the raw key
- Always use `validateKeyHash` (constant-time) instead of `==` to compare hashes
- Combine with `sunholo/gcp-auth` for GCP service-to-service authentication
- Key format: use `isValidKeyFormat("dp_", 35, key)` to validate before hashing
