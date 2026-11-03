"""Local request isolation and queued-job deduplication; no FE solve."""
import sys,json,threading,urllib.request,urllib.error,http.server
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server as app
from backend.catalog import default_project
class Queue:
 def __init__(self):self.calls=[]
 def submit(self,*args):self.calls.append(args)
app.POOL=Queue();server=http.server.ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
threading.Thread(target=server.serve_forever,daemon=True).start();root=f'http://127.0.0.1:{server.server_port}'
def request(path,data=None,headers=None):
 req=urllib.request.Request(root+path,data=json.dumps(data).encode() if data is not None else None,headers=headers or {'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=10) as response:return response.status,json.load(response)
 except urllib.error.HTTPError as e:return e.code,json.load(e)
try:
 status,health=request('/api/health');assert status==200 and health['version']=='1.3';p=default_project();data=dict(project=p)
 for headers in [{'Content-Type':'text/plain'},{'Content-Type':'application/json','Origin':'https://example.org'},{'Content-Type':'application/json','Host':'example.org'}]:assert request('/api/solve',data,headers)[0]==400
 assert not app.POOL.calls
 status,preview=request('/api/preview',data,{'Content-Type':'application/json','Origin':root});assert status==200 and preview['project']['schema']=='gmt'
 p['analysis']['fft']=12345;assert request('/api/solve',data)[0]==400;p['analysis']['fft']=4096
 status,a=request('/api/solve',data);status,b=request('/api/solve',data);assert status==200 and a['id']==b['id'] and len(app.POOL.calls)==1
 for height in [3,3.1]:p['body']['top']=height;assert request('/api/solve',data)[0]==200
 p['body']['top']=3.2;assert request('/api/solve',data)[0]==400 and len(app.POOL.calls)==3
 assert request('/api/job/unknown')[0]==400
 print('PASS: local origin/host/content type, invalid FFT, duplicate queued solves, bounded queue, unknown jobs and release health.')
finally:server.shutdown();server.server_close()
