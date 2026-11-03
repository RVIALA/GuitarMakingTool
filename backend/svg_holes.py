"""Read inert SVG geometry as separate, closed aperture contours.

No scripts, links, stylesheets, images or external resources are evaluated.
Curves are flattened before normalization; overlap and islands are rejected.
"""
import math,re,xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import Polygon

NUMBER=r'[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?'
TOKEN=re.compile(r'[A-Za-z]|'+NUMBER)
ERROR='SVG : contours fermés requis / closed contours required'

def numbers(text):
 text=text or ''
 if re.sub(NUMBER,'',text).strip(' ,\t\n\r'):raise ValueError('SVG : nombre invalide / invalid number')
 out=[float(v) for v in re.findall(NUMBER,text)]
 if not all(math.isfinite(x) and abs(x)<=1e7 for x in out):raise ValueError('SVG : coordonnées hors limites / coordinates out of range')
 return out

def length(text,default=0):
 if text is None:return default
 m=re.fullmatch(r'\s*('+NUMBER+r')\s*(px|mm|cm|in|pt|pc)?\s*',text)
 if not m:raise ValueError('SVG : unités absolues requises, pas de % / absolute units required, no %')
 return float(m[1])*{None:1,'px':1,'mm':96/25.4,'cm':96/2.54,'in':96,'pt':96/72,'pc':16}[m[2]]

def transform(text):
 out=np.eye(3);pos=0
 for m in re.finditer(r'([A-Za-z]+)\s*\(([^)]*)\)',text or ''):
  if (text[pos:m.start()]).strip(' ,\n\t'):raise ValueError('SVG transform')
  name=m[1];a=numbers(m[2]);t=np.eye(3)
  if name=='matrix' and len(a)==6:t=np.array([[a[0],a[2],a[4]],[a[1],a[3],a[5]],[0,0,1]])
  elif name=='translate' and len(a) in [1,2]:t[:2,2]=[a[0],a[1] if len(a)==2 else 0]
  elif name=='scale' and len(a) in [1,2]:t[0,0]=a[0];t[1,1]=a[-1]
  elif name=='rotate' and len(a) in [1,3]:
   angle=math.radians(a[0]);t[:2,:2]=[[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]]
   if len(a)==3:t[:2,2]=np.array(a[1:])-t[:2,:2]@a[1:]
  elif name in ['skewX','skewY'] and len(a)==1:t[0 if name=='skewX' else 1,1 if name=='skewX' else 0]=math.tan(math.radians(a[0]))
  else:raise ValueError('SVG : transformation non prise en charge / unsupported transform')
  out=out@t;pos=m.end()
 if (text or '')[pos:].strip(' ,\n\t'):raise ValueError('SVG transform')
 if not np.isfinite(out).all():raise ValueError('SVG transform')
 return out

def flatten_curve(points,tol,depth=0):
 a=np.array(points);line=a[-1]-a[0];norm=np.linalg.norm(line)
 error=max(np.linalg.norm(q-a[0]) if norm<1e-15 else abs(line[0]*(q-a[0])[1]-line[1]*(q-a[0])[0])/norm for q in a[1:-1])
 # Control polygon excess also catches collinear reversals.
 excess=sum(np.linalg.norm(q-p) for p,q in zip(a,a[1:]))-norm
 if max(error,excess)<tol:return [a[-1]]
 if depth>=16:raise ValueError('SVG : courbe trop complexe / curve too complex')
 left=[a[0]];right=[a[-1]]
 while len(a)>1:
  a=(a[:-1]+a[1:])/2;left.append(a[0]);right.append(a[-1])
 return flatten_curve(left,tol,depth+1)+flatten_curve(right[::-1],tol,depth+1)

