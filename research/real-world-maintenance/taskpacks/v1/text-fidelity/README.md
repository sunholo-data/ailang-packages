# Text fidelity: public real-requirement maintenance taskpack

This is a **development component adaptation** of the logical-text obligation
exposed by Calamine [#671](https://github.com/tafia/calamine/pull/671) and
[#673](https://github.com/tafia/calamine/pull/673). The exact historical Rust probe
is retained in the merged [mature study](../../../mature-2026-10-23/README.md).
These new AILANG/Python programs are authored counterparts, not historical Python
repairs, a whole XLSX/XML port, a secret holdout, or evidence of a language win.

Both native arms consume already-decoded logical text. The shared supplied JSON
producer fixes the upstream boundary; both arms own concatenation, ASCII edge
policy, event validation, error distinctions and consumer records. In S2 a
reference event carries a decoded character, including a literal space. No arm
calls the other or reads expected outputs. XML byte parsing remains upstream;
this task cannot support a claim about either language's XML parser quality.

Read the frozen [contract](stages/contract.md) and exact [S1](stages/s1.md),
[S2](stages/s2.md), [S3](stages/s3.md) requests. Fixture expected text was specified
independently before implementations; retained fixtures mechanically carry those
same obligations forward. `starter/` contains only competent baseline behavior.
`reference/` contains all development checkpoints and deliberate mutants, and
must never be seeded into an agent's starter workspace. Public checks are native
unit tests; the host oracle compares actual native outputs to shared independent
fixtures, outside the target program's tree.

Run from this directory, using Python 3 and AILANG v0.54.18 (prompt v0.16.7):

```sh
./qualify.sh --output /tmp/new-text-qualification.json
python3 -m unittest oracle_test.py
(cd starter/ailang && ailang check --package . && ailang test --package .)
(cd reference/ailang && ailang check --package . && ailang test --package .)
(cd starter/python && python3 -m unittest test_text.py)
(cd reference/python && python3 -m unittest test_text.py)
```

The qualification command uses a fresh copied source/build directory per
language/variant, verifies lock/compilation before each AILANG run, and records
input/expected/source/protocol/oracle/runtime digests. Each subprocess has a
30-second cap. Infrastructure errors, malformed output and timeouts fail the
campaign; they never satisfy an intended semantic negative control. Output paths
are create-only. Timing is descriptive, excluded from source identity, and is
not model generation/maintenance telemetry. No network or model calls are made by
the qualifier. The standalone `pkg quality` command separately attempts a registry
export-overlap lookup; its unavailable result is disclosed in validation.

Frozen control matrix:

| Role | Expected outcome |
|---|---|
| Native baseline + each S1/S2/S3 reference | 98 shared semantic assertions pass across both arms |
| No-op previous checkpoint at S1/S2/S3 | Exact named old/new obligations fail after successful compilation/run |
| Remove internal spaces; trim each chunk; drop CDATA; omit cell field | Exact expected mismatch identities, 144 deliberate assertion failures across arms including no-ops |
| Weaken oracle into unconditional acceptance | Independent canary rejects the weakened oracle |

The fixture-count and mismatch sets in `qualify.py` are an independent
expectation ledger, not a first-run golden. S2 rechecks all S1 cases and S3
rechecks all S2 cases. `oracle_test.py` verifies dropped output fields/rows and
known character loss cannot be accepted. An output equality check here is an
oracle for the frozen bounded contract, not proof of arbitrary source correctness.

Actual [validation](validation/README.md) separates native tests, oracle controls,
SMT proofs, runtime contracts and unavailable registry checks. Later executor
integration must prove worker/oracle isolation, retain the agent's own failures,
and charge all usage. Exposed cases are regression/development assets; subsequent
confirmation needs new frozen real requirements. No model campaign is included.
