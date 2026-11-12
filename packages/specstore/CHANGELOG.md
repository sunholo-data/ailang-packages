# Changelog

## 0.3.6

Every line describes itself, in every export. Each visit in a round carries its own comment, and the
sheet's Summary shows it on that visit's line: a consent-reject visit reads "correctly absent", not the
whole event's comment with every other visit in it. The event's full comment stays in the round and on
the Spec tab. A variable the dictionary types as `number` is compared as a number (3.00 is 3); a value
that is not a number is a gap of its own; text is still compared exactly. Observed values are not
written beside every parameter, since a logged-in visit can push personal data; a value appears only
where it differs from a fixed or allowed one. Rounds from earlier versions load as before.
Tests: `qa_test.ail` (38), `view_test.ail` (10).

## 0.3.5

A line says only what was checked. A `{{variable}}` whose dictionary entry lists allowed values is now
checked against them: a value outside the list is a gap, `not an allowed value`. A parameter without
a gap is `as the spec says` when its value was confirmed (a fixed value, or an allowed one) and
`present` when the dictionary gives no allowed values, so only "set" can be confirmed. The sheet's
Parameters tab writes the expected value out: the fixed value, `one of: …`, or `any value (name)`.
Each parameter carries its variable and allowed values from the spec's dictionary when the spec loads.
Tests: `qa_test.ail` (35), `view_test.ail` (9).

## 0.3.4

What went right shows as well as what went wrong, so a reader can trust the check. Each round
result now lists every visit that expects or forbids the event, with its own written verdict
(matched, gaps found, could not check, did not run; correctly absent, sent although forbidden),
and on the visit that checked them every parameter with a written status (as the spec says,
missing, empty, differs, not pushed). The round is written as block YAML. The Summary tab has a
line per event and visit, so a consent-reject visit that found nothing is a line of its own, and
counts every visit in its totals; a new Parameters tab lists every parameter with what the spec
expects and its status. The event's result sits on its first line only. Tests: `qa_test.ail` (31),
`view_test.ail` (8).

## 0.3.3

Output a person can read at a glance, in written values only: a result is never carried by colour.
`compare` writes, beside each event's state, a `check` (matched, gaps found, could not check,
waiting for release, no visit) and the parameter counts (`matched` of `expected`), and leads each
comment with them: "V01: 93 of 101 parameters match; …". The state still says "not tested" for a
match, since only a person sets a pass; the check says what the run found. `view` opens on a new
Summary tab (one written line per event, then the totals and what they were built from) and adds
Automatic check and Parameters columns to Spec and QA rounds; the Spec tab now shows a match,
which it hid before. Rounds written by earlier versions load as before, with those fields blank.
Tests: `qa_test.ail` (28), `view_test.ail` (5).

## 0.3.2

Two ways a spec could pass `check` and then fail every run. A `{{…}}` the standard's variable
pattern does not accept (`{{page_type}}` against camelCase) was compared as literal text, so each
such parameter failed on every page; `check` now refuses it under `notation`. A key through
`ecommerce.items` without `[]` (`ecommerce.items.item_id`) asked the list itself for the field and
always reported it missing; `check` now refuses it under a new check key, `arrays`, kept apart from
`key-casing` so a casing deviation does not waive it. The template standard gains an `arrays`
rule; an existing standard enables it by adding `check: arrays` to its rule on parameters. Found on
the first scheduled round against a real site. Tests: `check_test.ail` (16).

## 0.3.1

Builds on the AILANG compiler that ships #1443 (sunholo-data/ailang#2184): a `pure func` must
have an empty effect row. Ten declassifiers in `audit` were declared `pure ... ! {Declassify}`,
which that compiler rejects, so `audit` and `main` failed to check. They drop `pure` and keep
the row. Signatures, labels, proofs and behaviour are unchanged; the package still checks on
AILANG v0.57.4.

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
