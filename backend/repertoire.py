"""Fretted phrase rendering with the existing coupled string solver.

Each attack is an independent linear response, tapered at note release.
Changing fingerings does not model time-varying sympathetic coupling.
"""
from copy import deepcopy
import math
import numpy as np
from .audio import validate_events, templates

def synthesize_phrase(model,p,events,selected=0,sr=44100):
 clean,selected=validate_events(events,selected)
 for src,ev in zip(events,clean):
  fret=src.get('fret');duration=src.get('duration')
  if isinstance(fret,bool) or not isinstance(fret,int) or not 0<=fret<=24:
   raise ValueError('Case / fret: 0–24')
  if isinstance(duration,bool) or not isinstance(duration,(float,int)) or not math.isfinite(duration) or not .05<=duration<=8:
   raise ValueError('Durée de note / note duration: 0.05–8 s')
  ev.update(fret=fret,duration=duration)
 count=max(round((e['time']+min(e['duration'],p['excitation']['duration']))*sr) for e in clean)
 out=np.zeros((count,3),dtype=np.float32)
 # One bank at a time: bounded memory even for long phrases.
 groups={}
 for ev in clean:groups.setdefault((ev['string'],ev['fret']),[]).append(ev)
 for (string,fret),notes in groups.items():
  if p['strings']['items'][string].get('muted',False):continue
  note=deepcopy(p);note['strings']['items'][string]['fret']=fret
  bank=templates(model,note,[string],selected,sr)[:,:,0]
  for ev in notes:
   offset=round(ev['time']*sr);length=min(len(bank),round(ev['duration']*sr),count-offset)
   values=bank[:length].copy()*ev['strength']
   fade=min(length,max(1,round(.015*sr)))
   values[-fade:]*=np.linspace(1,0,fade)[:,None]
   out[offset:offset+length]+=values
 return dict(sr=sr,duration=count/sr,band=float(model['wood']['omega'][-1]/2/np.pi),synthesisBand=[p['synthesis']['fmin'],min(p['synthesis']['fmax'],sr*.48)],projection=p['synthesis']['extension']=='residual',**{key:out[:,i] for i,key in enumerate(['force','velocity','pressure'])})
