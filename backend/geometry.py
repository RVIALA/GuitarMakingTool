"""Conformal OpenCASCADE multi-volume mesh, quadratic wood / linear air."""
import math,os
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon, LineString, box
from shapely.affinity import scale, translate
from shapely.geometry.polygon import orient
from .catalog import validate

from .contours import outline

def holes(p):
 h=p['hole'];cx,cy=h['x']*.001,h['y']*.001;rx,ry=h['width']*.0005,h['height']*.0005
 if h['kind']=='svg':
  return [Polygon(np.asarray(ring)*[2*rx,2*ry]+[cx,cy]) for ring in h['contours']]
 if h['kind']=='f':
  shapes=[]
  for side in [-1,1]:
   pts=[(cx+side*(.21*p['body']['width']*.001+rx*.7*math.sin(2*math.pi*t)),cy+ry*(2*t-1)) for t in np.linspace(0,1,25)]
   shapes.append(LineString(pts).buffer(rx*.32,quad_segs=5))
  return shapes
 theta=np.linspace(0,2*np.pi,40,endpoint=False);pts=np.c_[cx+rx*np.cos(theta),cy+ry*np.sin(theta)]
 poly=Polygon(pts)
 if h['kind']=='D':poly=poly.intersection(box(cx-rx*1.1,cy-ry*.65,cx+rx*1.1,cy+ry*1.1))
 return [poly]

def checked_holes(p):
 hs=holes(p);inner=outline(p).buffer(-p['body']['ribs']*.001)
 if inner.is_empty or inner.geom_type!='Polygon':raise ValueError('Contour/éclisses incompatibles / invalid inner body')
 for i,h in enumerate(hs):
  if not h.is_valid or h.area<1e-8:raise ValueError('Ouverture dégénérée / degenerate opening')
  if not inner.contains(h) or inner.boundary.distance(h)<.0002:raise ValueError('Ouverture hors caisse ou trop proche des éclisses / opening outside body or too close to ribs')
  if any(h.distance(other)<.0002 for other in hs[:i]):raise ValueError('Ouvertures superposées ou trop proches / overlapping or too-close openings')
 b=p['bridge'];foot=box((b['x']-b['width']/2)*.001,(b['y']-b['depth']/2)*.001,(b['x']+b['width']/2)*.001,(b['y']+b['depth']/2)*.001)
 if any(foot.intersects(h) for h in hs):raise ValueError('Ouverture sous le chevalet / opening intersects bridge')
 return hs

def brace_footprint(p,bar,inner=None,hs=None):
 if inner is None:inner=outline(p).buffer(-p['body']['ribs']*.001,join_style='round')
 fp=LineString(np.array([bar['a'],bar['b']])*.001).buffer(bar['width']*.0005,cap_style='flat').intersection(inner)
 if bar['part']=='top':
  for h in holes(p) if hs is None else hs:fp=fp.difference(h)
 return fp

def brace_preview(p,poly):
 inner=poly.buffer(-p['body']['ribs']*.001,join_style='round');result=[]
 for b in p['braces']:
  if b['part']=='back' and not p['body']['backEnabled']:continue
  a=np.array(b['a'])*.001;e=np.array(b['b'])*.001;fp=brace_footprint(p,b,inner)
  for j in range(3):
   seg=LineString([a+(e-a)*j/3,a+(e-a)*(j+1)/3]).buffer(b['width']*.0005,cap_style='flat').intersection(fp)
   for part in [seg] if seg.geom_type=='Polygon' else getattr(seg,'geoms',[]):
    if part.is_empty or part.geom_type!='Polygon' or part.area<1e-8:continue
    result.append(dict(id=b['id'],side=b['part'],height=b['height']*.001*(1 if j==1 else b.get('profile',1)),outline=list(part.exterior.coords),holes=[list(r.coords) for r in part.interiors]))
 return result

def arch(p,x,y,part='top'):
 b=p['body'];height=b['archTop' if part=='top' else 'archBack']*.001
 if not height:return np.zeros_like(np.asarray(x,dtype=float))
 L=b['length']*.001;W=b['width']*.001
 # Smooth carved surface, zero on the body ends. Geometry is parametric, not a historical copy.
 return height*np.maximum(0,1-(2*np.asarray(x)/W)**2)*np.maximum(0,np.sin(np.pi*np.asarray(y)/L))**1.2

def warp(p,xyz):
 xyz=np.asarray(xyz,float).copy();d=p['body']['depth']*.001;t=np.clip((xyz[:,2]+d)/d,0,1)
 xyz[:,2]+=arch(p,xyz[:,0],xyz[:,1],'top')*t-arch(p,xyz[:,0],xyz[:,1],'back')*(1-t)
 return xyz

