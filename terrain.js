// Illustrative site terrain, generated from the model's own parts. It is not survey data.
// Frame: x along the bridge, y up, z across (the viewer and GLB frame), metres.
//
// The ground is a height field on a grid whose lines run along the bridge (z = const) and parallel to the abutment
// faces (u = x - s(z - zc) = const). Extra grid lines sit just inside and outside the faces of the retaining parts
// (abutments, wings, walls), the approach slab edges and the road edges, so a step at a wall falls inside the wall.
//
// Heights come from the parts:
// - natural ground: a valley floor through the support bases (footing tops, column, wall and cap bottoms), rising to a
//   spill slope under a short end span, with a channel under the waterway span or a level road for each crossed road;
// - fill: falls at 1:2 from the approach roads and slabs, from parts that stand on the ground (columns, walls, caps,
//   posts) and from footings that stay buried; retaining parts stop it, and under the bridge the embankment fill stays
//   at the natural ground; next to a road or slab the ground never falls steeper than 1:1.5;
// - clearance: rises at 1:2 from the underside of the superstructure, bearings, caps and rails, so the ground never
//   touches them;
// - contact: under approach slabs, sleepers and riprap the ground is their underside.

const K=0.5;                                   // 1:2 slopes
const DECK=new Set(['deck','road_surface','wearing']);
const SUPER=new Set(['deck','road_surface','wearing','girders','box_beams','steel','arches','truss_chords','truss_web',
  'floor_system','haunches','diaphragms','bracing','gussets','lacing','fill']);
const SUB=new Set(['piers','abutments','walls','foundations','casing','monuments']);
const FURNITURE=new Set(['rails','accessories','transitions']);
const SKIP=new Set(['detail_markers']);
const SUPER_CLEAR=.4,CLEAR=.15,EMBED=.1,DELTA=.03;
const K_CLEAR=1,K_STEEP=2/3,K_CUT=.8;           // clearance 1:1, steepest ground beside a road 1:1.5, road cut 1:1.25

const smooth=(x,a,b)=>{const t=Math.min(1,Math.max(0,(x-a)/(b-a)));return t*t*(3-2*t);};
const lower=(a,v)=>{let lo=0,hi=a.length;while(lo<hi){const m=(lo+hi)>>1;if(a[m]<v)lo=m+1;else hi=m;}return lo;};

function prep(p){const a=p.pos,min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];
  for(let i=0;i<a.length;i+=3)for(let k=0;k<3;k++){const v=a[i+k];if(v<min[k])min[k]=v;if(v>max[k])max[k]=v;}
  const dx=max[0]-min[0],dz=max[2]-min[2],plan=Math.max(dx,dz);
  return {...p,min,max,c:[(min[0]+max[0])/2,(min[1]+max[1])/2,(min[2]+max[2])/2],slender:plan<1&&max[1]-min[1]>1.5*plan};}

// Plan edge x(z) of a group of parts: the convex-hull side with the largest (sign 1) or smallest (sign -1) x. Past the
// parts' ends it continues along the fitted line, so a skewed edge stays skewed beyond the deck.
function envelope(list,sign,zc,halfW){const byZ=new Map();
  for(const p of list){const a=p.pos;for(let i=0;i<a.length;i+=3){const x=a[i],z=a[i+2],k=Math.round(z*1000),v=byZ.get(k);if(v===undefined||sign*(x-v)>0)byZ.set(k,x);}}
  const pts=[...byZ].map(([k,x])=>[k/1000,x]).sort((p,q)=>p[0]-q[0]),hull=[];
  for(const p of pts){while(hull.length>=2){const a=hull[hull.length-2],b=hull[hull.length-1];if(sign*((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))>=0)hull.pop();else break;}hull.push(p);}
  const onHull=z=>{let i=1;while(i<hull.length-1&&hull[i][0]<z)i++;const a=hull[i-1],b=hull[i]||a;return a[1]+(b[1]-a[1])*(z-a[0])/((b[0]-a[0])||1);};
  const zs=[...Array(11)].map((_,k)=>zc-halfW+k*halfW/5).map(z=>Math.min(hull[hull.length-1][0],Math.max(hull[0][0],z))),xs=zs.map(onHull);
  const mz=zs.reduce((t,z)=>t+z,0)/11,mx=xs.reduce((t,x)=>t+x,0)/11,vz=zs.reduce((t,z)=>t+(z-mz)**2,0);
  const s=vz>1e-6?zs.reduce((t,z,k)=>t+(z-mz)*(xs[k]-mx),0)/vz:0,line=z=>mx+s*(z-mz);
  const at=z=>z<hull[0][0]||z>hull[hull.length-1][0]?line(z):onHull(z);
  return {at,a:at(zc),s};}

// Grid coordinates from lo to hi: `step(t)` apart, plus break lines with a twin just either side.
function lines(lo,hi,step,breaks){const out=[];for(let t=lo;t<hi;t+=step(t))out.push(t);out.push(hi);
  for(const b of breaks)if(b>lo&&b<hi)out.push(b-DELTA,b,b+DELTA);
  out.sort((a,b)=>a-b);const keep=[out[0]];for(const v of out)if(v-keep[keep.length-1]>.012)keep.push(v);
  if(hi-keep[keep.length-1]>1e-6)keep.push(hi);else keep[keep.length-1]=hi;return Float64Array.from(keep);}

