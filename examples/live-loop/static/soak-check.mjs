import {EventWaiters,delay,timingSummary} from './check-utils.mjs';
const $=id=>document.getElementById(id);
let running=null;
async function api(path,body,signal) {
  const timeout=AbortSignal.timeout(4000),combined=signal?AbortSignal.any([signal,timeout]):timeout;
  const response=await fetch(path,body?{method:'POST',headers:{'Content-Type':'application/json','X-Loop-Lab':'1'},body:JSON.stringify(body),signal:combined}:{signal:combined});
  const data=await response.json();if(!response.ok||data.ok===false)throw new Error(data.error||'Planner bridge unavailable');return data;
}
$('stop').onclick=()=>running?.abort('Stopped by user');
$('run').onclick=async()=> {
  if(running)return;
  const controller=new AbortController();running=controller;const {signal}=controller;
  const long=$('profile').value==='soak',target=long?100:8,seconds=long?1800:0;
  const report={kind:'synthetic planner/worker/Web Audio repeated handoff check',profile:long?'100 handoffs and 30-minute soak':'8 handoffs only',userAgent:navigator.userAgent,startedAt:new Date().toISOString(),physicalDeviceLatencyMeasured:false,targetHandoffs:target,targetAudioSeconds:seconds,handoffs:[],workerMs:[],workerRoundTripMs:[],bridgeMs:[],passed:false,completed:false};
  let state,ownedEpoch=null,configureId=null,configureFromEpoch=null,ctx,program,capture,osc,worker,sink,lastMeter=null,privatePeak=0,programPeakBefore=0,sequence=0;
  const audioEvents=new EventWaiters(signal),workerEvents=new EventWaiters(signal);
  const frame=()=>Math.ceil(ctx.currentTime*ctx.sampleRate);
  const command=async(kind,extra={},useSignal=true)=> {
    const response=await api('/api/command',{command:{id:`check-${++sequence}-${crypto.randomUUID()}`,kind,epoch:state.epoch,expected:state.revision,now:ctx?frame():0,...extra}},useSignal?signal:undefined);
    state=response.state;
    if(report.bridgeMs.length<512)report.bridgeMs.push(response.bridgeMs);
    return state;
  };
  const fail=reason=>{if(!signal.aborted)controller.abort(reason);};
  const visibility=()=>{if(document.hidden)fail('Page hidden; repeat the check with this tab visible');};
  const leaving=()=>fail('Page closing');
  document.addEventListener('visibilitychange',visibility);window.addEventListener('pagehide',leaving);
  $('run').disabled=true;$('profile').disabled=true;$('stop').disabled=false;$('result').textContent='Running…';
  try {
    // Resume inside the user's click activation, before awaiting any network I/O.
    ctx=new AudioContext({latencyHint:'interactive'});await ctx.resume();
    ctx.onstatechange=()=>{if(ctx.state!=='running'&&!report.completed)fail(`Audio context ${ctx.state}`);};
    state=(await api('/api/state',null,signal)).state;
    if(state.running)throw new Error('Use Stop & reset in Loop Lab first, then run this check');
    report.rate=ctx.sampleRate;report.reportedBaseLatencyMs=ctx.baseLatency*1000;report.reportedOutputLatencyMs=(ctx.outputLatency||0)*1000;
    await Promise.all([ctx.audioWorklet.addModule('/program-worklet.mjs'),ctx.audioWorklet.addModule('/capture-worklet.mjs')]);
    const origin=frame()+ctx.sampleRate;
    configureId=`configure-check-${crypto.randomUUID()}`;configureFromEpoch=state.epoch;
    await command('configure',{id:configureId,rate:ctx.sampleRate,bpm:120,origin});ownedEpoch=state.epoch;
    sink=ctx.createGain();sink.gain.value=0;sink.connect(ctx.destination);
    program=new AudioWorkletNode(ctx,'loop-program',{numberOfInputs:0,outputChannelCount:[2]});program.connect(sink);
    capture=new AudioWorkletNode(ctx,'private-capture',{outputChannelCount:[1]});capture.connect(sink);
    program.onprocessorerror=()=>fail('Program AudioWorklet processor failed');capture.onprocessorerror=()=>fail('Capture AudioWorklet processor failed');
    program.port.onmessage=e=> {
      const m={...e.data,source:'program'};
      if(m.type==='rejected')fail(`Renderer rejected stage: ${m.reason}`);
      if(m.type==='meter') {
        if(!Number.isFinite(m.peak)||m.peak>1||m.clipped!==0)fail('Invalid program samples or unexpected clamping');
        lastMeter=m;if(!report.handoffs.length)programPeakBefore=Math.max(programPeakBefore,m.peak);
      }
      audioEvents.dispatch(m);
    };
    capture.port.onmessage=e=>{if(e.data.type==='capture-meter')privatePeak=Math.max(privatePeak,e.data.peak);audioEvents.dispatch({...e.data,source:'private'});};
    const initialized=audioEvents.wait(m=>m.type==='initialized');
    const tracks=state.tracks.map(t=>({...t,samples:new Float32Array(ctx.sampleRate*8)}));
    program.port.postMessage({type:'init',epoch:ownedEpoch,origin,rate:ctx.sampleRate,bpm:120,tracks},tracks.map(t=>t.samples.buffer));await initialized;
    $('progress').textContent='Checking private synthetic capture…';
    const privateSignal=audioEvents.wait(m=>m.type==='capture-meter'&&m.peak>.5);
    osc=ctx.createOscillator();osc.frequency.value=220;capture.port.postMessage({type:'start',id:1,frames:ctx.sampleRate});osc.connect(capture);osc.start();
    await privateSignal;await delay(250,signal);
    const takePromise=audioEvents.wait(m=>m.type==='take'&&m.id===1);capture.port.postMessage({type:'stop'});osc.stop();osc.disconnect();
    const take=await takePromise;const template=new Float32Array(take.samples.subarray(0,take.used));
    report.privateInputPeak=privatePeak;report.programPeakBeforeCommit=programPeakBefore;report.capturedFrames=take.used;
    if(privatePeak<.5||programPeakBefore!==0)throw new Error('Private routing isolation failed');
    capture.disconnect();capture.port.onmessage=null;capture=null;
    worker=new Worker('/prepare-worker.mjs',{type:'module'});worker.onerror=()=>fail('Preparation worker failed');worker.onmessage=e=>workerEvents.dispatch(e.data);
    for(let i=0;i<target;i++) {
      $('progress').textContent=`Preparing handoff ${i+1} of ${target}…`;
      const input=template.slice(),workerStart=performance.now(),preparedPromise=workerEvents.wait(m=>m.id===i);
      worker.postMessage({id:i,samples:input,rate:ctx.sampleRate,frames:ctx.sampleRate*8},[input.buffer]);
      const prepared=await preparedPromise;if(prepared.error)throw new Error(prepared.error);
      report.workerMs.push(prepared.prepareMs);report.workerRoundTripMs.push(performance.now()-workerStart);
      const track=state.tracks[i%4];
      await command('prepare',{track:track.id,base:track.revision,asset:`check-take-${i}`,hash:prepared.hash,ready:frame()});
      const pending=state.tracks[track.id-1].pending;
      const scheduledPromise=audioEvents.wait(m=>m.type==='scheduled'&&m.id===pending.id);
      const activatedPromise=audioEvents.wait(m=>m.type==='activated'&&m.id===pending.id);
      // Catch immediately so cancellation during Schedule cannot leave an unhandled rejection.
      activatedPromise.catch(()=>{});
      program.port.postMessage({type:'stage',epoch:ownedEpoch,track:track.id,base:track.revision,revision:pending.revision,id:pending.id,at:pending.at,samples:prepared.samples},[prepared.samples.buffer]);
      const staged=await scheduledPromise;
      await command('schedule',{track:track.id,base:track.revision,pendingId:pending.id,at:pending.at,now:staged.frame});
      $('progress').textContent=`Handoff ${i+1} of ${target}: waiting for the planned loop boundary…`;
      const active=await activatedPromise;
      if(active.applied!==pending.at||active.epoch!==ownedEpoch)throw new Error('Activation frame or epoch mismatch');
      await command('activate',{track:track.id,base:track.revision,pendingId:pending.id,at:pending.at,applied:active.applied});
      report.handoffs.push({track:track.id,plannedFrame:pending.at,appliedFrame:active.applied,errorFrames:active.applied-pending.at,stagingLeadFrames:pending.at-staged.frame});
      if(i===0) {
        // The tone is short: match a block that begins before the tail as well.
        if(!lastMeter||lastMeter.peak===0)await audioEvents.wait(m=>m.type==='meter'&&m.frame>=active.applied&&m.peak>.001);
        report.programPeakAfterCommit=lastMeter.peak;
      }
    }
    while((frame()-origin)/ctx.sampleRate<seconds) {
      const elapsed=Math.max(0,(frame()-origin)/ctx.sampleRate),last=lastMeter?.frame??0;
      $('progress').textContent=`${target} exact-frame handoffs complete. Soak: ${Math.floor(elapsed/60)} of 30 audio minutes.`;
      await audioEvents.wait(m=>m.type==='meter'&&m.frame>last,3000);await delay(500,signal);
    }
    report.audioElapsedSeconds=Math.max(0,(frame()-origin)/ctx.sampleRate);report.renderBlocks=lastMeter?.blocks;report.clampedFrames=lastMeter?.clipped;
    report.completed=true;report.passed=report.handoffs.length===target&&report.handoffs.every(h=>h.errorFrames===0)&&report.audioElapsedSeconds>=seconds;
    $('progress').textContent=long?'100 handoffs and 30-minute software soak complete.':'8-handoff short check complete. The 30-minute soak has not run.';
  } catch(error) {report.error=error.message;report.cancelled=signal.aborted;$('progress').textContent=`Check incomplete: ${error.message}`;}
  finally {
    controller.abort('Check finished');document.removeEventListener('visibilitychange',visibility);window.removeEventListener('pagehide',leaving);
    if(ctx)ctx.onstatechange=null;try{osc?.stop();}catch{}osc?.disconnect();worker?.terminate();capture?.disconnect();program?.disconnect();sink?.disconnect();
    if(configureId!==null) {
      try {
        const latest=(await api('/api/state')).state;
        // A cancelled HTTP response may hide an accepted configure command.
        if(ownedEpoch===null && latest.epoch===configureFromEpoch+1 && latest.seen.includes(configureId))ownedEpoch=latest.epoch;
        if(ownedEpoch!==null) {
          if(latest.epoch!==ownedEpoch)throw new Error('Session epoch changed; left the newer session untouched');
          state=latest;await command('reset',{now:0},false);
        }
      } catch(error) {report.cleanupError=error.message;report.passed=false;}
    }
    try{await ctx?.close();}catch(error){report.cleanupError=error.message;report.passed=false;}report.finishedAt=new Date().toISOString();
    report.workerSummary=timingSummary(report.workerMs);report.workerRoundTripSummary=timingSummary(report.workerRoundTripMs);report.bridgeSummary=timingSummary(report.bridgeMs);
    report.bridgeSamplesCappedAt=512;$('result').textContent=JSON.stringify(report,null,2);$('run').disabled=false;$('profile').disabled=false;$('stop').disabled=true;running=null;
  }
};
