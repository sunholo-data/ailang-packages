// Simulation of the upload widget's after-upload flow (0.1.3) under node,
// with a mocked ext-apps App, DOM, fetch and FormData. Runs assets/widget.js
// (or the file given as argv[2]) as the body of an async function, with
// `const CFG = ...` in front of it, exactly as widget.uploadWidgetHtml does.
// Usage: node tests/widget_sim.mjs [widget.js]   (exit 1 on any failure)
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const SRC = readFileSync(process.argv[2] || join(here, '..', 'assets', 'widget.js'), 'utf8');
const AsyncFunction = (async () => {}).constructor;

const REF = 'mcp-file://svc.example/file_0123456789abcdef0123456789abcdef';
const RECEIPT = { fileRef: REF, name: 'AGM.docx', sizeBytes: 13211, sha256: 'ab'.repeat(32) };
const DESCRIPTOR = {
  file: { name: '' }, fileRef: '', maxBytes: 1048576,
  upload: { transport: 'http', method: 'POST', url: 'https://svc.example/uploads',
            multipart: { fileField: 'file', fields: { token: 'tok_secret' } } },
};
const PARSE_ARGS = '{"fileRef":"{{fileRef}}","outputFormat":"blocks"}';
const PARSE_RESULT = { structuredContent: { document: { format: 'docx', blocks: [],
  summary: { totalBlocks: 68, headings: 13, tables: 0, images: 0, changes: 4 } } } };

function baseCfg(over) {
  return Object.assign({ uploadUrl: 'https://svc.example/uploads', hostToolName: 'uploadViaHost',
    maxViaHostBytes: 1048576, nextStep: 'Continue the user\'s request with this fileRef.',
    afterUpload: 'parsing…', extAppsVersion: '2.0.3',
    onUploaded: { tool: 'mcpParse', argsJson: PARSE_ARGS }, onUploadedProblem: '', resultSummary: true }, over || {});
}

// One widget run: render, deliver the descriptor, pick a file, let it settle.
async function run(opts) {
  const els = {};
  const node = (id) => els[id] || (els[id] = { id, hidden: false, disabled: false, textContent: '', className: '',
    listeners: {}, addEventListener(t, f) { this.listeners[t] = f; }, querySelectorAll() { return []; } });
  const log = { calls: [], contexts: [], messages: [], warnings: [], fetches: 0, links: [], els };
  class MockApp {
    constructor() { MockApp.last = this; }
    addEventListener() {}
    async connect() {}
    getHostContext() { return opts.toolInfo ? { toolInfo: opts.toolInfo } : null; }
    getHostCapabilities() { return opts.caps === undefined ? { serverTools: {} } : opts.caps; }
    async callServerTool(params, options) {
      log.calls.push({ params: JSON.parse(JSON.stringify(params)), options });
      const h = opts.tools && opts.tools[params.name];
      if (!h) throw new Error('no such tool ' + params.name);
      return h(params);
    }
    async updateModelContext(p) { log.contexts.push(p); }
    async sendMessage(p) { log.messages.push(p); }   // ui/message: must never be used
    async openLink(p) { log.links.push(p.url); }
  }
  const window = { parent: {}, addEventListener() {}, open: (u) => log.links.push('window.open:' + u),
    __extApps: { App: MockApp, PostMessageTransport: class {}, applyDocumentTheme() {},
                 applyHostStyleVariables() {}, applyHostFonts() {} } };
  const document = { getElementById: node };
  const fetch = async () => {
    log.fetches++;
    if (opts.fetchThrows) throw new TypeError('Failed to fetch');
    return { ok: true, status: 200, json: async () => opts.receipt || RECEIPT };
  };
  class FormData { constructor() { this.parts = []; } append(k, v) { this.parts.push(k); } }
  const btoa = (s) => Buffer.from(s, 'binary').toString('base64');
  const console = { warn: (m) => log.warnings.push(String(m)), log() {}, error() {} };
  const body = 'const CFG = ' + JSON.stringify(baseCfg(opts.cfg)) + ';\n' + SRC;
  await new AsyncFunction('window', 'document', 'fetch', 'FormData', 'btoa', 'console', body)(
    window, document, fetch, FormData, btoa, console);
  if (opts.input) MockApp.last.ontoolinput({ arguments: opts.input });
  if (opts.result) {
    // A card with no upload: the call's own result decides its one line.
    MockApp.last.ontoolresult(opts.result);
    for (let i = 0; i < 20; i++) await new Promise((r) => setImmediate(r));
    log.status = els.status.textContent; log.cls = els.status.className; log.text = '';
    return log;
  }
  MockApp.last.ontoolresult({ structuredContent: DESCRIPTOR });
  const file = { name: 'AGM.docx', size: 13211, arrayBuffer: async () => new ArrayBuffer(13211) };
  els.file.listeners.change({ target: { files: [file] } });
  for (let i = 0; i < 200; i++) await new Promise((r) => setImmediate(r));
  log.status = els.status.textContent; log.cls = els.status.className;
  log.text = log.contexts.map((c) => c.content[0].text).join('\n---\n');
  return log;
}

