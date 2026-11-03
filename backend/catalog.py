"""GMT catalogue. SI in the solver; mm/GPa in editable projects."""
import copy, math
import numpy as np

MATERIALS = {
 'spruce': dict(fr='Épicéa', en='Spruce', rho=430, EL=11.0, ER=.85, ET=.45, GLR=.75, GLT=.65, GRT=.045, nuLR=.35, nuLT=.40, nuRT=.45, loss=1.8),
 'cedar': dict(fr='Western red cedar', en='Western red cedar', rho=370, EL=8.5, ER=.65, ET=.35, GLR=.60, GLT=.52, GRT=.035, nuLR=.35, nuLT=.40, nuRT=.45, loss=2.2),
 'rosewood': dict(fr='Palissandre', en='Rosewood', rho=800, EL=15, ER=1.8, ET=1.0, GLR=1.5, GLT=.9, GRT=.12, nuLR=.35, nuLT=.40, nuRT=.45, loss=2.0),
 'mahogany': dict(fr='Acajou', en='Mahogany', rho=560, EL=10, ER=1.1, ET=.6, GLR=.85, GLT=.65, GRT=.09, nuLR=.35, nuLT=.40, nuRT=.45, loss=2.4),
 'maple': dict(fr='Érable', en='Maple', rho=650, EL=12, ER=1.2, ET=.65, GLR=1.2, GLT=.9, GRT=.10, nuLR=.35, nuLT=.40, nuRT=.45, loss=1.8),
 'ebony': dict(fr='Ébène', en='Ebony', rho=1000, EL=16, ER=1.7, ET=1.05, GLR=1.2, GLT=.9, GRT=.15, nuLR=.35, nuLT=.40, nuRT=.45, loss=2.0),
}
PRESETS = {
 'om': dict(family='steel',fr='Acier · OM',en='Steel · OM',length=491.96,width=380.64,depth=100,scale=645.2,top=2.8,back=2.8,ribs=2.0,hole='round',holeX=0,holeY=.66,holeW=98,holeH=98,bracing='X',bridge='glued'),
 'dread': dict(family='steel',fr='Acier · Dreadnought',en='Steel · Dreadnought',length=513.8,width=397,depth=120,scale=645.2,top=3,back=2.8,ribs=2.1,hole='round',holeX=0,holeY=.66,holeW=100,holeH=100,bracing='X',bridge='glued'),
 'classical': dict(family='nylon',fr='Classique · éventail',en='Classical · fan',length=483.877,width=354.0,depth=96,scale=650,top=2.5,back=2.5,ribs=2,hole='round',holeX=0,holeY=.66,holeW=86,holeH=86,bracing='fan',bridge='tie'),
 'selmer_oval': dict(family='gypsy',fr='Manouche · petite bouche',en='Gypsy jazz · oval hole',length=500,width=405,depth=100,scale=670,top=2.8,back=2.8,ribs=2,hole='oval',holeX=0,holeY=.66,holeW=58,holeH=88,bracing='ladder',bridge='floating'),
 'selmer_d': dict(family='gypsy',fr='Manouche · grande bouche',en='Gypsy jazz · D hole',length=500,width=405,depth=105,scale=640,top=2.8,back=2.8,ribs=2,hole='D',holeX=0,holeY=.66,holeW=110,holeH=92,bracing='ladder',bridge='floating'),
 'archtop': dict(family='steel',fr='Archtop · jazz',en='Archtop · jazz',length=525.78,width=431.8,depth=83,scale=648,top=4,back=4,ribs=2.2,hole='f',holeX=0,holeY=.48,holeW=18,holeH=130,bracing='parallel',bridge='floating'),
}

def brace(x1,y1,x2,y2,width=7,height=13,part='top',name=''):
 return dict(id=name or f'b{abs(hash((x1,y1,x2,y2,part)))%100000}',part=part,a=[x1,y1],b=[x2,y2],width=width,height=height,profile=.8,material='inherit')

