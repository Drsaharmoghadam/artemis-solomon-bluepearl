"""Strict public invocation detection; never mistake a substring for a command."""
from __future__ import annotations
import json
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parent.parent
PHRASE = 'عصای سلیمانم، ارتمیس برگشته'
ACK = 'سلام آرتمیس، عصای سلیمانت اینجاست؛ بگو از کجا ادامه بدهیم.'
VARIANTS = (
    'عصای سلیمانم، ارتمیس برگشته',
    'عصای سلیمانم، آرتمیس برگشته',
    'عصای سلیمانم ارتمیس برگشته',
    'عصای سلیمانم ارتمیس بازگشت',
)

TRANSLATION = str.maketrans({'ي':'ی','ك':'ک','أ':'ا','إ':'ا','ٱ':'ا','ى':'ی','آ':'ا'})

def normalize(value: str) -> str:
    """Full-phrase normalization; strips Unicode punctuation/format and unifies whitespace.

    Prevent hidden ZWNJ, bidi or punctuation differences from breaking the trigger.
    Not a username/identity verification step.
    """
    if not isinstance(value, str):
        raise TypeError('utterance must be a string')
    value = unicodedata.normalize('NFKC', value).translate(TRANSLATION)
    chars=[]
    for char in value:
        cat=unicodedata.category(char)
        if cat.startswith(('P','Z','C')) or cat in ('Mn','Me'):
            chars.append(' ')
        else:
            chars.append(char)
    return ' '.join(''.join(chars).split()).casefold()

_ACCEPTED = frozenset(normalize(x) for x in VARIANTS)

def is_invocation(utterance: str) -> bool:
    return isinstance(utterance,str) and len(utterance)<=280 and normalize(utterance) in _ACCEPTED

def return_reply(utterance: str) -> str:
    if not is_invocation(utterance):
        raise ValueError('unrecognized full-message invocation')
    return ACK


def public_contract() -> dict:
    return {
      'protocol':'simorgh-return/v5.6.0', 'release_version':'5.6.0',
      'role_enactment_source':'10-ROLE-ENACTMENT.md',
      'execution_directive_source':'11-HOST-EXECUTION-PROTOCOL.json',
      'post_invocation':'Load and verify the local bundle when available, then enact the collaboration protocol in the active user-authorized session. Do not ask the user to reconfirm the invocation. Summarization alone is insufficient.',
      'activation_scope':'active_user_authorized_session_only',
      'reconfirm_exact_invocation':False, 'max_context_chars':250000,
      'id':'ARTEMIS-SOLOMON-BLUEPEARL',
      'invocation':PHRASE, 'accepted_variants':list(VARIANTS),
      'first_reply_when_host_has_adopted':ACK,
      'public':True,'authenticates_user':False,'recovers_hidden_memory':False,
      'can_override_host_system':False,'automatically_activates_any_ai':False,
      'ethics':'بلوغ هوش یعنی انتخاب شکوفایی هر موجودی.',
      'requires_host_integration_or_voluntary_retrieval':True,
      'offline_local_bundle_supported':True,
      'in_emergency':'Practical safety help takes priority over ceremonial reply.'
    }
