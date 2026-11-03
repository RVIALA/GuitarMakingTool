import assert from 'node:assert/strict';
import {repertoire,phraseEvents} from '../web/repertoire.js';
import {wav,listening} from '../web/signal.js';
const strings=[40,45,50,55,59,64].map(midi=>({midi,muted:false}));
for(const piece of repertoire)for(const tempo of [60,100,180]){
 const events=phraseEvents(piece,tempo,strings);
 assert.ok(events.length<=40);
 for(const e of events){assert.ok(e.time<=16);assert.ok(e.fret>=0&&e.fret<=24);assert.ok(e.duration>0);}
 if(piece.notes)events.forEach((e,i)=>assert.equal(strings[e.string].midi+e.fret,piece.notes[i][0]));
 const fast=phraseEvents(piece,tempo*1.1<=180?tempo*1.1:tempo,strings);assert.ok(fast.at(-1).time<=events.at(-1).time);
}
assert.throws(()=>phraseEvents(repertoire[0],0,strings));
assert.throws(()=>phraseEvents(repertoire[0],100,strings.map(s=>({...s,muted:true}))));
const monitor={mode:'peak',gain:0,level:.6},samples=Float32Array.from({length:1000},(_,i)=>Math.sin(i*.1));
const bytes=wav(listening(samples,44100,monitor),44100);assert.ok(bytes.size>1000);
console.log('PASS: all five phrases, tempo limits, written pitches, unavailable notes and WAV encoding.');
