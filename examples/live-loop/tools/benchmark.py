#!/usr/bin/env python3
"""Same pure handler/command sequence for evaluator vs strict VM, CLI inclusive."""
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from server import invoke

def run(engine):
    state=invoke({'schema':1,'op':'init'},engine)[0]['state']
    observations=[]
    for i in range(25):
        kind='configure' if i==0 else 'parameter'
        c={'kind':kind,'id':f'bench-{i}','epoch':state['epoch'],'expected':state['revision'],'now':0,'rate':48000,'bpm':120,'origin':48000,'track':1,'level':i,'pan':0,'muted':False}
        response,ms=invoke({'schema':1,'state':state,'command':c},engine)
        if not response['ok']:raise RuntimeError(response)
        state=response['state'];observations.append(ms)
    ordered=sorted(observations)
    return {'ms':observations,'medianMs':statistics.median(observations),'p95Ms':ordered[23],'finalState':state}
result={'version':subprocess.check_output(['ailang','version'],text=True),'platform':platform.platform(),'measuredAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'probe':'1 configure + 24 parameter commands; process launch/parse/compile/call/encode included','engines':{e:run(e) for e in ['eval','vm']}}
result['equalFinalStates']=result['engines']['eval']['finalState']==result['engines']['vm']['finalState']
print(json.dumps(result,indent=2))
