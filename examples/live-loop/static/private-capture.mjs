// Main-thread ownership of input resources. Samples only enter the private,
// always-zero-output worklet. No stream or device identity enters diagnostics.
export const microphoneConstraints=()=>({audio:{channelCount:1,echoCancellation:false,noiseSuppression:false,autoGainControl:false}});
export function closeMedia(media) { for(const track of media.getTracks()){track.onended=null;track.stop();} }
export function inputError(error) {
  const messages={NotAllowedError:'Microphone permission was not granted',NotFoundError:'No microphone is available',NotReadableError:'Microphone is busy or disconnected',AbortError:'Input request was interrupted',SecurityError:'Microphone access requires a secure page'};
  return messages[error?.name]||'Input could not be opened';
}
export class MicrophoneAccess {
  constructor(getMedia) {this.getMedia=getMedia;this.pending=false;}
  async request() {
    if(this.pending)throw new Error('Resolve or dismiss the pending microphone permission request first');
    this.pending=true;
    try {return await this.getMedia(microphoneConstraints());}
    finally {this.pending=false;}
  }
  async authorize() {
    const media=await this.request();
    try {return true;}finally {closeMedia(media);}
  }
}
export class CaptureLifecycle {
  constructor({context,node,microphone,onPhase=()=>{},onTake=()=>{},onMeter=()=>{},onEvent=()=>{},onError=()=>{},finishTimeoutMs=2000}) {
    this.context=context;this.node=node;this.microphone=microphone;this.onPhase=onPhase;this.onTake=onTake;this.onMeter=onMeter;this.onEvent=onEvent;this.onError=onError;this.finishTimeoutMs=finishTimeoutMs;
    this.active=null;this.nextId=0;this.disposed=false;this.streams=new Set();
    node.port.onmessage=e=>this.message(e.data);
    node.onprocessorerror=()=>{this.dispose();this.onError('Capture processor failed; stop & reset');};
  }
  phase(op,phase) {op.phase=phase;this.onPhase({phase,id:op.id,track:op.track,kind:op.kind});}
  event(type,op,extra={}) {this.onEvent({type,id:op?.id??null,track:op?.track??null,kind:op?.kind??null,...extra});}
  owns(op) {return !this.disposed&&this.active===op;}
  closeStream(media,op,late=false) {
    closeMedia(media);this.streams.delete(media);this.event(late?'late-input-released':'input-released',op);
  }
  releaseResources(op) {
    clearTimeout(op.timer);
    if(op.source){op.source.disconnect();try{op.source.stop?.();}catch{}op.source=null;}
    if(op.media){this.closeStream(op.media,op);op.media=null;}
  }
  async begin(kind,track) {
    if(this.disposed||this.active||!['microphone','synthetic'].includes(kind)||!Number.isInteger(track)||track<1||track>4)return false;
    if(kind==='microphone'&&this.microphone.pending){this.onError('Resolve or dismiss the pending microphone permission request first');return false;}
    const op={id:++this.nextId,kind,track,phase:'opening',source:null,media:null,timer:null};
    this.active=op;this.phase(op,'opening');this.event('input-requested',op);
    try {
      if(kind==='microphone') {
        let media;
        try{media=await this.microphone.request();}
        catch(error){if(this.owns(op))throw error;this.event('late-input-error',op,{error:inputError(error)});return false;}
        this.streams.add(media);this.event('input-acquired',op);
        if(!this.owns(op)){this.closeStream(media,op,true);return false;}
        op.media=media;
        if(media.getTracks().some(t=>t.readyState==='ended'))throw new Error('Input ended before capture');
        op.source=this.context.createMediaStreamSource(media);
        for(const track of media.getTracks())track.onended=()=>{if(this.owns(op))this.cancel('Input disconnected · take discarded');};
      } else {op.source=this.context.createOscillator();op.source.frequency.value=220;op.source.type='sine';}
      if(!this.owns(op)){this.releaseResources(op);return false;}
      this.node.port.postMessage({type:'start',id:op.id,frames:this.context.sampleRate*16});
      op.source.connect(this.node);op.source.start?.();this.phase(op,'recording');this.event('capture-started',op);return true;
    } catch(error) {
      if(this.owns(op)){this.cancel('Input unavailable');this.onError(inputError(error));}
      else this.releaseResources(op);
      return false;
    }
  }
  release() {
    const op=this.active;if(!op)return;
    if(op.phase==='opening'){this.cancel('Released before input opened · hold again');return;}
    if(op.phase!=='recording')return;
    this.phase(op,'finishing');this.event('capture-released',op);
    this.node.port.postMessage({type:'stop',id:op.id});this.releaseResources(op);
    op.timer=setTimeout(()=>{if(this.owns(op))this.cancel('Capture did not finish · try again');},this.finishTimeoutMs);
  }
  cancel(reason='Take discarded') {
    const op=this.active;if(!op)return;
    this.active=null;this.node.port.postMessage({type:'cancel',id:op.id});this.releaseResources(op);
    this.event('capture-cancelled',op,{reason});this.onPhase({phase:'idle',reason,id:op.id,track:op.track,kind:op.kind});
  }
  message(m) {
    const op=this.active;
    if(!op||this.disposed||m.id!==op.id)return;
    if(m.type==='capture-meter'){if(op.phase==='recording')this.onMeter(m);return;}
    if(m.type!=='take'||!['recording','finishing'].includes(op.phase))return;
    if(!(m.samples instanceof Float32Array)||!Number.isInteger(m.used)||m.used<0||m.used>m.samples.length||m.samples.length>this.context.sampleRate*16||m.rate!==this.context.sampleRate){this.cancel('Invalid capture buffer');return;}
    this.active=null;this.releaseResources(op);this.event('take-delivered',op,{frames:m.used,rate:m.rate});this.onPhase({phase:'idle',id:op.id,track:op.track,kind:op.kind});
    this.onTake({...m,track:op.track,kind:op.kind});
  }
  dispose() {
    if(this.disposed)return;this.cancel('Capture stopped');this.disposed=true;
    this.node.port.onmessage=null;this.node.onprocessorerror=null;
  }
  snapshot() {return {phase:this.active?.phase??'idle',track:this.active?.track??null,kind:this.active?.kind??null,ownedLiveTracks:[...this.streams].flatMap(s=>s.getTracks()).filter(t=>t.readyState!=='ended').length,pendingPermission:this.microphone.pending,disposed:this.disposed};}
}
