import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {CS_COLORS,CS_NAMES,DEFECTS,FIELDS} from './inspect/catalog.js';
import {densify,planePoint} from './inspect/geometry.js';
import * as inspectionStore from './inspect/store.js';
import {elementSummary} from './inspect/summary.js';
import {planTerrain} from './terrain.js';

// Display models store positions as 16-bit integers (KHR_mesh_quantization). Placement, analysis deformation
// and section edits need plain float positions, so they are expanded once on load.
function floatPositions(geometry){const a=geometry.attributes.position;if(a.array instanceof Float32Array&&!a.isInterleavedBufferAttribute)return geometry;
  const out=new Float32Array(a.count*3);for(let i=0;i<a.count;i++){out[i*3]=a.getX(i);out[i*3+1]=a.getY(i);out[i*3+2]=a.getZ(i);}
  geometry.setAttribute('position',new THREE.BufferAttribute(out,3));return geometry;}

// Surface response by what a component is made of. Colours stay the model's own; only roughness/metalness change.
const METAL=/steel|w\d+\s*[x×]|hp\s?\d+|c\d+\s*[x×]|bolt|nut\b|washer|weld|plate|angle|channel|stiffener|splice|gusset|lacing|chord|truss|casing|guardrail|railing|pipe rail|bracket|anchor/i;
const METAL_LAYERS=new Set(['steel','truss_chords','truss_web','gussets','lacing','bracing','fasteners','casing','repairs']);
function surfaceFor(p){
  if(['road_surface','wearing'].includes(p.layer))return {roughness:.93,metalness:0};
  if(p.layer==='bearings'&&/elastomer|pad|neoprene/i.test(p.name))return {roughness:.95,metalness:0};
  if(METAL_LAYERS.has(p.layer)||METAL.test(p.name))return {roughness:.48,metalness:.55};
  return {roughness:.88,metalness:0};
}

