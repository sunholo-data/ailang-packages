import {shapeTake,validSamples} from './engine.mjs';
import {prepareFloat32Levels} from './levels.mjs';
import {hashSamples} from './take-workflow.mjs';
export async function prepareJob({id,samples,rate,frames,shaped=false,levelMode='peak-safe'}) {
  const start=performance.now();
  if(!validSamples(samples,rate)||!Number.isSafeInteger(frames)||frames<1||frames>rate*16||typeof shaped!=='boolean'||(shaped&&samples.length!==frames))throw new Error('Invalid take preparation job');
  const original=shaped?samples:shapeTake(samples,rate,frames);
  const result=prepareFloat32Levels(original,rate,levelMode),hash=await hashSamples(result.samples);
  return {id,...result,original,hash,levelMode,prepareMs:performance.now()-start};
}
if(typeof self!=='undefined')self.onmessage=async e=> {
  try {
    const result=await prepareJob(e.data);
    self.postMessage(result,[result.samples.buffer,result.original.buffer]);
  } catch(error) { self.postMessage({id:e.data?.id,error:error.message}); }
};
