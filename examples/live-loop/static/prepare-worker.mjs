import {prepareTake} from './engine.mjs';
self.onmessage=async e=> {
  const {id,samples,rate,frames}=e.data, start=performance.now();
  try {
    const output=prepareTake(samples,rate,frames);
    const digest=await crypto.subtle.digest('SHA-256',output.buffer);
    const hash=Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,'0')).join('');
    self.postMessage({id,samples:output,hash,prepareMs:performance.now()-start},[output.buffer]);
  } catch(error) { self.postMessage({id,error:error.message}); }
};
