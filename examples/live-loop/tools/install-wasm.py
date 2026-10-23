#!/usr/bin/env python3
"""Install an explicitly chosen local AILANG WASM binary and matching Go shim.
Never downloads, modifies core, or commits runtime artifacts. Version is measured
inside the worker; filenames/mtime alone are not version evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('wasm',type=Path)
p.add_argument('wasm_exec',type=Path)
a=p.parse_args()
raw=a.wasm.read_bytes()
if raw[:4]!=b'\0asm':p.error('not a WebAssembly binary')
root=Path(__file__).resolve().parent.parent/'.runtime'
root.mkdir(exist_ok=True)
shutil.copyfile(a.wasm,root/'ailang.wasm')
shutil.copyfile(a.wasm_exec,root/'wasm_exec.js')
(root/'manifest.json').write_text(json.dumps({'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'source':str(a.wasm.resolve()),'shim':str(a.wasm_exec.resolve())},indent=2)+'\n')
print('Installed optional runtime; browser probe will report version and compatibility.')
