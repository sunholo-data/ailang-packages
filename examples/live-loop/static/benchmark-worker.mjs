const summary=values=> {
  const s=[...values].sort((a,b)=>a-b);return `n=${s.length} · median ${s[Math.floor(s.length/2)].toFixed(2)} ms · p95 ${s[Math.ceil(s.length*.95)-1].toFixed(2)} ms`;
};
self.onmessage=async e=> {
  const times=[],mode=e.data.mode,start=performance.now();
  try {
    if(mode==='native') {
      for(let i=0;i<20;i++) {
        const r=await fetch('/api/probe',{method:'POST',headers:{'Content-Type':'application/json','X-Loop-Lab':'1'},body:JSON.stringify({op:'init'})});
        const data=await r.json();if(!r.ok||!data.ok)throw new Error(data.error||'native probe failed');times.push(data.bridgeMs);
      }
      self.postMessage({label:'Native init probe (includes CLI startup)',summary:summary(times),times});
    } else {
      const manifestResponse=await fetch('/runtime/manifest.json');
      if(!manifestResponse.ok)throw new Error('Optional runtime absent. See tools/install-wasm.py; native bridge remains active.');
      const manifest=await manifestResponse.json();
      await import('/runtime/wasm_exec.js');
      const go=new globalThis.Go(),bytes=await(await fetch('/runtime/ailang.wasm')).arrayBuffer();
      const {instance}=await WebAssembly.instantiate(bytes,go.importObject);go.run(instance).catch(()=>{});
      const waitStart=performance.now();while(typeof globalThis.ailangLoadModule!=='function') {if(performance.now()-waitStart>6000)throw new Error('WASM runtime initialization timeout');await new Promise(r=>setTimeout(r,5));}
      const version=globalThis.ailangVersion(),source=await(await fetch('/planner.ail')).text(),loadStart=performance.now();
      const loaded=globalThis.ailangLoadModule('sunholo/live_loop_lab/planner',source);
      if(!loaded.success)throw new Error(`Runtime ${JSON.stringify(version)} cannot load current planner: ${loaded.error}`);
      const loadMs=performance.now()-loadStart;
      for(let i=0;i<20;i++) {
        const callStart=performance.now(),r=globalThis.ailangCall('sunholo/live_loop_lab/planner','handle',JSON.stringify({schema:1,op:'init'}));
        if(!r.success)throw new Error(r.error);let result=r.result;
        if(typeof result==='string'&&result.endsWith(' :: String'))result=JSON.parse(result.slice(0,-10));
        if(!JSON.parse(result).ok)throw new Error('WASM probe returned invalid state');times.push(performance.now()-callStart);
      }
      self.postMessage({label:`WASM worker ${JSON.stringify(version)}`,summary:`${summary(times)} · source load ${loadMs.toFixed(1)} ms · cold ${ (performance.now()-start).toFixed(1)} ms · sha256 ${manifest.sha256.slice(0,12)} · runtime uses its exported call engine, not CLI --strict-bytecode`,times,manifest,version});
    }
  } catch(error) {self.postMessage({label:mode==='native'?'Native probe':'WASM worker',error:error.message});}
};
