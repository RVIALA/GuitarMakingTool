"""Four cutaway cases: conformal mesh, coupled response and string outputs."""
import sys,json,time,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from backend.catalog import default_project
from backend.geometry import mesh
from backend.fem import wood_system,boundary,port_matrix,air_system
from backend.response import prepare,public_response,visual_mesh
from backend.audio import synthesize
parser=argparse.ArgumentParser();parser.add_argument('--output',default='data/cutaway-physics');args=parser.parse_args();root=Path(args.output);root.mkdir(parents=True,exist_ok=True);reports=[]
for key,cut in [('om','venetian'),('classical','florentine'),('selmer_oval','selmer'),('archtop','florentine')]:
 p=default_project(key);p['body'].update(cutaway=cut,cutawayDepth={'selmer':60,'venetian':90,'florentine':78}[cut]);p['solver'].update(size=55,modes=12,airModes=6);p['excitation']['duration']=.5;start=time.time();raw=mesh(p,root/(key+'_'+cut));w=wood_system(raw);ext,i,a=boundary(raw);B,ports=port_matrix(raw,w,ext);air=air_system(raw,w,i,a);m=prepare(raw,w,air,B,ports,ext);r=public_response(m,p);view=visual_mesh(m);audio=synthesize(m,p,[dict(string=0,time=0),dict(string=5,time=.1)])
 assert w['quality']['modalResidualMax']<1e-5
 assert r['stats']['minimumPassivity']>-1e-8
 assert len(ports)==6 and np.min(np.diff(ports[:,0]))>.005
 for name in ['force','velocity','pressure']:assert np.isfinite(audio[name]).all() and np.max(abs(audio[name]))>0
 reports.append(dict(preset=key,cutaway=cut,stats=r['stats'],quality=w['quality'],seconds=time.time()-start,signalPeaks={name:float(np.max(abs(audio[name]))) for name in ['force','velocity','pressure']}));(root/'report.json').write_text(json.dumps(reports,indent=2));print(key,cut,reports[-1]['seconds'],'PASS',flush=True)
