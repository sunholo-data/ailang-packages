// Browser adapter for sunholo/audio/levels. Reference parity is tested against
// the AILANG API; its proofs do not transfer to this JavaScript implementation.
export const LEVEL_CONFIG=Object.freeze({windowFrames:1024,activityFloor:.001});
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const energy=()=>({samples:0,peak:0,squares:0,fullScaleSamples:0,overRangeSamples:0});
function add(e,x) {
  const a=Math.abs(x),peak=Math.max(e.peak,a),old=peak?e.peak/peak:0,next=peak?a/peak:0;
  return {samples:e.samples+1,peak,squares:e.squares*old*old+next*next,fullScaleSamples:e.fullScaleSamples+(a>=1?1:0),overRangeSamples:e.overRangeSamples+(a>1?1:0)};
}
const rms=e=>e.samples&&e.peak?e.peak*Math.sqrt(Math.min(1,e.squares/e.samples)):0;
function merge(a,b) {
  const peak=Math.max(a.peak,b.peak),ar=peak?a.peak/peak:0,br=peak?b.peak/peak:0;
  return {samples:a.samples+b.samples,peak,squares:a.squares*ar*ar+b.squares*br*br,fullScaleSamples:a.fullScaleSamples+b.fullScaleSamples,overRangeSamples:a.overRangeSamples+b.overRangeSamples};
}
export function measureLevels(planes,rate,config=LEVEL_CONFIG,limits={maxFrames:1440000,maxSamples:2880000}) {
  if(!Number.isInteger(rate)||rate<1||rate>384000||!Number.isInteger(config?.windowFrames)||config.windowFrames<1||config.windowFrames>65536||!finite(config.activityFloor)||config.activityFloor<0||config.activityFloor>1)throw new Error('Invalid level rate, window or activity floor');
  if(!Number.isInteger(limits?.maxFrames)||limits.maxFrames<0||limits.maxFrames>2147483647||!Number.isInteger(limits.maxSamples)||limits.maxSamples<0||limits.maxSamples>2147483647)throw new Error('Invalid level budget');
  if(!Array.isArray(planes)||planes.length<1||planes.length>2||planes.some(p=>!(p instanceof Float32Array||p instanceof Float64Array)))throw new Error('Level input requires mono or stereo float planes');
  const frames=planes[0].length,channels=planes.length;
  if(frames>limits.maxFrames||frames*channels>limits.maxSamples||planes.some(p=>p.length!==frames))throw new Error('Level shape or sample budget exceeded');
  let total=energy(),active=energy(),pending=energy();
  const flush=()=>{const value=rms(pending);if(value>0&&value>=config.activityFloor)active=merge(active,pending);pending=energy();};
  for(let i=0;i<frames;i++) {
    for(let ch=0;ch<channels;ch++) {
      const x=planes[ch][i];if(!finite(x))throw new Error('Level samples must be finite');
      total=add(total,x);pending=add(pending,x);
    }
    if(pending.samples===config.windowFrames*channels)flush();
  }
  flush();
  return {rate,layout:channels===1?'Mono':'Stereo',frames,samples:total.samples,peak:total.peak,rms:rms(total),activeRms:rms(active),activeFrames:active.samples/channels,fullScaleSamples:total.fullScaleSamples,overRangeSamples:total.overRangeSamples,windowFrames:config.windowFrames,activityFloor:config.activityFloor};
}
function peakGain(peak,ceiling){if(!peak||peak<=ceiling/64)return 64;return Math.max(0,(ceiling/peak)*(1-2e-15)-5e-324);}
function policyValid(p) {
  const range=(x,lo,hi)=>finite(x)&&x>=lo&&x<=hi;
  return p?.mode==='off'||(p?.mode==='peak-safe'&&range(p.peakCeiling,1e-12,1))
    ||(p?.mode==='matched'&&range(p.peakCeiling,1e-12,1)&&range(p.targetRms,1e-12,1)&&range(p.maxBoost,1,64)&&Number.isInteger(p.minActiveFrames)&&p.minActiveFrames>=1&&p.minActiveFrames<=2147483647);
}
function decision(r,policy) {
  if(policy.mode==='off')return {report:r,policy,requestedGain:1,gain:1,reason:'Bypassed'};
  if(policy.mode==='peak-safe') {
    const gain=r.peak<=policy.peakCeiling?1:Math.min(1,peakGain(r.peak,policy.peakCeiling));
    return {report:r,policy,requestedGain:1,gain,reason:gain<1?'PeakLimited':'AlreadyAtLevel'};
  }
  const quiet=!r.activeRms||r.activeFrames<policy.minActiveFrames,boosted=!quiet&&r.activeRms<policy.targetRms/policy.maxBoost;
  const requestedGain=quiet?1:boosted?policy.maxBoost:policy.targetRms/r.activeRms,gain=Math.min(requestedGain,peakGain(r.peak,policy.peakCeiling));
  const reason=gain<requestedGain?'PeakLimited':!r.activeRms?'BelowActivityFloor':r.activeFrames<policy.minActiveFrames?'InsufficientActivity':boosted?'BoostLimited':gain===1?'AlreadyAtLevel':'TargetMatched';
  return {report:r,policy,requestedGain,gain,reason};
}
export function planLevels(planes,rate,config,policy,limits) {
  if(!policyValid(policy))throw new Error('Invalid level policy');
  return decision(measureLevels(planes,rate,config,limits),{...policy});
}
export function capturePolicy(mode) {
  if(mode==='off')return {mode};
  if(mode==='peak-safe')return {mode,peakCeiling:.501187};
  if(mode==='matched')return {mode,targetRms:.125,peakCeiling:.501187,maxBoost:4,minActiveFrames:1024};
  throw new Error('Unknown take level mode');
}
export function prepareFloat32Levels(original,rate,mode) {
  const limits={maxFrames:rate*16,maxSamples:rate*16};
  const plan=planLevels([original],rate,LEVEL_CONFIG,capturePolicy(mode),limits);
  let samples=Float32Array.from(original,x=>x*plan.gain),after=measureLevels([samples],rate,LEVEL_CONFIG,limits);
  plan.float32Adjusted=false;
  // Float32 storage can round above a double-precision ceiling. Re-render the
  // original with a reserve, then enforce the actual stored-sample peak.
  if(mode!=='off'&&after.peak>plan.policy.peakCeiling) {
    plan.gain*=plan.policy.peakCeiling/after.peak*(1-2e-7);plan.float32Adjusted=true;
    samples=Float32Array.from(original,x=>x*plan.gain);after=measureLevels([samples],rate,LEVEL_CONFIG,limits);
  }
  if(mode!=='off'&&after.peak>plan.policy.peakCeiling)throw new Error('Prepared output exceeds the peak ceiling');
  return {samples,levelPlan:plan,after};
}
