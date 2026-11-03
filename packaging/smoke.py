"""Exercise the frozen server AND a real FEM job; run after packaging/build.py."""
from pathlib import Path
import subprocess,sys,os,socket,tempfile,time,json,urllib.request
NAME='GMT'
root=Path(__file__).resolve().parents[1]
exe=root/'dist'/NAME/(NAME+('.exe' if os.name=='nt' else ''))
subprocess.run([str(exe),'--self-test'],check=True,timeout=40)
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
with tempfile.TemporaryDirectory(prefix=NAME+'_smoke_') as tmp:
 env=os.environ.copy();env['GMT_DATA_DIR' if NAME=='GMT' else 'TONEWOODTOOL_DATA_DIR']=tmp
 log=open(Path(tmp)/'server.log','w');proc=subprocess.Popen([str(exe),'--port',str(port),'--no-browser'],env=env,stdout=log,stderr=log)
 base='http://127.0.0.1:'+str(port)
 def req(path,data=None):
  body=None if data is None else json.dumps(data).encode()
  try:
   with urllib.request.urlopen(urllib.request.Request(base+path,data=body,headers={'Content-Type':'application/json'}),timeout=30) as r:return json.load(r)
  except urllib.error.HTTPError as e:raise RuntimeError(e.read().decode()) from e
 try:
  for _ in range(100):
   try:p=req('/api/catalog' if NAME=='GMT' else '/api/default');break
   except Exception:
    if proc.poll() is not None:raise RuntimeError((Path(tmp)/'server.log').read_text())
    time.sleep(.2)
  else:raise RuntimeError('Server did not start')
  with urllib.request.urlopen(base) as r:assert NAME in r.read().decode()
  if NAME=='GMT':
   p=p['defaults']['om'];p['braces']=[];p['body'].update(backEnabled=False,ribsEnabled=False);p['solver'].update(size=40,modes=16,air=False,fmax=800);p['body']['rimTolerance']=.3
   j=req('/api/solve',{'project':p})['id']
  else:
   assert p['mass_g']==0 and p['geometry']['L']==0 and not p['observations']
   p['mass_g']=10.8;p['geometry'].update(L=200,w=12,H=10);p['solver'].update(size_mm=30,fmax=1000,modes=8)
   assert req('/api/preview',p)['cad']['rho']>0
   j=req('/api/run',{'project':p,'action':'solve'})['id']
  for _ in range(900):
   status=req('/api/job/'+j);state=status.get('state',status.get('status'))
   if state in ['error','failed','cancelled','interrupted']:raise RuntimeError(str(status))
   if state in ['done','completed']:break
   time.sleep(.2)
  else:raise RuntimeError('FEM job timed out')
  if NAME=='ToneWoodTool':
   result=req('/api/job/'+j+'/summary');assert result['frequencies'] and all(x>0 for x in result['frequencies'])
  else:assert req('/api/result/'+j)
  print(NAME+': frozen runtime, HTTP, assets and FEM PASS',flush=True)
 finally:
  proc.terminate()
  try:proc.wait(5)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
  log.close()
