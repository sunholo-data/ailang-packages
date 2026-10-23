// No capture sample is ever routed to program output. Fixed allocation per take.
class Capture extends AudioWorkletProcessor {
  constructor() {
    super(); this.buffer=null; this.id=null; this.used=0; this.meterAt=0; this.peak=0;
    this.port.onmessage=e=> {
      if(e.data.type==='start' && !this.buffer) {
        const n=e.data.frames;
        if(Number.isInteger(n) && n>0 && n<=sampleRate*16 && Number.isSafeInteger(e.data.id)) { this.buffer=new Float32Array(n); this.id=e.data.id; this.used=0; this.peak=0; }
      } else if(e.data.type==='stop' && (e.data.id===undefined || e.data.id===this.id)) this.finish();
      else if(e.data.type==='cancel' && (e.data.id===undefined || e.data.id===this.id)) { this.buffer=null; this.id=null; this.used=0; this.peak=0; }
    };
  }
  finish() {
    if(!this.buffer) return;
    const buffer=this.buffer; this.buffer=null;
    this.port.postMessage({type:'take',id:this.id,samples:buffer,used:this.used,rate:sampleRate},[buffer.buffer]);
    this.used=0;
  }
  process(inputs,outputs) {
    for(const channel of outputs[0]) channel.fill(0);
    const input=inputs[0]?.[0];
    if(this.buffer && input) {
      for(let i=0;i<input.length && this.used<this.buffer.length;i++) {
        const x=Number.isFinite(input[i])?Math.max(-1,Math.min(1,input[i])):0;
        this.buffer[this.used++]=x; this.peak=Math.max(this.peak,Math.abs(x));
      }
      if(this.used===this.buffer.length) this.finish();
    }
    if(currentFrame>=this.meterAt) { this.port.postMessage({type:'capture-meter',id:this.buffer?this.id:null,peak:this.peak,frames:this.used}); this.peak=0; this.meterAt=currentFrame+Math.floor(sampleRate/16); }
    return true;
  }
}
registerProcessor('private-capture',Capture);
