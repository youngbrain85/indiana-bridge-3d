/* Inspection app end to end: draw defects on the sheets, add a photo, override a condition state, reload,
   check the AASHTO element table and the backup, then see the defects placed on the members in 3D.
   Run with the app listening on localhost:8766 (python server.py --port 8766). */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const path=require('node:path');
const base=process.env.BRIDGE_TEST_URL||'http://127.0.0.1:8766';
const shots=process.env.INSPECTION_SHOTS||null;

(async()=>{
 const browser=await chromium.launch({...(process.env.BROWSER_EXECUTABLE?{executablePath:process.env.BROWSER_EXECUTABLE}:{}),headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const context=await browser.newContext({viewport:{width:1440,height:900},reducedMotion:'reduce',acceptDownloads:true});
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const shot=name=>shots&&page.screenshot({path:path.join(shots,name+'.png')});
 await page.goto(base+'/inspect#beechwood');
 await page.waitForSelector('dialog[open]');
 await page.fill('dialog input[type=text]','J. Rivera, M. Chen');
 await page.click('dialog button.primary');
 await page.waitForFunction(()=>window.__inspect.state.inspection&&!document.querySelector('dialog[open]'));

 // Page coordinates of a point inside an inspectable region: the centre of the part's largest piece,
 // nudged to a grid point that the region really contains.
 const pointIn=(viewId,part,du=0,dv=0)=>page.evaluate(({viewId,part,du,dv})=>{
  const s=window.__inspect.state,v=s.sheet.views.find(x=>x.id===viewId),reg=v.regions.find(r=>r.part===part);
  const inside=([x,y],rings)=>{let c=false;for(const ring of rings)for(let i=0,j=ring.length-1;i<ring.length;j=i++){const [xi,yi]=ring[i],[xj,yj]=ring[j];if((yi>y)!==(yj>y)&&x<(xj-xi)*(y-yi)/(yj-yi)+xi)c=!c;}return c;};
  const poly=reg.polygons.slice().sort((a,b)=>b[0].length-a[0].length)[0];const xs=poly[0].map(p=>p[0]),ys=poly[0].map(p=>p[1]);
  let best=null;for(let i=1;i<20&&!best;i++)for(let j=1;j<20&&!best;j++){const p=[(Math.min(...xs)+Math.max(...xs))/2+(i%2?1:-1)*Math.floor(i/2)*0.01,(Math.min(...ys)+Math.max(...ys))/2+(j%2?1:-1)*Math.floor(j/2)*0.01];if(inside(p,poly))best=p;}
  const uv=[best[0]+du,best[1]+dv];const [px,py,pw,ph]=v.placement;const svg=document.querySelector('.sheet-svg'),r=svg.getBoundingClientRect(),vb=svg.viewBox.baseVal;
  const mm=[px*420+uv[0]*pw*420,py*297+uv[1]*ph*297];return [r.left+(mm[0]-vb.x)/vb.width*r.width,r.top+(mm[1]-vb.y)/vb.height*r.height];},{viewId,part,du,dv});
 const viewPoint=(viewId,u,v)=>page.evaluate(({viewId,u,v})=>{const s=window.__inspect.state,view=s.sheet.views.find(x=>x.id===viewId);const [px,py,pw,ph]=view.placement;const svg=document.querySelector('.sheet-svg'),r=svg.getBoundingClientRect(),vb=svg.viewBox.baseVal;
  const mm=[px*420+u*pw*420,py*297+v*ph*297];return [r.left+(mm[0]-vb.x)/vb.width*r.width,r.top+(mm[1]-vb.y)/vb.height*r.height];},{viewId,u,v});
 const stroke=async pts=>{await page.mouse.move(...pts[0]);await page.mouse.down();for(let k=1;k<pts.length;k++){const [a,b]=[pts[k-1],pts[k]];for(let t=1;t<=8;t++)await page.mouse.move(a[0]+(b[0]-a[0])*t/8,a[1]+(b[1]-a[1])*t/8);}await page.mouse.up();};
 const openSheet=async id=>{await page.click(`.sheet-item:has(.sheet-code:text-is("${id}"))`);await page.waitForFunction(id=>window.__inspect.state.sheet.id===id&&document.querySelector('.sheet-layer text'),id);};
 const pick=async name=>{await page.click('text=Add defect');await page.click(`.pick:has(.pick-name:text-is("${name}"))`);await page.waitForFunction(()=>window.__inspect.state.panel==='draw');};
 const form=()=>page.waitForFunction(()=>window.__inspect.state.panel==='form');

 // 1. A crack on the deck soffit of span A, between girders 1 and 2: deck (12) is found from the sketch,
 //    RC cracking 1130 is used, 0.02 in suggests CS 2, the quantity is the traced length x 1 ft.
 await openSheet('DK-2');
 await pick('Cracking');
 await stroke([await viewPoint('DK2-A',0.30,0.25),await viewPoint('DK2-A',0.42,0.27),await viewPoint('DK2-A',0.55,0.24)]);
 await form();
 let draft=await page.evaluate(()=>window.__inspect.state.draft);
 assert.equal(draft.part,'deck');assert.equal(draft.element_code,12);assert.equal(draft.defect_code,1130);assert.equal(draft.unit,'sq ft');
 assert.ok(draft.quantity>=19&&draft.quantity<=22,`deck crack band ${draft.quantity} sq ft`);
 assert.match(draft.location,/^STA 105\+\d\d\.\d · \d+(\.\d)? ft RT$/);
 await page.fill('.defect-form .field input[type=number] >> nth=0','0.02');await page.press('.defect-form .field input[type=number] >> nth=0','Tab');
 await page.waitForFunction(()=>window.__inspect.state.draft.cs===2&&window.__inspect.state.draft.cs_suggested===2);
 await shot('inspection-form');
 await page.click('button:has-text("Save defect")');
 await page.waitForFunction(()=>window.__inspect.state.defects.length===1&&window.__inspect.state.panel==='list');

 // 2. A spall on the south face of the bent 2 cap, with a photo: 1.5 in deep suggests CS 3; the quantity is
 //    the length of cap affected (ft).
 await openSheet('BT-2');
 await pick('Delamination / Spall / Patched Area');
 const c=await pointIn('B2-S','b2_cap');
 await stroke([[c[0]-30,c[1]-12],[c[0]+30,c[1]-14],[c[0]+34,c[1]+14],[c[0]-28,c[1]+12]]);
 await form();
 draft=await page.evaluate(()=>window.__inspect.state.draft);
 assert.equal(draft.part,'b2_cap');assert.equal(draft.element_code,234);assert.equal(draft.kind,'area');
 await page.click('.segmented.choice button:has-text("Spall")');
 await page.fill('.defect-form .field input[type=number] >> nth=0','1.5');await page.press('.defect-form .field input[type=number] >> nth=0','Tab');
 await page.waitForFunction(()=>window.__inspect.state.draft.cs_suggested===3);
 const jpeg=await page.evaluate(()=>{const c=document.createElement('canvas');c.width=1200;c.height=900;const x=c.getContext('2d');x.fillStyle='#8a8f92';x.fillRect(0,0,1200,900);x.fillStyle='#5b4636';x.beginPath();x.ellipse(600,450,260,170,0,0,7);x.fill();return c.toDataURL('image/jpeg',.8).split(',')[1];});
 await page.setInputFiles('.photo-add:has-text("Add from files") input',{name:'IMG_0412.jpg',mimeType:'image/jpeg',buffer:Buffer.from(jpeg,'base64')});
 await page.waitForSelector('.photo img');
 await page.click('button:has-text("Save defect")');
 await page.waitForFunction(()=>window.__inspect.state.defects.length===2);

 // 3. A torn bearing, tapped as a point; the inspector raises CS 3 to CS 4, which needs a reason and flags
 //    a structural review.
 await pick('Bulging, Splitting or Tearing');
 const b=await pointIn('B2-S','b2_bearing_2_-1');
 await page.mouse.click(...b);
 await form();
 draft=await page.evaluate(()=>window.__inspect.state.draft);
 assert.equal(draft.part,'b2_bearing_2_-1');assert.equal(draft.element_code,310);assert.equal(draft.quantity,1);
 await page.click('label.check:has-text("Splitting or tearing") input');
 await page.waitForFunction(()=>window.__inspect.state.draft.cs_suggested===3);
 await page.click('.cs-chip:has-text("CS 4")');
 await page.click('button:has-text("Save defect")');
 assert.equal(await page.evaluate(()=>window.__inspect.state.defects.length),2,'a changed CS without a reason is not saved');
 await page.fill('#csReason','Split through two elastomer layers; bearing rotated.');
 await page.click('button:has-text("Save defect")');
 await page.waitForFunction(()=>window.__inspect.state.defects.length===3);
 await shot('inspection-sheet');

 // Saved on the device: a reload keeps the inspection, defects and photo.
 await page.reload();
 await page.waitForFunction(()=>window.__inspect.state.defects?.length===3);
 const saved=await page.evaluate(async()=>{const s=window.__inspect.state;const photos=await window.__inspect.store.inspectionPhotos(s.inspection.id);return {defects:s.defects.map(d=>({n:d.number,code:d.defect_code,el:d.element_code,cs:d.cs,q:d.quantity,review:d.structural_review})),photos:photos.map(p=>({bytes:p.bytes,w:p.width,name:p.file_name})),outbox:(await window.__inspect.store.outbox()).length};});
 assert.deepEqual(saved.defects.map(d=>[d.n,d.code,d.el,d.cs]),[[1,1130,12,2],[2,1080,234,3],[3,2230,310,4]]);
 assert.equal(saved.defects[2].review,true);
 assert.equal(saved.photos.length,1);assert.ok(saved.photos[0].bytes>1000&&saved.photos[0].w===1200);
 assert.match(saved.photos[0].name,/^\d{8}_\d{6}_BT-2_1080_D2_[0-9a-f]{6}\.jpg$/);
 assert.equal(saved.outbox,1+3+1,'inspection, defects and photo wait for cloud sync');

 // AASHTO element table: CS 1 is the element total less the defect quantities.
 await page.click('#tabElements');
 await page.waitForSelector('table.summary');
 const table=await page.evaluate(()=>Object.fromEntries([...document.querySelectorAll('.summary .element-row')].map(r=>[r.cells[0].querySelector('b').textContent,[...r.cells].slice(1).map(c=>Number(c.textContent.replace(/,/g,'')))])));
 assert.equal(table['12'][0],8316);assert.equal(table['12'][2],saved.defects[0].q);assert.equal(table['12'][1],8316-saved.defects[0].q);
 assert.equal(table['234'][3],saved.defects[1].q);assert.equal(table['310'][0],16);assert.equal(table['310'][4],1);assert.equal(table['310'][1],15);
 const download=page.waitForEvent('download');await page.click('button:has-text("Download backup")');
 const backup=JSON.parse(require('node:fs').readFileSync(await (await download).path(),'utf8'));
 assert.equal(backup.format,'bridge-inspection-backup');assert.equal(backup.defects.length,3);assert.ok(backup.photos[0].data_url.startsWith('data:image/jpeg;base64,'));
 await shot('inspection-elements');

 // Cloud sync against a stand-in for the Supabase API: sign-in, upserts in foreign-key order, the photo upload,
 // then the pull. Every column the app sends must exist in supabase/schema.sql.
 const schema=require('node:fs').readFileSync(path.join(__dirname,'supabase/schema.sql'),'utf8');
 const columns=Object.fromEntries([...schema.matchAll(/create table if not exists public\.(\w+) \(([\s\S]*?)\n\);/g)].map(m=>[m[1],m[2].split('\n').map(l=>l.trim().match(/^([a-z_]+) /)?.[1]).filter(c=>c&&c!=='constraint')]));
 const cloud='https://inspection-test.supabase.co',sent=[];
 const b64=o=>Buffer.from(JSON.stringify(o)).toString('base64url');
 const token=`${b64({alg:'HS256',typ:'JWT'})}.${b64({sub:'11111111-1111-1111-1111-111111111111',role:'authenticated',aud:'authenticated',email:'inspector@example.com',exp:Math.floor(Date.now()/1000)+3600})}.sig`;
 const user={id:'11111111-1111-1111-1111-111111111111',aud:'authenticated',role:'authenticated',email:'inspector@example.com',app_metadata:{},user_metadata:{},created_at:new Date().toISOString()};
 await page.route(cloud+'/**',async route=>{const r=route.request(),u=new URL(r.url());sent.push({method:r.method(),path:u.pathname,query:u.search,body:r.postDataBuffer()});
  const json=(body,status=200)=>route.fulfill({status,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify(body)});
  if(r.method()==='OPTIONS')return route.fulfill({status:204,headers:{'access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'*'}});
  if(u.pathname==='/auth/v1/token')return json({access_token:token,token_type:'bearer',expires_in:3600,expires_at:Math.floor(Date.now()/1000)+3600,refresh_token:'refresh',user});
  if(u.pathname.startsWith('/storage/v1/object/'))return json({Key:u.pathname.replace('/storage/v1/object/','')});
  if(u.pathname.startsWith('/rest/v1/'))return r.method()==='GET'?json([]):route.fulfill({status:201,headers:{'access-control-allow-origin':'*'},body:''});
  return json({message:'not mocked'},404);});
 await page.click('#settingsButton');
 await page.fill('dialog input[type=url]',cloud);await page.fill('dialog input[placeholder="Publishable or anon key"]','sb_publishable_TESTKEY');
 await page.fill('dialog input[type=email]','inspector@example.com');await page.fill('dialog input[type=password]','field-pass');
 await page.click('dialog button:has-text("Sign in")');
 await page.waitForFunction(()=>/^Synced/.test(document.getElementById('syncStatus').textContent),null,{timeout:30000});
 const writes=sent.filter(x=>x.method==='POST'&&x.path.startsWith('/rest/v1/'));
 assert.deepEqual(writes.map(w=>w.path),['/rest/v1/inspections','/rest/v1/defects','/rest/v1/defect_photos'],'inspections, then defects, then photos');
 for(const w of writes){const table=w.path.split('/').pop();const rows=JSON.parse(w.body.toString());
  for(const row of rows)for(const key of Object.keys(row))assert.ok(columns[table].includes(key),`${table}.${key} is not in supabase/schema.sql`);
  assert.ok(!rows.some(r=>'blob' in r||'uploaded' in r),'local-only photo fields stay on the device');}
 const upload=sent.find(x=>x.path.startsWith('/storage/v1/object/defect-photos/'));
 assert.match(upload.path,/^\/storage\/v1\/object\/defect-photos\/[0-9a-f-]{36}\/[0-9a-f-]{36}\/[0-9a-f-]{36}\.jpg$/);
 assert.ok(upload.body.length>1000,'the photo bytes are uploaded');
 assert.equal(await page.evaluate(async()=>(await window.__inspect.store.outbox()).length),0,'outbox is empty after sync');
 assert.ok(sent.some(x=>x.method==='GET'&&x.path==='/rest/v1/defects'&&/bridge_id=eq\.beechwood/.test(x.query)),'pulls the bridge\'s defects');
 await page.unroute(cloud+'/**');

 // Phone width: no sideways scrolling, sheet and panel both on screen.
 await page.setViewportSize({width:390,height:844});
 await page.click('#tabDefects');
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'no horizontal scroll at 390 px');
 await shot('inspection-phone');
 await page.setViewportSize({width:1440,height:900});

 // 3D: the defects saved on this device are placed on their members.
 await page.goto(base+'/#bridge/beechwood');
 await page.waitForFunction(()=>window.bridgeManager?.ready&&bridgeManager.data.id==='beechwood',null,{timeout:180000});
 assert.equal(await page.isVisible('#inspectLink'),true);
 await page.click('#defectsToggle');
 await page.waitForFunction(()=>bridgeManager.viewer.defectGroup.children.length===3&&bridgeManager.viewer.defectGroup.visible);
 const near=await page.evaluate(async()=>{const v=bridgeManager.viewer,store=window.BridgeInspection.store;const res=[];
  for(const g of v.defectGroup.children){const d=await store.get('defects',g.userData.defect);const mesh=[...v.meshes.values()].find(m=>m.name===d.part);mesh.geometry.computeBoundingBox();
   const pb=mesh.geometry.boundingBox.clone().expandByScalar(.05);const db=v.defectBoxes.get(d.id).box;res.push({part:d.part,inside:pb.containsBox(db)});}return res;});
 for(const n of near)assert.ok(n.inside,`${n.part}: defect lies on its member`);
 await page.evaluate(()=>{const d=bridgeManager.viewer.defectGroup.children[1].userData.defect;window.bridgeDefects.select(d,true);});
 await page.waitForSelector('.defect-details .defect-tag');
 assert.match(await page.textContent('.defect-details'),/D2.*1080 Delamination/s);
 await page.waitForSelector('.defect-details .defect-photos img');
 await shot('inspection-3d');
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({defects:saved.defects,element_table:table,placed:near},null,1));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