def arc(start,end,rx,ry,rotation,large,sweep,tol):
 if large not in [0,1] or sweep not in [0,1]:raise ValueError('SVG arc flags')
 rx,ry=abs(rx),abs(ry)
 if np.linalg.norm(end-start)<1e-12:return []
 if not rx or not ry:return [end]
 phi=math.radians(rotation%360);R=np.array([[math.cos(phi),-math.sin(phi)],[math.sin(phi),math.cos(phi)]])
 x,y=R.T@((start-end)/2);scale=x*x/(rx*rx)+y*y/(ry*ry)
 if scale>1:rx*=math.sqrt(scale);ry*=math.sqrt(scale)
 den=rx*rx*y*y+ry*ry*x*x
 factor=(-1 if large==sweep else 1)*math.sqrt(max(0,(rx*rx*ry*ry-den)/max(den,1e-300)))
 center=np.array([factor*rx*y/ry,-factor*ry*x/rx]);u=(np.array([x,y])-center)/[rx,ry];v=(-np.array([x,y])-center)/[rx,ry]
 first=math.atan2(u[1],u[0]);delta=math.atan2(u[0]*v[1]-u[1]*v[0],np.dot(u,v))
 if not sweep and delta>0:delta-=2*math.pi
 if sweep and delta<0:delta+=2*math.pi
 step=2*math.acos(max(-1,min(1,1-tol/max(rx,ry))))
 n=max(2,math.ceil(abs(delta)/max(1e-6,step)))
 if n>4096:raise ValueError('SVG : arc trop complexe / arc too complex')
 center=R@center+(start+end)/2
 points=[center+R@np.array([rx*math.cos(t),ry*math.sin(t)]) for t in np.linspace(first,first+delta,n+1)[1:]];points[-1]=end.copy()
 return points

def path_rings(data):
 if len(data)>200000:raise ValueError('SVG path too large')
 if TOKEN.sub('',data).strip(' ,\n\r\t'):raise ValueError('SVG path syntax')
 tokens=TOKEN.findall(data)
 if len(tokens)>12000:raise ValueError('SVG path too complex')
 numeric=[float(x) for x in tokens if not x.isalpha()]
 if not all(math.isfinite(x) and abs(x)<1e7 for x in numeric):raise ValueError('SVG coordinates')
 tol=max(1e-7,(max(numeric,default=1)-min(numeric,default=0))*1e-5)
 i=0;cmd=None;current=np.zeros(2);start=None;points=[];rings=[];prev='';control=None
 def finish():
  if not points:return
  closure_tol=max(1e-9,float(np.max(np.ptp(np.array(points),axis=0)))*1e-7)
  if len(points)<4 or np.linalg.norm(points[-1]-points[0])>closure_tol:raise ValueError(ERROR)
  rings.append(np.array(points));points.clear()
 while i<len(tokens):
  if tokens[i].isalpha():
   cmd=tokens[i];i+=1
   if cmd.upper()=='Z':
    if start is None:raise ValueError(ERROR)
    points.append(start.copy());current=start.copy();finish();start=None;prev='Z';control=None;cmd=None;continue
  if cmd is None or cmd.upper() not in 'MLHVCSQTA':raise ValueError('SVG : commande de tracé invalide / invalid path command')
  op=cmd.upper();count={'M':2,'L':2,'H':1,'V':1,'C':6,'S':4,'Q':4,'T':2,'A':7}[op]
  if i+count>len(tokens) or any(t.isalpha() for t in tokens[i:i+count]):raise ValueError('SVG path syntax')
  a=np.array([float(x) for x in tokens[i:i+count]]);i+=count;origin=current.copy() if cmd.islower() else np.zeros(2);old=current.copy()
  if op=='M':
   finish();current=a+origin;start=current.copy();points=[current.copy()];cmd='l' if cmd.islower() else 'L'
  elif start is None:raise ValueError(ERROR)
  elif op=='L':current=a+origin;points.append(current.copy())
  elif op in ['H','V']:
   k=0 if op=='H' else 1;current[k]=a[0]+origin[k];points.append(current.copy())
  elif op in ['C','S','Q','T']:
   if op=='C':c1=a[:2]+origin;c2=a[2:4]+origin;current=a[4:]+origin;curve=[old,c1,c2,current];control=c2
   elif op=='S':c1=2*old-control if prev in ['C','S'] else old;c2=a[:2]+origin;current=a[2:]+origin;curve=[old,c1,c2,current];control=c2
   elif op=='Q':c1=a[:2]+origin;current=a[2:]+origin;curve=[old,c1,current];control=c1
   else:c1=2*old-control if prev in ['Q','T'] else old;current=a+origin;curve=[old,c1,current];control=c1
   points.extend(flatten_curve(curve,max(1e-9,float(np.max(np.ptp(np.array(curve),axis=0)))*1e-5)))
  else:
   current=a[5:]+origin;points.extend(arc(old,current,*a[:5],max(1e-9,max(abs(a[0]),abs(a[1]),float(np.linalg.norm(current-old)))*1e-5)))
  if op not in ['C','S','Q','T']:control=None
  prev=op
  if len(points)>16000 or len(rings)>8:raise ValueError('SVG : géométrie trop complexe / geometry too complex')
 finish();return rings

