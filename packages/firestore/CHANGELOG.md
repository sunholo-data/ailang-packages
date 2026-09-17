# Changelog

## 0.7.3

Fix STRICT_FALLBACK_001 (empty-Ok in Result-returning matches) that broke
compilation on ailang v0.39.5+, blocking every consumer package.

- `client.listDocs`: the missing-`documents` branch keeps returning an empty
  array, now annotated `@allow_empty_ok` — Firestore's list response omits the
  `documents` field when the collection is empty, so an empty array is the
  by-spec success, not a masked failure.
- `query.parseQueryResponse`: a runQuery body that is not a JSON array is a
  malformed response — return a descriptive `Err` instead of masking it as an
  empty result set.
