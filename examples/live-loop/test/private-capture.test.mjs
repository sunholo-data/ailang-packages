import test from 'node:test';
import assert from 'node:assert/strict';
import {CaptureLifecycle,MicrophoneAccess,inputError} from '../static/private-capture.mjs';
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
function media() {
  const track={readyState:'live',onended:null,stops:0,stop(){this.stops++;this.readyState='ended';},end(){this.readyState='ended';this.onended?.();}};
  return {getTracks:()=>[track],track};
}
function source() {return {frequency:{value:0},connections:[],stops:0,connect(n){this.connections.push(n);},disconnect(){this.connections=[];},start(){},stop(){this.stops++;}};}
function fixture(getMedia=async()=>media(),options={}) {
  const messages=[],takes=[],phases=[],events=[],errors=[],sources=[];
  const node={port:{postMessage:m=>messages.push(m),onmessage:null},onprocessorerror:null};
  const context={sampleRate:8000,createMediaStreamSource(){const s=source();sources.push(s);return s;},createOscillator(){const s=source();sources.push(s);return s;}};
  const microphone=new MicrophoneAccess(getMedia);
  const capture=new CaptureLifecycle({context,node,microphone,onTake:m=>takes.push(m),onPhase:m=>phases.push(m),onEvent:m=>events.push(m),onError:m=>errors.push(m),...options});
  const send=m=>node.port.onmessage?.({data:m});
  return {capture,node,context,microphone,messages,takes,phases,events,errors,sources,send};
}
const take=id=>({type:'take',id,used:400,rate:8000,samples:new Float32Array(400)});

