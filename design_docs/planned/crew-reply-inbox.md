# Crew replies in the background: keep playing while AI words arrive

| Game pillar | Alignment | Constraint |
|---|---:|---|
| Choices Are Final | +2 | A crew member's decision commits at once from the authored policy. Words that arrive later can never change it, its seed or its resources. |
| The Game Doesn't Judge | 0 | No score is added. |
| Time Has Emotional Weight | +1 | The watch no longer freezes on network latency; time moves only when the captain advances. |
| The Ship Is Home | +2 | Several crew can be preparing personal replies at once while the captain reads Crew, Work or offers more work. |
| Grounded Strangeness | 0 | No content change. |
| We Are Not Built For This | +1 | Faster live play makes it practical to tune strain and refusal against real wording. |

**Status:** Planned 2026-10-12. Mark asked for this sprint ("do the next sprint for
background") after S-CREW-CORE-SPLIT merged (ailang-packages #130).
**Supersedes:** the 2026-10-10 plan S-CREW-REPLY-INBOX (mailboxes, gossip relay, five
days), whose M1 gate failed because AILANG v0.52.0 could not stop worker processes.
**Target:** crew-lab 0.6.0 (local only, never published). crew_core unchanged.

## What was wrong

`crew-watch` calls the model synchronously inside the key loop: a cache miss freezes the
screen on "HEARING YOUR CREW" until the provider answers. The crew member's *decision* never
needed to wait: the reaction label, the response roll, the text roll and the next seed all
come from the authored policy and the seed; the model only writes the words.

## What AILANG v0.54.5 gives us (measured 2026-10-12, scratch probe)

- `std/process.spawnProcess` + `cancelProcess`: a spawned `ailang run` worker writes its
  result file while the host keeps polling (seen after 1.6 s for a 1.5 s worker); its stdout
  does not reach the host terminal; `cancelProcess` on a running worker stops it and no
  process is left; on an already exited one it returns `WorkerHandleInvalid` (already reaped).
- `std/terminal.readEvent(session, timeoutMs)`: a native key read with a timeout; Idle maps to
  terminal_ui `NoInput`, which the watch loop already ignores.

So the host stays a single AILANG loop: wait up to 100 ms for a key, then check workers.
No `selectEvents`, mailboxes or extra languages.

## Design

1. **Decision now, words later.** In live mode `respond` picks the reaction exactly as today.
   If saved wording exists (full or short cache) it is used as today. On a miss it commits the
   decision immediately with the authored line (identical command, roll and seed to the
   synchronous path) and records a *reply job* `{request, actor, label, signature, textRoll}`.
2. **Worker.** New bin `crew-reply-worker HOME JOBFILE` (module `reply_worker`, caps `FS,AI`).
   It reads a `crew_reply_job/1` file, calls the existing `store.resolve` (cache lock, atomic
   write, narrative and bounds checks, one call at most) and writes a `crew_reply_result/1`
   file atomically. It never touches the journal or the session.
3. **Inbox (pure, `reply_jobs`).** Queued, Preparing, Ready, Failed, Cancelled; concurrency 3
   (1..5), at most 16 live jobs, one live job per signature. Completion of an unknown,
   finished or cancelled job is ignored, so late or duplicate results cannot apply twice.
   Wording is chosen with the text roll reserved at decision time, so arrival order cannot
   change which variant is shown.
4. **Host adapter (`reply_runner`, `! {FS, Process}`).** Writes the job file under the run
   folder, spawns the worker, polls the result file, reaps the handle; quit cancels every
   running worker. The journal gets a `wording` record (job, request, source, calls, tokens,
   text or error): transport only, never replayed as a domain command.
5. **Allowance.** A dispatch reserves one of the run's AI attempts; a result with zero calls
   (another writer filled the cache) refunds it. Out of attempts: the authored line stands and
   the job is recorded as not sent.
6. **Prefetch.** The session is pure, so the host can compute exactly what each idle crew
   member would be asked if offered their work now (same request, label and signature) and
   queue that wording at low priority while the captain reads. If the captain makes that offer,
   the reply is already cached and shows at once. Bounded: only while attempts remain above a
   reserve, at most one prefetch per crew member per state, never more than the concurrency.
7. **UI.** A status line "Replies: 2 preparing / 1 new (r)"; `r` opens a Replies reading view
   (newest first: who, about what, preparing or the words). Arrival redraws only that line and
   never changes the current view, cursor, page, numbering or a half-typed editor line. In
   line/plain modes arrivals appear at the next completed input.

Offline mode (`crew-watch-offline`) is unchanged: it never calls a provider.

## Out of scope

Peer gossip and relays, observer reactions to public notices, a separate async package, and
Godot integration. Each needs its own design.

## Acceptance (commands)

- `make -f examples/crew-lab/Makefile reply-test`: `reply_jobs` inline and named tests on
  interpreter and strict VM (bounds, duplicates, late and cancelled results, reserved-roll
  wording, allowance refund).
- `make -f examples/crew-lab/Makefile async-test`: installs the bins, puts a slow fixture
  worker first on PATH (no provider), drives the live watch in line mode:
  offer → the decision shows at once while the worker sleeps → read Crew → offer another →
  the words appear and the journal has `wording` records; the domain records (host input,
  output, seeds) equal a run with the fixture's wording already cached; quit leaves no worker
  processes.
- `make -f examples/crew-lab/Makefile prefetch-test`: after a prefetch completes, offering that
  crew member shows the generated words immediately with zero new dispatches.
- Existing `make -f examples/crew-lab/Makefile validate` stays green; CI on the PR.
