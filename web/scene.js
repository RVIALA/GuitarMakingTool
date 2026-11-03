import * as T from './vendor/three.module.js';
import {FreeOrbitControls} from './free-orbit.js';
import {paletteRGB} from './palettes.js';
const colors={top:0xd8b27a,back:0x78533c,ribs:0x91664a,braces:0xd09a59,bridge:0x3d3029,air:0x79b7cb};
export class GuitarScene{
 constructor(host,onSelect=()=>{}){this.host=host;this.onSelect=onSelect;this.scene=new T.Scene();this.scene.background=new T.Color(0xe7ece5);this.camera=new T.PerspectiveCamera(38,1,.001,20);this.camera.up.set(0,1,0);this.renderer=new T.WebGLRenderer({antialias:true,alpha:false,preserveDrawingBuffer:true});this.renderer.setPixelRatio(Math.min(2,devicePixelRatio));this.renderer.outputColorSpace=T.SRGBColorSpace;this.renderer.setClearColor(0xe7ece5);host.append(this.renderer.domElement);this.controls=new FreeOrbitControls(this.camera,this.renderer.domElement);this.controls.enableDamping=true;this.controls.target.set(0,.25,-.04);this.scene.add(new T.HemisphereLight(0xffffff,0x6b7967,2.3));let light=new T.DirectionalLight(0xfff2d5,3);light.position.set(-.5,.5,1);this.scene.add(light);let rim=new T.DirectionalLight(0xbedcfa,1.5);rim.position.set(.5,-.3,.1);this.scene.add(rim);this.group=new T.Group();this.scene.add(this.group);this.airGroup=new T.Group();this.scene.add(this.airGroup);this.grainGroup=new T.Group();this.scene.add(this.grainGroup);this.portGroup=new T.Group();this.scene.add(this.portGroup);this.mode=null;this.animating=false;this.options={xray:true,grain:false,wire:false,air:false,explode:0,fringes:true,component:'norm',palette:'viridis',levels:0,interpolation:3,showTop:true,showBack:true,showRibs:true,showBraces:true,showPorts:true};this.reset();this.resize=new ResizeObserver(()=>this.size());this.resize.observe(host);this.size();let down=null;this.renderer.domElement.addEventListener('pointerdown',e=>down=[e.clientX,e.clientY]);this.renderer.domElement.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>4)return;const r=this.renderer.domElement.getBoundingClientRect(),ray=new T.Raycaster();ray.setFromCamera(new T.Vector2((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1),this.camera);let hit=ray.intersectObjects(this.group.children).find(h=>h.object.userData.id);if(hit)this.onSelect(hit.object.userData.id);});let last=0;const frame=t=>{requestAnimationFrame(frame);if(!host.clientWidth)return;this.controls.update();if(this.animating&&this.mode&&t-last>32){last=t;this.deform(Math.sin(t*.004));}this.renderer.render(this.scene,this.camera);};requestAnimationFrame(frame);}
 size(){if(!this.host.clientWidth)return;const w=this.host.clientWidth,h=this.host.clientHeight;this.renderer.setSize(w,h,false);this.camera.aspect=w/h;this.camera.updateProjectionMatrix();}
 reset(){this.camera.up.set(0,1,0);this.camera.position.set(.53,-.18,.70);this.controls?.target.set(0,.25,-.04);this.controls?.update();}
 clear(){for(const group of [this.group,this.airGroup,this.grainGroup,this.portGroup]){for(const child of [...group.children]){group.remove(child);child.geometry?.dispose();child.material?.map?.dispose();child.material?.uniforms?.palette?.value?.dispose();if(child.material){if(Array.isArray(child.material))child.material.forEach(m=>m.dispose());else child.material.dispose();}}}this.mode=null;}
 material(part){return new T.MeshStandardMaterial({color:colors[part]||colors.top,roughness:.7,metalness:.03,side:T.DoubleSide,transparent:true});}
 shape(points,holes=[]){let s=new T.Shape(points.slice(0,-1).map(v=>new T.Vector2(...v)));for(const h of holes)s.holes.push(new T.Path(h.slice(0,-1).map(v=>new T.Vector2(...v))));return s;}
 warp(g,p){let a=g.attributes.position;for(let i=0;i<a.count;i++){let x=a.getX(i),y=a.getY(i),z=a.getZ(i),t=Math.max(0,Math.min(1,(z+p.body.depth*.001)/(p.body.depth*.001))),common=Math.max(0,1-(2*x/(p.body.width*.001))**2)*Math.max(0,Math.sin(Math.PI*y/(p.body.length*.001)))**1.2;a.setZ(i,z+(p.body.archTop*.001*t-p.body.archBack*.001*(1-t))*common);}a.needsUpdate=true;g.computeVertexNormals();}
 setDesign(p,preview){this.clear();const add=(shape,z,height,part,side,id)=>{let g=new T.ExtrudeGeometry(shape,{depth:height,bevelEnabled:false,curveSegments:16,steps:1});g.translate(0,0,z);this.warp(g,p);let m=new T.Mesh(g,this.material(part));m.userData={part,side,id};this.group.add(m);};add(this.shape(preview.outline,preview.holes),0,p.body.top*.001,'top');if(p.body.backEnabled)add(this.shape(preview.outline),-(p.body.depth+p.body.back)*.001,p.body.back*.001,'back');if(p.body.ribsEnabled)add(this.shape(preview.outline,[preview.inner]),-p.body.depth*.001,p.body.depth*.001,'ribs');for(const b of preview.braceShapes||[]){add(this.shape(b.outline,b.holes),b.side==='top'?-b.height:-p.body.depth*.001,b.height,'braces',b.side,b.id);}
 const b=p.bridge,x=b.x*.001,y=b.y*.001,w=b.width*.0005,d=b.depth*.0005,pts=[[x-w,y-d],[x+w,y-d],[x+w,y+d],[x-w,y+d],[x-w,y-d]];if(b.kind==='floating'){for(let sx of [-.35,.35]){let cx=x+sx*b.width*.001,fw=.009;add(this.shape([[cx-fw,y-d],[cx+fw,y-d],[cx+fw,y+d],[cx-fw,y+d],[cx-fw,y-d]]),p.body.top*.001,b.height*.0007,'bridge');}add(this.shape(pts),p.body.top*.001+b.height*.00065,b.height*.00035,'bridge');}else add(this.shape(pts),p.body.top*.001,b.height*.001,'bridge');
 const lines=[],line=(a,b)=>lines.push(...a,...b),grain=p.materials.top.grain*Math.PI/180;for(let y0=.08;y0<p.body.length*.001-.04;y0+=.045)for(let x0 of [-.06,0,.06])line([x0,y0,p.body.top*.001+.001],[x0+.022*Math.sin(grain),y0+.022*Math.cos(grain),p.body.top*.001+.001]);for(let i=0;i<preview.outline.length-1;i+=4){let a=preview.outline[i],b=preview.outline[i+1],d=Math.hypot(b[0]-a[0],b[1]-a[1]);if(d)line([a[0],a[1],-.04],[a[0]+.02*(b[0]-a[0])/d,a[1]+.02*(b[1]-a[1])/d,-.04]);}for(let b of p.braces){let dx=b.b[0]-b.a[0],dy=b.b[1]-b.a[1],d=Math.hypot(dx,dy),x=(b.a[0]+b.b[0])*.0005,y=(b.a[1]+b.b[1])*.0005,z=b.part==='top'?-b.height*.001:-p.body.depth*.001+b.height*.001;if(d)line([x,y,z],[x+.02*dx/d,y+.02*dy/d,z]);}let lg=new T.BufferGeometry();lg.setAttribute('position',new T.Float32BufferAttribute(lines,3));this.warp(lg,p);this.grainGroup.add(new T.LineSegments(lg,new T.LineBasicMaterial({color:0x146b4d})));this.apply();}
 fieldMaterial(){
  const bytes=new Uint8Array(256*4);
  for(let i=0;i<256;i++){let c=paletteRGB(this.options.palette,i/255);for(let j=0;j<3;j++)bytes[i*4+j]=c[j];bytes[i*4+3]=255;}
  const texture=new T.DataTexture(bytes,256,1,T.RGBAFormat);texture.colorSpace=T.SRGBColorSpace;texture.minFilter=texture.magFilter=T.LinearFilter;texture.needsUpdate=true;
  return new T.ShaderMaterial({side:T.DoubleSide,transparent:true,uniforms:{palette:{value:texture},levels:{value:Number(this.options.levels)},alpha:{value:1}},
   vertexShader:`attribute float field; varying float scalar; void main(){scalar=field;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
   fragmentShader:`uniform sampler2D palette;uniform float levels;uniform float alpha;varying float scalar;void main(){float v=clamp(scalar,0.0,1.0);if(levels>1.0)v=min(1.0,floor(v*levels)/(levels-1.0));gl_FragColor=vec4(texture2D(palette,vec2(v,0.5)).rgb,alpha);
#include <colorspace_fragment>
}`});
 }
 setMesh(data){
  this.clear();this.meshData=data;this.rawMode=null;
  const groups={};const useQuadratic=!!data.faces6;
  (data.faces6||data.triangles).forEach((tri,i)=>{const group=(useQuadratic?data.faceParts:data.parts)[i];(groups[group]??=[]).push(tri);});
  const div=useQuadratic?Number(this.options.interpolation):1;
  for(const [key,faces] of Object.entries(groups)){
   const base=[],indices=[],weights=[],triangles=[];
   for(const face of faces){
    const offset=base.length/3,lookup=new Map();
    for(let i=0;i<=div;i++)for(let j=0;j<=div-i;j++){
     const l=[1-(i+j)/div,i/div,j/div],N=useQuadratic?[...l.map(x=>x*(2*x-1)),4*l[0]*l[1],4*l[1]*l[2],4*l[2]*l[0]]:l;
     lookup.set(i+','+j,base.length/3-offset);
     for(let k=0;k<3;k++)base.push(N.reduce((a,w,n)=>a+w*data.points[face[n]][k],0));
     for(let n=0;n<N.length;n++){indices.push(face[n]);weights.push(N[n]);}
    }
    const at=(i,j)=>offset+lookup.get(i+','+j);
    for(let i=0;i<div;i++)for(let j=0;j<div-i;j++){
     triangles.push(at(i,j),at(i+1,j),at(i,j+1));
     if(j<div-i-1)triangles.push(at(i+1,j),at(i+1,j+1),at(i,j+1));
    }
   }
   const positions=new Float32Array(base),g=new T.BufferGeometry();g.setAttribute('position',new T.BufferAttribute(positions.slice(),3));g.setAttribute('field',new T.BufferAttribute(new Float32Array(base.length/3),1));g.setIndex(triangles);g.computeVertexNormals();
   const part=data.groups[key],m=new T.Mesh(g,this.material(part.part));m.userData={...part,base:positions,indices:new Int32Array(indices),weights:new Float32Array(weights),stride:useQuadratic?6:3};this.group.add(m);
  }
  if(data.air){const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(data.air.points.flat(),3));g.setIndex(data.air.triangles.flat());g.computeVertexNormals();this.airGroup.add(new T.Mesh(g,new T.MeshBasicMaterial({color:colors.air,transparent:true,opacity:.14,side:T.DoubleSide,wireframe:true})));}
  if(data.grain?.length){const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(data.grain.flatMap(a=>[...a[0],...a[1]]),3));this.grainGroup.add(new T.LineSegments(g,new T.LineBasicMaterial({color:0x146b4d})));}
  this.addPorts(data.ports||[]);this.apply();
 }
 addPorts(ports){
  const ink=['#497b70','#b36d43','#4e7b9e','#9975a5','#85914e','#a45862'];
  ports.forEach((p,i)=>{
   const m=new T.Mesh(new T.SphereGeometry(.0027,12,8),new T.MeshBasicMaterial({color:ink[i],depthTest:false}));m.position.set(p[0],p[1],p[2]+.001);m.renderOrder=10;m.userData={id:'port:'+i};this.portGroup.add(m);
   const canvas=document.createElement('canvas');canvas.width=canvas.height=64;const g=canvas.getContext('2d');g.fillStyle=ink[i];g.beginPath();g.arc(32,32,26,0,Math.PI*2);g.fill();g.fillStyle='white';g.font='bold 33px system-ui';g.textAlign='center';g.textBaseline='middle';g.fillText(String(i+1),32,33);
   const texture=new T.CanvasTexture(canvas),sprite=new T.Sprite(new T.SpriteMaterial({map:texture,depthTest:false}));sprite.scale.set(.013,.013,1);sprite.position.set(p[0],p[1]+.019,p[2]+.003);sprite.renderOrder=11;this.portGroup.add(sprite);
  });
 }
 setMode(displacements){
  this.rawMode=displacements;let max=1e-12;for(const v of displacements)max=Math.max(max,Math.hypot(...v));
  this.mode=Float32Array.from(displacements.flat(),x=>x/max);
  for(const m of this.group.children){const u=m.userData;if(!u.indices)continue;u.modal=new Float32Array(u.base.length);
   for(let v=0;v<u.base.length/3;v++)for(let n=0;n<u.stride;n++){const a=v*u.stride+n,id=u.indices[a],w=u.weights[a];for(let k=0;k<3;k++)u.modal[v*3+k]+=w*this.mode[id*3+k];}
  }
  this.updateFields();this.deform(1);this.apply();
 }
 updateFields(){
  if(!this.mode)return;let maximum=1e-12;const comp=this.options.component,axis={x:0,y:1,z:2}[comp];
  for(const m of this.group.children){const d=m.userData.modal;if(!d)continue;for(let i=0;i<d.length;i+=3)maximum=Math.max(maximum,comp==='norm'?Math.hypot(d[i],d[i+1],d[i+2]):Math.abs(d[i+axis]));}
  for(const m of this.group.children){const d=m.userData.modal;if(!d)continue;const a=m.geometry.attributes.field;
   for(let i=0;i<a.count;i++){const v=comp==='norm'?Math.hypot(d[i*3],d[i*3+1],d[i*3+2])/maximum:(d[i*3+axis]/maximum+1)*.5;a.array[i]=v;}a.needsUpdate=true;
  }
 }
 deform(phase){
  if(!this.mode)return;
  for(const m of this.group.children){const u=m.userData;if(!u.modal)continue;const a=m.geometry.attributes.position;
   for(let j=0;j<a.array.length;j++)a.array[j]=u.base[j]+u.modal[j]*(this.amplitude??.006)*phase;
   a.needsUpdate=true;if(!m.material.isShaderMaterial)m.geometry.computeVertexNormals();
  }
 }
 apply(options={}){
  const old={...this.options};Object.assign(this.options,options);
  if(this.meshData&&old.interpolation!==this.options.interpolation){const mode=this.rawMode;this.setMesh(this.meshData);if(mode)this.setMode(mode);return;}
  if(old.component!==this.options.component)this.updateFields();
  for(const m of this.group.children){const p=m.userData.part,side=m.userData.side,field=!!this.mode&&this.options.fringes;
   if(field!==!!m.material.isShaderMaterial||field&&old.palette!==this.options.palette){m.material.uniforms?.palette?.value?.dispose();m.material.dispose();m.material=field?this.fieldMaterial():this.material(p);}
   const opacity=(this.options.opacity??1)*(this.options.xray&&(p==='top'||p==='back')?.2:1);m.material.opacity=opacity;if(m.material.uniforms){m.material.uniforms.alpha.value=opacity;m.material.uniforms.levels.value=Number(this.options.levels);}
   m.material.wireframe=!!this.options.wire;m.material.depthWrite=opacity>.5;m.visible=(p==='top'?this.options.showTop:p==='back'?this.options.showBack:p==='ribs'?this.options.showRibs:p==='braces'?this.options.showBraces:true);
   m.position.z=this.options.explode*.001*((p==='back'||side==='back')?-1:(p==='top'||p==='bridge'||side==='top')?1:0);
  }
  this.airGroup.visible=!!this.options.air;this.grainGroup.visible=!!this.options.grain;this.portGroup.visible=!!this.options.showPorts;this.portGroup.position.z=this.options.explode*.001;
 }
}
