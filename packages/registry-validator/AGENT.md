# sunholo/registry-validator

## When to use this package
Use to validate AILANG packages before publishing to the registry. This is the AILANG-native validator — it validates AILANG packages *using AILANG itself* (dogfooding).

Can be deployed as a standalone `serve-api` service or used as a library.

## Quick start

### As a serve-api endpoint
```bash
ailang serve-api --caps IO,FS packages/registry-validator/
# POST http://localhost:8080/api/sunholo/registry-validator/validate/validatePackage
```

### As library imports
```ailang
import pkg/sunholo/registry-validator/validate (validatePackage, ValidationResult)
import pkg/sunholo/registry-validator/metadata (generateMetadata)

-- Validate a package directory
let result = validatePackage("/path/to/my-package")
if result.valid then
  println("Package valid: " ++ result.packageName ++ "@" ++ result.version)
else
  println("Errors: " ++ show(result.errors))
```

## Exported functions

| Function | Module | Signature | Description |
|----------|--------|-----------|-------------|
| `validatePackage` | validate | `string -> ValidationResult ! {IO, FS}` | Full validation pipeline on a package dir |
| `generateMetadata` | metadata | `(result, ...) -> string` | Generate metadata.json for registry upload |
| `generateIndexEntry` | metadata | `(result, ...) -> string` | Generate index.json entry |

## What it checks
1. `ailang.toml` exists and is parseable
2. Required fields: name, version, edition
3. Name format: vendor/name
4. At least one `.ail` source file exists
5. Content hash (SHA-256 of sorted source files)
6. Interface hash (SHA-256 of name + edition + exports)
7. AGENT.md presence (warning if missing)

## A/B testing with Go version
The Go version (`cmd/registry-validator/`) handles GCS upload and is the production service. This AILANG version can run alongside for comparison — same input tarball should produce matching validation results.
