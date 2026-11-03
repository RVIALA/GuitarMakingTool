"""Stiff-string tuning and passive driving-point impedance."""
import math
import numpy as np

def string_properties(p,i):
 a=p['strings']['items'][i];L0=p['strings']['scale']*.001;L=L0*2**(-a['fret']/12);f=p['strings']['a4']*2**((a['midi']-69)/12);EI=a['EI'];mu=a['mu']*.001;T=4*mu*L0*L0*f*f-np.pi**2*EI/(L0*L0)
 if T<=0:raise ValueError('Rigidité/accordage incompatibles / incompatible string stiffness and tuning')
 return dict(L=L,L0=L0,mu=mu,T=T,EI=EI,f0=math.sqrt((T*(np.pi/L)**2+EI*(np.pi/L)**4)/mu)/(2*np.pi),loss=a['loss']*p['strings'].get('damping',1),hf=a.get('hfLoss',.00008)*p['strings'].get('damping',1),palm=p['excitation'].get('palm',0))

def decay_rate(st,f):
 # Palm contact represented by additional positive, frequency-dependent modal loss.
 # This phenomenological model does not solve nonlinear hand/string contact.
 return st['loss']+st['hf']*f+2e-8*f*f+st.get('palm',0)*(12+.015*f)

def string_impedance(st,f):
 w=2*np.pi*np.maximum(f,.001);alpha=decay_rate(st,f);wc=w-1j*alpha;EI=st['EI'];T=st['T'];mu=st['mu'];L=st['L']
 if EI>1e-12:
  disc=np.sqrt(T*T+4*EI*mu*wc*wc);k2=2*mu*wc*wc/(T+disc);k=np.sqrt(k2);kap2=(T+disc)/(2*EI);kap=np.sqrt(kap2);A=kap2/(kap2+k2);B=k2/(kap2+k2);D=(T+EI*k2)*k/np.tan(k*L)*A-EI*k2*kap/np.tanh(kap*L)*B
 else:k=wc*np.sqrt(mu/T);D=T*k/np.tan(k*L)
 Z=D/(1j*w);Z[f==0]=0;return Z

