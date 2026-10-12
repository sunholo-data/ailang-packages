# S-CREW-REPLY-INBOX-2: background replies and prefetch

Design: [crew-reply-inbox](crew-reply-inbox.md). Authorised by Mark 2026-10-12 ("do the
next sprint for background"). Runtime AILANG v0.54.5 (CI pins v0.54.4; the APIs used,
`spawnProcess`, `cancelProcess`, `readEvent` with a timeout, exist in both).
AILANG prompt version loaded: v0.16.7. Estimate about 1,100 changed lines, 1–2 days.

## M1: pure reply inbox (`reply_jobs.ail`, ~300 lines)
- [x] Types Spec/Status/Job/Inbox; enqueue, dispatchable, preparing, complete, cancelAll,
      markRead, counts, status line, view lines, wording(bundle, label, roll).
- [x] Contracts: bounded live jobs (≤16), one live job per signature, complete changes only
      a Preparing job; tests for duplicates, late, cancelled and out-of-order results.
- [x] `make reply-test` passes on interpreter and strict VM.

## M2: worker and live host (~500 lines)
- [x] `reply_worker.ail` + bin `crew-reply-worker`; job/result codecs with bounds.
- [x] `play.respond` defers on a live cache miss: same command, roll, seed as the
      synchronous path; `Run.deferred` carries the job; allowance reserved and refunded.
- [x] `reply_runner.ail`: write job, spawn, poll, reap, cancel all; journal `wording` record.
- [x] native_watch: 100 ms key polling while jobs run; status line; `r` Replies view;
      arrivals never move the view, cursor, page or editor text.
- [x] `make async-test` (fixture worker, no provider) passes; quit leaves no workers.

## M3: prefetch (~200 lines)
- [x] Pure prediction of each idle crew member's offer request/signature from the session.
- [x] Bounded queueing (allowance reserve, one per member per state, below concurrency).
- [x] Prefetch checked inside `make async-test` (scenarios 6–7) rather than a separate
      target: a prefetched offer shows generated words with zero new jobs; an early offer adopts it.

## M4: landing (~100 lines)
- [ ] README/AGENT/CHANGELOG 0.6.0, Makefile `validate` includes the new targets, CI green.
- [ ] Independent evaluation (different agent), merge, reinstall bins.

## Outcome (2026-10-12)

M1–M3 done in one day, about 1,000 changed lines. `make reply-test` (5 + 1 tests, both
engines) and `make async-test` (nine installed scenarios, provider-free, about 30 s)
pass; existing suites pass after two intended test changes: the presenter's status
shares the Choices row (no layout change), and `test-short-reply.sh`'s installed section
now checks the background path (live domain records equal the offline baseline).
Found and reported: `spawnProcess` aborts the run on an unknown command (ailang#1784);
the watch checks PATH first.
