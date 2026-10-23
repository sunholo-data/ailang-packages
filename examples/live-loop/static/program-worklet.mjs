import {gains,validSamples} from './engine.mjs';
class Program extends AudioWorkletProcessor {
  constructor() {
    super(); this.tracks=Array.from({length:4},()=>({samples:null,gain:[0,0],pending:null,revision:0}));
    this.ready=false; this.epoch=-1; this.origin=0; this.rate=sampleRate; this.bpm=120; this.nextMeter=0;
    this.peak=0; this.clipped=0; this.blocks=0;
    this.port.onmessage=event=>this.message(event.data);
  }
  reject(message,reason) { this.port.postMessage({type:'rejected',id:message.id,track:message.track,epoch:this.epoch,reason,frame:currentFrame}); }
  message(m) {
    if(m.type==='init') {
      if(this.ready || !Number.isSafeInteger(m.epoch) || m.epoch<0 || !Number.isSafeInteger(m.origin) || m.origin>1e12 || m.origin<currentFrame+128 || m.rate!==sampleRate || m.bpm!==120 || !Array.isArray(m.tracks) || m.tracks.length!==4) return this.reject(m,'invalid initialization or deadline');
      let checked;
      try { checked=m.tracks.map(t=>({samples:t.samples,gain:gains(t.level,t.pan,t.muted),pending:null,revision:t.revision})); }
      catch { return this.reject(m,'invalid initial parameters'); }
      if(checked.some(t=>!validSamples(t.samples,sampleRate) || t.samples.length!==sampleRate*8 || !Number.isInteger(t.revision) || t.revision<0 || t.revision>=1000000)) return this.reject(m,'invalid initial assets');
      this.tracks=checked; this.origin=m.origin; this.epoch=m.epoch; this.bpm=m.bpm; this.ready=true;
      return this.port.postMessage({type:'initialized',epoch:this.epoch,frame:currentFrame});
    }
    if(!this.ready || m.epoch!==this.epoch || !Number.isInteger(m.track) || m.track<1 || m.track>4) return this.reject(m,'stale epoch or track');
    const t=this.tracks[m.track-1];
    if(m.type==='parameter') { try { t.gain=gains(m.level,m.pan,m.muted); } catch { this.reject(m,'invalid parameters'); } return; }
    if(m.type!=='stage' || t.pending || m.base!==t.revision || m.revision!==t.revision+1 || typeof m.id!=='string' || m.id.length<1 || m.id.length>96 || !Number.isSafeInteger(m.at) || m.at>1e12 || m.at<currentFrame+128 || !validSamples(m.samples,sampleRate) || m.samples.length!==sampleRate*8 || (m.at-this.origin)%(sampleRate*8)!==0) return this.reject(m,'invalid asset, revision, boundary or deadline');
    t.pending={id:m.id,at:m.at,samples:m.samples,revision:m.revision};
    this.port.postMessage({type:'scheduled',id:m.id,track:m.track,epoch:this.epoch,at:m.at,frame:currentFrame});
  }
  process(_inputs,outputs) {
    const left=outputs[0][0], right=outputs[0][1];
    if(!right) return true;
    for(let i=0;i<left.length;i++) {
      const frame=currentFrame+i; let l=0,r=0;
      if(this.ready && frame>=this.origin) for(let k=0;k<4;k++) {
        const t=this.tracks[k],p=t.pending;
        if(p && frame===p.at) {
          t.samples=p.samples; t.revision=p.revision; t.pending=null;
          this.port.postMessage({type:'activated',id:p.id,track:k+1,epoch:this.epoch,at:p.at,applied:frame,frame});
        }
        const x=t.samples[(frame-this.origin)%t.samples.length]; l+=x*t.gain[0]; r+=x*t.gain[1];
      }
      if(Math.abs(l)>1 || Math.abs(r)>1) this.clipped++;
      left[i]=Math.max(-1,Math.min(1,l)); right[i]=Math.max(-1,Math.min(1,r));
      this.peak=Math.max(this.peak,Math.abs(left[i]),Math.abs(right[i]));
    }
    this.blocks++;
    if(currentFrame>=this.nextMeter) {
      this.port.postMessage({type:'meter',frame:currentFrame,peak:this.peak,clipped:this.clipped,blocks:this.blocks,epoch:this.epoch});
      this.peak=0; this.nextMeter=currentFrame+Math.floor(sampleRate/16);
    }
    return true;
  }
}
registerProcessor('loop-program',Program);