export function planTerrain(input,{waterway='',site=null}={}){
  const parts=input.filter(p=>!SKIP.has(p.layer)&&p.pos.length>=9).map(prep);
  const deckP=parts.filter(p=>DECK.has(p.layer));if(!deckP.length)return null;
  let dMin=[Infinity,Infinity,Infinity],dMax=[-Infinity,-Infinity,-Infinity];
  for(const p of deckP)for(let k=0;k<3;k++){dMin[k]=Math.min(dMin[k],p.min[k]);dMax[k]=Math.max(dMax[k],p.max[k]);}
  const zc=(dMin[2]+dMax[2])/2,halfW=(dMax[2]-dMin[2])/2;

  // Skew from the deck's two end lines; u = x - s(z - zc) is then constant along the abutments.
  // Skew: first from the deck's two end lines, then from the abutment faces found with it (a deck end may be
  // squared where the abutments are not). u = x - s(z - zc) is constant along the abutments.
  const dW=envelope(deckP,-1,zc,halfW),dE=envelope(deckP,1,zc,halfW),mu=(dW.a+dE.a)/2,Lu=Math.max(dE.a-dW.a,5);
  const clampS=v=>Math.max(-2.5,Math.min(2.5,v));
  let s=clampS((dW.s+dE.s)/2);
  const setU=()=>{for(const p of parts){let lo=Infinity,hi=-Infinity;const a=p.pos;for(let i=0;i<a.length;i+=3){const u=a[i]-s*(a[i+2]-zc);if(u<lo)lo=u;if(u>hi)hi=u;}p.u=[lo,hi];p.uc=(lo+hi)/2;}};
  // Abutment faces: the span-facing plan edge of each end's retaining parts that cross most of the deck width.
  let ends,fW,fE;
  const faces=()=>{ends=parts.filter(p=>(p.layer==='abutments'||p.layer==='walls')&&p.u[1]-p.u[0]<.6*Lu);
    const faceOf=side=>{const own=ends.filter(p=>(p.uc<mu)===(side<0)),wide=own.filter(p=>p.max[2]-p.min[2]>=halfW),list=wide.length?wide:own;
      return list.length?envelope(list,side<0?1:-1,zc,halfW):null;};
    fW=faceOf(-1);fE=faceOf(1);};
  setU();faces();
  const fs=[fW,fE].filter(Boolean).map(f=>f.s);
  if(fs.length){const sf=clampS(fs.reduce((a,b)=>a+b,0)/fs.length);if(Math.abs(sf-s)>.03){s=sf;setU();faces();}}
  const U=(x,z)=>x-s*(z-zc);
  const uW=fW?U(fW.a,zc):dW.a,uE=fE?U(fE.a,zc):dE.a;
  // Retaining parts: end parts at or behind their face. They stop the fill and keep the step between their two sides.
  const behind=p=>p.uc<mu?p.uc<=uW+.3:p.uc>=uE-.3;
  const retaining=new Set(ends.filter(behind));

  // Supports: the two ends and each pier line. Each owns the substructure nearest to it.
  const pierParts=parts.filter(p=>p.layer==='piers').sort((a,b)=>a.uc-b.uc),piers=[];
  for(const p of pierParts){const last=piers[piers.length-1];if(last&&p.uc-last.u1<3){last.list.push(p);last.u1=Math.max(last.u1,p.u[1]);}else piers.push({list:[p],u1:p.u[1]});}
  // Pier-layer parts at or behind an end (end-bent columns) belong to that end.
  const inner=piers.map(g=>({kind:'pier',u:g.list.reduce((t,p)=>t+p.uc,0)/g.list.length})).filter(sp=>sp.u>uW+2&&sp.u<uE-2);
  const supports=[{kind:'end',side:-1,u:uW},...inner,{kind:'end',side:1,u:uE}];
  for(const sp of supports)sp.parts=[];
  for(const p of parts){if(!SUB.has(p.layer)||p.u[1]-p.u[0]>.6*Lu)continue;let best=null,bd=Infinity;
    for(const sp of supports){const d=sp.kind==='end'?Math.max(0,sp.side*(sp.u-p.uc)):Math.abs(p.uc-sp.u);if(d<bd){bd=d;best=sp;}}
    best.parts.push(p);p.support=best;}
  for(const sp of supports){
    // Parts far behind an end (sleepers, monuments on the approach) do not set its ground level.
    const near=sp.parts.filter(p=>sp.kind!=='end'||sp.side*(p.uc-sp.u)<6);
    const buried=near.filter(p=>(p.layer==='foundations'||p.layer==='casing')&&!p.slender);
    const standing=near.filter(p=>(p.layer==='piers'||p.layer==='abutments'||p.layer==='walls')&&(!p.slender||p.layer!=='walls'));
    sp.G=buried.length?Math.max(...buried.map(p=>p.max[1])):standing.length?Math.min(...standing.map(p=>p.min[1])):null;
    sp.F=sp.G===null?null:sp.G+(buried.length?.05:.12);
    // The opening between supports is measured between their piers and abutments (not footings, piles or spandrels).
    const solid=near.filter(p=>(p.layer==='piers'||p.layer==='abutments'||(sp.kind==='end'&&retaining.has(p)))&&!p.slender);
    sp.lo=solid.length?Math.min(...solid.map(p=>p.u[0])):sp.u;sp.hi=solid.length?Math.max(...solid.map(p=>p.u[1])):sp.u;}
  const known=supports.filter(sp=>sp.F!==null);
  if(!known.length)supports.forEach(sp=>sp.F=dMin[1]-3);
  else for(const sp of supports)if(sp.F===null){const n=known.reduce((a,b)=>Math.abs(b.u-sp.u)<Math.abs(a.u-sp.u)?b:a);sp.F=n.F;}
  // A short end span sits over a spill slope: when the opening is shorter than 2.2 times the abutment's height above
  // the next support's ground, the ground at the abutment rises so the slope just fits under the end span.
  for(const [end,next] of [[supports[0],supports[1]],[supports[supports.length-1],supports[supports.length-2]]]){
    if(!next||next===end)continue;const own=end.parts.filter(p=>p.layer==='abutments'||p.layer==='walls');if(!own.length)continue;
    const top=Math.max(...own.map(p=>p.max[1])),clear=end.side<0?next.lo-end.hi:end.lo-next.hi;
    if(clear>0&&clear<2.2*(top-next.F))end.F=Math.max(end.F,Math.min(next.F+clear/2.2,top-1));}
  const grounded=p=>SUB.has(p.layer)&&p.support&&p.support.G!==null&&p.min[1]<=p.support.G+.5;
  const valley=u=>{if(u<=supports[0].u)return supports[0].F;for(let i=1;i<supports.length;i++){const a=supports[i-1],b=supports[i];if(u<=b.u)return a.F+(b.F-a.F)*(u-a.u)/((b.u-a.u)||1);}return supports[supports.length-1].F;};

  // What runs under the bridge: a channel under the widest opening, or a level road under each long opening.
  const water=/river|creek|run|branch|fork|ditch|brook|stream/i.test(waterway),road=!water&&/\b(I|US|SR)-? ?\d+|interstate|road|street|avenue|ramp|highway/i.test(waterway);
  const openings=supports.slice(1).map((b,i)=>{const a=supports[i];return {a,b,lo:a.hi,hi:b.lo,clear:b.lo-a.hi,len:b.u-a.u};}).filter(o=>o.clear>1);
  let channel=null;const roads=[];
  if(water&&openings.length){const o=openings.reduce((a,b)=>b.clear>a.clear?b:a),uc=(o.lo+o.hi)/2;
    let depth=Math.min(1.8,Math.max(.6,.15*o.clear)),bank=2*depth,half=Math.max(1,Math.min(.28*o.clear,14,o.clear/2-.3-bank));
    if(half+bank>o.clear/2){depth=Math.max(.4,(o.clear/2-1.3)/2);bank=2*depth;half=1;}
    const bed=valley(uc)-depth;channel={uc,half,bank,depth,bed,level:bed+.65*depth};}
  if(road&&openings.length){const longest=Math.max(...openings.map(o=>o.len));
    const fit=(o,R)=>{const uA=o.lo+2*Math.max(0,o.a.F-R)+1,uB=o.hi-2*Math.max(0,o.b.F-R)-1;if(uB-uA<7)return null;const w=Math.min(uB-uA-2,24),rc=(uA+uB)/2;
      return {uA:rc-w/2-1,uB:rc+w/2+1,y:R,u0:rc-w/2,u1:rc+w/2};};
    for(const o of openings){if(o.len<.7*longest||o.clear<8)continue;const r=fit(o,Math.min(o.a.F,o.b.F));if(r){r.o=o;roads.push(r);}}
    // A drawn minimum vertical clearance (site hints, west to east) sets the road under the lowest steel above it.
    const hints=site?.crossed_roads||[];
    const lowest=(u0,u1)=>{let y=Infinity;for(const p of parts){if(!SUPER.has(p.layer)&&p.layer!=='bearings')continue;if(p.u[1]<u0||p.u[0]>u1)continue;const a=p.pos;
      for(let i=0;i<a.length;i+=3){const u=a[i]-s*(a[i+2]-zc);if(u>=u0&&u<=u1&&Math.abs(a[i+2]-zc)<=halfW&&a[i+1]<y)y=a[i+1];}}return y;};
    roads.forEach((r,k)=>{const h=hints.length===roads.length?hints[k]:hints.length===1?hints[0]:null,c=h?.min_vertical_clearance_m;if(!(c>0))return;
      for(let pass=0;pass<2;pass++){const y=lowest(r.u0,r.u1);if(!Number.isFinite(y))return;const next=fit(r.o,y-c);if(!next)return;Object.assign(r,next);}r.clearance=c;});}
  const cut=u=>{if(!channel)return 0;const d=Math.abs(u-channel.uc);return d<=channel.half?channel.depth:d>=channel.half+channel.bank?0:channel.depth*(1-(d-channel.half)/channel.bank);};
  const corridor=u=>{let d=Infinity;if(channel)d=Math.abs(u-channel.uc)-channel.half-channel.bank;for(const r of roads)d=Math.min(d,Math.max(r.uA-u,u-r.uB));return d;};
  const roll=(u,z)=>{const k=smooth(Math.abs(z-zc),halfW+8,halfW+45)*(channel||roads.length?smooth(corridor(u),3,15):1);return k*(1.15+Math.sin(u*.045+1.3)*Math.cos(z*.038)*.9+Math.sin(u*.11+z*.07)*.25);};

  // The block: wide enough for the site and every part (guardrail ends included).
  let pu0=Infinity,pu1=-Infinity,pz0=Infinity,pz1=-Infinity;for(const p of parts){pu0=Math.min(pu0,p.u[0]);pu1=Math.max(pu1,p.u[1]);pz0=Math.min(pz0,p.min[2]);pz1=Math.max(pz1,p.max[2]);}
  const sx=Lu+2*Math.max(30,Lu*.5),sz=2*Math.max(45,Lu*.45,halfW*4);
  const ub0=Math.min(mu-sx/2,pu0-8),ub1=Math.max(mu+sx/2,pu1+8),zb0=Math.min(zc-sz/2,pz0-8),zb1=Math.max(zc+sz/2,pz1+8);
  const carriers=parts.filter(p=>DECK.has(p.layer)||p.layer==='approaches');
  let cu0=Infinity,cu1=-Infinity;for(const p of carriers){cu0=Math.min(cu0,p.u[0]);cu1=Math.max(cu1,p.u[1]);}
  const nearU=[cu0-20,cu1+20],nearZ=[zc-halfW-20,zc+halfW+20];
  const stepIn=(t,[a,b])=>Math.min(2.5,.5+.06*Math.max(0,a-t,t-b));

  // Approach roads start at the outer edge of the approach slabs (or of the deck and sidewalks where there are none).
  // The edge is traced every 5 cm across the road, so square, skewed and stepped slab ends are all followed; the road
  // takes the slab's top (crown and cross-fall) and grade there and runs to the block edge.
  const pointAt=(list,x,z,top)=>{let y=top?-Infinity:Infinity;for(const p of list){if(x<p.min[0]-.01||x>p.max[0]+.01||z<p.min[2]-.01||z>p.max[2]+.01)continue;
    const a=p.pos,ix=p.index,n=ix?ix.length:a.length/3;
    for(let t=0;t<n;t+=3){const i0=ix?ix[t]:t,i1=ix?ix[t+1]:t+1,i2=ix?ix[t+2]:t+2;
      const ax=a[3*i0],az=a[3*i0+2],bx=a[3*i1],bz=a[3*i1+2],cx=a[3*i2],cz=a[3*i2+2],d=(bz-cz)*(ax-cx)+(cx-bx)*(az-cz);if(Math.abs(d)<1e-12)continue;
      const l1=((bz-cz)*(x-cx)+(cx-bx)*(z-cz))/d,l2=((cz-az)*(x-cx)+(ax-cx)*(z-cz))/d,l3=1-l1-l2;if(l1<-1e-9||l2<-1e-9||l3<-1e-9)continue;
      const h=l1*a[3*i0+1]+l2*a[3*i1+1]+l3*a[3*i2+1];y=top?Math.max(y,h):Math.min(y,h);}}return y;};
  const STEP=.05,approachRoads=[];
  for(const side of [-1,1]){
    const face=side<0?uW:uE,ext=p=>side<0?p.u[0]:p.u[1];
    let list=carriers.filter(p=>p.layer==='approaches'&&side*(p.uc-face)>0);
    if(!list.length){const end=Math.max(...deckP.map(p=>side*ext(p)));list=parts.filter(p=>(DECK.has(p.layer)||p.layer==='sidewalks')&&side*ext(p)>end-1);}
    const edge=new Map();
    for(const p of list){const a=p.pos,ix=p.index,n=ix?ix.length:a.length/3;
      for(let t=0;t<n;t+=3){const q=[0,1,2].map(k=>{const i=ix?ix[t+k]:t+k;return [a[3*i],a[3*i+2]];});
        const lo=Math.min(q[0][1],q[1][1],q[2][1]),hi=Math.max(q[0][1],q[1][1],q[2][1]);
        for(let k=Math.ceil(lo/STEP-1e-9);k*STEP<=hi+1e-9;k++){const z=k*STEP;let x=null;
          for(let e=0;e<3;e++){const [x1,z1]=q[e],[x2,z2]=q[(e+1)%3];if(z1===z2)continue;const f=(z-z1)/(z2-z1);if(f<-1e-9||f>1+1e-9)continue;
            const xc=x1+(x2-x1)*f;if(x===null||side*(xc-x)>0)x=xc;}
          if(x===null)continue;const cur=edge.get(k);if(cur===undefined||side*(x-cur)>0)edge.set(k,x);}}}
    // The end is the outermost edge: a point more than 3 m short of it both along x (square ends) and along u
    // (skewed or stepped ends) belongs to a part that stops earlier (a notch, a bracket), not to the end.
    let ox=-Infinity,ou=-Infinity;for(const [k,x] of edge){ox=Math.max(ox,side*x);ou=Math.max(ou,side*(x-s*(k*STEP-zc)));}
    for(const [k,x] of [...edge])if(side*x<ox-3&&side*(x-s*(k*STEP-zc))<ou-3)edge.delete(k);
    if(edge.size<2)continue;
    const ks=[...edge.keys()].sort((a,b)=>a-b),zA=ks[0]*STEP,zB=ks[ks.length-1]*STEP;
    const xAt=z=>{const k=Math.round(z/STEP);for(let d=0;d<200;d++){if(edge.has(k-d))return edge.get(k-d);if(edge.has(k+d))return edge.get(k+d);}return edge.get(ks[0]);};
    const zcol=new Set([zA,zB]);for(let z=zA;z<zB;z+=.25)zcol.add(Math.round(z/STEP)*STEP);
    for(let i=1;i<ks.length;i++){if(Math.abs(edge.get(ks[i])-edge.get(ks[i-1]))>.15){zcol.add(ks[i-1]*STEP);zcol.add(ks[i]*STEP);}}
    const cols=[];
    for(const z of [...zcol].sort((a,b)=>a-b)){const xe=xAt(z);let y0=-Infinity,yb=Infinity;
      for(const back of [.03,.1,.25,.5]){y0=pointAt(list,xe-side*back,z,true);if(Number.isFinite(y0)){yb=pointAt(list,xe-side*back,z,false);break;}}
      if(!Number.isFinite(y0))continue;
      const yIn=pointAt(list,xe-side*2,z,true),T=Number.isFinite(yb)?Math.min(1,Math.max(.15,y0-yb)):.3;cols.push({z,xe,y0,T,yIn});}
    if(cols.length<2)continue;
    // A curb or a sidewalk edge is a step in the slab top: add two columns either side of it, found by bisection, so
    // the road keeps the step instead of sloping across it.
    const top=z=>{const xe=xAt(z);for(const back of [.03,.1,.25,.5]){const y=pointAt(list,xe-side*back,z,true);if(Number.isFinite(y))return y;}return NaN;};
    for(let k=cols.length-1;k>0;k--){const A=cols[k-1],B=cols[k];if(!(Math.abs(B.y0-A.y0)>.05&&B.z-A.z>.02))continue;let lo=A.z,hi=B.z;
      for(let it=0;it<8;it++){const m=(lo+hi)/2,y=top(m);if(Math.abs(y-A.y0)<Math.abs(y-B.y0))lo=m;else hi=m;}
      const add=[[lo,A],[hi,B]].filter(([z])=>z>A.z+.004&&z<B.z-.004).map(([z,q])=>({z,xe:xAt(z),y0:q.y0+(top(z)-q.y0||0),T:q.T,yIn:NaN}));
      cols.splice(k,0,...add);}
    let g=0,c=0;for(const q of cols)if(Number.isFinite(q.yIn)){g+=(q.y0-q.yIn)/1.97;c++;}g=Math.max(-.06,Math.min(.06,c?g/c:0));
    const at=z=>{z=Math.min(cols[cols.length-1].z,Math.max(cols[0].z,z));let lo=0,hi=cols.length-1;while(hi-lo>1){const m=(lo+hi)>>1;if(cols[m].z<=z)lo=m;else hi=m;}
      const A=cols[lo],B=cols[hi],f=B.z>A.z?(z-A.z)/(B.z-A.z):0;return {xe:A.xe+(B.xe-A.xe)*f,y0:A.y0+(B.y0-A.y0)*f,T:A.T+(B.T-A.T)*f};};
    const edgeU=side<0?ub0:ub1;if(side*(edgeU-U(at(zc).xe,zc))<.5)continue;
    approachRoads.push({side,zA:cols[0].z,zB:cols[cols.length-1].z,zs:cols.map(q=>q.z),g,edgeU,at,
      end:{at:z=>at(z).xe,a:at(zc).xe},y:(x,z)=>{const q=at(z);return q.y0+g*Math.max(0,side*(x-q.xe));}});}

  // A wall along the side of an approach (an MSE side wall) that runs to the end of the model carries on beyond it:
  // walled approaches are longer than the model. Its line continues to the block edge with its top on the road grade
  // and the exposed height it has at the model's end, so the embankment stays behind it instead of spilling round
  // its end.
  const flankWalls=[];
  for(const r of approachRoads)for(const p of retaining){
    if(p.layer!=='walls'||p.max[0]-p.min[0]<3||p.max[2]-p.min[2]>1.5)continue;
    const left=p.max[2]<=r.zA+.3&&p.max[2]>=r.zA-3,right=p.min[2]>=r.zB-.3&&p.min[2]<=r.zB+3;if(!left&&!right)continue;
    const x0=r.side<0?p.min[0]:p.max[0];if(r.side*(x0-r.at(left?r.zA:r.zB).xe)<-.6)continue;
    let top=-Infinity,bottom=Infinity;const a=p.pos;
    for(let i=0;i<a.length;i+=3)if(r.side*(a[i]-x0)>-.5){top=Math.max(top,a[i+1]);bottom=Math.min(bottom,a[i+1]);}
    if(top-bottom<1)continue;
    flankWalls.push({id:p.id,side:r.side,x0,z0:p.min[2],z1:p.max[2],top,h:top-bottom,edgeU:r.edgeU,topAt:x=>top+r.g*Math.max(0,r.side*(x-x0))});}

  // Grid lines, with breaks at the faces of retaining parts, approach slabs, deck edges and roads.
  const bu=[],bz=[dMin[2],dMax[2]];
  for(const p of [...retaining,...parts.filter(p=>p.layer==='approaches')]){bu.push(p.u[0],p.u[1]);bz.push(p.min[2],p.max[2]);}
  for(const r of approachRoads){bu.push(U(r.end.a,zc));bz.push(r.zA,r.zB,r.zA-1,r.zB+1);}
  for(const r of roads)bu.push(r.uA,r.uB,r.u0,r.u1);
  // A retaining part that runs across the grid lines (a splayed wing) cannot have break lines along its faces: the grid
  // is fine over it instead, so cells on its two sides never share a grid square and the step stays inside the wall.
  const oblique=[...retaining].filter(p=>{const a=p.pos,ix=p.index,n=ix?ix.length:a.length/3;let top=0,bottom=0;
    for(let t=0;t<n;t+=3){const i0=ix?ix[t]:t,i1=ix?ix[t+1]:t+1,i2=ix?ix[t+2]:t+2;
      const ux=a[3*i1]-a[3*i0],uz=a[3*i1+2]-a[3*i0+2],vx=a[3*i2]-a[3*i0],vz=a[3*i2+2]-a[3*i0+2],c=(uz*vx-ux*vz)/2;if(c>0)top+=c;else bottom-=c;}
    return Math.max(top,bottom)<.4*(p.u[1]-p.u[0])*(p.max[2]-p.min[2]);});
  const FINE=.15,fine=(t,k)=>oblique.some(p=>k?t>=p.min[2]-.3&&t<=p.max[2]+.3:t>=p.u[0]-.3&&t<=p.u[1]+.3);
  const us=lines(ub0,ub1,t=>fine(t,0)?FINE:stepIn(t,nearU),bu),zs=lines(zb0,zb1,t=>fine(t,1)?FINE:stepIn(t,nearZ),bz),nu=us.length,nz=zs.length,N=nu*nz;
  const X=new Float64Array(N),Z=new Float64Array(N);for(let j=0;j<nz;j++)for(let i=0;i<nu;i++){const v=j*nu+i;Z[v]=zs[j];X[v]=us[i]+s*(zs[j]-zc);}

  // Each grid vertex under a triangle's plan projection, with the triangle's height there.
  // strict: points on a triangle's edge do not count, so a grid line on a wall face stays outside the wall.
  // grow: points up to this plan distance outside a triangle count too, with the height at the triangle's edge, so a
  // thin member (a diaphragm, a flange) that falls between grid lines still holds the ground down.
  const raster=(p,fn,strict=false,grow=0)=>{const a=p.pos,ix=p.index,n=ix?ix.length:a.length/3,e=strict?-1e-6:1e-7,gu=grow*(1+Math.abs(s));
    for(let t=0;t<n;t+=3){const i0=ix?ix[t]:t,i1=ix?ix[t+1]:t+1,i2=ix?ix[t+2]:t+2;
      const z1=a[3*i0+2],z2=a[3*i1+2],z3=a[3*i2+2],u1=a[3*i0]-s*(z1-zc),u2=a[3*i1]-s*(z2-zc),u3=a[3*i2]-s*(z3-zc),y1=a[3*i0+1],y2=a[3*i1+1],y3=a[3*i2+1];
      const d=(z2-z3)*(u1-u3)+(u3-u2)*(z1-z3);if(Math.abs(d)<1e-10)continue;
      const i_0=lower(us,Math.min(u1,u2,u3)-1e-7-gu),i_1=lower(us,Math.max(u1,u2,u3)+1e-7+gu),j_0=lower(zs,Math.min(z1,z2,z3)-1e-7-grow),j_1=lower(zs,Math.max(z1,z2,z3)+1e-7+grow);
      for(let j=j_0;j<j_1;j++){const z=zs[j];for(let i=i_0;i<i_1;i++){const u=us[i];let l1=((z2-z3)*(u-u3)+(u3-u2)*(z-z3))/d,l2=((z3-z1)*(u-u3)+(u1-u3)*(z-z3))/d,l3=1-l1-l2;
        if(l1<-e||l2<-e||l3<-e){if(!grow)continue;l1=Math.max(0,l1);l2=Math.max(0,l2);l3=Math.max(0,l3);const t=l1+l2+l3;l1/=t;l2/=t;l3/=t;
          const pz=l1*z1+l2*z2+l3*z3,pu=l1*u1+l2*u2+l3*u3,dz=z-pz,dx=(u-pu)+s*dz;if(dx*dx+dz*dz>grow*grow)continue;}
        fn(j*nu+i,l1*y1+l2*y2+l3*y3);}}}};
  // Two kinds of fill: the approach embankments (lbRoad) and fill that supports or buries a part (lbSrc).
  const ceil=new Float64Array(N).fill(Infinity),lbSrc=new Float64Array(N).fill(-Infinity),hard=new Float64Array(N).fill(-Infinity);
  const lbRoad=new Float64Array(N).fill(-Infinity),hardRoad=new Float64Array(N).fill(-Infinity),slab=new Uint8Array(N);
  const target=new Float64Array(N).fill(Infinity),keyTop=new Float64Array(N).fill(-Infinity),wallLb=new Float64Array(N).fill(-Infinity),wall=new Uint8Array(N);
  const wallTop=new Float64Array(N).fill(-Infinity),over=new Float64Array(N).fill(Infinity),deckUnder=new Float64Array(N).fill(Infinity);
  const span=p=>p.uc>uW&&p.uc<uE,later=[];
  // Rails, posts and drains go last: they stand on the structure where there is any under them, else on the ground.
  const box=(p,pad,fn)=>{const i0=lower(us,p.u[0]-pad),i1=lower(us,p.u[1]+pad),j0=lower(zs,p.min[2]-pad),j1=lower(zs,p.max[2]+pad);for(let j=j0;j<j1;j++)for(let i=i0;i<i1;i++)fn(j*nu+i);};
  const ceiling=(p,c)=>{raster(p,(v,y)=>{if(y-c<ceil[v])ceil[v]=y-c;if(y<over[v])over[v]=y;},false,.3);
    // A small part (a bearing, a bolt) can fall between grid lines: its plan box, a little wider, holds the ground
    // below its lowest point.
    if(p.u[1]-p.u[0]<2.5&&p.max[2]-p.min[2]<2.5){const y=p.min[1]-c;box(p,.3,v=>{if(y<ceil[v])ceil[v]=y;if(wall[v]&&p.min[1]<over[v])over[v]=p.min[1];});}};
  // A tall retaining wall (an MSE panel on its leveling pad) stands on the ground along its whole length, so the
  // ground beside it reaches its local bottom where the pad steps up, not only its lowest point.
  for(const p of retaining){const lb=grounded(p)?p.min[1]+EMBED:-Infinity,loc=p.layer==='walls'&&grounded(p)?new Map():null;
    raster(p,(v,y)=>{wall[v]=1;if(lb>wallLb[v])wallLb[v]=lb;if(y>wallTop[v])wallTop[v]=y;
      if(loc){const q=loc.get(v);if(!q)loc.set(v,[y,y]);else{if(y<q[0])q[0]=y;if(y>q[1])q[1]=y;}}},true);
    if(loc)for(const [v,[b,t]] of loc)if(t-b>1.5&&b+EMBED>wallLb[v])wallLb[v]=b+EMBED;}
  for(const f of flankWalls)for(let j=0;j<nz;j++){if(zs[j]<=f.z0+1e-6||zs[j]>=f.z1-1e-6)continue;
    for(let i=0;i<nu;i++){const v=j*nu+i;if(f.side*(X[v]-f.x0)<=-.05)continue;const t=f.topAt(X[v]);
      wall[v]=1;if(t>wallTop[v])wallTop[v]=t;if(t-f.h+EMBED>wallLb[v])wallLb[v]=t-f.h+EMBED;}}
  const behindFace=i=>us[i]<uW-.05||us[i]>uE+.05;
  for(const p of parts){
    if(FURNITURE.has(p.layer)||p.layer==='drainage'){later.push(p);continue;}
    if(retaining.has(p))continue;
    if(p.layer==='approaches'){raster(p,(v,y)=>{slab[v]=1;if(y<target[v])target[v]=y;});continue;}
    if(p.layer==='site'){if(/toe|key/i.test(p.name+' '+p.id))raster(p,(v,y)=>{if(y>keyTop[v])keyTop[v]=y;});else raster(p,(v,y)=>{if(y<target[v])target[v]=y;});continue;}
    if(SUB.has(p.layer)){
      if((p.layer==='foundations'||p.layer==='casing')&&!p.slender){raster(p,(v,y)=>{if(y>hard[v])hard[v]=y;});const y=p.max[1];box(p,.4,v=>{if(!wall[v]&&y>hard[v])hard[v]=y;});}
      else if(grounded(p)){const lb=p.min[1]+EMBED;raster(p,v=>{if(lb>hard[v])hard[v]=lb;});}
      else if(p.layer!=='foundations'&&p.layer!=='casing')raster(p,(v,y)=>{if(y-CLEAR<ceil[v])ceil[v]=y-CLEAR;});
      continue;}
    // A part that reaches down to the ground (a joint between precast pier modules) stands on it.
    if(!DECK.has(p.layer)&&p.min[1]<valley(p.uc)+.6){const lb=p.min[1]+EMBED;raster(p,v=>{if(lb>hard[v])hard[v]=lb;});continue;}
    // Behind the abutment faces the deck rests on backfill.
    if(DECK.has(p.layer))raster(p,(v,y)=>{const i=v%nu;if(!wall[v]&&behindFace(i)&&Math.abs(Z[v]-zc)<=halfW-1&&y<deckUnder[v])deckUnder[v]=y;});
    ceiling(p,SUPER.has(p.layer)?SUPER_CLEAR:CLEAR);}
  // Each is judged point by point from its own local bottom and top: tall pieces (posts) stand in the ground, low
  // pieces (rail beams) stay above it.
  for(const p of later){const loc=new Map();
    raster(p,(v,y)=>{const r=loc.get(v);if(!r)loc.set(v,[y,y]);else{if(y<r[0])r[0]=y;if(y>r[1])r[1]=y;}},false,.25);
    if(!loc.size)box(p,.25,v=>loc.set(v,[p.min[1],p.max[1]]));
    const onStructure=(v,b)=>wall[v]||target[v]<b+.05||over[v]<b+.05;
    let on=0;for(const [v,[b]] of loc)if(onStructure(v,b))on++;
    if(on>=.5*loc.size||(span(p)&&Math.abs(p.c[2]-zc)<=halfW+3)){ceiling(p,CLEAR);continue;}
    if(p.layer==='drainage')continue;
    for(const [v,[b,t]] of loc){if(onStructure(v,b))continue;
      if(t-b>.6||loc.size<=4){if(b+EMBED>hard[v])hard[v]=b+EMBED;}else if(b-.02<ceil[v])ceil[v]=b-.02;}}
  for(let v=0;v<N;v++){if(keyTop[v]>-Infinity&&target[v]===Infinity)target[v]=keyTop[v];
    // Behind an abutment face the deck rests on backfill (away from its edges), where nothing hangs under it.
    if(deckUnder[v]<Infinity){const i=v%nu,j=(v-i)/nu;let free=true;
      for(let dj=-2;dj<=2&&free;dj++)for(let di=-2;di<=2;di++){const ii=i+di,jj=j+dj;if(ii<0||jj<0||ii>=nu||jj>=nz)continue;if(over[jj*nu+ii]<deckUnder[v]-.05){free=false;break;}}
      if(free){slab[v]=1;if(deckUnder[v]<target[v])target[v]=deckUnder[v];}}}
  // Ground beside a part that stands on it reaches the part's bottom.
  for(let j=0;j<nz;j++)for(let i=0;i<nu;i++){const v=j*nu+i;if(wall[v])continue;
    for(let dj=-1;dj<=1;dj++)for(let di=-1;di<=1;di++){const ii=i+di,jj=j+dj;if(ii<0||jj<0||ii>=nu||jj>=nz)continue;const n=jj*nu+ii;if(wall[n]&&wallLb[n]>hard[v])hard[v]=wallLb[n];}}
  // Under an approach road the ground is one slab thickness down, level with the slab underside at the joint.
  // Its shoulders reach 1 m past the road edge, or stop at the outer face of a wall along the road.
  for(const r of approachRoads){let zLo=r.zA-1,zHi=r.zB+1;
    for(const f of flankWalls)if(f.side===r.side){if(f.z1<=r.zA+.3)zLo=Math.max(zLo,f.z0+.01);else zHi=Math.min(zHi,f.z1-.01);}
    for(let j=0;j<nz;j++){const z=zs[j];if(z<zLo||z>zHi)continue;const q=r.at(z);
    for(let i=0;i<nu;i++){const v=j*nu+i,t=r.side*(X[v]-q.xe);if(t<=0)continue;const y=q.y0+r.g*t;
      if(y-q.T>hardRoad[v])hardRoad[v]=y-q.T;if(y-.06<ceil[v])ceil[v]=y-.06;}}}
  // A crossed road and its shoulders are level; next to them fill is cut back at 1:1.25 (a cut slope), steeper than
  // the 1:2 fill, so it only bites where an embankment would spill onto the road.
  const cutC=new Float64Array(N).fill(Infinity),inRoad=new Uint8Array(N);
  for(const r of roads)for(let j=0;j<nz;j++)for(let i=0;i<nu;i++){if(us[i]<r.uA||us[i]>r.uB)continue;const v=j*nu+i;inRoad[v]=1;const g=r.y-.03;if(g<cutC[v])cutC[v]=g;if(g>lbSrc[v])lbSrc[v]=g;}
  // A ledge or bearing just under a slab carries it: the ground follows the lower of the two.
  for(let v=0;v<N;v++){if(target[v]<Infinity&&over[v]<target[v]&&over[v]>target[v]-.6)target[v]=over[v]-.02;
    const t=target[v]<Infinity?target[v]:-Infinity;if(slab[v])lbRoad[v]=Math.max(hardRoad[v],t);else{lbSrc[v]=Math.max(lbSrc[v],hard[v],t);lbRoad[v]=hardRoad[v];}
    // Beside a slab or riprap the ground may rise only at 1:2 from it.
    if(target[v]<Infinity&&target[v]+.25<ceil[v])ceil[v]=target[v]+.25;}

  // 1:2 cones from every source, in two sweeps each way over the grid; retaining parts block them.
  const nb=[[-1,0],[-1,-1],[0,-1],[1,-1]];
  const cone=(f,rise,k=K)=>{for(let pass=0;pass<2;pass++)for(const dir of [1,-1]){
    for(let jj=0;jj<nz;jj++){const j=dir>0?jj:nz-1-jj;for(let ii=0;ii<nu;ii++){const i=dir>0?ii:nu-1-ii,v=j*nu+i;if(wall[v])continue;let h=f[v];
      for(const [a,b] of nb){const i2=i+dir*a,j2=j+dir*b;if(i2<0||j2<0||i2>=nu||j2>=nz)continue;const n=j2*nu+i2;if(wall[n])continue;
        const d=Math.hypot(X[v]-X[n],Z[v]-Z[n]);h=rise?Math.min(h,f[n]+k*d):Math.max(h,f[n]-k*d);}f[v]=h;}}}};
  // Under the bridge, between the abutment faces, embankment fill stays at the natural ground: it wraps round an
  // abutment's corners but does not run into the opening. Spill slopes under the bridge come from the parts
  // standing on them (caps, footings, riprap), which lbSrc carries.
  const natural=(i,j)=>valley(us[i])-cut(us[i])+roll(us[i],zs[j]),open=new Float64Array(N).fill(Infinity);
  for(let j=0;j<nz;j++){if(Math.abs(zs[j]-zc)>halfW)continue;for(let i=0;i<nu;i++)if(us[i]>uW+.3&&us[i]<uE-.3){open[j*nu+i]=natural(i,j);}}
  // The channel keeps its bed against embankment fill too (fill that supports a part may still reach into it).
  if(channel)for(let j=0;j<nz;j++)for(let i=0;i<nu;i++){if(Math.abs(us[i]-channel.uc)>channel.half)continue;const v=j*nu+i;if(channel.bed<cutC[v])cutC[v]=channel.bed;}
  const steep=new Float64Array(N);for(let v=0;v<N;v++)steep[v]=slab[v]?Math.max(hardRoad[v],target[v]):hardRoad[v];
  // Where an embankment and a crossed road's cut compete for the same ground, one even slope joins the road
  // shoulder and the crossed road: the local levels of both (nearly flat cones) and the distances to each give it.
  const roadLevel=Float64Array.from(steep),cutLevel=Float64Array.from(cutC),openLevel=Float64Array.from(open);
  cone(lbSrc,false);cone(lbRoad,false);cone(open,true);cone(ceil,true,K_CLEAR);cone(steep,false,K_STEEP);if(roads.length||channel)cone(cutC,true,K_CUT);
  cone(roadLevel,false,.02);cone(cutLevel,true,.02);cone(openLevel,true,.02);
  // Ground beside a road falls at 1:1.5 at most; where that meets a crossed road's cut or the natural ground under the
  // bridge too soon, one even slope joins the two levels instead (no cliff at either end).
  const blend=(v,st,low,level,k)=>{if(!(st>low)||!Number.isFinite(level)||!Number.isFinite(roadLevel[v]))return st;
    const dR=Math.max(0,(roadLevel[v]-steep[v])/K_STEEP),dL=Math.max(0,(low-level)/k);return Math.max(level,level+(roadLevel[v]-level)*dL/Math.max(1e-6,dL+dR));};
  const H=new Float64Array(N);
  for(let j=0;j<nz;j++)for(let i=0;i<nu;i++){const v=j*nu+i;if(wall[v])continue;
    let h=Math.max(Math.min(natural(i,j),cutC[v]),Math.min(lbRoad[v],open[v],cutC[v]),lbSrc[v]);
    let st=steep[v];if(roads.length||channel)st=blend(v,st,cutC[v],cutLevel[v],K_CUT);st=blend(v,st,open[v],openLevel[v],K);
    if(inRoad[v])h=Math.min(h,cutC[v],ceil[v]);else h=Math.max(Math.min(Math.max(h,st),ceil[v]),hard[v],hardRoad[v]);
    if(target[v]<Infinity)h=target[v];H[v]=h;}
  // A berm under the superstructure between an end wall and the taller cap behind it stays at the wall's top: the
  // fill the wall holds does not rise over it against the cap.
  const near=(j,i,dir,fn)=>{for(let k=1;k<=6;k++){const ii=i+dir*k;if(ii<0||ii>=nu||Math.abs(us[ii]-us[i])>1.5)return null;if(wall[j*nu+ii])return fn(j*nu+ii);}return null;};
  for(let j=0;j<nz;j++)for(let i=0;i<nu;i++){const v=j*nu+i;if(wall[v]||over[v]===Infinity||target[v]<Infinity||!behindFace(i))continue;
    const dir=us[i]<mu?1:-1,front=near(j,i,dir,n=>wallTop[n]),back=near(j,i,-dir,n=>wallTop[n]);
    if(front!==null&&back!==null&&back>front+.3&&H[v]>front+.03&&H[v]<front+1.5)H[v]=Math.max(front+.03,hard[v],hardRoad[v]);}
  // Inside a retaining part the ground takes the height of the nearest outside point, so steps stay inside it.
  const dist=new Float64Array(N);for(let v=0;v<N;v++)dist[v]=wall[v]?Infinity:0;
  for(let pass=0;pass<2;pass++)for(const dir of [1,-1])for(let jj=0;jj<nz;jj++){const j=dir>0?jj:nz-1-jj;for(let ii=0;ii<nu;ii++){const i=dir>0?ii:nu-1-ii,v=j*nu+i;if(!wall[v])continue;
    for(const [a,b] of nb){const i2=i+dir*a,j2=j+dir*b;if(i2<0||j2<0||i2>=nu||j2>=nz)continue;const n=j2*nu+i2,d=dist[n]+Math.hypot(X[v]-X[n],Z[v]-Z[n]);if(d<dist[v]){dist[v]=d;H[v]=H[n];}}}}
  // Under the superstructure (bearing seats, beam ends) a retaining part's top stays clear: the fill behind a
  // backwall does not run over the seat in front of it. Elsewhere fill may pass over a low wall top.
  for(let v=0;v<N;v++)if(wall[v]&&over[v]<Infinity)H[v]=Math.min(H[v],wallTop[v]-.03,over[v]-.03);

  return {s,zc,halfW,nu,nz,us,zs,X,Z,H,wall,channel,roads,approachRoads,flankWalls,water:water?channel:null,
    block:{u0:ub0,u1:ub1,z0:zb0,z1:zb1},supports:supports.map(({kind,side,u,G,F,lo,hi})=>({kind,side,u,G,F,lo,hi})),
    across:u=>channel?Math.abs(u-channel.uc):Infinity,U,debug:{ceil,hard,target,over,wallTop,lbSrc,lbRoad,hardRoad,steep,open,retaining:[...retaining].map(p=>p.id),oblique:oblique.map(p=>p.id),
      grounded:parts.filter(p=>grounded(p)&&!retaining.has(p)&&!((p.layer==='foundations'||p.layer==='casing')&&!p.slender)).map(p=>p.id),
      cover:parts.filter(p=>(p.layer==='foundations'||p.layer==='casing')&&!p.slender).map(p=>p.id)}};
}
