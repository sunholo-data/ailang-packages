# sunholo/specstore

Tagging specifications as files, and the standard they follow as a file too.

A **spec** is a folder: `spec.yaml` (events with their parameters, a variable dictionary, a
version history) and `qa/round-01.yaml`, `round-02.yaml` … (one file per QA round, never
edited once written). A **standard** is one YAML file: rules with a status (`decided`,
`proposed`, `open`), where each was decided, and an optional `check` key that switches a
built-in check on. The readable standard, every check and the spreadsheet view come from that
one file, so they cannot drift apart.

```sh
ailang install --path packages/specstore     # puts `specstore` on PATH
specstore template my-standard.yaml          # a starting standard: name the owner, decide the rules
specstore check my-standard.yaml example/demo-bank-web
specstore guide my-standard.yaml STANDARD.md
specstore view  my-standard.yaml example/demo-bank-web demo-bank-web.xlsx
specstore visits  my-standard.yaml <spec> visits.json          # scheduled QA: the run list for a browser
specstore compare my-standard.yaml <spec> observed.json round.yaml   # what the browser saw → a QA round
```

`check` prints each problem with the rule that caught it and that rule's status:

```
✗ [event-casing, proposed] E02: eventName "ctaClick" is not snake_case
✗ [pass-by-person, decided] QA round 2, E03: an automated round recorded a pass; only a person sets a pass
```

A spec may list **deviations** (`rule`, `instead`, `approved_by`). A deviation approved by the
standard's owner turns that rule's findings into notes; one approved by anyone else is itself a
finding. That is how a client-owned data layer with its own naming is recorded rather than
flagged.

`view` writes five tabs: **Spec** (each event with its latest QA result and a retest flag when it
changed after its last test), **Matrix** (one column per dataLayer key), **Dictionary**, **History**
and **QA rounds**. It opens in Excel and, uploaded to Drive, in Google Sheets.

`audit` reads spreadsheets and documents parsed locally by `docparse` and reports only their
structure: column names, fill rates, casing and notation classes, colour use. Cell text is typed
`string<client>` and reaches the report only through declassifiers, so code that would print a
cell does not compile.

**Telemetry:** AILANG exports trace spans (which include file paths) when `GOOGLE_CLOUD_PROJECT`
or `OTLP_GOOGLE_CLOUD_PROJECT` is set. Unset both when the files are confidential.

## Scheduled tag QA

A spec with a `site` block and `visits` can be checked on a schedule. `specstore visits` writes the
run list; a browser script (Playwright, headless Chromium) visits each page and writes
`observed.json`, a list of visits with `status` (`ok`, `blocked`, `error`), `datalayer` (each push
as `{t, url, item}`) and `hits` (each GA4 hit as `{host, tid, en, params}`); `specstore compare`
reads it against the spec and writes the next QA round. The browser half is not part of this
package: it needs a browser, which AILANG does not drive. The comparison never records a pass.
