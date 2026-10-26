# sunholo/explainer — agent notes

Narration for explainer films, the half that is not drawing: voice a whole script in ONE
`std/ai.callSpeech` call, align speech-to-text word timings to the script, cut the take at the
longest pause between lines, then trim and level each line into a mono PCM16 WAV. The picture
(Manim), the speech-to-text model (e.g. faster-whisper) and the clip cache belong to the caller.

## Modules

| module | what | effects |
|---|---|---|
| `take` | `uniqueLines`, `takeText` (lines as paragraphs), `takeStyle`, `voiceId` (voice, language, model, hash of style and script), `takeFile` | pure |
| `words` | `normalise`: lower case, split at whitespace and hyphens, keep a-z0-9, number words as digits | pure |
| `align` | `matchingBlocks` (difflib's, autojunk off), `lineSpans(lines, [Heard]) -> Option[[Span]]` | pure |
| `cut` | `frameLevels` (10 ms RMS), `cutFrame`, `bounds(samples, spans) -> Option[[int]]` | pure |
| `level` | `levelClip(take, from, frames) -> Option[bytes]` (WAV), `keep`, `speechStart` | pure |
| `narrate` | `speak` (callSpeech with retries), `speechOptions`, `cutTake(take, heard, lines) -> Result[[bytes], string]` | `speak`: AI |

## Use

```ailang
import pkg/sunholo/explainer/take (takeText, takeStyle, voiceId)
import pkg/sunholo/explainer/narrate (speak, speechOptions, attempts, cutTake)

-- one call for the whole script
match speak(takeText(lines), "Sulafat", takeStyle(style), speechOptions("gemini-2.5-pro-tts", "en-GB"), attempts()) {
  Ok(take) => -- get word timings for `take` from your speech-to-text, as [Heard]
              match cutTake(take, heard, lines) { Ok(wavs) => ..., Err(why) => ... },
  Err(e) => ...
}
```

Run per-sample work on the bytecode VM: `ailang run --bytecode ...`. A 6-minute take
(7.4 M samples) cuts and levels in about 8 s there; the evaluator is about 50x slower.

## Behaviour

- **Name the TTS model.** `gemini-2.5-pro-tts` and `gemini-2.5-flash-tts` work on Vertex;
  AILANG's default `gemini-2.5-flash-preview-tts` answered "Internal error" there (2026-10-26).
- **Cut:** frame k is the RMS of samples within 5 ms of k x 10 ms; quiet is below 5% of the
  loudest frame. Each cut is the middle of the longest quiet run in
  [min(last word of line k, first word of line k+1) - 150 ms, max(...) + 150 ms); of equal
  runs the later wins; with no quiet frame, the quietest frame. `bounds` is None when a window
  starts before the previous cut (lines too close to separate).
- **Level:** the clip starts 20 ms before the 5 ms envelope passes 5% of its loudest (a breath
  is not speech) and ends 50 ms after the last sample above 1% of full scale; scaled to RMS
  0.07, clipped at 0.98, quantised at x * 32767 rounded to nearest.
- **Equivalence:** on the world_intro take (44 lines, 5 min 7 s), every cut and trim equals the
  Python pipeline this replaces, and every sample is within 1 LSB (the Python truncated).
- Lines are matched by words, so a line whose every word was misheard has no span: `cutTake`
  says so rather than guess.

## Limits

- One speaker: `std/ai.callSpeech` has no multi-speaker mode.
- Mono, 24 kHz in and out (Gemini's TTS rate).
- Building a long list by consing is quadratic in AILANG 0.54, so per-sample output goes
  through `std/array` whole-array operations (`scale`, `updateMany`) and
  `std/audio.floatsToPcm16`; keep it that way when changing `level`.

## Related packages, and why they are not dependencies

Checked against the registry on 2026-10-26 (`ailang pkg search` audio, wav, pcm, speech, tts,
whisper, diff, align, words, retry, gemini, dsp):

- `sunholo/audio` 0.5.0: its `levels` sets gain from active-window RMS (1024-frame windows)
  and meets a peak ceiling by turning the whole clip down. The kit levels to the plain RMS of
  the trimmed clip and clips the few samples past 0.98, and `level` must match the kit's own
  clips. Its PCM16 convention (`round(x * 32767)`) is the one `level` uses; both call the same
  `std/audio` builtins underneath. Onset trimming has no counterpart there.
- `sunholo/gemini_live` 0.5.1 `tts`: builds raw Vertex `generateContent` TTS requests for a
  Net caller. This package voices through `std/ai.callSpeech` (the AI effect, with its budget
  and trace). A take cut short is caught here by alignment: every line must be heard.
- `sunholo/external_backend` 0.2.0: for a caller that runs Whisper or the kit as a
  subprocess; the films' orchestrator (`ailang-explainers/films/narrate`) uses its `runJson`.
  This package itself has no Process effect.
- Nothing on the registry aligns a transcript to a script, normalises spoken words, or picks
  cut points; `align`, `words` and `cut` are new.

## Validation

`ailang test --package .` (26); inline, `ailang test --allow-skips <module>.ail` for each of
the six modules (property tests skip where there is no generator: Array, Map, records);
`_smoke.ail`.

Contracts: `ailang verify --package .` proves 18. Twelve more are skipped by the verifier
(Array or Map parameters, `join`, `toLower`, JSON) and so are runtime checks only. They run
under `ailang run --verify-contracts` on the **evaluator**: the bytecode VM ignores the flag
(sunholo-data/ailang#1956). `shortHash`, `voiceId` and `takeFile` carry none: `sha256Hex`
makes the verifier error (sunholo-data/ailang#1950). On the world_intro take (7.4 M samples,
44 lines), `cutTake` under the evaluator with `--verify-contracts` broke no contract and gave
the same 44 clips, byte for byte, as the bytecode VM (5 min 36 s against 8 s).

When writing contracts here: compare records field by field, not with `==` (#1954), and
prefer `contains` or a recursive predicate to `forall`, which Z3 proves but the runtime cannot
evaluate (#1955). String `<=`/`>=` do not encode (#1953); `find` does.
