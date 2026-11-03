"""Local launch and duplicate/occupied-port checks, without opening a browser."""
import os,sys,subprocess,socket,time,json,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
args=[sys.executable,str(root/'server.py'),'--no-browser','--port',str(port)]
server=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
try:
 for attempt in range(80):
  try:
   with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health',timeout=1) as r:health=json.load(r)
   break
  except Exception:
   if server.poll() is not None:raise RuntimeError(server.stdout.read())
   time.sleep(.1)
 else:raise AssertionError('Server did not become ready')
 assert health['application']=='GMT' and health['version']=='1.7.1'
 second=subprocess.run(args,capture_output=True,text=True,timeout=10);assert second.returncode==0 and 'already running' in second.stdout
 with socket.socket() as sock:
  sock.bind(('127.0.0.1',0));other=sock.getsockname()[1];sock.listen()
  occupied=subprocess.run([*args[:-1],str(other)],capture_output=True,text=True,timeout=10)
  assert occupied.returncode!=0 and 'Port unavailable' in occupied.stderr
 print('PASS: server launch, matching duplicate detection and friendly occupied-port failure.')
finally:
 server.terminate()
 try:server.wait(timeout=5)
 except subprocess.TimeoutExpired:server.kill();server.wait()
