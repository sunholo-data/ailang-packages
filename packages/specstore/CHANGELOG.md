# Changelog

## 0.3.1

Two fixes found in a live run. `check` now exits 1 when it reports problems (or when the
standard or the spec fails to load), so scripts and CI can gate on it; it still prints the
same ✗ lines. A parameter value written as an unquoted number (`value: 90`) is read as 90.0
and never matched what the site pushes; parameter values are now normalised to their
canonical string at load (90 → "90", 90.5 → "90.5"), and an unquoted boolean reads
true/false, in step with what `compare` reads back from the run.

## 0.3.0

Three things a real flow needed. A parameter key may name every element of an array with `[]`:
`ecommerce.items[].item_id` is checked in each item, an empty array fails, and the first bad
element is named (`ecommerce.items[1].item_id missing`). A spec's `site` block may say
`checks: [datalayer]` to judge the data layer only; without it both the data layer and GA4 are
judged, as before. An event may record `live`, the version the client has put on the site: when
its last change is newer, `compare` writes `not tested` with "waiting for release" instead of a
failure that is really a release not yet made. Tests: `qa_test.ail` (20).

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
