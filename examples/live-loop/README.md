# Loop Lab moved

The application now lives in [sunholo-data/ailang-loop-lab](https://github.com/sunholo-data/ailang-loop-lab).
It owns the UI, capture/device lifecycle, musical sessions, undo and DAW workflows.
This repository owns the generic `sunholo/audio` package.

The application history was retained through a subtree extraction from commit
`93314fc581a7ee2fefdc82392a92228f8b01a2dd`. Existing historical source/evidence is
available at that pinned commit. The new repository currently requires organization
access. Its prerelease manifest pins the audio candidate by exact Git revision;
released app builds will use an exact registry version.

See the [migration record](../../design_docs/implemented/loop-lab-repository-split/README.md).
