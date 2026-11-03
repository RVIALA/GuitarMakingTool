"""Build the bilingual manual, then a separate English-only edition from the same sources."""
from pathlib import Path
import json,re,subprocess,tempfile,shutil
import build_manual as base
ROOT=Path(__file__).resolve().parents[1]
def english(text):
 if ' / ' not in text:return text
 # A slash between Python filenames is a code path list, not bilingual prose.
 if ' : ' not in text and all('.py' in p for p in text.split(' / ')):return text
 tail=text.rsplit(' / ',1)[1]
 if ' : ' in text:return text.split(' : ',1)[0]+' : '+tail
 if ' → ' in text and ':' not in text:return text.split(' → ',1)[0]+' → '+tail
 return tail

def command(tex,name,remove=False):
 pattern='\\'+name+'{';start=0
 while True:
  at=tex.find(pattern,start)
  if at<0:break
  end=at+len(pattern);level=1;i=end
  while level:
   if tex[i]=='{' and (i==0 or tex[i-1]!='\\'):level+=1
   if tex[i]=='}' and (i==0 or tex[i-1]!='\\'):level-=1
   i+=1
  replacement='' if remove else tex[end:i-1]+'\\par'
  tex=tex[:at]+replacement+tex[i:];start=at+len(replacement)
 return tex

def build():
 spec=json.loads((ROOT/'docs/equations.json').read_text())
 for suffix in ['aux','toc','out']:(ROOT/'docs'/('manual.'+suffix)).unlink(missing_ok=True)
 base.build(spec)
 translated=json.loads(json.dumps(spec))
 for g in translated['groups']:g['title']=english(g['title'])
 for pair in translated['tree']:pair[0]=english(pair[0])
 for graph in translated['graphs']:
  graph[0]=english(graph[0])
  for n in graph[1]:n[2]=english(n[2])
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);base.diagrams(translated,d,ROOT)
  for name in ['tree','dependencies']:
   text=(d/(name+'.tikz')).read_text().replace('Arborescence · File tree','File tree')
   (ROOT/'docs'/(name+'-en.tikz')).write_text(text)
 tex=(ROOT/'docs/manual.tex').read_text()
 for old,new in zip(spec['groups'],translated['groups']):tex=tex.replace(base.esc(old['title']),base.esc(new['title']))
 tex=command(tex,'FR',True);tex=command(tex,'EN')
 translations={
 'Équations et architecture du code\\par ':'', 'Auteur des applications / Application author':'Application author',
 '3 novembre 2026 / 3 November 2026':'3 November 2026','FR + EN':'EN',
 'Modèles et équations / Models and equations':'Models and equations','Arborescence / File tree':'File tree',
 'Interdépendances / Dependencies':'Dependencies','Index des équations / Equation index':'Equation index',
 'Groupe / Group':'Group','Fichier, ligne / File, line':'File, line','Compilation et limites / Build and limitations':'Build and limitations',
 'tree.tikz':'tree-en.tikz','dependencies.tikz':'dependencies-en.tikz'}
 for old,new in translations.items():tex=tex.replace(old,new)
 tex=tex.replace('\\textbf{Code :}','\\textbf{Code:}')
 d=ROOT/'docs';(d/'manual-en.tex').write_text(tex)
 for suffix in ['aux','out','toc']:(d/('manual-en.'+suffix)).unlink(missing_ok=True)
 for _ in range(2):
  p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','manual-en.tex'],cwd=d,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  if p.returncode:raise RuntimeError(p.stdout[-2500:])
 print(spec['name'],'English edition complete')
if __name__=='__main__':build()
