# sunholo/linkedin — CHANGELOG

## 0.5.1
- Fix STRICT_FALLBACK_001 in `comments.ail`: a comments/replies response that
  returns HTTP 200 but is missing the `elements` field is now reported as
  `Err("... missing the 'elements' field ...")` instead of `Ok([])`, so callers'
  `Err` handlers actually fire on malformed responses. A genuine zero-comment
  response (`elements: []`) still returns `Ok([])`.
- No exported signatures changed; `[effects] max` ceiling unchanged.
