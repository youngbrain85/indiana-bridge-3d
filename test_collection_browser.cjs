/* Live result review. Two explicitly labeled Six Mile pressure runs verify the form. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.env.BRIDGE_TEST_URL||'http://127.0.0.1:8766';
const additions=[
 {id:'us35-deer',count:72,part:'beam_0_0',page:20},
 {id:'us224-eight-mile',count:91,part:'beam_0_0',page:9,source:'9548292',sourcePage:8},
 {id:'virginia-avenue',count:146,part:'beam_1',page:31,source:'9548460',sourcePage:28},
 {id:'sr44-little-blue',count:37,part:'deck',page:12},
 {id:'sr1-six-mile',count:24,part:'deck',page:4}
];
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.BROWSER_EXECUTABLE||undefined,headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1680,height:1000}}),errors=[],report={models:[],analysis:[]};
 page.on('pageerror',e=>errors.push(e.message));page.setDefaultTimeout(30000);
 const open=async(id,fem=false)=>{
  await page.goto(base+'/?fem='+(fem?'1':'0')+'#bridge/'+id,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(id=>window.bridgeManager?.ready&&bridgeManager.data.id===id,id);
  if(fem)await page.waitForFunction(id=>window.bridgeAnalysis?.result?.bridge_id===id&&bridgeAnalysis.applied&&bridgeAnalysis.run.current_inputs,id);
 };
 try{
  for(const s of additions){
   await open(s.id);
   assert.equal(await page.evaluate(()=>bridgeManager.viewer.meshes.size),s.count);
   assert.equal(await page.evaluate(()=>bridgeManager.data.detail_status),'needs_detail');
   await page.locator('#partSearch').fill(s.part);
   await page.locator('.part-button[data-id="'+s.id+':'+s.part+'"]').click();
   await page.locator('#inspector').getByRole('button',{name:'p. '+s.page,exact:true}).click();
   await page.waitForFunction(()=>{const i=document.getElementById('drawingImage');return i.complete&&!i.hidden&&i.naturalWidth>0;});
   assert.equal(await page.locator('#pageNumber').inputValue(),String(s.page));
   await page.locator('#closeDrawing').click();
   if(s.source){
    const link=page.locator('#inspector a[href="/assets/'+s.id+'/source/'+s.source+'.pdf#page='+s.sourcePage+'"]');
    assert.equal(await link.count(),1);
    const pdf=await page.request.get(base+(await link.getAttribute('href')).split('#')[0],{headers:{Range:'bytes=0-4'}});
    assert.equal(pdf.status(),206);assert.equal((await pdf.body()).toString(),'%PDF-');
   }
   report.models.push({...s,source_page_rendered:true});
  }
  const ids=fs.readdirSync(path.join(__dirname,'fem/collection')).filter(f=>f.endsWith('.json')).map(f=>f.slice(0,-5));
  assert.equal(ids.length,14);
  for(const id of ids){
   await open(id,true);
   const info=await page.evaluate(()=>({members:bridgeAnalysis.result.members.length,mapped:[...bridgeManager.viewer.meshes.values()].filter(m=>m.geometry.attributes.color).length,
     scope:bridgeAnalysis.result.scope,run:bridgeAnalysis.run.id,passed:bridgeAnalysis.result.verification.passed,
     field_validated:bridgeAnalysis.result.verification.field_validated,inputs:bridgeAnalysis.result.settings,
     finite:[...bridgeManager.viewer.meshes.values()].every(m=>m.geometry.attributes.position.array.every(Number.isFinite))}));
   assert.equal(info.members,info.mapped);assert(info.passed&&info.finite&&!info.field_validated);
   assert((await page.locator('#femDemoNotice').textContent()).includes('Assumed-input demonstration'));
   assert(!/undefined|NaN/.test(await page.locator('#inspector').innerText()));
   assert((await page.locator('#femLegend').textContent()).includes('Gray: not analyzed'));
   await page.selectOption('#femField','deflection_mm');await page.selectOption('#femScale','100');
   assert.equal(await page.evaluate(()=>bridgeManager.viewer.analysis.deformationScale),100);
   const csv=await page.request.get(base+'/api/analysis/runs/'+info.run+'/samples.csv');
   assert(csv.ok());assert((await csv.text()).includes('assumed_input_demo'));
   await page.locator('#femMesh').click();
   assert(await page.evaluate(()=>!!bridgeManager.viewer.analysisGeometry&&!bridgeManager.viewer.root.visible));
   await page.locator('#femMeshBack').click();
   assert(await page.evaluate(()=>!bridgeManager.viewer.analysisGeometry&&bridgeManager.viewer.root.visible));
   await page.selectOption('#femField','stress_MPa');await page.selectOption('#femScale','0');
   if(['us35-deer','sr1-wabash','us421-wildcat','sr1-six-mile'].includes(id)){
    await page.evaluate(()=>document.getElementById('inspector').scrollTop=0);
    await page.screenshot({path:path.join(__dirname,'data',id+'-fem-verified.png')});
   }
   report.analysis.push({id,...info});
  }
  await open('sr1-six-mile',true);
  const baseline=await page.evaluate(()=>bridgeAnalysis.result.max_deflection_mm);
  const run=async pressure=>{
   const old=await page.evaluate(()=>bridgeAnalysis.run.id);
   await page.fill('#fem_pressure_kPa',String(pressure));
   assert(await page.locator('#femDirty').isVisible());await page.locator('#femRun').click();
   await page.waitForFunction(old=>bridgeAnalysis.run?.id!==old&&bridgeAnalysis.run.status==='completed'&&bridgeAnalysis.applied&&bridgeAnalysis.result?.settings.pressure_kPa===bridgeAnalysis.options.pressure_kPa,old,{timeout:60000});
   return page.evaluate(()=>({id:bridgeAnalysis.run.id,deflection:bridgeAnalysis.result.max_deflection_mm}));
  };
  const doubled=await run(2);assert(Math.abs(doubled.deflection/baseline-2)<1e-7);
  const restored=await run(1);assert(Math.abs(restored.deflection/baseline-1)<1e-7);
  report.form_runs={doubled,restored};
  await page.reload({waitUntil:'domcontentloaded'});await page.waitForFunction(id=>bridgeAnalysis.applied&&bridgeAnalysis.run.id===id,restored.id);
  await page.setViewportSize({width:390,height:844});
  await page.locator('.mobile-tabs [data-pane="inspector"]').click();
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  assert(await page.locator('#femRun').isVisible());
  assert.deepEqual(errors,[]);report.page_errors=errors;report.passed=true;
  fs.writeFileSync(path.join(__dirname,'data/collection-browser-verification.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify({passed:true,models:report.models.length,analysis:report.analysis.length,form_runs:report.form_runs,page_errors:errors}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
