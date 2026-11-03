import {paletteRGB} from './palettes.js';
export function fft(re,im){let n=re.length;if(n<2||n>4194304||(n&(n-1))||im.length!==n)throw new RangeError('FFT: matching power-of-two arrays required');for(let i=1,j=0;i<n;i++){let b=n>>1;for(;j&b;b>>=1)j^=b;j^=b;if(i<j){[re[i],re[j]]=[re[j],re[i]];[im[i],im[j]]=[im[j],im[i]];}}for(let len=2;len<=n;len<<=1){const a=-2*Math.PI/len,cr=Math.cos(a),ci=Math.sin(a);for(let i=0;i<n;i+=len){let wr=1,wi=0;for(let j=0;j<len/2;j++){let k=i+j,h=k+len/2,tr=re[h]*wr-im[h]*wi,ti=re[h]*wi+im[h]*wr;re[h]=re[k]-tr;im[h]=im[k]-ti;re[k]+=tr;im[k]+=ti;[wr,wi]=[wr*cr-wi*ci,wr*ci+wi*cr];}}}}
const windowCache=new Map();
export function windowData(n,name='hann'){
 const key=n+':'+name;if(windowCache.has(key))return windowCache.get(key);const weights=new Float64Array(n);let sum=0;
 for(let i=0;i<n;i++){const a=2*Math.PI*i/Math.max(1,n-1);weights[i]=name==='rect'?1:name==='hamming'?.54-.46*Math.cos(a):name==='blackman'?.42-.5*Math.cos(a)+.08*Math.cos(2*a):.5-.5*Math.cos(a);sum+=weights[i];}
 const data={weights,gain:2/Math.max(sum,1)};windowCache.set(key,data);return data;
}
export function spectrum(samples,n=4096,start=0,window='hann'){
 const re=new Float64Array(n),im=new Float64Array(n),{weights,gain}=windowData(n,window);
 for(let i=0;i<n;i++)re[i]=(samples[start+i]||0)*weights[i];fft(re,im);
 return Float32Array.from(re.slice(0,n/2),(x,i)=>20*Math.log10(Math.max(1e-14,Math.hypot(x,im[i])*gain*(i===0?.5:1))));
}

