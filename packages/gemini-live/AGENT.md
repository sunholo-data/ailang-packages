# sunholo/gemini_live

WebSocket protocol helpers for the Gemini Live API — build setup/text/audio messages, parse responses, configure proactive audio/affective dialog/thinking/VAD.

## When to use this package

Use when building AILANG applications that connect to Gemini Live API via WebSocket for bidirectional audio streaming. This package handles protocol-level message construction and parsing, not session management or audio playback.

Supports **two backends**:
- **Vertex AI** (ADC auth): `gemini-3.8-live` (GA, us-central1 only, live avatars) and `gemini-live-2.5-flash-native-audio` (GA, us-central1 and europe-west4), plus batch **text-to-speech** (`tts` module: `gemini-2.5-flash-tts`, `gemini-2.5-pro-tts`, `gemini-3.1-flash-tts-preview`). Both message protocols are accepted on Vertex 3.8 (measured 25 Sept 2026).
- **Google AI Studio** (API key, 3.1 models): `realtimeInput.text` text, `realtimeInput.audio` audio

**Three things that surprised us, measured against Vertex on 25 Sept 2026:**
- The prebuilt voices have **no accent of their own** — pass a `languageCode` (`britishEnglish()` = `"en-GB"`) and say the accent in the instruction or TTS style line. With neither, Charon was judged American English.
- `gemini-3.8-live` **thinks by default** (78 thought tokens on one sentence). `thinkingBudget: 0` — inside `generationConfig`, which every 0.5.0 builder does — turns it off.
- TTS `maxOutputTokens` is a real ceiling on spend, but a response cut at the cap still says `finishReason: STOP`. Use `tts.completeOk`, which also judges by the token count.

**Availability is per region and changes.** List before assuming: `GET https://<region>-aiplatform.googleapis.com/v1beta1/publishers/google/models`. `global` lists the Live models but did not serve a Live session for them.

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
| Vertex AI (2.5 / 3.8) | `buildTextMessage` or `buildRealtimeText` | `buildRealtimeAudio` (+ `buildAudioStreamEnd`); `buildAudioChunk` for 16 kHz | `vertexLive25()` / `vertexLive38()` |
| Google AI Studio (3.1) | `buildRealtimeText` | `buildRealtimeAudio` | `defaultGoogleAiModel()` |

The response format is the same for both backends — `parseMessage` works with either.

## 0.5.0 — speech, avatars and batch TTS

```ailang
import pkg/sunholo/gemini_live/endpoints (vertexAiUrl, vertexModelPath, vertexGenerateContentUrl)
import pkg/sunholo/gemini_live/messages (buildSpeechSetup, buildAvatarSetup, buildAudioStreamEnd, buildRealtimeAudio)
import pkg/sunholo/gemini_live/parsers (usageOf, mediaPartsOf, outputTranscriptOf, turnCompleteOf)
import pkg/sunholo/gemini_live/tts (buildTtsRequest, ttsAudioOf, outputTokensOf, finishReasonOf, completeOk)
import pkg/sunholo/gemini_live/voices (vertexLive38, ttsFlash25, britishEnglish, defaultAvatar)

-- Live, British, no thinking:
let model = vertexModelPath(project, "us-central1", vertexLive38());
let setup = buildSpeechSetup(model, "Charon", britishEnglish(), "Speak in a calm British accent.", 0);

-- Live avatar (3.8 only): the reply streams as video/mp4 parts — concatenate them.
let avatar = buildAvatarSetup(model, "Charon", britishEnglish(), defaultAvatar(), instruction, 0);

-- Voice in: 100 ms chunks of 24 kHz PCM, then close the stream.
transmit(conn, buildRealtimeAudio(b64, "audio/pcm;rate=24000")); transmit(conn, buildAudioStreamEnd());

-- On each server message: usage by modality, media by mime type, transcripts.
let u = usageOf(json);            -- u.audioOut, u.videoOut, u.thoughts …
let parts = mediaPartsOf(json);   -- [{mimeType, data}]

-- Batch TTS with a provider-enforced cap, POSTed to vertexGenerateContentUrl(...):
let body = buildTtsRequest(script, "Charon", britishEnglish(), "Read this aloud in a calm British English accent: ", 3000);
-- then: completeOk(outputTokensOf(resp), 3000, finishReasonOf(resp)) before using ttsAudioOf(resp)
```

**Measured costs and rates (25 Sept 2026, us-central1):** audio is 25 tokens/s; avatar video
6,192 tokens/s while speaking (idle not billed); TTS prose ran 8.7–10.2 audio tokens per word,
a number-heavy script 18.2. First audio after the end of a spoken question: 350–670 ms
(3.8 with thinking 0: 380 ms). Avatar first frame: ~2.5 s after the text turn.

| Module | Adds in 0.5.0 |
|---|---|
| `endpoints` | `vertexHost` (proven: `global` has no prefix), `vertexModelPath`, `vertexGenerateContentUrl` |
| `config` | `buildSpeechConfig`, `buildGenerationConfig`, `buildAvatarConfig` |
| `messages` | `buildSpeechSetup`, `buildAvatarSetup`, `buildAudioStreamEnd`; `buildSetupWithFeatures` fixed |
| `parsers` | `usageOf`, `mediaPartsOf`, `inputTranscriptOf`, `outputTranscriptOf`, `turnCompleteOf` |
| `tts` | new: `buildTtsRequest`, `ttsAudioOf`, `ttsMimeOf`, `finishReasonOf`, `outputTokensOf`, `inputTokensOf`, `completeOk` (proven), `pcmSeconds` |
| `voices` | model names, `isVertexLiveModel` / `isTtsModel` / `supportsAvatar` (proven), `defaultAvatar`, `britishEnglish` |
