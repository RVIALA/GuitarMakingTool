"""Independent coupled-solve, curved frames, event timing and input regressions."""
import sys,copy,concurrent.futures
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from backend.catalog import default_project,validate
from backend.fem import frames
from backend.geometry import warp
from backend.response import coefficients,response_grid,modal_parameters,RHO,SOUND
from backend.audio import synthesize,validate_events
rng=np.random.default_rng(719);p=default_project();nm=32;na=8
wm=2*np.pi*np.geomspace(95,12000,nm);projection=rng.normal(size=(nm,12))*.1
m=dict(omega=wm,wood=dict(omega=wm,loss=np.full(nm,.02)),projection=projection,air=dict(C=rng.normal(size=(nm,na))*.03,h=rng.normal(size=na)*3,k2=(2*np.pi*np.r_[0,np.linspace(300,3000,na-1)]/SOUND)**2,area=.006,volume=.012,aperture=[dict(center=[0,.3,0],area=.006)]),centers=rng.uniform(-.1,.1,(4,3)),radiation=rng.normal(size=(4,nm))*.001,residual=dict(rank=0),cache={})
f=np.unique(np.r_[0,.01,.1,1,5,20,np.geomspace(30,20000,100),wm/(2*np.pi)])
y,h=coefficients(m,p,f);a=m['air'];mass=RHO*p['hole']['endFactor']*np.sqrt(a['area']/np.pi)/a['area'];wm,z,gain=modal_parameters(m,p);reference=[]
for frequency in f:
 w=2*np.pi*max(.01,frequency);den=a['k2']-(w/SOUND)**2+2j*.025*w*SOUND*np.sqrt(a['k2'])/SOUND**2;fluid=RHO*w*w/den
 D=np.zeros((nm+1,nm+1),complex);D[:nm,:nm]=np.diag(wm**2-w*w+2j*w*z*wm)-(a['C']*fluid)@a['C'].T
 cross=-(a['C']*fluid)@a['h'];D[:nm,-1]=cross;D[-1,:nm]=cross
 resistance=p['hole']['resistance']*(RHO*w*w/(4*np.pi*SOUND)+.05*mass*max(1,SOUND*np.sqrt(a['area']/(a['volume']*p['hole']['endFactor']*np.sqrt(a['area']/np.pi)))))
 D[-1,-1]=-w*w*mass+1j*w*resistance-np.sum(a['h']**2*fluid)
 q=np.linalg.solve(D,np.vstack([projection,np.zeros((1,12))]));reference.append(1j*w*projection.T@q[:nm] if frequency else np.zeros((12,12)))
error=np.linalg.norm(y-reference)/np.linalg.norm(reference);assert error<1e-10,error
assert np.max(abs(y-np.swapaxes(y,1,2)))<1e-10
assert min(np.linalg.eigvalsh((v+v.conj().T)/2).min() for v in y)>-1e-10
print('PASS: independent dense coupled solve, reciprocity/passivity; relative error',error)
p=default_project('archtop');xy=np.array([[.12,.19],[-.1,.31],[0,.25]])
for part,z0 in [('top',.002),('back',-.085)]:
 original=np.c_[xy,np.full(len(xy),z0)];points=warp(p,original);rot=frames(dict(part=part),points,p);eps=1e-6
 dx=(warp(p,original+[eps,0,0])-warp(p,original-[eps,0,0]))/(2*eps);dy=(warp(p,original+[0,eps,0])-warp(p,original-[0,eps,0]))/(2*eps)
 normal=np.cross(dx,dy);normal/=np.linalg.norm(normal,axis=1)[:,None]
 assert np.max(abs(np.einsum('ni,nij->nj',normal,rot[:,:,:2])))<1e-9
 assert np.max(abs(np.einsum('nji,njk->nik',rot,rot)-np.eye(3)))<1e-12
print('PASS: tangent, orthonormal top/back material frames')
p=default_project();p['excitation']['duration']=.5;p['synthesis']['extension']='none';p['synthesis']['fmax']=6000
wm=2*np.pi*np.array([145,230,380,640.]);m=dict(omega=wm,wood=dict(omega=wm,loss=np.full(4,.025)),projection=rng.normal(size=(4,12))*.2,air=None,centers=np.array([[0,.25,0]]),radiation=np.array([[.03,.015,.01,.005]]),residual=dict(rank=0),cache={})
a=synthesize(m,p,[dict(string=5,time=.25)]);b=synthesize(m,p,[dict(string=5,time=0)]);off=round(.25*a['sr'])
for key in ['force','velocity','pressure']:
 assert np.count_nonzero(a[key][:off])==0;np.testing.assert_array_equal(a[key][off:],b[key]);assert a[key][-1]==0
c=synthesize(m,p,[dict(string=5,time=0,strength=.5),dict(string=5,time=.25)])
for key in ['force','velocity','pressure']:
 expected=a[key].astype(float);expected[:len(b[key])]+=.5*b[key];np.testing.assert_allclose(c[key],expected,atol=1e-8,rtol=1e-6)
p2=copy.deepcopy(p);p2['monitor']['point'][2]=2
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda project:response_grid(m,project),[p,p2]*4))
for i in range(2,len(results)):np.testing.assert_array_equal(results[i][2],results[i%2][2])
assert np.linalg.norm(results[0][2]-results[1][2])>0
print('PASS: exact time shift, zero pre-attack, superposition, smooth ending and concurrent response cache')
for key in ['om','dread','classical','selmer_oval','selmer_d','archtop']:validate(default_project(key))
legacy=default_project();del legacy['analysis'];del legacy['synthesis'];del legacy['solver']['fmin'];assert validate(legacy)['analysis']['fft']==4096
for modify in [lambda p:p['analysis'].update(fft=12345),lambda p:p['monitor'].update(point=[0,1]),lambda p:p['solver'].update(modes=8.5),lambda p:p['analysis'].update(tmax=float('nan')),lambda p:p.update(braces='bad'),lambda p:p['strings']['items'][0].update(midi=24,mu=.05,EI=.01),lambda p:p.update(modalEdits={'-1':{}})]:
 p=default_project();modify(p)
 try:validate(p);raise AssertionError('Invalid project accepted')
 except ValueError:pass
for event in [dict(string=-1),dict(string=6),dict(string=.5),dict(string=0,time=float('nan')),dict(string=0,strength=float('inf'))]:
 try:validate_events([event],0);raise AssertionError('Invalid event accepted')
 except ValueError:pass
print('PASS: current/legacy sessions and invalid input rejection')
