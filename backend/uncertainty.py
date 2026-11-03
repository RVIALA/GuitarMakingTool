"""Monte Carlo modal sensitivity, not material/geometry uncertainty propagation."""
import copy
import numpy as np
from .response import coefficients,modal_parameters
from .strings import string_properties,string_impedance

def ensemble(model,p,settings):
 def number(key,default,lo,hi,integer=False):
  v=settings.get(key,default)
  if isinstance(v,bool) or not isinstance(v,(int,float)) or not np.isfinite(v) or not lo<=v<=hi or integer and int(v)!=v:raise ValueError('Uncertainty '+key)
  return int(v) if integer else float(v)
 count=number('samples',24,8,64,True);seed=number('seed',2026,0,2147483647,True);port=number('port',0,0,11,True)
 lo=number('fmin',20,.1,19999);hi=number('fmax',1600,1,20000)
 if lo>=hi:raise ValueError('fmin < fmax')
 cvf=number('frequencyCV',2,0,20)/100;cvz=number('dampingCV',10,0,50)/100;cvg=number('participationCV',5,0,30)/100;correlation=number('correlation',.5,0,1)
 kind=settings.get('kind','mobility');loaded=settings.get('loaded',False)
 if kind not in ['mobility','pressure'] or not isinstance(loaded,bool):raise ValueError('Uncertainty response')
 wm,z,g=modal_parameters(model,p);n=len(model['wood']['omega']);f0=wm[:n]/(2*np.pi);rng=np.random.default_rng(seed)
 def factors(cv):
  sigma=np.sqrt(np.log1p(cv*cv));draw=np.sqrt(correlation)*rng.normal(size=(count,1))+np.sqrt(1-correlation)*rng.normal(size=(count,n))
  return np.exp(sigma*draw-.5*sigma*sigma)
 fs=f0*factors(cvf);zs=z[:n]*factors(cvz);gs=g[:n]*factors(cvg)
 # Include actual sampled resonances and their half-widths, not interpolated FRF peaks.
 extra=(fs[:,:,None]*(1+zs[:,:,None]*np.array([-1,0,1]))).ravel();f=np.unique(np.r_[np.linspace(lo,hi,1024),extra[(extra>lo)&(extra<hi)]])
 if len(f)>18000:raise ValueError('Réduire la bande ou le nombre de tirages / Reduce band or sample count')
 def response(project):
  Y,H=coefficients(model,project,f,pressure=kind=='pressure')
  if loaded:
   Z=np.tile(np.stack([string_impedance(string_properties(project,i),f) for i in range(6)],axis=1),(1,2));rhs=np.zeros((len(f),12),complex);rhs[:,port]=1;force=np.linalg.solve(np.eye(12)[None]+Z[:,:,None]*Y,rhs[:,:,None])[:,:,0]
   return np.einsum('fi,fi->f',Y[:,port,:] if kind=='mobility' else H,force)
  return Y[:,port,port] if kind=='mobility' else H[:,port]
 nominal=abs(response(p));curves=[];clipped=0
 for i in range(count):
  sample=copy.deepcopy(p);sample['modalEdits']={}
  for j in range(n):
   raw=[fs[i,j],100*zs[i,j],40*np.log10(gs[i,j])];bounded=np.clip(raw,[5,.1,-24],[20000,15,24]);clipped+=int(np.any(bounded!=raw));sample['modalEdits'][str(j)]=dict(zip(['f','zeta','gainDB'],map(float,bounded)))
  curves.append(abs(response(sample)))
 q=np.quantile(curves,[.1,.5,.9],axis=0)
 return dict(frequency=f.tolist(),nominal=nominal.tolist(),p10=q[0].tolist(),p50=q[1].tolist(),p90=q[2].tolist(),samples=count,seed=seed,clipped=clipped,settings=settings,method='Lognormal modal Monte Carlo; fixed FE mode shapes, air and residual projection. Pointwise quantiles, not confidence intervals.')
