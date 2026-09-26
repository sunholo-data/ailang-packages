# Changelog — sunholo/duckdb

## 0.2.1

Fixes 0.2.0, which made writes read-only too.

`schema.execScript` was implemented by calling `query`, so the read/write
split was a naming convention rather than a fact. Turning `query` read-only
therefore turned every write read-only as well, and a fresh database could not
be created at all: `eparse index` failed with "Cannot open database ... in
read-only mode: database does not exist". The write path is now its own
invocation (`query.execRaw`), and both share one process wrapper so the split
cannot quietly collapse again.

0.2.0 was never depended on by a published package, so nothing was broken in
the field.

## 0.2.0

Reads open the database **read-only**.

DuckDB allows either many readers or one writer. `query` (and so `queryAll`,
`queryOne`, `scalar`) opened read-write for a SELECT, which took the exclusive
lock — so two simultaneous reads of the same database collided. Measured
26 Sept 2026 against an 83,825-message archive: **3 of 4 concurrent
`eparse query` calls failed** with `Conflicting lock is held`, and DuckDB's own
error text names `-readonly` as the fix. Anything serving reads concurrently —
an MCP server, several shells, a scheduled job alongside a person — hit this.

Two behaviour changes follow, both deliberate:

- **A write sent through the read half is refused** by DuckDB rather than
  performed. Writes belong in `schema.execScript`, which still opens
  read-write. Nothing in `sunholo/email` wrote through `query*`.
- **Querying a path that does not exist is an error** (`Cannot open database
  ... in read-only mode: database does not exist`) instead of silently
  CREATING an empty database and returning no rows. A caller that meant to
  create one wants `execScript`; a caller with a typo wants the error.

`":memory:"` keeps the read-write form: DuckDB refuses to launch an in-memory
database read-only, and it has no second process to race.

No signature changed, and no new effect — the decision is made from the path
string, so the package's effect ceiling is untouched. That matters because
`sunholo/email` deliberately carries no `FS` in its ceiling, and an existence
check here would have forced one on it.
