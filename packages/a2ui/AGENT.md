# sunholo/a2ui 0.3.0

Two APIs coexist:

- `sunholo/a2ui/components`: existing custom node builders and flat-array JSON.
  Preserved without changes. Its format is not a versioned A2UI wire envelope.
- `sunholo/a2ui/protocol_v091`: additive A2UI 0.9.1 protocol helpers.

Versioned exports: createSurface(surfaceId), updateComponents(surfaceId, [Json]),
updateDataModel(surfaceId, path, Json), deleteSurface(surfaceId), binding(path),
envelope(name, Json), reviewSurface(surfaceId, draftId, revision, destination, text),
actionJson(Action), decodeAction(string).

`reviewSurface` returns three envelopes: creation, component updates and data model.
It uses the basic catalog ID
`https://a2ui.org/specification/v0_9_1/catalogs/basic/catalog.json`, a root Column,
Text, bound TextField and a submit Button. The `submitDraft` event context carries
draftId, revision and edited text. The application must validate stored draft revision,
destination and write authorization; UI actions do not confer authority themselves.

`decodeAction` checks version and required fields/context. Generic JSON builder
arguments are not a full schema validator. Validate custom components/catalogs at
integration boundaries. All helpers are pure, suitable for native or WASM callers;
no browser renderer or network handler is included.

Validate: `ailang check --package .`. The Discord demo pins upstream schemas at
8ff4651232ab0e02b0123730b502711170637a3a, validates both envelope directions and
component references with AJV 2020, and preserves upstream schema files/licenses.
Specification: https://a2ui.org/specification/v0.9.1-a2ui/
