/* Source linkage and presentation checks for the Fletcher / SR 10 additions. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const base=process.env.BRIDGE_TEST_URL||'http://127.0.0.1:8766';
const specs=[
 {id:'fletcher-avenue',count:379,girders:16,part:'pier_2_wall',page:98,county:'Marion'},
 {id:'sr10-i65',count:312,girders:36,part:'deck',page:59,county:'Jasper'}
];
(async()=>{
 const browser=await chromium.launch({...(process.env.BROWSER_EXECUTABLE?{executablePath:process.env.BROWSER_EXECUTABLE}:{}),headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1600,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const result={tested_utc:new Date().toISOString(),models:[],checks:[]};
 try{
  for(const s of specs){
   await page.goto(base+'/#bridge/'+s.id,{waitUntil:'domcontentloaded'});
   await page.waitForFunction(id=>window.bridgeManager?.ready&&bridgeManager.data.id===id,s.id);
   const loaded=await page.evaluate(()=>({count:bridgeManager.data.parts.length,meshes:bridgeManager.viewer.meshes.size,status:bridgeManager.data.detail_status,spans:bridgeManager.data.spans}));
   assert.equal(loaded.count,s.count);assert.equal(loaded.meshes,s.count);assert.equal(loaded.status,'needs_detail');
   await page.locator('[data-category="superstructure"] > summary').click();
   await page.locator('[data-group="'+s.id+':girders"] > summary').click();
   await page.locator('[data-group="'+s.id+':girders"]').getByRole('button',{name:'Isolate group',exact:true}).click();
   assert.equal(await page.evaluate(()=>[...bridgeManager.viewer.meshes.values()].filter(m=>m.visible).length),s.girders);
   await page.locator('#clearIsolation').click();
   await page.locator('#partSearch').fill(s.part);
   await page.locator('.part-button[data-id="'+s.id+':'+s.part+'"]').click();
   assert.deepEqual(await page.evaluate(()=>bridgeManager.selected),[s.id+':'+s.part]);
   await page.locator('#inspector').getByRole('button',{name:'p. '+s.page,exact:true}).click();
   await page.waitForFunction(()=>{const i=document.getElementById('drawingImage');return i.complete&&!i.hidden&&i.naturalWidth>0;});
   assert.equal(await page.locator('#pageNumber').inputValue(),String(s.page));
   await page.locator('#closeDrawing').click();
   await page.locator('#partSearch').fill('');
   await page.evaluate(()=>bridgeManager.select([]));
   await page.locator('[data-tab="coverage"]').click();
   assert.ok((await page.locator('#inspector').innerText()).includes('not_modeled'));
   await page.locator('#openAnalysis').click();
   await page.waitForSelector('#femRun');
   assert.ok((await page.locator('#femDemoNotice').innerText()).includes('Assumed-input demonstration'));
   const download=await page.locator('#modelDownload').getAttribute('href');
   const response=await page.request.get(base+download);assert.ok(response.ok());
   const bytes=await response.body();assert.equal(bytes.subarray(0,4).toString(),'glTF');
   const local=fs.readFileSync(path.join(__dirname,'data/bridges',s.id,'model.glb'));
   assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),crypto.createHash('sha256').update(local).digest('hex'));
   await page.locator('[data-tab="properties"]').click();
   await page.evaluate(()=>{bridgeManager.viewer.grid.visible=false;bridgeManager.viewer.fit(null,'iso');});
   await page.screenshot({path:path.join(__dirname,'data',s.id+'_verified.png')});
   result.models.push({...s,...loaded,download_bytes:bytes.length,source_page_rendered:true});
  }
  await page.goto(base+'/#map',{waitUntil:'domcontentloaded'});await page.waitForSelector('.bridge-card');
  for(const s of specs){
   await page.locator('#countyFilter').selectOption(s.county);
   const card=page.locator('.bridge-card[data-bridge="'+s.id+'"]');
   assert.equal(await card.count(),1);assert.ok((await card.innerText()).includes('More detail needed'));
   assert.equal(await card.locator('a[href="#bridge/'+s.id+'"]').count(),1);
   const img=card.locator('img');await img.scrollIntoViewIfNeeded();
   await page.waitForFunction(id=>{const i=document.querySelector('.bridge-card[data-bridge="'+id+'"] img');return i?.complete&&i.naturalWidth>0;},s.id);
  }
  const saved=await(await page.request.get(base+'/api/analysis/minnich-road')).json();
  assert.ok(saved.available&&saved.latest?.status==='completed'&&saved.latest.current_inputs);
  result.preserved_minnich_run=saved.latest.id;
  result.checks=['Both complete span layouts load','Girder isolation','Component source page rendering','Amber coverage and incomplete details','Assumed-input FEM available','GLB downloads match source bytes','County map cards and preview images','Existing Minnich result remains current'];
  assert.deepEqual(errors,[]);result.page_errors=errors;result.passed=true;
  fs.writeFileSync(path.join(__dirname,'data','batch3_browser_verification.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify(result,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
