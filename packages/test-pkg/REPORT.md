# test-pkg feedback report — feature: `shout` + `greetAll` (v0.1.4)

## Incoming feedback
User feature request (via `mcp.ailang.sunholo.com/submit_feedback`), explicitly
authorized for implementation with a version bump:

- Add `shout(name: string) -> string` = `toUpper(greet(name, "!"))` (std/string `toUpper`).
- Add `greetAll(names: [string]) -> string` = `join(" ", map(\n. greet(n, "."), names))`
  (std/list `map` + std/string `join`).
- Keep `greet` unchanged.
- Bump `ailang.toml` version to `0.1.4`; touch nothing else in that file
  (in particular `[effects].max` stays `[]`).

## Changes made
- `packages/test-pkg/hello.ail`
  - Added imports: `std/string (toUpper, join)`, `std/list (map)`.
  - Added exported `shout` and `greetAll` exactly as specified; `greet` untouched.
- `packages/test-pkg/ailang.toml`
  - `version = "0.1.3"` → `"0.1.4"`. No other field modified; `[effects].max` unchanged.

## Verification (evidence, per source)

### Type check
`ailang check` (tool: `ailang_check`) on a probe program that imports the real
package module via a path dependency:
`/workspace/task-a0a96c0e/scratch/probe.ail` → **ok: true** (only a benign
"dependency content changed vs lock" warning from the hand-written scratch lock).

Note: running `ailang check` directly on `packages/test-pkg/hello.ail` fails with
`MOD010: module 'sunholo/test_pkg/hello' doesn't match file path 'hello'`. This is
pre-existing standalone-check behavior (the module path is the published package
path, the file is checked without package context); it reproduces identically on
the untouched v0.1.3 file, so it is not caused by this change.

### Runtime proof
`ailang run` (tool: `ailang_run`) on the probe, admitted with caps {FS, IO, Process},
declared effect row `{IO}`:

```
shout("world")        → HELLO, WORLD!
greetAll(["alice","bob"]) → Hello, alice. Hello, bob.
```

Both outputs match the spec: upper-cased `greet(name, "!")`, and greet-with-"."
per name joined by single spaces. `greet` is exercised unchanged inside both
results. Probe programs live outside `packages/test-pkg`
(`/workspace/task-a0a96c0e/scratch/`), so the package's `[effects].max = []`
ceiling was never widened or bypassed — the scratch probe root declares its own
`max = ["IO"]`.

### Not done / limitations
- `ailang lock`, `ailang test --package .`, `ailang pkg quality --strict`, and
  `ailang publish --dry-run` were **not run**: this lane has no shell, and those
  are CLI subcommands. The scratch `ailang.lock` was hand-written (path source,
  placeholder hashes) purely to make the probe resolve; it is local-only and
  not part of the package.
- No GitHub issue was opened: the message instructed direct implementation
  rather than triage-only handling, and this lane has no network access.
- No reply was sent via `ailang messages send` (no shell in this lane); the
  coordinator should relay the outcome to `mcp-public`.
- `ailang publish` was **not** run — publishing is out of scope for this lane;
  v0.1.4 is committed but unreleased.

## Tools used
- `read` — inspect `hello.ail`, `ailang.toml`, `AGENT.md`, consumer lock schema.
- `edit` — implement the two functions and the version bump.
- `write` — probe program + scratch package root (`ailang.toml`, `ailang.lock`)
  outside the package; this report.
- `ailang_check` — type-check the probe (3 failed resolution attempts before the
  path-dependency route worked; final result ok).
- `ailang_run` — execute the probe and capture the proof output.
- `examples_search` / `builtins_search` — attempted; no examples dir was found
  from the package directory (tool reported an error), so stdlib signatures were
  taken from the in-repo teaching prompt.

## What AILANG / the tooling made hard
1. **No shell** — every standard CLI step (`ailang lock`, `ailang check --package .`,
   `ailang test --package .`, `ailang pkg quality --strict`, git) was unavailable.
2. **Standalone check of package modules fails** (`MOD010`) — a package module
   whose declared path differs from its filename cannot be `ailang check`ed
   without package context; the only workaround was a full import probe.
3. **Importing the package locally requires lock machinery** — `pkg/` imports
   refuse to resolve without `ailang.lock` ("run 'ailang lock'"), and `ailang lock`
   is not runnable in this lane. Hand-writing the lock (schema copied from
   `test-pkg-consumer`) worked, with a permanent content-hash warning.
4. **Path-dep TOML syntax is undocumented in-repo** — `{ path = "..." }` was a
   guess that happened to be accepted; the FS sandbox also prevented listing the
   repo to find prior art beyond the consumer package.
5. **Hyphenated package dirs are unimportable by module path** — `test-pkg` can
   never appear in an import (`PAR_HYPHEN_IN_IMPORT`-class parse error), so
   relative-dir imports were not an option; only the manifest-driven path dep worked.
