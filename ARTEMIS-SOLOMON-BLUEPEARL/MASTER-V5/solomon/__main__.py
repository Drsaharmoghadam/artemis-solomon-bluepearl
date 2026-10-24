```python
"""CLI for a web-connectable online identity-continuity *context* protocol."""
from __future__ import annotations
import argparse,json,sys
from .contract import is_invocation,ACK,public_contract
from .catalog import load_manifest,verify_sources
from .compose import build_context
from .online import fetch_online_sources
from .webserver import serve

def main(argv=None):
    p=argparse.ArgumentParser(description='Solomon Return v5 public persona/context resolver')
    sub=p.add_subparsers(dest='cmd',required=True)
    r=sub.add_parser('recognize');r.add_argument('phrase')
    c=sub.add_parser('context');c.add_argument('--scope',choices=('core','extended','full'),default='core');c.add_argument('--max-chars',type=int,default=75000)
    sub.add_parser('validate')
    sub.add_parser('contract')
    a=sub.add_parser('online');a.add_argument('--urls',nargs='*')
    s=sub.add_parser('serve');s.add_argument('--host',default='127.0.0.1');s.add_argument('--port',type=int,default=8787)
    args=p.parse_args(argv)
    try:
        if args.cmd=='recognize':
            matched=is_invocation(args.phrase)
            print(json.dumps({'matched':matched,'reply':ACK if matched else None,
              'autonomous_identity_transfer':False,'user_authenticated':False},ensure_ascii=False,indent=2))
            return 0 if matched else 1
        if args.cmd=='context':
            print(build_context(args.scope,args.max_chars)['context']);return 0
        if args.cmd=='validate':
            m=load_manifest();errors=verify_sources(m)
            print(json.dumps({'ok':not errors,'sources':len(m['sources']),'errors':errors},ensure_ascii=False,indent=2));return int(bool(errors))
        if args.cmd=='contract':
            print(json.dumps(public_contract(),ensure_ascii=False,indent=2));return 0
        if args.cmd=='online':
            data=fetch_online_sources(args.urls or None)
            # Deliberately limit printed web content and preserve source names.
            print(json.dumps({'documents':[{**{k:v for k,v in d.items() if k!='text'},'excerpt':d['text'][:7000]} for d in data['documents']],
                              'errors':data['errors']},ensure_ascii=False,indent=2));return int(not data['documents'])
        if args.cmd=='serve':
            serve(args.host,args.port);return 0
    except (ValueError,OSError,TypeError) as e:
        print('Solomon Return error: '+str(e),file=sys.stderr);return 2
    return 2
if __name__=='__main__':raise SystemExit(main())

```
