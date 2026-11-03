import sys,tempfile
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pyuff
from backend.universal import universal_modes,export_job
p=np.array([[0,0,0],[.1,0,0],[0,.2,0],[0,0,.03]],float);tri=np.array([[0,1,2],[0,3,1],[0,2,3],[1,3,2]])
v=np.arange(24,dtype=float).reshape(4,3,2)/31;f=np.array([123.456789,765.432198]);eta=np.array([.02,.04])
with tempfile.TemporaryDirectory() as d:
 path=Path(d)/'modes.unv';path.write_bytes(universal_modes(p,tri,v,f,eta,'Test instrument'))
 data=pyuff.UFF(str(path)).read_sets();assert [x['type'] for x in data]==[164,2411,2412,55,55]
 nodes=data[1];np.testing.assert_allclose(np.c_[nodes['x'],nodes['y'],nodes['z']],p,rtol=1e-14);assert len(data[2][91])==4
 for j,m in enumerate(data[3:]):
  assert m['analysis_type']==2 and m['data_ch']==2 and m['spec_data_type']==8
  np.testing.assert_allclose(np.c_[m['r1'],m['r2'],m['r3']],v[:,:,j],rtol=5e-6,atol=1e-8);np.testing.assert_allclose(m['freq'],f[j],rtol=5e-6);np.testing.assert_allclose(m['modal_damp_vis'],eta[j]/2);assert m['modal_m']==1
 model={'wood':{'ids':np.arange(4),'V':v.reshape(12,2),'omega':f*2*np.pi,'loss':eta},'raw':{'points':p}}
 export_job(model,{'triangles':tri},Path(d)/'stream.unv');assert (Path(d)/'stream.unv').read_bytes()==universal_modes(p,tri,v,f,eta)
 try:universal_modes(p,[[0,1,9]],v,f,eta)
 except ValueError:pass
 else:raise AssertionError('Invalid connectivity was accepted')
print('PASS: independent pyuff readback of SI units, geometry, connectivity, XYZ modes, modal mass, frequencies, damping and streamed export; invalid connectivity rejected.')
