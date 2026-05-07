# motoko-ext-abi

## When to use this package

Use when building a `motoko_agent` extension package (`motoko-ext-*`). This package provides the stable ABI contract — the shared type definitions that every extension must satisfy when registering with the host agent.

## Quick start

```ailang
import motoko-ext-abi/types (ExtensionHooks, ExtCtx, ToolPolicyDecision, NoOpinion, Delegate, NoIntercept, NoDecision)
import src/core/config (RuntimeConfig)

export func register_with_config(cfg: RuntimeConfig) -> ExtensionHooks ! {} {
  {
    id: "my-extension",
    provided_tools: [],
    on_describe_tools: () -> [],
    on_build_system_prompt: (_ctx) -> { prepend: [], append: [] },
    on_budget_plan: (_ctx, _plan) -> { requested_total: None, requested_solver: None, requested_verifier: None },
    on_tool_policy: (_ctx, _call) -> NoOpinion,
    on_tool_handle: (_ctx, _call) -> Delegate,
    on_response_intercept: (_ctx, _resp) -> NoIntercept,
    on_solver_candidate: (_ctx, _candidate) -> NoDecision
  }
}
```

## Exported types

| Type | Description |
|------|-------------|
| `ExtensionHooks` | Return type from `register_with_config` — all hook slots |
| `ExtCtx` | Runtime context passed to every hook |
| `BudgetPlan` | `{ total, solver, verifier: int }` |
| `BudgetPatch` | Optional budget adjustments |
| `PromptPatch` | `{ prepend, append: [string] }` |
| `ToolPolicyDecision` | `Allow \| Deny(string) \| NoOpinion \| Pending(string, PolicyDefault)` |
| `ToolHandleDecision` | `Handled(ToolResultEnvelope) \| Delegate` |
| `ResponseInterceptDecision` | `InterceptHandled(ToolResultEnvelope) \| NoIntercept` |
| `FinalizeDecision` | `Accept(string) \| ContinueWithFeedback(string) \| NoDecision` |
| `Msg` | `{ role, content: string }` |
| `ToolCallEnvelope` | `{ id, tool: string, arguments: Json }` |
| `ToolResultEnvelope` | `{ tool_call_id, tool, stdout, stderr: string, exit_code: int, metadata: Json }` |
| `VerificationConfig` | `{ enabled: bool, command: string }` |
| `ExtRuntime` | `{ registry: ExtRegistry, strict_mode: bool, verification: VerificationConfig }` |

## Common patterns

- Every extension's `ailang.toml` must declare `"motoko-ext-abi" = "1.0.0"` as a dependency
- The `register_with_config` function must be exported from a module named `<your-package>/register`
- For extensions that provide tools: populate `provided_tools` with tool names and implement `on_describe_tools`
- For policy extensions (approval gates): implement `on_tool_policy` and return `Pending` / `Allow` / `Deny`
- For tool-intercepting extensions: implement `on_tool_handle` and return `Handled(result)` to short-circuit native execution
- Wire the extension into `motoko_agent` by adding it to `[extensions].packages` in `ailang.toml` and running `ailang generate-extension-registry`
