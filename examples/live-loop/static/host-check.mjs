import {prepareTake} from './engine.mjs';
const button=document.getElementById('run'),result=document.getElementById('result');
button.onclick=async()=> {
  button.disabled=true;result.textContent='Running synthetic capture…';
  let ctx,osc,program,capture,muted;
  const report={kind:'synthetic Web Audio host check',userAgent:navigator.userAgent,startedAt:new Date().toISOString(),physicalDeviceLatencyMeasured:false},messages=[];
  const waitFor=(predicate,ms=12000)=>new Promise((resolve,reject)=> {
    const start=performance.now();
    const poll=()=>{const m=messages.find(predicate);if(m)resolve(m);else if(performance.now()-start>=ms)reject(new Error('Timed out waiting for audio acknowledgement'));else setTimeout(poll,10);};poll();
  });
  try {
    ctx=new AudioContext({latencyHint:'interactive'});await ctx.resume();report.rate=ctx.sampleRate;
    report.reportedBaseLatencyMs=ctx.baseLatency*1000;report.reportedOutputLatencyMs=(ctx.outputLatency||0)*1000;
    await Promise.all([ctx.audioWorklet.addModule('/program-worklet.mjs'),ctx.audioWorklet.addModule('/capture-worklet.mjs')]);
    muted=ctx.createGain();muted.gain.value=0;muted.connect(ctx.destination);
    program=new AudioWorkletNode(ctx,'loop-program',{numberOfInputs:0,outputChannelCount:[2]});program.connect(muted);
    capture=new AudioWorkletNode(ctx,'private-capture',{outputChannelCount:[1]});capture.connect(muted);
    program.port.onmessage=e=>messages.push({...e.data,source:'program'});
    capture.port.onmessage=e=>messages.push({...e.data,source:'private'});
    const origin=Math.ceil(ctx.currentTime*ctx.sampleRate)+Math.round(ctx.sampleRate*.5);
    const tracks=Array.from({length:4},()=>({samples:new Float32Array(ctx.sampleRate*8),level:100,pan:0,muted:false,revision:0}));
    program.port.postMessage({type:'init',epoch:1,origin,rate:ctx.sampleRate,bpm:120,tracks},tracks.map(t=>t.samples.buffer));
    await waitFor(m=>m.type==='initialized');
    osc=ctx.createOscillator();osc.frequency.value=220;capture.port.postMessage({type:'start',id:1,frames:ctx.sampleRate});osc.connect(capture);osc.start();
    await waitFor(m=>m.type==='capture-meter'&&m.peak>.5);
    await new Promise(resolve=>setTimeout(resolve,250));
    capture.port.postMessage({type:'stop'});osc.stop();osc.disconnect();
    const take=await waitFor(m=>m.type==='take');
    report.capturedFrames=take.used;report.privateInputPeak=Math.max(...messages.filter(m=>m.type==='capture-meter').map(m=>m.peak));
    report.programPeakBeforeCommit=Math.max(...messages.filter(m=>m.source==='program'&&m.type==='meter').map(m=>m.peak));
    if(report.programPeakBeforeCommit!==0 || report.privateInputPeak<.5)throw new Error('Private routing isolation failed');
    const start=performance.now(),samples=prepareTake(take.samples.subarray(0,take.used),ctx.sampleRate,ctx.sampleRate*8);report.preparationMs=performance.now()-start;
    // No raw take remains in the diagnostic report.
    for(let i=0;i<messages.length;i++)if(messages[i].type==='take')messages[i]={type:'take-discarded'};
    result.textContent='Private signal captured; program remained silent. Waiting for the committed loop boundary…';
    const at=origin+ctx.sampleRate*8;
    program.port.postMessage({type:'stage',epoch:1,track:1,base:0,revision:1,id:'synthetic-check',at,samples},[samples.buffer]);
    const staged=await waitFor(m=>m.type==='scheduled');report.stagedAtFrame=staged.frame;report.plannedFrame=at;
    const active=await waitFor(m=>m.type==='activated');report.appliedFrame=active.applied;report.activationErrorFrames=active.applied-at;
    const audible=await waitFor(m=>m.source==='program'&&m.type==='meter'&&m.frame>=at&&m.peak>.001);
    report.programPeakAfterCommit=audible.peak;report.passed=report.activationErrorFrames===0;
  } catch(error) {report.passed=false;report.error=error.message;}
  finally {try{osc?.stop();}catch{}program?.disconnect();capture?.disconnect();muted?.disconnect();await ctx?.close();button.disabled=false;result.textContent=JSON.stringify(report,null,2);}
};