let failed = 0, passed = 0;
async function check(name, opts, assert) {
  let log;
  try { log = await run(opts); } catch (e) { console.log('FAIL ' + name + ': threw ' + e); failed++; return; }
  const problems = [];
  const expect = (cond, what) => { if (!cond) problems.push(what); };
  expect(log.messages.length === 0, 'ui/message (sendMessage) used');
  assert(log, expect);
  if (problems.length) { failed++; console.log('FAIL ' + name + ': ' + problems.join('; ') + '\n  status=' + JSON.stringify(log.status) + ' calls=' + JSON.stringify(log.calls.map((c) => c.params)) + ' text=' + JSON.stringify(log.text.slice(0, 300))); }
  else { passed++; console.log('ok   ' + name); }
}
const parseTool = { mcpParse: () => PARSE_RESULT };
const toolCalls = (log, name) => log.calls.filter((c) => c.params.name === name);

await check('upload ok: calls the tool with the substituted args, then tells the model', { tools: parseTool }, (log, expect) => {
  expect(log.fetches === 1, 'one direct POST');
  expect(log.calls.length === 1, 'exactly one tools/call');
  const c = log.calls[0];
  expect(c && c.params.name === 'mcpParse', 'tool name');
  expect(c && JSON.stringify(c.params.arguments) === JSON.stringify({ fileRef: REF, outputFormat: 'blocks' }), 'arguments substituted');
  expect(c && c.options && c.options.timeout >= 60000, 'a timeout above the 60 s default');
  expect(log.contexts.length === 1, 'one model-context update');
  expect(log.text.includes('fileRef: ' + REF), 'context names the fileRef');
  expect(log.text.includes('68 blocks · 13 headings · 4 tracked changes'), 'context carries the summary');
  expect(log.text.includes('"totalBlocks":68'), 'context carries the result');
  expect(log.contexts[0] && log.contexts[0].structuredContent.fileRef === REF, 'structured receipt');
  expect(log.status === '✓ Parsed AGM.docx · 68 blocks · 13 headings · 4 tracked changes', 'status shows the summary');
  expect(log.cls === 'ok', 'ok class');
});

await check('upload ok, result without a summary: "✓ Done"', { tools: { mcpParse: () => ({ content: [{ type: 'text', text: 'converted' }] }) } }, (log, expect) => {
  expect(log.calls.length === 1, 'one tools/call');
  expect(log.status === '✓ Done', 'status ✓ Done');
  expect(log.text.includes('converted'), 'text result in context');
});

await check('summary from a text result holding JSON', { tools: { mcpParse: () => ({ content: [{ type: 'text', text: JSON.stringify(PARSE_RESULT.structuredContent) }] }) } }, (log, expect) => {
  expect(log.status === '✓ Parsed AGM.docx · 68 blocks · 13 headings · 4 tracked changes', 'status shows the summary');
});

await check('large result: summary and fileRef only, model told to call the tool', { tools: { mcpParse: () => ({ structuredContent: { summary: { totalBlocks: 9000 }, blob: 'x'.repeat(150000) } }) } }, (log, expect) => {
  expect(log.contexts.length === 1, 'one context update');
  expect(log.text.length < 100000, 'context under 100k characters (' + log.text.length + ')');
  expect(!log.text.includes('xxxxxxxxxx'), 'result body left out');
  expect(log.text.includes('9000 blocks') && log.text.includes(REF), 'summary and fileRef kept');
  expect(log.text.includes('call mcpParse yourself'), 'model told to call the tool');
  expect(log.status === '✓ Parsed AGM.docx · 9000 blocks', 'status');
});

await check('tool error: shown to the user and told to the model', { tools: { mcpParse: () => ({ isError: true, content: [{ type: 'text', text: 'unsupported format' }] }) } }, (log, expect) => {
  expect(log.calls.length === 1, 'one tools/call');
  expect(log.cls === 'err' && log.status.includes('mcpParse failed: unsupported format'), 'error shown');
  expect(log.contexts.length === 1 && log.text.includes('failed: unsupported format') && log.text.includes('Retry by calling mcpParse'), 'model told it can retry');
  expect(log.text.includes(REF), 'model has the fileRef');
});

await check('tool call rejected (timeout/transport): shown and told', { tools: { mcpParse: () => { throw new Error('Request timed out'); } } }, (log, expect) => {
  expect(log.cls === 'err' && log.status.includes('Request timed out'), 'error shown');
  expect(log.contexts.length === 1 && log.text.includes('Request timed out'), 'model told');
});