def shape_rings(el):
 tag=el.tag.split('}')[-1];a=el.attrib
 if tag=='path':return path_rings(a.get('d',''))
 if tag in ['polygon','polyline']:
  v=numbers(a.get('points',''))
  if len(v)<6 or len(v)%2:raise ValueError(ERROR)
  pts=np.array(v).reshape(-1,2)
  if tag=='polyline' and np.linalg.norm(pts[0]-pts[-1])>1e-9:raise ValueError(ERROR)
  return [np.vstack([pts,pts[0]])]
 if tag in ['circle','ellipse']:
  cx,cy=length(a.get('cx')),length(a.get('cy'));rx=length(a.get('r' if tag=='circle' else 'rx'));ry=rx if tag=='circle' else length(a.get('ry'))
  if min(rx,ry)<=0:raise ValueError('SVG : rayon invalide / invalid radius')
  t=np.linspace(0,2*math.pi,257);return [np.c_[cx+rx*np.cos(t),cy+ry*np.sin(t)]]
 if tag=='rect':
  x,y=length(a.get('x')),length(a.get('y'));w,h=length(a.get('width')),length(a.get('height'))
  if min(w,h)<=0:raise ValueError('SVG : rectangle invalide / invalid rectangle')
  rx=min(w/2,length(a.get('rx',a.get('ry','0'))));ry=min(h/2,length(a.get('ry',a.get('rx','0'))))
  if min(rx,ry)<0:raise ValueError('SVG radius')
  if rx and ry:
   pts=[]
   for cx,cy,start in [(x+w-rx,y+ry,-math.pi/2),(x+w-rx,y+h-ry,0),(x+rx,y+h-ry,math.pi/2),(x+rx,y+ry,math.pi)]:
    pts.extend([[cx+rx*math.cos(t),cy+ry*math.sin(t)] for t in np.linspace(start,start+math.pi/2,33)])
   return [np.array(pts+[pts[0]])]
  return [np.array([[x,y],[x+w,y],[x+w,y+h],[x,y+h],[x,y]])]
 return []

