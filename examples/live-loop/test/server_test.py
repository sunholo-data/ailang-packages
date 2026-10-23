import concurrent.futures
import http.client
import importlib.util
import json
from pathlib import Path
import sys
import threading
import unittest

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from server import Server, Session, invoke

class PlannerIntegration(unittest.TestCase):
    def test_json_guards_and_epoch_lifecycle(self):
        s=Session()
        def command(kind,**extra):
            return {'id':kind+str(s.state['revision']),'kind':kind,'epoch':s.state['epoch'],'expected':s.state['revision'],'now':0,**extra}
        start=command('configure',rate=48000,bpm=120,origin=48000)
        self.assertEqual(s.command(start)[1],200)
        initial=s.state.copy()
        p=command('prepare',track=1,base=0,ready=48001,asset='take',hash='a'*64,now=48001)
        self.assertEqual(s.command(p)[1],200)
        planned=s.state['tracks'][0]['pending']['at']
        self.assertEqual(planned,432000)
        self.assertEqual(s.command(command('activate',track=1,base=0,pendingId=p['id'],at=planned,applied=planned,now=planned))[1],409)
        self.assertEqual(s.command(command('schedule',track=1,base=0,pendingId=p['id'],at=planned,now=planned-128))[1],200)
        self.assertEqual(s.command(command('activate',track=1,base=0,pendingId=p['id'],at=planned,applied=planned,now=planned))[1],200)
        self.assertEqual(s.state['tracks'][0]['revision'],1)
        self.assertEqual(s.command(command('reset'))[1],200)
        self.assertFalse(s.state['running']);self.assertEqual(s.state['epoch'],2)
        self.assertEqual(s.command(start)[1],409)

    def test_real_json_decoder_rejects_fractional_missing_and_wrong_boolean_types(self):
        s=Session()
        start={'id':'start','kind':'configure','epoch':0,'expected':0,'now':0,'rate':48000,'bpm':120,'origin':48000}
        s.command(start)
        base={'id':'p','kind':'parameter','epoch':1,'expected':1,'now':0,'track':1,'level':50,'pan':0,'muted':False}
        for patch in [{'muted':'false'},{'level':1.5},{'track':5},{'now':-1},{'epoch':0},{'expected':0}]:
            with self.subTest(patch=patch):
                result,_=invoke({'schema':1,'state':s.state,'command':base|patch})
                self.assertFalse(result['ok'])
        with self.assertRaises(ValueError):s.command(base|{'samples':[.1]})
        with self.assertRaises(ValueError):s.command(['raw'])
        for key in ['muted','now','id']:
            with self.assertRaises(ValueError):s.command(base|{key:[.1,.2]})

    def test_missing_state_fields_are_rejected(self):
        state=Session().state
        for field in ['running','seen','tracks','epoch']:
            damaged={k:v for k,v in state.items() if k!=field}
            result,_=invoke({'schema':1,'state':damaged,'command':{'id':'reset','kind':'reset','epoch':0,'expected':0,'now':0}})
            self.assertFalse(result['ok'],field)

class HTTPBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=Server(('127.0.0.1',0))
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def request(self,path='/',body=None,headers=None,method=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=6)
        c.request(method or ('POST' if body is not None else 'GET'),path,body,headers or {})
        r=c.getresponse();data=r.read();status=r.status;h=dict(r.getheaders());c.close();return status,data,h
    def headers(self):return {'Origin':f'http://127.0.0.1:{self.server.server_port}','Content-Type':'application/json','X-Loop-Lab':'1'}
    def test_static_root_and_repo_traversal(self):
        status,data,headers=self.request();self.assertEqual(status,200);self.assertIn(b'Loop Lab',data);self.assertIn('Content-Security-Policy',headers)
        for path in ['/../ailang.toml','/%2e%2e/ailang.toml','/.git/config','/api/capture','/audio/']:
            self.assertEqual(self.request(path)[0],404,path)
    def test_host_origin_raw_upload_and_size_rejection(self):
        self.assertEqual(self.request(headers={'Host':'evil.example'})[0],403)
        self.assertEqual(self.request('/api/command','{}')[0],403)
        h=self.headers()|{'Origin':'https://evil.example'}
        self.assertEqual(self.request('/api/command','{}',h)[0],403)
        self.assertEqual(self.request('/api/command','x'*65537,self.headers())[0],413)
        self.assertEqual(self.request('/api/command',json.dumps({'command':{'samples':[.5]}}),self.headers())[0],400)
        self.assertEqual(self.request('/api/capture','{}',self.headers())[0],404)
    def test_probe_is_fixed_and_does_not_mutate_session(self):
        before=self.request('/api/state')[1]
        self.assertEqual(self.request('/api/probe','{"op":"init"}',self.headers())[0],200)
        self.assertEqual(self.request('/api/probe','{"op":"anything"}',self.headers())[0],400)
        after=self.request('/api/state')[1];self.assertEqual(before,after)

if __name__=='__main__':unittest.main()
