# Sprint S-SOCIAL-DYNAMICS-0.4.1: linear wire framing (skip speed, option a)

**Why:** with crew_core 0.4.1, a healthy crew's auto-run skip costs about 4 s per
crew-year at cadence 30. The game's budget (AC11) is 10 years in 2 s. Profile
(crew-sim, 4-year skip, v0.54.8 strict VM): 191 GB allocated, 98% in the VM's
`_list_tail`. The hot site is `social_dynamics/wire.oneObjectTail`, which frames every
host command character by character with a cons pattern. Each step copies the
rest of the list (ailang#1827, follow-up #1830), so framing is quadratic in the
line's length, and the auto-captain's answer commands are a few KB long.

**Authorization:** Mark, attended 2026-10-15: "great yes lets go with your
recommendations" (option a now; option c as a design question).
**AILANG prompt version loaded:** v0.16.7 (runtime v0.54.8).
**Registry reuse:** none (fix inside social_dynamics).

| ID | What | Gate |
|---|---|---|
| ✅ A1 | `wire.framed`: one left fold over the characters, replacing `oneObjectTail`; `singleObject` uses it | `framing_test.ail`: the 0.4.0 framer kept as the oracle agrees on 25 cases (escapes, quoted brackets, mismatched closers, trailing data); a 32 KB object frames; a seeded mutation (escape ignored) fails all 3 tests |
| ✅ A2 | social_dynamics 0.4.1: changelog, `kind = "fix"`, contract on `framed` | 170 tests on both engines; `pkg quality --strict` shows no gates |
| ✅ A3 | Measured through the crew lab (path pins, not committed) | crew-sim 4-year skip, cadence 30, orders, ask_advice: 16.1 s → 7.5 s, 191 GB → 4.2 GB allocated, output byte-identical (md5) at 1 and 4 years |
| A4 | Publish 0.4.1; crew_core 0.4.2 and the crew lab pin it; integration agent re-pins | after merge |

**Not in scope:**
- **Option b**, a typed in-process path for the auto-captain.
- **Option c**, a coarser cadence for long skips. This is a design question for Mark.
- **content_library `frameTail`**, which has the same pattern. Only the lab uses it, on short lines.
