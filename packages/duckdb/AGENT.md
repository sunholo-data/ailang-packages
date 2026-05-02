# sunholo/duckdb

DuckDB query client for AILANG. Execute SQL against a local `.db` file and get typed results back. Pure AILANG — no FFI, no Go bindings. Shells out to the `duckdb` CLI binary via `std/process`.

## When to use

- You need to query a DuckDB database file from AILANG
- You want SQL analytics (GROUP BY, window functions, aggregates) over local data
- Your pipeline writes a `.db` file in Python/Go and you want to read it in AILANG

## Requirements

- `duckdb` CLI must be on `PATH` (`brew install duckdb` on macOS)
- Capability: `--caps Process,FS`

## Quick start

```ailang
import pkg/sunholo/duckdb/types (openDB)
import pkg/sunholo/duckdb/query (queryAll, scalar)
import std/json (asString, asNumber, get)
import std/option (Some, None)

let db = openDB("data/index.db")

-- Query all rows
match queryAll(db, "SELECT subject, from_email FROM messages LIMIT 5") {
  Err(e)   => println("error: ${e}"),
  Ok(rows) =>
    map(\row.
      match get(row, "subject") {
        Some(v) => match asString(v) { Some(s) => println(s), None => () },
        None    => ()
      },
    rows)
}

-- Scalar query
match scalar(db, "SELECT COUNT(*) FROM messages") {
  Ok(Some(v)) => match asNumber(v) { Some(n) => println("total: ${show(n)}"), None => () },
  _           => ()
}
```

## Exported API

### `sunholo/duckdb/types`

| Symbol | Kind | Description |
|--------|------|-------------|
| `DB` | type | `{ path: string }` — lightweight DB handle |
| `Row` | type | `Json` — a JObject; use `std/json.get` to access fields |
| `QueryResult` | type | `{ columns: [string], rows: [Row], rowCount: int }` |
| `openDB` | func | `(path: string) -> DB` |

### `sunholo/duckdb/query`

| Function | Signature | Description |
|----------|-----------|-------------|
| `query` | `(DB, string) -> Result[QueryResult, string] ! {Process}` | Full result with column list |
| `queryAll` | `(DB, string) -> Result[[Row], string] ! {Process}` | All rows |
| `queryOne` | `(DB, string) -> Result[Option[Row], string] ! {Process}` | First row or None |
| `scalar` | `(DB, string) -> Result[Option[Json], string] ! {Process}` | First column of first row |

### `sunholo/duckdb/schema`

| Function | Signature | Description |
|----------|-----------|-------------|
| `execScript` | `(DB, string) -> Result[unit, string] ! {Process}` | Run DDL/DML (multi-statement ok) |
| `tableExists` | `(DB, string) -> Result[bool, string] ! {Process}` | Check if table exists |

## Accessing row fields

`Row` is a `Json` value (JObject). Use `std/json` helpers:

```ailang
import std/json (get, asString, asNumber, asBool, getString, getNumber)

-- Safe extraction
match get(row, "subject") { Some(v) => ..., None => ... }

-- Convenience (returns Option directly)
getString(row, "subject")  -- Option[string]
getNumber(row, "count")    -- Option[float]
```

## Effects

```
--caps Process,FS
```

`Process` is required to invoke the `duckdb` CLI. `FS` is used if you check DB file existence before opening.

## Error model

All functions return `Result[_, string]`. Errors include:
- `"duckdb process error: NotFound(duckdb)"` — duckdb not on PATH
- `"duckdb error (exit 1): Parser Error: ..."` — SQL syntax error
- `"failed to parse duckdb output: ..."` — unexpected output format

## Limitations (v0.1.0)

- Read-only focused: `execScript` works for DDL/inserts but bulk loading 13k+ rows via SQL strings is slow — use the Python loader for initial ingestion
- No parameterised queries: SQL is constructed as strings; callers must sanitise values
- No connection pooling: each call spawns a new duckdb process
- `Process` allowlist: if `--process-allowlist` is set, `duckdb` must be included
