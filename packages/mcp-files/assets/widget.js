// sunholo/mcp_files upload widget logic. Inlined by widget.uploadWidgetHtml
// as a module script after the ext-apps client (window.__extApps), with
// `const CFG = {...}` (widget.configJson) in front of it.
// Edit THIS file, then run tools/gen_bundle.sh to regenerate widget_assets.ail.
// Rules: report with updateModelContext only (never the host message request:
// it drafts a user message under a caution banner); DOM via textContent only.
const el = (id) => document.getElementById(id);
const picker = el('file');
function say(m, cls) { const s = el('status'); s.textContent = m; s.className = cls || ''; }
let app = null, desc = null, pending = null, busy = false, spent = false;

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
function useDescriptor(d) {
  if (!d || desc) return;
  desc = d;
  if (pending) { const f = pending; pending = null; upload(f); }
  else say('Choose a file to upload.');
}
function uploadUrl() { return (desc && desc.upload && desc.upload.url) || CFG.uploadUrl; }
function isReceipt(b) { return !!b && typeof b.fileRef === 'string' && b.fileRef !== ''; }

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

async function viaHost(f) {
  const buf = new Uint8Array(await f.arrayBuffer());
  let bin = '';
  for (let i = 0; i < buf.length; i += 0x8000) bin += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
  const r = await app.callServerTool({ name: CFG.hostToolName,
    arguments: { token: desc.upload.multipart.fields.token, filename: f.name, base64: btoa(bin) } });
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
  try {
    await app.updateModelContext({ content: [{ type: 'text', text: text }], structuredContent: rc });
    say('Uploaded ' + rc.name + ' (' + rc.sizeBytes + ' bytes). The assistant has the file reference.', 'ok');
  } catch (e) {
    say('Uploaded ' + rc.name + ', but the assistant could not be told. Tell it: fileRef ' + rc.fileRef, 'err');
  }
}

async function upload(f) {
  if (busy || spent) return;
  if (!desc) { pending = f; say('Waiting for the upload token from the tool result...'); return; }
  if (f.size === 0) { say('That file is empty.', 'err'); return; }
  if (desc.maxBytes && f.size > desc.maxBytes) {
    say(f.name + ' is ' + f.size + ' bytes; this upload allows at most ' + desc.maxBytes + '.', 'err'); return;
  }
  busy = true; picker.disabled = true; say('Uploading ' + f.name + '...');
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
  app = new App({ name: 'sunholo-mcp-files', version: '0.1.0' }, {});
  app.ontoolresult = (r) => useDescriptor(fromToolResult(r));
  await app.connect(new PostMessageTransport(window.parent, window.parent));
} catch (e) {
  say('Could not connect to the host: ' + e, 'err');
}
if (!desc && window.openai && window.openai.toolOutput) useDescriptor(asDescriptor(window.openai.toolOutput));
