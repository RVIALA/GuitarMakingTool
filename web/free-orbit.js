/* Romain VIALA — unrestricted trackball orbit; no fixed world-up direction. */
import * as T from './vendor/three.module.js';
export class FreeOrbitControls{
 constructor(camera,element){
  this.object=camera;this.domElement=element;this.target=new T.Vector3();this.enabled=true;this.enableRotate=true;this.enablePan=true;this.enableZoom=true;this.minDistance=camera.near*4;this.maxDistance=camera.far*.45;this.mouseButtons={LEFT:T.MOUSE.ROTATE,MIDDLE:T.MOUSE.DOLLY,RIGHT:T.MOUSE.PAN};this.touches={ONE:T.TOUCH.ROTATE,TWO:T.TOUCH.DOLLY_PAN};this.pointers=new Map();element.style.touchAction='none';this.handlers={};
  this.bind('contextmenu',e=>e.preventDefault());this.bind('wheel',e=>{if(!this.enabled||!this.enableZoom)return;e.preventDefault();this.zoom(Math.exp(Math.max(-200,Math.min(200,e.deltaY))*.0015));},{passive:false});
  this.bind('pointerdown',e=>{if(!this.enabled)return;e.preventDefault();element.setPointerCapture(e.pointerId);this.pointers.set(e.pointerId,{x:e.clientX,y:e.clientY,button:e.button,type:e.pointerType});});
  this.bind('pointermove',e=>this.move(e));
  for(const type of ['pointerup','pointercancel','lostpointercapture'])this.bind(type,e=>this.pointers.delete(e.pointerId));
 }
 bind(type,fn,options){this.handlers[type]=fn;this.domElement.addEventListener(type,fn,options);}
 ball(x,y){const r=this.domElement.getBoundingClientRect(),s=Math.max(1,Math.min(r.width,r.height)),v=new T.Vector3((2*(x-r.left)-r.width)/s,(r.height-2*(y-r.top))/s,0),d=v.lengthSq();v.z=d<=.5?Math.sqrt(1-d):.5/Math.sqrt(d);return v.normalize();}
 orbit(a,b){if(!this.enableRotate)return;this.object.updateMatrixWorld();const q=new T.Quaternion().setFromUnitVectors(this.ball(b.x,b.y).applyQuaternion(this.object.quaternion),this.ball(a.x,a.y).applyQuaternion(this.object.quaternion));this.rotate(q);}
 rotate(q){this.object.position.sub(this.target).applyQuaternion(q).add(this.target);this.object.up.applyQuaternion(q).normalize();this.update();}
 pan(dx,dy){if(!this.enablePan)return;const c=this.object,r=this.domElement.getBoundingClientRect(),scale=2*c.position.distanceTo(this.target)*Math.tan(c.fov*Math.PI/360)/Math.max(1,r.height),v=new T.Vector3(-dx*scale,dy*scale,0).applyQuaternion(c.quaternion);c.position.add(v);this.target.add(v);this.update();}
 zoom(factor){if(!this.enableZoom)return;const v=this.object.position.clone().sub(this.target),d=Math.max(this.minDistance,Math.min(this.maxDistance,v.length()*factor));v.setLength(d);this.object.position.copy(this.target).add(v);this.update();}
 move(e){const old=this.pointers.get(e.pointerId);if(!old||!this.enabled)return;const next={...old,x:e.clientX,y:e.clientY},other=[...this.pointers.entries()].find(([id])=>id!==e.pointerId)?.[1];
  if(other){const d0=Math.hypot(old.x-other.x,old.y-other.y),d1=Math.hypot(next.x-other.x,next.y-other.y);if(d0>2&&d1>2)this.zoom(d0/d1);this.pan((next.x-old.x)/2,(next.y-old.y)/2);if(this.enableRotate){let a=Math.atan2(old.y-other.y,old.x-other.x),b=Math.atan2(next.y-other.y,next.x-other.x),axis=this.object.position.clone().sub(this.target).normalize();this.rotate(new T.Quaternion().setFromAxisAngle(axis,a-b));}}
  else{const action=old.type==='touch'?(this.touches.ONE===T.TOUCH.PAN?T.MOUSE.PAN:T.MOUSE.ROTATE):this.mouseButtons[['LEFT','MIDDLE','RIGHT'][old.button]];if(action===T.MOUSE.PAN||e.shiftKey)this.pan(next.x-old.x,next.y-old.y);else if(action===T.MOUSE.DOLLY)this.zoom(Math.exp((next.y-old.y)*.01));else this.orbit(old,next);}
  this.pointers.set(e.pointerId,next);
 }
 update(){this.object.lookAt(this.target);this.object.updateMatrixWorld();return false;}
 dispose(){for(const [type,fn] of Object.entries(this.handlers))this.domElement.removeEventListener(type,fn);this.pointers.clear();}
}
