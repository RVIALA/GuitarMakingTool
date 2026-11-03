"""Load-dependent residual-flexibility Ritz vectors for modal truncation.

These vectors approximate omitted elastic response; they are not resolved
eigenmodes. K and M are the same conformal FE operators as the retained modes.
"""
import numpy as np
from scipy import sparse,linalg
from scipy.sparse.linalg import splu


def residual_modes(raw,wood,B):
    free=wood['free'];K=wood['K'][free][:,free].tocsc();M=wood['M'][free][:,free]
    loads=B[free];V=wood['V'][free];omega=wood['omega']
    if raw['project']['solver']['support']=='free':
        # Elastic pseudoinverse: remove six rigid motions through mass constraints.
        xyz=raw['points'][wood['ids']];xyz=xyz-xyz.mean(0);R=np.zeros((len(xyz)*3,6))
        for j in range(3):
            R[j::3,j]=1
            axis=np.eye(3)[j];R[:,j+3]=np.cross(np.broadcast_to(axis,xyz.shape),xyz).ravel()
        R=R[free];gram=R.T@(M@R);R=R@linalg.solve_triangular(linalg.cholesky(gram,lower=True).T,np.eye(6),lower=False)
        # Scale constraints into the elastic stiffness range; unscaled mass
        # constraints make the indefinite solve needlessly ill-conditioned.
        MR=(M@R)*max(float(np.max(omega)**2),(2*np.pi*100)**2)
        system=sparse.bmat([[K,sparse.csc_matrix(MR)],[sparse.csc_matrix(MR.T),None]],format='csc')
        factor=splu(system)
        static=factor.solve(np.vstack([loads,np.zeros((6,loads.shape[1]))]))[:len(free)]
    else:
        factor=splu(K);static=factor.solve(loads)
    residual=static-V@((V.T@loads)/omega[:,None]**2)
    # Twice reorthogonalise to protect the low modes from numerical cancellation.
    for _ in range(2):residual-=V@(V.T@(M@residual))
    # Energy scaling keeps weak, very stiff local bridge vectors: a mass-only
    # rank test can discard their important static compliance in free bodies.
    G=residual.T@(K@residual);values,U=linalg.eigh((G+G.T)*.5)
    keep=values>max(values[-1]*1e-12,1e-30)
    if not np.any(keep):
        return dict(V=np.zeros((len(wood['ids'])*3,0)),omega=np.array([]),staticError=0.,rank=0)
    Q=residual@(U[:,keep]/np.sqrt(values[keep]))
    small=Q.T@(K@Q);mass=Q.T@(M@Q);ev,R=linalg.eigh((small+small.T)*.5,(mass+mass.T)*.5)
    positive=ev>(2*np.pi*5)**2;ev=ev[positive];local=Q@R[:,positive]
    full=np.zeros((len(wood['ids'])*3,len(ev)));full[free]=local
    P=V.T@loads;Pr=local.T@loads
    exact=loads.T@static
    corrected=(P.T/omega**2)@P+(Pr.T/ev)@Pr
    error=float(np.linalg.norm(corrected-exact)/max(np.linalg.norm(exact),1e-30))
    return dict(V=full,omega=np.sqrt(ev),staticError=error,rank=len(ev))
