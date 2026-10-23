// The worklet owns timing. Functions here are shared by the renderer and tests.
export const TRACKS = 4;
export const MAX_SECONDS = 16;
// The renderer has already reached its acknowledged frame even when a cached or
// reduced-precision main-thread currentTime still trails it. Keep exact-frame
// validation; use the acknowledgement as a lower bound on the known clock.
export function activationNow(mainFrame, plannedFrame, appliedFrame) {
  if([mainFrame,plannedFrame,appliedFrame].some(x=>!Number.isSafeInteger(x)||x<0||x>1e12))throw new Error('Invalid activation clock');
  if(appliedFrame!==plannedFrame)throw new Error('Activation differs from planned frame');
  return Math.max(mainFrame,appliedFrame);
}
export function validSamples(xs, rate) {
  return xs instanceof Float32Array && Number.isInteger(rate) && rate >= 8000 && rate <= 192000
    && xs.length > 0 && xs.length <= rate * MAX_SECONDS && xs.every(x => Number.isFinite(x) && Math.abs(x) <= 1);
}
export function gains(level, pan, muted) {
  if (!Number.isInteger(level) || level < 0 || level > 100 || !Number.isInteger(pan) || Math.abs(pan) > 100 || typeof muted !== 'boolean') throw new Error('invalid parameters');
  const angle = (pan / 100 + 1) * Math.PI / 4, amplitude = muted ? 0 : level / 100;
  return [Math.cos(angle)*amplitude, Math.sin(angle)*amplitude];
}
export function prepareTake(input, rate, frames) {
  const output=shapeTake(input,rate,frames);
  let peak=0;for(const x of output)peak=Math.max(peak,Math.abs(x));
  const scale=peak>0.501187?0.501187/peak:1;
  for(let i=0;i<output.length;i++)output[i]*=scale;
  return output;
}
export function shapeTake(input, rate, frames) {
  if (!validSamples(input,rate) || !Number.isSafeInteger(frames) || frames < 1 || frames > rate*MAX_SECONDS) throw new Error('invalid take or frame budget');
  const output = new Float32Array(frames), used = Math.min(frames,input.length), edge = Math.min(Math.round(rate*.01),Math.floor(used/2));
  for(let i=0;i<used;i++) {
    const fade=edge>1?Math.min(1,i/(edge-1),(used-1-i)/(edge-1)):1;
    output[i]=input[i]*fade;
  }
  return output;
}
export function cycleFrame(rate,bpm,origin,cycle) { return origin+Math.floor(cycle*rate*960/bpm); }