def default_braces(p):
 L,W=p['length'],p['width'];bars=[]
 def b(x1,y1,x2,y2,w=7,h=13,part='top'):
  bars.append(brace(x1*W,y1*L,x2*W,y2*L,w,h,part,'bar'+str(len(bars)+1)))
 if p['bracing']=='X':
  b(-.36,.13,.25,.73,8,15);b(.36,.13,-.25,.73,8,15);b(-.25,.2,.33,.32,6,10);b(-.31,.12,.24,.22,6,9);b(-.27,.79,.27,.79,9,15)
 elif p['bracing']=='fan':
  for i in range(7):b((i-3)*.085,.10,(i-3)*.045,.54,5,7)
  b(-.32,.56,.32,.56,10,13);b(-.28,.78,.28,.78,9,12)
 elif p['bracing']=='parallel':
  b(-.16,.12,-.11,.83,11,18);b(.16,.12,.11,.83,11,18)
 else:
  for y in [.18,.37,.55,.79]:b(-.36,y,.36,y,9,14)
 for y in [.2,.43,.73]:b(-.38,y,.38,y,10,15,'back')
 return bars

def default_project(key='om'):
 p=copy.deepcopy(PRESETS.get(key,PRESETS['om']));family=p['family']
 tensions=([70,70,65,62,63,70] if family=='steel' else [60,55,50,48,58,65] if family=='gypsy' else [68,65,62,52,53,70])
 gauges=([.053,.042,.032,.024,.016,.012] if family=='steel' else [.045,.036,.028,.022,.014,.010] if family=='gypsy' else [.043,.035,.029,.040,.032,.028])
 mat={k:dict(material=v,grain=0,ring=0,**copy.deepcopy(MATERIALS[v])) for k,v in [('top','spruce'),('back','rosewood'),('ribs','rosewood'),('braces','spruce'),('bridge','ebony')]}
 out=dict(schema='gmt',version=1,name='GMT '+p['en'],preset=key,family=family,
  body=dict(length=p['length'],width=p['width'],depth=p['depth'],top=p['top'],back=p['back'],ribs=p['ribs'],backEnabled=True,ribsEnabled=True,archTop=18 if key=='archtop' else 0,archBack=14 if key=='archtop' else 0,outline=None,cutaway='selmer' if family=='gypsy' else 'venetian' if key=='archtop' else 'none',cutawayDepth=60 if family=='gypsy' else 90,cutawaySide='right',contourVersion=4,rimTolerance=.08),
  hole=dict(kind=p['hole'],x=0,y=p['holeY']*p['length'],width=p['holeW'],height=p['holeH'],endFactor=1.7,resistance=1.0),
  bridge=dict(kind=p['bridge'],x=0,y=.405*p['length'],width=180 if p['bridge']=='floating' else 150,depth=15 if p['bridge']=='floating' else 28,height=16 if p['bridge']=='floating' else 8,spacing=55),
  braces=default_braces(p),materials=mat,
  strings=dict(damping=1,scale=p['scale'],a4=440,items=[dict(midi=m,fret=0,tension=t,gauge=g,EI=2e-5 if family=='nylon' else 1e-4,loss=.45 if family=='nylon' else .25,hfLoss=.00008) for m,t,g in zip([40,45,50,55,59,64],tensions,gauges)]),
  excitation=dict(palm=0,kind='pick',position=110,force=1,hardness=.65,width=1.2,angle=0,strum=25,duration=3,sympathetic=True),
  solver=dict(size=25,modes=96,airModes=10,support='neck',air=True,fmin=5,fmax=4000),
  synthesis=dict(fmin=20,fmax=10000,extension='residual',residualDamping=10),
  analysis=dict(fft=4096,window='hann',palette='magma',range=80,fmin=0,fmax=10000,tmin=0,tmax=3,scale='linear',reference='peak',ceiling=0,gesture='pan',volume=.6),
  monitor=dict(source='pressure',level=.6,gain=0,mode='peak',point=[0,p['length']/2000,1],radiation='panels'),modalEdits={})
 for a in out['strings']['items']:
  L=p['scale']*.001;f=440*2**((a['midi']-69)/12);a['mu']=(a['tension']+math.pi**2*a['EI']/L**2)/(4*L*L*f*f)*1000;a.pop('tension')
 return out

