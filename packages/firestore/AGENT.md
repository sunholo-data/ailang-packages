# sunholo/firestore

## When to use this package
Use when your AILANG service needs to read/write Firestore documents. This is the **general-purpose Firestore client** — it handles auth, field encoding, CRUD, and structured queries. Build domain-specific repo modules on top of this rather than rolling your own REST API calls.

## Quick start
```ailang
import pkg/sunholo/firestore/client (getDoc, setDoc, deleteDoc, getSubDoc, setSubDoc)
import pkg/sunholo/firestore/fields (stringVal, intVal, boolVal, buildFields, asStr, asInt, asBoolField)
import pkg/sunholo/firestore/query (runQuery, where, orderBy, Asc, Desc)

-- Write a document
let fields = buildFields([
  { key: "name", value: stringVal("Alice") },
  { key: "age", value: intVal(30) },
  { key: "active", value: boolVal(true) }
])
match setDoc("users", "uid_123", fields) {
  Ok(_) => -- written
  Err(e) => -- error
}

-- Read a document
match getDoc("users", "uid_123") {
  Ok(fields) => {
    let name = asStr(fields, "name");     -- "Alice"
    let age = asInt(fields, "age");       -- 30
    let active = asBoolField(fields, "active")  -- true
  },
  Err(e) => -- not found or error
}

-- Subcollections
match setSubDoc("users", "uid_123", "sessions", "sess_abc", sessionFields) {
  Ok(_) => -- written
  Err(e) => -- error
}

-- Query with filters
let filters = [where("status", "EQUAL", stringVal("active"))]
let orders = [orderBy("createdAt", Desc)]
match runQuery("tasks", filters, orders, 10) {
  Ok(docs) => -- docs is [{id: string, fields: Json}]
  Err(e) => -- query error
}

-- Delete
match deleteDoc("users", "uid_123") {
  Ok(_) => -- deleted
  Err(e) => -- error
}
```

## Exported functions

### client module
| Function | Signature | Description |
|----------|-----------|-------------|
| `getDoc` | `(collection, docId) -> Result[Json, string] ! {Net, FS, Env}` | Get document fields |
| `setDoc` | `(collection, docId, fields) -> Result[(), string] ! {Net, FS, Env}` | Create or overwrite |
| `deleteDoc` | `(collection, docId) -> Result[(), string] ! {Net, FS, Env}` | Delete document |
| `docExists` | `(collection, docId) -> Result[bool, string] ! {Net, FS, Env}` | Check existence |
| `getSubDoc` | `(parent, parentId, sub, docId) -> Result[Json, string] ! {Net, FS, Env}` | Get from subcollection |
| `setSubDoc` | `(parent, parentId, sub, docId, fields) -> Result[(), string] ! {Net, FS, Env}` | Write to subcollection |
| `deleteSubDoc` | `(parent, parentId, sub, docId) -> Result[(), string] ! {Net, FS, Env}` | Delete from subcollection |
| `baseUrl` | `() -> Result[string, string] ! {Env}` | Get Firestore REST API base URL |

### fields module
| Function | Signature | Description |
|----------|-----------|-------------|
| `stringVal` | `string -> Json` | Encode string field |
| `intVal` | `int -> Json` | Encode int field |
| `boolVal` | `bool -> Json` | Encode bool field |
| `floatVal` | `float -> Json` | Encode float field |
| `timestampVal` | `string -> Json` | Encode timestamp field |
| `arrayVal` | `[Json] -> Json` | Encode array field |
| `mapVal` | `Json -> Json` | Encode nested map field |
| `nullVal` | `() -> Json` | Encode null field |
| `asStr` | `(Json, string) -> string` | Decode string (default: "") |
| `asInt` | `(Json, string) -> int` | Decode int (default: 0) |
| `asBoolField` | `(Json, string) -> bool` | Decode bool (default: false) |
| `asFloat` | `(Json, string) -> float` | Decode float (default: 0.0) |
| `asTimestamp` | `(Json, string) -> string` | Decode timestamp |
| `asMap` | `(Json, string) -> Json` | Decode nested map |
| `buildFields` | `[{key, value}] -> Json` | Build fields from list |
| `hasField` | `(Json, string) -> bool` | Check field exists |

### query module
| Function | Signature | Description |
|----------|-----------|-------------|
| `runQuery` | `(collection, filters, orders, limit) -> Result[[{id, fields}], string] ! {Net, FS, Env}` | Execute query |
| `where` | `(field, op, value) -> QueryFilter` | Build filter |
| `orderBy` | `(field, direction) -> QueryOrder` | Build sort |

## Environment variables
- `GOOGLE_CLOUD_PROJECT` — GCP project ID (required)
- `FIRESTORE_DATABASE` — Database name (optional, defaults to `(default)`)

## Common patterns
- Build fields with `buildFields` + encode helpers, read with `asStr`/`asInt`/`asBoolField`
- Use `getSubDoc`/`setSubDoc` for subcollection patterns like `users/{uid}/sessions/{sid}`
- Query operators: `EQUAL`, `NOT_EQUAL`, `LESS_THAN`, `GREATER_THAN`, `IN`, `ARRAY_CONTAINS`
- Effects: `--caps Net,FS,Env` (Net for REST API, FS for ADC credentials, Env for project config)
- Requires AILANG >= 0.9.5 (PATCH/DELETE HTTP methods)
