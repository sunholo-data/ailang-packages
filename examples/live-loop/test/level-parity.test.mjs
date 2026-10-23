import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {planLevels,capturePolicy,LEVEL_CONFIG} from '../static/levels.mjs';
import {wav16Mono} from '../static/take-workflow.mjs';
const application=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
function invoke(entry,index){
  const p=spawnSync('ailang',['run','--quiet','--strict-bytecode','--verify-contracts','--package-dir',application,'--entry',entry,'--args-json',String(index),path.join(application,'test/fixtures/adapter_probe.ail')],{cwd:application,encoding:'utf8',timeout:10000});
  assert.equal(p.status,0,p.stderr);return JSON.parse(p.stdout);
}
function fixture(index){
  const kind=index%6,channels=kind===4?2:1;
  return Array.from({length:channels},(_,ch)=>Float64Array.from({length:2051},(_,i)=>kind===0?0:kind===1?.01:kind===2?(i%2===0?.25:-.25):kind===3?(i===10?1:.01):kind===4?(ch===0?.1:-.1):i>=1024&&i<2048?.0001:.1));
}
test('browser plan adapter agrees with AILANG on 18 signal/policy cases with runtime contracts',()=> {
  for(let i=0;i<18;i++) {
    const expected=invoke('probe',i),mode=i<6?'off':i<12?'peak-safe':'matched';
    const p=planLevels(fixture(i),8000,LEVEL_CONFIG,capturePolicy(mode));
    const actual={peak:p.report.peak,rms:p.report.rms,activeRms:p.report.activeRms,activeFrames:p.report.activeFrames,gain:p.gain,requestedGain:p.requestedGain,reason:p.reason};
    for(const [key,want] of Object.entries(expected)) {
      if(typeof want==='number')assert.ok(Math.abs(actual[key]-want)<=Math.max(1e-15,Math.abs(want)*1e-12),`${i} ${key}: ${actual[key]} != ${want}`);
      else assert.equal(actual[key],want,`${i} ${key}`);
    }
  }
});
test('browser WAV export is byte-identical to the AILANG PCM16 adapter on a pinned fixture',()=> {
  assert.deepEqual([...wav16Mono(new Float32Array([-1,-.5,0,.5,1]),44100)],invoke('wavProbe',0));
});
