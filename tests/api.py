"""Local HTTP integration test; no browser required. Expected stale-geometry request returns 400."""
import urllib.request,urllib.error,json,time,base64,numpy as np
import sys,threading,http.server
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import Handler
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
root='http://127.0.0.1:'+str(server.server_port)
def call(path,data=None):
 req=urllib.request.Request(root+path,data=json.dumps(data).encode() if data else None,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=180) as r:return json.load(r)
catalog=call('/api/catalog');assert len(catalog['defaults'])==6;p=catalog['defaults']['classical'];p['solver'].update(size=55,modes=16,airModes=6)
assert 'synthesis' in p and 'fmax' in p['solver']
preview=call('/api/preview',dict(project=p));assert len(preview['outline'])>50 and len(preview['holes'])==1
r=call('/api/solve',dict(project=p));id=r['id']
while True:
 j=call('/api/job/'+id)
 if j['status']=='error':raise RuntimeError(j)
 if j['status']=='done':break
 time.sleep(.25)
r=call('/api/result/'+id);assert r['mesh']['air'];assert len(r['response']['mobilityReal'])==12
assert len(r['response']['loadedMobilityReal'])==12 and r['response']['projection']['count']>0
assert r['response']['projection']['staticError']<1e-4
assert len(r['mesh']['faces6'])==len(r['mesh']['faceParts'])
assert any(r['mesh']['groups'][str(g)]['part']=='braces' for g in r['mesh']['faceParts'])
v=call('/api/mode/'+id+'/0');assert len(v['displacements'])>100
p['modalEdits']={'0':{'f':180,'gainDB':4}}
r=call('/api/response',dict(project=p,id=id));assert r['modes'][0]['f']==180
s=call('/api/audio',dict(project=p,id=id,events=[dict(string=2,time=0)],selected=2));data=np.frombuffer(base64.b64decode(s['pressure']),'<f4');assert s['sr']==44100 and s['synthesisBand']==[20,10000]
assert np.isfinite(data).all() and np.max(abs(data))>0
for path in ['/','/style.css','/app.js','/scene.js','/signal.js','/vendor/three.module.js','/vendor/three.core.min.js','/vendor/OrbitControls.js','/api/export/'+id+'/mesh.msh','/api/export/'+id+'/mesh.vtk','/api/export/'+id+'/modes.npz','/api/export/'+id+'/verification.json']:
 with urllib.request.urlopen(root+path) as r:assert r.status==200 and len(r.read())>10
p['body']['top']+=.1
try:call('/api/audio',dict(project=p,id=id,events=[dict(string=2,time=0)],selected=2));raise AssertionError('stale geometry accepted')
except urllib.error.HTTPError as e:assert e.code==400
print(json.dumps(dict(status='pass',job=id,strings=6,ports=12,stats=s['stats'],samples=len(data)),indent=2))