def mesh(project,directory,progress=lambda *a:None):
 import gmsh
 p=validate(project);directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
 poly=outline(p);hs=checked_holes(p);inner=poly.buffer(-p['body']['ribs']*.001,join_style='round')
 if inner.is_empty or inner.geom_type!='Polygon':raise ValueError('Contour/éclisses incompatibles')
 for h in hs:
  if not inner.contains(h):raise ValueError('Bouche extérieure au corps / soundhole outside body')
 top=poly
 for h in hs:top=top.difference(h)
 depth=p['body']['depth']*.001;tt=p['body']['top']*.001;tb=p['body']['back']*.001
 g=gmsh;g.initialize([],readConfigFiles=False,run=False,interruptible=False);g.option.setNumber('General.Terminal',1 if os.getenv('GMT_DEBUG') else 0)
 try:
  g.model.add('GMT');occ=g.model.occ;objects=[];descriptors=[]
  def planar(pg,z):
   pg=orient(pg,sign=1.0);rings=[pg.exterior,*pg.interiors];loops=[]
   for ring in rings:
    xy=np.array(ring.coords)[:-1];xy=xy[np.linalg.norm(xy-np.roll(xy,1,axis=0),axis=1)>1e-7];tags=[occ.addPoint(float(x),float(y),z) for x,y in xy];lines=[occ.addLine(tags[i],tags[(i+1)%len(tags)]) for i in range(len(tags))];loops.append(occ.addCurveLoop(lines))
   surface=occ.addPlaneSurface([loops[0]])
   for loop in loops[1:]:
    holeface=occ.addPlaneSurface([loop]);out,_=occ.cut([(2,surface)],[(2,holeface)],removeObject=True,removeTool=True);surface=next(tag for dim,tag in out if dim==2)
   return surface
  def extrude(pg,z,height,desc):
   if pg.is_empty:return
   for part in ([pg] if pg.geom_type=='Polygon' else list(pg.geoms)):
    if part.area<1e-8:continue
    part=part.simplify(1e-7,preserve_topology=True)
    face=planar(part,z);vol=[v for dim,v in occ.extrude([(2,face)],0,0,height) if dim==3]
    for v in vol:objects.append((3,v));descriptors.append(desc)
  extrude(top,0,tt,dict(part='top'))
  if p['body']['backEnabled']:extrude(poly,-depth-tb,tb,dict(part='back'))
  if p['body']['ribsEnabled']:extrude(poly.difference(inner),-depth,depth,dict(part='ribs'))
  for bar in p['braces']:
   if bar['part']=='back' and not p['body']['backEnabled']:continue
   a=np.array(bar['a'])*.001;b=np.array(bar['b'])*.001
   if np.linalg.norm(a-b)<.008:raise ValueError('Barre trop courte / brace too short')
   footprint=brace_footprint(p,bar,inner,hs)
   # Height profile is implemented by three bonded, constant-height segments.
   nseg=3;line=LineString([a,b]);barheight=bar['height']*.001
   for j in range(nseg):
    aa=a+(b-a)*j/nseg;bb=a+(b-a)*(j+1)/nseg;fp=LineString([aa,bb]).buffer(bar['width']*.0005,cap_style='flat').intersection(footprint)
    height=barheight*(1 if j==1 else bar.get('profile',1));z=-height if bar['part']=='top' else -depth
    extrude(fp,z,height,dict(part='braces',side=bar['part'],id=bar['id'],angle=float(math.atan2(*(b-a)[::-1]))))
  bridge=p['bridge'];cx=bridge['x']*.001;cy=bridge['y']*.001;bw=bridge['width']*.001;bd=bridge['depth']*.001;bh=bridge['height']*.001
  foot=box(cx-bw/2,cy-bd/2,cx+bw/2,cy+bd/2)
  if not poly.contains(foot) or any(foot.intersects(h) for h in hs):raise ValueError('Chevalet extérieur ou sur la bouche / invalid bridge footprint')
  if bridge['kind']=='floating':
   for x in [cx-bw*.35,cx+bw*.35]:extrude(box(x-.009,cy-bd/2,x+.009,cy+bd/2),tt,bh*.7,dict(part='bridge'))
   extrude(foot,tt+bh*.65,bh*.35,dict(part='bridge'))
  elif bridge['kind']=='tie':
   extrude(foot,tt,bh*.55,dict(part='bridge'))
   extrude(box(cx-bw*.35,cy-bd*.08,cx+bw*.35,cy+bd*.08),tt+bh*.5,bh*.5,dict(part='bridge'))
   extrude(box(cx-bw*.3,cy-bd*.45,cx+bw*.3,cy-bd*.18),tt+bh*.5,bh*.4,dict(part='bridge'))
  else:extrude(foot,tt,bh,dict(part='bridge'))
  if p['body']['ribsEnabled']:
   block=inner.intersection(box(-.035,p['body']['length']*.001-.026,.035,p['body']['length']*.001+.001));extrude(block,-depth,depth,dict(part='braces',side='block',id='neckblock',angle=math.pi/2))
  solid_count=len(objects);air_enabled=p['solver']['air'] and p['body']['backEnabled'] and p['body']['ribsEnabled']
  if air_enabled:
   extrude(inner,-depth,depth,dict(part='air'))
   for h in hs:extrude(h,0,tt,dict(part='air'))
  progress(.12,'CAD / Boolean fragments')
  fragments,mapping=occ.fragment(objects[:1],objects[1:],removeObject=True,removeTool=True);occ.removeAllDuplicates();occ.synchronize()
  boundary_tags=set(g.model.getBoundary(g.model.getEntities(3),combined=False,oriented=False,recursive=False));orphans=[e for e in g.model.getEntities(2) if e not in boundary_tags]
  if orphans:occ.remove(orphans,recursive=True);occ.synchronize()
  groups={};used=set()
  # Wood owns overlaps; crossing braces form one union with the first brace orientation.
  for desc,frags in zip(descriptors,mapping):
   ids=[t for dim,t in frags if dim==3 and t not in used]
   if ids:
    idx=len(groups);groups[idx]=dict(**desc,volumes=ids);used.update(ids);g.model.addPhysicalGroup(3,ids,idx+1);g.model.setPhysicalName(3,idx+1,desc['part']+'_'+str(idx))
  size=p['solver']['size']*.001
  g.option.setNumber('Mesh.MeshSizeMax',size);g.option.setNumber('Mesh.MeshSizeMin',min(.003,size/8));g.option.setNumber('Mesh.MeshSizeFromCurvature',0);g.option.setNumber('Mesh.MeshSizeExtendFromBoundary',0);g.option.setNumber('Mesh.MeshSizeFromPoints',0)
  g.option.setNumber('Mesh.Algorithm',6);g.option.setNumber('Mesh.Algorithm3D',1);g.option.setNumber('Mesh.Optimize',1);g.option.setNumber('General.NumThreads',2)
  progress(.22,'Maillage volumique / Volume mesh')
  try:g.model.mesh.generate(3)
  except Exception:
   if os.getenv('GMT_DEBUG'):
    import re
    for sid in map(int,re.findall(r'surface (\d+)',g.logger.getLastError())):
     print('BAD SURFACE',sid,occ.getCenterOfMass(2,sid),g.model.getAdjacencies(2,sid)[0],flush=True)
    g.write(str(directory/'failure.msh'));g.write(str(directory/'failure.brep'))
   raise
  g.model.mesh.setOrder(2)
  # Gmsh can duplicate a quadratic edge node to floating-point precision.
  # Merge in the native mesh so both connectivity and exported files agree.
  from scipy.spatial import cKDTree
  _,mesh_coordinates,_=g.model.mesh.getNodes()
  if cKDTree(np.asarray(mesh_coordinates).reshape(-1,3)).query_pairs(1e-10):g.model.mesh.removeDuplicateNodes()
  node_tags,coords,_=g.model.mesh.getNodes();tags=np.asarray(node_tags);order=np.argsort(tags);tags=tags[order];xyz=np.array(coords).reshape(-1,3)[order];xyz=warp(p,xyz)
  elements=[];labels=[]
  for idx,desc in groups.items():
   for vol in desc['volumes']:
    types,etags,enodes=g.model.mesh.getElements(3,vol)
    for typ,conn in zip(types,enodes):
     name,dim,degree,numnodes,local,_=g.model.mesh.getElementProperties(typ)
     if numnodes!=10:raise ValueError('Tetra10 attendu / expected')
     a=np.searchsorted(tags,np.array(conn).reshape(-1,10));elements.append(a);labels.extend([idx]*len(a))
  conn=np.concatenate(elements);labels=np.array(labels)
  # Update high-order geometry before exporting. Every shared tag is transformed once.
  for tag,point in zip(tags,xyz):g.model.mesh.setNode(int(tag),point.tolist(),[])
  g.write(str(directory/'mesh.msh'));g.write(str(directory/'mesh.vtk'))
  _,_,_,_,local,_=g.model.mesh.getElementProperties(11);local=np.array(local).reshape(10,3);bary=np.c_[1-local.sum(1),local];edges=[np.flatnonzero(row>.1).tolist() for row in bary[4:]]
  raw=dict(points=xyz,elements=conn,labels=labels,groups=groups,edges=edges,air=air_enabled,outline=np.array(poly.exterior.coords),holes=[np.array(h.exterior.coords) for h in hs],project=p)
  from scipy.sparse import coo_matrix
  from scipy.sparse.csgraph import connected_components
  from scipy.spatial import cKDTree
  if cKDTree(xyz).query_pairs(1e-10):raise ValueError('Nœuds distincts superposés / duplicate coincident nodes')
  for name in ['wood','air']:
   subset=conn[[((groups[int(k)]['part']=='air')==(name=='air')) for k in labels]]
   if not len(subset):continue
   unique=np.unique(subset);local=np.searchsorted(unique,subset);a=np.repeat(local[:,0],9);bb=local[:,1:].ravel();graph=coo_matrix((np.ones(len(a)),(a,bb)),shape=(len(unique),len(unique)))
   count=connected_components(graph,directed=False,return_labels=False)
   if count!=1:raise ValueError(f'{name}: {count} pièces déconnectées / disconnected components')
  if len(xyz)>90000:raise ValueError('Maillage trop grand pour cette version : augmenter la taille / increase mesh size')
  np.savez_compressed(directory/'mesh.npz',points=xyz,elements=conn,labels=labels)
  progress(.32,'Maillage conforme / Conformal mesh');return raw
 finally:g.finalize()
