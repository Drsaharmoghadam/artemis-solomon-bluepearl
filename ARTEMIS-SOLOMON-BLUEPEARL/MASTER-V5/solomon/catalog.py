```python
"""Load and validate the signed-by-hash (not cryptographically signed) public bundle catalog."""
from __future__ import annotations
from pathlib import Path
import json, hashlib
from .contract import ROOT

MANIFEST = ROOT/'manifest.json'


def safe_path(relative: str) -> Path:
    if not isinstance(relative, str) or not relative or relative.startswith(('/', '\\')):
        raise ValueError('unsafe path')
    base=ROOT.resolve(); candidate=(ROOT/relative).resolve()
    if not candidate.is_relative_to(base) or not candidate.is_file():
        raise ValueError('path absent or outside bundle')
    return candidate


def load_manifest() -> dict:
    data=json.loads(MANIFEST.read_text(encoding='utf-8'))
    if data.get('project_id')!='ARTEMIS-SOLOMON-BLUEPEARL':
        raise ValueError('wrong project_id')
    if data.get('schema')!='simorgh-master-manifest/5.0.0':
        raise ValueError('unsupported manifest schema')
    return data


def verify_sources(manifest=None) -> list:
    manifest=manifest or load_manifest()
    failures=[]
    seen=set()
    for entry in manifest['sources']:
        name=entry['path']
        if name in seen:
            failures.append(f'duplicate: {name}')
            continue
        seen.add(name)
        try:
            path=safe_path(name)
            raw=path.read_bytes()
            digest=hashlib.sha256(raw).hexdigest()
            if digest!=entry['sha256']:
                failures.append(f'sha256 mismatch: {name}')
            if len(raw)!=entry['bytes']:
                failures.append(f'byte length mismatch: {name}')
        except Exception as err:
            failures.append(f'{name}: {err}')
    return failures


def selected_sources(manifest, scope='core'):
    if scope not in ('core','extended','full'):
        raise ValueError('scope must be core, extended or full')
    rank={'core':0,'extended':1,'full':2}
    return [e for e in manifest['sources'] if rank[e['tier']] <= rank[scope]]

```
