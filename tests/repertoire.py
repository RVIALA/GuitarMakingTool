"""Render fretted phrases with a controlled reduced body model, including HTTP."""
import runpy,copy,json,base64,threading,urllib.request,http.server
from pathlib import Path
import numpy as np
ns=runpy.run_path(str(Path(__file__).with_name('live_bank.py')))
m,p=ns['m'],ns['p']
from backend.repertoire import synthesize_phrase
from backend.audio import templates
original=copy.deepcopy(p)
events=[dict(string=3,fret=2,time=0,duration=.2,strength=1),dict(string=3,fret=4,time=.3,duration=.2,strength=.8)]
r=synthesize_phrase(m,p,events,2)
assert p==original
assert len(r['pressure'])==22050 and np.isfinite(r['pressure']).all()
assert np.max(np.abs(r['pressure'][8820:13230]))==0
q=copy.deepcopy(p);q['strings']['items'][3]['fret']=2
expected=templates(m,q,[3],2,44100)[:8000,2,0]
np.testing.assert_allclose(r['pressure'][:8000],expected)
q=copy.deepcopy(p);q['excitation']['force']*=.5
half=synthesize_phrase(m,q,events,2)
np.testing.assert_allclose(half['pressure'],r['pressure']*.5,rtol=1e-5,atol=1e-10)
q=copy.deepcopy(p);q['strings']['items'][3]['muted']=True
assert not synthesize_phrase(m,q,events,2)['pressure'].any()
for key,value in [('fret',25),('fret',True),('duration',float('nan')),('duration',-1)]:
 bad=copy.deepcopy(events);bad[0][key]=value
 try:synthesize_phrase(m,p,bad,2);raise AssertionError('Invalid event accepted')
 except ValueError:pass
import server
http=http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
threading.Thread(target=http.serve_forever,daemon=True).start()
try:
 req=urllib.request.Request(f'http://127.0.0.1:{http.server_port}/api/audio',data=json.dumps(dict(id='banktest',project=p,events=events,selected=2,repertoire=True)).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req) as f:raw=json.load(f)
 np.testing.assert_array_equal(np.frombuffer(base64.b64decode(raw['pressure']),dtype='<f4'),r['pressure'])
finally:http.shutdown();http.server_close()
print('PASS: frets use coupled solver; no project mutation; timing, release, force scaling, mute, input validation and HTTP exactness.')
