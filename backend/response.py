"""Reduced FE fluid/structure response and field synthesis. No fitted guitar FRFs."""
import copy,hashlib,json,threading
import numpy as np
from .reduction import residual_modes
from .strings import string_properties,string_impedance

RHO=1.204;SOUND=343.
def geometry_key(p):
 keys={k:p[k] for k in ['body','hole','bridge','braces','materials','solver']};keys['hole']={k:v for k,v in p['hole'].items() if k not in ['endFactor','resistance']}
 return hashlib.sha256(json.dumps(keys,sort_keys=True).encode()).hexdigest()[:20]

def prepare(raw,wood,air,B,ports,exterior):
 p=raw['project'];residual=residual_modes(raw,wood,B);basis=np.column_stack([wood['V'],residual['V']]);nm=basis.shape[1];V=basis.reshape(-1,3,nm);map_=wood['map'];centers=[];radiation=[];areas=[]
 if air is not None:
  from .fem import coupling_to_air,boundary
  _,interfaces,_=boundary(raw);air=dict(air,C=np.vstack([air['C'],coupling_to_air(raw,residual['V'],wood['map'],interfaces,air)])) if residual['rank'] else dict(air)
 for f in exterior:
  if np.min(map_[f['nodes']])<0:continue
  # Exact area average of a planar quadratic triangle: zero corner weights,
  # one third on each midside node. Face normals are piecewise planar.
  u=V[map_[f['nodes'][3:]]].mean(0);r=f['area']*(f['normal']@u);centers.append(f['center']);radiation.append(r);areas.append(f['area'])
 return dict(project=copy.deepcopy(p),raw=raw,wood=wood,air=air,B=B,ports=ports,exterior=exterior,
  projection=basis.T@B,basis=basis,residual=residual,omega=np.r_[wood['omega'],residual['omega']],centers=np.array(centers),radiation=np.array(radiation),areas=np.array(areas),key=geometry_key(p),cache={},lock=threading.RLock())

def modal_parameters(model,p):
 w=model['omega'].copy();base=len(model['wood']['omega']);z=np.r_[np.asarray(model['wood']['loss'])/2,np.full(len(w)-base,p['synthesis']['residualDamping']/100)];gain=np.ones(len(w))
 for index,edit in p.get('modalEdits',{}).items():
  i=int(index)
  if not 0<=i<base:continue
  f=float(edit.get('f',w[i]/(2*np.pi)));d=float(edit.get('zeta',z[i]*100));g=float(edit.get('gainDB',0))
  if not (5<=f<=20000 and .1<=d<=15 and -24<=g<=24):raise ValueError('Modification modale hors limites / modal edit out of bounds')
  w[i]=2*np.pi*f;z[i]=d/100;gain[i]=10**(g/40)
 return w,z,gain

