const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const base=process.env.BRIDGE_TEST_URL||'http://127.0.0.1:8766';
(async()=>{
  const browser=await chromium.launch({executablePath:process.env.BROWSER_EXECUTABLE||undefined,headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const page=await browser.newPage({viewport:{width:1600,height:1000}}),errors=[];
  page.setDefaultTimeout(25000);page.on('pageerror',e=>errors.push(String(e)));
  try{
    await page.goto(base+'/?fem=1#bridge/minnich-road',{waitUntil:'domcontentloaded'});
    await page.locator('#femDemoNotice').waitFor();
    const run=async()=>{
      const old=await page.evaluate(()=>bridgeAnalysis.run?.id);
      await page.locator('#femRun').click();
      await page.waitForFunction(old=>bridgeAnalysis.run?.id!==old&&bridgeAnalysis.run?.status==='completed'&&bridgeAnalysis.applied&&bridgeAnalysis.result?.settings.pressure_kPa===bridgeAnalysis.options.pressure_kPa,old,{timeout:60000});
      return page.evaluate(()=>({id:bridgeAnalysis.run.id,settings:bridgeAnalysis.result.settings,stress:bridgeAnalysis.result.max_stress_MPa,displacement:bridgeAnalysis.result.max_deflection_mm,count:bridgeAnalysis.result.members.length,verified:bridgeAnalysis.result.verification.passed,current:bridgeAnalysis.run.current_inputs}));
    };
    await page.locator('#femAssumedProperties summary').click();
    await page.locator('#femDefaults').click();
    const first=await run();assert.equal(first.count,197);assert(first.verified&&first.current);
    assert((await page.locator('#femLegend').textContent()).includes('ASSUMED-INPUT DEMONSTRATION'));
    await page.selectOption('#femFamily','all');
    assert.equal(await page.evaluate(()=>[...bridgeManager.viewer.meshes.values()].filter(m=>m.geometry.attributes.color).length),197);
    await page.selectOption('#femFamily','column');
    assert.equal(await page.evaluate(()=>[...bridgeManager.viewer.meshes.values()].filter(m=>m.geometry.attributes.color).length),18);
    await page.selectOption('#femFamily','girder');
    await page.fill('#fem_pressure_kPa','2');assert.equal(await page.locator('#femDirty').isVisible(),true);
    const doubled=await run();assert(Math.abs(doubled.displacement/first.displacement-2)<1e-7);
    await page.selectOption('#femCase','demo_eccentric');
    const eccentric=await run();assert.equal(eccentric.settings.case,'demo_eccentric');
    await page.selectOption('#femFamily','girder');
    await page.selectOption('#femField','deflection_mm');await page.selectOption('#femScale','100');
    assert.equal(await page.evaluate(()=>bridgeManager.viewer.analysis.deformationScale),100);
    await page.locator('#femMesh').click();assert(await page.evaluate(()=>!!bridgeManager.viewer.analysisGeometry&&!bridgeManager.viewer.root.visible));
    assert((await page.locator('#femLegend').innerText()).includes('ASSUMED-INPUT DEMONSTRATION'));
    await page.screenshot({path:'data/minnich-demo-fe-mesh.png'});
    await page.locator('#femMeshBack').click();assert(await page.evaluate(()=>!bridgeManager.viewer.analysisGeometry&&bridgeManager.viewer.root.visible));
    await page.selectOption('#femScale','0');await page.selectOption('#femField','stress_MPa');
    const csv=await page.request.get(base+'/api/analysis/runs/'+eccentric.id+'/samples.csv');assert(csv.ok());const csvText=await csv.text();assert(csvText.includes('minnich-road:column_1_0_0'));assert(csvText.includes('assumed_input_demo'));assert(csvText.includes('hypothetical_connected_frame_shell_demo,true,false'));
    const js=await page.request.get(base+'/api/analysis/runs/'+eccentric.id+'/result.json');assert((await js.json()).demonstration);
    // Restore default inputs and save a ready-to-view example for the user.
    await page.locator('#femAssumedProperties summary').click();await page.locator('#femDefaults').click();
    const saved=await run();
    await page.reload({waitUntil:'domcontentloaded'});
    await page.waitForFunction(id=>bridgeAnalysis.run?.id===id&&bridgeAnalysis.applied,saved.id);
    assert.equal(await page.locator('#femFamily').inputValue(),'girder');
    await page.screenshot({path:'data/minnich-demo-workspace.png'});
    await page.setViewportSize({width:390,height:844});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    await page.goto(base+'/?fem=1#bridge/beechwood',{waitUntil:'domcontentloaded'});
    await page.locator('#femRun').waitFor();
    assert.equal(await page.locator('#femDemoNotice').count(),0);
    assert(!(await page.locator('#femCase').innerHTML()).includes('demo_uniform'));
    assert.deepEqual(errors,[]);
    const report={passed:true,first,doubled,eccentric,saved,checks:['197 mapped FE components','input change recomputes response','pressure linearity','eccentric pressure','family filter','actual mesh','magnified deformation','JSON/CSV','saved-result reload','mobile overflow','Beechwood mode separation'],page_errors:errors};
    fs.writeFileSync('data/minnich-demo-verification.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
