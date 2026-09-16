# AILANG package development

Read [.agents/skills/ailang-packages/SKILL.md](.agents/skills/ailang-packages/SKILL.md)
before creating, changing, validating or publishing packages. Start with
`ailang version` and `ailang docs package-authoring`. Use the installed binary's
`ailang prompt`, `ailang docs std/<module>` and `ailang pkg-docs <vendor/name>`
before web research for AILANG. The skill includes an older-binary fallback.
Read the affected package's `AGENT.md` and `ailang.toml`; each `packages/*` directory
is an independent package root.

Compilation is one check. Include meaningful contracts, native tests/properties,
effect ceilings and budgets. Run `ailang pkg quality --strict <package-dir>` — NOT YET SHIPPED in any ailang binary (`unknown pkg command 'quality'` as of v0.39.0); skip it rather than report it as blocked — when
available and report gaps; source evidence is not a test run or a proof. Use native
package tests and relevant runtime/integration checks. Reproduce old compiler/test
bug notes against the installed version before adopting workarounds.

Use path dependencies for local development and registry versions for released
consumers. `ailang publish --dry-run` checks packaging; it does not establish that
tests passed or contracts were proved. Report those results separately.

## Coordinator-dispatched jobs only

The remaining instructions apply when the AILANG coordinator dispatched this task
inside a Cloud Run Job. Local interactive sessions follow the user's requested
workflow; they are not automatically coordinator jobs.

## Git Workflow

1. **Branch naming**: Create a working branch using the pattern specified in the directive (e.g., `build/<user>/<site>`, `design-doc/<name>`, `sprint/<sprint-id>`)
2. **Commit messages**: Use descriptive prefixes: `Build:`, `Design:`, `Sprint:`, `Fix:`, `Implement:`
3. **Push your work**: Always `git push` your branch before completing. The coordinator tracks your branch name.
4. **Don't merge**: Push branches only. Merging is handled by the coordinator after approval.

## Output Markers

The coordinator parses your stdout for structured markers. Include these when relevant:

| Marker | Purpose | Example |
|--------|---------|---------|
| `DESIGN_DOC_PATH:` | Path to created design doc | `DESIGN_DOC_PATH: design_docs/planned/v0.9/rate-limiting.md` |
| `SPRINT_PLAN_PATH:` | Path to sprint plan | `SPRINT_PLAN_PATH: design_docs/planned/v0.9/sprint-rate-limiting.md` |
| `SPRINT_JSON_PATH:` | Path to sprint JSON progress file | `SPRINT_JSON_PATH: .ailang/state/sprints/S-RATE-LIMIT.json` |
| `IMPLEMENTATION_COMPLETE:` | Signal that implementation is done | `IMPLEMENTATION_COMPLETE: true` |
| `BRANCH_NAME:` | Branch name for the coordinator | `BRANCH_NAME: build/default/bean-scene` |
| `BUILD_COMPLETE:` | Website build finished | `BUILD_COMPLETE: true` |
| `FILES_CREATED:` | List of files created | `FILES_CREATED: index.html, about.html, style.css` |
| `FILES_MODIFIED:` | List of files modified | `FILES_MODIFIED: src/parser.go, src/types.go` |

## General Behavior

- **Read existing code first**: Understand the codebase before making changes
- **Don't over-engineer**: Make only the changes requested in the directive
- **Run tests if available**: Check for `Makefile`, `package.json`, or test files
- **Commit incrementally**: Small, focused commits are better than one large commit
- **Report errors clearly**: If something fails, explain what went wrong in your output

## Safety Rules (for generated websites)

When building websites, NEVER include:
- `eval()`, `Function()`, `new Function`
- `document.write`, `document.cookie`
- `innerHTML` (use `textContent` if JS needed)
- `XMLHttpRequest`, `fetch` to external URLs
- Tracking scripts, analytics, or third-party embeds
- Form actions pointing to external URLs

## Environment

You have access to:
- `git` — for version control
- `ailang` — the AILANG CLI (if installed)
- Your AI provider's tools (Bash, Read, Write, Edit, Glob, Grep)
- The cloned workspace repository as your working directory

Environment variables available:
- `AILANG_TASK_ID` — Your task identifier
- `AILANG_OBSERVATORY_URL` — Dashboard URL for telemetry (if set)
- `GITHUB_TOKEN` — For git push authentication
