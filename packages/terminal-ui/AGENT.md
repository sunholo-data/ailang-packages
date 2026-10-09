# sunholo/terminal_ui
Pure reusable rendering; independent terminal-ui-demo uses IO only.
Core exports are ui dimensions, safeText, cells, wrap, pad, rule, gauge,
clampPage, screen and Dimensions/Screen. Call dimensions first. Screen is exactly
rows lines with body paging, caller chrome with all action rows retained; reserve one empty prompt row.
Body never clips; callers keep total wrapped header/action rows <= rows-5. Screen text ends on the empty prompt row: print(text), print(prompt), flush, readLine. Do not append a newline before input. No raw mode, cursor hiding,
alternate buffer, Process, AI, terminal-size detection or automatic resize.
Cells counts codepoints conservatively: Latin, punctuation/box drawing1,
other symbols including CJK2; unknown glyphs may be overestimated.
No grapheme/emoji combining precision promised. C0/C1 and bidi stripped.
Display sanitation never rewrites source journals. ANSI is trusted clear/home/reset,
plain has no escapes. Use wrap for untrusted bodies; do not emit raw source.
Validate check, test --package both engines, source inline tests, pkg quality --strict.
Demo keys n/v page, h guide, b main, 0 quit, all followed by Enter; EOF quits.
Public module: `sunholo/terminal_ui/ui`.
Imported-callback evaluator bug inbox_1791551801569_90564219 also affects
character closures in generated named tests on pinned v0.52.0. Direct recursive
traversals avoid it; real entry and both-engine named controls are required.
