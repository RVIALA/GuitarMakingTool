"""Tetra10 orthotropic elasticity and Tetra4 pressure acoustics, SI units."""
import math,itertools
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh
from .catalog import MATERIALS,compliance
from .geometry import arch

GRAD=np.array([[-1,-1,-1],[1,0,0],[0,1,0],[0,0,1]],float)
_q=[([.25]*4,-.0131555555555556)]
for i in range(4):
 l=np.full(4,1/14);l[i]=11/14;_q.append((l,.00762222222222222))
for ij in itertools.combinations(range(4),2):
 l=np.full(4,.100596423833201);l[list(ij)]=.399403576166799;_q.append((l,.0248888888888889))
LAMBDA=np.array([x[0] for x in _q]);WEIGHTS=np.array([x[1] for x in _q])

def shape(edges):
 n=np.empty((11,10));dn=np.empty((11,10,3))
 for i in range(4):n[:,i]=LAMBDA[:,i]*(2*LAMBDA[:,i]-1);dn[:,i]=(4*LAMBDA[:,i,None]-1)*GRAD[i]
 for k,(i,j) in enumerate(edges):n[:,k+4]=4*LAMBDA[:,i]*LAMBDA[:,j];dn[:,k+4]=4*(LAMBDA[:,i,None]*GRAD[j]+LAMBDA[:,j,None]*GRAD[i])
 return n,dn

def frames(desc,centers,p):
 N=len(centers);part=desc['part'];L=np.zeros((N,3));R=np.zeros_like(L)
 if part in ['top','back']:L[:,1]=1;R[:,0]=1
 elif part=='ribs':
  pts=np.asarray(p['_outline']);a=pts[:-1,:2];b=pts[1:,:2];v=b-a;den=np.sum(v*v,axis=1)
  for k,c in enumerate(centers):
   t=np.clip(np.sum((c[:2]-a)*v,axis=1)/np.maximum(den,1e-20),0,1);j=np.argmin(np.sum((a+t[:,None]*v-c[:2])**2,axis=1));L[k,:2]=v[j]
  R[:,2]=1
 elif part=='braces':L[:,0]=math.cos(desc.get('angle',math.pi/2));L[:,1]=math.sin(desc.get('angle',math.pi/2));R[:,2]=1
 else:L[:,0]=1;R[:,1]=1
 # Transport wood directions through the same arching map as the nodes.
 x,y=centers[:,0],centers[:,1];d=p['body']['depth']*.001
 at=arch(p,x,y,'top');ab=arch(p,x,y,'back');z0=(centers[:,2]-at)/(1+(at+ab)/d);t=np.clip((z0+d)/d,0,1)
 eps=1e-6
 dx=t*(arch(p,x+eps,y,'top')-arch(p,x-eps,y,'top'))/(2*eps)-(1-t)*(arch(p,x+eps,y,'back')-arch(p,x-eps,y,'back'))/(2*eps)
 dy=t*(arch(p,x,y+eps,'top')-arch(p,x,y-eps,'top'))/(2*eps)-(1-t)*(arch(p,x,y+eps,'back')-arch(p,x,y-eps,'back'))/(2*eps)
 scale=np.where((z0>-d)&(z0<0),1+(at+ab)/d,1)
 for direction in [L,R]:direction[:,2]=direction[:,0]*dx+direction[:,1]*dy+direction[:,2]*scale
 L/=np.linalg.norm(L,axis=1)[:,None];R-=L*np.sum(L*R,axis=1)[:,None];R/=np.linalg.norm(R,axis=1)[:,None];T=np.cross(L,R)
 m=p['materials'][part];angle=np.deg2rad(m.get('grain',0));L2=L*np.cos(angle)+R*np.sin(angle);R2=-L*np.sin(angle)+R*np.cos(angle)
 ring=np.deg2rad(m.get('ring',0));R3=R2*np.cos(ring)+T*np.sin(ring);T3=-R2*np.sin(ring)+T*np.cos(ring)
 return np.stack([L2,R3,T3],axis=2)

def stiffness_material(m,rot):
 C=np.linalg.inv(compliance(m));basis=np.zeros((6,3,3));basis[0,0,0]=basis[1,1,1]=basis[2,2,2]=1
 for k,(i,j) in enumerate([(0,1),(0,2),(1,2)],3):basis[k,i,j]=basis[k,j,i]=.5
 local=np.einsum('eia,kij,ejb->ekab',rot,basis,rot)
 Q=np.stack([local[:,:,0,0],local[:,:,1,1],local[:,:,2,2],2*local[:,:,0,1],2*local[:,:,0,2],2*local[:,:,1,2]],axis=1)
 return np.einsum('eai,ab,ebj->eij',Q,C,Q)