test('release before permission resolves closes the late stream and emits no take',async()=> {
  const pending=deferred(),m=media(),f=fixture(()=>pending.promise);
  const opening=f.capture.begin('microphone',2);f.capture.release();pending.resolve(m);
  assert.equal(await opening,false);assert.equal(m.track.readyState,'ended');assert.equal(m.track.stops,1);
  assert.equal(f.sources.length,0);assert.equal(f.takes.length,0);assert.equal(f.capture.snapshot().ownedLiveTracks,0);
});
test('a late permission success cannot attach to or stop a later synthetic take',async()=> {
  const pending=deferred(),m=media(),f=fixture(()=>pending.promise);
  const old=f.capture.begin('microphone',1);f.capture.cancel('Focus lost');
  assert.equal(await f.capture.begin('synthetic',4),true);const current=f.capture.active;
  pending.resolve(m);assert.equal(await old,false);assert.equal(m.track.readyState,'ended');
  assert.equal(f.capture.active,current);assert.equal(current.phase,'recording');assert.equal(f.sources.length,1);
  f.send(take(current.id));assert.equal(f.takes[0].track,4);assert.equal(f.takes[0].kind,'synthetic');
});
test('late permission rejection cannot cancel a newer take',async()=> {
  const pending=deferred(),f=fixture(()=>pending.promise);
  const old=f.capture.begin('microphone',1);f.capture.cancel('Cancelled');await f.capture.begin('synthetic',3);
  const id=f.capture.active.id;pending.reject({name:'NotAllowedError'});
  assert.equal(await old,false);assert.equal(f.capture.active.id,id);assert.equal(f.errors.length,0);f.capture.dispose();
});
test('only one permission request is outstanding and the gate recovers after rejection',async()=> {
  const pending=deferred();let calls=0;const f=fixture(()=>{calls++;return pending.promise;});
  const old=f.capture.begin('microphone',1);f.capture.cancel();assert.equal(await f.capture.begin('microphone',2),false);assert.equal(calls,1);
  pending.reject({name:'NotAllowedError'});await old;assert.equal(f.microphone.pending,false);
  assert.match(f.errors[0],/pending microphone/);f.capture.dispose();
});
test('permission preflight releases its stream without connecting a capture graph',async()=> {
  const m=media();let constraints;
  const gate=new MicrophoneAccess(async c=>{constraints=c;return m;});
  assert.equal(await gate.authorize(),true);assert.equal(gate.pending,false);assert.equal(m.track.readyState,'ended');
  assert.deepEqual(constraints,{audio:{channelCount:1,echoCancellation:false,noiseSuppression:false,autoGainControl:false}});
});
test('release stops microphone tracks immediately and only its matching buffer becomes a take',async()=> {
  const m=media(),f=fixture(async()=>m);await f.capture.begin('microphone',2);const id=f.capture.active.id;
  f.capture.release();assert.equal(m.track.readyState,'ended');assert.equal(f.capture.active.phase,'finishing');
  f.send(take(id+1));assert.equal(f.takes.length,0);f.send(take(id));f.send(take(id));
  assert.equal(f.takes.length,1);assert.equal(f.takes[0].track,2);assert.equal(f.capture.active,null);assert.equal(f.capture.snapshot().ownedLiveTracks,0);
});
test('automatic capacity completion releases input and ignores old device-ended callbacks',async()=> {
  const m=media(),f=fixture(async()=>m);await f.capture.begin('microphone',1);const id=f.capture.active.id,oldEnded=m.track.onended;
  f.send(take(id));assert.equal(m.track.readyState,'ended');await f.capture.begin('synthetic',4);const current=f.capture.active;
  oldEnded();assert.equal(f.capture.active,current);assert.equal(f.takes.length,1);f.capture.dispose();
});
test('device loss cancels its current capture and drops an already queued raw buffer',async()=> {
  const m=media(),f=fixture(async()=>m);await f.capture.begin('microphone',1);const id=f.capture.active.id;
  m.track.end();f.send(take(id));assert.equal(f.takes.length,0);assert.equal(f.capture.active,null);
  assert.match(f.phases.at(-1).reason,/disconnected/);assert.equal(f.capture.snapshot().ownedLiveTracks,0);
});
test('dispose during permission open closes a late grant and never reconnects input',async()=> {
  const pending=deferred(),m=media(),f=fixture(()=>pending.promise),opening=f.capture.begin('microphone',1);
  f.capture.dispose();pending.resolve(m);await opening;
  assert.equal(m.track.readyState,'ended');assert.equal(f.sources.length,0);assert.equal(f.node.port.onmessage,null);assert.equal(f.capture.disposed,true);
});
test('capture processor errors release input and prevent reuse until a fresh context',async()=> {
  const m=media(),f=fixture(async()=>m);await f.capture.begin('microphone',1);f.node.onprocessorerror();
  assert.equal(m.track.readyState,'ended');assert.equal(f.capture.disposed,true);assert.equal(await f.capture.begin('synthetic',1),false);assert.match(f.errors[0],/stop & reset/);
});
test('a missing finish acknowledgement times out without leaking input or delivering a take',async()=> {
  const m=media(),f=fixture(async()=>m,{finishTimeoutMs:1});await f.capture.begin('microphone',1);f.capture.release();
  await new Promise(r=>setTimeout(r,10));assert.equal(f.capture.active,null);assert.equal(f.takes.length,0);assert.equal(m.track.readyState,'ended');assert.match(f.phases.at(-1).reason,/did not finish/);
});
test('invalid buffer metadata and unsupported track IDs never reach preparation',async()=> {
  const f=fixture();assert.equal(await f.capture.begin('synthetic',5),false);await f.capture.begin('synthetic',1);
  f.send({...take(f.capture.active.id),used:401});assert.equal(f.takes.length,0);assert.equal(f.capture.active,null);
});
test('permission failure is reported without device strings and capture can be retried',async()=> {
  let count=0;const f=fixture(async()=>{if(!count++)throw {name:'NotAllowedError',message:'private device identifier'};return media();});
  assert.equal(await f.capture.begin('microphone',1),false);assert.equal(f.errors[0],'Microphone permission was not granted');
  assert.equal(await f.capture.begin('microphone',1),true);f.capture.dispose();assert.equal(inputError({name:'UnknownError',message:'secret'}),'Input could not be opened');
});
