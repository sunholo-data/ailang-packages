const $=id=>document.getElementById(id), names=['Drums','Bass','Harmony','Texture'];
let state=null,ctx=null,program=null,captureNode=null,source=null,stream=null,sink=null,worker=null,ready=null;
let captureId=0,activeCaptureId=null;
let selected=1,token=0,held=false,capturing=false,preparing=false,takeTrack=1,queue=Promise.resolve(),queued=0,sequence=0;
let bridgeTimes=[],events=[],lastMeter={frame:0,peak:0,clipped:0,blocks:0},preparationMs=0,activationErrors=[],workerJob=0,stopping=false;
const rows=[];
function notice(message) { $('notice').textContent=message; }
function log(message) { events=[message,...events].slice(0,24); $('events').textContent=events.join('\n'); }
function currentFrame() { return ctx?Math.ceil(ctx.currentTime*ctx.sampleRate):0; }
async function api(path,body) {
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),4000);
  try {
    const r=await fetch(path,body?{method:'POST',headers:{'Content-Type':'application/json','X-Loop-Lab':'1'},body:JSON.stringify(body),signal:controller.signal}:{signal:controller.signal});
    const data=await r.json(); if(!r.ok && !data.state) throw new Error(data.error||'Local bridge unavailable'); return data;
  } finally { clearTimeout(timer); }
}
function command(kind,extra={}) {
  if(queued>=16) return Promise.reject(new Error('Control queue full'));
  const sessionToken=token; queued++;
  const task=queue.then(async()=> {
    if(sessionToken!==token) throw new Error('Session changed');
    const response=await api('/api/command',{command:{id:`c-${++sequence}-${crypto.randomUUID()}`,kind,epoch:state.epoch,expected:state.revision,now:currentFrame(),...extra}});
    if(sessionToken!==token) throw new Error('Session changed');
    if(response.state) state=response.state;
    if(response.bridgeMs) bridgeTimes=[...bridgeTimes,response.bridgeMs].slice(-128);
    render(); if(!response.ok) throw new Error(response.error); return response.state;
  });
  queue=task.catch(()=>{}).finally(()=>queued--); return task;
}
function stats(values) {
  if(!values.length) return 'No samples'; const sorted=[...values].sort((a,b)=>a-b);
  return `n=${sorted.length} · median ${sorted[Math.floor(sorted.length/2)].toFixed(1)} ms · p95 ${sorted[Math.ceil(sorted.length*.95)-1].toFixed(1)} ms`;
}
function render() {
  if(!state) return;
  for(let i=0;i<4;i++) {
    const t=state.tracks[i],r=rows[i]; r.row.classList.toggle('selected',selected===t.id);
    r.select.setAttribute('aria-pressed',String(selected===t.id)); r.level.value=t.level; r.pan.value=t.pan;
    r.mute.textContent=t.muted?'Unmute':'Mute'; r.mute.classList.toggle('muted-on',t.muted);
    r.revision.textContent=t.pending?(t.pending.scheduled?'Scheduled for next loop':'Prepared · staging'):`${t.revision?'Take':'Original'} · active r${t.revision}`;
    for(const control of [r.level,r.pan,r.mute]) control.disabled=!ctx || !state.running || stopping;
  }
  $('capture-title').textContent=`A new part for ${names[selected-1]}`;
  $('start').disabled=!!ctx || stopping || state.running;
  $('stop').disabled=(!ctx&&!state.running) || stopping;
  $('capture').disabled=!ctx || !state.running || ctx.state!=='running' || !!ready || preparing || stopping || !!state.tracks[selected-1].pending;
  $('commit').disabled=!ready || stopping || !ctx || ctx.state!=='running' || !!state.tracks[ready?.track-1]?.pending;
  $('discard').disabled=!ready;
  $('input').disabled=capturing || held || preparing;
  $('capture').classList.toggle('recording',capturing);
  $('transport-state').textContent=ctx?(ctx.state==='running'?'Playing':'Audio suspended'):state.running?'Reset required':'Stopped';
  $('bridge').textContent=`Strict bytecode CLI · no fallback\n${stats(bridgeTimes)}\nPreparation worker: ${preparationMs.toFixed(1)} ms\nQueued controls: ${queued}`;
}
function buildTracks() {
  names.forEach((name,i)=> {
    const row=document.createElement('article'); row.className='lane';
    const select=document.createElement('button'); select.className='track-select';
    const number=document.createElement('span');number.className='track-number';number.textContent=`0${i+1}`;
    const title=document.createElement('strong');title.textContent=name;
    const subtitle=document.createElement('small');subtitle.textContent=['Pulse & percussion','Low phrase','Three-note bed','Air & motion'][i];
    select.append(number,title,subtitle); select.onclick=()=>{selected=i+1;render();};
    const phrase=document.createElement('div');phrase.className='phrase';phrase.setAttribute('aria-hidden','true');
    for(let n=0;n<32;n++) { const bar=document.createElement('i');bar.style.height=`${i===0?(n%4===0?90:18):i===1?(n%8<5?45+(n%3)*12:8):i===2?40+Math.round(Math.sin(n/3)*15):12+((n*17)%42)}%`;phrase.append(bar); }
    const controls=document.createElement('div');controls.className='track-controls';
    const makeSlider=(text,min,max,label)=> {
      const wrapper=document.createElement('label');wrapper.textContent=text;
      const input=document.createElement('input');input.type='range';input.min=min;input.max=max;input.step=1;input.setAttribute('aria-label',`${name} ${label}`);wrapper.append(input);controls.append(wrapper);return input;
    };
    const level=makeSlider('Level',0,100,'level'),pan=makeSlider('Pan',-100,100,'pan');
    const mute=document.createElement('button');mute.setAttribute('aria-label',`${name} mute`);controls.append(mute);
    const revision=document.createElement('span');revision.className='revision';controls.append(revision);
    const update=()=> command('parameter',{track:i+1,level:Number(level.value),pan:Number(pan.value),muted:state.tracks[i].muted}).then(sendParams).catch(e=>notice(e.message));
    level.onchange=update;pan.onchange=update;
    mute.onclick=()=>command('parameter',{track:i+1,level:state.tracks[i].level,pan:state.tracks[i].pan,muted:!state.tracks[i].muted}).then(sendParams).catch(e=>notice(e.message));
    row.append(select,phrase,controls);$('tracks').append(row); rows.push({row,select,level,pan,mute,revision});
  });
}
function sendParams() { if(program) for(const t of state.tracks) program.port.postMessage({type:'parameter',epoch:state.epoch,track:t.id,level:t.level,pan:t.pan,muted:t.muted}); }
async function start() {
  const sessionToken=++token; ready=null; $('start').disabled=true; notice('Loading the four original phrases…');
  try {
    ctx=new AudioContext({latencyHint:'interactive'}); await ctx.resume();
    ctx.onstatechange=()=> { if(ctx?.state!=='running') cancelCapture('Capture cancelled: audio suspended'); render(); };
    const audio=ctx;
    await Promise.all([audio.audioWorklet.addModule('/program-worklet.mjs'),audio.audioWorklet.addModule('/capture-worklet.mjs')]);
    const samples=await Promise.all(names.map(async(_,i)=> {
      const response=await fetch(`/audio/demo-${i+1}.wav`),buffer=await audio.decodeAudioData(await response.arrayBuffer());
      return new Float32Array(buffer.getChannelData(0));
    }));
    if(sessionToken!==token) return;
    const now=currentFrame(),origin=now+audio.sampleRate;
    await command('configure',{rate:audio.sampleRate,bpm:120,origin,now});
    program=new AudioWorkletNode(audio,'loop-program',{numberOfInputs:0,outputChannelCount:[2]});program.connect(audio.destination);
    program.port.onmessage=e=>programMessage(e.data,sessionToken);
    program.port.postMessage({type:'init',epoch:state.epoch,origin,rate:audio.sampleRate,bpm:120,tracks:state.tracks.map((t,i)=>({...t,samples:samples[i]}))},samples.map(x=>x.buffer));
    captureNode=new AudioWorkletNode(audio,'private-capture',{numberOfInputs:1,outputChannelCount:[1]});
    sink=audio.createGain();sink.gain.value=0;captureNode.connect(sink).connect(audio.destination);
    captureNode.port.onmessage=e=>captureMessage(e.data,sessionToken);
    worker=new Worker('/prepare-worker.mjs',{type:'module'});worker.onmessage=e=>preparedMessage(e.data,sessionToken);
    worker.onerror=()=>{ready=null;preparing=false;render();notice('Preparation worker failed; reset and retry');};
    render();notice('Four parts playing. Select a part, then hold to capture privately.');
    log(`Transport epoch ${state.epoch} · origin frame ${origin} · ${audio.sampleRate} Hz`);
  } catch(error) { notice(error.message); await stop(false); }
}
function programMessage(m,sessionToken) {
  if(sessionToken!==token) return;
  if(m.type==='meter') { lastMeter=m; return; }
  if(m.type==='initialized') {log(`Audio initialized at frame ${m.frame}`);return;}
  const t=state.tracks[m.track-1];
  if(m.type==='rejected') {
    log(`Host rejected: ${m.reason}`);notice(`Current audio retained: ${m.reason}`);
    if(t?.pending&&!t.pending.scheduled) command('cancel',{track:t.id,base:t.revision,pendingId:t.pending.id}).catch(e=>notice(e.message));
    if(!t) stop(false);return;
  }
  if(m.epoch!==state.epoch || !t?.pending || m.id!==t.pending.id) {log('Ignored stale host acknowledgement');return;}
  if(m.type==='scheduled') {
    log(`Part ${m.track} staged at frame ${m.frame}; target ${m.at}`);
    command('schedule',{track:m.track,base:t.revision,pendingId:m.id,at:m.at,now:m.frame}).catch(error=>{notice(`Schedule acknowledgement failed: ${error.message}. Reset required.`);stop(false);});
  } else if(m.type==='activated') {
    activationErrors.push(m.applied-m.at); activationErrors=activationErrors.slice(-128);
    log(`Part ${m.track} activated · planned ${m.at} / applied ${m.applied} / error ${m.applied-m.at} frames`);
    command('activate',{track:m.track,base:t.revision,pendingId:m.id,at:m.at,applied:m.applied}).then(()=>notice(`${names[m.track-1]}: committed take is now active.`)).catch(error=>{notice(`Activation acknowledgement failed: ${error.message}. Reset required.`);stop(false);});
  }
}
function releaseSource() { if(source) { try{source.disconnect();source.stop?.();}catch{} source=null; } if(stream){for(const t of stream.getTracks())t.stop();stream=null;} }
function cancelCapture(message='Capture discarded') { held=false;capturing=false;preparing=false;activeCaptureId=null;workerJob++;captureNode?.port.postMessage({type:'cancel'});releaseSource();$('capture-status').textContent=message;render(); }
async function beginCapture() {
  if(!ctx || capturing || ready || held || preparing || state.tracks[selected-1].pending) return;
  held=true;activeCaptureId=++captureId;takeTrack=selected;const sessionToken=token;
  $('capture-status').textContent='Opening private input…';render();
  try {
    if($('input').value==='microphone') {
      const media=await navigator.mediaDevices.getUserMedia({audio:{channelCount:1,echoCancellation:false,noiseSuppression:false,autoGainControl:false}});
      if(!held || sessionToken!==token) {media.getTracks().forEach(t=>t.stop());return;}
      stream=media; source=ctx.createMediaStreamSource(media);
      for(const track of media.getTracks()) track.onended=()=>cancelCapture('Input disconnected · take discarded');
    } else { source=ctx.createOscillator();source.frequency.value=220;source.type='sine'; }
    if(!held || sessionToken!==token) {releaseSource();return;}
    captureNode.port.postMessage({type:'start',id:activeCaptureId,frames:ctx.sampleRate*16});source.connect(captureNode);source.start?.();capturing=true;
    $('capture-status').textContent=`Recording privately for ${names[takeTrack-1]}…`;render();
  } catch(error) { cancelCapture('Input unavailable');notice(error.message); }
}
function finishCapture() {
  const wasCapturing=capturing;held=false;capturing=false;
  if(wasCapturing) {preparing=true;captureNode.port.postMessage({type:'stop'});releaseSource();$('capture-status').textContent='Preparing privately…';}
  render();
}
function captureMessage(m,sessionToken) {
  if(sessionToken!==token)return;
  if(m.type==='capture-meter') { if(capturing)drawMeter(m.peak);return; }
  if(m.type==='take') {
    if(m.id!==activeCaptureId)return;activeCaptureId=null;
    held=false;capturing=false;releaseSource();
    if(m.used<ctx.sampleRate*.1) {preparing=false;notice('Take too short. Hold for at least a tenth of a second.');render();return;}
    preparing=true;const input=m.samples.subarray(0,m.used);workerJob++;
    // Transfer the fixed capture buffer once. The worker sees only used frames.
    worker.postMessage({id:workerJob,samples:input,rate:m.rate,frames:ctx.sampleRate*8},[input.buffer]);
    $('capture-status').textContent='Preparing privately…';render();
  }
}
function preparedMessage(m,sessionToken) {
  if(sessionToken!==token || m.id!==workerJob)return;
  preparing=false;
  if(m.error) {notice(m.error);render();return;}
  ready={track:takeTrack,samples:m.samples,hash:m.hash};preparationMs=m.prepareMs;
  drawWave(m.samples);$('capture-status').textContent=`Ready for ${names[takeTrack-1]} · still private`;notice('Prepared in memory. Commit when you want this take to join the loop.');render();
}
async function commit() {
  if(!ready || !ctx) return;
  const take=ready;ready=null;render();$('capture-status').textContent='Planning the next loop…';
  try {
    const t=state.tracks[take.track-1];
    await command('prepare',{track:t.id,base:t.revision,asset:`take-${crypto.randomUUID()}`,hash:take.hash,ready:currentFrame()});
    const p=state.tracks[t.id-1].pending;
    program.port.postMessage({type:'stage',epoch:state.epoch,track:t.id,base:t.revision,revision:p.revision,id:p.id,at:p.at,samples:take.samples},[take.samples.buffer]);
    $('capture-status').textContent='Committed · waiting for the loop';notice(`${names[t.id-1]} will change at the next planned loop boundary.`);drawWave(null);
  } catch(error) {notice(`Current part retained: ${error.message}`);$('capture-status').textContent='Commit failed · capture again';}
  render();
}
async function stop(clearNotice=true) {
  if(stopping)return;stopping=true;token++;workerJob++;ready=null;preparing=false;cancelCapture('Take discarded');
  worker?.terminate();worker=null;captureNode?.disconnect();captureNode=null;sink?.disconnect();sink=null;program?.disconnect();program=null;
  const old=ctx;ctx=null;if(old){old.onstatechange=null;await old.close();}
  await queue;
  try {state=(await api('/api/state')).state;await command('reset',{now:0});}catch(error){notice(`Reset failed: ${error.message}. Reload when bridge is available.`);}
  stopping=false;lastMeter={frame:0,peak:0,blocks:0,clipped:0};drawWave(null);render();
  if(clearNotice)notice('Stopped. Private takes, pending changes and active recordings cleared.');
}
function drawWave(xs) {
  const canvas=$('wave'),g=canvas.getContext('2d');g.clearRect(0,0,canvas.width,canvas.height);g.strokeStyle='#dce3e8';g.beginPath();g.moveTo(0,55);g.lineTo(600,55);g.stroke();
  if(!xs)return;g.strokeStyle='#314352';g.beginPath();for(let x=0;x<600;x++){let peak=0;const from=Math.floor(x*xs.length/600),to=Math.floor((x+1)*xs.length/600);for(let i=from;i<to;i++)peak=Math.max(peak,Math.abs(xs[i]));g.moveTo(x,55-peak*50);g.lineTo(x,55+peak*50);}g.stroke();
}
function drawMeter(peak) {drawWave(null);const g=$('wave').getContext('2d');g.fillStyle='#bd3012';g.fillRect(0,48,600*peak,14);}
function tick() {
  if(ctx&&state?.running) {
    const frame=currentFrame(),phase=Math.max(0,frame-state.origin)%(ctx.sampleRate*8);
    $('bar').textContent=`${Math.floor(phase/(ctx.sampleRate*2))+1} / 4`;$('playhead').style.width=`${phase/(ctx.sampleRate*8)*100}%`;
    $('timing').textContent=`${ctx.sampleRate} Hz · ${ctx.state}\nRender frame: ${lastMeter.frame}\nReported base latency: ${(ctx.baseLatency*1000).toFixed(2)} ms\nReported output latency: ${((ctx.outputLatency||0)*1000).toFixed(2)} ms\nHandoffs: ${activationErrors.length} · errors [${activationErrors.join(', ')}] frames\nClamped frames: ${lastMeter.clipped} · render blocks: ${lastMeter.blocks}`;
  } else {$('bar').textContent='— / 4';$('playhead').style.width='0%';}
  $('master-meter').value=lastMeter.peak;$('master-text').textContent=lastMeter.peak>0?`${(20*Math.log10(lastMeter.peak)).toFixed(1)} dBFS`:'Silent';
  requestAnimationFrame(tick);
}
$('start').onclick=start;$('stop').onclick=()=>stop();$('commit').onclick=commit;
$('discard').onclick=()=>{ready=null;workerJob++;drawWave(null);$('capture-status').textContent='Take discarded';render();};
$('capture').onpointerdown=e=>{e.preventDefault();$('capture').setPointerCapture(e.pointerId);beginCapture();};
$('capture').onpointerup=finishCapture;$('capture').onpointercancel=()=>cancelCapture();
$('capture').onkeydown=e=>{if((e.key===' '||e.key==='Enter')&&!e.repeat){e.preventDefault();beginCapture();}};
$('capture').onkeyup=e=>{if(e.key===' '||e.key==='Enter'){e.preventDefault();finishCapture();}};
window.addEventListener('blur',()=>{if(held||capturing)cancelCapture('Focus lost · take discarded');});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&(held||capturing))cancelCapture('Page hidden · take discarded');});
window.addEventListener('pagehide',()=>{releaseSource();worker?.terminate();ctx?.close();});
$('benchmark').onclick=async()=> {
  const button=$('benchmark');button.disabled=true;
  try {
    // Read-only planner init probe; no mutation to the live session.
    const w=new Worker('/benchmark-worker.mjs',{type:'module'});
    const timer=setTimeout(()=>{w.terminate();button.disabled=false;notice('Benchmark timed out');},20000);
    w.onmessage=e=>{clearTimeout(timer);w.terminate();button.disabled=false;$('bridge').textContent+=`\n${e.data.label}: ${e.data.summary||e.data.error}`;};
    w.postMessage({mode:'native'});
  }catch(error){button.disabled=false;notice(error.message);}
};
$('wasm').onclick=async()=> {
  const button=$('wasm');button.disabled=true;
  const w=new Worker('/benchmark-worker.mjs',{type:'module'}),timer=setTimeout(()=>{w.terminate();button.disabled=false;notice('WASM benchmark timed out; native bridge remains active.');},20000);
  w.onmessage=e=>{clearTimeout(timer);w.terminate();button.disabled=false;$('bridge').textContent+=`\n${e.data.label}: ${e.data.summary||e.data.error}`;};w.postMessage({mode:'wasm'});
};
buildTracks();drawWave(null);tick();
try {state=(await api('/api/state')).state;render();} catch(error){notice(`Start the local server: ${error.message}`);}