def coefficients(model,p,freq,pressure=True):
 """Return reciprocal 12x12 mobility and pressure/force for all six ports."""
 freq=np.asarray(freq,float);w=2*np.pi*np.maximum(freq,.01);wm,z,gain=modal_parameters(model,p);keep=np.arange(len(wm)) if p['synthesis']['extension']=='residual' else np.arange(len(model['wood']['omega']));wm=wm[keep];z=z[keep];gain=gain[keep];P=model['projection'][keep]*gain[:,None];C=model['air']['C'][keep]*gain[:,None] if model['air'] is not None else None;nm=len(wm);air=model['air'];np_=P.shape[1];outY=np.zeros((len(w),np_,np_),complex);outH=np.zeros((len(w),np_),complex)
 point=np.asarray(p['monitor']['point'],float)
 if point.shape!=(3,) or not np.isfinite(point).all():raise ValueError('Point acoustique invalide')
 distances=np.linalg.norm(model['centers']-point,axis=1)
 if pressure and np.min(distances)<.03:raise ValueError('Point P trop près de la surface : 30 mm minimum / move P away from surface')
 rad=model['radiation'][:,keep]*gain[None,:]
 if air is not None:
  S=air['area'];radius=np.sqrt(S/np.pi);leff=p['hole']['endFactor']*radius;mass=RHO*leff/S
  # Low-ka monopole radiation resistance plus editable dissipative port factor.
  center=np.average(np.array([a['center'] for a in air['aperture']]),axis=0,weights=[a['area'] for a in air['aperture']]);port_distance=max(.03,float(np.linalg.norm(center-point)))
 for start in range(0,len(w),96):
  sl=slice(start,start+96);ww=w[sl];n=len(ww);ds=wm[None,:]**2-ww[:,None]**2+2j*ww[:,None]*z*wm[None,:]
  if air is None:q=P[None,:,:]/ds[:,:,None]
  else:
   # Exact Woodbury elimination: solve only the retained cavity coordinates.
   ka=air['k2'];wa=SOUND*np.sqrt(ka);den=ka[None,:]-(ww[:,None]/SOUND)**2+2j*.025*ww[:,None]*wa[None,:]/SOUND**2
   resistance=p['hole']['resistance']*(RHO*ww**2/(4*np.pi*SOUND)+.05*mass*max(1,SOUND*np.sqrt(S/(air['volume']*leff))))
   da=-ww**2*mass+1j*ww*resistance;inverse=1/np.column_stack([ds,da]);A=np.vstack([C,air['h'][None,:]])
   U=inverse[:,:,None]*A[None,:,:];reduced=-np.einsum('ia,fib->fab',A,U)
   ia=np.arange(len(ka));reduced[:,ia,ia]+=den/(RHO*ww[:,None]**2)
   q0=np.zeros((n,nm+1,np_),complex);q0[:,:nm]=P[None,:,:]/ds[:,:,None]
   acoustic=np.linalg.solve(reduced,np.einsum('ia,fij->faj',A,q0));q=q0+np.einsum('fia,faj->fij',U,acoustic)
  disp=np.einsum('mi,fmj->fij',P,q[:,:nm]);outY[sl]=1j*ww[:,None,None]*disp
  if pressure:
   # Exterior monopole-panel approximation, with the same signed FE normal
   # velocities; the acoustic aperture contributes its outward volume flow.
   G=np.exp(-1j*ww[:,None]*distances[None,:]/SOUND)/distances[None,:]
   radm=G@rad
   outH[sl]=-RHO*ww[:,None]**2/(4*np.pi)*np.einsum('fm,fmi->fi',radm,q[:,:nm])
   if air is not None:outH[sl]+=-RHO*ww[:,None]**2/(4*np.pi)*np.exp(-1j*ww[:,None]*port_distance/SOUND)/port_distance*q[:,-1,:]
 zero=freq==0;outY[zero]=0;outH[zero]=0
 return outY,outH

def response_grid(model,p):
 wm,z,gain=modal_parameters(model,p);upper=max(6000,p['synthesis']['fmax']);f=np.r_[0,np.arange(.5,1000,.5),np.arange(1000,4000,2.),np.arange(4000,upper+1,4.),upper]
 # Add points around structural poles; coupled peaks also get the dense low band.
 extra=np.concatenate([w/(2*np.pi)*(1+z0*np.array([-3,-1,-.5,0,.5,1,3])) for w,z0 in zip(wm,z)])
 f=np.unique(np.r_[f,extra[(extra>0)&(extra<upper)]])
 key=json.dumps([p.get('modalEdits',{}),p['monitor']['point'],p['hole']['endFactor'],p['hole']['resistance'],p['synthesis']],sort_keys=True)
 with model.setdefault('lock',threading.RLock()):
  found=model['cache'].get(key)
  if found is None:
   Y,H=coefficients(model,p,f);found=(f,Y,H);model['cache']={key:found}
  return found

