# Installing the `omnigraph` binary

This AILANG package is a thin wrapper that shells out to the **`omnigraph` CLI** — a typed property-graph database with git-style branching, by [ModernRelay](https://github.com/ModernRelay/omnigraph). The package itself does nothing useful without the binary installed.

If you (a future AI agent or human) are reading this because `OmnigraphRead`/`OmnigraphMutate`/`OmnigraphBranch`/`OmnigraphStatus` calls are failing with `omnigraph: command not found`, install it via one of the methods below.

## What omnigraph is

A versioned property graph (Decision nodes, Component nodes, `DependsOn` / `Governs` edges in the motoko default schema) with git-like branching: branch off `main`, mutate, verify, merge. Storage is a local file (`./repo.omni`) or S3. Queries live in `.gq` files. Project home: <https://www.omnigraph.dev>. Source: <https://github.com/ModernRelay/omnigraph>.

## Quick install (recommended)

The shell installer drops binaries in `~/.local/bin`, which is exactly what `exec.ail` adds to `$PATH` before invoking the CLI. No further wiring required.

```bash
curl -fsSL https://raw.githubusercontent.com/ModernRelay/omnigraph/main/scripts/install.sh | bash
```

## Homebrew (macOS / Linux)

```bash
brew tap ModernRelay/tap
brew install ModernRelay/tap/omnigraph
```

## Other methods

```bash
# Edge / rolling release
curl -fsSL https://raw.githubusercontent.com/ModernRelay/omnigraph/main/scripts/install.sh | RELEASE_CHANNEL=edge bash

# Pin a specific version
curl -fsSL https://raw.githubusercontent.com/ModernRelay/omnigraph/main/scripts/install.sh | VERSION=v0.1.0 bash

# Custom install directory
curl -fsSL https://raw.githubusercontent.com/ModernRelay/omnigraph/main/scripts/install.sh | INSTALL_DIR="$HOME/bin" bash

# From source (Rust)
curl -fsSL https://raw.githubusercontent.com/ModernRelay/omnigraph/main/scripts/install-source.sh | bash

# Manual cargo build
cargo build --release --locked -p omnigraph-cli -p omnigraph-server
install -m 0755 target/release/omnigraph        ~/.local/bin/omnigraph
install -m 0755 target/release/omnigraph-server ~/.local/bin/omnigraph-server
```

## Verify

```bash
omnigraph version
omnigraph-server --help    # only needed if you run the server mode
```

If `which omnigraph` returns nothing after install, make sure `~/.local/bin` is on your `$PATH`. The motoko extension prepends it automatically for its own subprocess (see `exec.ail` `build_shell_argv`), but your interactive shell may not.

## How this package invokes it

The extension shells out from `exec.ail` with `bash -lc 'PATH="$HOME/.local/bin:$PATH"; cd <workdir>/omnigraph; omnigraph <args>'`. Two consequences:

1. The binary **must** be reachable via `$HOME/.local/bin` or the system `$PATH`. The Homebrew install path (`/opt/homebrew/bin` or `/usr/local/bin`) works because it's already on `$PATH` for typical shells.
2. The CLI is invoked **inside an `omnigraph/` subdirectory of the agent's workdir**. That dir should contain `omnigraph.yaml`, `schema.pg`, `queries/`, `mutations/`, and the storage file (`repo.omni` by default). See `motoko_agent/omnigraph/` for a reference layout.

## When omnigraph is not installed

The motoko host currently registers this extension unconditionally if it's in the profile's `extensions.order`. Calls will fail with non-zero exit and `command not found` in stderr. If you don't have an omnigraph-shaped task in front of you, the cheaper move is to **remove `"omnigraph"` from `extensions.order`** in the active profile (e.g. `.motoko/config/dogfood/config.json`) rather than installing the binary just to silence the warning.