class BridgeViewer {
  constructor(host, onSelect, onChange) {
    this.host=host;this.onSelect=onSelect;this.onChange=onChange;this.meshes=new Map();this.textures=new Set();this.selected=new Set();this.hidden=new Set();this.isolated=null;this.loadId=0;
    this.scene=new THREE.Scene();this.scene.background=new THREE.Color('#1d2124');
    this.camera=new THREE.PerspectiveCamera(38,1,.01,10000);
    this.renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});this.renderer.setPixelRatio(Math.min(devicePixelRatio,2));
    // No synchronous shader-error queries: they make the page wait for every shader link (seconds on software GPUs).
    this.renderer.debug.checkShaderErrors=false;
    this.renderer.localClippingEnabled=true;this.renderer.outputColorSpace=THREE.SRGBColorSpace;this.renderer.toneMapping=THREE.ACESFilmicToneMapping;this.renderer.toneMappingExposure=1.15;
    host.append(this.renderer.domElement);this.renderer.domElement.setAttribute('aria-label','3D bridge model. Components can also be selected in the tree.');
    this.controls=new OrbitControls(this.camera,this.renderer.domElement);this.controls.addEventListener('change',()=>this.render());
    // Software WebGL (remote desktops, VMs, no GPU driver) needs seconds per frame for image-based light and shadow
    // maps, so it gets plain lights instead.
    const gl=this.renderer.getContext(),info=gl.getExtension('WEBGL_debug_renderer_info');
    this.lite=/swiftshader|llvmpipe|softpipe|software|basic render|warp/i.test(gl.getParameter(info?info.UNMASKED_RENDERER_WEBGL:gl.RENDERER)||'');
    // Image-based light from a neutral room gives metal and concrete their sheen; one key light casts soft shadows.
    if(!this.lite){const pmrem=new THREE.PMREMGenerator(this.renderer);this.scene.environment=pmrem.fromScene(new RoomEnvironment(),.04).texture;pmrem.dispose();this.scene.environmentIntensity=.5;}
    this.renderer.shadowMap.enabled=!this.lite;this.renderer.shadowMap.type=THREE.PCFSoftShadowMap;
    this.scene.add(new THREE.HemisphereLight(0xffffff,0x6f7a6a,this.lite?1.9:1.1));
    const key=this.key=new THREE.DirectionalLight(0xfff6e8,2.7);key.position.set(30,70,40);key.castShadow=!this.lite;key.shadow.mapSize.set(2048,2048);key.shadow.bias=-.0004;this.scene.add(key,key.target);
    const fill=new THREE.DirectionalLight(0xdbeaff,.7);fill.position.set(-30,20,-60);this.scene.add(fill);
    this.terrain=null;this.terrainVisible=true;
    // Recorded inspection defects, placed on the model from their sheet sketches (see setDefects).
    this.defectGroup=new THREE.Group();this.defectGroup.name='defects';this.scene.add(this.defectGroup);this.defectsOn=false;this.onDefect=null;
    // Analysis colours use two shared, long-lived materials (analyzed / not analyzed), so their shaders compile once per page.
    this.analysisMaterials={analyzed:new THREE.MeshBasicMaterial({color:0xffffff,side:THREE.DoubleSide,vertexColors:true,toneMapped:false}),
      other:new THREE.MeshBasicMaterial({color:0x71838e,side:THREE.DoubleSide,toneMapped:false,transparent:true,opacity:.12,depthWrite:false})};
    for(const m of Object.values(this.analysisMaterials))m.userData.shared=true;
    this.root=new THREE.Group();this.scene.add(this.root);this.plane=new THREE.Plane(new THREE.Vector3(-1,0,0),1e6);
    this.helper=new THREE.Box3Helper(new THREE.Box3(),0x5fe6df);this.helper.visible=false;this.scene.add(this.helper);
    this.grid=null;
    this.raycaster=new THREE.Raycaster();let down=null;
    // Only presses on the canvas pick; overlays inside the host (toolbar, legend) do not.
    host.addEventListener('pointerdown',e=>{down=e.button===0&&e.target===this.renderer.domElement?[e.clientX,e.clientY]:null;});
    host.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5){down=null;return;}down=null;
      if(this.analysisGeometry)return;
      const r=this.renderer.domElement.getBoundingClientRect();this.raycaster.setFromCamera(new THREE.Vector2((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1),this.camera);
      if(this.defectGroup.visible&&this.defectGroup.children.length){const d=this.raycaster.intersectObjects(this.defectGroup.children,true).find(h=>h.object.userData.defect);if(d){this.onDefect?.(d.object.userData.defect);return;}}
      const targets=[...this.meshes.values()].filter(m=>m.visible&&m.material.opacity>.2);if(this.terrain?.visible)targets.push(...this.terrain.children.filter(o=>o.userData.blocksPick));
      const hit=this.raycaster.intersectObjects(targets,false).find(h=>!this.clipping||this.plane.distanceToPoint(h.point)>=0);
      if(hit?.object.userData.part)this.onSelect(hit.object.userData.part.id);
    });
    new ResizeObserver(()=>this.resize()).observe(host);this.resize();
  }
  render(){if(this.host.clientWidth&&this.host.clientHeight){
    // Retain depth precision at whole-bridge scale without clipping close component views.
    // A fixed sub-millimetre near plane makes the deck's front/back faces flicker at a distance.
    const near=Math.max(.0001,this.camera.position.distanceTo(this.controls.target)/2000);
    if(Math.abs(this.camera.near-near)>1e-8){this.camera.near=near;this.camera.updateProjectionMatrix();}
    this.renderer.render(this.scene,this.camera);
  }}
  resize(){const w=this.host.clientWidth,h=this.host.clientHeight;if(!w||!h)return;this.renderer.setSize(w,h,false);this.camera.aspect=w/h;this.camera.updateProjectionMatrix();this.render();}
  clear(){this.clearAnalysis();this.clearTerrain();this.clearDefects();for(const mesh of this.meshes.values()){mesh.geometry.dispose();mesh.material.dispose();}if(this.grid){this.scene.remove(this.grid);this.grid.geometry.dispose();this.grid.material.dispose();this.grid=null;}for(const t of this.textures)t.dispose();this.textures.clear();this.root.clear();this.meshes.clear();this.selected.clear();this.hidden.clear();this.isolated=null;this.helper.visible=false;}
  cancel(){this.loadId++;this.abort?.abort();this.clear();this.render();}
  async load(data,progress){const seq=++this.loadId;this.abort?.abort();this.abort=new AbortController();this.clear();this.data=data;this.clipping=false;this.opacity=1;
    // A textured display copy (same meshes, baked AO) is preferred when the bridge has one.
    let response=data.model.render_url?await fetch(data.model.render_url,{signal:this.abort.signal}):null;
    if(!response?.ok)response=await fetch(data.model.url,{signal:this.abort.signal});if(!response.ok)throw Error('Could not load the GLB file.');const bytes=await response.arrayBuffer();
    if(seq!==this.loadId)return false;progress('Preparing 3D objects…');
    const gltf=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(bytes,'');if(seq!==this.loadId){gltf.scene.traverse(n=>{n.geometry?.dispose();for(const m of Array.isArray(n.material)?n.material:[n.material])m?.dispose();});return false;}
    const byName=new Map(data.parts.map(p=>[p.mesh_name,p]));gltf.scene.updateMatrixWorld(true);
    gltf.scene.traverse(original=>{if(!original.isMesh)return;const p=byName.get(original.name)||byName.get(original.parent?.name);if(!p)throw Error('Unregistered 3D object: '+original.name);
      const geom=floatPositions(original.geometry.clone()).applyMatrix4(original.matrixWorld);geom.computeVertexNormals();const material=new THREE.MeshStandardMaterial({color:p.color||'#a7b8bc',...surfaceFor(p),...this.bakedMaps(original.material,geom),side:THREE.DoubleSide,flatShading:true});
      const mesh=new THREE.Mesh(geom,material);mesh.castShadow=true;mesh.receiveShadow=true;mesh.name=p.mesh_name;mesh.userData.part=p;this.meshes.set(p.id,mesh);this.root.add(mesh);
      original.geometry.dispose();for(const m of Array.isArray(original.material)?original.material:[original.material])m.dispose();
    });
    if(this.meshes.size!==data.parts.length)throw Error('Component and 3D object counts do not match.');
    this.bounds=new THREE.Box3().setFromObject(this.root);const center=this.bounds.getCenter(new THREE.Vector3()),size=this.bounds.getSize(new THREE.Vector3());this.grid=new THREE.GridHelper(Math.max(size.x,size.z)*2.5,32,0x4a5157,0x30363b);this.grid.position.set(center.x,this.bounds.min.y-.2,center.z);this.grid.material.transparent=true;this.grid.material.opacity=.35;this.scene.add(this.grid);this.buildTerrain();this.fitShadow();this.warmAnalysis();this.view='iso';this.defaultVisibility();this.fit();return true;
  }
  // Surface texture, its normal map and baked AO from a display GLB. The part colour still tints the texture,
  // and the textures are shared, so they are tracked here and disposed with the model.
  bakedMaps(src,geom){const maps={};if(!src)return maps;const keep=t=>{this.textures.add(t);t.anisotropy=Math.min(8,this.renderer.capabilities.getMaxAnisotropy());return t;};
    if(src.map&&geom.attributes.uv)maps.map=keep(src.map);
    if(src.normalMap&&geom.attributes.uv&&!this.lite){maps.normalMap=keep(src.normalMap);maps.normalScale=src.normalScale.clone();}
    if(src.aoMap&&geom.attributes.uv1){maps.aoMap=keep(src.aoMap);maps.aoMapIntensity=1;}
    return maps;}
  ids(){return [...this.meshes.keys()];}
  defaultVisibility(){this.hidden=new Set(this.data.parts.filter(p=>this.data.model.hidden_layers.includes(p.layer)).map(p=>p.id));this.isolated=null;this.sync();}
  showAll(){this.hidden.clear();this.isolated=null;this.sync();}
  show(ids){for(const id of ids){this.hidden.delete(id);if(this.isolated)this.isolated.add(id);}this.sync();}
  hide(ids){for(const id of ids)this.hidden.add(id);this.sync();}
  isolate(ids){this.isolated=new Set(ids);for(const id of ids)this.hidden.delete(id);this.sync();this.fit(ids);}
  unisolate(){this.isolated=null;this.sync();}
  select(ids){this.selected=new Set(ids);this.sync();}
  sync(){for(const [id,mesh] of this.meshes){mesh.visible=!this.hidden.has(id)&&(!this.isolated||this.isolated.has(id));if(mesh.material.emissive){mesh.material.emissive.set(this.selected.has(id)?'#008d97':'#000000');mesh.material.emissiveIntensity=.35;}}
    const selectedMeshes=[...this.selected].map(id=>this.meshes.get(id)).filter(m=>m?.visible);this.helper.visible=selectedMeshes.length>0&&!this.analysisGeometry;
    if(selectedMeshes.length){this.helper.box.makeEmpty();for(const m of selectedMeshes)this.helper.box.expandByObject(m);}
    this.render();this.onChange?.({visible:[...this.meshes.values()].filter(m=>m.visible).length,total:this.meshes.size,isolated:!!this.isolated});
  }
  fit(ids=null,view=this.view||'iso',frame=null){if(!this.meshes.size)return;this.view=view;const box=new THREE.Box3();if(frame)box.copy(frame);else if(this.analysisGeometry)box.setFromObject(this.analysisGeometry);else for(const [id,m] of this.meshes){if(ids?ids.includes(id):m.visible)box.expandByObject(m);}if(box.isEmpty())box.copy(this.bounds);
    const center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3());const radius=Math.max(size.length()/2,.2);
    const direction=new THREE.Vector3(...{iso:[1,.65,1.15],top:[0,1,.0001],side:[0,.025,1],end:[1,.025,0]}[view]).normalize();
    const right=new THREE.Vector3().crossVectors(this.camera.up,direction).normalize(),up=new THREE.Vector3().crossVectors(direction,right).normalize();
    const tanV=Math.tan(THREE.MathUtils.degToRad(this.camera.fov)/2),tanH=tanV*this.camera.aspect;
    let distance=.5;
    for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){const p=new THREE.Vector3(x,y,z).sub(center);distance=Math.max(distance,Math.abs(p.dot(right))/tanH+p.dot(direction),Math.abs(p.dot(up))/tanV+p.dot(direction));}
    distance*=1.16;this.camera.position.copy(center).add(direction.multiplyScalar(distance));
    this.camera.far=Math.max(10000,distance*30);this.camera.updateProjectionMatrix();this.controls.target.copy(center);this.controls.maxDistance=Math.max(2000,distance*20);this.controls.minDistance=.02;this.controls.update();this.render();
  }

  // Shadow camera fitted to the bridge so the shadow map's resolution is spent on the structure.
  fitShadow(){if(!this.bounds)return;const c=this.bounds.getCenter(new THREE.Vector3()),r=Math.max(this.bounds.getSize(new THREE.Vector3()).length()/2,1);
    this.key.target.position.copy(c);this.key.position.copy(c).add(new THREE.Vector3(30,70,40).normalize().multiplyScalar(r*2.5));
    const cam=this.key.shadow.camera;cam.left=-r*1.25;cam.right=r*1.25;cam.top=r*1.25;cam.bottom=-r*1.25;cam.near=r*.5;cam.far=r*5;cam.updateProjectionMatrix();this.key.shadow.normalBias=r/1500;}
  // Compile the analysis shaders with the scene's real lights and shadows once, so opening Analysis does not stall.
  warmAnalysis(){if(this.analysisWarm)return;this.analysisWarm=true;const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute([0,0,0,0,0,1e-4,1e-4,0,0],3));g.setAttribute('color',new THREE.Float32BufferAttribute([1,1,1,1,1,1,1,1,1],3));
    const dummies=Object.values(this.analysisMaterials).map(m=>{const d=new THREE.Mesh(g,m);d.castShadow=true;d.receiveShadow=true;return d;});this.scene.add(...dummies);
    try{this.renderer.compile(this.scene,this.camera);}finally{this.scene.remove(...dummies);g.dispose();}}
  clearTerrain(){if(!this.terrain)return;this.scene.remove(this.terrain);this.terrain.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});this.terrain=null;}
  setTerrain(visible){this.terrainVisible=visible;if(this.terrain)this.terrain.visible=visible&&!this.analysisGeometry;if(this.grid)this.grid.visible=!(this.terrain&&visible)&&!this.analysisGeometry;this.render();}
  // Illustrative site, not survey data (terrain.js): the ground is fitted to the model's own parts. It stays under
  // the superstructure, bearings and rails, carries the approach slabs and roads, buries footings and post ends, stops
  // at abutments, wings and walls, and leaves a channel (waterways) or a level corridor (crossed roads) under the spans.
  buildTerrain(){this.clearTerrain();
    const parts=[...this.meshes.values()].map(m=>({id:m.userData.part.id,name:m.userData.part.name||'',layer:m.userData.part.layer,pos:m.geometry.attributes.position.array,index:m.geometry.index?m.geometry.index.array:null}));
    const T=planTerrain(parts,{waterway:this.data.waterway||'',site:this.data.source_metadata?.site||null});this.terrainPlan=T;if(!T)return false;
    const {nu,nz,X,Z,H,s,zc,block}=T,n=nu*nz,P=new Float32Array(n*3);
    for(let v=0;v<n;v++){P[3*v]=X[v];P[3*v+1]=H[v];P[3*v+2]=Z[v];}
    const idx=new Uint32Array((nu-1)*(nz-1)*6);let k=0;
    for(let j=0;j<nz-1;j++)for(let i=0;i<nu-1;i++){const a=j*nu+i,b=a+1,c=a+nu,d=c+1;idx.set([a,c,b,b,c,d],k);k+=6;}
    const geom=new THREE.BufferGeometry();geom.setAttribute('position',new THREE.BufferAttribute(P,3));geom.setIndex(new THREE.BufferAttribute(idx,1));geom.computeVertexNormals();
    const grass=new THREE.Color('#5d6a48'),soil=new THREE.Color('#7a6b52'),colors=new Float32Array(n*3),c=new THREE.Color(),nrm=geom.attributes.normal,ch=T.channel;
    // Fill slopes (1:2) read as drier grass with a crisp edge at the slope break; only the channel banks read as wet soil.
    for(let v=0;v<n;v++){const x=X[v],z=Z[v],steep=THREE.MathUtils.smoothstep(1-nrm.getY(v),.05,.08)*.55,wet=ch?1-THREE.MathUtils.smoothstep(T.across(T.U(x,z)),ch.half+ch.bank,ch.half+ch.bank+1.5):0;
      const jitter=.94+.12*(Math.sin(x*12.9898+z*78.233)*43758.5453%1+1)%1;c.copy(grass).lerp(soil,Math.max(steep,wet*.8)).multiplyScalar(jitter);colors.set([c.r,c.g,c.b],v*3);}
    geom.setAttribute('color',new THREE.BufferAttribute(colors,3));
    const group=new THREE.Group();group.name='terrain';
    const flat=(mesh)=>{mesh.receiveShadow=true;mesh.userData.blocksPick=true;group.add(mesh);return mesh;};
    flat(new THREE.Mesh(geom,new THREE.MeshStandardMaterial({vertexColors:true,roughness:1,metalness:0})));
    const xOf=(u,z)=>u+s*(z-zc),quad=(pts,y,material)=>{const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pts.flatMap(([u,z])=>[xOf(u,z),y,z]),3));g.setIndex([0,3,1,1,3,2]);g.computeVertexNormals();return flat(new THREE.Mesh(g,material));};
    // Skirt: the site reads as a cut-out block, which marks it as illustrative rather than surveyed.
    let minY=Infinity;for(let v=0;v<n;v++)minY=Math.min(minY,H[v]);
    const base=Math.min(minY-4,this.bounds.min.y-1),skirt=[],at=(i,j)=>{const v=j*nu+i;return [X[v],H[v],Z[v]];};
    const wall=pts=>{for(let q=0;q<pts.length-1;q++){const [a,b]=[pts[q],pts[q+1]];skirt.push(a[0],a[1],a[2],b[0],b[1],b[2],b[0],base,b[2],a[0],a[1],a[2],b[0],base,b[2],a[0],base,a[2]);}};
    wall([...Array(nu)].map((_,i)=>at(i,0)));wall([...Array(nu)].map((_,i)=>at(i,nz-1)));wall([...Array(nz)].map((_,j)=>at(0,j)));wall([...Array(nz)].map((_,j)=>at(nu-1,j)));
    const sg=new THREE.BufferGeometry();sg.setAttribute('position',new THREE.Float32BufferAttribute(skirt,3));sg.computeVertexNormals();
    group.add(new THREE.Mesh(sg,new THREE.MeshStandardMaterial({color:'#4a4133',roughness:1,metalness:0,side:THREE.DoubleSide})));
    // Water fills the whole block at one level; the ground hides it everywhere but the channel.
    if(T.water)quad([[block.u0,block.z0],[block.u1,block.z0],[block.u1,block.z1],[block.u0,block.z1]],T.water.level,new THREE.MeshStandardMaterial({color:'#38545d',roughness:.12,metalness:0,transparent:true,opacity:.86}));
    const asphalt=new THREE.MeshStandardMaterial({color:'#36393b',roughness:.95,metalness:0,side:THREE.DoubleSide});
    // Crossed roads: level ribbons with a centre line, run parallel to the abutments under the bridge.
    for(const r of T.roads){quad([[r.u0,block.z0],[r.u1,block.z0],[r.u1,block.z1],[r.u0,block.z1]],r.y+.02,asphalt);const m=(r.u0+r.u1)/2;
      quad([[m-.075,block.z0],[m+.075,block.z0],[m+.075,block.z1],[m-.075,block.z1]],r.y+.035,new THREE.MeshStandardMaterial({color:'#c9b46a',roughness:.8,metalness:0}));}
    // Approach roads: from the outer end of the approach slabs on the same line, with the slab's cross-fall and grade,
    // to the block edge; short skirts close the edges against the ground.
    for(const r of T.approachRoads){const zs=[r.zA,...r.zs,r.zB],rows=30,pos=[],ind=[],cols=zs.length;
      for(let q=0;q<=rows;q++){const f=(q/rows)**1.7;for(const z of zs){const xe=r.end.at(z),tm=r.side*(xOf(r.edgeU,z)-xe),x=xe+r.side*tm*f;pos.push(x,r.y(x,z),z);}}
      for(let q=0;q<rows;q++)for(let c2=0;c2<cols-1;c2++){const a=q*cols+c2,b=a+1,c3=a+cols,d=c3+1;ind.push(a,c3,b,b,c3,d);}
      const edge=(list)=>{for(let e=0;e<list.length-1;e++){const p0=list[e],p1=list[e+1],o=pos.length/3;pos.push(...p0,...p1,p1[0],p1[1]-.3,p1[2],p0[0],p0[1]-.3,p0[2]);ind.push(o,o+1,o+2,o,o+2,o+3);}};
      const V=i=>[pos[3*i],pos[3*i+1],pos[3*i+2]];
      edge([...Array(rows+1)].map((_,q)=>V(q*cols)));edge([...Array(rows+1)].map((_,q)=>V(q*cols+cols-1)));edge([...Array(cols)].map((_,c2)=>V(rows*cols+c2)));
      const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setIndex(ind);g.computeVertexNormals();flat(new THREE.Mesh(g,asphalt));}
    group.visible=this.terrainVisible;this.terrain=group;this.scene.add(group);if(this.grid)this.grid.visible=!this.terrainVisible;return true;}
  setDeckOpacity(value){this.opacity=value;for(const mesh of this.meshes.values()){const layer=mesh.userData.part.layer;if(['deck','wearing','road_surface'].includes(layer)&&!mesh.material.userData.shared){mesh.material.opacity=value;mesh.material.transparent=value<1;mesh.material.depthWrite=value>=1;mesh.castShadow=value>=1;mesh.material.needsUpdate=true;}}this.render();}
  setClip(enabled,percent){this.clipping=enabled;if(!this.bounds)return;this.plane.constant=THREE.MathUtils.lerp(this.bounds.min.x-.02,this.bounds.max.x+.02,percent/100);for(const m of [...this.meshes.values(),...(this.terrain?.children||[])]){m.material.clippingPlanes=enabled?[this.plane]:[];m.material.needsUpdate=true;}this.render();}
  clearAnalysis(){
    this.showAnalysisMesh(null);
    for(const mesh of this.meshes.values()){
      const saved=mesh.userData.analysisOriginal;if(!saved)continue;
      if(!mesh.material.userData.shared)mesh.material.dispose();mesh.material=saved.material;
      mesh.geometry.attributes.position.array.set(saved.positions);mesh.geometry.attributes.position.needsUpdate=true;
      mesh.geometry.deleteAttribute('color');mesh.geometry.computeBoundingBox();mesh.geometry.computeBoundingSphere();
      mesh.material.clippingPlanes=this.clipping?[this.plane]:[];
      if(['deck','wearing','road_surface'].includes(mesh.userData.part.layer)){
        mesh.material.opacity=this.opacity;mesh.material.transparent=this.opacity<1;mesh.material.depthWrite=this.opacity>=1;
      }
      delete mesh.userData.analysisOriginal;
    }
    this.analysis=null;this.render();
  }
  setAnalysis(result,field='stress_MPa',deformationScale=0,family='all'){
    this.showAnalysisMesh(null);
    if(result.bridge_id!==this.data?.id)throw Error('Analysis belongs to another bridge.');
    const members=new Map(result.members.filter(m=>family==='all'||m.family===family).map(m=>[m.component_id,m]));
    const clip=this.clipping?[this.plane]:[],shared=this.analysisMaterials;for(const m of Object.values(shared))m.clippingPlanes=clip;
    if([...members.keys()].some(id=>!this.meshes.has(id)))throw Error('Analysis component mapping is incomplete.');
    const max=Math.max(1e-12,...[...members.values()].flatMap(m=>m.samples.map(p=>Math.abs(p[field]||0))));
    const stops=['#335cde','#17b7ce','#7cdb99','#ffcb55','#ed5947'].map(c=>new THREE.Color(c));
    const color=value=>{const t=Math.min(1,Math.max(0,Math.abs(value)/Math.max(max,1e-12)))*4,i=Math.min(3,Math.floor(t));return stops[i].clone().lerp(stops[i+1],t-i);};
    const tree=(points,depth=0)=>{if(!points.length)return null;const axis=depth%3;points.sort((a,b)=>a.xyz_m[axis]-b.xyz_m[axis]);const mid=points.length>>1;return {p:points[mid],axis,left:tree(points.slice(0,mid),depth+1),right:tree(points.slice(mid+1),depth+1)};};
    const closest=(root,target)=>{let best=root.p,distance=Infinity;const visit=n=>{if(!n)return;const p=n.p.xyz_m,value=(p[0]-target[0])**2+(p[1]-target[1])**2+(p[2]-target[2])**2;if(value<distance){best=n.p;distance=value;}const delta=target[n.axis]-p[n.axis];visit(delta<0?n.left:n.right);if(delta*delta<=distance)visit(delta<0?n.right:n.left);};visit(root);return best;};
    for(const [id,mesh] of this.meshes){
      let saved=mesh.userData.analysisOriginal;
      if(!saved){saved={material:mesh.material,positions:mesh.geometry.attributes.position.array.slice()};mesh.userData.analysisOriginal=saved;}
      const member=members.get(id),geom=mesh.geometry,positions=geom.attributes.position;
      positions.array.set(saved.positions);
      mesh.material=member?shared.analyzed:shared.other;
      if(member){
        const samples=member.samples,colors=new Float32Array(positions.count*3);
        const global=!!member.family;
        const spatial=global?tree(samples.slice()):null;
        const axes=global?[0,1,2].map(axis=>[Math.min(...samples.map(p=>p.xyz_m[axis])),Math.max(...samples.map(p=>p.xyz_m[axis]))]):null;
        const visual=mesh.userData.part.bounds;
        for(let i=0;i<positions.count;i++){
          if(global){
            // Structural axes are straightened. Use actual X/Y for deck, and
            // normalized local positions for vertical/transverse frame members.
            const native=[saved.positions[i*3],-saved.positions[i*3+2],saved.positions[i*3+1]];
            const target=result.display_mapping==='native_coordinates'?native:axes.map(([a,b],axis)=>b-a<1e-7?a:(member.family==='deck'&&axis<2?native[axis]:a+(b-a)*THREE.MathUtils.clamp((native[axis]-visual[0][axis])/Math.max(1e-9,visual[1][axis]-visual[0][axis]),0,1)));
            const nearest=closest(spatial,target);
            const c=color(nearest[field]||0);colors.set([c.r,c.g,c.b],i*3);
            if(result.case!=='global_staged'){
              const u=nearest.displacement_m;positions.array[i*3]+=u[0]*deformationScale;positions.array[i*3+1]+=u[2]*deformationScale;positions.array[i*3+2]-=u[1]*deformationScale;
            }
            continue;
          }
          const x=saved.positions[i*3];let lo=0,hi=samples.length-1;
          while(hi-lo>1){const mid=(lo+hi)>>1;if(samples[mid].x_m<=x)lo=mid;else hi=mid;}
          const a=samples[lo],b=samples[hi],t=THREE.MathUtils.clamp((x-a.x_m)/Math.max(1e-12,b.x_m-a.x_m),0,1);
          const c=color(THREE.MathUtils.lerp(a[field],b[field],t));colors.set([c.r,c.g,c.b],i*3);
          // GLB axes (X,Z,-Y): native vertical displacement maps to display Y.
          positions.array[i*3+1]-=THREE.MathUtils.lerp(a.deflection_mm,b.deflection_mm,t)*deformationScale/1000;
        }
        geom.setAttribute('color',new THREE.BufferAttribute(colors,3));
      }else geom.deleteAttribute('color');
      positions.needsUpdate=true;geom.computeBoundingBox();geom.computeBoundingSphere();
    }
    this.analysis={result,field,deformationScale,family,max};this.sync();
  }
  showAnalysisMesh(mesh){
    if(this.analysisGeometry){this.scene.remove(this.analysisGeometry);this.analysisGeometry.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});this.analysisGeometry=null;}
    this.root.visible=!mesh;this.defectGroup.visible=!mesh&&this.defectsOn;if(this.terrain)this.terrain.visible=!mesh&&this.terrainVisible;if(this.grid)this.grid.visible=!mesh&&!(this.terrain&&this.terrainVisible);
    if(!mesh){this.render();return;}
    const nodes=new Map(mesh.nodes.map(n=>[n.id,new THREE.Vector3(n.xyz_m[0],n.xyz_m[2],-n.xyz_m[1])]));
    const group=new THREE.Group(),lines=[];
    for(const b of mesh.beams)lines.push(nodes.get(b.nodes[0]),nodes.get(b.nodes[1]));
    for(const s of mesh.shells)for(let i=0;i<4;i++)lines.push(nodes.get(s.nodes[i]),nodes.get(s.nodes[(i+1)%4]));
    group.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(lines),new THREE.LineBasicMaterial({color:0x5ce1d2})));
    const links=mesh.links.flatMap(pair=>pair.map(n=>nodes.get(n)));
    group.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(links),new THREE.LineBasicMaterial({color:0xc59b64,transparent:true,opacity:.55})));
    group.add(new THREE.Points(new THREE.BufferGeometry().setFromPoints(mesh.supports.map(n=>nodes.get(n))),new THREE.PointsMaterial({color:0xffbd69,size:7,sizeAttenuation:false})));
    this.scene.add(group);this.analysisGeometry=group;this.helper.visible=false;
    const box=new THREE.Box3().setFromObject(group),center=box.getCenter(new THREE.Vector3()),radius=box.getSize(new THREE.Vector3()).length()/2;
    this.camera.position.copy(center).add(new THREE.Vector3(1,.6,1).normalize().multiplyScalar(radius*3));this.controls.target.copy(center);this.controls.update();this.render();
  }
  // Defects drawn on inspection sheets. Each sketch point maps to the view plane (sheets.json "mapping"); a ray
  // along -normal then finds the recorded member's surface, so the defect sits on the real face in 3D. A defect on a
  // view that a later sheet build retired is placed with the retired frame it was drawn on.
  clearDefects(){for(const o of [...this.defectGroup.children]){o.traverse(n=>{n.geometry?.dispose();n.material?.map?.dispose();n.material?.dispose();});this.defectGroup.remove(o);}this.defectBoxes=new Map();}
  setDefects(defects,catalog){this.clearDefects();if(!catalog)return 0;
    const byName=new Map([...this.meshes.values()].map(m=>[m.name,m])),ray=new THREE.Raycaster();let placed=0;
    for(const d of defects){const sheet=catalog.sheets.find(s=>s.id===d.sheet_id),view=sheet?.views.find(v=>v.id===d.view_id)||catalog.retired_views?.[d.view_id];const own=byName.get(d.part);if(!view||!own)continue;
      const N=new THREE.Vector3(...view.normal),back=N.clone().negate(),others=view.parts.map(n=>byName.get(n)).filter(m=>m&&m!==own);
      const onSurface=uv=>{ray.set(new THREE.Vector3(...planePoint(uv,view)),back);const hit=ray.intersectObject(own,false)[0]||ray.intersectObjects(others,false)[0];return hit?hit.point.addScaledVector(N,.012):null;};
      const colour=new THREE.Color(CS_COLORS[d.cs]||'#6b7378'),group=new THREE.Group();group.userData.defect=d.id;
      const pts=(d.kind==='point'?d.path:densify(d.path,.004,d.kind==='area')).map(onSurface).filter(Boolean);if(!pts.length)continue;
      const solid=new THREE.MeshBasicMaterial({color:colour,toneMapped:false});
      if(d.kind==='point'){const dot=new THREE.Mesh(new THREE.SphereGeometry(.09,16,12),solid);dot.position.copy(pts[0]);dot.userData.defect=d.id;group.add(dot);}
      else{if(pts.length>1){const tube=new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts,d.kind==='area','centripetal'),Math.min(400,pts.length*3),d.kind==='area'?.012:.018,6,d.kind==='area'),solid);tube.userData.defect=d.id;group.add(tube);}
        if(d.kind==='area'&&d.path.length>2){const ring=d.path.map(([u,v])=>new THREE.Vector2(u*view.extent_m[0],v*view.extent_m[1]));const tris=THREE.ShapeUtils.triangulateShape(ring,[]);const corners=d.path.map(onSurface);
          if(corners.every(Boolean)){const geom=new THREE.BufferGeometry().setFromPoints(tris.flat().map(i=>corners[i]));const fill=new THREE.Mesh(geom,new THREE.MeshBasicMaterial({color:colour,transparent:true,opacity:.42,side:THREE.DoubleSide,depthWrite:false,toneMapped:false,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-4}));fill.userData.defect=d.id;group.add(fill);}}}
      const tag=this.defectTag('D'+d.number,colour);tag.position.copy(pts.reduce((a,p)=>p.y>a.y?p:a,pts[0])).addScaledVector(N,.25);tag.userData.defect=d.id;group.add(tag);
      this.defectGroup.add(group);this.defectBoxes.set(d.id,{box:new THREE.Box3().setFromPoints(pts),normal:N});placed++;}
    this.defectGroup.visible=this.defectsOn&&this.root.visible;this.render();return placed;}
  defectTag(text,colour){const c=document.createElement('canvas'),x=c.getContext('2d');c.width=128;c.height=56;x.fillStyle='#'+colour.getHexString();x.beginPath();x.roundRect(2,2,124,52,12);x.fill();x.fillStyle='#fff';x.font='600 34px "IBM Plex Sans",Arial,sans-serif';x.textAlign='center';x.textBaseline='middle';x.fillText(text,64,30);
    const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;const s=new THREE.Sprite(new THREE.SpriteMaterial({map:t,depthTest:false,toneMapped:false}));s.scale.set(.75,.33,1);s.renderOrder=5;return s;}
  showDefects(on){this.defectsOn=on;this.defectGroup.visible=on&&this.root.visible;this.render();}
  // Look at the defect square-on from the side of the face it was drawn on. Vertical faces are viewed from slightly
  // below, so substructure under a deck is not hidden by the deck; plan views are tilted a little for depth.
  focusDefect(id){const hit=this.defectBoxes?.get(id);if(!hit)return;const box=hit.box.clone().expandByScalar(1.2),center=box.getCenter(new THREE.Vector3());
    const dir=hit.normal.clone();if(Math.abs(dir.y)<.9)dir.add(new THREE.Vector3(0,-.12,0));else dir.add(new THREE.Vector3(.25,0,.25));dir.normalize();
    const radius=Math.max(box.getSize(new THREE.Vector3()).length()/2,1.5),distance=radius/Math.tan(THREE.MathUtils.degToRad(this.camera.fov/2))*1.1;
    this.camera.position.copy(center).addScaledVector(dir,distance);this.controls.target.copy(center);this.controls.update();this.render();}
}
window.BridgeViewer=BridgeViewer;
// The 3D page reads defects saved by the inspection page on this device (same origin, same IndexedDB).
window.BridgeInspection={store:inspectionStore,catalog:{CS_COLORS,CS_NAMES,DEFECTS,FIELDS},elementSummary};
