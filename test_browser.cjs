/* Run with the app listening on localhost:8766. Uses only existing model assets. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.env.BRIDGE_TEST_URL||'http://127.0.0.1:8766';
const out=path.join(__dirname,'data');
(async()=>{
 const browser=await chromium.launch({...(process.env.BROWSER_EXECUTABLE?{executablePath:process.env.BROWSER_EXECUTABLE}:{}),headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const context=await browser.newContext({viewport:{width:1600,height:1000},reducedMotion:'reduce'});
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const result={tested_utc:new Date().toISOString(),models:[],checks:[]};
 const screen=name=>page.screenshot({path:path.join(out,name+'.png')});
 const open=async id=>{await page.evaluate(id=>location.hash='#bridge/'+id,id);await page.waitForFunction(id=>window.bridgeManager?.ready&&bridgeManager.data.id===id,id);};
 try{
  await page.goto(base+'/#map',{waitUntil:'domcontentloaded'});await page.waitForSelector('.bridge-card');
  assert.equal(await page.locator('.bridge-card').count(),9);
  await page.locator('#countyFilter').selectOption('Vanderburgh');assert.equal(await page.locator('.bridge-card').count(),3);
  await page.locator('#countyFilter').selectOption('');await page.locator('#statusFilter').selectOption('complete');assert.equal(await page.locator('.bridge-card').count(),1);
  await page.locator('#statusFilter').selectOption('');await page.locator('#bridgeSearch').fill('no-such-bridge');assert.equal(await page.locator('.bridge-card').count(),0);await page.locator('#bridgeSearch').fill('');
  result.checks.push('Catalog / County / detail-status / empty-search filters');
  const ids=await page.evaluate(async()=>(await(await fetch('/api/catalog')).json()).bridges.map(b=>b.id));
  for(const id of ids){await open(id);const model=await page.evaluate(()=>({id:bridgeManager.data.id,components:bridgeManager.data.parts.length,meshes:bridgeManager.viewer.meshes.size,normals:[...bridgeManager.viewer.meshes.values()].every(m=>!!m.geometry.attributes.normal)}));assert.equal(model.components,model.meshes);assert.ok(model.normals);result.models.push(model);}
  result.checks.push('All nine GLBs match database components and have lit geometry');
  await open('beechwood');await screen('beechwood_desktop');
  await page.locator('[data-category="superstructure"] > summary').click();
  await page.locator('[data-group="beechwood:girders"] summary').click();
  await page.locator('[data-group="beechwood:girders"]').getByRole('button',{name:'Isolate group',exact:true}).click();
  assert.deepEqual(await page.evaluate(()=>({selected:bridgeManager.selected.length,visible:[...bridgeManager.viewer.meshes.values()].filter(m=>m.visible).length})),{selected:12,visible:12});
  await page.locator('#clearIsolation').click();
  await page.locator('#partSearch').fill('girder_A1');
  await page.locator('[data-group="beechwood:girders"]').getByRole('button',{name:'Isolate group',exact:true}).click();
  assert.equal(await page.evaluate(()=>[...bridgeManager.viewer.meshes.values()].filter(m=>m.visible).length),12);
  await page.locator('#clearIsolation').click();
  result.checks.push('Parent isolation includes all 12 girders even with one search result');
  await page.locator('#partSearch').fill('b2_column_L');await page.locator('.part-button').click();
  assert.equal((await page.evaluate(()=>bridgeManager.selected))[0],'beechwood:b2_column_L');
  await page.locator('#inspector').getByRole('button',{name:'p. 38',exact:true}).click();
  await page.waitForFunction(()=>document.getElementById('drawingImage').complete&&!document.getElementById('drawingImage').hidden);
  assert.equal(await page.locator('#pageNumber').inputValue(),'38');await screen('drawing_desktop');
  await page.locator('#nextPage').click();assert.equal(await page.locator('#pageNumber').inputValue(),'39');
  await page.locator('#pageNumber').fill('9999');await page.locator('#pageNumber').press('Tab');assert.equal(await page.locator('#pageNumber').inputValue(),'63');
  await page.locator('#closeDrawing').click();await page.locator('#partSearch').fill('');
  await page.getByRole('button',{name:'Focus selection',exact:true}).click();await screen('component_desktop');
  result.checks.push('Component search, real PDF p.38, page navigation and bounds');
  await page.locator('#clipEnabled').check();await page.locator('#clipPosition').fill('50');assert.equal(await page.evaluate(()=>bridgeManager.viewer.clipping),true);await page.locator('#clipEnabled').uncheck();
  await page.locator('#deckOpacity').fill('30');assert.equal(await page.evaluate(()=>bridgeManager.viewer.meshes.get('beechwood:deck').material.opacity),.3);
  await page.locator('#deckOpacity').fill('100');result.checks.push('Clipping and deck transparency');
  await page.getByRole('button',{name:'Isolate selection',exact:true}).click();
  const hit=await page.evaluate(()=>{const v=bridgeManager.viewer,m=v.meshes.get('beechwood:b2_column_L');m.geometry.computeBoundingBox();const p=m.geometry.boundingBox.getCenter(v.camera.position.clone()).project(v.camera);const r=v.renderer.domElement.getBoundingClientRect();bridgeManager.select([]);return{x:r.left+(p.x+1)*r.width/2,y:r.top+(1-p.y)*r.height/2};});
  await page.mouse.click(hit.x,hit.y);assert.equal((await page.evaluate(()=>bridgeManager.selected))[0],'beechwood:b2_column_L');result.checks.push('3D raycast picking selects the database component');
  await page.locator('#clearIsolation').click();
  // Deliberately race two real bridge loads; only the final selection may be installed.
  await page.evaluate(()=>{location.hash='#bridge/21st-street-i465';setTimeout(()=>location.hash='#bridge/us421-wildcat',20);});
  await page.waitForFunction(()=>bridgeManager.ready&&bridgeManager.data.id==='us421-wildcat');assert.equal(await page.evaluate(()=>bridgeManager.viewer.meshes.size),1057);
  await page.waitForTimeout(150);assert.equal(await page.evaluate(()=>bridgeManager.data.id),'us421-wildcat');result.checks.push('Rapid bridge switching cancels stale loads');
  await page.setViewportSize({width:390,height:844});await open('beechwood');
  await page.locator('.mobile-tabs [data-pane="tree"]').click();await page.locator('#partSearch').fill('girder_A1');await page.locator('.part-button').click();
  await page.locator('.mobile-tabs [data-pane="inspector"]').click();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await screen('mobile_inspector');
  await page.locator('.mobile-tabs [data-pane="viewer"]').click();await page.locator('#fitModel').click();await screen('mobile_viewer');
  await page.locator('.back-link').click();await page.waitForSelector('#mapView',{state:'visible'});await page.locator('#fitState').click();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await screen('mobile_map');
  await page.setViewportSize({width:844,height:390});await open('sr62-tekoppel');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);result.checks.push('390px portrait and 844px landscape panel navigation without horizontal overflow');
  await page.setViewportSize({width:1600,height:1000});await page.evaluate(()=>location.hash='#map');await page.waitForSelector('#mapView',{state:'visible'});await page.locator('#fitState').click();await screen('map_desktop');
  await page.locator('#catalogButton').click();assert.equal(await page.locator('#catalogContent .data-table tr').count(),10);await page.locator('#closeCatalog').click();result.checks.push('Collection summary / database export entry point');
  // Force the road service to fail while keeping local HTTP available.
  await context.route('https://carto.nationalmap.gov/**',route=>route.abort());
  await page.locator('#roadsToggle').uncheck();await page.locator('#roadsToggle').check();
  await page.waitForFunction(()=>/unavailable|delayed/.test(document.getElementById('mapStatus').textContent));
  assert.equal(await page.locator('.bridge-card').count(),9);await open('sr58-white');assert.equal(await page.evaluate(()=>bridgeManager.viewer.meshes.size),41);result.checks.push('Road-service failure leaves local map and models usable');
  assert.deepEqual(errors,[]);result.page_errors=errors;result.passed=true;
  fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
