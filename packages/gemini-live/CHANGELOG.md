# Changelog — sunholo/gemini_live

## 0.5.0

Measured against Vertex AI on 25 Sept 2026 (project `sunholo-daneel`, us-central1),
for Daneel's narrated briefs and live avatar (daneel repo, `design_docs/planned/m-daneel-live.md`).
Every builder below was sent to the live API and accepted; the tests pin those shapes.

**Fixes**
- `endpoints.vertexAiUrl("global", …)` built `global-aiplatform.googleapis.com`, which is not
  the Live endpoint (HTTP 404 on the WebSocket handshake). It is now
  `aiplatform.googleapis.com`, via the new `vertexHost` (proven: `global` has no prefix).
- `messages.buildSetupWithFeatures` put `thinkingConfig` at setup level, which Vertex refuses
  (close 1007: *Unknown name "thinkingConfig" at 'setup'*). It is now inside `generationConfig`,
  where `thinkingBudget: 0` is accepted and removes thinking (0 thought tokens, measured).
- The docs said the 3.1 message protocol (`realtimeInput.text` / `.audio`) is AI Studio only.
  Both protocols are accepted on Vertex `gemini-3.8-live`, and `realtimeInput.audio` on 2.5.

**Features**
- `voices`: the Vertex models listed on 25 Sept (`vertexLive38`, `vertexLive25`, `ttsFlash25`,
  `ttsPro25`, `ttsFlash31Preview`), proven closed sets `isVertexLiveModel`, `isTtsModel`,
  `supportsAvatar` (3.8 only), `defaultAvatar` ("Ben", measured), `britishEnglish` ("en-GB").
  `defaultVertexModel` is unchanged.
- `config`: `buildSpeechConfig(voice, languageCode)` — the prebuilt voices carry no accent
  (with none requested, Charon was judged American English); `buildGenerationConfig`,
  `buildAvatarConfig`.
- `messages`: `buildSpeechSetup` (voice, languageCode, thinking), `buildAvatarSetup`
  (gemini-3.8-live live avatar: `responseModalities: ["VIDEO"]` + `avatarConfig`; the server
  streams fragmented MP4 in ~16 KB `video/mp4` parts), `buildAudioStreamEnd`.
- `parsers`: `usageOf` (prompt, output, thoughts, total, and output by modality — AUDIO, VIDEO,
  TEXT), `mediaPartsOf` (inline parts with their mime type, in order), `inputTranscriptOf`,
  `outputTranscriptOf`, `turnCompleteOf` — read together, since one message can carry media
  and a transcription.
- New module `tts`: batch text-to-speech on Vertex `generateContent` — `buildTtsRequest` (voice,
  languageCode, style line, `maxOutputTokens`), `ttsAudioOf`, `ttsMimeOf`, `finishReasonOf`,
  `outputTokensOf`, `inputTokensOf`, `pcmSeconds`, and the proven `completeOk`.
  `maxOutputTokens` is **enforced** on audio (cap 300 → 292 tokens, speech cut at 11.7 s), and
  the truncated response reported `finishReason: STOP`, not `MAX_TOKENS` — so `completeOk`
  judges by the token count as well as the reason.
- Native tests (`live_test.ail`, 17) and a boot smoke (`_smoke.ail`); `[release]` declared.
- `ailang` floor raised to `>=0.40.0` (checked on 0.40.1 and 0.43.1).

## 0.4.1

Protocol helpers for the Gemini Live WebSocket API on Vertex AI (2.5) and Google AI Studio (3.1):
URLs, setup/text/audio/video/tool messages, feature configs (proactive audio, affective dialog,
thinking, VAD, activity handling), parsers, and the 30-voice catalog.
