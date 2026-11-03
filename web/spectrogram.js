import {spectrum,canvasSize} from './signal.js';
import {paletteRGB} from './palettes.js';

export class SpectrogramView{
 constructor(canvas,{settings,onView=()=>{},onSelection=()=>{},onSeek=()=>{},cursor=()=>null}={}){
  Object.assign(this,{canvas,settings,onView,onSelection,onSeek,cursor});this.samples=null;this.sr=44100;this.down=null;
  new ResizeObserver(()=>this.draw()).observe(canvas);
  canvas.addEventListener('pointerdown',e=>this.begin(e));canvas.addEventListener('pointermove',e=>this.move(e));
  canvas.addEventListener('pointerup',e=>this.end(e));canvas.addEventListener('pointercancel',()=>{this.down=null;});
  canvas.addEventListener('wheel',e=>this.zoom(e),{passive:false});
  let previous=null;const frame=()=>{requestAnimationFrame(frame);if(!canvas.clientWidth)return;let t=this.cursor();if(t!==previous){previous=t;this.draw();}};requestAnimationFrame(frame);
 }
 setData(samples,sr){if(samples!==this.samples||sr!==this.sr){this.samples=samples;this.sr=sr;this.stft=null;this.bitmap=null;this.bitmapKey=null;}this.draw();}
 clamp(){
  const a=this.settings(),duration=this.samples?this.samples.length/this.sr:3,nyquist=this.sr/2;
  a.tmin=Math.max(0,Math.min(duration-.001,Number(a.tmin)||0));a.tmax=Math.max(a.tmin+.001,Math.min(duration,Number(a.tmax)||duration));
  a.fmin=Math.max(a.scale==='log'?10:0,Math.min(nyquist-20,Number(a.fmin)||0));a.fmax=Math.max(a.fmin+20,Math.min(nyquist,Number(a.fmax)||10000));
  return a;
 }
 compute(){
  const a=this.clamp(),n=Number(a.fft),key=n+':'+a.window;
  if(this.stft?.key===key)return this.stft;
  const count=Math.min(1600,Math.max(2,Math.ceil(this.samples.length/(n/4)))),frames=[],duration=this.samples.length/this.sr;let peak=-280;
  for(let i=0;i<count;i++){
   const center=i*this.samples.length/(count-1),start=Math.round(center-n/2),s=spectrum(this.samples,n,start,a.window);frames.push(s);
   for(const v of s)peak=Math.max(peak,v);
  }
  return this.stft={key,frames,peak,duration,n};
 }
 point(e){const r=this.canvas.getBoundingClientRect();return [e.clientX-r.left,e.clientY-r.top];}
 time(x){const a=this.settings();return a.tmin+(x-58)/(this.w-82)*(a.tmax-a.tmin);}
 frequency(y){const a=this.settings(),t=1-(y-20)/(this.h-58);return a.scale==='log'?Math.exp(Math.log(a.fmin)+t*Math.log(a.fmax/a.fmin)):a.fmin+t*(a.fmax-a.fmin);}
 x(t){const a=this.settings();return 58+(t-a.tmin)/(a.tmax-a.tmin)*(this.w-82);}
 y(f){const a=this.settings(),v=a.scale==='log'?Math.log(Math.max(f,a.fmin)/a.fmin)/Math.log(a.fmax/a.fmin):(f-a.fmin)/(a.fmax-a.fmin);return this.h-38-v*(this.h-58);}
 begin(e){
  if(!this.samples)return;const p=this.point(e);if(p[0]<58||p[0]>this.w-24||p[1]<20||p[1]>this.h-38)return;
  this.down={p,settings:{...this.settings()},t:this.time(p[0]),f:this.frequency(p[1]),moved:false};this.canvas.setPointerCapture(e.pointerId);
 }
 move(e){
  if(!this.down)return;const p=this.point(e),d=this.down,a=this.settings();d.moved||=Math.hypot(p[0]-d.p[0],p[1]-d.p[1])>4;
  if(a.gesture==='select'){
   const t=this.time(p[0]),f=this.frequency(p[1]);a.selection={t0:Math.max(0,Math.min(d.t,t)),t1:Math.min(this.samples.length/this.sr,Math.max(d.t,t)),f0:Math.max(0,Math.min(d.f,f)),f1:Math.min(this.sr/2,Math.max(d.f,f))};
  }else{
   const dt=(p[0]-d.p[0])/(this.w-82)*(d.settings.tmax-d.settings.tmin),width=d.settings.tmax-d.settings.tmin;
   a.tmin=Math.max(0,Math.min(this.samples.length/this.sr-width,d.settings.tmin-dt));a.tmax=a.tmin+width;
   const dy=(p[1]-d.p[1])/(this.h-58);
   if(a.scale==='log'){const ratio=(d.settings.fmax/d.settings.fmin)**dy;a.fmin=d.settings.fmin*ratio;a.fmax=d.settings.fmax*ratio;}
   else{const df=dy*(d.settings.fmax-d.settings.fmin);a.fmin=d.settings.fmin+df;a.fmax=d.settings.fmax+df;}
  }
  this.clamp();this.draw();this.onView();
 }
 end(e){
  if(!this.down)return;const d=this.down;this.down=null;
  if(this.settings().gesture==='select'&&d.moved)this.onSelection(this.settings().selection);
  else if(!d.moved)this.onSeek(Math.max(0,Math.min(this.samples.length/this.sr,this.time(this.point(e)[0]))));
 }
 zoom(e){
  if(!this.samples)return;const p=this.point(e);if(p[0]<58||p[0]>this.w-24||p[1]<20||p[1]>this.h-38)return;e.preventDefault();const a=this.settings(),z=Math.exp(Math.sign(e.deltaY)*.15);
  if(e.shiftKey){const f=this.frequency(p[1]);if(a.scale==='log'){a.fmin=f*(a.fmin/f)**z;a.fmax=f*(a.fmax/f)**z;}else{a.fmin=f+(a.fmin-f)*z;a.fmax=f+(a.fmax-f)*z;}}
  else{const t=this.time(p[0]);a.tmin=t+(a.tmin-t)*z;a.tmax=t+(a.tmax-t)*z;}
  this.clamp();this.draw();this.onView();
 }
 draw(){
  const box=canvasSize(this.canvas);if(!box)return;const {g,w,h}=box;this.w=w;this.h=h;g.fillStyle='#112b33';g.fillRect(0,0,w,h);
  if(!this.samples){g.fillStyle='#b2c9c3';g.font='12px system-ui';g.fillText('GMT · Spectrogramme / Spectrogram',58,40);return;}
  if(w<=82||h<=58)return;const a=this.clamp(),data=this.compute(),cols=Math.max(2,Math.min(760,Math.round(w-82))),rows=Math.max(2,Math.min(440,Math.round(h-58)));
  const key=JSON.stringify([data.key,cols,rows,a.tmin,a.tmax,a.fmin,a.fmax,a.scale,a.range,a.palette,a.reference,a.ceiling]);
  if(this.bitmapKey!==key){
   const bitmap=document.createElement('canvas');bitmap.width=cols;bitmap.height=rows;const image=new ImageData(cols,rows),ceiling=a.reference==='peak'?data.peak:Number(a.ceiling),lut=Array.from({length:256},(_,i)=>paletteRGB(a.palette,i/255));
   for(let x=0;x<cols;x++){
    const t=a.tmin+x/(cols-1)*(a.tmax-a.tmin),frame=data.frames[Math.max(0,Math.min(data.frames.length-1,Math.round(t/data.duration*(data.frames.length-1))))];
    for(let y=0;y<rows;y++){
     const v=1-y/(rows-1),f=a.scale==='log'?a.fmin*(a.fmax/a.fmin)**v:a.fmin+v*(a.fmax-a.fmin),bin=Math.max(0,Math.min(frame.length-1,Math.round(f*data.n/this.sr)));
     const value=frame[bin],c=lut[Math.max(0,Math.min(255,Math.round((value-ceiling+Number(a.range))/Number(a.range)*255)))],i=(y*cols+x)*4;
     image.data[i]=c[0];image.data[i+1]=c[1];image.data[i+2]=c[2];image.data[i+3]=255;
    }
   }
   bitmap.getContext('2d').putImageData(image,0,0);this.bitmap=bitmap;this.bitmapKey=key;
  }
  g.drawImage(this.bitmap,58,20,w-82,h-58);g.fillStyle='#c6d8d0';g.font='11px system-ui';
  for(let i=0;i<=5;i++){const x=58+i*(w-82)/5,t=a.tmin+i*(a.tmax-a.tmin)/5;g.textAlign='center';g.fillText(t.toFixed(t<1?2:1),x,h-17);}
  for(let i=0;i<=5;i++){const f=a.scale==='log'?a.fmin*(a.fmax/a.fmin)**(i/5):a.fmin+i*(a.fmax-a.fmin)/5;g.textAlign='right';g.fillText(f>=1000?(f/1000).toPrecision(2)+'k':f.toFixed(0),51,h-35-i*(h-58)/5);}
  g.textAlign='left';g.fillText('Hz',6,14);g.textAlign='right';g.fillText('s',w-5,h-17);g.fillText(a.reference==='absolute'?`${Number(a.ceiling)} … ${Number(a.ceiling)-Number(a.range)} dB re 1 SI`:`0 … −${a.range} dB`,w-29,14);
  g.save();g.beginPath();g.rect(58,20,w-82,h-58);g.clip();
  if(a.selection){const s=a.selection,x=this.x(s.t0),y=this.y(s.f1),dx=this.x(s.t1)-x,dy=this.y(s.f0)-y;g.fillStyle='#f6ead125';g.strokeStyle='#fff2bc';g.lineWidth=1.5;g.setLineDash([5,3]);g.fillRect(x,y,dx,dy);g.strokeRect(x,y,dx,dy);g.setLineDash([]);}
  const t=this.cursor();if(t!==null){g.strokeStyle='#fff6dc';g.lineWidth=1.3;g.beginPath();g.moveTo(this.x(t),20);g.lineTo(this.x(t),h-38);g.stroke();}g.restore();
 }
}
