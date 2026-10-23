// Actual application module + real strict AILANG planner, with in-memory DOM,
// device and render-clock fakes. This is not a real microphone/browser test.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {prepareJob} from '../static/prepare-worker.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
class Element {
  constructor(){this.value=0;this.textContent='';this.style={};this.children=[];this.classList={toggle(){}};}
  append(...items){this.children.push(...items);}setAttribute(){}setPointerCapture(){}
  click(){this.clicked=true;}remove(){}
  getContext(){return {clearRect(){},beginPath(){},moveTo(){},lineTo(){},stroke(){},fillRect(){}};}
}
const stream=()=>({track:{readyState:'live',onended:null,stop(){this.readyState='ended';}},getTracks(){return [this.track];}});
const settle=async(predicate)=>{const start=Date.now();while(!predicate()){assert.ok(Date.now()-start<3000,'application flow timeout');await new Promise(r=>setTimeout(r,1));}};

test('instrument permission → private capture → real-planner activation → hide/reset owns the right input',async()=> {
  const temp=mkdtempSync(path.join(tmpdir(),'loop-instrument-')),args=path.join(temp,'arg.json');
  const invoke=payload=>{
    writeFileSync(args,JSON.stringify(JSON.stringify(payload)));
    const p=spawnSync('ailang',['run','--strict-bytecode','--entry','handle','--args-file',args,'--package-dir',root,path.join(root,'planner.ail')],{cwd:root,encoding:'utf8',timeout:10000});
    assert.equal(p.status,0,p.stderr);return JSON.parse(p.stdout);
  };
  let backend=invoke({schema:1,op:'init'}).state;
  const nodes={},elements={},documentEvents={},windowEvents={},mediaEvents={},streams=[],workers=[];
  let pendingPermission=null,context,holdWorkerReply=false,deferredWorkerReply=null;
  for(const match of readFileSync(path.join(root,'static/index.html'),'utf8').matchAll(/id="([^"]+)"/g))elements[match[1]]=new Element();
  elements.input.value='synthetic';elements['level-mode'].value='peak-safe';elements.wave.width=600;elements.wave.height=110;
  globalThis.document={hidden:false,body:new Element(),getElementById:id=>{assert.ok(elements[id],id);return elements[id];},createElement:()=>new Element(),addEventListener:(type,fn)=>documentEvents[type]=fn};
  const blobs=[],revoked=[],originalCreate=URL.createObjectURL,originalRevoke=URL.revokeObjectURL;
  URL.createObjectURL=blob=>{blobs.push(blob);return `blob:test-${blobs.length}`;};URL.revokeObjectURL=url=>revoked.push(url);
  globalThis.window={addEventListener:(type,fn)=>windowEvents[type]=fn};globalThis.requestAnimationFrame=()=>0;
  Object.defineProperty(globalThis,'navigator',{configurable:true,value:{userAgent:'node-fake-browser',mediaDevices:{addEventListener:(type,fn)=>mediaEvents[type]=fn,getUserMedia:async()=>{
    if(pendingPermission)return pendingPermission.promise;const m=stream();streams.push(m);return m;
  }}}});
  globalThis.fetch=async(url,options)=> {
    if(url==='/api/state')return {ok:true,json:async()=>({state:structuredClone(backend)})};
    if(url==='/api/command') {
      const r=invoke({schema:1,state:backend,command:JSON.parse(options.body).command});if(r.ok)backend=r.state;
      return {ok:r.ok,json:async()=>({...r,state:structuredClone(backend),bridgeMs:1})};
    }
    assert.match(url,/^\/audio\/demo-[1-4]\.wav$/);return {ok:true,arrayBuffer:async()=>new ArrayBuffer(0)};
  };
  const processors=new Map();globalThis.sampleRate=8000;globalThis.currentFrame=0;
  globalThis.AudioWorkletProcessor=class{constructor(){this.port={postMessage(){},onmessage:null};}};
  globalThis.registerProcessor=(name,type)=>processors.set(name,type);
  await import('../static/program-worklet.mjs');await import('../static/capture-worklet.mjs');
  const source=()=>({frequency:{value:0},connect(){},disconnect(){},start(){},stop(){}});
  globalThis.AudioContext=class {
    constructor(){context=this;this.state='suspended';this.sampleRate=8000;this.currentTime=0;this.destination={};this.baseLatency=0;this.outputLatency=0;this.audioWorklet={addModule:async()=>{}};}
    async resume(){this.state='running';}async close(){this.state='closed';}
    async decodeAudioData(){return {getChannelData:()=>new Float32Array(64000).fill(.1)};}
    createGain(){return {gain:{value:1},connect(node){return node;},disconnect(){}};}
    createOscillator(){return source();}createMediaStreamSource(){return source();}
  };
  globalThis.AudioWorkletNode=class {
    constructor(_ctx,name){nodes[name]=this;this.port={onmessage:null,postMessage:(m,transfer=[])=>this.processor.port.onmessage({data:structuredClone(m,{transfer})})};this.processor=new(processors.get(name))();this.processor.port.postMessage=(m,transfer=[])=>{const data=structuredClone(m,{transfer});queueMicrotask(()=>this.port.onmessage?.({data}));};}
    connect(node){return node;}disconnect(){}
  };
  globalThis.Worker=class {
    constructor(){workers.push(this);}
    postMessage(m,transfer){const data=structuredClone(m,{transfer});queueMicrotask(async()=>{
      const result=await prepareJob(data);
      const resultData=structuredClone(result,{transfer:[result.samples.buffer,result.original.buffer]});
      const deliver=()=>this.onmessage?.({data:resultData});if(holdWorkerReply)deferredWorkerReply=deliver;else deliver();
    });}
    terminate(){this.onmessage=null;}
  };
  const report=()=>{elements['capture-report-button'].onclick();return JSON.parse(elements['capture-report'].textContent);};
  const pointer={pointerId:1,preventDefault(){}};
  try {
    await import('../static/app.mjs');await elements.start.onclick();
    const controls=elements.tracks.children[0].children[2].children;
    const undo=controls.find(e=>e.textContent==='Undo take'),download=controls.find(e=>e.textContent==='Download WAV');
    assert.equal(undo.disabled,true);download.onclick();
    const originalWav=new Uint8Array(await blobs.at(-1).arrayBuffer());
    assert.equal(new DataView(originalWav.buffer).getInt16(44,true),3277);
    elements.input.value='microphone';elements.input.onchange();assert.equal(elements.capture.disabled,true);
    await elements['enable-mic'].onclick();assert.equal(streams[0].track.readyState,'ended');assert.equal(elements.capture.disabled,false);
    elements.capture.onpointerdown(pointer);await settle(()=>report().capture.phase==='recording');
    const privateNode=nodes['private-capture'];
    for(let i=0;i<8;i++){globalThis.currentFrame=i*128;const output=[[new Float32Array(128)]];privateNode.processor.process([[new Float32Array(128).fill(.5)]],output);assert.ok(output[0][0].every(x=>x===0));nodes['loop-program'].processor.process([],[[new Float32Array(128),new Float32Array(128)]]);}
    await Promise.resolve();assert.equal(report().capture.ownedLiveTracks,1);assert.equal(report().lastCapture.privateInputPeak,.5);assert.equal(report().lastCapture.programPeakDuringCapture,0);assert.ok(report().lastCapture.programMeterSamples>0);
    elements.capture.onpointerup();await settle(()=>!elements.commit.disabled);assert.equal(streams[1].track.readyState,'ended');assert.equal(report().readyTrack,1);
    elements['level-mode'].value='matched';elements['level-mode'].onchange();assert.equal(elements.commit.disabled,true);await settle(()=>!elements.commit.disabled);
    assert.match(elements['level-report'].textContent,/Active RMS target matched/);assert.ok(report().workflow.readyLevels.gain<1);assert.equal(report().workflow.version,3);
    const matchedReport=elements['level-report'].textContent;
    elements['level-mode'].value='off';elements['level-mode'].onchange();await settle(()=>!elements.commit.disabled);assert.match(elements['level-report'].textContent,/Original level retained/);
    elements['level-mode'].value='matched';elements['level-mode'].onchange();await settle(()=>!elements.commit.disabled);assert.equal(elements['level-report'].textContent,matchedReport);
    download.onclick();assert.deepEqual(new Uint8Array(await blobs.at(-1).arrayBuffer()),originalWav,'private candidate cannot enter exports');
    await elements.commit.onclick();await settle(()=>backend.tracks[0].pending?.scheduled);
    download.onclick();assert.deepEqual(new Uint8Array(await blobs.at(-1).arrayBuffer()),originalWav,'scheduled candidate cannot enter exports');assert.equal(undo.disabled,true);
    const at=backend.tracks[0].pending.at;context.currentTime=(at-67)/8000;globalThis.currentFrame=at;
    nodes['loop-program'].processor.process([],[[new Float32Array(128),new Float32Array(128)]]);
    await settle(()=>backend.tracks[0].revision===1);assert.equal(backend.running,true);assert.deepEqual(report().activationErrorsFrames,[0]);
    await settle(()=>!undo.disabled);download.onclick();
    const committedWav=new Uint8Array(await blobs.at(-1).arrayBuffer());assert.notDeepEqual(committedWav,originalWav);
    assert.match(document.body.children.at(-1).download,/-r1-120bpm-4bars\.wav$/);
    await undo.onclick();await settle(()=>backend.tracks[0].pending?.scheduled);
    const undoAt=backend.tracks[0].pending.at;context.currentTime=undoAt/8000;globalThis.currentFrame=undoAt;nodes['loop-program'].processor.process([],[[new Float32Array(128),new Float32Array(128)]]);
    await settle(()=>backend.tracks[0].revision===2&&!undo.disabled);assert.equal(undo.textContent,'Redo take');download.onclick();assert.deepEqual(new Uint8Array(await blobs.at(-1).arrayBuffer()),originalWav);
    await undo.onclick();await settle(()=>backend.tracks[0].pending?.scheduled);
    const redoAt=backend.tracks[0].pending.at;context.currentTime=redoAt/8000;globalThis.currentFrame=redoAt;nodes['loop-program'].processor.process([],[[new Float32Array(128),new Float32Array(128)]]);
    await settle(()=>backend.tracks[0].revision===3&&!undo.disabled);download.onclick();assert.deepEqual(new Uint8Array(await blobs.at(-1).arrayBuffer()),committedWav);
    holdWorkerReply=true;elements.capture.onpointerdown(pointer);await settle(()=>report().capture.phase==='recording');
    for(let i=0;i<8;i++)privateNode.processor.process([[new Float32Array(128).fill(.75)]],[[new Float32Array(128)]]);
    elements.capture.onpointerup();await settle(()=>deferredWorkerReply);assert.equal(elements.discard.disabled,false);
    elements.discard.onclick();deferredWorkerReply();await Promise.resolve();assert.equal(elements.commit.disabled,true);assert.equal(report().readyTrack,null);holdWorkerReply=false;
    download.onclick();assert.deepEqual(new Uint8Array(await blobs.at(-1).arrayBuffer()),committedWav,'discarded late worker output cannot enter exports');
    let resolve;pendingPermission={promise:new Promise(r=>resolve=r)};
    elements.capture.onpointerdown(pointer);await settle(()=>report().capture.phase==='opening');
    document.hidden=true;documentEvents.visibilitychange();const late=stream();resolve(late);await settle(()=>late.track.readyState==='ended');pendingPermission=null;
    assert.equal(report().capture.ownedLiveTracks,0);assert.equal(report().readyTrack,null);assert.equal(backend.tracks[0].revision,3);
    assert.ok(report().events.some(e=>e.type==='late-input-released'));assert.equal(report().rawAudioIncluded,false);
    document.hidden=false;
    elements.capture.onpointerdown(pointer);await settle(()=>report().capture.phase==='recording');const unplugged=streams.at(-1);mediaEvents.devicechange();assert.equal(unplugged.track.readyState,'ended');assert.equal(report().capture.phase,'idle');
    await elements['enable-mic'].onclick();elements.capture.onpointerdown(pointer);await settle(()=>report().capture.phase==='recording');const focusInput=streams.at(-1);elements.capture.onblur();assert.equal(focusInput.track.readyState,'ended');assert.equal(report().capture.phase,'idle');
    elements.capture.onpointerdown(pointer);await settle(()=>report().capture.phase==='recording');const failedInput=streams.at(-1);workers[0].onerror();assert.equal(failedInput.track.readyState,'ended');assert.equal(elements.capture.disabled,true);
    await undo.onclick();await settle(()=>backend.tracks[0].pending?.scheduled);const stale={...backend.tracks[0].pending,epoch:backend.epoch};
    await elements.stop.onclick();assert.equal(backend.running,false);assert.equal(context.state,'closed');assert.equal(report().capture.disposed,true);
    nodes['loop-program'].port.onmessage({data:{type:'activated',epoch:stale.epoch,id:stale.id,track:1,at:stale.at,applied:stale.at}});await Promise.resolve();assert.equal(backend.running,false);assert.equal(report().readyTrack,null);
    assert.equal(undo.disabled,true);assert.equal(download.disabled,true);assert.equal(revoked.length,blobs.length);assert.equal(report().workflow.retainedCommittedSamples,0);
    const stoppedNotice=elements.notice.textContent;workers[0].onerror();assert.equal(elements.notice.textContent,stoppedNotice,'obsolete worker errors cannot mutate a later lifecycle');
  } finally {URL.createObjectURL=originalCreate;URL.revokeObjectURL=originalRevoke;rmSync(temp,{recursive:true,force:true});}
});
