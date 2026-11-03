"""Reproducible numerical checks. Run from GMT: python tests/verify.py --full."""
import sys,json,time,argparse,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from backend.catalog import default_project,compliance,validate
from backend.geometry import mesh
from backend.fem import shape,GRAD,WEIGHTS,stiffness_material,frames,wood_system,boundary,port_matrix,air_system
from backend.response import prepare,coefficients,public_response,visual_mesh
from backend.audio import synthesize,string_impedance,string_properties

def element_checks():
 edges=[[0,1],[1,2],[2,0],[0,3],[2,3],[1,3]];N,dN=shape(edges)
 assert np.max(abs(N.sum(1)-1))<1e-12
 assert np.max(abs(dN.sum(1)))<1e-12
 assert abs(WEIGHTS.sum()-1/6)<1e-13
 xyz=np.r_[np.array([[0.,0,0],[1,0,0],[0,1,0],[0,0,1]]),np.array([(np.eye(4,3,k=-1)[i]+np.eye(4,3,k=-1)[j])/2 for i,j in edges])]
 xyz[:4]=np.array([[0.,0,0],[1,0,0],[0,1,0],[0,0,1]])
 for k,(i,j) in enumerate(edges):xyz[4+k]=(xyz[i]+xyz[j])/2
 # Gradient reproduction of coordinates for affine Tet10.
 J=np.einsum('qna,nb->qab',dN,xyz);gradient=np.einsum('qba,qna->qnb',np.linalg.inv(J),dN)
 assert np.max(abs(np.einsum('qna,nb->qab',gradient,xyz)-np.eye(3)))<1e-12
 B=np.zeros((11,6,30))
 for j in range(10):
  gx,gy,gz=gradient[:,j,:].T;B[:,0,3*j]=gx;B[:,1,3*j+1]=gy;B[:,2,3*j+2]=gz;B[:,3,3*j]=gy;B[:,3,3*j+1]=gx;B[:,4,3*j]=gz;B[:,4,3*j+2]=gx;B[:,5,3*j+1]=gz;B[:,5,3*j+2]=gy
 p=default_project();C=stiffness_material(p['materials']['top'],np.eye(3)[None])[0];K=np.einsum('qai,ab,qbj,q->ij',B,C,B,WEIGHTS)
 for axis in np.eye(3):
  u=np.tile(axis,(10,1)).ravel();assert np.max(abs(B@u))<1e-12
  u=np.cross(np.broadcast_to(axis,xyz.shape),xyz).ravel();assert np.max(abs(B@u))<1e-12
 E=np.array([[.01,.003,.002],[.003,-.004,.001],[.002,.001,.002]])
 strain=np.array([E[0,0],E[1,1],E[2,2],2*E[0,1],2*E[0,2],2*E[1,2]]);u=(xyz@E.T).ravel();assert np.max(abs(B@u-strain))<1e-12
 expected=strain@C@strain/6;assert abs(u@K@u/expected-1)<1e-12
 mass=np.einsum('qi,qj,q->ij',N,N,WEIGHTS);assert np.linalg.eigvalsh(mass).min()>0
 assert abs(mass.sum()-1/6)<1e-12
 # Wood rotation: a 90-degree swap changes the longitudinal stiffness.
 R=np.array([[[0,1,0],[1,0,0],[0,0,-1]]]);Cr=stiffness_material(p['materials']['top'],R)[0];assert abs(Cr[0,0]/C[1,1]-1)<1e-12
 return dict(partition='pass',rigidMotions='pass',constantStrainEnergy='pass',consistentMassSPD='pass',orthotropicRotation='pass')

def solve_case(key,out,size=55,modes=16):
 start=time.time();p=default_project(key);p['solver'].update(size=size,modes=modes,airModes=8);raw=mesh(p,out,lambda v,t:print(key,round(v,2),t,flush=True));w=wood_system(raw);ext,interfaces,ap=boundary(raw);B,ports=port_matrix(raw,w,ext);a=air_system(raw,w,interfaces,ap);model=prepare(raw,w,a,B,ports,ext);r=public_response(model,p)
 assert w['quality']['modalResidualMax']<1e-5
 assert w['loss'].min()>0 and w['loss'].max()<.16
 assert len(ports)==6 and np.min(np.diff(ports[:,0]))>.005
 freq=np.r_[0,np.geomspace(.01,6000,250)];Y,H=coefficients(model,p,freq);assert np.max(abs(Y-Y.transpose(0,2,1)))<1e-8
 assert np.max(abs(Y[0]))==0 and np.max(abs(H[0]))==0
 assert r['stats']['minimumPassivity']>-1e-8
 assert np.max(abs(Y[1]))<1e-4
 if a:assert a['k2'][0]<1e-6
 v=visual_mesh(model);assert len(v['triangles'])>0 and 'air' in v
 p['excitation']['duration']=1.5;audio=synthesize(model,p,[dict(string=0,time=0),dict(string=5,time=.1)])
 for k in ['force','velocity','pressure']:assert np.isfinite(audio[k]).all() and np.max(abs(audio[k]))>0
 edit=copy.deepcopy(p);edit['modalEdits']={'0':{'f':r['modes'][0]['f']*1.12,'gainDB':6}};Ye,_=coefficients(model,edit,freq);effect=float(np.linalg.norm(Ye-Y)/np.linalg.norm(Y));assert effect>.01
 for i in range(6):
  Z=string_impedance(string_properties(p,i),np.geomspace(1,8000,500));assert np.isfinite(Z).all();assert Z.real.min()>-1e-6
 report=dict(preset=key,seconds=time.time()-start,stats=r['stats'],dryFrequencies=[m['f'] for m in r['modes']],virtualEditRelativeMobilityChange=effect,quality=w['quality'],audio={k:dict(peak=float(abs(audio[k]).max()),rms=float(np.sqrt(np.mean(audio[k]**2)))) for k in ['force','velocity','pressure']})
 Path(out,'verification.json').write_text(json.dumps(report,indent=2));return report,model,p,audio

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');parser.add_argument('--output',default='data/verification');args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True);report={'elementChecks':element_checks(),'cases':[]};print(report['elementChecks'],flush=True)
 if args.full:
  for key in ['om','classical','selmer_oval','selmer_d','dread','archtop']:
   r,model,p,audio=solve_case(key,out/key);report['cases'].append(r);(out/'report.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
