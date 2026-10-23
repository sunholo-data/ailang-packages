import test from 'node:test';
import assert from 'node:assert/strict';
import {gains,validSamples,prepareTake,cycleFrame} from '../static/engine.mjs';

test('preparation trims/pads, fades edges and caps without boosting silence or quiet input',()=> {
  const full=new Float32Array(8000).fill(1),p=prepareTake(full,8000,16000);
  assert.equal(p.length,16000);assert.equal(p[0],0);assert.equal(p[7999],0);assert.equal(p[8000],0);
  assert.ok(Math.max(...p)<=.501188);assert.ok(Math.abs(p[4000]-.501187)<1e-7);
  const quiet=prepareTake(new Float32Array(8000).fill(.1),8000,8000);assert.ok(Math.abs(quiet[4000]-.1)<1e-7);
  assert.ok(prepareTake(new Float32Array(800),8000,8000).every(x=>x===0));
});
test('rejects nonfinite, out-of-range and resource overflow before output allocation',()=> {
  for(const bad of [NaN,Infinity,-Infinity,1.1])assert.equal(validSamples(new Float32Array([bad]),8000),false);
  assert.throws(()=>prepareTake(new Float32Array(1),8000,8000*17));
  assert.throws(()=>gains(101,0,false));assert.throws(()=>gains(1,101,false));
  assert.deepEqual(gains(50,0,true),[0,0]);assert.ok(gains(100,-100,false)[0]===1);
});
test('absolute frames do not accumulate rounded beat error',()=> {
  assert.equal(cycleFrame(44100,137,100,1000),100+Math.floor(44100*960*1000/137));
});

// Deterministic render-kernel tests. These are not browser/device latency evidence.
const processors=new Map();
globalThis.AudioWorkletProcessor=class{constructor(){this.messages=[];this.port={postMessage:m=>this.messages.push(m)};}};
globalThis.registerProcessor=(name,type)=>processors.set(name,type);
globalThis.sampleRate=8000;globalThis.currentFrame=0;
await import('../static/program-worklet.mjs');await import('../static/capture-worklet.mjs');
const block=()=>[[new Float32Array(128),new Float32Array(128)]];
function initialized() {
  globalThis.currentFrame=0;const p=new(processors.get('loop-program'))();
  p.message({type:'init',epoch:1,origin:256,rate:8000,bpm:120,tracks:Array.from({length:4},()=>({samples:new Float32Array(64000).fill(.1),level:25,pan:0,muted:false,revision:0}))});return p;
}
test('four-part renderer is silent before origin then mixes every part',()=> {
  const p=initialized(),out=block();p.process([],out);assert.ok(out[0][0].every(x=>x===0));
  globalThis.currentFrame=256;p.process([],out);assert.ok(Math.abs(out[0][0][0]-.1*Math.SQRT1_2)<1e-7);
});
test('all muted tracks are silent while private capture meters a nonzero signal',()=> {
  const p=initialized();for(let track=1;track<=4;track++)p.message({type:'parameter',epoch:1,track,level:25,pan:0,muted:true});
  const c=new(processors.get('private-capture'))();c.port.onmessage({data:{type:'start',id:1,frames:8000}});
  globalThis.currentFrame=256;const out=block();p.process([],out);const privateOut=block();c.process([[new Float32Array(128).fill(.8)]],privateOut);
  assert.ok(out[0][0].every(x=>x===0));assert.ok(privateOut[0].every(channel=>channel.every(x=>x===0)));
  assert.ok(c.messages.some(m=>m.type==='capture-meter'&&m.peak>.7));
  c.port.onmessage({data:{type:'stop'}});const take=c.messages.find(m=>m.type==='take');assert.equal(take.used,128);assert.equal(take.samples.length,8000);
});
test('cancel and fixed buffer capacity drop private state and never emit input',()=> {
  const c=new(processors.get('private-capture'))();c.port.onmessage({data:{type:'start',id:1,frames:129}});
  for(let i=0;i<2;i++)c.process([[new Float32Array(128).fill(.7)]],block());
  assert.equal(c.messages.find(m=>m.type==='take').used,129);assert.equal(c.buffer,null);
  c.port.onmessage({data:{type:'start',id:1,frames:100}});c.port.onmessage({data:{type:'cancel'}});assert.equal(c.buffer,null);
});
test('commit activates inside the render block at the exact planned sample',()=> {
  const p=initialized();globalThis.currentFrame=64000;
  p.message({type:'stage',epoch:1,track:1,base:0,revision:1,id:'take',at:64256,samples:new Float32Array(64000).fill(.3)});
  globalThis.currentFrame=64200;const out=block();p.process([],out);
  const a=p.messages.find(m=>m.type==='activated');assert.equal(a.applied,64256);assert.equal(a.applied-a.at,0);
  assert.ok(out[0][0][56]>out[0][0][55]);assert.equal(p.tracks[0].revision,1);
});
test('late wrong-length and stale revisions retain the old program asset',()=> {
  const p=initialized();const original=p.tracks[0].samples;globalThis.currentFrame=64200;
  const m={type:'stage',epoch:1,track:1,base:0,revision:1,id:'take',at:64256,samples:new Float32Array(64000)};
  p.message(m);p.message({...m,at:128256,epoch:0});p.message({...m,at:128256,base:1});p.message({...m,at:128256,samples:new Float32Array(1)});
  assert.equal(p.tracks[0].samples,original);assert.equal(p.tracks[0].pending,null);assert.equal(p.messages.filter(m=>m.type==='rejected').length,4);
});
test('100 legal handoffs keep the exact planned frame and bounded pending slots',()=> {
  const p=initialized();
  for(let i=1;i<=100;i++) {
    const at=256+64000*i;globalThis.currentFrame=at-256;
    p.message({type:'stage',epoch:1,track:1,base:i-1,revision:i,id:`take-${i}`,at,samples:new Float32Array(64000).fill(.1)});
    globalThis.currentFrame=at-64;p.process([],block());assert.equal(p.tracks[0].pending,null);
  }
  const a=p.messages.filter(m=>m.type==='activated');assert.equal(a.length,100);assert.ok(a.every(m=>m.applied===m.at));
});
test('malformed initialization is rejected without killing the render processor',()=> {
  globalThis.currentFrame=0;const p=new(processors.get('loop-program'))();
  const m={type:'init',epoch:1,origin:256,rate:8000,bpm:120,tracks:Array.from({length:4},()=>({samples:new Float32Array(64000),level:101,pan:0,muted:false,revision:0}))};
  assert.doesNotThrow(()=>p.message(m));assert.equal(p.ready,false);assert.equal(p.messages[0].type,'rejected');
  assert.doesNotThrow(()=>p.message({...m,tracks:'abcd'}));
});
