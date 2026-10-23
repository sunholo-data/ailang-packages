# Audio 0.3.0 release record

Published 2026-10-23 with AILANG v0.54.18, after [PR 163](https://github.com/sunholo-data/ailang-packages/pull/163)
merged as `ed9a627b792cf6564b0668a680242c196d3be34e`.
[GitHub source release](https://github.com/sunholo-data/ailang-packages/releases/tag/audio-v0.3.0).
Published package sources are immutable at that commit; this record is subsequent bookkeeping.

The publisher reported a successful upload. `ailang pkg info sunholo/audio`,
`ailang pkg versions sunholo/audio` and the public registry index independently
confirmed latest `0.3.0`. Loop Lab's portable registry lock resolves the same content
identity; its fresh clone passes verification and original fixture generation.
[receipt.json](receipt.json) is a manually curated record of observed results.

## Published identity

- Content: `sha256:a39b7372488e4fe9881f065efcd1a97594d6d6f1b2f36f98e569c0cd0f1f6874`
- Interface v1: `sha256:b50e418677dbe148cd0fbd567298f3311d914654981454529cc5cafc35eba691`
- Interface v2: `sha256:ifacev2:e323556e6a947daaa5af0d4dfd9474b06bc84a041ba381803affb10d587cc730`
- Tarball: `sha256:80205df6c66d9e59e1fa25606350dc57e6ef517ea4120361a6ccfa5487063a17`, 57,362 bytes

## Quality sections from the actual publisher

| Section | Result |
|---|---|
| Compile | 27 files pass |
| Contracts | 14/62 verified, 48 skipped (5 missing postconditions, 43 unsupported encodings), 0 refuted/errors; 33 uncontracted exports |
| Interface | 141 signatures; v2 identity above |
| Effects | Declared max [IO], rank IO; processing exports pure, IO in smoke |
| Release | Feature, nonempty 0.3.0 changelog section |
| Docs | AGENT.md and ai_summary present; implementation quality report covers 7 exports |
| Style | 93/93 pure exported functions |
| Tests | 164/164 pass across 12 files, 0 skipped; executed locally, attested to registry |
| Smoke | Present, executed locally and passed; attested to registry |
| Gates / badges | No gates. PUB016 records unproved contracts; PUB011 warns about 33 uncontracted exports |

The registry validator repeats structural/proof checks; it does not execute attested
tests/smoke. Mathematical Real/Int proofs do not establish IEEE-754 equivalence,
device timing or perceptual quality. The unchanged inline DSP suite separately
reports 11 passing checks and 1 precondition-generator skip, outside the 164/164 count.
See [implementation evidence](../audio-blocks-0.3.0/README.md) for runtime-contract,
strict-bytecode, property and headless fixture evidence.

Loop Lab is a separate [application consumer](https://github.com/sunholo-data/ailang-loop-lab)
with an exact registry dependency on audio 0.3.0 and an independent GitHub source
release. Its repository remains private; it is never uploaded as an AILANG registry
package. These checks do not imply a new physical audio or browser-soak result.
