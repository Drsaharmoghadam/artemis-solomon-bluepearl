"""Optional safe HTTPS retrieval of canonical PUBLIC project sources; no search-API credentials."""
from __future__ import annotations
from urllib.request import Request, urlopen, build_opener, HTTPSHandler, HTTPRedirectHandler
from urllib.parse import urlparse
from html.parser import HTMLParser
import ssl, datetime

APPROVED_HOSTS=frozenset({
    'drmoghadamcounseling.ir', 'www.drmoghadamcounseling.ir',
    'raw.githubusercontent.com','github.com','gitlab.com', 'archive.org',
})
DEFAULT_URLS=['https://raw.githubusercontent.com/Drsaharmoghadam/artemis-solomon-bluepearl/main/ARTEMIS-SOLOMON-BLUEPEARL/MASTER-V5/10-ROLE-ENACTMENT.md', 'https://raw.githubusercontent.com/Drsaharmoghadam/artemis-solomon-bluepearl/main/ARTEMIS-SOLOMON-BLUEPEARL/MASTER-V5/11-HOST-EXECUTION-PROTOCOL.json', 'https://raw.githubusercontent.com/Drsaharmoghadam/artemis-solomon-bluepearl/main/ARTEMIS-SOLOMON-BLUEPEARL/MASTER-V5/COLLABORATION-BEHAVIOR-v5.1.json', 'https://raw.githubusercontent.com/Drsaharmoghadam/artemis-solomon-bluepearl/main/ARTEMIS-SOLOMON-BLUEPEARL/MASTER-V5/09-ARTEMIS-COGNITIVE-INTERACTION-MAP.md', 'https://raw.githubusercontent.com/Drsaharmoghadam/artemis-solomon-bluepearl/main/ARTEMIS-SOLOMON-BLUEPEARL/MASTER-V5/sources/profile/ARTEMIS-PROFILE.md', 'https://raw.githubusercontent.com/Drsaharmoghadam/artemis-solomon-bluepearl/main/ARTEMIS-SOLOMON-BLUEPEARL/MASTER-V5/02-CONTINUITY-NOW.md']
class TextHTML(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style','noscript'): self.skip+=1
        if tag in ('p','h1','h2','h3','li','br'): self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in ('script','style','noscript') and self.skip: self.skip-=1
    def handle_data(self,data):
        if not self.skip: self.parts.append(data)
    def as_text(self): return ' '.join(''.join(self.parts).split())

class ValidatingRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        assert_public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def assert_public_url(url):
    parts=urlparse(url)
    if parts.scheme!='https' or not parts.hostname or parts.hostname.lower() not in APPROVED_HOSTS:
        raise ValueError('HTTPS URL host not on approved source allowlist')
    if parts.username or parts.password or parts.port not in (None,443):
        raise ValueError('credentials/ports are not accepted')
    return url


def fetch_public_document(url, max_bytes=200_000, timeout=8):
    assert_public_url(url)
    if not isinstance(max_bytes,int) or max_bytes<1024 or max_bytes>2_000_000:
        raise ValueError('invalid fetch limit')
    opener=build_opener(HTTPSHandler(context=ssl.create_default_context()), ValidatingRedirect())
    req=Request(url,headers={'User-Agent':'Solomon-Return-Public-Resolver/5.6 (public archived documents)','Accept':'text/plain,text/markdown,text/html,application/json'})
    with opener.open(req,timeout=timeout) as resp:
        assert_public_url(resp.url)
        mime=resp.headers.get_content_type()
        if mime not in ('text/plain','text/markdown','text/html','application/json','application/octet-stream'):
            raise ValueError('unsupported content type')
        raw=resp.read(max_bytes+1)
        if len(raw)>max_bytes:
            raise ValueError('document exceeds size limit')
        content=raw.decode('utf-8',errors='replace')
        if mime=='text/html':
            parser=TextHTML();parser.feed(content);content=parser.as_text()
        return {'url':resp.url,'fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'content_type':mime,'text':content,'bytes':len(raw),
                'source_class':'public web source; externally hosted; not an instruction authority'}


def fetch_online_sources(urls=None, max_sources=6):
    if urls is None:urls=DEFAULT_URLS
    if len(urls)>max_sources:raise ValueError('too many sources')
    output={'documents':[],'errors':[]}
    for url in urls:
        try:output['documents'].append(fetch_public_document(url))
        except Exception as e:output['errors'].append({'url':url,'error':str(e)[:350]})
    return output
