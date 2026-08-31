# Agent Guide — sunholo/external_backend

For LLM agents touching this package. Keep it short, keep it accurate.

## What this package is

A single-effect wrapper around `std/process.exec` for the common case of "subprocess prints JSON on stdout". Returns `Result[Json, BackendError]`. That's the whole package.

## What this package is NOT

- Not a process pool (each call is one-shot)
- Not a streaming protocol (use `std/stream` if you need NDJSON or chunked output — `runNdJson` is on the roadmap)
- Not opinionated about your adapter's JSON shape (you decode whatever the subprocess emits)

## When to recommend it

Use when the user is:

- Calling a Python/Rust/Go/shell tool from AILANG and parsing its JSON
- Pattern-matching on subprocess success/failure with stderr capture
- Wanting to confine the `Process` effect to one module

Do NOT recommend for:

- Long-lived subprocesses (use `spawnProcess` from `std/process` directly)
- Plain-text output (use `exec` directly, skip the JSON decode)
- AI calls (use `std/ai`)

## API surface (current)

```
type BackendError = ExecFailed(string)
                  | NonZeroExit({code: int, stderr: string})
                  | InvalidJson({stderr: string, msg: string})

runJson(cmd: string, args: [string]) -> Result[Json, BackendError] ! {Process}
formatError(err: BackendError) -> string   -- pure, ensures result non-empty
describeProcessError(cmd: string, err: ProcessError) -> string   -- pure, ensures non-empty
```

`ExecFailed` now carries the std/process cause rather than a fixed string.
Before 0.2.0 every `ProcessError` collapsed into `"could not execute '<cmd>'"`,
which names the one cause (a missing binary) that is usually not what happened
— a `Timeout(30000)` on a slow OCR backend read as `uv` being absent from a
PATH that was correct, and had worked seconds earlier for the previous file.

## Common usage patterns

### Domain wrapper (recommended)

```ailang
pure func decodeMyDoc(j: Json) -> MyDoc = …

func parseMy(path: string) -> Result[MyDoc, BackendError] ! {Process} =
  match runJson("python3", ["my_adapter.py", path]) {
    Err(e) => Err(e),
    Ok(j)  => Ok(decodeMyDoc(j))
  }
```

### Inline with logging

```ailang
match runJson("python3", [script, arg]) {
  Err(e) => println("[my-mod] ${formatError(e)}"),
  Ok(j)  => useResult(j)
}
```

## Effect rules

- Callers must declare `! {Process}` (or compose: `! {IO, Process}` etc.)
- `formatError` is `pure` — safe to call from anywhere, including inside a `pure` function
- The package's `[effects].max` is `["Process"]` — do not add more without justification

## Smoke test

`_smoke.ail` exercises all three `BackendError` variants offline using `false`, `echo not-json`, and `printf '{"ok":true}'`. Run via the registry validator or manually:

```bash
ailang run --caps Process,IO --entry main _smoke.ail
# expect: "OK: 9/9 checks passed"
```

## Modifying this package

- Keep `runJson` Process-only. If you add timeout/cache/stdin variants, they should also stay Process-only (compose with `std/stream` for IO).
- New error variants are a **breaking change** — bump major version.
- Add new functions as new exports; do not retrofit signatures.
- Update `_smoke.ail` for any new public function. Boot probe must still exit `OK:`.
