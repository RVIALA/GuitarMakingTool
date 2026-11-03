"""Original Universal ASCII export: 164 units, 2411 nodes, 2412 surface, 55 modes.
Romain VIALA. No pyuff runtime dependency. UFF and UNV are alternative extensions.
"""
import numpy as np

def universal_modes(points,triangles,vectors,frequencies,losses,name='GMT',output=None):
    points=np.asarray(points,float);triangles=np.asarray(triangles,int);vectors=np.asarray(vectors,float)
    frequencies=np.asarray(frequencies,float);losses=np.asarray(losses,float)
    if points.ndim!=2 or points.shape[1]!=3 or vectors.shape!=(len(points),3,len(frequencies)):raise ValueError('Inconsistent nodal modal arrays')
    if triangles.ndim!=2 or triangles.shape[1]!=3 or (triangles.size and (triangles.min()<0 or triangles.max()>=len(points))):raise ValueError('Invalid surface connectivity')
    if losses.shape!=frequencies.shape or not all(np.isfinite(x).all() for x in [points,vectors,frequencies,losses]) or np.any(frequencies<=0) or np.any(losses<0):raise ValueError('Invalid modal values')
    class Sink:
        def append(self,line):output.write(line+'\n')
        def extend(self,values):
            for line in values:self.append(line)
    lines=Sink() if output is not None else []
    def begin(dataset):lines.extend([f'{-1:6d}',f'{dataset:6d}'])
    def end():lines.append(f'{-1:6d}')
    def ints(values):return ''.join(f'{int(x):10d}' for x in values)
    begin(164);lines.append(f'{1:10d}{"SI: m, N, s, K":20s}{1:10d}')
    lines.append(''.join(f'{x:25.17E}' for x in [1.,1.,1.]).replace('E','D'));lines.append(f'{0.:25.17E}'.replace('E','D'));end()
    begin(2411)
    for i,p in enumerate(points,1):lines.extend([ints([i,0,0,8]),''.join(f'{x:25.16E}' for x in p).replace('E','D')])
    end();begin(2412)
    # Linear skin triangles subdivide the quadratic surface; this is visualization
    # connectivity, not a replacement volume FE model. All solid nodes are retained.
    for i,tri in enumerate(triangles,1):lines.extend([ints([i,91,1,1,8,3]),ints(tri+1)])
    end()
    safe=''.join(c if 32<=ord(c)<127 else '_' for c in str(name))[:70]
    for j,f in enumerate(frequencies):
        begin(55);lines.extend([safe,'GMT - Romain VIALA','Original dry FE modes; no virtual FRF edits; no air modes','Mass normalized: Phi^T M Phi = 1; global XYZ translations','Coordinates: m. Equivalent viscous damping ratio eta/2.'])
        lines.extend([ints([1,2,2,8,2,3]),ints([2,4,1,j+1]),''.join(f'{x:13.5E}' for x in [f,1.,losses[j]/2,0.])])
        for i,v in enumerate(vectors[:,:,j],1):lines.extend([f'{i:10d}',''.join(f'{x:13.5E}' for x in v)])
        end()
    return None if output is not None else ('\n'.join(lines)+'\n').encode('ascii')

def export_job(model,visual,path,name='GMT'):
    w=model['wood'];temporary=path.with_suffix('.writing')
    try:
        with temporary.open('w',encoding='ascii',newline='\n') as output:
            universal_modes(model['raw']['points'][w['ids']],visual['triangles'],w['V'].reshape(-1,3,len(w['omega'])),w['omega']/(2*np.pi),w['loss'],name,output)
        temporary.replace(path)
    finally:temporary.unlink(missing_ok=True)
