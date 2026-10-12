const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const base=process.env.BRIDGE_TEST_URL||'http://127.0.0.1:8766';
(async()=>{
  const browser=await chromium.launch({executablePath:process.env.BROWSER_EXECUTABLE||undefined,headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const page=await browser.newPage({viewport:{width:1600,height:1000}}),errors=[];
  page.setDefaultTimeout(20000);
  page.on('pageerror',e=>errors.push(String(e)));
  try{
    await page.route('https://carto.nationalmap.gov/**',r=>r.abort());
    await page.goto(base+'/',{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>window.bridgeManager?.ready);
    await page.locator('#openAnalysis').click();await page.locator('#femRun').waitFor();
    const ids={};
    for(const name of ['global_staged','global_eccentric','global_uniform']){
      console.log('Running '+name);
      await page.selectOption('#femCase',name);await page.locator('#femRun').click();
      await page.waitForFunction(name=>window.bridgeAnalysis.result?.case===name&&window.bridgeAnalysis.applied&&window.bridgeAnalysis.run.current_inputs,name,{timeout:90000});
      const r=await page.evaluate(()=>({id:window.bridgeAnalysis.run.id,count:window.bridgeAnalysis.result.members.length,mapped:[...window.bridgeManager.viewer.meshes.values()].filter(m=>m.geometry.attributes.color).length,warnings:window.bridgeAnalysis.result.verification.mesh_warnings}));
      assert.equal(r.count,72);assert.equal(r.mapped,72);assert(r.warnings.length);ids[name]=r.id;
      console.log('Completed '+name);
      if(name==='global_staged')assert.equal(await page.locator('#femScale').isDisabled(),true);
    }
    await page.selectOption('#femFamily','column');
    assert.equal(await page.evaluate(()=>[...window.bridgeManager.viewer.meshes.values()].filter(m=>m.geometry.attributes.color).length),4);
    await page.selectOption('#femFamily','all');
    await page.locator('#femMesh').click();
    assert.equal(await page.evaluate(()=>!!window.bridgeManager.viewer.analysisGeometry&&!window.bridgeManager.viewer.root.visible),true);
    await page.screenshot({path:'data/global-fe-mesh.png'});
    await page.locator('#femMeshBack').click();
    assert.equal(await page.evaluate(()=>window.bridgeManager.viewer.root.visible&&!window.bridgeManager.viewer.analysisGeometry),true);
    await page.selectOption('#femScale','100');
    assert.equal(await page.evaluate(()=>window.bridgeManager.viewer.analysis.deformationScale),100);
    await page.selectOption('#femScale','0');
    await page.screenshot({path:'data/global-fem-workspace.png'});
    const response=await page.request.get(base+'/api/analysis/runs/'+ids.global_uniform+'/samples.csv');assert(response.ok());assert((await response.text()).includes('beechwood:b2_column_L'));
    await page.goto(base+'/model-corrections');assert((await page.textContent('body')).includes('22 ft'));
    await page.setViewportSize({width:390,height:844});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({passed:true,runs:ids,checks:['three persisted global cases','72 mapped components','family filter','actual mesh toggle','scaled deformation','staged deformation guard','CSV substructure values','correction report','mobile report overflow'],page_errors:errors},null,2));
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
