"""Bundled entry point; Python is included in desktop releases."""
import sys
if __name__=='__main__':
 if '--worker' in sys.argv:
  from backend.runner import run_job
  run_job(sys.argv[sys.argv.index('--worker')+1])
 elif '--self-test' in sys.argv:
  import numpy,scipy,shapely
  from backend.geometry import mesh
  print('Bundled runtime: OK')
 else:
  from server import main
  main()
