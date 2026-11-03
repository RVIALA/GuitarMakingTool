// Traditional melodies and original acoustic studies, no recorded audio.
export const repertoire=[
 {id:'frere',fr:'Frère Jacques',en:'Frère Jacques / Brother John',credit:['Traditionnel · mélodie du domaine public','Traditional · public-domain melody'],tempo:100,notes:[[60,1],[62,1],[64,1],[60,1],[60,1],[62,1],[64,1],[60,1],[64,1],[65,1],[67,2],[64,1],[65,1],[67,2]]},
 {id:'lune',fr:'Au clair de la lune',en:'Au clair de la lune',credit:['Traditionnel · mélodie du domaine public','Traditional · public-domain melody'],tempo:90,notes:[[60,1],[60,1],[60,1],[62,1],[64,2],[62,2],[60,1],[64,1],[62,1],[62,1],[60,4]]},
 {id:'joy',fr:'Ode à la joie',en:'Ode to Joy',credit:['L. van Beethoven · thème de 1824, domaine public','L. van Beethoven · 1824 theme, public domain'],tempo:110,notes:[[64,1],[64,1],[65,1],[67,1],[67,1],[65,1],[64,1],[62,1],[60,1],[60,1],[62,1],[64,1],[64,1.5],[62,.5],[62,2]]},
 {id:'arp',fr:'Arpège en mi mineur',en:'E minor arpeggio',credit:['Motif original GMT','Original GMT pattern'],tempo:90,tab:[[0,0],[2,2],[3,0],[4,0],[5,0],[4,0],[3,0],[2,2],[0,0],[2,2],[3,0],[4,0],[5,2],[4,0],[3,0],[2,2]]},
 {id:'folk',fr:'Basse alternée et cordes aiguës',en:'Alternating bass and treble strings',credit:['Motif original GMT','Original GMT pattern'],tempo:110,tab:[[0,3],[3,0],[4,0],[5,3],[2,0],[3,0],[4,0],[5,0],[0,3],[3,0],[4,0],[5,2],[2,0],[3,0],[4,0],[5,3]]}
];
export function phraseEvents(piece,tempo,strings){
 if(!Number.isFinite(tempo)||tempo<60||tempo>180)throw new Error('Tempo: 60–180 BPM');
 let beat=0;return (piece.notes||piece.tab).map(([pitch,duration],i)=>{
  let string,fret,beats;
  if(piece.tab){string=pitch;fret=duration;beats=.5;}
  else{beats=duration;const candidates=strings.map((s,string)=>({string,fret:pitch-s.midi})).filter(s=>Number.isInteger(s.fret)&&s.fret>=0&&s.fret<=24&&!strings[s.string].muted).sort((a,b)=>a.fret-b.fret);if(!candidates.length)throw new Error('Note hors accordage ou cordes muettes / Note unavailable in this tuning or strings muted: '+pitch);({string,fret}=candidates[0]);}
  const event={string,fret,time:beat*60/tempo,duration:beats*60/tempo*(piece.tab?1.8:.94),strength:i%4===0?1:.8};beat+=beats;return event;
 });
}
