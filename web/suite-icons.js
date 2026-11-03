/* Original interface pictograms — Romain VIALA. Decorative; labels stay readable. */
(function(){'use strict';
 const paths={
 instrument:'M14 3l7 0-1 3-3 1-6 8m4-4c4 3 2 8-2 9-3 2-7 0-8-3-1-3 1-5 4-6l2 1 2-2zM8 17l2-2',
 strings:'M5 3v18M10 3v18M15 3v18M20 3v18M3 6h19M3 18h19',
 pickup:'M6 5h12v14H6zM9 8h.1M15 8h.1M9 12h.1M15 12h.1M9 16h.1M15 16h.1M3 9h3M18 15h3',
 circuit:'M3 7h5l2-3 4 6 2-3h5M3 17h7m4 0h7M10 14v6M14 14v6M3 7v10M21 7v10',
 settings:'M4 6h16M4 12h16M4 18h16M8 3v6M16 9v6M10 15v6',
 audio:'M3 10v4M7 6v12M11 3v18M15 7v10M19 9v6M23 11v2',
 analysis:'M3 3v18h18M5 17l4-4 3 2 3-10 3 8 3-2',
 geometry:'M12 2l9 5v10l-9 5-9-5V7zM3 7l9 5 9-5M12 12v10',
 material:'M4 3h16v18H4zM7 3c8 5-5 9 4 18M12 3c-3 5 9 9 3 18M17 3c5 8-3 11 2 18',
 mesh:'M3 3h18v18H3zM3 3l18 18M21 3L3 21M3 12h18M12 3v18',
 notes:'M9 18V5l11-2v13M9 8l11-2M9 18c0-3-6-3-6 0s6 3 6 0M20 16c0-3-6-3-6 0s6 3 6 0',
 save:'M4 3h13l4 4v14H3V3h1M7 3v7h9V3M7 21v-7h10v7',
 compare:'M4 4h6v16H4zM14 4h6v16h-6zM7 9v6M17 7v10',
 book:'M12 5C8 2 4 3 2 4v16c4-2 7-1 10 1 3-2 6-3 10-1V4c-4-1-7-2-10 1zM12 5v16',
 export:'M12 2v13M7 10l5 5 5-5M4 15v6h16v-6',
 bank:'M3 5h18v15H3zM3 9h18M7 13h4M15 13h2M7 17h4M15 17h2'
 };
 const tabs={play:'instrument',instrument:'instrument',strings:'strings',pickups:'pickup',circuit:'circuit',bridge:'audio',pedals:'settings',riffs:'notes',repertoire:'notes',analysis:'analysis',method:'book',help:'book',sessions:'save',design:'geometry',materials:'material',mesh:'mesh',frf:'analysis',compare:'compare',bank:'bank',specimen:'material',geometry:'geometry',audio:'audio',modes:'mesh',sensitivity:'analysis',inverse:'settings',jobs:'export'};
 const selector='[data-tab],[data-page],h2,h3';
 function decorate(el){if(!el.matches?.(selector))return;let key=tabs[el.dataset.tab||el.dataset.page];
  if(!key){const label=(el.dataset.en||el.textContent||'').toLowerCase();for(const [re,icon] of [[/export|télécharg|download/,'export'],[/compar/,'compare'],[/spect|analys|response|réponse|sensib/,'analysis'],[/cord|strings|tuning|accord/,'strings'],[/micro|pickup/,'pickup'],[/circuit|composant|component|impedance/,'circuit'],[/géom|geom|caisse|body|dimension|pièce|piece|specimen|atelier|workshop/,'geometry'],[/bois|wood|matériau|material|grain/,'material'],[/mode|maill|mesh/,'mesh'],[/répertoire|repertoire|phrase|riff|note/,'notes'],[/écoute|listen|audio|son |sound|archet|bow|geste|gesture|vibrato|mobilité|mobility/,'audio'],[/session|configur|mémoire|memor/,'save'],[/guide|help|aide|source|crédit|credit|hypoth|model|modèle/,'book'],[/régl|setting|param|control|effet|effect|pédal|pedal/,'settings']])if(re.test(label)){key=icon;break;}}
  if(!key||el.dataset.toolIcon===key)return;el.dataset.toolIcon=key;const svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round"><path d="'+paths[key]+'"/></svg>';el.style.setProperty('--tool-icon','url("data:image/svg+xml,'+encodeURIComponent(svg)+'")');
 }
 function scan(root){if(root.nodeType===1)decorate(root);root.querySelectorAll?.(selector).forEach(decorate);}
 scan(document);new MutationObserver(records=>{for(const r of records){decorate(r.target);for(const n of r.addedNodes)if(n.nodeType===1)scan(n);}}).observe(document.body,{childList:true,subtree:true});
})();
