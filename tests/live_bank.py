"""Prepared 6-string bank equals direct responses at one common observation port."""
import sys,json,time,threading,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from backend.catalog import default_project
from backend.audio import templates,synthesize
p=default_project();p['excitation']['duration']=.5;p['synthesis']['extension']='none';p['synthesis']['fmax']=6000
rng=np.random.default_rng(719);wm=2*np.pi*np.array([145,230,380,640.]);m=dict(omega=wm,wood=dict(omega=wm,loss=np.full(4,.025)),projection=rng.normal(size=(4,12))*.2,air=None,centers=np.array([[0,.25,0]]),radiation=np.array([[.03,.015,.01,.005]]),residual=dict(rank=0),cache={},lock=threading.RLock())
start=time.perf_counter();bank=templates(m,p,list(range(6)),2,44100);seconds=time.perf_counter()-start
max_error=0
for i in range(6):
 out=synthesize(m,p,[dict(string=i)],2)
 for j,k in enumerate(['force','velocity','pressure']):
  err=float(np.linalg.norm(bank[:,j,i]-out[k])/max(1e-30,np.linalg.norm(out[k])));max_error=max(max_error,err);assert err<1e-6
assert bank.shape==(22050,3,6)
expected=np.zeros((22050+4410,3),np.float32)
for i,strength in [(0,.5),(3,1.2)]:
 offset=0 if i==0 else 4410;expected[offset:offset+22050]+=strength*bank[:,:,i]
out=synthesize(m,p,[dict(string=0,strength=.5,time=0),dict(string=3,strength=1.2,time=.1)],2)
for j,k in enumerate(['force','velocity','pressure']):np.testing.assert_allclose(expected[:,j],out[k],rtol=2e-6,atol=1e-8)
print(json.dumps(dict(status='PASS',prepare_seconds=seconds,bank_bytes=bank.nbytes,max_relative_error=max_error,contact=2,linear_superposition=True),indent=2))
# Real HTTP serialization and stale-project rejection, with the same controlled model.
import urllib.request,urllib.error,http.server,base64
import server
from backend.response import geometry_key
m['key']=geometry_key(p);server.JOBS['banktest']={'status':'done','model':m}
http=http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);threading.Thread(target=http.serve_forever,daemon=True).start()
try:
 def post(project,selected):
  request=urllib.request.Request(f'http://127.0.0.1:{http.server_port}/api/audio-bank',data=json.dumps({'project':project,'id':'banktest','selected':selected}).encode(),headers={'Content-Type':'application/json'})
  return urllib.request.urlopen(request,timeout=30)
 with post(p,2) as response:raw=json.load(response)
 assert len(raw['force'])==6 and raw['sr']==44100
 np.testing.assert_array_equal(np.frombuffer(base64.b64decode(raw['force'][0]),dtype='<f4'),bank[:,0,0])
 invalid=copy.deepcopy(p);invalid['body']['width']+=1
 for proj,port in [(invalid,2),(p,6)]:
  try:post(proj,port);raise AssertionError('invalid request accepted')
  except urllib.error.HTTPError as e:assert e.code==400
 print('PASS: /api/audio-bank exact float32 transport, common contact, invalid contact and stale FE rejection.')
finally:http.shutdown();http.server_close()