def wood_system(raw,progress=lambda *a:None):
 p=raw['project'];p['_outline']=raw['outline'].tolist();xyz=raw['points'];conn=raw['elements'];labels=raw['labels'];groups=raw['groups'];wood_idx=np.flatnonzero([groups[int(k)]['part']!='air' for k in labels]);ids=np.unique(conn[wood_idx]);mapper=np.full(len(xyz),-1,int);mapper[ids]=np.arange(len(ids));nDOF=len(ids)*3
 if nDOF>180000:raise ValueError('Plus de 180 000 ddl : augmenter la taille de maille / increase mesh size')
 N,dN=shape(raw['edges']);rows=[];cols=[];vals=[];mr=[];mc=[];mv=[];totalmass=0.;minimum=1e99;maximum=0.;volumes=np.zeros(len(conn));chunkloss=[]
 for gi,desc in groups.items():
  if desc['part']=='air':continue
  indices=wood_idx[labels[wood_idx]==gi];m=p['materials'][desc['part']];density=m['rho']
  for start in range(0,len(indices),128):
   ii=indices[start:start+128];ec=mapper[conn[ii]];x=xyz[conn[ii]];rot=frames(desc,x.mean(1),p);C=stiffness_material(m,rot)
   J=np.einsum('qna,enb->eqab',dN,x);det=np.linalg.det(J)
   if np.any(np.min(det,axis=1)*np.max(det,axis=1)<=0) or np.min(np.abs(det))<1e-18:raise ValueError('Élément dégénéré/inversé : réduire le bombé ou modifier le maillage / invalid element')
   minimum=min(minimum,float(np.min(abs(det))));maximum=max(maximum,float(np.max(abs(det))));grad=np.einsum('eqba,qna->eqnb',np.linalg.inv(J),dN);B=np.zeros((len(ii),11,6,30))
   for j in range(10):
    gx,gy,gz=[grad[:,:,j,k] for k in range(3)];B[:,:,0,3*j]=gx;B[:,:,1,3*j+1]=gy;B[:,:,2,3*j+2]=gz;B[:,:,3,3*j]=gy;B[:,:,3,3*j+1]=gx;B[:,:,4,3*j]=gz;B[:,:,4,3*j+2]=gx;B[:,:,5,3*j+1]=gz;B[:,:,5,3*j+2]=gy
   w=abs(det)*WEIGHTS;ke=np.einsum('eqai,eab,eqbj,eq->eij',B,C,B,w,optimize=True);me=density*np.einsum('qi,qj,eq->eij',N,N,w);volume=w.sum(1);volumes[ii]=volume;totalmass+=float(volume.sum()*density)
   dofs=(ec[:,:,None]*3+np.arange(3)).reshape(-1,30);rows.append(np.repeat(dofs,30,axis=1).ravel());cols.append(np.tile(dofs,(1,30)).ravel());vals.append(ke.ravel());chunkloss.append(m['loss']/100)
   for k in range(3):mr.append(np.repeat(ec*3+k,10,axis=1).ravel());mc.append(np.tile(ec*3+k,(1,10)).ravel());mv.append(me.ravel())
  progress(.34+.17*(gi+1)/max(1,len(groups)),'Assemblage orthotrope / Orthotropic assembly')
 K=sparse.coo_matrix((np.concatenate(vals),(np.concatenate(rows),np.concatenate(cols))),shape=(nDOF,nDOF)).tocsr();M=sparse.coo_matrix((np.concatenate(mv),(np.concatenate(mr),np.concatenate(mc))),shape=(nDOF,nDOF)).tocsr();K=(K+K.T)*.5;M=(M+M.T)*.5
 # Assemble the energy-weighted loss operator before extracting modes, then
 # release element COO buffers. Keeping them during eigensolution doubled RAM.
 KL=sparse.csr_matrix(K.shape)
 for eta in sorted(set(chunkloss)):
  chosen=[i for i,x in enumerate(chunkloss) if x==eta];kp=sparse.coo_matrix((np.concatenate([vals[i] for i in chosen]),(np.concatenate([rows[i] for i in chosen]),np.concatenate([cols[i] for i in chosen]))),shape=(nDOF,nDOF)).tocsr();KL+=eta*kp
 del rows,cols,vals,mr,mc,mv,chunkloss,kp
 fixed=np.array([],int);coords=xyz[ids]
 if p['solver']['support']=='neck':fixed=np.flatnonzero(coords[:,1]>p['body']['length']*.001-.02)
 if p['solver']['support']=='rim':fixed=np.unique(mapper[conn[np.flatnonzero([groups[int(k)]['part']=='ribs' for k in labels])]])
 locked=(fixed[:,None]*3+np.arange(3)).ravel();free=np.setdiff1d(np.arange(nDOF),locked);nm=int(p['solver']['modes']);fmin=max(5.,p['solver'].get('fmin',5));fmax=p['solver'].get('fmax',4000)
 # Shift near the lower band edge; retain the lowest requested modes above it.
 # A second, larger search is needed when many neighbours lie below the edge.
 progress(.55,'Modes de structure / Structural modes')
 k=min(nm+8,len(free)-2);sigma=-1 if fmin<=5 else (2*np.pi*fmin)**2*(1-1e-7)
 while True:
  ev,V=eigsh(K[free][:,free],k=k,M=M[free][:,free],sigma=sigma,which='LM',tol=1e-7,maxiter=4000)
  order=np.argsort(ev);ev=ev[order];V=V[:,order];frequencies=np.sqrt(np.maximum(0,ev))/(2*np.pi)
  eligible=(frequencies>=fmin*(1-1e-8))&(frequencies<=fmax*(1+1e-8))
  if eligible.sum()>=nm or frequencies[-1]>=fmax or k>=min(2*nm+20,len(free)-2):break
  k=min(2*nm+20,len(free)-2)
 coverage=bool(frequencies[-1]>=fmax and eligible.sum()<=nm)
 ev=ev[eligible][:nm];V=V[:,eligible][:,:nm]
 if not len(ev):raise ValueError('Aucun mode dans la bande demandée : élargir la bande ou le budget / no modes in requested band')
 full=np.zeros((nDOF,len(ev)));full[free]=V
 for j in range(len(ev)):full[:,j]/=math.sqrt(float(full[:,j]@(M@full[:,j])))
 residual=[float(np.linalg.norm((K@full[:,j]-ev[j]*(M@full[:,j]))[free])/max(1e-20,np.linalg.norm((K@full[:,j])[free]))) for j in range(len(ev))]
 modal_loss=np.sum(full*(KL@full),axis=0)/ev
 return dict(K=K,M=M,ids=ids,map=mapper,V=full,omega=np.sqrt(ev),loss=modal_loss,mass=totalmass,volumes=volumes,free=free,modalBand=dict(requestedMin=fmin,requestedMax=fmax,complete=coverage,cap=nm,extracted=len(ev)),quality=dict(minAbsJacobian=minimum,maxAbsJacobian=maximum,modalResidualMax=max(residual,default=0),dofs=nDOF,locked=len(locked)),wood_idx=wood_idx)

