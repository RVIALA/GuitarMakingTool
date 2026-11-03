import sys,copy,threading,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from shapely.geometry import Polygon
from backend.catalog import default_project,PRESETS,validate
from backend.geometry import brace_preview,brace_footprint,holes
from backend.contours import outline
from backend.strings import string_properties,decay_rate,string_impedance
from backend.audio import templates,synthesize
from backend.uncertainty import ensemble
p=default_project();p['excitation']['duration']=.5;p['synthesis']['extension']='none';p['synthesis']['fmax']=6000
rng=np.random.default_rng(719);wm=2*np.pi*np.array([145,230,380,640.]);m=dict(omega=wm,wood=dict(omega=wm,loss=np.full(4,.025)),projection=rng.normal(size=(4,12))*.2,air=None,centers=np.array([[0,.25,0]]),radiation=np.array([[.03,.015,.01,.005]]),residual=dict(rank=0),cache={},lock=threading.RLock())
free=templates(m,p,list(range(6)),0,44100).copy();p['excitation']['palm']=.8;muted=templates(m,p,list(range(6)),0,44100)
assert np.linalg.norm(muted[12000:,0,0])<np.linalg.norm(free[12000:,0,0])*.3
assert not np.allclose(free,muted);p['strings']['items'][0]['muted']=True
assert not np.any(synthesize(m,p,[dict(string=0)])['force'])
st=string_properties(p,0);f=np.array([100.,1000.]);assert np.all(decay_rate(st,f)>10)
p['excitation']['palm']=0;p['strings']['damping']=2;assert string_properties(p,0)['loss']==p['strings']['items'][0]['loss']*2
for v in [-1,11]:
 bad=copy.deepcopy(p);bad['strings']['damping']=v
 try:validate(bad);raise AssertionError('Invalid damping accepted')
 except ValueError:pass
checked=0
for preset in PRESETS:
 q=default_project(preset)
 for cut in ['none','selmer','venetian','florentine']:
  q['body']['cutaway']=cut;q['braces'][0]['a']=[-600,40];q['braces'][0]['b']=[600,40];poly=outline(q,preview=True);inner=poly.buffer(-q['body']['ribs']*.001)
  for b in brace_preview(q,poly):
   shape=Polygon(b['outline'],b['holes']);assert shape.difference(inner).area<1e-12
   if b['side']=='top':
    for hole in holes(q):assert shape.intersection(hole).area<1e-12
   checked+=1
zero=ensemble(m,p,dict(samples=8,frequencyCV=0,dampingCV=0,participationCV=0,fmax=800))
for k in ['p10','p50','p90']:assert np.allclose(zero[k],zero['nominal'],rtol=1e-12,atol=1e-15)
a=ensemble(m,p,dict(samples=8,seed=32,fmax=800));b=ensemble(m,p,dict(samples=8,seed=32,fmax=800));assert a==b
assert np.all(np.array(a['p10'])<=a['p50']) and np.all(np.array(a['p50'])<=a['p90']);assert max(np.array(a['p90'])-a['p10'])>0
report=dict(status='PASS',clipped_preview_parts=checked,palm_tail_ratio=float(np.linalg.norm(muted[12000:,0,0])/np.linalg.norm(free[12000:,0,0])),muted_note_silent=True,zero_uncertainty_matches_nominal=True,monte_carlo_reproducible=True)
print(json.dumps(report,indent=2));Path(__file__).with_name('features_1_5.json').write_text(json.dumps(report,indent=2))
# Exercise new routes through the real HTTP handler (same controlled modal model).
import http.server,urllib.request
import server
from backend.response import geometry_key
m['key']=geometry_key(p);server.JOBS['features']={'status':'done','model':m}
http=http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);threading.Thread(target=http.serve_forever,daemon=True).start()
try:
 def post(path,data):
  req=urllib.request.Request(f'http://127.0.0.1:{http.server_port}'+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
 r=post('/api/preview',dict(project=p));assert r['braceShapes'];assert all('holes' in x for x in r['braceShapes'])
 r=post('/api/uncertainty',dict(id='features',project=p,settings=dict(samples=8,frequencyCV=0,dampingCV=0,participationCV=0,fmax=800)))
 assert np.allclose(r['nominal'],r['p50'])
 print('PASS: real /api/preview clipped braces and /api/uncertainty routes')
finally:http.shutdown();http.server_close()
