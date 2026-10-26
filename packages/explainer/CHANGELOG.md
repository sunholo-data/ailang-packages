# Changelog

## 0.1.1

Contracts on 33 of the 36 exports: 18 proved by Z3, 15 checked at runtime
(`--verify-contracts`, evaluator) and by the property tests, where the verifier cannot encode
the function (Array or Map parameters, `join`, `toLower`, JSON). The three left (`shortHash`,
`voiceId`, `takeFile`) call `sha256Hex`, which `ailang verify` cannot yet encode
(sunholo-data/ailang#1950); `take_test` covers them.

Fixes found while writing them:
- `cut.longer`'s contract compared records with `==`, which fails when contracts are
  evaluated (sunholo-data/ailang#1954); it compares fields now.
- `cut.bounds` returns None when the last cut would reach the end of the take (the cut in a
  one-frame quiet run can fall on the window's last frame), and for no lines. Before, the
  last line came out empty and `cutTake` called it silent.
- `cutTake` refuses no lines, and its message for a failed cut says what went wrong.
- `words.kept` compares with `find` instead of `charCode`, so Z3 proves that a kept character
  is never a separator. A string longer than one character is no longer "kept" (foldChars
  never passes one).

Output is unchanged: on the world_intro take all 44 clips are byte-identical to 0.1.0's.

## 0.1.0

First release. `take`, `words`, `align`, `cut`, `level` (pure) and `narrate` (`speak` needs AI):
one-take narration, difflib-equivalent word alignment, pause-centred cuts, kit-equivalent
trimming and levelling to PCM16 WAV. Matches the Python pipeline it replaces on the
world_intro take: the same 44 cuts and trims, every sample within 1 LSB.
