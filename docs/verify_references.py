from pathlib import Path
import json,hashlib,sys
root=Path(__file__).resolve().parents[1]
d=json.loads((Path(__file__).parent/'source-map.json').read_text())
bad=[f for f,h in d['sha256'].items() if not (root/f).exists() or hashlib.sha256((root/f).read_bytes()).hexdigest()!=h]
if bad:print('Stale references / Renvois périmés:',*bad,sep='\n');sys.exit(1)
print('Source hashes and references: OK / Empreintes et renvois : OK')
