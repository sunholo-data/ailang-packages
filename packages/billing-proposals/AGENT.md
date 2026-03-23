# sunholo/billing_proposals

## When to use this package
Use when AI agents or UI need to prepare a billing action before human approval. This package manages the proposal lifecycle (create, approve, expire, reject) as a pure state machine. No network calls — just state transitions.

## Quick start
```ailang
import pkg/sunholo/billing_proposals/proposal (
  createProposal, canCreateApprovalLink, markAwaitingPayment,
  markApproved, isAgentInitiated, statusLabel, Agent, Human
)
import pkg/sunholo/billing_proposals/proposal_summary (summarizeProposal)
import pkg/sunholo/billing_entitlements/plan (defaultCatalog)

-- Agent creates a payment proposal
let prop = createProposal(
  "prop_abc", "uid_123", "pro_monthly",
  "Monthly page limit nearly exhausted",
  Agent("docparse-assistant"), "2026-03-23T12:00:00Z"
)

-- Check if we can generate an approval link
if canCreateApprovalLink(prop) then
  -- After Stripe checkout session is created:
  let prop2 = markAwaitingPayment(prop, "https://checkout.stripe.com/...", "2026-03-23T13:00:00Z")
  -- After human approves:
  let prop3 = markApproved(prop2)
else ()

-- Generate human-readable summary
match summarizeProposal("pro_monthly", "free", defaultCatalog(), "page limit reached") {
  Ok(summary) => -- summary.description, summary.pageLimit, etc.
  Err(e) => -- unknown plan
}
```

## Exported functions

| Function | Module | Signature | Description |
|----------|--------|-----------|-------------|
| `createProposal` | proposal | `(id, principalId, plan, reason, requestedBy, time) -> Proposal` | Create pending proposal |
| `canCreateApprovalLink` | proposal | `(Proposal) -> bool` | Can attach checkout URL? |
| `markAwaitingPayment` | proposal | `(Proposal, url, expires) -> Proposal` | Transition to awaiting |
| `markApproved` | proposal | `(Proposal) -> Proposal` | Transition to approved |
| `markExpired` | proposal | `(Proposal) -> Proposal` | Transition to expired |
| `markRejected` | proposal | `(Proposal) -> Proposal` | Transition to rejected |
| `isActionable` | proposal | `(Proposal) -> bool` | Still pending or awaiting? |
| `isAgentInitiated` | proposal | `(Proposal) -> bool` | Created by AI agent? |
| `statusLabel` | proposal | `(ProposalStatus) -> string` | Display string |
| `summarizeProposal` | proposal_summary | `(targetKey, currentPlan, catalog, reason) -> Result[Summary, string]` | Human-readable summary |
| `upgradePrompt` | proposal_summary | `(current, target, reason) -> string` | One-line chat prompt |

## Common patterns
- Create proposal → create approval link → present URL → await webhook
- Use `isAgentInitiated` to log agent-initiated billing actions separately
- Effects: **none** (pure package)
