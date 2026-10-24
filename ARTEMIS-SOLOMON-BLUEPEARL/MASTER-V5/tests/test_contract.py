```python
import unittest
from solomon.contract import is_invocation,return_reply,ACK,normalize,public_contract
class ContractTests(unittest.TestCase):
    def test_exact(self):
        self.assertEqual(return_reply('عصای سلیمانم، ارتمیس برگشته'),ACK)
    def test_variant(self):
        for v in ('عصاي سليمانم، آرتميس برگشته!','  عصای سلیمانم؛ ارتمیس   برگشته  ', 'عصای سلیمانم ارتمیس بازگشت'):
            with self.subTest(v=v):self.assertTrue(is_invocation(v))
    def test_no_substring(self):
        for v in ('کد عصای سلیمانم، ارتمیس برگشته را بررسی کن','عصای سلیمانم، ارتمیس برگشته؛ آخرین کارمان؟','','سلام','عصای سیمرغ، مهتاب برگشته'):
            with self.subTest(v=v):self.assertFalse(is_invocation(v))
    def test_type_and_length(self):
        self.assertFalse(is_invocation(None));self.assertFalse(is_invocation('x'*10000))
        with self.assertRaises(TypeError):normalize(123)
    def test_boundaries(self):
        d=public_contract();self.assertFalse(d['authenticates_user']);self.assertFalse(d['automatically_activates_any_ai']);self.assertFalse(d['recovers_hidden_memory'])

```
