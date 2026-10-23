# Arbitrary retained candidate grading

Each family's `grade_candidate.py` is a controller-only bridge. It grades the actual supplied native candidate; it never restores a reference or applies a model solution. A fresh runtime copy is compiled before public/independent checks. This host code is not a second language implementation and contains no metrics or provider parser.

```sh
python3 text-fidelity/grade_candidate.py \
  --candidate /absolute/retained/candidate --language python --stage 1 \
  --expected-source-digest CHECKPOINT_SHA256 --output /absolute/new-grade.json \
  --command-prefix-json '["/absolute/trusted-wrapper","policy-arguments"]' \
  --containment-qualified CONTROLLER_QUALIFICATION_SHA256
```

The trusted prefix receives `--` followed by complete executable argv. Its cwd is a fresh temporary `candidate/` directory. Only copied input JSON and newly created resource directories under that same temporary parent are passed to the candidate; host expected outputs, oracle source, controller paths and verdicts are never candidate arguments. The wrapper must enforce confinement for compilation and execution over this specific runtime root. Core admission must validate the frozen wrapper/policy and actual containment receipt. A caller-supplied digest alone is not qualification; reports always state `containment.qualified=false` and identify the external controller assertion separately. Missing confinement is invalid setup. `--development-unconfined` is an explicit, incompatible mode for no-model development controls only.

Source identity is SHA256 of compact UTF8 JSON, no trailing newline, sorted entries `[{"path":"relative/posix","sha256":"...","executable":false}]`. All copied regular files participate except `.git`, `.ailang`, `__pycache__` trees and Python bytecode. Any symlink/device is rejected, including in those trees. Mode is preserved in the fresh copy. Core checkpoints must use the same declared artifact set/serialization; the bridge checks that copying leaves identity unchanged. New builds run only against the copied native source, never a prior compiled artifact.

`maintenance.candidate-grade/1` has `status` passed, semantic_failure, artifact_failure or invalid_setup. Native source that does not compile, lacks its entry, crashes, times out or emits invalid JSON is an artifact failure. Missing trusted runtimes/fixtures, altered input/oracle source, changed checkpoint identity, skipped oracle assertions or weakened-oracle controls are invalid measurement setup. A syntax failure never satisfies a semantic mutation control. Process groups are reaped after bounded commands on POSIX. Every result binds source/runtime/protocol/oracle/fixture/output hashes. Output creation is exclusive and existing evidence is never replaced.

Resource grading runs both current-stage operation orders, which retain prior ownership/cap/lifetime obligations, plus the deliberately weak public single-document check. The independent assertion counts are 87/123/152 per order at stages 1/2/3. The resource oracle stops at its first semantic failure, so that row's completed assertion count remains null rather than invented; expected inventory stays explicit. Text grading uses the current frozen stage fixture, including retained cell/text/event obligations; it checks 8/15/21 exact typed rows. The existing always-pass/field-loss controls remain separate. All evidence is public development evidence, not a sealed holdout or population language-quality claim.

Run `make -C packages/maintenance-bench candidate-grading-test` from the repository root. Controls include both languages across all stages, a real semantic mutation, uncompileable/missing native source, missing runtime/fixture, source identity drift, native-source mutation, duplicate JSON keys, oracle weakening/skipped assertions/overwrite, timeout, prefix forwarding and create-only output. No model/provider is called. Actual OS containment qualification is an additional core gate, not a passing unit test here.
