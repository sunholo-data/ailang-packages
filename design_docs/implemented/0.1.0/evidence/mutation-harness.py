#!/usr/bin/env python3
"""Read-only native mutation controls for sunholo/social_dynamics.
Each control copies the package, changes one named behaviour, checks compilation,
and executes the existing targeted native tests. Never edits the source package.
"""
from pathlib import Path
import shutil, subprocess, json, re, hashlib, time
REPO = Path(__file__).resolve().parents[4]
SRC = REPO / 'packages/social-dynamics'
import os
BIN = os.environ.get('AILANG', 'ailang')
ROOT = Path('/private/tmp/social-mutation-controls-20261009')
OUT = REPO / '.ailang/state/evaluations/social_mutations.json'
ANSI = re.compile(r'\x1b\[[0-9;]*m')

MUTATIONS = [
 dict(id='reverse_directed_relationship', file='indicators.ail', test='indicators_test.ail', old='r.from == from && r.to == to && r.dimension == dimension', new='r.from == to && r.to == from && r.dimension == dimension', old2='old.from == from && old.to == to && old.dimension == dimension', new2='old.from == to && old.to == from && old.dimension == dimension', description='Apply A→B relationship delta to B→A instead.'),
 dict(id='unseen_evidence_bypass', file='relationships.ail', test='relationships_test.ail', old='if not knows(s, observer, evidence) then Err(UnseenEvidence(evidence))', new='if false then Err(UnseenEvidence(evidence))', description='Permit appraisal context for evidence unknown to observer.'),
 dict(id='repeat_reservation', file='tasks.ail', test='engine_test.ail', old='match reserve(s.resources, r.costs)', new='match reserve(s.resources, r.costs ++ r.costs)', description='Apply recipe reservation a second time during one task acceptance.'),
 dict(id='ignore_cooldown', file='conditions.ail', test='conditions_test.ail', old='match add(s.tick, r.cooldown)', new='match add(s.tick, 0)', description='Discard configured cooldown after recovery.'),
 dict(id='early_condition_entry', file='conditions.ail', test='conditions_test.ail', old='r.duration', new='1', count=4, description='Replace duration with one tick in both condition scheduling and entry guard.'),
 dict(id='simultaneous_boundary_reorder', file='engine.ail', test='engine_test.ail', old='if a.phase < b.phase then 0 - 1 else if a.phase > b.phase then 1', new='if a.phase < b.phase then 1 else if a.phase > b.phase then 0 - 1', description='Execute condition phase before task phase at same tick.'),
 dict(id='accept_stale_revision', file='proposals.ail', test='proposals_test.ail', old='if p.baseRevision != s.revision then Err(StaleRevision(p.id))', new='if false then Err(StaleRevision(p.id))', description='Remove stale nonduplicate revision gate.'),
 dict(id='partial_invalid_proposal_commit', file='proposals.ail', test='proposals_test.ail', old='Err(e) => Err(e), Ok(step) => stage(c, policies, step.state, principal, rest, concat(events, step.events))', new='Err(e) => Ok({state: s, disposition: Applied, events: events}), Ok(step) => stage(c, policies, step.state, principal, rest, concat(events, step.events))', description='On a failed later operation, return successfully staged earlier operations.'),
]

def digest():
    return {str(p.relative_to(SRC)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SRC.rglob('*')) if p.is_file()}

def call(cwd, args, label):
    start=time.monotonic()
    p=subprocess.run([BIN,*args], cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
    clean=ANSI.sub('',p.stdout)
    log=ROOT/f'{label}.log'; log.write_text(clean)
    m=re.search(r'(\d+) tests: (\d+) passed, (\d+) failed, (\d+) skipped',clean)
    return dict(command=[BIN,*args],cwd=str(cwd),exit_code=p.returncode,seconds=round(time.monotonic()-start,3),counts=({k:int(v) for k,v in zip(['total','passed','failed','skipped'],m.groups())} if m else None),log=str(log),failed_tests=re.findall(r'✗ ([^\n]+)',clean),assertion_failures=clean.count('expected true, got false'),compilation_error=('pipeline error:' in clean or 'parse\n' in clean))

def copy_package(name):
    target=ROOT/name
    if target.exists(): shutil.rmtree(target)
    frozen = SRC if name == 'baseline' else ROOT/'baseline'
    shutil.copytree(frozen,target,ignore=shutil.ignore_patterns('.ailang','_namedtest_body_*.ail'))
    return target

def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    before=digest()
    result=dict(schema='social_mutation_controls/1',toolchain=subprocess.check_output([BIN,'version'],text=True).strip(),source=str(SRC),source_sha256=before,baselines=[],mutants=[],status='in_progress')
    baseline=copy_package('baseline')
    result['baseline_compile']=call(baseline,['check','--package','.'],'baseline_compile')
    if result['baseline_compile']['exit_code']!=0: raise RuntimeError('baseline does not compile')
    for test in sorted({m['test'] for m in MUTATIONS}):
        b=call(baseline,['test',test],'baseline_'+test)
        result['baselines'].append(b)
        print('baseline',test,b['counts'],flush=True)
        if b['exit_code']!=0 or not b['counts'] or b['counts']['failed'] or b['counts']['skipped']: raise RuntimeError('baseline native tests failed')
    for spec in MUTATIONS:
        cwd=copy_package(spec['id']); file=cwd/spec['file']; text=file.read_text()
        count=text.count(spec['old']); expected=spec.get('count',1)
        if count!=expected: raise RuntimeError(f"{spec['id']} anchor count {count} expected {expected}")
        text=text.replace(spec['old'],spec['new'])
        if 'old2' in spec:
            if text.count(spec['old2'])!=1: raise RuntimeError('second mutation anchor mismatch')
            text=text.replace(spec['old2'],spec['new2'])
        file.write_text(text)
        compile_result=call(cwd,['check','--package','.'],spec['id']+'_compile')
        record=dict(spec,compile=compile_result,status='not_compiling')
        if compile_result['exit_code']==0:
            run=call(cwd,['test',spec['test']],spec['id']+'_native')
            record['native']=run
            record['status']='killed' if run['counts'] and run['counts']['failed']>0 and run['assertion_failures']>0 and not run['compilation_error'] else ('survived' if run['exit_code']==0 else 'inconclusive_runtime_failure')
        result['mutants'].append(record)
        print(spec['id'],record['status'],record.get('native',{}).get('counts'),flush=True)
        OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(result,indent=2)+'\n')
    after=digest(); result['source_unchanged']=before==after
    result['summary']={status:sum(m['status']==status for m in result['mutants']) for status in ['killed','survived','not_compiling','inconclusive_runtime_failure']}
    result['status']='pass' if result['source_unchanged'] and result['summary']['killed']==8 else 'fail'
    OUT.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],summary=result['summary'],source_unchanged=result['source_unchanged'],report=str(OUT))))
    return 0 if result['status']=='pass' else 1
if __name__=='__main__': raise SystemExit(main())
