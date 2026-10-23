import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {activationNow} from '../static/engine.mjs';

test('render receipt supplies a known clock floor and preserves exact-frame checks',()=> {
  assert.equal(activationNow(396772,396900,396900),396900);
  assert.equal(activationNow(397000,396900,396900),397000);
  assert.throws(()=>activationNow(397000,396900,396901),/differs/);
  for(const bad of [NaN,Infinity,-1,1.5,1e12+1])assert.throws(()=>activationNow(bad,0,0),/Invalid/);
});

test('real strict planner reproduces the stale-main-clock rejection and accepts the render receipt',()=> {
  const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),temp=mkdtempSync(path.join(tmpdir(),'loop-activation-'));
  const file=path.join(temp,'args.json');
  const invoke=payload=> {
    writeFileSync(file,JSON.stringify(JSON.stringify(payload)));
    const p=spawnSync('ailang',['run','--strict-bytecode','--entry','handle','--args-file',file,'--package-dir',root,path.join(root,'planner.ail')],{cwd:root,encoding:'utf8',timeout:10000});
    assert.equal(p.status,0,p.stderr);return JSON.parse(p.stdout);
  };
  try {
    let state=invoke({schema:1,op:'init'}).state;
    const apply=(kind,extra={})=>invoke({schema:1,state,command:{id:kind,kind,epoch:state.epoch,expected:state.revision,now:0,...extra}});
    let r=apply('configure',{rate:44100,bpm:120,origin:44100});assert.equal(r.ok,true);state=r.state;
    r=apply('prepare',{track:1,base:0,asset:'clock-regression',hash:'a'.repeat(64),now:44101,ready:44101});assert.equal(r.ok,true);state=r.state;
    const pending=state.tracks[0].pending,at=pending.at;
    r=apply('schedule',{track:1,base:0,pendingId:pending.id,at,now:at-128});assert.equal(r.ok,true);state=r.state;
    const ack={track:1,base:0,pendingId:pending.id,at,applied:at},mainFrame=at-128;
    r=apply('activate',{...ack,now:mainFrame});assert.equal(r.ok,false);assert.match(r.error,/activation not acknowledged/);
    r=apply('activate',{...ack,now:activationNow(mainFrame,at,at)});assert.equal(r.ok,true);assert.equal(r.state.tracks[0].revision,1);assert.equal(r.state.tracks[0].pending,null);
    // A later main clock still cannot authorize an incorrectly applied frame.
    r=apply('activate',{...ack,applied:at+1,now:at+128});assert.equal(r.ok,false);
  } finally {rmSync(temp,{recursive:true,force:true});}
});