def public_response(model,p):
 f,Y,H=response_grid(model,p);diag=np.diagonal(Y,axis1=1,axis2=2);wm,z,gain=modal_parameters(model,p);a=model['air'];radius=np.sqrt(a['area']/np.pi) if a else 0;leff=p['body']['top']*.001+p['hole']['endFactor']*radius if a else 1
 modes=[dict(index=i,f=float(w/2/np.pi),zeta=float(z[i]*100),gainDB=float(40*np.log10(gain[i])),original=float(model['wood']['omega'][i]/(2*np.pi))) for i,w in enumerate(wm[:len(model['wood']['omega'])])]
 # String-loaded bridge responses use exactly the same 12-port connection as synthesis.
 Z=np.tile(np.stack([string_impedance(string_properties(p,i),f) for i in range(6)],axis=1),(1,2));Q=np.linalg.solve(np.eye(12)[None]+Z[:,:,None]*Y,np.broadcast_to(np.eye(12),Y.shape));loaded=np.einsum('fij,fjk->fik',Y,Q);loadedH=np.einsum('fi,fij->fj',H,Q);ld=np.diagonal(loaded,axis1=1,axis2=2)
 # Hermitian mobility eigenvalues verify dissipative driving-point behaviour.
 tests=Y[1::max(1,len(Y)//120)];minimum=float(min(np.linalg.eigvalsh((v+v.conj().T)/2).min() for v in tests))
 return dict(frequencies=f.tolist(),mobilityReal=diag.real.T.tolist(),mobilityImag=diag.imag.T.tolist(),pressureReal=H.real.T.tolist(),pressureImag=H.imag.T.tolist(),loadedMobilityReal=ld.real.T.tolist(),loadedMobilityImag=ld.imag.T.tolist(),loadedPressureReal=loadedH.real.T.tolist(),loadedPressureImag=loadedH.imag.T.tolist(),modes=modes,projection=dict(method='residual-flexibility Ritz',count=model['residual']['rank'],staticError=model['residual']['staticError'],enabled=p['synthesis']['extension']=='residual',frequencies=(model['residual']['omega']/(2*np.pi)).tolist()),modalBand=model['wood']['modalBand'],
  stats=dict(mass=model['wood']['mass'],dofs=model['wood']['quality']['dofs'],nodes=len(model['raw']['points']),tetrahedra=len(model['raw']['elements']),modalResidual=model['wood']['quality']['modalResidualMax'],firstMode=float(min(model['wood']['omega'])/2/np.pi),lastMode=float(max(model['wood']['omega'])/2/np.pi),computedModes=len(model['wood']['omega']),minimumPassivity=minimum,
  airVolume=a['volume'] if a else 0,holeArea=a['area'] if a else 0,helmholtzRigid=SOUND/(2*np.pi)*np.sqrt(a['area']/(a['volume']*leff)) if a else 0,airModes=(SOUND*np.sqrt(a['k2'])/(2*np.pi)).tolist() if a else []),ports=model['ports'].tolist(),key=model['key'])

def visual_mesh(model):
 raw=model['raw'];mapper=model['wood']['map'];faces=[];parts=[];faces6=[]
 from .fem import boundary
 _,interfaces,_=boundary(raw);surface=model['exterior']+[sf for sf,af in interfaces]
 for f in surface:
  n=mapper[f['nodes']];faces6.append(n.tolist())
  for tri in [[n[0],n[3],n[5]],[n[3],n[1],n[4]],[n[5],n[4],n[2]],[n[3],n[4],n[5]]]:faces.append(tri);parts.append(f['group'])
 points=raw['points'][model['wood']['ids']]
 groups={str(k):dict(part=v['part'],side=v.get('side'),id=v.get('id'),angle=v.get('angle',0),tetrahedra=int(np.count_nonzero(raw['labels']==k)),volume=float(model['wood']['volumes'][raw['labels']==k].sum())) for k,v in raw['groups'].items() if v['part']!='air'}
 lines=[]
 for idx,desc in raw['groups'].items():
  if desc['part']=='air':continue
  from .fem import frames
  e=raw['elements'][raw['labels']==idx];centers=raw['points'][e].mean(1);take=np.linspace(0,len(centers)-1,min(12,len(centers))).astype(int);r=frames(desc,centers[take],raw['project'])
  for x,R in zip(centers[take],r):lines.append([x.tolist(),(x+.015*R[:,0]).tolist(),desc['part']])
 out=dict(faces6=faces6,faceParts=[f['group'] for f in surface],ports=model['ports'].tolist(),points=points.tolist(),triangles=np.asarray(faces).tolist(),parts=parts,groups=groups,grain=lines)
 if model['air'] is not None:
  from .fem import boundary
  _,interfaces,aperture=boundary(raw);af=[a['corners'] for _,a in interfaces]+[a['corners'] for a in aperture];ids=np.unique(af);mp=np.full(len(raw['points']),-1,int);mp[ids]=np.arange(len(ids));out['air']=dict(points=raw['points'][ids].tolist(),triangles=mp[np.array(af)].tolist())
 return out
