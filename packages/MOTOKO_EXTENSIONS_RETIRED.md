# Retired: `sunholo/motoko_ext_*` (extension ABI 2.2)

**Retired 2026-09-28 (Mark).** All 14 packages below were unpublished from the AILANG registry,
96 versions in total. The sources stay here for reference.

**Why:** these target motoko's extension ABI **2.2**, which only the old `sunholo/eval-canonical`
fork loaded. That fork is retired. Motoko `main` (arniwesth/motoko_agent) uses extension ABI
**8.0** and ships its own in-repo copies under `packages/`, some with the same names and version
numbers but different code. Keeping these in the registry would have been actively misleading.

| Package | Status |
|---|---|
| motoko_ext_abi, a2a, ai_compat, ailang_docs, compaction_ai, compose, context_mode, decision_framework, exa_search, mcp, microrag, omnigraph, test_dummy | Superseded by the ABI 8.0 copies in arniwesth/motoko_agent `packages/` |
| motoko_ext_fmt | Not superseded. **Port to ABI 8.0 planned**, likely inside `motoko_ext_ailang_tools` (arniwesth/motoko_agent#200) |
| motoko_ext_typefix_agent | Unused; was never published |

**Do not republish these from here.** The current AILANG-specific motoko extension is
`motoko_ext_ailang_tools` (ABI 8.0). See `MOTOKO.md` §9 in sunholo-data/ailang.
