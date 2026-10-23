import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {TakeHistory,hashSamples,wav16Mono} from '../static/take-workflow.mjs';
import {measureLevels,planLevels,prepareFloat32Levels} from '../static/levels.mjs';
import {prepareJob} from '../static/prepare-worker.mjs';
const rate=8000,frames=rate*8,asset=x=>({samples:new Float32Array(frames).fill(x),hash:(x===.1?'a':'b').repeat(64)});
function seeded(){const h=new TakeHistory();h.seed(7,rate,[asset(.1),asset(.1),asset(.1),asset(.1)]);return h;}

test('private and pending assets cannot replace the exportable current asset',()=> {
  const h=seeded(),take=asset(.3);h.stage(7,1,'p',1,take);
  structuredClone(take.samples,{transfer:[take.samples.buffer]});
  assert.equal(h.current(1).samples[0],Math.fround(.1));
  assert.throws(()=>h.activate(6,1,'p',1));assert.throws(()=>h.activate(7,1,'wrong',1));assert.throws(()=>h.activate(7,1,'p',2));
  h.activate(7,1,'p',1);assert.equal(h.current(1).samples[0],Math.fround(.3));assert.equal(h.current(1).revision,1);
});
test('undo and redo stage a new revision; a new capture replaces one previous slot',()=> {
  const h=seeded();h.stage(7,1,'one',1,asset(.3));h.activate(7,1,'one',1);
  const undo=h.restore(1);assert.equal(undo.kind,'undo');h.stage(7,1,'undo',2,undo,'undo');h.activate(7,1,'undo',2);
  assert.equal(h.current(1).samples[0],Math.fround(.1));assert.equal(h.status(1).restoreLabel,'Redo take');
  const redo=h.restore(1);h.stage(7,1,'redo',3,redo,'redo');h.activate(7,1,'redo',3);assert.equal(h.current(1).samples[0],Math.fround(.3));
  h.stage(7,1,'new',4,asset(.4));h.activate(7,1,'new',4);assert.equal(h.restore(1).samples[0],Math.fround(.3));assert.equal(h.restore(1).kind,'undo');
  assert.equal(h.retainedSamples(),frames*5);
});
test('rejection preserves the current/previous pair and reset drops all owned history',()=> {
  const h=seeded();h.stage(7,1,'one',1,asset(.3));h.activate(7,1,'one',1);
  h.stage(7,1,'two',2,asset(.4));h.reject(6,1,'two');assert.equal(h.status(1).pending,true);h.reject(7,1,'two');
  assert.equal(h.current(1).samples[0],Math.fround(.3));assert.equal(h.restore(1).samples[0],Math.fround(.1));
  h.clear();assert.equal(h.retainedSamples(),0);assert.throws(()=>h.current(1));
});
test('history validates slots, budgets and buffers and never exposes mutable owned samples',()=> {
  const h=seeded();h.current(1).samples.fill(1);assert.equal(h.current(1).samples[0],Math.fround(.1));
  for(const patch of [{samples:new Float32Array(1)},{hash:'invalid'},{samples:new Float32Array(frames).fill(NaN)}])assert.throws(()=>h.stage(7,1,'p',1,{...asset(.3),...patch}));
  assert.throws(()=>h.stage(8,1,'p',1,asset(.3)));assert.throws(()=>h.stage(7,5,'p',1,asset(.3)));assert.throws(()=>h.stage(7,1,'p',2,asset(.3)));
  for(let id=1;id<=4;id++){h.stage(7,id,`one-${id}`,1,asset(.3));h.activate(7,id,`one-${id}`,1);h.stage(7,id,`two-${id}`,2,asset(.4));}
  assert.equal(h.retainedSamples(),frames*12);assert.throws(()=>h.stage(7,1,'overflow',2,asset(.4)));
});
test('WAV is RIFF PCM16 mono with pinned half-away rounding and strict range checks',()=> {
  const bytes=wav16Mono(new Float32Array([-1,-.5,0,.5,1]),44100),v=new DataView(bytes.buffer);
  assert.equal(new TextDecoder().decode(bytes.slice(0,4)),'RIFF');assert.equal(v.getUint32(4,true),46);assert.equal(v.getUint32(24,true),44100);assert.equal(v.getUint16(22,true),1);assert.equal(v.getUint16(34,true),16);assert.equal(v.getUint32(40,true),10);
  assert.deepEqual(Array.from({length:5},(_,i)=>v.getInt16(44+i*2,true)),[-32767,-16384,0,16384,32767]);
  const decoded=spawnSync('python3',['-c','import io,json,sys,wave; w=wave.open(io.BytesIO(sys.stdin.buffer.read())); print(json.dumps([w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()]))'],{input:bytes});
  assert.equal(decoded.status,0,decoded.stderr.toString());assert.deepEqual(JSON.parse(decoded.stdout.toString()),[1,2,44100,5]);
  for(const x of [NaN,Infinity,1.1])assert.throws(()=>wav16Mono(new Float32Array([x]),8000));
  assert.throws(()=>wav16Mono(new Float32Array(8000*17),8000));
});
test('hashing uses only the view bytes, not unrelated underlying buffer data',async()=> {
  const xs=new Float32Array([1,.25,.5,1]);assert.equal(await hashSamples(xs.subarray(1,3)),await hashSamples(new Float32Array([.25,.5])));
});
test('level measurement pools stereo energy and guards report config against field injection',()=> {
  const r=measureLevels([new Float64Array([.5,-.5]),new Float64Array([-.5,.5])],44100,{windowFrames:2,activityFloor:.1,peak:999,frames:999});
  assert.equal(r.rms,.5);assert.equal(r.activeRms,.5);assert.equal(r.activeFrames,2);assert.equal(r.samples,4);assert.equal(r.peak,.5);assert.equal(r.frames,2);
  assert.equal(measureLevels([new Float64Array([1.6e308,-1.6e308])],8000).rms,1.6e308);
  for(const bad of [NaN,Infinity])assert.throws(()=>measureLevels([new Float64Array([bad])],8000));
  assert.throws(()=>measureLevels([new Float64Array([1])],8000,{windowFrames:0,activityFloor:0}));
  assert.throws(()=>measureLevels([new Float64Array(3)],8000,undefined,{maxFrames:2,maxSamples:2}));
});
test('Float32 preparation respects the stored peak ceiling, keeps silence quiet and caps boost',()=> {
  const silent=prepareFloat32Levels(new Float32Array(2051),8000,'matched');assert.equal(silent.levelPlan.gain,1);assert.equal(silent.levelPlan.reason,'BelowActivityFloor');
  const quiet=prepareFloat32Levels(new Float32Array(2051).fill(.01),8000,'matched');assert.equal(quiet.levelPlan.gain,4);
  const strong=prepareFloat32Levels(new Float32Array(2051).fill(1),8000,'peak-safe');assert.ok(strong.after.peak<=.501187);assert.equal(strong.levelPlan.float32Adjusted,true);
  assert.ok(prepareFloat32Levels(new Float32Array(2051).fill(.0001),8000,'matched').samples.every(x=>x===Math.fround(.0001)));
  assert.throws(()=>planLevels([new Float64Array()],8000,undefined,{mode:'matched',maxBoost:Infinity}));
});
test('worker keeps an unlevelled original so mode changes cannot compound gain or fades',async()=> {
  const raw=new Float32Array(8000).fill(.01);
  const first=await prepareJob({id:1,samples:raw,rate:8000,frames:64000,levelMode:'matched'});
  const off=await prepareJob({id:2,samples:first.original,rate:8000,frames:64000,shaped:true,levelMode:'off'});
  const again=await prepareJob({id:3,samples:first.original,rate:8000,frames:64000,shaped:true,levelMode:'matched'});
  assert.deepEqual(again.samples,first.samples);assert.equal(again.hash,first.hash);assert.deepEqual(off.samples,first.original);assert.equal(raw[0],Math.fround(.01));
  await assert.rejects(prepareJob({id:4,samples:raw,rate:8000,frames:64000,shaped:true}));
});
