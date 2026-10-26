# sunholo/explainer

Narrate an explainer film in one Gemini take, with AILANG doing the audio work: the script
voiced in a single `std/ai.callSpeech` call (so the voice does not drift between lines), word
timings from your speech-to-text aligned to the script, the take cut at the longest pause
between lines, and each line trimmed and levelled into a mono PCM16 WAV.

First used for the AILANG World film (https://www.sunholo.com/ailang-world/), with the Manim
explainer kit drawing the picture. See [AGENT.md](AGENT.md) for modules, behaviour and limits.
