# Changelog

## 0.1.2
- Fix: `++` on strings is list-only in the March-2026 dialect; replaced all 9
  string-concat sites in `validate.ail` with `"${...}"` interpolation.
- Fix: `computeHash` now uses effectful `foldlE` instead of pure `foldl` for the
  FS-reading fold (callback reads files, so it carries `! {FS}`).
- No exported signatures changed; `[effects] max` ceiling unchanged.
