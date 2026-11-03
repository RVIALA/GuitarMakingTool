"""SVG geometry, sessions, preview API and optional conformal mesh checks."""
import sys,copy,json,argparse,threading,http.server,urllib.request,urllib.error
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from shapely.geometry import Polygon
from backend.svg_holes import parse_svg,validate_contours
from backend.catalog import default_project,validate
from backend.geometry import holes,checked_holes,outline,mesh,brace_footprint
from backend.response import geometry_key

def svg(body):return '<svg xmlns="http://www.w3.org/2000/svg">'+body+'</svg>'
def expect_error(fn):
 try:fn()
 except ValueError:return
 raise AssertionError('Invalid geometry accepted')

circle=parse_svg(svg('<circle cx="30" cy="50" r="20"/>'))
assert circle['count']==1 and abs(Polygon(circle['contours'][0]).area-np.pi/4)<.0002
rect=parse_svg(svg('<path d="M0 0h20v10h-20z m40 0 h20 v10 h-20z"/>'))
assert rect['count']==2 and abs(rect['aspect']-6)<1e-12
assert abs(sum(Polygon(r).area for r in rect['contours'])-2/3)<1e-12
transformed=parse_svg(svg('<g transform="translate(80 30) rotate(90) scale(2 1)"><rect width="20" height="10"/></g>'))
assert abs(transformed['aspect']-.25)<1e-10
for d in ['M0 0C0 -20 20 -20 20 0S40 20 40 0L40 30H0Z',
          'M0 0Q10 -20 20 0T40 0L40 30H0Z',
          'M0 10A10 10 0 1 0 20 10A10 10 0 1 0 0 10Z',
          'M0 0c0 -20 20 -20 20 0q-10 20 -20 0z']:
 shape=parse_svg(svg('<path d="'+d+'"/>'));validate_contours(shape['contours'])
for bad in ['<path d="M0 0L20 0L20 10"/>','<path d="M0 0L20 20L0 20L20 0Z"/>',
            '<circle r="20"/><circle r="10"/>','<rect width="20" height="20"/><rect x="10" width="20" height="20"/>',
            '<use href="#shape"/>','<rect width="50%" height="10"/>','<path d="M0 0LNaN 20Z"/>']:
 expect_error(lambda:parse_svg(svg(bad)))
expect_error(lambda:parse_svg('<!DOCTYPE svg [<!ENTITY x "bad">]><svg/>'))
expect_error(lambda:parse_svg('x'*1000001))
for preset in ['om','dread','classical','selmer_oval','selmer_d','archtop']:
 checked_holes(validate(default_project(preset)))
p=default_project();initial=geometry_key(p)
p['hole']['width']=p['hole']['height']=80
small=sum(h.area for h in holes(p));p['hole']['width']=p['hole']['height']=120
assert abs(sum(h.area for h in holes(p))/small-2.25)<1e-12
assert geometry_key(p)!=initial
legacy=default_project();legacy['hole']['height']=80
assert validate(legacy)['hole']['kind']=='oval'
p=default_project();shape=parse_svg(svg('<ellipse cx="-50" cy="0" rx="10" ry="35"/><ellipse cx="50" cy="0" rx="10" ry="35"/>'))
p['hole'].update(kind='svg',contours=shape['contours'],svgName='two.svg',width=120,height=70,x=0,y=320)
p=validate(json.loads(json.dumps(p)));hs=checked_holes(p);area=sum(h.area for h in hs)
assert abs(area/(2*np.pi*.01*.035)-1)<.001
assert p['hole']['svgName']=='two.svg'
for bar in p['braces']:
 if bar['part']=='top':assert all(brace_footprint(p,bar).intersection(h).area<1e-14 for h in hs)
for mutate in [lambda q:q['hole'].update(x=240),lambda q:q['hole'].update(y=q['bridge']['y']),lambda q:q['hole'].update(contours=[[[0,0],[.6,0],[0,.5]]])]:
 q=copy.deepcopy(p);mutate(q);expect_error(lambda:checked_holes(validate(q)))
import server
http=http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);threading.Thread(target=http.serve_forever,daemon=True).start()
try:
 def post(path,payload):
  req=urllib.request.Request(f'http://127.0.0.1:{http.server_port}'+path,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=15) as f:return json.load(f)
 result=post('/api/import-holes',dict(project=default_project(),svg=svg('<circle r="10"/>')));assert result['count']==1
 result=post('/api/preview',dict(project=p));assert len(result['holes'])==2 and result['project']['hole']['contours']==p['hole']['contours']
 q=copy.deepcopy(p);q['hole']['x']=240
 try:post('/api/preview',dict(project=q));raise AssertionError('invalid preview accepted')
 except urllib.error.HTTPError as e:assert e.code==400
finally:http.shutdown();http.server_close()
print('PASS: SVG curves/arcs/transforms, relative subpaths, rejected open/invalid/nested contours, diameter area scaling, legacy sessions, custom sessions, bounds, bridge clearance, brace cuts and HTTP preview.',flush=True)
if '--mesh' in sys.argv:
 from backend.fem import boundary
 p['solver'].update(size=60,modes=8,airModes=2);p['braces']=[]
 raw=mesh(p,Path(__file__).resolve().parents[1]/'data/svg-test')
 exterior,interfaces,aperture=boundary(raw)
 aperture_area=sum(a['area'] for a in aperture)
 assert raw['air'] and len(aperture)>0
 assert abs(aperture_area/area-1)<.005,(aperture_area,area)
 print(json.dumps(dict(mesh='PASS',nodes=len(raw['points']),tetrahedra=len(raw['elements']),holes=len(raw['holes']),aperture_area_mm2=aperture_area*1e6,expected_area_mm2=area*1e6)),flush=True)
