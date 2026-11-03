import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
const code=fs.readFileSync(new URL('../web/app.js',import.meta.url),'utf8');
const elements={};const $=id=>elements[id]??={classList:{toggle(){}},setAttribute(k,v){this[k]=v}};
const context=vm.createContext({$,audioBusy:false,tr:(fr,en)=>fr,toast(){}});
vm.runInContext(code.slice(code.indexOf('function liveStatus('),code.indexOf('\nconst live=')),context);
for(const state of ['missing','dirty','preparing','error']){context.liveStatus(state);assert.equal($('strum').disabled,true);assert.equal($('repertoirePlay').disabled,true);assert.equal($('bodyboard')['aria-disabled'],'true');}
context.liveStatus('error',new Error('Network'));assert.equal($('prepareLive').disabled,false);
context.liveStatus('ready');assert.equal($('strum').disabled,false);assert.equal($('preparationTitle').textContent,'Prêt à jouer');
context.audioBusy=true;context.liveStatus('ready');assert.equal($('strum').disabled,true);assert.equal($('preparationProgress').hidden,false);
context.audioBusy=false;context.tr=(fr,en)=>en;context.liveStatus('preparing');assert.equal($('preparationTitle').textContent,'Preparation in progress — please wait');
let resolve,plays=0;
Object.assign(context,{audioBusy:false,isReady:()=>true,stopAudio:()=>{context.audioToken++},audioToken:0,modelEpoch:1,job:'test',performance,clone:structuredClone,project:{hole:{},strings:{},excitation:{},monitor:{},analysis:{}},selectedString:0,audioCache:new Map(),ensureAudio:async()=>{},api:()=>new Promise(r=>resolve=r),responseSignature:p=>JSON.stringify(p||context.project),status(){},decode:()=>new Float32Array(1),renderAudio(){},playTake:async()=>{plays++},setTimeout,animateString(){},playing:false});
vm.runInContext(code.slice(code.indexOf('async function pluck('),code.indexOf('\nasync function ensureAudio')),context);
const pending=context.pluck([{string:0,time:0}],true);await new Promise(setImmediate);context.stopAudio();resolve({});await pending;assert.equal(plays,0);assert.equal(context.audioBusy,false);
const pending2=context.pluck([{string:0,time:0}],true);await new Promise(setImmediate);context.project.excitation.force=2;resolve({});await pending2;assert.equal(plays,0);assert.equal(context.audioBusy,false);
console.log('PASS: FR/EN preparation status, input locking, error retry, stop cancellation and stale synthesis rejection.');