FACE=[(0,1,2,3),(0,1,3,2),(0,2,3,1),(1,2,3,0)]
def boundary(raw):
 faces={};g=raw['groups'];conn=raw['elements'];labels=raw['labels']
 for ei,e in enumerate(conn):
  for a,b,c,o in FACE:
   key=tuple(sorted([int(e[a]),int(e[b]),int(e[c])]))
   faces.setdefault(key,[]).append((ei,[a,b,c],o))
 mid={}
 for e in conn:
  for k,(a,b) in enumerate(raw['edges']):mid[tuple(sorted([int(e[a]),int(e[b])]))]=int(e[k+4])
 exterior=[];interfaces=[];aperture=[];xyz=raw['points'];tt=raw['project']['body']['top']*.001
 for key,owners in faces.items():
  solid=[o for o in owners if g[int(labels[o[0]])]['part']!='air'];air=[o for o in owners if g[int(labels[o[0]])]['part']=='air']
  def item(owner):
   ei,loc,opp=owner;corners=conn[ei,loc].copy();x=xyz[corners];normal=np.cross(x[1]-x[0],x[2]-x[0]);area=np.linalg.norm(normal)/2;normal/=max(1e-30,2*area)
   if np.dot(normal,xyz[conn[ei,opp]]-x.mean(0))>0:normal=-normal
   mids=[mid[tuple(sorted([int(corners[a]),int(corners[b])]))] for a,b in [(0,1),(1,2),(2,0)]]
   return dict(corners=corners,nodes=np.r_[corners,mids],normal=normal,area=area,center=x.mean(0),element=ei,group=int(labels[ei]))
  if len(solid)==1 and not air:exterior.append(item(solid[0]))
  if len(solid)==1 and len(air)==1:interfaces.append((item(solid[0]),item(air[0])))
  if len(air)==1 and not solid:
   f=item(air[0]);aperture.append(f)
 return exterior,interfaces,aperture

