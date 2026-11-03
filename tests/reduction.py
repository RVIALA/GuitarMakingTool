"""Independent dense-system check of residual-flexibility Ritz projection."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy import sparse
from backend.reduction import residual_modes

rng=np.random.default_rng(4103)
Q,_=np.linalg.qr(rng.normal(size=(9,9)));omega=2*np.pi*np.array([80,120,220,380,640,1000,1600,2500,4200.])
K=(Q*omega**2)@Q.T;B=rng.normal(size=(9,12));wood=dict(free=np.arange(9),K=sparse.csr_matrix(K),M=sparse.eye(9,format='csr'),V=Q[:,:3],omega=omega[:3],ids=np.arange(3))
raw=dict(project=dict(solver=dict(support='neck')))
res=residual_modes(raw,wood,B);assert res['rank']==6;assert res['staticError']<1e-10
V=np.column_stack([wood['V'],res['V']]);w=np.r_[wood['omega'],res['omega']];P=V.T@B
assert np.linalg.norm(V.T@V-np.eye(9))<1e-9
for f in [10,90,300,800,1800,3600,8000]:
    dynamic=K-(2*np.pi*f)**2*np.eye(9)+1j*.01*(2*np.pi*f)*np.eye(9)
    exact=B.T@np.linalg.solve(dynamic,B)
    projected=(P.T/(w**2-(2*np.pi*f)**2+1j*.01*(2*np.pi*f)))@P
    assert np.linalg.norm(projected-exact)/np.linalg.norm(exact)<1e-8
print('PASS: residual static compliance, mass orthogonality and dynamic response against an independent dense 9-DOF solution.')
