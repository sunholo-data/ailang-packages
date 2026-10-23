# Local source consumer

This never-published example imports native 0.2 source by an explicit relative path. Registry 0.1 has no v2 ledger and is never a fallback. Run `ailang lock`, then `ailang lock --check` and `sh check.sh`. The movable relative lock records actual package source/interface hashes. Core separately attests checkout/module/lock/binary identities; the compiler argument remains declared.

`main` reads three explicit inputs and writes new output via snapshot_io. Effects: IO/FS/Env only; no AI/Net/Process. Pure contracts and native tests remain in ledger_report/run_validate/run_compare owners. Wrapper contracts/properties skip: no new analytical rule. `check.sh` executes real native analysis with independent control expectations and refuses overwrite. File bytes/workload limits belong to caller runtime admission; no fabricated step/token budget.
