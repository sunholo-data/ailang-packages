# Changelog

## 0.2.0

Scheduled tag QA. A spec can now carry a `site` block (base URL, consent buttons) and a `visits`
list: the page, consent state, steps, and the events each visit expects or forbids. `visits`
writes the run list for a browser script; `compare` reads what that script observed (dataLayer
pushes, GA4 hits on any host) and writes a QA round by an automated tester: `fail` with the
reason, `blocked` when the visit could not run, and `not tested` with a note when everything
matched, because only a person sets a pass. Events may name a `datalayer_event` that differs from
the GA4 `eventName`, or `none`. A new check key, `visits`, requires every high-priority event to be
covered. Two new proved rules: `worstOutcome` and `visitOutcome`. Tests: `qa_test.ail` (14).

## 0.1.0

First release. A tagging-specification standard kept as YAML drives three things: `check` (a
spec folder against the standard, with owner-approved deviations), `guide` (the readable
standard as Markdown) and `view` (an .xlsx with Spec, Matrix, Dictionary, History and QA rounds
tabs). `template` writes a starting standard; `audit` reports the structure of docparse-parsed
spreadsheets and documents with cell text kept behind IFC labels. Version, QA-round,
pass-by-person and retest rules carry Z3 contracts.
