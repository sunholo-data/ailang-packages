# Audio 0.3 consumer workflow evidence

Full behavior, quality sections, proof scope, tests and review limits:
[implementation report](../../../../design_docs/implemented/audio-v3-workflow/README.md).

- `native-tests.txt`: 10/10 strict-bytecode app checks, no fallback.
- `node-tests.txt`: 45/45 host checks, including reference parity and actual-app
  flow with fake browser APIs, real AILANG planning and actual JavaScript preparation/render code.
- `python-tests.txt`: 6/6 planner/HTTP checks; temporary loopback listener.
- `quality.json`: local app 0.2.0 report; 3/6 proved, 3 skipped, no gates.
- `node-worker-timing.json`: descriptive Node preparation cost, not browser/device latency.
- `loopback-preview.json`, `private-preview.json`: server-side route/probe evidence,
  not laptop/browser visual or listening acceptance.

No microphone samples, raw take, private asset, device label or device identifier
is retained as evidence. Text logs have ANSI styling stripped. Earlier Firefox
microphone feedback and runner-v2 soak are historical, not new-control acceptance.
