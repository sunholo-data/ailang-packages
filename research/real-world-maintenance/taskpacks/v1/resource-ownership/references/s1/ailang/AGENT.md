# Resource ownership native task fixture

Run `ailang check --package .`, `ailang test --package .`, then execute `main.ail` with input JSON and an existing empty resource directory as arguments, under IO/FS/Env. Pure withinCap has a meaningful contract; effectful orchestration relies on independent host-oracle byte/lifetime tests and does not claim SMT verification. No Net/AI/Process capability is required. This is an unpublished development fixture, not registry-library API or measured model performance.

Public fixture modules: `study/resource_ownership/engine` exports the resource record, pure withinCap and effectful run; `study/resource_ownership/main` is the CLI wrapper. `examples/qualify_f1.ail` delegates to run and contains no new pure logic; its contracts/inline tests are intentionally skipped in favor of the owner-module tests and independent oracle.
