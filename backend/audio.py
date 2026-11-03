"""Linear plucked strings coupled to the complete FE 12-port body mobility."""
import json, math, threading
import numpy as np
from scipy.fft import rfft,irfft,next_fast_len
from .response import response_grid
from .strings import string_properties,string_impedance,decay_rate

def interpolate(grid,values,f):
 flat=values.reshape(len(grid),-1);out=np.empty((len(f),flat.shape[1]),complex)
 for j in range(flat.shape[1]):out[:,j]=np.interp(f,grid,flat[:,j].real)+1j*np.interp(f,grid,flat[:,j].imag)
 beyond=f>grid[-1];out[beyond]*=(grid[-1]/f[beyond])[:,None]
 return out.reshape((len(f),)+values.shape[1:])

def validate_events(events,selected):
 def integer(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) and int(x)==x
 if not integer(selected) or not 0<=selected<6:raise ValueError('Contact sélectionné : 0–5 / selected contact')
 if not isinstance(events,list) or not 1<=len(events)<=40:raise ValueError('1–40 attaques / attacks')
 clean=[]
 for event in events:
  if not isinstance(event,dict):raise ValueError('Événement invalide / invalid event')
  i=event.get('string');t=event.get('time',0);s=event.get('strength',1)
  if not integer(i) or not 0<=i<6:raise ValueError('Corde : 0–5 / string')
  if any(isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x) for x in [t,s]) or not 0<=t<=16 or not .01<=s<=3:raise ValueError('Événement hors limites / invalid event')
  clean.append(dict(string=int(i),time=float(t),strength=float(s)))
 return clean,int(selected)

def templates(model,p,active,selected,sr):
 """Finite-duration per-attack responses, independent of event timing.

 Frequency-domain coupling remains a finite-FFT transient approximation.
 Cropping each note at its release origin makes sequencing strictly ordered.
 """
 e=p['excitation'];duration=e['duration'];count=math.ceil(duration*sr)
 signature=json.dumps([p['strings'],e,p['synthesis'],p.get('modalEdits',{}),p['hole']['endFactor'],p['hole']['resistance'],p['monitor']['point'],active,selected,sr],sort_keys=True)
 with model.setdefault('lock',threading.RLock()):
  cached=model.get('audioTemplates')
  if cached is not None and cached[0]==signature:return cached[1]
  N=next_fast_len(count+2*sr,real=True);t=np.arange(count)/sr;blocked=np.zeros((N,len(active)));angle=np.deg2rad(e['angle']);ca,sa=np.cos(angle),np.sin(angle);strings=[string_properties(p,i) for i in range(6)]
  for j,i in enumerate(active):
   st=strings[i];position=np.clip(e['position']*.001,.002,st['L']-.002);width=e['width']*.001*(4 if e['kind']=='finger' else 1)
   for n in range(1,385):
    k=n*np.pi/st['L'];w=np.sqrt((st['T']*k*k+st['EI']*k**4)/st['mu']);f=w/(2*np.pi)
    if f>min(sr*.48,p['synthesis']['fmax']*1.1):break
    smoothing=np.sinc(k*width/(2*np.pi))*np.exp(-(1-e['hardness'])*f/(1400 if e['kind']=='finger' else 3800))
    q=2*e['force']*np.sin(k*position)/(st['L']*(st['T']*k*k+st['EI']*k**4))*smoothing
    A=(st['T']*k+st['EI']*k**3)*q;alpha=decay_rate(st,f)
    blocked[:count,j]+=A*np.cos(w*t)*np.exp(-alpha*t)
  fft=rfft(blocked,axis=0);del blocked
  frequencies=np.fft.rfftfreq(N,1/sr);grid,Ybody,Hbody=response_grid(model,p);spectra=np.zeros((len(frequencies),3,len(active)),complex);identity=np.eye(12)
  for start in range(0,len(frequencies),512):
   sl=slice(start,start+512);f=frequencies[sl];Y=interpolate(grid,Ybody,f);H=interpolate(grid,Hbody,f)
   Z=np.tile(np.stack([string_impedance(st,f) if e.get('sympathetic',True) or i in active else np.zeros(len(f)) for i,st in enumerate(strings)],axis=1),(1,2))
   rhs=np.zeros((len(f),12,len(active)),complex)
   for j,i in enumerate(active):rhs[:,i,j]=fft[sl,j]*ca;rhs[:,i+6,j]=fft[sl,j]*sa
   force=np.linalg.solve(identity[None]+Z[:,:,None]*Y,rhs)
   spectra[sl,0]=ca*force[:,selected]+sa*force[:,selected+6]
   spectra[sl,1]=np.einsum('fi,fij->fj',ca*Y[:,selected]+sa*Y[:,selected+6],force)
   spectra[sl,2]=np.einsum('fi,fij->fj',H,force)
  del fft
  low=p['synthesis']['fmin'];high=min(p['synthesis']['fmax'],sr*.48);taper=np.ones(len(frequencies));upper=min((high-low)*.2,max(20,high*.04));taper[frequencies>=high]=0;edge=(frequencies>high-upper)&(frequencies<high);taper[edge]=.5*(1+np.cos(np.pi*(frequencies[edge]-(high-upper))/upper))
  if low>0:
   lower=min((high-low)*.2,max(5,low*.15));taper[frequencies<=low]=0;edge=(frequencies>low)&(frequencies<low+lower);taper[edge]*=.5*(1-np.cos(np.pi*(frequencies[edge]-low)/lower))
  spectra*=taper[:,None,None];bank=irfft(spectra,n=N,axis=0)[:count].astype(np.float32)
  # Avoid hard truncation clicks when a finite-duration note ends in a phrase.
  fade=min(len(bank),round(.01*sr));bank[-fade:]*=(.5*(1+np.cos(np.linspace(0,np.pi,fade))))[:,None,None]
  if not np.isfinite(bank).all():raise ValueError('Réponse non finie / non-finite response')
  model['audioTemplates']=(signature,bank);return bank

def synthesize(model,p,events,selected=0,sr=44100):
 events,selected=validate_events(events,selected);active=sorted({e['string'] for e in events});bank=templates(model,p,active,selected,sr)
 count=max(round(ev['time']*sr)+len(bank) for ev in events);out=np.zeros((count,3))
 for ev in events:
  if p['strings']['items'][ev['string']].get('muted',False):continue
  offset=round(ev['time']*sr);out[offset:offset+len(bank)]+=ev['strength']*bank[:,:,active.index(ev['string'])]
 return dict(sr=sr,duration=count/sr,**{key:out[:,j].astype(np.float32) for j,key in enumerate(['force','velocity','pressure'])},band=float(model['wood']['omega'][-1]/2/np.pi),synthesisBand=[p['synthesis']['fmin'],min(p['synthesis']['fmax'],sr*.48)],projection=p['synthesis']['extension']=='residual',strings=[string_properties(p,i) for i in range(6)])
