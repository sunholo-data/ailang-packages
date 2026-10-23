// Main-thread test orchestration only. Nothing here runs in an audio callback.
export class EventWaiters {
  constructor(signal) { this.signal=signal;this.pending=new Set(); }
  wait(predicate,timeout=12000) {
    if(this.signal.aborted)return Promise.reject(new Error(String(this.signal.reason)));
    if(this.pending.size>=8)return Promise.reject(new Error('Check waiter limit'));
    return new Promise((resolve,reject)=> {
      const entry={accept:null};let timer;
      const finish=(error,value)=>{clearTimeout(timer);this.signal.removeEventListener('abort',abort);this.pending.delete(entry);error?reject(error):resolve(value);};
      const abort=()=>finish(new Error(String(this.signal.reason)));
      entry.accept=value=>{try{if(predicate(value))finish(null,value);}catch(error){finish(error);}};
      this.pending.add(entry);this.signal.addEventListener('abort',abort,{once:true});
      timer=setTimeout(()=>finish(new Error('Timed out waiting for audio/worker acknowledgement')),timeout);
    });
  }
  dispatch(value) { for(const entry of [...this.pending])entry.accept(value); }
}
export function delay(ms,signal) {
  if(signal.aborted)return Promise.reject(new Error(String(signal.reason)));
  return new Promise((resolve,reject)=>{
    const abort=()=>{clearTimeout(timer);reject(new Error(String(signal.reason)));};
    const timer=setTimeout(()=>{signal.removeEventListener('abort',abort);resolve();},ms);
    signal.addEventListener('abort',abort,{once:true});
  });
}
export function timingSummary(values) {
  if(!values.length)return null;
  if(values.length>512 || values.some(x=>!Number.isFinite(x)||x<0))throw new Error('Invalid timing samples');
  const sorted=[...values].sort((a,b)=>a-b),n=sorted.length;
  return {count:n,medianMs:n%2?sorted[Math.floor(n/2)]:(sorted[n/2-1]+sorted[n/2])/2,p95Ms:sorted[Math.ceil(n*.95)-1],maxMs:sorted[n-1]};
}
