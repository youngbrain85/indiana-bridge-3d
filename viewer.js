import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

class BridgeViewer {
  constructor(host, onSelect, onChange) {
    this.host=host;this.onSelect=onSelect;this.onChange=onChange;this.meshes=new Map();this.selected=new Set();this.hidden=new Set();this.isolated=null;this.loadId=0;
    this.scene=new THREE.Scene();this.scene.background=new THREE.Color('#182533');
    this.camera=new THREE.PerspectiveCamera(38,1,.01,10000);
    this.renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});this.renderer.setPixelRatio(Math.min(devicePixelRatio,2));
    this.renderer.localClippingEnabled=true;this.renderer.outputColorSpace=THREE.SRGBColorSpace;this.renderer.toneMapping=THREE.ACESFilmicToneMapping;this.renderer.toneMappingExposure=1.15;
    host.append(this.renderer.domElement);this.renderer.domElement.setAttribute('aria-label','3D bridge model. Components can also be selected in the tree.');
    this.controls=new OrbitControls(this.camera,this.renderer.domElement);this.controls.addEventListener('change',()=>this.render());
    this.scene.add(new THREE.HemisphereLight(0xffffff,0x82969f,2.2));
    const key=new THREE.DirectionalLight(0xffffff,2.6);key.position.set(30,70,40);this.scene.add(key);
    const fill=new THREE.DirectionalLight(0xdbeaff,1.1);fill.position.set(-30,20,-60);this.scene.add(fill);
    this.root=new THREE.Group();this.scene.add(this.root);this.plane=new THREE.Plane(new THREE.Vector3(-1,0,0),1e6);
    this.helper=new THREE.Box3Helper(new THREE.Box3(),0x5fe6df);this.helper.visible=false;this.scene.add(this.helper);
    this.grid=null;
    this.raycaster=new THREE.Raycaster();let down=null;
    host.addEventListener('pointerdown',e=>{if(e.button===0)down=[e.clientX,e.clientY];});
    host.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5){down=null;return;}down=null;
      const r=this.renderer.domElement.getBoundingClientRect();this.raycaster.setFromCamera(new THREE.Vector2((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1),this.camera);
      const hit=this.raycaster.intersectObjects([...this.meshes.values()].filter(m=>m.visible&&m.material.opacity>.2),false).find(h=>!this.clipping||this.plane.distanceToPoint(h.point)>=0);
      if(hit)this.onSelect(hit.object.userData.part.id);
    });
    new ResizeObserver(()=>this.resize()).observe(host);this.resize();
  }
  render(){if(this.host.clientWidth&&this.host.clientHeight)this.renderer.render(this.scene,this.camera);}
  resize(){const w=this.host.clientWidth,h=this.host.clientHeight;if(!w||!h)return;this.renderer.setSize(w,h,false);this.camera.aspect=w/h;this.camera.updateProjectionMatrix();this.render();}
  clear(){this.clearAnalysis();for(const mesh of this.meshes.values()){mesh.geometry.dispose();mesh.material.dispose();}if(this.grid){this.scene.remove(this.grid);this.grid.geometry.dispose();this.grid.material.dispose();this.grid=null;}this.root.clear();this.meshes.clear();this.selected.clear();this.hidden.clear();this.isolated=null;this.helper.visible=false;}
  cancel(){this.loadId++;this.abort?.abort();this.clear();this.render();}
  async load(data,progress){const seq=++this.loadId;this.abort?.abort();this.abort=new AbortController();this.clear();this.data=data;this.clipping=false;this.opacity=1;
    const response=await fetch(data.model.url,{signal:this.abort.signal});if(!response.ok)throw Error('Could not load the GLB file.');const bytes=await response.arrayBuffer();
    if(seq!==this.loadId)return false;progress('Preparing 3D objects…');
    const gltf=await new GLTFLoader().parseAsync(bytes,'');if(seq!==this.loadId){gltf.scene.traverse(n=>{n.geometry?.dispose();for(const m of Array.isArray(n.material)?n.material:[n.material])m?.dispose();});return false;}
    const byName=new Map(data.parts.map(p=>[p.mesh_name,p]));gltf.scene.updateMatrixWorld(true);
    gltf.scene.traverse(original=>{if(!original.isMesh)return;const p=byName.get(original.name)||byName.get(original.parent?.name);if(!p)throw Error('Unregistered 3D object: '+original.name);
      const geom=original.geometry.clone().applyMatrix4(original.matrixWorld);geom.computeVertexNormals();const material=new THREE.MeshStandardMaterial({color:p.color||'#a7b8bc',roughness:.72,metalness:.08,side:THREE.DoubleSide,flatShading:true});
      const mesh=new THREE.Mesh(geom,material);mesh.name=p.mesh_name;mesh.userData.part=p;this.meshes.set(p.id,mesh);this.root.add(mesh);
      original.geometry.dispose();for(const m of Array.isArray(original.material)?original.material:[original.material])m.dispose();
    });
    if(this.meshes.size!==data.parts.length)throw Error('Component and 3D object counts do not match.');
    this.bounds=new THREE.Box3().setFromObject(this.root);const center=this.bounds.getCenter(new THREE.Vector3()),size=this.bounds.getSize(new THREE.Vector3());this.grid=new THREE.GridHelper(Math.max(size.x,size.z)*2.5,32,0x426173,0x2b4151);this.grid.position.set(center.x,this.bounds.min.y-.2,center.z);this.grid.material.transparent=true;this.grid.material.opacity=.35;this.scene.add(this.grid);this.view='iso';this.defaultVisibility();this.fit();return true;
  }
  ids(){return [...this.meshes.keys()];}
  defaultVisibility(){this.hidden=new Set(this.data.parts.filter(p=>this.data.model.hidden_layers.includes(p.layer)).map(p=>p.id));this.isolated=null;this.sync();}
  showAll(){this.hidden.clear();this.isolated=null;this.sync();}
  show(ids){for(const id of ids){this.hidden.delete(id);if(this.isolated)this.isolated.add(id);}this.sync();}
  hide(ids){for(const id of ids)this.hidden.add(id);this.sync();}
  isolate(ids){this.isolated=new Set(ids);for(const id of ids)this.hidden.delete(id);this.sync();this.fit(ids);}
  unisolate(){this.isolated=null;this.sync();}
  select(ids){this.selected=new Set(ids);this.sync();}
  sync(){for(const [id,mesh] of this.meshes){mesh.visible=!this.hidden.has(id)&&(!this.isolated||this.isolated.has(id));if(mesh.material.emissive){mesh.material.emissive.set(this.selected.has(id)?'#008d97':'#000000');mesh.material.emissiveIntensity=.35;}}
    const selectedMeshes=[...this.selected].map(id=>this.meshes.get(id)).filter(m=>m?.visible);this.helper.visible=selectedMeshes.length>0;
    if(selectedMeshes.length){this.helper.box.makeEmpty();for(const m of selectedMeshes)this.helper.box.expandByObject(m);}
    this.render();this.onChange?.({visible:[...this.meshes.values()].filter(m=>m.visible).length,total:this.meshes.size,isolated:!!this.isolated});
  }
  fit(ids=null,view=this.view||'iso'){if(!this.meshes.size)return;this.view=view;const box=new THREE.Box3();for(const [id,m] of this.meshes){if(ids?ids.includes(id):m.visible)box.expandByObject(m);}if(box.isEmpty())box.copy(this.bounds);
    const center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3());const radius=Math.max(size.length()/2,.2);
    const direction=new THREE.Vector3(...{iso:[1,.65,1.15],top:[0,1,.0001],side:[0,.025,1],end:[1,.025,0]}[view]).normalize();
    const right=new THREE.Vector3().crossVectors(this.camera.up,direction).normalize(),up=new THREE.Vector3().crossVectors(direction,right).normalize();
    const tanV=Math.tan(THREE.MathUtils.degToRad(this.camera.fov)/2),tanH=tanV*this.camera.aspect;
    let distance=.5;
    for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){const p=new THREE.Vector3(x,y,z).sub(center);distance=Math.max(distance,Math.abs(p.dot(right))/tanH+p.dot(direction),Math.abs(p.dot(up))/tanV+p.dot(direction));}
    distance*=1.16;this.camera.position.copy(center).add(direction.multiplyScalar(distance));
    this.camera.near=Math.max(radius/10000,.0005);this.camera.far=Math.max(10000,distance*30);this.camera.updateProjectionMatrix();this.controls.target.copy(center);this.controls.maxDistance=Math.max(2000,distance*20);this.controls.minDistance=.02;this.controls.update();this.render();
  }
  setDeckOpacity(value){this.opacity=value;for(const mesh of this.meshes.values()){const layer=mesh.userData.part.layer;if(['deck','wearing','road_surface'].includes(layer)){mesh.material.opacity=value;mesh.material.transparent=value<1;mesh.material.depthWrite=value>=1;mesh.material.needsUpdate=true;}}this.render();}
  setClip(enabled,percent){this.clipping=enabled;if(!this.bounds)return;this.plane.constant=THREE.MathUtils.lerp(this.bounds.min.x-.02,this.bounds.max.x+.02,percent/100);for(const m of this.meshes.values()){m.material.clippingPlanes=enabled?[this.plane]:[];m.material.needsUpdate=true;}this.render();}
  clearAnalysis(){
    for(const mesh of this.meshes.values()){
      const saved=mesh.userData.analysisOriginal;if(!saved)continue;
      mesh.material.dispose();mesh.material=saved.material;
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
  setAnalysis(result,field='stress_MPa',deformationScale=0){
    if(result.bridge_id!==this.data?.id)throw Error('Analysis belongs to another bridge.');
    const members=new Map(result.members.map(m=>[m.component_id,m]));
    if([...members.keys()].some(id=>!this.meshes.has(id)))throw Error('Analysis component mapping is incomplete.');
    const max=field==='stress_MPa'?result.max_stress_MPa:result.max_deflection_mm;
    const stops=['#335cde','#17b7ce','#7cdb99','#ffcb55','#ed5947'].map(c=>new THREE.Color(c));
    const color=value=>{const t=Math.min(1,Math.max(0,Math.abs(value)/Math.max(max,1e-12)))*4,i=Math.min(3,Math.floor(t));return stops[i].clone().lerp(stops[i+1],t-i);};
    for(const [id,mesh] of this.meshes){
      let saved=mesh.userData.analysisOriginal;
      if(!saved){saved={material:mesh.material,positions:mesh.geometry.attributes.position.array.slice()};mesh.userData.analysisOriginal=saved;}
      else mesh.material.dispose();
      const member=members.get(id),geom=mesh.geometry,positions=geom.attributes.position;
      positions.array.set(saved.positions);
      mesh.material=new THREE.MeshBasicMaterial({color:member?0xffffff:0x71838e,side:THREE.DoubleSide,vertexColors:!!member,toneMapped:false,transparent:!member,opacity:member?1:.12,depthWrite:!!member,clippingPlanes:this.clipping?[this.plane]:[]});
      if(member){
        const samples=member.samples,colors=new Float32Array(positions.count*3);
        for(let i=0;i<positions.count;i++){
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
    this.analysis={result,field,deformationScale};this.sync();
  }
}
window.BridgeViewer=BridgeViewer;
