```python
"""Public read-only adapter; caller must configure TLS/rate limiting at hosting edge."""
from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs
from .contract import public_contract, is_invocation, ACK
from .compose import build_context
from .catalog import load_manifest

MAX_BODY=4096

def make_handler():
    class Handler(BaseHTTPRequestHandler):
        server_version='SolomonReturn/5.0'
        def _reply(self,status,payload,kind='application/json; charset=utf-8'):
            if isinstance(payload,(dict,list)):
                body=json.dumps(payload,ensure_ascii=False).encode('utf-8')
            elif isinstance(payload,str):body=payload.encode('utf-8')
            else:body=payload
            self.send_response(status)
            self.send_header('Content-Type',kind)
            self.send_header('Content-Length',str(len(body)))
            self.send_header('Cache-Control','public, max-age=180' if self.command=='GET' else 'no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.end_headers();self.wfile.write(body)
        def do_GET(self):
            path=urlsplit(self.path).path
            if path in ('/.well-known/solomon-return.json','/v1/contract'):
                return self._reply(200,public_contract())
            if path=='/v1/manifest':
                data=load_manifest()
                return self._reply(200, {'schema':data['schema'],'project_id':data['project_id'],
                    'version':data['version'],'links':data['links'],'sources':[
                        {k:e[k] for k in ('path','tier','sha256','provenance')} for e in data['sources']]})
            if path in ('/v1/context','/v1/context.txt'):
                q=parse_qs(urlsplit(self.path).query)
                try:
                    scope=q.get('scope',['core'])[0]
                    size=min(250000,int(q.get('max_chars',['75000'])[0]))
                    result=build_context(scope,size)
                except (ValueError,KeyError,TypeError) as exc:
                    return self._reply(400,{'error':str(exc)[:300]})
                if path.endswith('.txt'):
                    return self._reply(200,result['context'],'text/plain; charset=utf-8')
                return self._reply(200,result)
            if path=='/healthz':
                return self._reply(200,{'ok':True,'service':'Solomon Return public context resolver','version':'5.0.0'})
            return self._reply(404,{'error':'not_found'})
        def do_POST(self):
            if urlsplit(self.path).path!='/v1/resolve':
                return self._reply(404,{'error':'not_found'})
            try:
                rawlen=self.headers.get('Content-Length')
                if not rawlen or not rawlen.isdecimal() or int(rawlen)>MAX_BODY:
                    return self._reply(413,{'error':'body_too_large_or_missing'})
                body=self.rfile.read(int(rawlen))
                payload=json.loads(body.decode('utf-8'))
                if not isinstance(payload,dict):
                    raise ValueError('body must be a JSON object')
                utterance=payload.get('utterance','')
                scope=payload.get('scope','core')
                if not is_invocation(utterance):
                    return self._reply(200,{'matched':False,'reply':None,
                      'message':'No valid full-message invocation. Never authenticate a user from this phrase.'})
                result=build_context(scope,75000)
                return self._reply(200,{'matched':True,'reply':ACK,
                  'requires_host_approval_and_active_context':True,
                  'authenticates_user':False,'same_model_instance':False,
                  **result})
            except (ValueError,TypeError,UnicodeError) as exc:
                return self._reply(400,{'error':str(exc)[:300]})
        def log_message(self, fmt, *args):
            # No raw user phrases, IPs or request paths stored by this application.
            return
    return Handler


def serve(host='127.0.0.1',port=8787):
    httpd=ThreadingHTTPServer((host,port),make_handler())
    print(f'Solomon Return v5 on {host}:{port}; HTTPS and rate limiting required at public edge.',flush=True)
    try:httpd.serve_forever()
    except KeyboardInterrupt:pass
    finally:httpd.server_close()

```