await check('host without serverTools: no call, fileRef reported, user asked to continue', { caps: {}, tools: parseTool }, (log, expect) => {
  expect(log.calls.length === 0, 'no tools/call');
  expect(log.contexts.length === 1 && log.text.includes(REF), 'fileRef reported');
  expect(log.status === 'Uploaded AGM.docx (12.9 KB) — tell the assistant to continue.', 'status asks the user to continue');
});

await check('host without capabilities at all: same fallback', { caps: null, tools: parseTool }, (log, expect) => {
  expect(log.calls.length === 0, 'no tools/call');
  expect(log.status.endsWith('tell the assistant to continue.'), 'fallback status');
});

await check('no tool configured: the 0.1.2 behaviour', { cfg: { onUploaded: { tool: '', argsJson: '' }, afterUpload: 'processing…' }, tools: parseTool }, (log, expect) => {
  expect(log.calls.length === 0, 'no tools/call');
  expect(log.status === 'Uploaded AGM.docx (12.9 KB) — processing…', 'status');
  expect(log.text.includes('Continue the user\'s request with this fileRef.'), 'nextStep appended');
});

await check('invalid config dropped by the package: warning in the console', { cfg: { onUploaded: { tool: '', argsJson: '' }, onUploadedProblem: 'argsJson is not valid JSON' }, tools: parseTool }, (log, expect) => {
  expect(log.calls.length === 0, 'no tools/call');
  expect(log.warnings.some((w) => w.includes('argsJson is not valid JSON')), 'console warning');
});

await check('via-host fallback, then the tool', { fetchThrows: true, tools: { uploadViaHost: () => ({ structuredContent: RECEIPT }), mcpParse: () => PARSE_RESULT } }, (log, expect) => {
  expect(toolCalls(log, 'uploadViaHost').length === 1, 'via-host upload');
  expect(toolCalls(log, 'uploadViaHost')[0] && toolCalls(log, 'uploadViaHost')[0].params.arguments.ticket === 'tok_secret', 'ticket sent');
  const p = toolCalls(log, 'mcpParse');
  expect(p.length === 1 && p[0].params.arguments.fileRef === REF, 'tool called after the via-host upload');
  expect(log.text.includes('(via host)'), 'via host reported');
  expect(log.status.startsWith('✓ Parsed'), 'status');
});

// The widget re-checks the template itself (defence in depth): a bad one
// never reaches tools/call; the user sees why and the model gets the fileRef.
const badTemplates = {
  'bad JSON': '{"fileRef":"{{fileRef}}"',
  'zero placeholders': '{"fileRef":"x"}',
  'two placeholders': '{"a":"{{fileRef}}","b":"{{fileRef}}"}',
  'placeholder in a key': '{"{{fileRef}}":"x"}',
  'placeholder concatenated in a string': '{"path":"/files/{{fileRef}}"}',
  'placeholder in code-like concatenation': '{"q":"\\"+{{fileRef}}+\\""}',
  'not an object': '["{{fileRef}}"]',
  // One whole value plus a second mention: the count alone would pass these.
  'whole value plus a concatenated copy': '{"fileRef":"{{fileRef}}","path":"/files/{{fileRef}}"}',
  'whole value plus a placeholder key': '{"{{fileRef}}":"{{fileRef}}"}',
};
for (const [what, tpl] of Object.entries(badTemplates)) {
  await check('template refused in the widget: ' + what, { cfg: { onUploaded: { tool: 'mcpParse', argsJson: tpl } }, tools: parseTool }, (log, expect) => {
    expect(toolCalls(log, 'mcpParse').length === 0, 'no tools/call');
    expect(log.cls === 'err' && log.status.includes('mcpParse failed'), 'error shown');
    expect(log.contexts.length === 1 && log.text.includes(REF), 'model told, with the fileRef');
  });
}

await check('a nested template is filled in place', { tools: parseTool,
  cfg: { onUploaded: { tool: 'mcpParse', argsJson: '{"opts":{"files":["{{fileRef}}"]},"n":2}' } } }, (log, expect) => {
  const a = log.calls[0] && log.calls[0].params.arguments;
  expect(a && a.opts.files[0] === REF && a.n === 2 && Object.keys(a).length === 2, 'nested template filled');
});

// A hostile receipt value is data: it lands as one string, never as JSON or code.
const HOSTILE = 'x","outputFormat":"html","y":"';
await check('a fileRef with JSON metacharacters stays one string value', { tools: parseTool,
  receipt: Object.assign({}, RECEIPT, { fileRef: HOSTILE }) }, (log, expect) => {
  const a = log.calls[0] && log.calls[0].params.arguments;
  expect(a && a.fileRef === HOSTILE && a.outputFormat === 'blocks' && Object.keys(a).length === 2, 'fileRef substituted as a value');
});