export function canvasSize(c){let r=c.getBoundingClientRect(),d=Math.min(2,globalThis.devicePixelRatio||1);if(!r.width||!r.height)return null;let w=Math.round(r.width*d),h=Math.round(r.height*d);if(c.width!==w||c.height!==h){c.width=w;c.height=h;}let g=c.getContext('2d');g.setTransform(d,0,0,d,0,0);return {g,w:r.width,h:r.height};}
export class LinePlot{
 constructor(canvas,{x=[0,1600],y=[-90,-10],xlabel='Hz',ylabel='dB',onEdit=null,onView=null}={}){this.canvas=canvas;this.x=[...x];this.y=[...y];this.xlabel=xlabel;this.ylabel=ylabel;this.onEdit=onEdit;this.onView=onView;this.curves=[];this.markers=[];this.edit=false;this.band=0;this.down=null;new ResizeObserver(()=>this.draw()).observe(canvas);canvas.addEventListener('pointerdown',e=>{let p=this.loc(e);if(!this.w||this.w<=76||this.h<=55||p[0]<57||p[0]>this.w-19||p[1]<20||p[1]>this.h-35)return;let marker=this.edit?this.markers.find(m=>Math.hypot(this.sx(m.x)-p[0],this.sy(m.y)-p[1])<14):null;this.down={p,x:[...this.x],y:[...this.y],marker};canvas.setPointerCapture(e.pointerId);});canvas.addEventListener('pointermove',e=>{if(!this.down)return;let p=this.loc(e),d=this.down;if(d.marker){this.onEdit?.(d.marker,this.ux(p[0]),this.uy(p[1]),false);}else{let dx=(p[0]-d.p[0])/(this.w-76)*(d.x[1]-d.x[0]),dy=(p[1]-d.p[1])/(this.h-55)*(d.y[1]-d.y[0]);this.x=[d.x[0]-dx,d.x[1]-dx];this.y=[d.y[0]+dy,d.y[1]+dy];if(this.x[0]<0){this.x[1]-=this.x[0];this.x[0]=0;}this.draw();this.onView?.();}});const up=()=>{if(this.down?.marker)this.onEdit?.(this.down.marker,null,null,true);this.down=null;};canvas.addEventListener('pointerup',up);canvas.addEventListener('pointercancel',up);canvas.addEventListener('wheel',e=>{let p=this.loc(e);if(!this.w||this.w<=76||this.h<=55||p[0]<57||p[0]>this.w-19||p[1]<20||p[1]>this.h-35)return;e.preventDefault();let cx=this.ux(p[0]),cy=this.uy(p[1]),z=Math.exp(Math.sign(e.deltaY)*.14),span=(this.x[1]-this.x[0])*z;if(span>=.001&&span<=1e7){const a=cx+(this.x[0]-cx)*z;this.x=[Math.max(0,a),Math.max(0,a)+span];}if(e.shiftKey&&(this.y[1]-this.y[0])*z>=.001)this.y=this.y.map(y=>cy+(y-cy)*z);this.draw();this.onView?.();},{passive:false});}
 loc(e){let r=this.canvas.getBoundingClientRect();return [e.clientX-r.left,e.clientY-r.top];}sx(x){return 57+(x-this.x[0])/(this.x[1]-this.x[0])*(this.w-76);}sy(y){return this.h-35-(y-this.y[0])/(this.y[1]-this.y[0])*(this.h-55);}ux(x){return this.x[0]+(x-57)/(this.w-76)*(this.x[1]-this.x[0]);}uy(y){return this.y[0]+(this.h-35-y)/(this.h-55)*(this.y[1]-this.y[0]);}
 draw(){const s=canvasSize(this.canvas);if(!s)return;let {g,w,h}=s;this.w=w;this.h=h;if(w<=76||h<=55)return;g.clearRect(0,0,w,h);g.font='10px system-ui';g.fillStyle='#758780';g.strokeStyle='#dce1d9';g.lineWidth=1;for(let i=0;i<=5;i++){let x=this.x[0]+i*(this.x[1]-this.x[0])/5,px=this.sx(x);g.beginPath();g.moveTo(px,20);g.lineTo(px,h-35);g.stroke();g.textAlign='center';g.fillText(Math.abs(x)<10?x.toFixed(1):x.toFixed(0),px,h-18);}for(let i=0;i<=4;i++){let y=this.y[0]+i*(this.y[1]-this.y[0])/4,py=this.sy(y);g.beginPath();g.moveTo(57,py);g.lineTo(w-19,py);g.stroke();g.textAlign='right';g.fillText(Math.abs(y)<1&&y!==0?y.toExponential(1):y.toFixed(1),50,py+3);}g.textAlign='right';g.fillText(this.xlabel,w-20,h-2);g.textAlign='left';g.fillText(this.ylabel,58,11);g.save();g.beginPath();g.rect(57,20,w-76,h-55);g.clip();if(this.band>0&&this.band<this.x[1]){g.fillStyle='#bc8d5230';g.fillRect(this.sx(Math.max(this.band,this.x[0])),20,w,h-55);}if(this.lowerBand>this.x[0]){g.fillStyle='#bc8d5230';g.fillRect(57,20,this.sx(Math.min(this.lowerBand,this.x[1]))-57,h-55);}for(const c of this.curves){g.strokeStyle=c.color||'#497e72';g.lineWidth=c.width||1.5;g.setLineDash(c.dash||[]);g.beginPath();let begun=false;for(let i=0;i<c.x.length;i++){if(c.x[i]<this.x[0]||c.x[i]>this.x[1]||!Number.isFinite(c.y[i]))continue;let x=this.sx(c.x[i]),y=this.sy(c.y[i]);if(!begun){g.moveTo(x,y);begun=true;}else g.lineTo(x,y);}g.stroke();}g.setLineDash([]);if(this.edit)for(const m of this.markers){g.fillStyle='#b56d43';g.strokeStyle='#fff';g.beginPath();g.arc(this.sx(m.x),this.sy(m.y),5,0,Math.PI*2);g.fill();g.stroke();}g.restore();g.textAlign='left';for(let i=0;i<this.curves.length;i++){const c=this.curves[i];if(!c.name)continue;g.fillStyle=c.color||'#497e72';g.fillText(c.name,68+i*95,32);}}
}
export function drawSpectrogram(c,samples,sr,n,fmax,range){const s=canvasSize(c);if(!s)return;let {g,w,h}=s;g.fillStyle='#123036';g.fillRect(0,0,w,h);if(!samples)return;const cols=Math.min(420,Math.floor(w-62)),rows=Math.min(240,Math.floor(h-40)),hop=Math.max(1,Math.floor((samples.length-n)/cols)),image=new ImageData(cols,rows);let maximum=-200,all=[];for(let x=0;x<cols;x++){let spec=spectrum(samples,n,x*hop);all.push(spec);for(let y=0;y<Math.min(spec.length,Math.floor(fmax*n/sr));y++)maximum=Math.max(maximum,spec[y]);}const palette=[[14,36,46],[32,87,105],[57,138,135],[155,182,118],[242,209,133],[255,244,212]];for(let x=0;x<cols;x++)for(let y=0;y<rows;y++){let bin=Math.min(n/2-1,Math.round((rows-1-y)/(rows-1)*fmax*n/sr)),v=Math.max(0,Math.min(1,(all[x][bin]-maximum+range)/range))*(palette.length-1),j=Math.min(palette.length-2,Math.floor(v)),t=v-j,idx=(y*cols+x)*4;for(let k=0;k<3;k++)image.data[idx+k]=palette[j][k]*(1-t)+palette[j+1][k]*t;image.data[idx+3]=255;}const tmp=document.createElement('canvas');tmp.width=cols;tmp.height=rows;tmp.getContext('2d').putImageData(image,0,0);g.drawImage(tmp,48,10,w-62,h-40);g.fillStyle='#bed2cc';g.font='10px system-ui';g.fillText('Hz',5,15);for(let i=0;i<=4;i++){g.fillText((fmax*i/4).toFixed(0),4,h-30-i*(h-40)/4);g.fillText((samples.length/sr*i/4).toFixed(1)+' s',48+i*(w-70)/4,h-10);}g.fillText('0 … −'+range+' dB',w-110,20);}
export function wav(samples,sr,float=false){const bytes=float?4:2,b=new ArrayBuffer(44+samples.length*bytes),v=new DataView(b);const str=(i,s)=>[...s].forEach((c,j)=>v.setUint8(i+j,c.charCodeAt(0)));str(0,'RIFF');v.setUint32(4,b.byteLength-8,true);str(8,'WAVE');str(12,'fmt ');v.setUint32(16,16,true);v.setUint16(20,float?3:1,true);v.setUint16(22,1,true);v.setUint32(24,sr,true);v.setUint32(28,sr*bytes,true);v.setUint16(32,bytes,true);v.setUint16(34,bytes*8,true);str(36,'data');v.setUint32(40,samples.length*bytes,true);for(let i=0;i<samples.length;i++){if(float)v.setFloat32(44+i*4,samples[i],true);else v.setInt16(44+i*2,Math.max(-1,Math.min(1,samples[i]))*32767,true);}return new Blob([b],{type:'audio/wav'});}
export function playbackGain({peak,rms},monitor){
 peak=Math.max(1e-12,peak);let requested=10**(monitor.gain/20)*monitor.level;
 if(monitor.mode==='peak')requested*=.8/peak;else if(monitor.mode==='rms')requested*=.12/Math.max(1e-12,rms);
 const gain=Math.min(requested,.9/peak);return {gain,reductionDB:requested>0?20*Math.log10(requested/Math.max(1e-30,gain)):0};
}
export function listening(samples,sr,monitor){
 let peak=1e-12,sum=0;for(const x of samples){peak=Math.max(peak,Math.abs(x));sum+=x*x;}
 const {gain}=playbackGain({peak,rms:Math.sqrt(sum/Math.max(1,samples.length))},monitor);return Float32Array.from(samples,x=>x*gain);
}
export function waveformEnvelope(samples,sr,buckets=1200){
 const x=[],y=[],step=Math.max(1,Math.ceil(samples.length/buckets));
 for(let start=0;start<samples.length;start+=step){
  const end=Math.min(samples.length,start+step);let lo=start,hi=start;
  for(let i=start+1;i<end;i++){if(samples[i]<samples[lo])lo=i;if(samples[i]>samples[hi])hi=i;}
  for(const i of lo===hi?[lo]:lo<hi?[lo,hi]:[hi,lo]){x.push(i/sr);y.push(samples[i]);}
 }
 return {x,y};
}
export function extractBand(samples,sr,selection){
 const first=Math.max(0,Math.floor(selection.t0*sr)),last=Math.min(samples.length,Math.ceil(selection.t1*sr)),count=Math.max(0,last-first);
 if(!count)return new Float32Array();const pad=Math.ceil(.03*sr),n=2**Math.ceil(Math.log2(count+2*pad)),re=new Float64Array(n),im=new Float64Array(n);
 re.set(samples.subarray(first,last),pad);fft(re,im);
 const lo=Math.max(0,selection.f0),hi=Math.min(sr/2,selection.f1),edge=Math.max(10,Math.min(100,(hi-lo)*.05));
 for(let i=0;i<n;i++){
  const f=Math.min(i,n-i)*sr/n;let a=1;
  if(f<lo-edge||f>hi+edge)a=0;else if(f<lo)a=.5*(1-Math.cos(Math.PI*(f-lo+edge)/edge));else if(f>hi)a=.5*(1+Math.cos(Math.PI*(f-hi)/edge));
  re[i]*=a;im[i]*=-a;
 }
 fft(re,im);const out=new Float32Array(count),fade=Math.min(Math.round(sr*.005),count/2);
 for(let i=0;i<count;i++)out[i]=re[i+pad]/n*Math.min(1,i/Math.max(1,fade),(count-1-i)/Math.max(1,fade));return out;
}