def compliance(m):
 E=np.array([m['EL'],m['ER'],m['ET']])*1e9
 S=np.diag(np.r_[1/E,1/(np.array([m['GLR'],m['GLT'],m['GRT']])*1e9)])
 for i,j,k in [(0,1,'nuLR'),(0,2,'nuLT'),(1,2,'nuRT')]:S[i,j]=S[j,i]=-m[k]/E[i]
 return S

def _validate_parameters(p):
 p=copy.deepcopy(p)
 b=p['body'];old=b.get('contourVersion',0)<4
 if old and p.get('family')=='gypsy' and b.get('cutaway','venetian')=='venetian' and b.get('outline') is None:
  b.update(cutaway='selmer',cutawayDepth=60 if b.get('cutawayDepth',95)==95 else b['cutawayDepth'])
 b.setdefault('cutaway','selmer' if p.get('family')=='gypsy' else 'venetian' if p.get('preset')=='archtop' else 'none');b.setdefault('cutawayDepth',60 if p.get('family')=='gypsy' else 90);b.setdefault('cutawaySide','right');b['contourVersion']=4;b.setdefault('rimTolerance',.08)
 p['solver'].setdefault('fmin',5);p['solver'].setdefault('fmax',4000)
 p['synthesis']={**dict(fmin=20,fmax=10000,extension='residual',residualDamping=10),**p.get('synthesis',{})}
 p['analysis']={**dict(fft=4096,window='hann',palette='magma',range=80,fmin=0,fmax=10000,tmin=0,tmax=3,scale='linear',reference='peak',ceiling=0,gesture='pan',volume=.6),**p.get('analysis',{})}
 if p.get('schema')!='gmt' or p.get('version')!=1:raise ValueError('Session GMT v1 attendue / expected')
 def limit(x,a,b,key):
  if isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x) or not a<=x<=b:raise ValueError(f'{key}: {a}–{b}')
 for k,a,b in [('length',350,650),('width',250,500),('depth',50,180),('top',1,8),('back',1,8),('ribs',1,6),('archTop',0,35),('archBack',0,30)]:limit(p['body'][k],a,b,k)
 if p['body']['cutaway'] not in ['none','selmer','venetian','florentine'] or p['body']['cutawaySide'] not in ['left','right']:raise ValueError('Pan coupé / cutaway')
 limit(p['body']['cutawayDepth'],20,120,'Cutaway depth mm')
 limit(p['solver']['size'],15,70,'Mesh mm');limit(p['solver']['modes'],8,180,'Modes');limit(p['solver']['airModes'],2,30,'Air modes')
 limit(p['body']['rimTolerance'],.05,.3,'Rim outline tolerance mm')
 for key in ['fmin','fmax']:limit(p['solver'][key],0 if key=='fmin' else 20,20000,'Modal '+key)
 if p['solver']['fmin']>=p['solver']['fmax']:raise ValueError('Bande modale : fmin < fmax / modal band')
 for key in ['fmin','fmax']:limit(p['synthesis'][key],0 if key=='fmin' else 100,20000,'Synthesis '+key)
 if p['synthesis']['fmin']>=p['synthesis']['fmax']:raise ValueError('Bande de synthèse : fmin < fmax / synthesis band')
 if p['synthesis']['extension'] not in ['residual','none']:raise ValueError('Projection / projection')
 limit(p['synthesis']['residualDamping'],1,30,'Residual damping %')
 if p['solver']['support'] not in ['neck','free','rim']:raise ValueError('Support')
 if p['hole']['kind'] not in ['round','oval','D','f','svg']:raise ValueError('Soundhole')
 for k in ['width','height']:limit(p['hole'][k],10,320 if p['hole']['kind']=='svg' else 160,k)
 if p['hole'].get('contours') is not None:
  from .svg_holes import validate_contours
  validate_contours(p['hole']['contours'])
 if p['hole']['kind']=='svg' and not p['hole'].get('contours'):raise ValueError('Importer les contours SVG / import SVG contours first')
 p['hole']['svgName']=str(p['hole'].get('svgName',''))[:120]
 if p['hole']['kind']=='round' and p['hole']['width']!=p['hole']['height']:p['hole']['kind']='oval'
 limit(p['hole']['endFactor'],.5,3,'End correction');limit(p['hole']['resistance'],.05,10,'Port loss')
 for k,a,b in [('width',50,220),('depth',8,50),('height',3,30),('spacing',35,70)]:limit(p['bridge'][k],a,b,k)
 if len(p['braces'])>30:raise ValueError('30 barres maximum / 30 braces maximum')
 for b in p['braces']:
  if b['part'] not in ['top','back']:raise ValueError('Brace part')
  limit(b['width'],3,25,'Brace width');limit(b['height'],2,35,'Brace height');limit(b.get('profile',1),.2,1,'Brace profile')
  for v in b['a']+b['b']:limit(v,-650,650,'Brace position')
 for m in p['materials'].values():
  limit(m['rho'],150,1500,'Density');limit(m['loss'],.1,15,'Loss %')
  for k in ['EL','ER','ET','GLR','GLT','GRT']:limit(m[k],.005,40,k)
  for k in ['nuLR','nuLT','nuRT']:limit(m[k],0,.95,k)
  if np.linalg.eigvalsh(compliance(m)).min()<=0:raise ValueError('Matrice orthotrope non positive / unstable orthotropic compliance')
  limit(m.get('grain',0),-90,90,'Grain');limit(m.get('ring',0),-90,90,'Ring')
 p['strings'].setdefault('damping',1);p['excitation'].setdefault('palm',0)
 limit(p['strings']['damping'],.1,10,'String damping multiplier');limit(p['excitation']['palm'],0,1,'Palm mute')
 limit(p['strings']['scale'],550,750,'Scale');limit(p['excitation']['duration'],.5,8,'Duration');limit(p['excitation']['force'],.01,5,'Pluck force');limit(p['excitation']['position'],5,450,'Pluck position')
 if len(p['strings']['items'])!=6:raise ValueError('6 strings')
 limit(p['strings']['a4'],400,480,'A4')
 for k,a,b in [('angle',0,90),('hardness',0,1),('width',.1,8),('strum',0,200)]:limit(p['excitation'][k],a,b,k)
 if p['excitation']['kind'] not in ['pick','finger']:raise ValueError('Excitation')
 if p['bridge']['kind'] not in ['glued','tie','floating']:raise ValueError('Bridge')
 for obj in ['hole','bridge']:
  limit(p[obj]['x'],-250,250,obj+' x');limit(p[obj]['y'],0,650,obj+' y')
 for v in p['monitor']['point']:limit(v,-10,10,'Point P')
 if len(p['monitor']['point'])!=3:raise ValueError('Point P')
 for a in p['strings']['items']:
  limit(a['midi'],24,88,'MIDI');limit(a['fret'],0,24,'Fret');limit(a['EI'],0,.01,'EI');limit(a['loss'],.01,10,'String loss')
  limit(a['mu'],.05,50,'Linear density');limit(a['hfLoss'],0,.01,'High frequency loss')
 if p['body'].get('outline') is not None:
  pts=np.asarray(p['body']['outline'],float)
  if pts.ndim!=2 or pts.shape[1]!=2 or not 16<=len(pts)<=180 or not np.isfinite(pts).all():raise ValueError('Contour SVG: 16–180 points')
 p['name']=str(p.get('name','GMT'))[:100]
 return p

