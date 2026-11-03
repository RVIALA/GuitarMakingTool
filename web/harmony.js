/* PickupTool harmony: pitch-class naming and deterministic, tuning-aware fingering search. */
function PafHarmonyFactory(){
  'use strict';
  const names=['C','C♯','D','E♭','E','F','F♯','G','A♭','A','B♭','B'];
  const types=[
    ['major','',[0,4,7],'Majeur','Major'],['minor','m',[0,3,7],'Mineur','Minor'],
    ['7','7',[0,4,7,10],'Septième dominante','Dominant seventh'],['maj7','maj7',[0,4,7,11],'Septième majeure','Major seventh'],['m7','m7',[0,3,7,10],'Septième mineure','Minor seventh'],
    ['5','5',[0,7],'Quinte / power chord','Fifth / power chord'],['sus2','sus2',[0,2,7],'Suspendu 2','Suspended 2'],['sus4','sus4',[0,5,7],'Suspendu 4','Suspended 4'],
    ['7sus4','7sus4',[0,5,7,10],'Septième suspendue 4','Suspended seventh'],['m11','m11',[0,3,5,7,10],'Mineur onzième (sans 9)','Minor eleventh (no 9)'],
    ['dim','dim',[0,3,6],'Diminué','Diminished'],['aug','+',[0,4,8],'Augmenté','Augmented'],['6','6',[0,4,7,9],'Sixte majeure','Major sixth'],['m6','m6',[0,3,7,9],'Sixte mineure','Minor sixth'],
    ['m7b5','m7♭5',[0,3,6,10],'Demi-diminué','Half-diminished'],['dim7','dim7',[0,3,6,9],'Septième diminuée','Diminished seventh'],
    ['add9','add9',[0,2,4,7],'Neuvième ajoutée','Added ninth'],['madd9','m(add9)',[0,2,3,7],'Neuvième ajoutée mineure','Minor added ninth'],
    ['9','9',[0,2,4,7,10],'Neuvième dominante','Dominant ninth'],['maj9','maj9',[0,2,4,7,11],'Neuvième majeure','Major ninth'],['m9','m9',[0,2,3,7,10],'Neuvième mineure','Minor ninth']
  ].map(([id,suffix,intervals,fr,en])=>({id,suffix,intervals,fr,en}));
  const pc=n=>((n%12)+12)%12, symbol=(root,type)=>names[pc(root)]+(types.find(t=>t.id===type)?.suffix||'');
  function recognize(notes){
    if(!notes.length)return [];
    const bass=pc(Math.min(...notes)),pcs=new Set(notes.map(pc));if(pcs.size===1)return [{symbol:names[bass],root:bass,type:'note',score:100,exact:true,bass}];
    const result=[];
    for(let root=0;root<12;root++)for(let rank=0;rank<types.length;rank++){
      const t=types[rank],target=t.intervals.map(x=>pc(root+x)),missing=target.filter(x=>!pcs.has(x)),extra=[...pcs].filter(x=>!target.includes(x));
      // Never name unrelated notes. A missing fifth is the sole incomplete-chord interpretation.
      if(extra.length||missing.some(x=>pc(x-root)!==7)||missing.length>1||pcs.size<3&&t.id!=='5')continue;
      const exact=missing.length===0,score=100-22*missing.length+(root===bass?8:0)-rank*.25;
      result.push({symbol:symbol(root,t.id)+(bass!==root?'/'+names[bass]:'')+(missing.length?' (no5)':''),root,type:t.id,bass,exact,score});
    }
    return result.sort((a,b)=>b.score-a.score).slice(0,4);
  }
  const common={
    '0:major':[[-1,3,2,0,1,0]],'2:major':[[-1,-1,0,2,3,2]],'4:major':[[0,2,2,1,0,0]],'5:major':[[1,3,3,2,1,1]],'7:major':[[3,2,0,0,0,3],[3,2,0,0,3,3]],'9:major':[[-1,0,2,2,2,0]],
    '2:minor':[[-1,-1,0,2,3,1]],'4:minor':[[0,2,2,0,0,0]],'9:minor':[[-1,0,2,2,1,0]],
    '0:7':[[-1,3,2,3,1,0]],'2:7':[[-1,-1,0,2,1,2]],'4:7':[[0,2,0,1,0,0]],'7:7':[[3,2,0,0,0,1]],'9:7':[[-1,0,2,0,2,0]],'11:7':[[-1,2,1,2,0,2]],
    '0:maj7':[[-1,3,2,0,0,0]],'2:maj7':[[-1,-1,0,2,2,2]],'4:maj7':[[0,2,1,1,0,0]],'9:maj7':[[-1,0,2,1,2,0]],'5:maj7':[[-1,-1,3,2,1,0]],
    '2:m7':[[-1,-1,0,2,1,1]],'4:m7':[[0,2,0,0,0,0]],'9:m7':[[-1,0,2,0,1,0]],
    '2:sus2':[[-1,-1,0,2,3,0]],'9:sus2':[[-1,0,2,2,0,0]],'2:sus4':[[-1,-1,0,2,3,3]],'9:sus4':[[-1,0,2,2,3,0]],'4:sus4':[[0,2,2,2,0,0]]
  };
  function voicings(root,type,tuning=[40,45,50,55,59,64],limit=5){
    const t=types.find(t=>t.id===type);if(!t)return [];
    root=pc(root);const targets=t.intervals.map(x=>pc(root+x)),needed=targets.length>tuning.length?targets.filter(x=>pc(x-root)!==7):targets;
    const candidates=new Map(),standard=String(tuning)==='40,45,50,55,59,64',bass=tuning.length===4;
    function add(frets,priority=0){
      const midi=frets.map((f,i)=>f<0?-1:tuning[i]+f).filter(x=>x>=0),pcs=new Set(midi.map(pc));
      if(needed.some(x=>!pcs.has(x))||[...pcs].some(x=>!targets.includes(x))||midi.length<Math.min(3,needed.length))return;
      const finger=frets.filter(x=>x>0),lo=Math.min(...finger,25),hi=Math.max(...finger,0),span=hi-lo;
      if(span>(bass&&lo<7?3:4))return;
      // One index barre plus three independent fingers; an open note cannot lie under the barre.
      let count=finger.length;
      if(count>4){for(const f of new Set(finger)){const at=frets.map((x,i)=>x===f?i:-1).filter(i=>i>=0);if(at.length<2)continue;const a=at[0],b=at.at(-1);if(frets.slice(a,b+1).every(x=>x<0||x>=f))count=Math.min(count,finger.length-at.length+1);}}
      if(count>4)return;
      const low=pc(Math.min(...midi)),muted=frets.filter(x=>x<0).length,internal=frets.slice(frets.findIndex(x=>x>=0),frets.findLastIndex(x=>x>=0)+1).filter(x=>x<0).length;
      const score=priority? -1000+priority : (lo===25?0:lo)*1.3+Math.max(0,span)*2.5+count*.6+muted*1.5+internal*5+(low!==root?8:0)-(frets.filter(x=>x===0).length)*.5;
      const key=frets.join(',');if(!candidates.has(key)||score<candidates.get(key).score)candidates.set(key,{frets:frets.slice(),score,position:lo===25?0:lo,common:!!priority,symbol:symbol(root,type)+(low!==root?'/'+names[low]:''),omitted:targets.filter(x=>!pcs.has(x)).map(x=>pc(x-root)),notes:midi});
    }
    if(standard){(common[root+':'+type]||[]).forEach((f,i)=>add(f,i+1));
      // Familiar E and A barre families, ordered after open first-position shapes.
      const families={major:[[0,2,2,1,0,0],[-1,0,2,2,2,0]],minor:[[0,2,2,0,0,0],[-1,0,2,2,1,0]],'7':[[0,2,0,1,0,0],[-1,0,2,0,2,0]],maj7:[[0,2,1,1,0,0],[-1,0,2,1,2,0]],m7:[[0,2,0,0,0,0],[-1,0,2,0,1,0]],'5':[[0,2,2,-1,-1,-1],[-1,0,2,2,-1,-1]]};
      (families[type]||[]).forEach((f,i)=>{const offset=pc(root-[4,9][i]);for(const n of [offset,offset+12])if(n<=15)add(f.map(x=>x<0?-1:x+n),10+n+i*.1);});
    }
    // Search compact four-fret windows. Supports arbitrary tuning and the four-string bass.
    for(let start=0;start<=(bass?21:20);start++){
      const end=Math.min(24,start+(bass&&start<7?3:4)),choices=tuning.map(m=>{let a=[-1];if(start<5&&targets.includes(pc(m)))a.push(0);for(let f=Math.max(1,start);f<=end;f++)if(targets.includes(pc(m+f)))a.push(f);return a;});
      function walk(i,f){if(i===tuning.length){add(f);return;}for(const n of choices[i]){f.push(n);walk(i+1,f);f.pop();}}walk(0,[]);
    }
    const sorted=[...candidates.values()].sort((a,b)=>a.score-b.score),chosen=[];
    // Prefer distinct positions/voicings, then fill remaining slots with the next simplest candidates.
    for(const c of sorted){if(chosen.length===limit)break;if(chosen.every(a=>Math.abs(a.position-c.position)>=2||a.frets.filter((f,i)=>f!==c.frets[i]).length>=3))chosen.push(c);}
    for(const c of sorted){if(chosen.length===limit)break;if(!chosen.includes(c))chosen.push(c);}
    return chosen;
  }
  return {types,names,pc,symbol,recognize,voicings};
}
export const Harmony=PafHarmonyFactory();
