// Compute-only WASM probe in Node/V8. Browser scheduling is a separate experiment.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const start=performance.now(),times=[];
await import(pathToFileURL(path.join(root,'.runtime/wasm_exec.js')));
const go=new globalThis.Go();
const {instance}=await WebAssembly.instantiate(fs.readFileSync(path.join(root,'.runtime/ailang.wasm')),go.importObject);
go.run(instance).catch(error=>{console.error(error.message);process.exit(1);});
while(typeof globalThis.ailangLoadModule!=='function')await new Promise(resolve=>setTimeout(resolve,5));
const version=globalThis.ailangVersion();
const loaded=globalThis.ailangLoadModule('sunholo/live_loop_lab/planner',fs.readFileSync(path.join(root,'planner.ail'),'utf8'));
if(!loaded.success) {console.log(JSON.stringify({version,compatible:false,error:loaded.error,coldMs:performance.now()-start},null,2));process.exit(2);}
for(let i=0;i<20;i++) {
  const at=performance.now(),r=globalThis.ailangCall('sunholo/live_loop_lab/planner','handle',JSON.stringify({schema:1,op:'init'}));
  if(!r.success)throw new Error(r.error);
  let value=r.result;
  if(typeof value==='string'&&value.endsWith(' :: String'))value=JSON.parse(value.slice(0,-10));
  if(!JSON.parse(value).ok)throw new Error('invalid response');
  times.push(performance.now()-at);
}
let state=JSON.parse(globalThis.ailangCall('sunholo/live_loop_lab/planner','handle',JSON.stringify({schema:1,op:'init'})).result).state;
const commandTimes=[];
for(let i=0;i<25;i++) {
  const command={kind:i===0?'configure':'parameter',id:`bench-${i}`,epoch:state.epoch,expected:state.revision,now:0,rate:48000,bpm:120,origin:48000,track:1,level:i,pan:0,muted:false};
  const at=performance.now(),r=globalThis.ailangCall('sunholo/live_loop_lab/planner','handle',JSON.stringify({schema:1,state,command}));
  if(!r.success)throw new Error(r.error);const response=JSON.parse(r.result);
  if(!response.ok)throw new Error(response.error);state=response.state;commandTimes.push(performance.now()-at);
}
const commandsSorted=[...commandTimes].sort((a,b)=>a-b);
const sorted=[...times].sort((a,b)=>a-b);
console.log(JSON.stringify({platform:'Node '+process.version,version,compatible:true,probe:'20 pure handle init calls after module load; exported runtime engine, not strict-bytecode CLI',times,medianMs:sorted[10],p95Ms:sorted[18],coldMs:performance.now()-start,commands:{probe:"1 configure + 24 parameter commands; resident WASM exported call engine",times:commandTimes,medianMs:commandsSorted[12],p95Ms:commandsSorted[23],finalState:state},manifest:JSON.parse(fs.readFileSync(path.join(root,'.runtime/manifest.json'),'utf8'))},null,2));
process.exit(0);
