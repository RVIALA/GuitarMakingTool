"""Independent analytical benchmarks for solid bending and rigid cavity modes."""
import sys,itertools,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from backend.catalog import default_project
from backend.fem import wood_system,air_system

def grid_tets(lengths,counts):
 nx,ny,nz=counts;axes=[np.linspace(0,a,n+1) for a,n in zip(lengths,counts)];points=np.array(list(itertools.product(*axes)));idx=lambda i,j,k:(i*(ny+1)+j)*(nz+1)+k;tet=[]
 for i,j,k in itertools.product(range(nx),range(ny),range(nz)):
  for perm in itertools.permutations(range(3)):
   c=np.array([i,j,k]);v=[idx(*c)]
   for a in perm:c[a]+=1;v.append(idx(*c))
   tet.append(v)
 return points,np.array(tet)

def beam(n):
 xyz,tet=grid_tets([.04,1.,.02],[1,n,1]);xyz[:,0]-=.02;edges=[[0,1],[1,2],[2,0],[0,3],[2,3],[1,3]];points=xyz.tolist();mids={};conn=[]
 for t in tet:
  row=list(t)
  for i,j in edges:
   key=tuple(sorted([int(t[i]),int(t[j])]))
   if key not in mids:mids[key]=len(points);points.append(((xyz[key[0]]+xyz[key[1]])/2).tolist())
   row.append(mids[key])
  conn.append(row)
 p=default_project();p['body']['length']=1000;p['solver'].update(modes=8,support='neck');p['materials']['bridge'].update(rho=500,EL=10,ER=10,ET=10,GLR=10/2.6,GLT=10/2.6,GRT=10/2.6,nuLR=.3,nuLT=.3,nuRT=.3)
 # A bridge-tagged rectangular test beam uses Cartesian isotropic material.
 raw=dict(points=np.array(points),elements=np.array(conn),labels=np.zeros(len(conn),int),groups={0:dict(part='bridge')},edges=edges,outline=np.array([[0,0],[0,1],[.04,1],[.04,0],[0,0]]),project=p)
 # Only y=1 nodes lie beyond the final 20 mm at these two mesh sizes.
 p['body']['length']=1000
 w=wood_system(raw);calculated=w['omega'][0]/2/np.pi;E=10e9;rho=500;A=.04*.02;I=.04*.02**3/12;expected=1.8751040687**2/(2*np.pi)*np.sqrt(E*I/(rho*A))
 return dict(elements=len(conn),frequency=calculated,EulerBernoulli=expected,errorPercent=(calculated/expected-1)*100)

def cavity():
 xyz,tet=grid_tets([.5,.3,.1],[10,6,3]);p=default_project();p['solver']['airModes']=8;raw=dict(points=xyz,elements=tet,labels=np.zeros(len(tet),int),groups={0:dict(part='air')},project=p,air=True)
 aperture=[dict(corners=tet[0,:3],area=.01,center=xyz[tet[0,:3]].mean(0))];a=air_system(raw,dict(V=np.zeros((0,1))),[],aperture);f=343*np.sqrt(a['k2'])/2/np.pi;expected=sorted([343/2*np.sqrt((i/.5)**2+(j/.3)**2+(k/.1)**2) for i,j,k in itertools.product(range(4),repeat=3) if i+j+k])[:3];error=(f[1:4]/expected-1)*100
 assert np.max(abs(error))<4
 return dict(calculated=f[:4].tolist(),analytical=[0,*expected],errorPercent=error.tolist())
if __name__=='__main__':
 b1,b2=beam(12),beam(24);assert abs(b2['errorPercent'])<3 and abs(b2['errorPercent'])<abs(b1['errorPercent']);r=dict(beamCoarse=b1,beamFine=b2,cavity=cavity());print(json.dumps(r,indent=2))
