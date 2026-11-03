/* Common file exports and explicit recovery after a Safari audio interruption. */
(()=>{'use strict';
const contexts=new Set(),pending=new Set();let notice;
const english=()=>document.documentElement.lang==='en'||document.querySelector('#language')?.value==='en';
function refresh(){const interrupted=[...contexts].filter(c=>c.state==='interrupted');if(!notice&&interrupted.length){notice=document.createElement('div');notice.className='suite-audio-notice';notice.setAttribute('role','status');notice.innerHTML='<span></span><button type="button"></button>';notice.querySelector('button').onclick=()=>{for(const c of contexts)if(c.state==='interrupted'||pending.has(c))resumeAudio(c).catch(()=>{});};document.body.append(notice);}if(notice){notice.hidden=!interrupted.length;notice.querySelector('span').textContent=english()?'Audio interrupted. Tap Resume to enable sound.':'Audio interrompu. Touchez Reprendre pour réactiver le son.';notice.querySelector('button').textContent=english()?'Resume':'Reprendre';}}
function watchAudio(c){if(!contexts.has(c)){contexts.add(c);c.addEventListener('statechange',()=>{if(c.state==='closed'){contexts.delete(c);pending.delete(c);}if(c.state==='running')pending.delete(c);refresh();});}return c;}
function resumeAudio(c){watchAudio(c);if(c.state==='running')return Promise.resolve();if(c.state==='closed')return Promise.reject(Error('Audio context closed'));pending.add(c);return c.resume().then(()=>{if(c.state==='running')pending.delete(c);refresh();});}
// On touch devices the activation may arrive on release, after pointerdown.
for(const type of ['touchend','click','keydown'])document.addEventListener(type,()=>{for(const c of pending)if(c.state!=='closed')resumeAudio(c).catch(()=>{});},{capture:true,passive:true});
function download(blob,name){const u=URL.createObjectURL(blob),a=document.createElement('a');a.href=u;a.download=name;a.style.display='none';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),60000);}

// Display precision only: numerical state, inputs and exports retain their precision.
function number(value,digits=3,language=document.documentElement.lang||'en',maxDecimals){
 if(value===null||value===undefined||value===''||!Number.isFinite(Number(value)))return '—';
 const x=Number(value),a=Math.abs(x),opts={maximumSignificantDigits:Math.min(4,Math.max(1,digits)),useGrouping:false,notation:a!==0&&(a<.001||a>=1e6)?'scientific':'standard'};
 if(maxDecimals!==undefined&&a>=.001&&a<1e6){const rounded=Number(x.toPrecision(opts.maximumSignificantDigits));return Number(rounded.toFixed(maxDecimals)).toLocaleString(language,{maximumFractionDigits:maxDecimals,useGrouping:false});}
 return x.toLocaleString(language,opts);
}
function interval(value,lower,upper,language=document.documentElement.lang||'en'){
 if(![value,lower,upper].every(v=>typeof v==='number'&&Number.isFinite(v))||upper<=lower||value<lower||value>upper)return {value:number(value,3,language),lower:number(lower,3,language),upper:number(upper,3,language)};
 const uncertainty=Math.max(value-lower,upper-value),place=Math.floor(Math.log10(uncertainty))-1,step=10**place;
 const format=x=>{const rounded=Math.round(x/step)*step;return rounded.toLocaleString(language,{useGrouping:false,minimumFractionDigits:Math.min(12,Math.max(0,-place)),maximumFractionDigits:Math.min(12,Math.max(0,-place))});};
 return {value:format(value),lower:format(lower),upper:format(upper)};
}

window.AppUX={resumeAudio,watchAudio,download,number,interval};
document.addEventListener('DOMContentLoaded',()=>{
 document.querySelectorAll('input[type=file]').forEach(input=>{const a=input.accept||'';if(a.includes('.json')&&!a.includes('application/json'))input.accept+=',application/json';if(a.includes('.svg')&&!a.includes('image/svg+xml'))input.accept+=',image/svg+xml';});
 document.querySelectorAll('.tabs,.sidebar nav').forEach(nav=>nav.addEventListener('click',e=>{const b=e.target.closest('button');if(!b||nav.scrollWidth<=nav.clientWidth)return;nav.scrollTo({left:b.offsetLeft-nav.offsetLeft-(nav.clientWidth-b.offsetWidth)/2,behavior:'auto'});}));
});
})();
