// sunholo/mcp_files upload widget logic. Inlined by widget.uploadWidgetHtml
// as a module script after the ext-apps client (window.__extApps), with
// `const CFG = {...}` (widget.configJson) in front of it.
// Edit THIS file, then run tools/gen_bundle.sh to regenerate widget_assets.ail.
// Rules: report with updateModelContext only (never the host message request:
// it drafts a user message under a caution banner); DOM via textContent only.
//
// States: the page starts blank (no picker). A tool result holding an upload
// descriptor shows the picker; any other result shows one quiet line and no
// picker ("No upload needed", or "Done." when this tool call was given a
// fileRef). After an upload: "Uploaded <name> (<size>) - <CFG.afterUpload>".
// ext-apps 2.0.3 delivers tool-result only for the call this widget is
// attached to, so the later tool call that uses the file cannot update this
// instance; that call renders its own instance, which says "Done.".
const el = (id) => document.getElementById(id);
const picker = el('file');
const ready = el('ready');
function say(m, cls) { const s = el('status'); s.textContent = m; s.className = cls || ''; }
let app = null, desc = null, busy = false, spent = false, settled = false, gotRef = false;

function asDescriptor(v) {
  if (!v || typeof v !== 'object') return null;
  if (v.upload && v.upload.multipart && v.upload.multipart.fields) return v;
  if (v.descriptor && v.descriptor.upload) return asDescriptor(v.descriptor);
  return null;
}
function fromToolResult(r) {
  if (!r) return null;
  const d = asDescriptor(r.structuredContent);
  if (d) return d;
  for (const c of (r.content || [])) {
    if (c && c.type === 'text') { try { const t = asDescriptor(JSON.parse(c.text)); if (t) return t; } catch (e) {} }
  }
  return null;
}
// Did this tool call carry a fileRef (an earlier upload being used)?
function hasFileRef(args) {
  for (const k of Object.keys(args || {})) {
    const v = args[k];
    if (typeof v === 'string' && v.indexOf('mcp-file://') === 0) return true;
  }
  return false;
}
function useDescriptor(d) {
  if (desc) return;
  desc = d; settled = true;
  ready.hidden = false; picker.disabled = false;
  say('Choose a file to upload.');
}
// A result without a descriptor: nothing to upload here, so no picker.
function idle(isError) {
  if (settled) return;
  settled = true;
  ready.hidden = true;
  say(gotRef && !isError ? 'Done.' : 'No upload needed.', 'quiet');
}
function onResult(r) {
  const d = fromToolResult(r);
  if (d) useDescriptor(d); else idle(!!(r && r.isError));
}
function uploadUrl() { return (desc && desc.upload && desc.upload.url) || CFG.uploadUrl; }
function isReceipt(b) { return !!b && typeof b.fileRef === 'string' && b.fileRef !== ''; }
function size(n) {
  if (n < 1024) return n + ' bytes';
  if (n < 1048576) return (n / 1024).toFixed(1) + ' KB';
  return (n / 1048576).toFixed(1) + ' MB';
}

async function direct(f) {
  const mp = desc.upload.multipart;
  const fd = new FormData();
  for (const k of Object.keys(mp.fields || {})) fd.append(k, mp.fields[k]);
  fd.append(mp.fileField || 'file', f, f.name);
  const resp = await fetch(uploadUrl(), { method: 'POST', body: fd });
  let body = null;
  try { body = await resp.json(); } catch (e) {}
  return { ok: resp.ok && isReceipt(body), body: body, status: resp.status };
}

// The widget-only tool takes the upload token as `ticket`: a tool parameter
// named token reads as a credential to MCP scanners.
async function viaHost(f) {
  const buf = new Uint8Array(await f.arrayBuffer());
  let bin = '';
  for (let i = 0; i < buf.length; i += 0x8000) bin += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
  const r = await app.callServerTool({ name: CFG.hostToolName,
    arguments: { ticket: desc.upload.multipart.fields.token, filename: f.name, base64: btoa(bin) } });
  let body = (r && r.structuredContent) || null;
  if (!isReceipt(body)) {
    for (const c of ((r && r.content) || [])) {
      if (c && c.type === 'text') { try { body = JSON.parse(c.text); } catch (e) {} }
    }
  }
  return { ok: !(r && r.isError) && isReceipt(body), body: body, status: 0 };
}

async function report(rc, via) {
  const text = 'The user uploaded ' + rc.name + ' (' + rc.sizeBytes + ' bytes, sha256 ' + rc.sha256 +
    ') with the upload widget (' + via + '). fileRef: ' + rc.fileRef + '. ' + CFG.nextStep;
  ready.hidden = true;
  try {
    await app.updateModelContext({ content: [{ type: 'text', text: text }], structuredContent: rc });
    say('Uploaded ' + rc.name + ' (' + size(rc.sizeBytes) + ') — ' + CFG.afterUpload, 'ok');
  } catch (e) {
    say('Uploaded ' + rc.name + ', but the assistant could not be told. Tell it: fileRef ' + rc.fileRef, 'err');
  }
}

async function upload(f) {
  if (busy || spent || !desc) return;
  if (f.size === 0) { say('That file is empty.', 'err'); return; }
  if (desc.maxBytes && f.size > desc.maxBytes) {
    say(f.name + ' is ' + f.size + ' bytes; this upload allows at most ' + desc.maxBytes + '.', 'err'); return;
  }
  busy = true; picker.disabled = true; say('Uploading ' + f.name + ' (' + size(f.size) + ')…');
  let res = null, via = 'direct';
  try {
    res = await direct(f);
    spent = true;
  } catch (e) {
    if (app && CFG.hostToolName && f.size <= CFG.maxViaHostBytes) {
      via = 'via host';
      try { res = await viaHost(f); spent = true; }
      catch (e2) { res = { ok: false, body: { error_description: 'the host could not deliver the file: ' + e2 } }; }
    } else {
      res = { ok: false, body: { error_description: 'this window cannot reach ' + uploadUrl() + ' (' + e + ')' +
        (f.size > CFG.maxViaHostBytes ? ', and the file is too large to send through the host' : '') } };
    }
  }
  if (res.ok) await report(res.body, via);
  else say('Upload failed: ' + ((res.body && (res.body.error_description || res.body.error)) || ('HTTP ' + res.status)) +
    (spent ? '. Ask the assistant for a new upload.' : ''), 'err');
  busy = false;
  picker.disabled = spent;
}

picker.addEventListener('change', (ev) => { const f = ev.target.files && ev.target.files[0]; if (f) upload(f); });

try {
  const { App, PostMessageTransport } = window.__extApps;
  app = new App({ name: 'sunholo-mcp-files', version: '0.1.1' }, {});
  app.ontoolinput = (p) => { gotRef = hasFileRef(p && p.arguments); };
  app.ontoolresult = onResult;
  app.ontoolcancelled = () => idle(true);
  await app.connect(new PostMessageTransport(window.parent, window.parent));
} catch (e) {
  say('Could not connect to the host: ' + e, 'err');
}
// ChatGPT (Apps SDK) also exposes the result as window.openai.toolOutput.
if (!settled && window.openai && window.openai.toolOutput) {
  gotRef = hasFileRef(window.openai.toolInput);
  const d = asDescriptor(window.openai.toolOutput);
  if (d) useDescriptor(d); else idle(false);
}
