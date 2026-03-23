# sunholo/docparse_access_gate

## When to use this package
Use in the DocParse API service to enforce billing entitlements and record usage. This is the bridge between the billing system and DocParse's parse execution. Add it as a dependency to DocParse, call `authorizeParse` before every parse, and `recordSuccessfulParse` after.

## Quick start
```ailang
import pkg/sunholo/docparse_access_gate/parse_authorization (authorizeParse)
import pkg/sunholo/docparse_access_gate/usage_recording (recordSuccessfulParse)
import pkg/sunholo/billing_entitlements/capability_check (AllowDecision, Allow, Deny)

-- Before parse:
match authorizeParse("uid_123", 5, true, "2026_03") {
  Ok(Allow) => {
    -- Proceed with parse...
    let result = doParse(file);
    -- After successful parse:
    let _ = recordSuccessfulParse("uid_123", "2026_03", result.pages, result.bytes, result.ocrPages);
    Ok(result)
  },
  Ok(Deny(reason)) => Err("Forbidden: " ++ reason),
  Err(e) => {
    -- Firestore error — fail open with free tier defaults
    let result = doParse(file);
    Ok(result)
  }
}
```

## Exported functions

| Function | Module | Signature | Description |
|----------|--------|-----------|-------------|
| `authorizeParse` | parse_authorization | `(principalId, fileSizeMb, isApiRequest, period) -> Result[AllowDecision, string] ! {Net, FS, Env}` | Check if parse is allowed |
| `recordSuccessfulParse` | usage_recording | `(principalId, period, pages, bytes, ocrPages) -> Result[(), string] ! {Net, FS, Env}` | Record usage after parse |

## Design decisions
- **Fail-open**: If Firestore is unavailable, falls back to free tier (availability > enforcement)
- **Lazy init**: Missing usage docs start from zero (no pre-provisioning needed)
- **No retries**: Write failures return error; caller decides retry strategy
- Effects: `--caps Net,FS,Env`
