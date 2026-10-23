import {validSamples} from './engine.mjs';
export async function hashSamples(samples) {
  const digest=await crypto.subtle.digest('SHA-256',samples);
  return Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,'0')).join('');
}
const hashValid=hash=>typeof hash==='string'&&/^[0-9a-f]{64}$/.test(hash);
// At most current + previous + pending per track, all fixed eight-second mono
// assets. The cap bounds retained sample buffers, not all browser heap/transfers.
export class TakeHistory {
  constructor(){this.clear();}
  clear(){this.epoch=null;this.rate=null;this.tracks=[];}
  seed(epoch,rate,assets) {
    if(!Number.isSafeInteger(epoch)||epoch<0||!Array.isArray(assets)||assets.length!==4)throw new Error('Invalid history session');
    const checked=assets.map(a=>this.asset(a,rate));
    this.clear();this.epoch=epoch;this.rate=rate;
    this.tracks=checked.map(current=>({current:{...current,revision:0},previous:null,pending:null,undone:false}));
  }
  asset(a,rate=this.rate) {
    if(!a||!validSamples(a.samples,rate)||a.samples.length!==rate*8||!hashValid(a.hash))throw new Error('Invalid history asset');
    return {samples:a.samples.slice(),hash:a.hash};
  }
  track(id){if(!Number.isInteger(id)||id<1||id>4||this.epoch===null)throw new Error('No active track history');return this.tracks[id-1];}
  status(id){const t=this.track(id);return {revision:t.current.revision,canRestore:!!t.previous&&!t.pending,restoreLabel:t.undone?'Redo take':'Undo take',pending:!!t.pending};}
  current(id){const t=this.track(id);return {...t.current,samples:t.current.samples.slice()};}
  restore(id){const t=this.track(id);if(!t.previous||t.pending)throw new Error('No previous take available');return {...t.previous,samples:t.previous.samples.slice(),kind:t.undone?'redo':'undo'};}
  stage(epoch,id,pendingId,revision,asset,kind='capture') {
    const t=this.track(id);
    if(epoch!==this.epoch||typeof pendingId!=='string'||!pendingId||pendingId.length>96||t.pending||revision!==t.current.revision+1||!['capture','undo','redo'].includes(kind))throw new Error('Stale history stage');
    if(kind!=='capture'&&(!t.previous||asset.hash!==t.previous.hash||kind!==(t.undone?'redo':'undo')))throw new Error('Stale history restore');
    t.pending={...this.asset(asset),id:pendingId,revision,kind};
  }
  activate(epoch,id,pendingId,revision) {
    const t=this.track(id),p=t.pending;
    if(epoch!==this.epoch||!p||p.id!==pendingId||p.revision!==revision)throw new Error('Stale history activation');
    t.previous=t.current;t.current={samples:p.samples,hash:p.hash,revision};t.undone=p.kind==='undo';t.pending=null;
  }
  reject(epoch,id,pendingId){const t=this.track(id);if(epoch===this.epoch&&t.pending?.id===pendingId)t.pending=null;}
  retainedSamples(){return this.tracks.reduce((n,t)=>n+t.current.samples.length+(t.previous?.samples.length||0)+(t.pending?.samples.length||0),0);}
}
// Legacy-compatible *32767, half-away-from-zero quantization; strict full scale.
export function wav16Mono(samples,rate) {
  if(!validSamples(samples,rate))throw new Error('Invalid committed WAV asset');
  const bytes=new Uint8Array(44+samples.length*2),view=new DataView(bytes.buffer);
  const text=(at,value)=>{for(let i=0;i<value.length;i++)view.setUint8(at+i,value.charCodeAt(i));};
  text(0,'RIFF');view.setUint32(4,bytes.length-8,true);text(8,'WAVE');text(12,'fmt ');view.setUint32(16,16,true);view.setUint16(20,1,true);view.setUint16(22,1,true);view.setUint32(24,rate,true);view.setUint32(28,rate*2,true);view.setUint16(32,2,true);view.setUint16(34,16,true);text(36,'data');view.setUint32(40,samples.length*2,true);
  for(let i=0;i<samples.length;i++){const x=samples[i]*32767;view.setInt16(44+i*2,x>=0?Math.floor(x+.5):Math.ceil(x-.5),true);}
  return bytes;
}
