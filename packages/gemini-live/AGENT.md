# sunholo/gemini_live

WebSocket protocol helpers for the Gemini Live API — build setup/text/audio messages, parse responses, configure proactive audio/affective dialog/thinking/VAD.

## When to use this package

Use when building AILANG applications that connect to Gemini Live API via WebSocket for bidirectional audio streaming. This package handles protocol-level message construction and parsing, not session management or audio playback.

Supports **two backends**:
- **Vertex AI** (ADC auth, 2.5 models): `clientContent.turns` text, `realtimeInput.mediaChunks` audio
- **Google AI Studio** (API key, 3.1 models): `realtimeInput.text` text, `realtimeInput.audio` audio

## Quick start

```ailang
import pkg/sunholo/gemini_live/endpoints (vertexAiUrl, googleAiUrl)
import pkg/sunholo/gemini_live/messages (buildSetup, buildTextMessage, buildRealtimeText)
import pkg/sunholo/gemini_live/parsers (parseMessage)
import pkg/sunholo/gemini_live/voices (defaultVoice, defaultVertexModel, defaultGoogleAiModel)
import pkg/sunholo/gemini_live/config (buildProactivityConfig, buildThinkingConfig)

-- Connect to Vertex AI (2.5)
let url = vertexAiUrl("us-central1", "v1");
let setup = buildSetup(defaultVertexModel(), defaultVoice(), "You are a helpful assistant.");
-- Send text with 2.5 protocol
let msg = buildTextMessage("Hello!");

-- Or connect to Google AI Studio (3.1)
let url = googleAiUrl(apiKey, "v1beta");
let setup = buildSetup(defaultGoogleAiModel(), defaultVoice(), "You are a helpful assistant.");
-- Send text with 3.1 protocol
let msg = buildRealtimeText("Hello!");

-- Parse incoming messages (works for both backends)
let event = parseMessage(rawJson);
-- Returns: {"type":"setup"}, {"type":"modelTurn","parts":[...]}, etc.
```

## Modules

### `sunholo/gemini_live/endpoints`
URL constructors for WebSocket connections.
- `vertexAiUrl(region, apiVersion)` — Vertex AI endpoint
- `googleAiUrl(apiKey, apiVersion)` — Google AI Studio endpoint
- `aiStudioUrl(apiKey, useAlpha)` — AI Studio with alpha toggle

### `sunholo/gemini_live/config`
Composable feature config builders (return KV lists for concat into setup).
- `buildProactivityConfig(enabled)` — proactive audio
- `buildAffectiveConfig(enabled)` — emotion-aware tone
- `buildThinkingConfig(budget, includeThoughts)` — reasoning
- `buildVadConfig(start, end, prefix, silence)` — VAD sensitivity
- `buildActivityHandlingConfig(noInterrupt)` — barge-in control
- `buildRealtimeInputConfig(vadKvs, activityKvs)` — wraps VAD + activity
- `mergeThinkingIntoGenConfig(genKvs, thinkingKvs)` — merge into genConfig

### `sunholo/gemini_live/messages`
Outgoing message builders.
- `buildSetup(model, voice, instruction)` — basic setup
- `buildSetupWithFeatures(model, voice, instruction, proactive, affective, thinkingBudget)` — v2 features
- `buildSetupWithTools(model, voice, instruction, toolsJson)` — with tool declarations
- `buildTextMessage(text)` — 2.5 protocol (clientContent.turns)
- `buildRealtimeText(text)` — 3.1 protocol (realtimeInput.text)
- `buildAudioChunk(b64Audio)` — 2.5 protocol (mediaChunks)
- `buildRealtimeAudio(b64Audio, mimeType)` — 3.1 protocol (realtimeInput.audio)
- `buildRealtimeVideo(b64Video, mimeType)` — 3.1 protocol (realtimeInput.video)
- `buildToolResponse(callId, name, result)` — sync tool response
- `buildToolResponseScheduled(callId, name, result, scheduling)` — async tool response

### `sunholo/gemini_live/parsers`
Incoming message parsers.
- `parseMessage(jsonStr)` — full message dispatch
- `parseToolCall(json)` — extract tool call info
- `parseServerContent(json)` — parse server content
- `checkOutputTranscript(sc)` — extract output transcription
- `checkModelTurn(sc)` — extract model audio/text parts

### `sunholo/gemini_live/voices`
Voice catalog and model defaults.
- `defaultVertexModel()` — `"gemini-live-2.5-flash-native-audio"`
- `defaultGoogleAiModel()` — `"gemini-3.1-flash-live-preview"`
- `defaultBrowserModel()` — `"models/gemini-3.1-flash-live-preview"`
- `defaultVoice()` — `"Sulafat"`
- `voiceCatalog()` — JSON array of 30 voices with name + description

## Effects

**Zero effects** — all functions are pure. This is a protocol library, not an I/O library. Your application handles WebSocket connections (via `std/stream`) and audio playback.

## Choosing the right protocol

| Backend | Text Builder | Audio Builder | Model |
|---------|-------------|---------------|-------|
| Vertex AI (2.5) | `buildTextMessage` | `buildAudioChunk` | `defaultVertexModel()` |
| Google AI Studio (3.1) | `buildRealtimeText` | `buildRealtimeAudio` | `defaultGoogleAiModel()` |

The response format is the same for both backends — `parseMessage` works with either.