// ---------- result-only cards (0.1.3): one line from the call's own result ----------
const PARSED = { structuredContent: { document: { format: 'docx', filename: '/tmp/ailang-upload-1/AGM report.docx',
  blocks: [{ type: 'text' }, { type: 'comment' }, { type: 'section', children: [{ type: 'comment' }, { type: 'text' }] }],
  summary: { totalBlocks: 68, headings: 13, tables: 2, images: 0, changes: 4 } } } };
const CONVERT_INFO = { tool: { name: 'mcpConvert', title: 'Convert' } };
const LINK_CAPS = { serverTools: {}, openLinks: {} };

await check('result card: parse summary with filename, counts and comments', { input: { fileRef: REF }, result: PARSED }, (log, expect) => {
  expect(log.status === '✓ Parsed AGM report.docx · 68 blocks · 13 headings · 2 tables · 4 tracked changes · 2 comments', 'one-liner');
  expect(log.cls === 'quiet', 'quiet class');
  expect(log.calls.length === 0 && log.contexts.length === 0, 'a result card calls nothing and tells nothing');
});

await check('result card: a Windows path keeps only the file name', { result: { structuredContent: { filename: 'C:\\Users\\m\\Q3.docx', summary: { totalBlocks: 5 } } } }, (log, expect) => {
  expect(log.status === '✓ Parsed Q3.docx · 5 blocks', 'basename');
});

await check('result card: error object', { input: { fileRef: REF }, result: { structuredContent: { error: { code: 'INVALID_FORMAT', message: 'not a docx\nsee docs' } } } }, (log, expect) => {
  expect(log.status === '✗ INVALID_FORMAT: not a docx see docs', 'error line');
  expect(log.cls === 'err', 'err class');
});

await check('result card: mcp_files error shape', { result: { isError: true, content: [{ type: 'text', text: JSON.stringify({ error: 'token_used', error_description: 'this upload token was already used — call createUpload again for each file', status: 409 }) }] } }, (log, expect) => {
  expect(log.status.startsWith('✗ token_used: this upload token was already used'), 'error line');
});

await check('result card: isError text only', { result: { isError: true, content: [{ type: 'text', text: 'quota exceeded' }] } }, (log, expect) => {
  expect(log.status === '✗ quota exceeded', 'error line');
});

await check('result card: convert, titled, with an https download', { caps: LINK_CAPS, toolInfo: CONVERT_INFO,
  result: { structuredContent: { filename: 'out/report.pdf', target: 'pdf', download_url: 'https://dl.example/d/1' } } }, (log, expect) => {
  expect(log.status === '✓ Convert done · report.pdf', 'one-liner');
  expect(log.els.dl && log.els.dl.hidden === false, 'download button shown');
});

await check('result card: the download opens through the host', { caps: LINK_CAPS, toolInfo: CONVERT_INFO,
  result: { structuredContent: { target: 'pdf', download_url: 'https://dl.example/d/1' } } }, (log, expect) => {
  log.els.dl.listeners.click();
  expect(log.links.length === 1 && log.links[0] === 'https://dl.example/d/1', 'app.openLink with the url: ' + JSON.stringify(log.links));
  expect(log.status === '✓ Convert done · pdf', 'target when no filename');
});

await check('result card: an http download_url is not offered', { toolInfo: CONVERT_INFO,
  result: { structuredContent: { filename: 'r.pdf', download_url: 'http://dl.example/d/1' } } }, (log, expect) => {
  expect(!log.els.dl || log.els.dl.hidden !== false, 'no download button');
  expect(log.status === '✓ Convert done · r.pdf', 'one-liner');
});

await check('result card: a long line is cut at 120 characters', { result: { structuredContent: { filename: 'x'.repeat(70) + '.docx',
  summary: { totalBlocks: 123456, headings: 23456, tables: 3456, images: 456, changes: 56789, comments: 678 } } } }, (log, expect) => {
  expect(log.status.length <= 120 && log.status.endsWith('…'), 'clipped (' + log.status.length + ')');
});

await check('result card: resultSummary off keeps the bare "Done."', { cfg: { resultSummary: false }, input: { fileRef: REF }, result: PARSED }, (log, expect) => {
  expect(log.status === 'Done.', 'bare Done.');
});

await check('result card: nothing to read and no title: "Done."', { input: { fileRef: REF }, result: { content: [{ type: 'text', text: 'ok' }] } }, (log, expect) => {
  expect(log.status === 'Done.', 'fallback');
});

console.log(`widget simulation: ${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
