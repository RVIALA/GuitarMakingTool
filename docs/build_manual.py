from pathlib import Path
import json,hashlib,csv,subprocess,re,ast
ROOT=Path(__file__).resolve().parents[2]
def esc(s):
 s=str(s).replace('—','-').replace('–','-').replace('−','-').replace('→',' > ').replace('↔',' < > ')
 return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','^':r'\textasciicircum{}','~':r'\textasciitilde{}','_':r'\_','{':r'\{','}':r'\}'}.get(c,c) for c in s)
PRE=r'''\documentclass[10pt,a4paper]{article}
\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}\usepackage{lmodern,textcomp}
\usepackage[english]{babel}\babelprovide[import=fr]{french}\usepackage[a4paper,margin=21mm,headheight=14pt]{geometry}
\usepackage{amsmath,amssymb,mathtools,microtype,xcolor,graphicx,longtable,booktabs,array,needspace,fancyhdr,hyperref,tikz}
\usetikzlibrary{arrows.meta,positioning,calc}
\definecolor{ink}{HTML}{154C4C}\definecolor{paper}{HTML}{F0F5F3}
\hypersetup{colorlinks=true,linkcolor=ink,urlcolor=ink,pdftitle={TITLE - Equations and code},pdfauthor={Romain VIALA}}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small\sffamily TITLE}\fancyhead[R]{\small\sffamily VERSION / FR + EN}\fancyfoot[L]{\small\sffamily Romain VIALA}\fancyfoot[R]{\thepage}
\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}\setlength{\emergencystretch}{2em}
\newcommand{\FR}[1]{\textbf{FR.} #1\par}\newcommand{\EN}[1]{{\selectlanguage{english}\textbf{EN.} #1\par}}
\newcommand{\loc}[1]{{\small\color{ink}\textbf{Code :} #1\par}}
\newcommand{\sinc}{\operatorname{sinc}}\newcommand{\clip}{\operatorname{clip}}\newcommand{\diag}{\operatorname{diag}}\newcommand{\Rea}{\operatorname{Re}}\newcommand{\rms}{\operatorname{RMS}}
\allowdisplaybreaks[2]
\begin{document}
{\sffamily\color{ink}\Huge TITLE\par}\vspace{3mm}
{\sffamily\Large Équations et architecture du code\par Equations and code architecture\par}\vspace{5mm}
\textbf{Auteur des applications / Application author : Romain VIALA}\par
Version VERSION · 3 novembre 2026 / 3 November 2026\par
\FR{Ce manuel décrit les équations physiques, numériques, acoustiques, statistiques et de traitement du signal de cette distribution. Les opérations de mise en page en pixels et les contrôles de formulaire sont exclus. Les paramètres illustratifs ne sont pas des mesures.}
\EN{This manual describes the physical, numerical, acoustic, statistical and signal-processing equations in this distribution. Pixel layout and form validation are excluded. Illustrative parameters are not measurements.}
\FR{Les renvois sont relatifs à la racine du dépôt et comptent les lignes à partir de 1. Une plage désigne le bloc de fonction qui implémente le groupe ; une ligne seule désigne l’ancre de code. Une ligne JavaScript compacte peut contenir plusieurs équations. Le code fait foi pour les bornes et détails d’implémentation. source-map.json contient les ancres et empreintes SHA-256 ; verify\_references.py détecte les modifications.}
\EN{References are relative to the repository root and use one-based lines. Ranges identify implementing function blocks; single lines identify code anchors. A compact JavaScript line may contain several equations. Code is authoritative for bounds and implementation details. source-map.json records anchors and SHA-256 hashes; verify\_references.py detects changes.}
\FR{Conventions : unités SI sauf mention contraire ; $f$ en Hz, $\omega=2\pi f$ en rad/s, $f_s$ fréquence d’échantillonnage, $t$ en s, $i^2=-1$. Gain d’amplitude $10^{g/20}$ pour g en dB ; $\sinc x=\sin x/x$, avec $\sinc0=1$.}
\EN{Conventions: SI unless stated otherwise; $f$ in Hz, $\omega=2\pi f$ in rad/s, sample rate $f_s$, time $t$ in seconds, $i^2=-1$. Amplitude gain $10^{g/20}$ for g in dB; $\sinc x=\sin x/x$, with $\sinc0=1$.}
\clearpage\tableofcontents\clearpage
'''
VERIFY='''from pathlib import Path
import json,hashlib,sys
root=Path(__file__).resolve().parents[1]
d=json.loads((Path(__file__).parent/'source-map.json').read_text())
bad=[f for f,h in d['sha256'].items() if not (root/f).exists() or hashlib.sha256((root/f).read_bytes()).hexdigest()!=h]
if bad:print('Stale references / Renvois périmés:',*bad,sep='\\n');sys.exit(1)
print('Source hashes and references: OK / Empreintes et renvois : OK')
'''
TIKZ=r'''\begin{tikzpicture}[box/.style={draw=ink!65,fill=paper,rounded corners=3pt,align=left,text width=13.2cm,inner sep=8pt,font=\small\sffamily},arrow/.style={-{Stealth[length=2.5mm]},draw=ink!70,line width=.6pt}]
'''
def diagrams(spec,d,root):
 core=spec['tree'];parts=[]
 for page in range(0,len(core),9):
  lines=[TIKZ,r'\node[box,fill=ink!10] (root) at (0,0) {\textbf{'+esc(spec['name'])+r'} / '+esc('Arborescence · File tree')+'};']
  for n,(label,files) in enumerate(core[page:page+9],1):
   lines += [r'\node[box] (n'+str(n)+') at (0,'+str(-1.85*n)+r') {\textbf{'+esc(label)+r'}\\ '+esc(files)+'};',r'\draw[arrow] (root.west) -- ++(-.55,0) |- (n'+str(n)+'.west);']
  lines+= [r'\end{tikzpicture}'];parts.append('\n'.join(lines))
 (d/'tree.tikz').write_text('\n\\newpage\n'.join(parts))
 # Directed module dependencies, with routed edges behind generously spaced nodes.
 pages=[]
 for title,nodes,edges in spec['graphs']:
  lines=[TIKZ.replace('text width=13.2cm','text width=5.7cm'),r'\node[box,text width=13cm,fill=ink!10] at (0,2) {\textbf{'+esc(title)+'}};']
  for n,(x,y,label) in enumerate(nodes):
   lines += [r'\node[box] (n'+str(n)+') at ('+str(x)+','+str(y)+') {'+esc(label)+'};']
  for edge,(a,b) in enumerate(edges):
   xa,ya,_=nodes[a];xb,yb,_=nodes[b]
   if ya==yb:
    start,end=('east','west') if xa<xb else ('west','east')
    route='(n'+str(a)+'.'+start+') -- (n'+str(b)+'.'+end+')'
   elif xa==xb and abs(ya-yb)<3:
    start,end=('south','north') if ya>yb else ('north','south')
    route='(n'+str(a)+'.'+start+') -- (n'+str(b)+'.'+end+')'
   else:
    start='south' if ya>yb else 'north';gap=ya+(-1.05 if ya>yb else 1.05)
    sign=-1 if xb<0 else 1;lane=sign*(7.05+.02*edge);end='west' if sign<0 else 'east'
    route='(n'+str(a)+'.'+start+') -- ('+str(xa)+','+str(gap)+') -- ('+str(lane)+','+str(gap)+') |- (n'+str(b)+'.'+end+')'
   lines += [r'\draw[arrow] '+route+';']
  lines += [r'\end{tikzpicture}'];pages.append('\n'.join(lines))
 (d/'dependencies.tikz').write_text('\n\\newpage\n'.join(pages))
 for stem in ['tree','dependencies']:
  (d/(stem+'-standalone.tex')).write_text(r'''\documentclass[a4paper,10pt]{article}\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}\usepackage{lmodern,tikz}\usepackage[margin=21mm]{geometry}\usetikzlibrary{arrows.meta,positioning,calc}\definecolor{ink}{HTML}{154C4C}\definecolor{paper}{HTML}{F0F5F3}\begin{document}\pagestyle{empty}\begin{center}\input{'''+stem+r'''.tikz}\end{center}\end{document}''')
