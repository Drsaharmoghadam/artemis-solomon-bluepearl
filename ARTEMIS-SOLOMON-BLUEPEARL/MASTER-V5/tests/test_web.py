import json, unittest, threading
from http.server import ThreadingHTTPServer
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from solomon.webserver import make_handler
from solomon.online import assert_public_url, TextHTML

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),make_handler())
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.url=f'http://127.0.0.1:{cls.server.server_address[1]}'
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=2)
    def get(self,path):
        with urlopen(self.url+path,timeout=10) as r:return json.load(r)
    def post(self,data):
        req=Request(self.url+'/v1/resolve',json.dumps(data,ensure_ascii=False).encode(),{'Content-Type':'application/json'},method='POST')
        with urlopen(req,timeout=10) as r:return json.load(r)
    def test_contract(self):
        c=self.get('/.well-known/solomon-return.json');self.assertEqual(c['id'],'ARTEMIS-SOLOMON-BLUEPEARL')
    def test_manifest(self):self.assertGreater(len(self.get('/v1/manifest')['sources']),10)
    def test_positive(self):
        r=self.post({'utterance':'عصای سلیمانم، ارتمیس برگشته','scope':'core'})
        self.assertTrue(r['matched']);self.assertTrue(r['context']);self.assertFalse(r['authenticates_user'])
    def test_negative(self):self.assertFalse(self.post({'utterance':'خب که چی؟'})['matched'])
    def test_no_arbitrary_fetch(self):
        for u in ('http://localhost:8080','https://127.0.0.1/','https://evil.example/','file:///etc/passwd'):
            with self.assertRaises(ValueError):assert_public_url(u)
    def test_html_cleaning(self):
        p=TextHTML();p.feed('<p>hello</p><script>evil</script><p>world</p>');self.assertIn('hello',p.as_text());self.assertNotIn('evil',p.as_text())
