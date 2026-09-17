# sunholo/http_helpers

## 0.1.5

- fix: align `authGet`/`authPost`/`authPostJson` return type annotations with the
  current `std/net.HttpResponse` record (it gained a `bodyBytes` field), so the
  package compiles again on ailang v0.39.5+. Exported signatures are otherwise
  unchanged for consumers.
