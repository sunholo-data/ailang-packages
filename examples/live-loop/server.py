#!/usr/bin/env python3
"""Local, single-session bridge. Raw captures have no transport endpoint."""
import argparse
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent
MAX_BODY = 65536
FIELDS = {'id','kind','epoch','expected','track','base','now','ready','origin','rate','bpm','level','pan','muted','asset','hash','pendingId','at','applied'}
TEXT_FIELDS = {'id','kind','asset','hash','pendingId'}


def invoke(payload, engine='vm'):
    # args-file is a JSON string argument, not an argv array. No shell or caps.
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as f:
        json.dump(json.dumps(payload, separators=(',', ':'), ensure_ascii=False), f)
        f.flush()
        command = ['ailang', 'run']
        if engine == 'vm':
            command += ['--strict-bytecode']
        command += ['--entry','handle','--args-file',f.name,'--package-dir',str(ROOT),str(ROOT/'planner.ail')]
        start = time.perf_counter()
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=3, check=True)
        response = json.loads(result.stdout)
        return response, (time.perf_counter()-start)*1000


class Session:
    def __init__(self):
        self.lock = threading.Lock()
        self.state = invoke({'schema':1,'op':'init'})[0]['state']
        self.timings = []

    def command(self, command):
        if not isinstance(command, dict) or set(command)-FIELDS:
            raise ValueError('metadata commands only; unknown field')
        for key, value in command.items():
            if key in TEXT_FIELDS:
                valid = isinstance(value,str) and len(value)<=96
            elif key == 'muted':
                valid = isinstance(value,bool)
            else:
                valid = type(value) is int and -1000000000000<=value<=1000000000000
            if not valid:
                raise ValueError('flat typed metadata only')
        if not self.lock.acquire(blocking=False):
            return {'ok':False,'error':'planner busy; retry serially'}, 409
        try:
            response, ms = invoke({'schema':1,'state':self.state,'command':command})
            if response['ok']:
                self.state = response['state']
            self.timings = (self.timings+[ms])[-128:]
            response.update(state=self.state, bridgeMs=round(ms,3))
            return response, 200 if response['ok'] else 409
        finally:
            self.lock.release()


class Server(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, address, public_origin=None):
        self.session = Session()
        self.probe_lock = threading.Lock()
        self.public_origin = public_origin
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    server_version = 'LoopLab/0.1'
    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, fmt, *args):
        # No request bodies, query strings, takes or command payloads in logs.
        pass

    def allowed_host(self):
        host = self.headers.get('Host','')
        port = self.server.server_port
        return host in {f'127.0.0.1:{port}',f'localhost:{port}'} | ({urlsplit(self.server.public_origin).netloc} if self.server.public_origin else set())

    def send(self, status, data, mime='application/json'):
        if isinstance(data, dict):
            data = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type',mime)
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self'; connect-src 'self'; worker-src 'self'; img-src 'self' data:; media-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self.allowed_host():
            return self.send(403, {'error':'unrecognized host'})
        route = urlsplit(self.path).path
        if route == '/api/state':
            with self.server.session.lock:
                return self.send(200, {'state':self.server.session.state,'timings':self.server.session.timings})
        if route == '/planner.ail':
            return self.send(200, (ROOT/'planner.ail').read_bytes(), 'text/plain; charset=utf-8')
        # Only a small optional, explicitly installed WASM runtime can be served.
        if route in ['/runtime/ailang.wasm','/runtime/wasm_exec.js','/runtime/manifest.json']:
            file = ROOT/'.runtime'/route.rsplit('/',1)[1]
        else:
            file = ROOT/'static'/('index.html' if route=='/' else unquote(route).lstrip('/'))
            if not file.resolve().is_relative_to((ROOT/'static').resolve()):
                return self.send(404, {'error':'not found'})
        if not file.is_file() or file.is_symlink():
            return self.send(404, {'error':'not found'})
        mime = 'application/wasm' if file.suffix=='.wasm' else mimetypes.guess_type(file)[0] or 'application/octet-stream'
        return self.send(200,file.read_bytes(),mime)

    def do_POST(self):
        if not self.allowed_host():
            return self.send(403, {'error':'unrecognized host'})
        origin = self.headers.get('Origin')
        accepted = {f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'} | ({self.server.public_origin} if self.server.public_origin else set())
        if origin not in accepted or self.headers.get('Content-Type')!='application/json' or self.headers.get('X-Loop-Lab')!='1':
            return self.send(403, {'error':'same-origin JSON commands required'})
        if self.path not in ('/api/command','/api/probe'):
            return self.send(404, {'error':'not found'})
        try:
            length = int(self.headers.get('Content-Length','0'))
            if length <= 0 or length > MAX_BODY:
                return self.send(413, {'error':'request size limit'})
            body = json.loads(self.rfile.read(length))
            if self.path == '/api/probe':
                if body != {'op':'init'}:
                    raise ValueError('fixed probe only')
                if not self.server.probe_lock.acquire(blocking=False):
                    return self.send(409,{'error':'probe busy'})
                try:
                    response, ms = invoke({'schema':1,'op':'init'})
                    return self.send(200,{'ok':response['ok'],'bridgeMs':ms})
                finally:
                    self.server.probe_lock.release()
            if not isinstance(body,dict) or set(body)!={'command'}:
                raise ValueError('command envelope required')
            response, status = self.server.session.command(body['command'])
            self.send(status,response)
        except (ValueError, UnicodeError):
            self.send(400,{'error':'invalid metadata command'})
        except TimeoutError:
            self.send(408,{'error':'request read timeout'})
        except (subprocess.SubprocessError, KeyError):
            self.send(503,{'error':'AILANG planner unavailable; keep current audio'})


def fixtures():
    target = ROOT/'static'/'audio'
    target.mkdir(exist_ok=True)
    if not all((target/f'demo-{i}.wav').is_file() for i in range(1,5)):
        print('Generating four original AILANG phrases…', flush=True)
        result = subprocess.run(['ailang','run','--entry','generate','--caps','FS,IO','--package-dir',str(ROOT),str(ROOT/'assets.ail')],cwd=ROOT,capture_output=True,text=True,timeout=180,check=True)
        if 'OK:' not in result.stdout:
            raise RuntimeError('fixture generation failed')
    manifest = {f'demo-{i}':hashlib.sha256((target/f'demo-{i}.wav').read_bytes()).hexdigest() for i in range(1,5)}
    (target/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8976)
    parser.add_argument('--public-origin', help='explicit private HTTPS preview origin, e.g. Tailscale Serve')
    args=parser.parse_args()
    if args.public_origin and (urlsplit(args.public_origin).scheme!='https' or urlsplit(args.public_origin).path not in ('','/')):
        parser.error('public-origin must be an HTTPS origin')
    fixtures()
    with Server(('127.0.0.1',args.port),args.public_origin.rstrip('/') if args.public_origin else None) as server:
        print(f'Loop Lab: http://127.0.0.1:{args.port}',flush=True)
        try: server.serve_forever()
        except KeyboardInterrupt: pass
