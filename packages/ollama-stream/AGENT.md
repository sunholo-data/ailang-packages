# sunholo/ollama_stream

## When to use this package

Use this when you want incremental, line-by-line streaming from a local Ollama server — the kind that lets you render tokens as they arrive instead of waiting for the full response.

**Why not `std/ai.stepWithStream`?** That function is wired for SSE-based AI APIs (Anthropic, OpenAI, Gemini). For Ollama it documents itself as a "NO-OP fallback" — it calls the non-streaming version and synthesises one fake chunk at the end. This package goes directly at Ollama's NDJSON `/api/chat` endpoint via `std/stream.ndjsonPost`, so you get the real stream.

**Thinking-model aware.** Models like `gemma4:26b` emit a long `message.thinking` reasoning phase before any `message.content` arrives. The parser surfaces both as separate fields so you can render reasoning differently (dim it, prefix it, hide it).

## Quick start

```ailang
import pkg/sunholo/ollama_stream/client (streamChat, Chunk)
import std/io (print, println)
import std/result (Result, Ok, Err)

func render(c: Chunk) -> bool ! {IO} {
  if c.thinking != "" then { print("[think] " ++ c.thinking); true }
  else if c.text != "" then { print(c.text); true }
  else if c.done then { println(""); false }
  else true
}

export func main() -> () ! {Stream, IO} {
  match streamChat("http://100.83.21.3:11434", "gemma4:26b",
                   "Say hi in three words.", render) {
    Ok(_)  => println("--- stream ended cleanly ---"),
    Err(_) => println("--- stream error ---")
  }
}
```

Run with `ailang run --caps Stream,IO that_file.ail`.

## Exported items

- `Chunk` — record `{ text: string, thinking: string, done: bool }`
- `streamChat(endpoint, model, userMessage, handler) -> Result[unit, StreamErrorKind] ! {Stream}` — main entry
- `chatBody(model, userMessage) -> string` — request-body builder, exported for debugging
- `parseChatChunk(line) -> Option[Chunk]` — parses one NDJSON line
- `dispatchEvent(evt, handler) -> bool` — bridge from `StreamEvent` to `Chunk` handler (you usually don't call this directly)

## Endpoint expectations

`endpoint` is the base URL of the Ollama daemon — e.g. `"http://localhost:11434"` or, over Tailscale, `"http://100.83.21.3:11434"`. The package appends `/api/chat` itself. Don't include a trailing slash.

Ollama's API has no auth on the wire. Tailscale provides device-level identity for tailnet-only deployments; never expose `:11434` to the public internet.

## Scope (what this package deliberately does NOT do)

- **No `/api/generate`.** Single-turn chat is enough for now and the response shapes differ. Add a `streamGenerate` if you need it; the underlying `ndjsonPost` plumbing is identical.
- **No multi-turn history.** `chatBody` builds a one-message conversation. Copy and adapt the JSON builder if you need history.
- **No tool calls.** Ollama itself rejects tools per the AILANG provider docs (`AIError{ToolsNotSupported}`); this package doesn't try to work around that.
- **No automatic reconnect.** Per AILANG's stream determinism axiom, callers handle reconnection.

## Requirements

- AILANG `>=0.22.0` — this version added the `_stream_ndjson_post` builtin and the `ndjsonPost` wrapper in `std/stream`. Earlier versions don't have an NDJSON-tolerant streaming primitive.
- `--caps Stream` at runtime (plus `IO` if your handler prints).