def build(spec):
 root=Path(__file__).resolve().parents[1];d=root/'docs';d.mkdir(exist_ok=True);maps=[];hashes={};parts=[PRE.replace('TITLE',spec['name']).replace('VERSION',spec['version'])]
 diagrams(spec,d,root)
 parts += [r'\section{Modèles et équations / Models and equations}']
 for n,g in enumerate(spec['groups'],1):
  refs=[]
  byfile={}
  for file,anchor in g['refs']:
   lines=(root/file).read_text().splitlines();hits=[i for i,x in enumerate(lines,1) if anchor in x]
   if not hits:raise ValueError(f'{spec["id"]} {file}: {anchor}')
   line=hits[0];end=line
   if file.endswith('.py') and anchor.strip().startswith(('def ','class ')):
    nodes=[x for x in ast.walk(ast.parse('\n'.join(lines))) if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and x.lineno==line]
    if nodes:end=nodes[0].end_lineno
   span=str(line) if end==line else str(line)+'-'+str(end)
   byfile.setdefault(file,[]).append(span);refs.append(r'\texttt{'+esc(file)+'} : '+str(line));maps.append(dict(group=n,title=g['title'],file=file,line=line,line_end=end,anchor=anchor));hashes[file]=hashlib.sha256((root/file).read_bytes()).hexdigest()
  refs=[r'\texttt{'+esc(f)+'} : '+', '.join(map(str,sorted(set(ls)))) for f,ls in byfile.items()]
  parts.extend([r'\begin{samepage}\Needspace{9\baselineskip}\subsection{'+esc(g['title'])+'}',r'\loc{'+r';\allowbreak\quad '.join(refs)+'}',r'\begin{align}'+re.sub(r'(\\\\\s*)(?=\[)',r'\1{}',g['math'])+r'\end{align}',r'\FR{'+esc(g['fr'])+'}',r'\EN{'+esc(g['en'])+'}',r'\end{samepage}'])
 parts += [r'\clearpage\section{Arborescence / File tree}',r'\FR{Les groupes de fichiers correspondent aux modules actifs. Le manifeste CSV du dépôt donne la liste complète.}',r'\EN{File groups describe active modules. The repository CSV manifest lists every distributed file.}',r'\begin{center}\input{tree.tikz}\end{center}',r'\clearpage\section{Interdépendances / Dependencies}',r'\FR{Flèches : appels, imports ou flux de données. Les sous-systèmes sont séparés pour garder les boîtes et les liens lisibles.}',r'\EN{Arrows: calls, imports or data flow. Subsystems are separated to keep boxes and links readable.}',r'\begin{center}\input{dependencies.tikz}\end{center}',r'\clearpage\section{Index des équations / Equation index}',r'\small\begin{longtable}{p{8mm}p{75mm}p{65mm}}\toprule N° & Groupe / Group & Fichier, ligne / File, line \\ \midrule\endhead']
 for m in maps:parts.append(str(m['group'])+' & '+esc(m['title'])+' & '+r'\texttt{'+esc(m['file'])+'} : '+(str(m['line']) if m['line_end']==m['line'] else str(m['line'])+'-'+str(m['line_end']))+r'\\[3pt]')
 parts += [r'\bottomrule\end{longtable}\normalsize',r'\Needspace{16\baselineskip}\section{Compilation et limites / Build and limitations}',r'\FR{Depuis docs/, exécuter deux fois pdflatex -halt-on-error manual.tex. Les fichiers *-standalone.tex compilent chaque schéma séparément. Papier A4, marges de 21 mm, sans réduction automatique des schémas. Les sources, licences et crédits tiers figurent dans CREDITS.md et SOURCES.md. Cette documentation décrit l’implémentation ; elle ne constitue pas une validation expérimentale.}',r'\EN{From docs/, run pdflatex -halt-on-error manual.tex twice. The *-standalone.tex wrappers compile each diagram separately. A4 paper, 21 mm margins, no automatic diagram shrinkage. Third-party sources, licenses and credits are in CREDITS.md and SOURCES.md. This documents implementation, not experimental validation.}',r'\end{document}']
 (d/'manual.tex').write_text('\n'.join(parts));(d/'equations.json').write_text(json.dumps(spec,indent=2,ensure_ascii=False));(d/'source-map.json').write_text(json.dumps(dict(author='Romain VIALA',version=spec['version'],sha256=hashes,references=maps),indent=2,ensure_ascii=False));(d/'verify_references.py').write_text(VERIFY)
 with (d/'equations.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=['group','title','file','line','line_end','anchor']);w.writeheader();w.writerows(maps)
 for _ in range(2):
  p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','manual.tex'],cwd=d,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  if p.returncode:raise RuntimeError(spec['id']+': '+p.stdout[-2200:])
 print(spec['name'],len(spec['groups']),'groups',len(maps),'references',flush=True)
if __name__=='__main__':
 import sys
 for path in sys.argv[1:]:build(json.loads(Path(path).read_text()))