def port_matrix(raw,wood,exterior):
 p=raw['project'];br=p['bridge'];xyz=raw['points'];B=np.zeros((len(wood['ids'])*3,12));ports=[]
 candidates=[f for f in exterior if raw['groups'][f['group']]['part']=='bridge' and f['normal'][2]>.6]
 if not candidates:raise ValueError('Surface du chevalet absente / bridge surface missing')
 for i in range(6):
  xy=np.array([(br['x']+(i-2.5)*br['spacing']/5)*.001,br['y']*.001]);best=None
  for f in candidates:
   a=xyz[f['corners'],:2];mat=np.c_[a[0]-a[2],a[1]-a[2]]
   if abs(np.linalg.det(mat))<1e-15:continue
   l=np.r_[np.linalg.solve(mat,xy-a[2]),0.];l[2]=1-l[:2].sum();penalty=max(0,-l.min())
   if best is None or penalty<best[0]:best=(penalty,f,l)
  _,f,l=best
  if l.min()<-.02:raise ValueError('Point corde hors chevalet / string point outside bridge')
  N=np.r_[l*(2*l-1),4*l[0]*l[1],4*l[1]*l[2],4*l[2]*l[0]];nodes=wood['map'][f['nodes']];B[nodes*3+2,i]+=N;B[nodes*3,i+6]+=N;position=N@xyz[f['nodes']];ports.append(position)
 return B,np.array(ports)

def air_system(raw,wood,interfaces,aperture,progress=lambda *a:None):
 if not raw['air']:return None
 xyz=raw['points'];indices=np.flatnonzero([raw['groups'][int(k)]['part']=='air' for k in raw['labels']]);tet=raw['elements'][indices,:4];ids=np.unique(tet);mapper=np.full(len(xyz),-1,int);mapper[ids]=np.arange(len(ids));cells=mapper[tet];x=xyz[tet];J=x[:,1:]-x[:,:1];volume=abs(np.linalg.det(J))/6;grad=np.einsum('eba,na->enb',np.linalg.inv(J),GRAD);ke=np.einsum('ena,ema,e->enm',grad,grad,volume);me=volume[:,None,None]*(np.ones((4,4))+np.eye(4))/20;rows=np.repeat(cells,4,axis=1).ravel();cols=np.tile(cells,(1,4)).ravel();shape_=(len(ids),len(ids));K=sparse.coo_matrix((ke.ravel(),(rows,cols)),shape=shape_).tocsr();M=sparse.coo_matrix((me.ravel(),(rows,cols)),shape=shape_).tocsr();count=min(int(raw['project']['solver']['airModes']),len(ids)-2)
 progress(.7,'Cavité EF / FE cavity');ev,V=eigsh(K,k=count,M=M,sigma=-1,which='LM',tol=1e-8);order=np.argsort(ev);ev=np.maximum(0,ev[order]);V=V[:,order]
 for j in range(count):V[:,j]/=np.sqrt(V[:,j]@(M@V[:,j]))
 ap=np.zeros(count);surface=0.
 for f in aperture:
  ap+=f['area']*V[mapper[f['corners']]].mean(0);surface+=f['area']
 if surface<=0:raise ValueError('Ouverture acoustique non trouvée / no acoustic opening')
 ap/=surface
 air=dict(K=K,M=M,V=V,k2=ev,h=ap,area=surface,volume=float(volume.sum()),ids=ids,aperture=aperture,nodes=len(ids),cells=len(tet))
 air['C']=coupling_to_air(raw,wood['V'],wood.get('map'),interfaces,air)
 return air

def coupling_to_air(raw,basis,wood_map,interfaces,air):
 """Consistent quadratic-solid/linear-pressure interface projection."""
 C=np.zeros((basis.shape[1],len(air['k2'])));mapper=np.full(len(raw['points']),-1,int);mapper[air['ids']]=np.arange(len(air['ids']))
 q=[]
 for a,w in [(.445948490915965,.223381589678011),(.091576213509771,.109951743655322)]:
  for k in range(3):l=np.full(3,a);l[k]=1-2*a;q.append((l,w))
 for sf,af in interfaces:
  si=wood_map[sf['nodes']];ai=mapper[af['corners']];permutation=[list(af['corners']).index(x) for x in sf['corners']]
  u=basis.reshape(-1,3,basis.shape[1])[si];un=np.einsum('nci,c->ni',u,af['normal']);pa=air['V'][ai][permutation]
  for l,w in q:
   N=np.r_[l*(2*l-1),4*l[0]*l[1],4*l[1]*l[2],4*l[2]*l[0]];C+=sf['area']*w*np.outer(N@un,l@pa)
 return C
