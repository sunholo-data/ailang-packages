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
