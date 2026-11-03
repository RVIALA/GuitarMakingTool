"""Documented outline data and physical cutaway geometry, in SI metres."""
import json
from functools import lru_cache
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,LineString,Point,box
from shapely.geometry.polygon import orient

ASSETS=Path(__file__).resolve().parent/'outlines'
@lru_cache(None)
def source(key):
 return json.loads((ASSETS/(key+'.json')).read_text(encoding='utf8'))
def source_key(p):return 'selmer' if p.get('family')=='gypsy' else p.get('preset','om') if p.get('preset') in ['om','dread','classical','archtop'] else 'om'
def metadata(p):return {k:v for k,v in source(source_key(p)).items() if k!='points'}
def catalog_outlines():return {k:{a:b for a,b in source(k).items() if a!='points'} for k in ['om','dread','classical','selmer','archtop']}
def bezier(p0,p1,p2,p3,n=48):
 t=np.linspace(0,1,n)[:,None];return (1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t*t*p2+t**3*p3

def right_point(poly,y,W):
 section=poly.intersection(LineString([[-W,y],[W,y]]))
 if section.is_empty:raise ValueError('Contour incompatible avec le pan coupé / cutaway incompatible with outline')
 return np.array([section.bounds[2],y])

@lru_cache(None)
def cutaway_profiles():
 return json.loads((Path(__file__).parent/'cutaways.json').read_text(encoding='utf8'))

def cutaway(poly,p):
 b=p['body'];kind=b.get('cutaway','none')
 if kind=='none':return poly
 if kind not in cutaway_profiles():raise ValueError('Profil de pan coupé inconnu / unknown cutaway profile')
 from shapely.affinity import scale
 from shapely.ops import substring
 W=b['width']*.001;L=b['length']*.001;sign=-1 if b.get('cutawaySide','right')=='left' else 1
 base=orient(scale(poly,xfact=sign,yfact=1,origin=(0,0)),sign=1)
 profile=cutaway_profiles()[kind];a=np.asarray(profile['points'],float)*[W,L]
 nx=.075*W;section=base.intersection(LineString([[nx,.90*L],[nx,1.03*L]]))
 if section.is_empty:raise ValueError('Le contour ne rejoint pas le talon du pan coupé / outline does not meet cutaway neck')
 N=np.array([nx,section.bounds[3]]);R=right_point(base,a[-1,1],W)
 d=np.r_[0,np.cumsum(np.linalg.norm(np.diff(a/[W,L],axis=0),axis=1))];t=d/d[-1]
 blend=t*t*(3-2*t);a+=(N-a[0])[None,:]*(1-blend[:,None])+(R-a[-1])[None,:]*blend[:,None]
 th=profile['throat'];horn=profile['horn'];i=np.argmin(abs(t-th))
 weight=np.where(t<=th,.5*(1-np.cos(np.pi*np.minimum(t/th,1))),np.where(t<horn,.5*(1+np.cos(np.pi*(t-th)/(horn-th))),0))
 depth=b.get('cutawayDepth',profile['defaultDepth'])*.001
 a[:,1]-=(depth-(N[1]-a[i,1]))*weight
 # Match the outer branch tangentially to the selected body's shoulder.
 j=np.searchsorted(t,max(horn+.12,.82));j=min(j,len(a)-3);A=a[j];ta=a[j]-a[j-2];ta/=np.linalg.norm(ta)
 dy=.002*L;tr=right_point(base,R[1]-dy,W)-right_point(base,R[1]+dy,W);tr/=np.linalg.norm(tr)
 h=np.linalg.norm(R-A)/3
 a=np.r_[a[:j],bezier(A,A+h*ta,R-h*tr,R,n=max(12,len(a)-j))]
 ring=LineString(base.exterior.coords);sN=ring.project(Point(N));sR=ring.project(Point(R));total=ring.length
 if sR<sN:
  rest=np.r_[np.asarray(substring(ring,sN,total).coords),np.asarray(substring(ring,0,sR).coords)[1:]]
 else:rest=np.asarray(substring(ring,sN,sR).coords)
 result=Polygon(np.r_[a[::-1],rest[1:]])
 if result.geom_type!='Polygon' or not result.is_valid or result.area<base.area*.65:raise ValueError('Pan coupé incompatible ou trop profond / incompatible or excessive cutaway')
 return orient(scale(result,xfact=sign,yfact=1,origin=(0,0)),sign=1.)

def outline(p,preview=False):
 b=p['body'];L=b['length']*.001;W=b['width']*.001
 if b.get('outline') is not None:
  a=np.asarray(b['outline'],float)*.001;span=np.ptp(a,axis=0)
  if min(span)<.001:raise ValueError('Contour sans surface / empty outline')
  a[:,0]=(a[:,0]-(a[:,0].min()+a[:,0].max())/2)*W/span[0];a[:,1]=(a[:,1]-a[:,1].min())*L/span[1]
 else:a=np.asarray(source(source_key(p))['points'])*[W,L]
 poly=Polygon(a)
 if not poly.is_valid or poly.area<.04:raise ValueError('Contour simple fermé requis / simple closed contour required')
 poly=cutaway(orient(poly,sign=1),p)
 # Shared CAD polygon for all components. Bounded simplification avoids hundreds
 # of tiny CAD edges without rescaling the shape after cutting away material.
 if not preview:
  detailed=poly;tolerance=p['body'].get('rimTolerance',.08)*.001
  for _ in range(6):
   poly=detailed.simplify(tolerance,preserve_topology=True)
   if detailed.hausdorff_distance(poly)<=p['body'].get('rimTolerance',.08)*.001*1.005:break
   tolerance*=.5
 return poly
