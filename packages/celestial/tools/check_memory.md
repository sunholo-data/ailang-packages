# Celestial check memory, 2026-11-02

`stellar_ld.ldRows()` now concatenates eight private constant batches (at most
64 rows) instead of one 508-row record literal. All 508 records, their order,
`LdRow`, and the public `ldRows` signature are unchanged. No physics formula,
coefficient, table coverage, interpolation, clamp or result changed.

AILANG v0.56.0, commit `e1ef997298bd96f27a3cf28e7997e766b73270be`,
Darwin arm64. Teaching prompt loaded: v0.16.11. Parent package baseline:
`00f0c7f` (celestial 0.6.0 before this change).

## Cold package measurements

Each row is a fresh directory containing only the package's `*.ail` and
`ailang.toml`; no `.ailang` compilation cache was copied. The before directory
uses `git show 00f0c7f:packages/celestial/stellar_ld.ail` for its table.
`/usr/bin/time -l "$AILANG" check --package "$scratch_dir"` checked all 22 files.
These are process RSS values, not Go heap sizes or the remote validator's peak.

| Pair | Before maximum RSS (bytes) | After maximum RSS (bytes) | Before elapsed | After elapsed |
|---|---:|---:|---:|---:|
| 1 | 295550976 | 100417536 | 2.85 s | 2.05 s |
| 2 | 302366720 | 105840640 | 2.98 s | 2.09 s |

RSS dropped by 65–66%. The first in-place cold baseline check was higher
(496877568 bytes, 2.74 s); compiler allocation/GC timing varies. A warm check
is not evidence for a cold validator budget. No remote validation or
publication was performed, and the registry still listed 0.5.0 when checked.

## Behavior and API evidence

- `ailang check --package .`: **22 files checked, all passed**.
- `ailang test --package packages/celestial`: **156 tests: 156 passed,
  0 failed, 0 skipped** (37.28 s).
- `ailang test --strict-bytecode stellar_test.ail`: **16 tests: 16 passed,
  0 failed, 0 skipped**; 16 named-test bodies on VM, zero fallbacks.
- `_smoke.main` with `--strict-bytecode --verify-contracts --caps IO` passed.
- `ailang iface` for `stellar_ld` before and after is identical after removing
  only the CLI's path-derived `module` field. The exported type, function,
  effects and IFC signature are unchanged.
- A temporary consumer emitted complete JSON for all 508 rows plus 1400
  interpolation/clamp samples. Before/interpreter, before/strict VM,
  after/interpreter and after/strict VM were byte-identical. SHA256:
  `42a7ab2996026697201ee74f1351e70132e3eb6649fbad23a5cd8a2898502858`.
  Every row was serialized explicitly; no truncated `show` comparison was used.

The temporary probe used a path dependency on the package and this body:

```ailang
module test/celestial_memory/probe
import pkg/sunholo/celestial/stellar_ld (ldRows)
import pkg/sunholo/celestial/stellar (ldCoeffs)
import std/json (encode, ja, jnum)
import std/list (map, range)
import std/math (intToFloat)
export func main() -> () ! {IO} {
 let rows = map(\r. ja([jnum(r.logg),jnum(r.teff),jnum(r.a),jnum(r.b),jnum(intToFloat(r.model))]),ldRows());
 let probes = map(\i. {
  let p=ldCoeffs(1800.0+intToFloat(i)*37.0,-0.5+intToFloat(i%67)*0.1);
  ja([jnum(p.a),jnum(p.b),jnum(intToFloat(p.source)),jnum(p.teffUsed),jnum(p.loggUsed)])
 },range(0,1400));
 println(encode(ja(rows ++ probes)))
}
```

The existing human-readable source table format is preserved. The v0.56.0
formatter also reports drift for the original table and collapses each batch
onto one long line; no unrelated table reformat was applied.

Full final-head package quality is coordinated by the parent execution session,
which may add separate W2.1 APIs. This note records only the memory change's
scope and its tested checkpoint; it does not attest those later edits.
