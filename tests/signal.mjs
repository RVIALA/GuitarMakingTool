import assert from 'node:assert/strict';
import {fft,spectrum,wav,listening} from '../web/signal.js';
let re=new Float64Array(1024),im=new Float64Array(1024);for(let i=0;i<1024;i++)re[i]=Math.cos(2*Math.PI*64*i/1024);fft(re,im);assert.ok(Math.abs(re[64]-512)<1e-8);assert.ok(Math.abs(re[960]-512)<1e-8);
let samples=Float32Array.from({length:8192},(_,i)=>.5*Math.sin(2*Math.PI*256*i/8192));let spec=spectrum(samples,8192);let maximum=spec.reduce((i,v,j,a)=>v>a[i]?j:i,0);assert.equal(maximum,256);assert.ok(Math.abs(spec[256]+6.0206)<.01);
for(let float of [false,true]){let b=await wav(samples,22050,float).arrayBuffer(),d=new DataView(b);assert.equal(d.getUint16(20,true),float?3:1);assert.equal(d.getUint32(40,true),samples.length*(float?4:2));}
for(let mode of ['peak','rms','fixed']){let out=listening(samples,22050,{gain:60,level:1,mode},3000);assert.ok(Math.max(...out.map(Math.abs))<=.9000001);assert.ok(out.every(Number.isFinite));}
let outA=listening(samples,22050,{gain:0,level:1,mode:'fixed'},3000),outB=listening(Float32Array.from(samples,x=>x*.5),22050,{gain:0,level:1,mode:'fixed'},3000);assert.ok(Math.abs(outA[200]/outB[200]-2)<1e-6);
console.log('PASS: FFT sinus, spectral amplitude, PCM16/float32 headers, no-clipping global gain, fixed-gain level comparison.');
const {extractBand}=await import('../web/signal.js');
let bright=Float32Array.from({length:44100},(_,i)=>.4*Math.sin(2*Math.PI*400*i/44100)+.2*Math.sin(2*Math.PI*6000*i/44100));
let preserved=listening(bright,44100,{gain:0,level:1,mode:'fixed'},800);let error=0;for(let i=0;i<bright.length;i++)error=Math.max(error,Math.abs(bright[i]-preserved[i]));assert.ok(error<1e-7,'Listening must not low-pass at the last FE mode.');
let selected=extractBand(bright,44100,{t0:.2,t1:.6,f0:5000,f1:7000});assert.ok(Math.abs(selected.length-17640)<=1);let ss=spectrum(selected,8192,2000),nearest=f=>Math.round(f*8192/44100);assert.ok(ss[nearest(6000)]-ss[nearest(400)]>50,'Selection playback must isolate the selected frequency band.');
console.log('PASS: high overtones retained independently of the FE band; time-frequency selection isolates its band.');

const {waveformEnvelope,playbackGain}=await import('../web/signal.js');
const dc=spectrum(Float32Array.from({length:8192},()=>.5),8192);assert.ok(Math.abs(dc[0]+6.0206)<.001);
assert.throws(()=>fft(new Float64Array(12345),new Float64Array(12345)),RangeError);
const impulse=new Float32Array(20000);impulse[157]=1;impulse[18000]=-2;const envelope=waveformEnvelope(impulse,44100,100);assert.equal(Math.max(...envelope.y),1);assert.equal(Math.min(...envelope.y),-2);
const protectedGain=playbackGain({peak:4,rms:1},{gain:20,level:1,mode:'fixed'});assert.ok(Math.abs(protectedGain.gain*4-.9)<1e-12);assert.ok(protectedGain.reductionDB>30);
console.log('PASS: DC calibration, invalid FFT rejection, waveform extrema and reported headroom reduction.');
