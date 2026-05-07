# motoko-ext-abi

ABI contract for `motoko_agent` extension packages.

Every `motoko-ext-*` package depends on this package and must export a `register_with_config` function from a `<package>/register` module. This package provides the shared types that form the stable contract between extensions and the host agent.

## Usage

```toml
# In your motoko-ext-* package's ailang.toml
[dependencies]
"motoko-ext-abi" = "1.0.0"
```

```ailang
-- In your extension's register.ail
module motoko-ext-myplugin/register

import pkg/sunholo/motoko_ext_abi/types (ExtensionHooks, ExtCtx, ToolPolicyDecision, Allow, NoOpinion)
import src/core/config (RuntimeConfig)

export func register_with_config(cfg: RuntimeConfig) -> ExtensionHooks ! {} {
  {
    id: "myplugin",
    provided_tools: [],
    on_describe_tools: () -> [],
    on_build_system_prompt: (_ctx) -> { prepend: [], append: [] },
    on_budget_plan: (_ctx, plan) -> { requested_total: None, requested_solver: None, requested_verifier: None },
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
| `ExtensionHooks` | The hooks record every extension must return from `register_with_config` |
| `ExtCtx` | Runtime context passed to every hook (task, step, model, budget, history) |
| `BudgetPlan` | Step budget breakdown (total / solver / verifier) |
| `BudgetPatch` | Optional budget adjustments returned by `on_budget_plan` |
| `PromptPatch` | Prepend/append slices returned by `on_build_system_prompt` |
| `ToolPolicyDecision` | `Allow \| Deny(reason) \| NoOpinion \| Pending(reason, default)` |
| `ToolHandleDecision` | `Handled(result) \| Delegate` |
| `ResponseInterceptDecision` | `InterceptHandled(result) \| NoIntercept` |
| `FinalizeDecision` | `Accept(msg) \| ContinueWithFeedback(msg) \| NoDecision` |
| `PolicyDefault` | `AllowAfterTimeout \| DenyAfterTimeout` |
| `Msg` | `{ role: string, content: string }` — conversation message |
| `ToolCallEnvelope` | `{ id, tool, arguments: Json }` — inbound tool call |
| `ToolResultEnvelope` | `{ tool_call_id, tool, exit_code, stdout, stderr, metadata }` — tool result |
| `VerificationConfig` | `{ enabled: bool, command: string }` — DP7 verifier config |
| `ExtRegistry` | `{ hooks: [ExtensionHooks] }` |
| `ExtRuntime` | `{ registry, strict_mode, verification }` |
| `ToolDecisionEnvelope` | `{ call, decision }` — policy log entry |

## Versioning policy

`ExtensionHooks` is the ABI boundary. Adding an **optional** field (with a `None` default) is backwards-compatible and is a **minor** version bump. Changing an existing field's type or removing a field is a **major** version bump, requiring all published `motoko-ext-*` packages to update their dependency.

## Installation

```bash
ailang install motoko-ext-abi@1.0.0
```

## Integration with motoko_agent

`motoko_agent` uses `ailang generate-extension-registry` to wire installed extensions into a static dispatch file. See the [Extension Packages guide](https://ailang.sunholo.com/docs/guides/extension-packages) for the full workflow.
