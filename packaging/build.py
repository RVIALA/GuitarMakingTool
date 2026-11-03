from pathlib import Path
import sys,subprocess,platform,shutil,json,importlib.metadata as md
root=Path(__file__).resolve().parents[1]
name='GMT'
args=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onedir','--name',name,'--collect-all','numpy','--collect-all','scipy','--collect-all','shapely','--collect-submodules','backend']
for d in ['web','examples','backend/outlines']:
 if (root/d).exists():args+=['--add-data',str(root/d)+':'+d]
for f in ['backend/cutaways.json','LICENSE.txt','NOTICE.txt','CREDITS.md']:
 if (root/f).exists():args+=['--add-data',str(root/f)+':'+str(Path(f).parent)]
if name=='GMT':
 import gmsh
 args+=['--hidden-import','gmsh','--add-binary',str(gmsh.lib._name)+':.']
else:args+=['--collect-all','openpyxl']
args.append('desktop.py');subprocess.run(args,cwd=root,check=True)
folder=root/'dist'/name
if platform.system()!='Windows':
 p=folder/('Launch.command' if platform.system()=='Darwin' else 'Launch.sh')
 p.write_text('#!/bin/sh\ncd "$(dirname "$0")"\nexec ./'+name+' "$@"\n');p.chmod(0o755)
licenses=folder/'licenses';licenses.mkdir(exist_ok=True);manifest=[]
for candidate in [Path(sys.base_prefix)/'LICENSE.txt',Path(sys.base_prefix)/'lib'/('python'+str(sys.version_info.major)+'.'+str(sys.version_info.minor))/'LICENSE.txt']:
 if candidate.exists():shutil.copy2(candidate,licenses/'Python-LICENSE.txt');break
for package in ['numpy','scipy','shapely','gmsh' if name=='GMT' else 'openpyxl','pyinstaller']:
 dist=md.distribution(package);manifest.append(dict(name=package,version=dist.version))
 for f in dist.files or []:
  if any(x in str(f).lower() for x in ['license','copying','notice']) and '.dist-info/' in str(f):
   src=Path(dist.locate_file(f))
   if src.is_file():dst=licenses/package/Path(str(f).split('.dist-info/',1)[1]);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
(folder/'dependencies.json').write_text(json.dumps(manifest,indent=2))
for f in ['CREDITS.md','NOTICE.txt','LICENSE.txt','CORRESPONDING_SOURCE.md']:
 if (root/f).exists():shutil.copy2(root/f,folder/f)
shutil.copytree(root/'THIRD_PARTY_LICENSES',folder/'licenses',dirs_exist_ok=True)
archive=f'{name}-{platform.system()}-{platform.machine()}'
print(shutil.make_archive(str(root/'dist'/archive),'zip',root/'dist',name))
