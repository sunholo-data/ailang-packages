# Loop Lab application and audio package boundary

Status: proposed extraction plan, 2026-10-23. The user identifies Loop Lab as an
application and a main consumer of the package. Proposed application repository:
`sunholo-data/ailang-loop-lab`. No remote repository has been created and no source
has been removed from this repository by this plan.

## Ownership

| Owner | Responsibilities |
|---|---|
| `ailang-packages/packages/audio` | Generic source-independent clips, checked synthesis, processing, analysis, gain plans, limits and reports; pure public APIs |
| `std/audio` / numeric stdlib | Shared PCM/WAV/codec boundaries and reusable measured kernels; coordinated resampling when available |
| `std/ai` / provider packages | Speech/model inference, provider formats, credentials, network/AI effects and their budgets |
| Standalone Loop Lab application | UI/branding, capture/privacy, device lifecycle, clock/planner session, workers/worklets, four-track behavior, undo, persistence, WAV/MIDI handoff, future instrument/plugin integration |
| Other consumers | Game assets, headless media tools, speech/model-output pipelines and batch generation; no Loop Lab concepts required |

Four tracks, 120 BPM, eight-second loops, capture permissions and session history
must not enter `sunholo/audio`'s generic types or release requirements. The package
should be usable without a browser, audio device, DAW, model account or Loop Lab.
Model-generated samples use the same checked Clip boundary as procedural or recorded
samples. Models that return recipes use checked recipe parsing/rendering.

The existing browser level adapter stays application integration initially and is
tested against the versioned AILANG API. Its JavaScript does not inherit package
proofs. If a second browser consumer needs it, consider a separately versioned host
adapter; do not turn the AILANG library into a four-part Web Audio application.

## Audit of extraction dependencies

- `examples/live-loop/ailang.toml` uses a local path dependency on `../../packages/audio`.
  That is correct for current co-development. A released standalone consumer must
  pin the published audio version, initially `0.3.0` after that release exists.
- The parity test previously climbed three directories to a producer checkout and
  loaded its design-doc fixture. The fixture now belongs to the application under
  `test/fixtures/adapter_probe.ail`; tests use the application's declared dependency
  and `--package-dir`, so they can run outside this monorepo.
- Planner/server/kernel tests otherwise resolve their own application root.
  Python uses a fixed AILANG entry and no shell invocation. Node/Python need no
  third-party package install for the current test suite.
- README and evidence links still refer to shared monorepo design documents.
  Application-owned design docs should move to its `docs/`; historical package
  evidence should use pinned links back to this repository. This remains part of
  the actual extraction, not a claim that every current link is standalone-ready.
- Generated demo WAVs, runtime binaries and `.ailang` caches are not source assets.
  Carry their ignore rules and generation/install instructions, not a developer's
  generated files. Preserve brand provenance, font OFL, repository license and notices.
- The private preview is an application service with a running process/root path.
  Repoint it only after the standalone copy is healthy; preserve other Serve routes.

## Migration order and concrete acceptance

1. Finish generic audio 0.3 scope, validate and release the package through its own
   PR/registry workflow. The application's work does not itself publish that package.
2. Create the application repository after its name/visibility are decided. Preserve
   the application directory's history and original commit/evidence provenance;
   carry relevant application design docs in a separate documented move.
3. Put the application at its own root. Pin the released `sunholo/audio` version in
   its default manifest/lock. Document an explicit opt-in path dependency for local
   co-development; never require a producer checkout in normal consumer tests.
4. Add application-owned AGENTS/skill instructions, license, ignores and CI. Run
   native checks, 45 host tests, 6 HTTP/planner checks, quality and static/link checks
   from a clean clone using only the released dependency. Test registry installation
   with no access to the old producer tree. Optional runtime assets remain optional.
5. Recheck browser controls/downloads and update the existing private preview to
   the application's new root. Keep software tests, user runs and physical device
   evidence separately scoped.
6. Replace the old full application directory with a short migration pointer only
   after standalone CI/reference checks pass. Avoid maintaining two source copies.
   Keep a small selection of generic headless package examples in this repository.

The current isolated extraction check can establish path-independent compilation
and behavior using an explicitly supplied local library. It cannot establish that
unpublished audio 0.3 is installable from the registry or that a remote application
repository exists. Those are separate migration gates.

## Release responsibilities after the split

The package release validates generic behavior, compatibility and supported formats.
Loop Lab pins versions and runs consumer compatibility checks; its releases cover
UI, capture, session/recovery and musical workflows. Save/load and Live integration
can ship on the application's schedule without forcing a DSP package release.

For the package's next scope, see [generic audio 0.3](audio-0.3-generic-scope.md).
