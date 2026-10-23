# Native text-fidelity development asset

This package is a reference for the public bounded cell-text task. No model/network calls. Read ../../stages/contract.md for the frozen interface and expected stage semantics. Transport needs IO/FS/Env; text processing is pure. Run ailang lock --check, ailang check --package ., ailang test --package . and the taskpack external qualifier. A passing type check does not establish logical-text correctness. Contracts have their own reported solver coverage.

Exports: `benchmark/text_fidelity/text` owns pure processing; `benchmark/text_fidelity/main` owns CLI transport. Starter render preserves baseline logical text; reference render selects qualified stages and explicit deliberate mutants. `examples/qualify_f2.ail` is orchestration over tested owner functions; it has an explicit IO row, with contracts/native tests in the owner.
