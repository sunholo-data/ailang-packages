// Actual application module + real strict AILANG planner, with in-memory DOM,
// device and render-clock fakes. This is not a real microphone/browser test.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {prepareTake} from '../static/engine.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
class Element {
  constructor(){this.value=0;this.textContent='';this.style={};this.children=[];this.classList={toggle(){}};}
  append(...items){this.children.push(...items);}setAttribute(){}setPointerCapture(){}
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
  const nodes={},elements={},documentEvents={},windowEvents={},mediaEvents={},streams=[];
  let pendingPermission=null,context;
  for(const match of readFileSync(path.join(root,'static/index.html'),'utf8').matchAll(/id="([^"]+)"/g))elements[match[1]]=new Element();
  elements.input.value='synthetic';elements.wave.width=600;elements.wave.height=110;
  globalThis.document={hidden:false,getElementById:id=>{assert.ok(elements[id],id);return elements[id];},createElement:()=>new Element(),addEventListener:(type,fn)=>documentEvents[type]=fn};
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
    postMessage(m,transfer){const data=structuredClone(m,{transfer});queueMicrotask(async()=>{
      const samples=prepareTake(data.samples,data.rate,data.frames),digest=await crypto.subtle.digest('SHA-256',samples.buffer);
      this.onmessage?.({data:{id:data.id,samples,hash:Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,'0')).join(''),prepareMs:1}});
    });}
    terminate(){this.onmessage=null;}
  };
  const report=()=>{elements['capture-report-button'].onclick();return JSON.parse(elements['capture-report'].textContent);};
  const pointer={pointerId:1,preventDefault(){}};
  try {
    await import('../static/app.mjs');await elements.start.onclick();
    elements.input.value='microphone';elements.input.onchange();assert.equal(elements.capture.disabled,true);
    await elements['enable-mic'].onclick();assert.equal(streams[0].track.readyState,'ended');assert.equal(elements.capture.disabled,false);
    elements.capture.onpointerdown(pointer);await settle(()=>report().capture.phase==='recording');
    const privateNode=nodes['private-capture'];
    for(let i=0;i<8;i++){globalThis.currentFrame=i*128;const output=[[new Float32Array(128)]];privateNode.processor.process([[new Float32Array(128).fill(.5)]],output);assert.ok(output[0][0].every(x=>x===0));nodes['loop-program'].processor.process([],[[new Float32Array(128),new Float32Array(128)]]);}
    await Promise.resolve();assert.equal(report().capture.ownedLiveTracks,1);assert.equal(report().lastCapture.privateInputPeak,.5);assert.equal(report().lastCapture.programPeakDuringCapture,0);assert.ok(report().lastCapture.programMeterSamples>0);
    elements.capture.onpointerup();await settle(()=>!elements.commit.disabled);assert.equal(streams[1].track.readyState,'ended');assert.equal(report().readyTrack,1);
    await elements.commit.onclick();await settle(()=>backend.tracks[0].pending?.scheduled);
    const at=backend.tracks[0].pending.at;context.currentTime=(at-67)/8000;globalThis.currentFrame=at;
    nodes['loop-program'].processor.process([],[[new Float32Array(128),new Float32Array(128)]]);
    await settle(()=>backend.tracks[0].revision===1);assert.equal(backend.running,true);assert.deepEqual(report().activationErrorsFrames,[0]);
    let resolve;pendingPermission={promise:new Promise(r=>resolve=r)};
    elements.capture.onpointerdown(pointer);await settle(()=>report().capture.phase==='opening');
    document.hidden=true;documentEvents.visibilitychange();const late=stream();resolve(late);await settle(()=>late.track.readyState==='ended');pendingPermission=null;
    assert.equal(report().capture.ownedLiveTracks,0);assert.equal(report().readyTrack,null);assert.equal(backend.tracks[0].revision,1);
    assert.ok(report().events.some(e=>e.type==='late-input-released'));assert.equal(report().rawAudioIncluded,false);
    document.hidden=false;
    elements.capture.onpointerdown(pointer);await settle(()=>report().capture.phase==='recording');const unplugged=streams.at(-1);mediaEvents.devicechange();assert.equal(unplugged.track.readyState,'ended');assert.equal(report().capture.phase,'idle');
    await elements['enable-mic'].onclick();elements.capture.onpointerdown(pointer);await settle(()=>report().capture.phase==='recording');const focusInput=streams.at(-1);elements.capture.onblur();assert.equal(focusInput.track.readyState,'ended');assert.equal(report().capture.phase,'idle');
    await elements.stop.onclick();assert.equal(backend.running,false);assert.equal(context.state,'closed');assert.equal(report().capture.disposed,true);
  } finally {rmSync(temp,{recursive:true,force:true});}
});
