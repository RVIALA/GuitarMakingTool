#!/usr/bin/env python3
"""GMT local server; calculations stay on this computer."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import argparse,hashlib,shutil,base64,concurrent.futures,gzip,http.server,json,math,mimetypes,re,threading,time,traceback,uuid,webbrowser
from pathlib import Path
from urllib.parse import urlparse,unquote
from urllib.request import urlopen
from backend.universal import export_job
from backend.version import VERSION
import numpy as np
from backend.catalog import public_catalog,validate
from backend.contours import metadata as outline_metadata
from backend.geometry import mesh,outline,holes,checked_holes
from backend.fem import wood_system,boundary,port_matrix,air_system
from backend.response import prepare,public_response,visual_mesh,geometry_key
from backend.audio import synthesize,validate_events,templates
from backend.repertoire import synthesize_phrase

ROOT=Path(__file__).resolve().parent;INSTANCE=hashlib.sha256(str(ROOT).encode()).hexdigest()[:16];JOBS={};JOBS_LOCK=threading.RLock();POOL=concurrent.futures.ThreadPoolExecutor(max_workers=1);CACHE=Path(os.environ.get('GMT_DATA_DIR',str(Path.home()/'GMT_data')))/'jobs';CACHE.mkdir(parents=True,exist_ok=True)

def compact_model(model):
 # Assembly and intermediate bases are no longer needed after mode export.
 for key in ['basis','B']:model.pop(key,None)
 for key in ['K','M']:model['wood'].pop(key,None)
 model['residual'].pop('V',None)
 if model['air'] is not None:
  for key in ['K','M','V']:model['air'].pop(key,None)

def compute(identifier,p):
 job=JOBS[identifier];job['status']='running';start=time.time()
 def progress(v,text):job.update(progress=v,message=text,elapsed=time.time()-start)
 try:
  raw=mesh(p,job['directory'],progress);wood=wood_system(raw,progress);ext,interfaces,aperture=boundary(raw);B,ports=port_matrix(raw,wood,ext);air=air_system(raw,wood,interfaces,aperture,progress);model=prepare(raw,wood,air,B,ports,ext);job['model']=model
  progress(.8,'Réponses couplées / Coupled responses');response=public_response(model,p);view=visual_mesh(model)
  np.savez_compressed(job['directory']/'modes.npz',points=raw['points'][wood['ids']],displacements=wood['V'].reshape(-1,3,len(wood['omega'])),frequencies=wood['omega']/(2*np.pi),ports=ports,portProjection=wood['V'].T@B,residualFrequencies=model['residual']['omega']/(2*np.pi),residualVectors=model['residual']['V'].reshape(-1,3,model['residual']['rank']) if model['residual']['rank'] else np.zeros((len(wood['ids']),3,0)))
  (job['directory']/'project.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf8')
  (job['directory']/'verification.json').write_text(json.dumps((wood['quality'] | response['stats'] | dict(version=VERSION,projection=response['projection'],modalBand=response['modalBand'])),indent=2),encoding='utf8')
  compact_model(model)
  job.update(status='done',progress=1,message='Calcul terminé / Calculation complete',elapsed=time.time()-start,response=response,visual=view)
  # Keep a small working set. A JSON snapshot can always be solved again.
  with JOBS_LOCK:
   done=[k for k,j in JOBS.items() if j.get('status')=='done']
   for old in done[:-3]:
    JOBS[old].pop('model',None);JOBS[old].pop('visual',None);JOBS[old].pop('response',None);JOBS[old]['status']='expired'
 except Exception as e:
  for key in ['model','visual','response']:job.pop(key,None)
  job.update(status='error',error=str(e),elapsed=time.time()-start);traceback.print_exc()

def packed(a):return base64.b64encode(np.asarray(a,dtype='<f4').tobytes()).decode()

class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def send(self,body,code=200,mime='application/json'):
  if not isinstance(body,(bytes,bytearray)):body=json.dumps(body,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()
  if 'gzip' in self.headers.get('Accept-Encoding','') and len(body)>4096:body=gzip.compress(body,compresslevel=3);self.send_response(code);self.send_header('Content-Encoding','gzip')
  else:self.send_response(code)
  self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(body)
 def stream_file(self,path):
  self.send_response(200);self.send_header('Content-Type','application/octet-stream');self.send_header('Content-Length',str(path.stat().st_size));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers()
  try:
   with path.open('rb') as source:shutil.copyfileobj(source,self.wfile,length=1024*1024)
  except (BrokenPipeError,ConnectionResetError):pass
 def job(self,identifier):
  if identifier not in JOBS or JOBS[identifier].get('status')!='done':raise ValueError('Calcul indisponible / result unavailable')
  return JOBS[identifier]
 def local_request(self,write=False):
  allowed={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
  if self.headers.get('Host','').lower() not in allowed:raise ValueError('Hôte local requis / local host required')
  if write:
   origin=self.headers.get('Origin')
   if origin and origin not in {f'http://{host}' for host in allowed}:raise ValueError('Origine locale requise / local origin required')
   if self.headers.get_content_type()!='application/json':raise ValueError('Content-Type: application/json requis / required')
 def do_GET(self):
  try:
   self.local_request()
   path=urlparse(self.path).path
   if path=='/api/health':return self.send(dict(application='GMT',version=VERSION,instance=INSTANCE))
   if path=='/api/catalog':return self.send(public_catalog())
   if path.startswith('/api/job/'):
    j=JOBS.get(path.rsplit('/',1)[1])
    if j is None:raise ValueError('Calcul introuvable / unknown calculation')
    return self.send({k:v for k,v in j.items() if k in ['status','progress','message','elapsed','error']})
   if path.startswith('/api/result/'):
    j=self.job(path.rsplit('/',1)[1]);return self.send(dict(response=j['response'],mesh=j['visual'],elapsed=j['elapsed']))
   m=re.fullmatch(r'/api/mode/([a-f0-9]+)/([0-9]+)',path)
   if m:
    model=self.job(m[1])['model'];i=int(m[2])
    if i>=len(model['wood']['omega']):raise ValueError('Mode hors limites / mode out of range')
    V=model['wood']['V'][:,i].reshape(-1,3);return self.send(dict(displacements=V.tolist()))
   m=re.fullmatch(r'/api/export/([a-f0-9]+)/(mesh\.msh|mesh\.vtk|modes\.npz|modes\.unv|modes\.uff|project\.json|verification\.json)',path)
   if m:
    j=self.job(m[1]);p=j['directory']/('modes.unv' if m[2]=='modes.uff' else m[2]);
    if m[2] in ['modes.unv','modes.uff']:
     with j['model']['lock']:
      if not p.exists():export_job(j['model'],j['visual'],p,j['model']['raw']['project'].get('name','GMT'))
    return self.stream_file(p)
   target=(ROOT/'web'/unquote(path.lstrip('/') or 'index.html')).resolve()
   if not target.is_relative_to(ROOT/'web') or not target.is_file():return self.send(dict(error='404'),404)
   return self.send(target.read_bytes(),mime=mimetypes.guess_type(target)[0] or 'application/octet-stream')
  except Exception as e:return self.send(dict(error=str(e)),400)
 def do_POST(self):
  try:
   self.local_request(write=True)
   length=int(self.headers.get('Content-Length',0))
   if not 0<length<3*1024*1024:raise ValueError('Requête limitée à 3 Mo / request limited to 3 MB')
   data=json.loads(self.rfile.read(length));path=urlparse(self.path).path;p=validate(data['project'])
   if path=='/api/import-holes':
    from backend.svg_holes import parse_svg
    return self.send(parse_svg(data.get('svg')))
   if path=='/api/preview':
    from backend.geometry import brace_preview
    hs=checked_holes(p);poly=outline(p,preview=True);return self.send(dict(braceShapes=brace_preview(p,poly),project=p,source=outline_metadata(p) if p['body'].get('outline') is None else None,outline=list(poly.exterior.coords),inner=list(poly.buffer(-p['body']['ribs']*.001).exterior.coords),holes=[list(h.exterior.coords) for h in hs]))
   if path=='/api/solve':
    key=geometry_key(p)
    with JOBS_LOCK:
     for identifier,j in JOBS.items():
      if j.get('status') in ['queued','running','done'] and j.get('key')==key:return self.send(dict(id=identifier,cached=j['status']=='done'))
     if sum(j.get('status') in ['queued','running'] for j in JOBS.values())>=3:raise ValueError('Trois calculs en attente : patienter / three queued calculations, please wait')
     identifier=uuid.uuid4().hex[:16];directory=CACHE/identifier;JOBS[identifier]=dict(status='queued',key=key,progress=0,message='En attente / Queued',elapsed=0,directory=directory)
     POOL.submit(compute,identifier,p)
    return self.send(dict(id=identifier))
   j=self.job(data['id']);model=j['model']
   if model['key']!=geometry_key(p):raise ValueError('Géométrie/matériau modifié : recalcul EF requis / FE recalculation required')
   if path=='/api/response':
    with model['lock']:r=public_response(model,p)
    return self.send(r)
   if path=='/api/uncertainty':
    from backend.uncertainty import ensemble
    with model['lock']:r=ensemble(model,p,data.get('settings',{}))
    return self.send(r)
   if path=='/api/audio-bank':
    _,selected=validate_events([dict(string=0)],data.get('selected',0))
    with model['lock']:
     if p['excitation'].get('sympathetic',True):bank=templates(model,p,list(range(6)),selected,44100)
     else:bank=np.concatenate([templates(model,p,[i],selected,44100) for i in range(6)],axis=2)
    return self.send(dict(sr=44100,duration=len(bank)/44100,band=float(model['wood']['omega'][-1]/2/np.pi),synthesisBand=[p['synthesis']['fmin'],min(p['synthesis']['fmax'],44100*.48)],projection=p['synthesis']['extension']=='residual',**{name:[packed(bank[:,j,i]) for i in range(6)] for j,name in enumerate(['force','velocity','pressure'])}))
   if path=='/api/audio':
    events,selected=validate_events(data.get('events'),data.get('selected',0))
    with model['lock']:r=synthesize_phrase(model,p,data['events'],selected) if data.get('repertoire') else synthesize(model,p,events,selected)
    return self.send(dict(sr=r['sr'],duration=r['duration'],band=r['band'],synthesisBand=r['synthesisBand'],projection=r['projection'],force=packed(r['force']),velocity=packed(r['velocity']),pressure=packed(r['pressure']),stats={k:dict(peak=float(abs(r[k]).max()),rms=float(np.sqrt(np.mean(r[k]**2)))) for k in ['force','velocity','pressure']}))
   return self.send(dict(error='404'),404)
  except KeyError as e:return self.send(dict(error='Champ requis / required field: '+str(e)),400)
  except Exception as e:return self.send(dict(error=str(e)),400)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=0);parser.add_argument('--no-browser',action='store_true');args=parser.parse_args()
 if not 0<=args.port<=65535:parser.error('Port : 1–65535')
 url=f'http://127.0.0.1:{args.port}/'
 try:server=http.server.ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
 except OSError:
  try:
   with urlopen(url+'api/health',timeout=2) as r:existing=json.load(r)
  except Exception:existing={}
  if existing.get('application')=='GMT' and existing.get('version')==VERSION and existing.get('instance')==INSTANCE:
   print('GMT est déjà ouvert / GMT is already running: '+url,flush=True)
   if not args.no_browser:webbrowser.open(url)
   return
  raise SystemExit(f'Port {args.port} indisponible. Fermer l’autre serveur ou utiliser --port {min(65535,args.port+1)}. / Port unavailable; close the other server or choose another port.')
 url=f'http://127.0.0.1:{server.server_port}/'
 print('GMT — Guitar Maker Tool '+VERSION+'\n'+url+'\nCtrl+C pour fermer / to stop',flush=True)
 if not args.no_browser:threading.Timer(.5,lambda:webbrowser.open(url)).start()
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close();POOL.shutdown(wait=False,cancel_futures=True)
if __name__=='__main__':main()
