"""Modal-band selection, independent synthesis range, reciprocity/passivity and three support cases.

Static recovery target: 1e-7 relative for supported models; 1% for the
numerically constrained elastic pseudoinverse of a free body. Neither is a
mesh-convergence criterion. Outputs retain the observed error explicitly.
"""
import sys,json,time,copy,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from backend.catalog import default_project,validate
from backend.geometry import mesh
from backend.fem import wood_system,boundary,port_matrix,air_system
from backend.response import prepare,coefficients,public_response
from backend.audio import synthesize
parser=argparse.ArgumentParser();parser.add_argument('--output',default='data/bands-verification');args=parser.parse_args();root=Path(args.output);root.mkdir(parents=True,exist_ok=True);reports=[]
for name,support,fmin,fmax,cap in [('band','neck',300,500,20),('free','free',5,2000,12),('rim','rim',5,2000,12)]:
 p=default_project('om');p['solver'].update(size=55,modes=cap,airModes=4,support=support,fmin=fmin,fmax=fmax);p['excitation']['duration']=.5;start=time.time();raw=mesh(p,root/name);w=wood_system(raw);f=w['omega']/(2*np.pi);assert np.min(f)>=max(5,fmin)*(1-1e-7) and np.max(f)<=fmax*(1+1e-7)
 ext,itf,ap=boundary(raw);B,ports=port_matrix(raw,w,ext);air=air_system(raw,w,itf,ap);m=prepare(raw,w,air,B,ports,ext);freq=np.r_[0,np.geomspace(.1,15000,150)];Y,H=coefficients(m,p,freq)
 assert np.isfinite(Y).all() and np.isfinite(H).all() and np.max(abs(Y[0]))==0
 symmetry=np.linalg.norm(Y-Y.transpose(0,2,1))/np.linalg.norm(Y);assert symmetry<1e-8
 passivity=min(np.linalg.eigvalsh((v+v.conj().T)/2).min() for v in Y);assert passivity>-1e-8
 print(name,'projection rank',m['residual']['rank'],'static error',m['residual']['staticError'],flush=True);assert m['residual']['staticError']<(1e-2 if support=='free' else 1e-7)
 key=__import__('backend.response',fromlist=['geometry_key']).geometry_key(p);q=copy.deepcopy(p);q['synthesis'].update(fmin=1500,fmax=5000);assert __import__('backend.response',fromlist=['geometry_key']).geometry_key(q)==key
 a=synthesize(m,q,[dict(string=5,time=0)]);assert np.isfinite(a['pressure']).all();assert a['synthesisBand']==[1500,5000]
 reports.append(dict(case=name,modeMin=float(f.min()),modeMax=float(f.max()),modes=len(f),complete=w['modalBand']['complete'],staticError=m['residual']['staticError'],minimumPassivity=float(passivity),reciprocity=float(symmetry),seconds=time.time()-start));(root/'report.json').write_text(json.dumps(reports,indent=2));print(reports[-1],flush=True)