def parse_svg(text):
 if not isinstance(text,str) or len(text.encode('utf8'))>1000000:raise ValueError('SVG < 1 Mo / MB')
 if re.search(r'<!DOCTYPE|<!ENTITY',text,re.I):raise ValueError('SVG : DTD / entities non pris en charge / unsupported')
 try:root=ET.fromstring(text)
 except ET.ParseError as e:raise ValueError('SVG invalide / invalid SVG') from e
 if root.tag.split('}')[-1]!='svg':raise ValueError('SVG root required')
 rings=[];warnings=[];visited=0
 ignored={'defs','metadata','title','desc','script','style','clipPath','mask','symbol','pattern'}
 def visit(el,parent,depth=0):
  nonlocal visited
  visited+=1
  if visited>2000 or depth>32:raise ValueError('SVG : document trop complexe / document too complex')
  tag=el.tag.split('}')[-1];style=re.sub(r'\s+','',el.attrib.get('style','')).lower()
  if tag in ignored or el.get('display')=='none' or el.get('visibility') in ['hidden','collapse'] or 'display:none' in style or 'visibility:hidden' in style:return
  if tag=='svg' and el is not root:raise ValueError('SVG : aplatir les SVG imbriqués / flatten nested SVGs')
  if tag in ['use','image','text','foreignObject']:raise ValueError('SVG : convertir objets et textes en tracés / convert objects and text to paths')
  if 'transform:' in style or any(el.get(k) for k in ['clip-path','mask','filter']):raise ValueError('SVG : aplatir transformations CSS et découpes / flatten CSS transforms and clipping')
  matrix=parent@transform(el.get('transform',''))
  shapes=shape_rings(el)
  for ring in shapes:
   xy=(matrix@np.c_[ring,np.ones(len(ring))].T).T[:,:2]
   rings.append(xy)
   if len(rings)>8:raise ValueError('SVG : 8 ouvertures maximum / at most 8 openings')
  for child in el:visit(child,matrix,depth+1)
 visit(root,np.eye(3))
 if not rings:raise ValueError('SVG : aucun contour fermé / no closed contour')
 points=np.vstack(rings)
 if not np.isfinite(points).all():raise ValueError('SVG coordinates')
 xmin,ymin=points.min(axis=0);xmax,ymax=points.max(axis=0);w,h=xmax-xmin,ymax-ymin
 if min(w,h)<1e-9:raise ValueError('SVG : dimensions nulles / zero dimensions')
 normalized=[];polygons=[]
 for ring in rings:
  xy=np.c_[(ring[:,0]-(xmin+xmax)/2)/w,((ymin+ymax)/2-ring[:,1])/h]
  poly=Polygon(xy)
  if not poly.is_valid or poly.area<1e-7:raise ValueError('SVG : contour croisé ou dégénéré / self-intersecting or degenerate contour')
  original=poly;tol=.00008;poly=original.simplify(tol,preserve_topology=True)
  while len(poly.exterior.coords)>385 and tol<.0003:
   tol=min(.0003,tol*1.5);poly=original.simplify(tol,preserve_topology=True)
  if len(poly.exterior.coords)>385:raise ValueError('SVG : simplifier le contour (384 sommets maximum) / simplify outline (384 vertices maximum)')
  if any(poly.intersects(q) for q in polygons):raise ValueError('SVG : contours superposés ou imbriqués / overlapping or nested contours')
  polygons.append(poly);normalized.append(np.array(poly.exterior.coords)[:-1].tolist())
 if sum(map(len,normalized))>2048:raise ValueError('SVG : 2048 sommets maximum / vertices maximum')
 return dict(contours=normalized,aspect=w/h,count=len(normalized))

def validate_contours(contours):
 if not isinstance(contours,list) or not 1<=len(contours)<=8:raise ValueError('SVG : 1–8 contours')
 polygons=[];total=0
 for ring in contours:
  try:xy=np.asarray(ring,dtype=float)
  except (TypeError,ValueError) as e:raise ValueError('SVG : coordonnées invalides / invalid coordinates') from e
  if xy.ndim!=2 or xy.shape[1]!=2 or not 3<=len(xy)<=384 or not np.isfinite(xy).all() or np.max(np.abs(xy))>.501:raise ValueError('SVG : contour normalisé invalide / invalid normalized contour')
  if any(isinstance(v,bool) for point in ring for v in point):raise ValueError('SVG coordinates')
  poly=Polygon(xy)
  if not poly.is_valid or poly.area<1e-7:raise ValueError('SVG : contour croisé ou dégénéré / invalid contour')
  if any(poly.intersects(q) for q in polygons):raise ValueError('SVG : contours superposés ou imbriqués / overlapping or nested contours')
  polygons.append(poly);total+=len(xy)
 if total>2048:raise ValueError('SVG : 2048 sommets maximum / vertices maximum')
 return contours
