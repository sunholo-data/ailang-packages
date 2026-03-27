# sunholo/auth

## When to use this package
Use when your API needs key-based authentication, bearer token extraction, or Firebase ID token verification. Provides SHA-256 hashing with constant-time comparison (prevents timing attacks), bearer token extraction from HTTP headers, and Firebase JWT verification (both local RSA and REST API options).

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

### Firebase JWT verification (local RSA — recommended)
```ailang
import pkg/sunholo/auth/firebase_jwt (verifyFirebaseJWTFull, fetchFirebasePublicKeys, verifyFirebaseJWT)

-- Option 1: Full flow (fetch keys + verify + check expiry)
match verifyFirebaseJWTFull(idToken, "my-project-id", nowUnix) {
  Ok(user) => println("Verified: " ++ user.uid ++ " " ++ user.email),
  Err(e) => println("Auth failed: " ++ e)
}

-- Option 2: Fetch keys once, verify many tokens (pure after key fetch)
match fetchFirebasePublicKeys() {
  Ok(keys) => {
    let result1 = verifyFirebaseJWT(token1, "my-project", keys);
    let result2 = verifyFirebaseJWT(token2, "my-project", keys)
  },
  Err(e) => println("Key fetch failed: " ++ e)
}
```

### Firebase verification (REST API — legacy)
```ailang
import pkg/sunholo/auth/firebase_token (verifyIdToken)

-- Requires FIREBASE_WEB_API_KEY env var
match verifyIdToken(idToken) {
  Ok(user) => println("Verified: " ++ user.uid),
  Err(e) => println("Auth failed: " ++ e)
}
```

## Exported functions

| Function | Module | Signature | Effects | Description |
|----------|--------|-----------|---------|-------------|
| `validateKeyHash` | auth/keys | `(string, string) -> bool` | pure | Compare key's SHA-256 against stored hash (constant-time) |
| `hashKey` | auth/keys | `string -> string` | pure | SHA-256 hex hash for storage |
| `isValidKeyFormat` | auth/keys | `(string, int, string) -> bool` | pure | Check prefix + minimum length |
| `extractBearer` | auth/bearer | `string -> Option[string]` | pure | Extract token from "Bearer ..." header |
| `hasBearer` | auth/bearer | `string -> bool` | pure | Check if bearer prefix present |
| `verifyFirebaseJWT` | auth/firebase_jwt | `(string, string, Json) -> Result[FirebaseUser, string]` | pure | Verify Firebase token with pre-fetched keys |
| `fetchFirebasePublicKeys` | auth/firebase_jwt | `() -> Result[Json, string]` | Net | Fetch Google's public keys |
| `verifyFirebaseJWTFull` | auth/firebase_jwt | `(string, string, int) -> Result[FirebaseUser, string]` | Net | Full flow: fetch keys + verify + validate claims |
| `verifyIdToken` | auth/firebase_token | `string -> Result[FirebaseUser, string]` | Net, Env | Verify via REST API (legacy, needs API key) |

## Common patterns
- Store `hashKey(rawKey)` in your database, never the raw key
- Always use `validateKeyHash` (constant-time) instead of `==` to compare hashes
- Combine with `sunholo/gcp-auth` for GCP service-to-service authentication
- Key format: use `isValidKeyFormat("dp_", 35, key)` to validate before hashing
- **Firebase JWT**: Use `verifyFirebaseJWT` (pure) for testing or when you manage key caching yourself
- **Firebase JWT**: Use `verifyFirebaseJWTFull` for simple one-shot verification
- **Firebase REST**: Use `verifyIdToken` only if you have `FIREBASE_WEB_API_KEY` and prefer the REST approach