def validate(project):
 """Validate shape before numerical work, retaining compatible v1 defaults."""
 if not isinstance(project,dict) or project.get('schema')!='gmt' or project.get('version')!=1:raise ValueError('Session GMT v1 attendue / expected')
 for key in ['body','hole','bridge','materials','strings','solver','excitation','monitor']:
  if not isinstance(project.get(key),dict):raise ValueError('Objet requis / required object: '+key)
 for key in ['synthesis','analysis','modalEdits']:
  if key in project and not isinstance(project[key],dict):raise ValueError('Objet invalide / invalid object: '+key)
 for values,label in [(project.get('braces'),'Braces'),(project['strings'].get('items'),'Strings')]:
  if not isinstance(values,list) or any(not isinstance(v,dict) for v in values):raise ValueError(label+': invalid list')
 for key in ['top','back','ribs','braces','bridge']:
  if not isinstance(project['materials'].get(key),dict):raise ValueError('Matériau requis / required material: '+key)
 for b in project['braces']:
  if any(not isinstance(b.get(k),list) or len(b[k])!=2 for k in ['a','b']):raise ValueError('Extrémités des barres / brace endpoints')
 if not isinstance(project['monitor'].get('point'),list):raise ValueError('Point P : trois coordonnées / three coordinates')
 try:p=_validate_parameters(project)
 except (KeyError,TypeError) as e:raise ValueError('Session incomplète ou mal formée / incomplete or malformed session: '+str(e)) from e
 def limit(x,a,b,key):
  if isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x) or not a<=x<=b:raise ValueError(f'{key}: {a}–{b}')
 def integer(x,a,b,key):
  limit(x,a,b,key)
  if int(x)!=x:raise ValueError(key+': entier requis / integer required')
 for obj,key in [(p['body'],'backEnabled'),(p['body'],'ribsEnabled'),(p['solver'],'air')]:
  if not isinstance(obj.get(key),bool):raise ValueError(key+': boolean required')
 if 'sympathetic' in p['excitation'] and not isinstance(p['excitation']['sympathetic'],bool):raise ValueError('Sympathetic: boolean required')
 integer(p['solver']['modes'],8,180,'Modes');integer(p['solver']['airModes'],2,30,'Air modes')
 ids=set()
 for b in p['braces']:
  if not isinstance(b.get('id'),str) or not b['id'] or b['id'] in ids:raise ValueError('Identifiants de barres uniques requis / unique brace IDs required')
  ids.add(b['id'])
  if math.dist(b['a'],b['b'])<1:raise ValueError('Barre trop courte / brace shorter than 1 mm')
 from .strings import string_properties
 for i,a in enumerate(p['strings']['items']):
  if not isinstance(a.get('muted',False),bool):raise ValueError('Muted: boolean required')
  integer(a['midi'],24,88,'MIDI');integer(a['fret'],0,24,'Fret');string_properties(p,i)
 monitor=p['monitor'];analysis=p['analysis']
 for key,allowed in [('source',['force','velocity','pressure']),('mode',['peak','rms','fixed']),('radiation',['panels'])]:
  if monitor.get(key) not in allowed:raise ValueError('Monitor '+key)
 limit(monitor.get('level'),0,1,'Volume');limit(monitor.get('gain'),-100,100,'Gain dB')
 if str(analysis['fft']) not in ['1024','2048','4096','8192','16384']:raise ValueError('FFT: 1024, 2048, 4096, 8192, 16384')
 analysis['fft']=int(analysis['fft'])
 for key,allowed in [('window',['hann','hamming','blackman','rect']),('palette',['magma','viridis','turbo','rainbow','balance','gray']),('scale',['linear','log']),('reference',['peak','absolute']),('gesture',['pan','select'])]:
  if analysis[key] not in allowed:raise ValueError('Analysis '+key)
 for key,a,b in [('range',20,120),('ceiling',-180,80),('volume',0,1),('fmin',0,22050),('fmax',0,22050),('tmin',0,30),('tmax',0,30)]:limit(analysis[key],a,b,'Analysis '+key)
 if analysis['fmin']>=analysis['fmax'] or analysis['tmin']>=analysis['tmax']:raise ValueError('Axes analyse : min < max / analysis axes')
 selection=analysis.get('selection')
 if selection is not None:
  if not isinstance(selection,dict):raise ValueError('Sélection / selection')
  for key,maximum in [('t0',30),('t1',30),('f0',22050),('f1',22050)]:limit(selection.get(key),0,maximum,'Selection '+key)
  if selection['t0']>=selection['t1'] or selection['f0']>=selection['f1']:raise ValueError('Sélection vide / empty selection')
 for index,edit in p.get('modalEdits',{}).items():
  if not str(index).isdigit() or not 0<=int(index)<180 or not isinstance(edit,dict):raise ValueError('Mode invalide / invalid mode')
  for key,a,b in [('f',5,20000),('zeta',.1,15),('gainDB',-24,24)]:
   if key in edit:limit(edit[key],a,b,'Mode '+key)
 return p

def public_catalog():
 from .contours import catalog_outlines,cutaway_profiles
 return dict(materials=MATERIALS,presets=PRESETS,defaults={k:default_project(k) for k in PRESETS},outlines=catalog_outlines(),cutaways={k:{a:b for a,b in v.items() if a!='points'} for k,v in cutaway_profiles().items()})
