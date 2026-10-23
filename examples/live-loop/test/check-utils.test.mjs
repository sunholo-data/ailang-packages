import test from 'node:test';
import assert from 'node:assert/strict';
import {EventWaiters,delay,timingSummary} from '../static/check-utils.mjs';
test('waiters match identities, drop resolved subscriptions and reject cancellation',async()=> {
  const c=new AbortController(),events=new EventWaiters(c.signal);
  const a=events.wait(m=>m.id==='a'),b=events.wait(m=>m.id==='b');
  events.dispatch({id:'old'});assert.equal(events.pending.size,2);
  events.dispatch({id:'a',frame:42});assert.deepEqual(await a,{id:'a',frame:42});assert.equal(events.pending.size,1);
  c.abort('Stopped by user');await assert.rejects(b,/Stopped by user/);assert.equal(events.pending.size,0);
});
test('waiter timeout and count ceiling prevent an unbounded pending queue',async()=> {
  const c=new AbortController(),events=new EventWaiters(c.signal);
  await assert.rejects(events.wait(()=>false,1),/Timed out/);assert.equal(events.pending.size,0);
  const p=Array.from({length:8},()=>events.wait(()=>false).catch(e=>e));
  await assert.rejects(events.wait(()=>false),/limit/);c.abort('done');await Promise.all(p);assert.equal(events.pending.size,0);
});
test('cancellable delay does not leave a completed wait or report completion after stop',async()=> {
  const c=new AbortController();await delay(1,c.signal);const p=delay(1000,c.signal);c.abort('cancelled');await assert.rejects(p,/cancelled/);
  await assert.rejects(delay(1,c.signal),/cancelled/);
});
test('timing summary reports nearest-rank p95 and rejects invalid evidence',()=> {
  assert.equal(timingSummary([]),null);
  assert.deepEqual(timingSummary([10,1,2,3]),{count:4,medianMs:2.5,p95Ms:10,maxMs:10});
  assert.throws(()=>timingSummary([NaN]));assert.throws(()=>timingSummary([-1]));assert.throws(()=>timingSummary(new Array(513).fill(1)));
});

test('visibility accounting permits hidden intervals and snapshots do not double-count them',async()=> {
  const {VisibilityLog}=await import('../static/check-utils.mjs');
  const v=new VisibilityLog(false,100);
  v.record(true,200);assert.equal(v.summary(400).hiddenMs,200);
  v.record(false,500);const result=v.summary(600);
  assert.equal(result.hiddenMs,300);assert.equal(result.visibleMs,200);assert.equal(result.changes,2);
  v.record(false,650);assert.equal(v.summary(700).changes,2);
});
test('visibility evidence stays bounded while counting all hidden intervals',async()=> {
  const {VisibilityLog}=await import('../static/check-utils.mjs');const v=new VisibilityLog(true,0);
  for(let i=1;i<=100;i++)v.record(i%2===0,i);
  const s=v.summary(110);assert.equal(s.events.length,32);assert.equal(s.eventsDropped,69);
  assert.equal(s.changes,100);assert.equal(s.hiddenMs,60);assert.equal(s.visibleMs,50);
  assert.equal(s.startedHidden,true);assert.equal(s.endedHidden,true);
  assert.throws(()=>v.summary(109),/Non-monotonic/);
});
test('a hidden synthetic check can still receive its pending render acknowledgement',async()=> {
  const {VisibilityLog}=await import('../static/check-utils.mjs');const c=new AbortController(),events=new EventWaiters(c.signal),v=new VisibilityLog(false,0);
  const received=events.wait(m=>m.type==='activated');v.record(true,100);
  assert.equal(c.signal.aborted,false);assert.equal(events.pending.size,1);
  events.dispatch({type:'activated',applied:44100});assert.equal((await received).applied,44100);
  assert.equal(v.summary(200).hiddenMs,100);
});
