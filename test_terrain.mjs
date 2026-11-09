// Checks of the illustrative terrain (terrain.js) on real bridge models: node --test test_terrain.mjs
// The ground is sampled on the same triangles the viewer draws. Points over a retaining part (abutment, wing, wall)
// are skipped: there the part hides the ground.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const ROOT=path.dirname(fileURLToPath(import.meta.url));
const {planTerrain}=await import('data:text/javascript;base64,'+Buffer.from(fs.readFileSync(path.join(ROOT,'terrain.js'),'utf8')).toString('base64'));

// World-space positions and indices per mesh node of a plain GLB (no compression), as the viewer bakes them.
function readGlb(file){const b=fs.readFileSync(file);let o=12,json,bin;
  while(o<b.length){const len=b.readUInt32LE(o),type=b.readUInt32LE(o+4),d=b.subarray(o+8,o+8+len);if(type===0x4e4f534a)json=JSON.parse(d.toString());else bin=d;o+=8+len;}
  const mul=(a,c)=>{const r=new Array(16).fill(0);for(let i=0;i<4;i++)for(let j=0;j<4;j++)for(let k=0;k<4;k++)r[i*4+j]+=a[k*4+j]*c[i*4+k];return r;};
  const trs=n=>{if(n.matrix)return n.matrix;const [tx,ty,tz]=n.translation||[0,0,0],[x,y,z,w]=n.rotation||[0,0,0,1],[sx,sy,sz]=n.scale||[1,1,1];
    return [(1-2*(y*y+z*z))*sx,2*(x*y+z*w)*sx,2*(x*z-y*w)*sx,0,2*(x*y-z*w)*sy,(1-2*(x*x+z*z))*sy,2*(y*z+x*w)*sy,0,2*(x*z+y*w)*sz,2*(y*z-x*w)*sz,(1-2*(x*x+y*y))*sz,0,tx,ty,tz,1];};
  const dv=new DataView(bin.buffer,bin.byteOffset,bin.byteLength);
  const acc=i=>{const a=json.accessors[i],v=json.bufferViews[a.bufferView],C={SCALAR:1,VEC3:3}[a.type],size={5126:4,5125:4,5123:2,5121:1}[a.componentType];
    const stride=v.byteStride||C*size,base=(v.byteOffset||0)+(a.byteOffset||0),out=new Float64Array(a.count*C);
    for(let n=0;n<a.count;n++)for(let k=0;k<C;k++){const p=base+n*stride+k*size;out[n*C+k]=a.componentType===5126?dv.getFloat32(p,true):a.componentType===5125?dv.getUint32(p,true):a.componentType===5123?dv.getUint16(p,true):dv.getUint8(p);}return out;};
  const out=[];const walk=(ni,parent)=>{const n=json.nodes[ni],m=mul(parent,trs(n));
    if(n.mesh!==undefined){const pos=[],idx=[];let off=0;
      for(const pr of json.meshes[n.mesh].primitives){const p=acc(pr.attributes.POSITION),ix=pr.indices!==undefined?acc(pr.indices):Float64Array.from({length:p.length/3},(_,i)=>i);
        for(let i=0;i<p.length;i+=3){const x=p[i],y=p[i+1],z=p[i+2];pos.push(m[0]*x+m[4]*y+m[8]*z+m[12],m[1]*x+m[5]*y+m[9]*z+m[13],m[2]*x+m[6]*y+m[10]*z+m[14]);}
        for(const k of ix)idx.push(k+off);off+=p.length/3;}
      out.push({name:n.name,pos:Float32Array.from(pos),index:Uint32Array.from(idx)});}
    for(const c of n.children||[])walk(c,m);};
  for(const r of json.scenes[json.scene||0].nodes)walk(r,[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);return out;}

function load(id){
  const bridge=JSON.parse(fs.readFileSync(path.join(ROOT,'data/registry.json'))).bridges.find(b=>b.id===id);
  const manifest=JSON.parse(fs.readFileSync(path.join(ROOT,'data/bridges',id,'model_manifest.json')));
  const byId=new Map(manifest.parts.map(p=>[p.id,p]));
  const parts=readGlb(path.join(ROOT,'data',bridge.model.glb)).map(m=>{const p=byId.get(m.name);return {id:m.name,name:p.name,layer:p.layer,pos:m.pos,index:m.index};});
  const T=planTerrain(parts,{waterway:bridge.waterway||'',site:manifest.site||null});
  const lower=(a,v)=>{let lo=0,hi=a.length;while(lo<hi){const k=(lo+hi)>>1;if(a[k]<v)lo=k+1;else hi=k;}return lo;};
  const cell=(x,z)=>{const u=x-T.s*(z-T.zc);return [Math.min(T.nu-2,Math.max(0,lower(T.us,u)-1)),Math.min(T.nz-2,Math.max(0,lower(T.zs,z)-1)),u];};
  // Same split as the viewer's index: triangles (a, c, b) and (b, c, d) of each grid quad.
  const ground=(x,z)=>{const [i,j,u]=cell(x,z),fu=(u-T.us[i])/(T.us[i+1]-T.us[i]),fz=(z-T.zs[j])/(T.zs[j+1]-T.zs[j]),H=T.H,n=T.nu;
    const a=H[j*n+i],b=H[j*n+i+1],c=H[(j+1)*n+i],d=H[(j+1)*n+i+1];return fu+fz<=1?a+fu*(b-a)+fz*(c-a):d+(1-fu)*(c-d)+(1-fz)*(b-d);};
  const onWall=(x,z)=>{const [i,j]=cell(x,z),n=T.nu,w=T.wall;return w[j*n+i]||w[j*n+i+1]||w[(j+1)*n+i]||w[(j+1)*n+i+1];};
  // Centroids of a part's downward (or upward) faces.
  const faces=(p,up)=>{const a=p.pos,ix=p.index,out=[];for(let t=0;t<ix.length;t+=3){const P=[0,1,2].map(k=>[a[3*ix[t+k]],a[3*ix[t+k]+1],a[3*ix[t+k]+2]]);
    const e1=P[1].map((v,k)=>v-P[0][k]),e2=P[2].map((v,k)=>v-P[0][k]),ny=e1[2]*e2[0]-e1[0]*e2[2],l=Math.hypot(e1[1]*e2[2]-e1[2]*e2[1],ny,e1[0]*e2[1]-e1[1]*e2[0]);
    if(l<1e-9||(up?ny/l<.5:ny/l>-.5))continue;out.push([0,1,2].map(k=>(P[0][k]+P[1][k]+P[2][k])/3));}return out;};
  return {T,parts,manifest,ground,onWall,faces};}

const SUPER=new Set(['deck','girders','box_beams','steel','haunches','diaphragms','bracing','bearings','sidewalks']);

for(const id of ['sr1-six-mile','sr44-little-blue','virginia-avenue','us224-eight-mile']){
  test(`${id}: superstructure stays clear and approach slabs bear on the ground`,()=>{
    const {T,parts,ground,onWall,faces}=load(id);assert.ok(T,'terrain planned');
    for(const p of parts){
      if(SUPER.has(p.layer))for(const c of faces(p,false)){if(onWall(c[0],c[2]))continue;
        assert.ok(ground(c[0],c[2])<=c[1]+.01,`${p.id} underside at ${c.map(v=>v.toFixed(2))} is ${(ground(c[0],c[2])-c[1]).toFixed(3)} m under ground`);}
      if(p.layer==='approaches')for(const c of faces(p,false)){if(onWall(c[0],c[2]))continue;const g=ground(c[0],c[2]);
        assert.ok(c[1]-g<.25,`${p.id} at ${c.map(v=>v.toFixed(2))}: ${(c[1]-g).toFixed(3)} m of air under the slab`);}}});
  test(`${id}: approach roads start at the slab top`,()=>{
    const {T}=load(id);assert.equal(T.approachRoads.length,2);
    for(const r of T.approachRoads){assert.ok(Math.abs(r.g)<=.06);for(const z of r.zs){const x=r.end.at(z);assert.ok(Number.isFinite(r.y(x,z)));}}});}

test('virginia-avenue: the crossed road keeps the drawn 15 ft 8 3/8 in minimum vertical clearance',()=>{
  const {T,parts}=load('virginia-avenue');assert.equal(T.roads.length,1);const r=T.roads[0];
  let low=Infinity;for(const p of parts){if(!['girders','steel','bearings','deck','haunches'].includes(p.layer))continue;const a=p.pos;
    for(let i=0;i<a.length;i+=3){const u=a[i]-T.s*(a[i+2]-T.zc);if(u>=r.u0&&u<=r.u1&&Math.abs(a[i+2]-T.zc)<=T.halfW&&a[i+1]<low)low=a[i+1];}}
  assert.ok(Math.abs(low-r.y-4.7847)<.01,`clearance ${(low-r.y).toFixed(3)} m`);});

test('21st-street-i465: a road under each span, clear of fill, between the supports',()=>{
  const {T,ground}=load('21st-street-i465');assert.equal(T.roads.length,2);
  for(const r of T.roads){for(let z=T.block.z0+1;z<T.block.z1;z+=2)for(let u=r.u0;u<=r.u1;u+=.5){const x=u+T.s*(z-T.zc);
    assert.ok(ground(x,z)<=r.y+.02,`road at u=${u.toFixed(1)}, z=${z.toFixed(1)} is buried`);}}});

test('beechwood: footings stay covered, columns do not hang and the channel lies between the piers',()=>{
  const {T,parts,ground,faces}=load('beechwood');assert.ok(T.channel);
  const piers=T.supports.filter(s=>s.kind==='pier');assert.equal(piers.length,2);
  assert.ok(T.channel.uc>piers[0].hi&&T.channel.uc<piers[1].lo);
  for(const p of parts){if(!/column|shaft|casing/.test(p.id))continue;let bottom=Infinity;for(let i=1;i<p.pos.length;i+=3)bottom=Math.min(bottom,p.pos[i]);
    for(const c of faces(p,false)){if(c[1]>bottom+.05)continue;assert.ok(ground(c[0],c[2])>=c[1]-.02,`${p.id} hangs ${(c[1]-ground(c[0],c[2])).toFixed(3)} m above ground`);}}});

test('21st-street-i465: the MSE side walls hold the approach fill, and carry on past the model',()=>{
  const {T,ground}=load('21st-street-i465');assert.equal(T.flankWalls.length,4);
  for(const f of T.flankWalls){const out=f.z0<T.zc?f.z0-.3:f.z1+.3,inn=f.z0<T.zc?f.z1+.3:f.z0-.3;
    for(const d of [-3,1,6,15]){const x=f.x0+f.side*d,top=f.topAt(x);
      assert.ok(ground(x,out)<top-2,`${f.id}: ground ${(top-ground(x,out)).toFixed(2)} m under the top outside at ${d} m`);
      assert.ok(ground(x,inn)>top-.5,`${f.id}: fill ${(top-ground(x,inn)).toFixed(2)} m under the top inside at ${d} m`);}}});

test('21st-street-i465: the berm between each end wall and its cap stays at the coping top',()=>{
  const {parts,ground}=load('21st-street-i465');
  // Plan extent along x of a part's section at z (from its triangle edges crossing z).
  const span=(id,z)=>{const p=parts.find(q=>q.id===id),a=p.pos,ix=p.index;let lo=Infinity,hi=-Infinity;
    for(let t=0;t<ix.length;t+=3)for(let e=0;e<3;e++){const i=ix[t+e],j=ix[t+(e+1)%3],z1=a[3*i+2],z2=a[3*j+2];if((z1-z)*(z2-z)>0||z1===z2)continue;
      const x=a[3*i]+(a[3*j]-a[3*i])*(z-z1)/(z2-z1);lo=Math.min(lo,x);hi=Math.max(hi,x);}return [lo,hi];};
  for(const [cap,coping,side] of [['bent_1_cap','mse_coping_west',-1],['bent_3_cap','mse_coping_east',1]]){
    const a=parts.find(q=>q.id===coping).pos;let top=-Infinity;for(let i=1;i<a.length;i+=3)top=Math.max(top,a[i]);
    for(let z=-5;z<=5;z+=1){const c=span(cap,z),w=span(coping,z),x=side<0?(c[1]+w[0])/2:(c[0]+w[1])/2;
      assert.ok(side<0?c[1]<w[0]:w[1]<c[0],`${cap}: no berm at z=${z}`);
      assert.ok(ground(x,z)<=top+.05,`${cap}: berm at z=${z} is ${(ground(x,z)-top).toFixed(2)} m over the coping`);}}});

test('beechwood: the end-bent drain outlets daylight',()=>{
  const {parts,ground}=load('beechwood');
  for(const id of ['b1_drain_1','b4_drain_1']){const a=parts.find(p=>p.id===id).pos;let k=1;for(let i=1;i<a.length;i+=3)if(a[i]<a[k])k=i;
    assert.ok(ground(a[k-1],a[k+1])<=a[k]+.05,`${id} mouth is ${(ground(a[k-1],a[k+1])-a[k]).toFixed(2)} m under ground`);}});
