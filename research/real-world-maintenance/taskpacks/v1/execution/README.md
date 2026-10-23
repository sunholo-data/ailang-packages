# Frozen maintenance execution bindings

`manifest.schema.json` describes the controller-only `maintenance.execution/1`
envelope. The Go loader additionally checks duplicate JSON keys, source hashes,
regular-file/no-symlink paths, owned-file bounds, exact native tool identities,
matched language arms and the finite three-stage schedule. Controller references
are resolved relative to the execution document. No whole envelope is model input.

The checked-in `development.example.json` binds eight trajectories and 24 changes
to the existing public development taskpacks. It references `development.plan.json`
in the native `maintenance.trajectory/2` shape; it does not reuse the analytical
ledger fixture's synthetic source hashes. Its role is `instrument_control` and its
subject is `scripted-control`. It is neither an actual model result nor a claim
about average maintenance work or language superiority.

After building the adapter CLI:

```sh
ailang eval-suite --agent \
  --maintenance-manifest "$PWD/research/real-world-maintenance/taskpacks/v1/execution/development.example.json" \
  --dry-run
```

This reads and verifies local inputs only. It creates no executor, asks for no
credentials, takes no rig lock, discovers no standing eval tasks and calls no
model or inference canary. The output records the complete stage schedule,
identities, declared bounds and unavailable usage. `isolation.status` is a
**declaration**, not proof; live admission is closed until actual qualification
and a separately reviewed launch manifest. An ordinary suite flag such as
`--models`, `--tier`, `--trials` or `--queue=false` conflicts even at its default.
Only `--agent`, `--dry-run` and `--output` may accompany this mode.

Source starts at package revision
`a4163559a2e20dddc1a1bb0869a06e42372994a1` (merged foundation); these new execution
bindings and grader overlay are separately digest-bound. The native source
consumer is `packages/maintenance-bench/ledger_report.ail`. Registry 0.1 lacks
this source's ledger APIs and must not substitute for it.

The deterministic `write_development_manifest.py` freezes source files and
independently collected runtime evidence; it never invokes a model or a toolchain.
Its two `--*-evidence` files use `maintenance.toolchain/1`: explicit native
`command`, `versionCommand`, observed `version` and executable `binarySHA256`.
Dry run validates these metadata and their hashes without running the binaries;
the native grader verifies actual executable bytes and version before and after
grading. This attests the executable, not every mutable operating-system library.
It uses create-only outputs and refuses to replace prior documents. When changing
sources, freeze new documents in an isolated source checkout and review all
changed hashes; do not overwrite banked run evidence.

Starter identity is SHA256 of compact UTF-8 JSON (no trailing newline), sorted by
owned path: `[{"path":"main.py","sha256":"…","executable":false},…]`.
The mode bit is any executable bit. Source locks/public app files are included;
only these declared owned files plus HANDOVER.md carry between fresh sessions.
Missing/deleted files remain missing; a failed stage is never reset to reference
source. Oracle bindings include the shared grader, family driver, protocol and
all fixture inputs/expected values. Stage requirements remain separate and only
the current request enters its stage.

Grader argv uses explicit placeholders filled only by the trusted host bridge:
`{candidate}`, `{output}`, `{candidateDigest}`, `{commandPrefixJSON}` and
`{containmentDigest}`. The bridge resolves the driver from `oracle.files[0]`,
checks all bound source hashes, and verifies confinement qualification rather
than trusting a user-supplied digest. No placeholder or oracle path is passed to
the model. Development-only unconfined controls are labelled as such and cannot
qualify protected execution.

Before any model campaign, oracleDigest now binds SHA256 of compact JSON containing ALL ordered oracle-source/fixture file SHA256 values, not the wrapper alone. This identity is shared by native arms and is independent of checkout paths. Toolchain evidence uses maintenance.toolchain/1 with explicit native/version commands, full observed version and actual executable SHA256; loader validation is static, while native grading independently verifies version and binary before/after execution. These amendments occurred during no-model development and do not rescore frozen studies.

Direct protected candidate checks demonstrate declared filesystem/network denials. POSIX process-group cleanup does not establish reaping of descendants that detach sessions or escape cwd; full live admission remains closed pending an owned process boundary and nested-tool execution fix.
