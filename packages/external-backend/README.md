# sunholo/external_backend

Run external subprocess backends (Python, Rust, Go, shell, …) that emit JSON on stdout, with typed errors and stderr capture.

Useful any time AILANG needs to delegate to a non-AILANG helper and get structured data back:

- PDF parsers (Docling, LiteParse, Marker, MinerU, …)
- OCR engines (Tesseract, PaddleOCR, …)
- Embedders / classifiers running in Python or Rust
- Layout / table extraction models
- Anything wrapped in a `--json` CLI flag

## Why it exists

`std/process.exec` returns raw bytes; `std/json.decode` returns a generic decode error. Stitching them together (check exit code → toString stdout → decode → preserve stderr) is mechanical but easy to get subtly wrong. This package gives you one call with a discriminated error type.

It also **confines the `Process` effect** to one module. Your higher-level wrapper picks up `! {Process}` once at the boundary and exposes a domain-typed API to the rest of your codebase.

## Install

```bash
ailang add --git https://github.com/sunholo-data/ailang-packages \
  --subdir packages/external-backend --tag main
ailang lock
```

## Usage

```ailang
import sunholo/external_backend/runner (runJson, formatError, BackendError)
import std/io (println)
import std/result (Ok, Err)
import std/json (getString)

export func parseWithMyBackend(filepath: string) -> () ! {IO, Process} =
  match runJson("python3", ["adapter.py", filepath]) {
    Err(e) => println("backend failed: ${formatError(e)}"),
    Ok(doc) =>
      match getString(doc, "result") {
        Some(s) => println("got: ${s}"),
        None    => println("missing 'result' key")
      }
  }
```

## API

### `BackendError`

```ailang
type BackendError = ExecFailed(string)
                  | NonZeroExit({code: int, stderr: string})
                  | InvalidJson({stderr: string, msg: string})
```

- `ExecFailed(msg)` — the subprocess did not produce output: not found, not permitted, timed out, killed, or over the output limit. Since 0.2.0 `msg` says which (see `describeProcessError`)
- `NonZeroExit{code, stderr}` — process ran but reported failure; stderr is captured for inclusion in diagnostics
- `InvalidJson{stderr, msg}` — process exited 0 but stdout did not parse as JSON; both the decoder message and stderr are surfaced so callers can distinguish "produced rubbish" from "produced warnings then valid output"

### `runJson(cmd, args) -> Result[Json, BackendError] ! {Process}`

Execute a subprocess and decode its stdout as JSON. The single effect is `Process`.

### `formatError(err) -> string` (pure)

Render an error as a human-readable string. Contract: `ensures { strLength(result) > 0 }`.

### `describeProcessError(cmd, err) -> string` (pure)

Render a `std/process.ProcessError` with the detail its variant carries — the
timeout duration, the output-byte limit, the kill signal, the PATH miss — and
the flag that fixes it (`--process-timeout`, `--process-max-output`).

`runJson` applies this to every `exec` failure, so `ExecFailed` messages are
specific by default. It is exported because callers that run `exec` directly
want the same treatment.

Before 0.2.0 all seven variants rendered as `"could not execute '<cmd>'"`. That
is the missing-binary message, so a timeout sent readers to check a PATH that
was never wrong. Downstream, docparse's docling backend was being killed at the
30s default on every non-trivial PDF and reporting `uv` as unavailable.

## Adapter contract

Your subprocess should:

- Print **exactly one JSON value** on stdout (object, array, string, number, bool, or null)
- Use stderr for progress, warnings, logs, or error messages
- Exit `0` on success, non-zero on failure

That's it. No envelope, no length prefix, no protocol. If your tool already emits JSON via a `--json` flag, you're done.

## Effect hygiene

Because `runJson` requires only `! {Process}`, you can build a domain wrapper that has a much tighter signature than calling `exec` directly:

```ailang
-- Pure decoder: no IO, no Process.
pure func decodeMyResult(j: Json) -> MyResult = …

-- Effectful entry: only Process (and optionally IO for logging).
func extractWith(filepath: string) -> Result[MyResult, BackendError] ! {Process} =
  match runJson("python3", ["adapter.py", filepath]) {
    Err(e) => Err(e),
    Ok(j)  => Ok(decodeMyResult(j))
  }
```

Callers who want to log errors compose with their own `IO`; callers who want to bubble up keep the signature `Process`-only.

## Roadmap

Additive extensions (no breaking changes planned):

- `runJsonWithTimeout(cmd, args, ms)` — fail fast on hangs
- `runNdJson(cmd, args)` — stream line-delimited JSON via `std/stream`
- `runWithStdin(cmd, args, bytes)` — pipe input to subprocess
- `pingHealth(cmd, args)` — cheap probe for long-lived backends
- `runCached(cmd, args, cacheDir)` — hash inputs, skip re-exec on hit

## Real-world use

Extracted from [sunholo/ailang-parse](https://github.com/sunholo-data/ailang-parse), which uses it to dispatch PDF parsing across multiple backends (Docling, LiteParse, …) selected at runtime via a `--pdf-backend` flag.
