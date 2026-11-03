"""Contour dimensional checks and optional conformal mesh checks."""
import sys,argparse,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from shapely.geometry import LineString
from backend.catalog import default_project,validate
from backend.geometry import outline,holes,mesh
from backend.contours import source_key,metadata

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--mesh',action='store_true');parser.add_argument('--output',default='data/contour-verification');args=parser.parse_args();root=Path(args.output);root.mkdir(parents=True,exist_ok=True);report=[]
 for key in ['om','dread','classical','selmer_oval','selmer_d','archtop']:
  p=default_project(key);p['solver'].update(size=55,modes=8,airModes=4)
  p['body']['cutaway']='none';base=outline(p,preview=True);W=p['body']['width']*.001;L=p['body']['length']*.001
  assert abs((base.bounds[2]-base.bounds[0])-W)<1e-7
  assert abs((base.bounds[3]-base.bounds[1])-L)<1e-7
  assert base.interiors.__len__()==0
  for kind in ['none','selmer','venetian','florentine']:
   p['body']['cutaway']=kind;p['body']['cutawayDepth']={'none':90,'selmer':60,'venetian':90,'florentine':78}[kind];p['body']['cutawaySide']='right';p=validate(p);poly=outline(p);display=outline(p,preview=True);inner=poly.buffer(-p['body']['ribs']*.001)
   assert display.is_valid and poly.is_valid and inner.geom_type=='Polygon'
   assert display.hausdorff_distance(poly)<=p['body']['rimTolerance']*.001*1.005
   assert all(inner.contains(h) for h in holes(p))
   if kind!='none':assert .65*base.area<poly.area<base.area
   r=dict(preset=key,cutaway=kind,source=metadata(p)['fr'],area_cm2=poly.area*10000,removed_cm2=(base.area-poly.area)*10000,cadVertices=len(poly.exterior.coords),displayVertices=len(display.exterior.coords),maximumContourError_mm=display.hausdorff_distance(poly)*1000)
   if args.mesh:
    start=time.time();raw=mesh(p,root/(key+'_'+kind));r.update(nodes=len(raw['points']),tetrahedra=len(raw['elements']),seconds=time.time()-start);assert raw['air'];print(key,kind,r['nodes'],r['tetrahedra'],flush=True)
   # Reflection must preserve all areas and change only the selected shoulder.
   p['body']['cutawaySide']='left';left=outline(p,preview=True);assert abs(left.area-display.area)<1e-8
   p['body']['cutawaySide']='right'
   if kind!='none':
    p['body']['cutawayDepth']=60;small=outline(p,preview=True);p['body']['cutawayDepth']=115;large=outline(p,preview=True);assert large.area<small.area
   report.append(r);(root/'report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
 # Legacy sessions acquire the new controls without changing user dimensions.
 p=default_project('om')
 for k in ['cutaway','cutawaySide','cutawayDepth','contourVersion']:p['body'].pop(k)
 assert validate(p)['body']['cutaway']=='none'
 p=default_project('selmer_d');p['body'].update(contourVersion=3,cutaway='venetian',cutawayDepth=95);q=validate(p);assert q['body']['cutaway']=='selmer' and q['body']['cutawayDepth']==60
 p['body']['outline']=[[100*np.cos(t),200+200*np.sin(t)] for t in np.linspace(0,2*np.pi,32,endpoint=False)];assert validate(p)['body']['cutaway']=='venetian'
 print('PASS: dimensions, closure, simplification bound, cutaway area/depth/side, openings and legacy session migration.',flush=True)
if __name__=='__main__':main()
