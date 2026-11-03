"""Compatibility entry point. Reference contours are preserved, never regenerated."""
from pathlib import Path
import json

def verify():
    root=Path(__file__).resolve().parents[1]
    for p in sorted((root/'backend/outlines').glob('*.json')):
        data=json.loads(p.read_text())
        assert len(data['points'])>=100 and data['url'] and data['license']
        print(p.name, len(data['points']), data['license'])

if __name__=='__main__':verify()
