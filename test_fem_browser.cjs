const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const base=process.env.BRIDGE_TEST_URL||'http://127.0.0.1:8766';
(async()=>{
  const browser=await chromium.launch({executablePath:process.env.BROWSER_EXECUTABLE||undefined,headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const page=await browser.newPage({viewport:{width:1600,height:1000}}),errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  try{
    await page.route('https://carto.nationalmap.gov/**',r=>r.abort());
    await page.goto(base+'/',{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>window.bridgeManager?.ready);
    await page.locator('#openAnalysis').click();
    await page.locator('#femRun').waitFor();
    const runIds={};
    for(const name of ['girder_weight','wearing','uniform']){
      await page.selectOption('#femCase',name);
      await page.locator('#femRun').click();
      await page.waitForFunction(name=>window.bridgeAnalysis.result?.case===name&&window.bridgeAnalysis.applied&&window.bridgeAnalysis.run?.status==='completed',name,{timeout:60000});
      const result=await page.evaluate(()=>({id:window.bridgeAnalysis.run.id,stress:window.bridgeAnalysis.result.max_stress_MPa,current:window.bridgeAnalysis.run.current_inputs,mapped:[...window.bridgeManager.viewer.meshes.values()].filter(m=>m.geometry.attributes.color).length}));
      assert.equal(result.current,true);assert.equal(result.mapped,12);assert(result.stress>0);runIds[name]=result.id;
    }
    await page.selectOption('#femHistory',runIds.wearing);
    await page.waitForFunction(()=>window.bridgeAnalysis.result?.case==='wearing'&&window.bridgeAnalysis.applied);
    assert.equal(await page.locator('#femCase').inputValue(),'wearing');
    await page.selectOption('#femHistory',runIds.uniform);
    await page.waitForFunction(()=>window.bridgeAnalysis.result?.case==='uniform'&&window.bridgeAnalysis.applied);
    await page.selectOption('#femField','deflection_mm');
    await page.selectOption('#femScale','300');
    assert.equal(await page.evaluate(()=>window.bridgeManager.viewer.analysis.deformationScale),300);
    assert(await page.evaluate(()=>{
      const m=window.bridgeManager.viewer.meshes.get('beechwood:girder_A1');
      const a=m.geometry.attributes.position.array,b=m.userData.analysisOriginal.positions;
      return a.some((v,i)=>i%3===1&&Math.abs(v-b[i])>.01)&&a.every(Number.isFinite);
    }));
    await page.locator('#femToggle').click();
    assert(await page.evaluate(()=>[...window.bridgeManager.viewer.meshes.values()].every(m=>!m.userData.analysisOriginal&&!m.geometry.attributes.color)));
    assert(await page.locator('#femLegend').isHidden());
    await page.locator('#femToggle').click();
    await page.locator('.fem-hotspots button').first().click();
    assert.equal(await page.evaluate(()=>window.bridgeManager.selected.length),1);
    await page.selectOption('#femField','stress_MPa');
    await page.selectOption('#femScale','0');
    await page.evaluate(()=>{document.getElementById('inspector').scrollTop=0;});
    fs.mkdirSync('data',{recursive:true});
    await page.screenshot({path:'data/fem-workspace.png'});
    await page.setViewportSize({width:390,height:844});
    await page.locator('.mobile-tabs button[data-pane="inspector"]').click();
    await page.locator('[data-tab="analysis"]').click();
    assert(await page.locator('#femRun').isVisible());
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    await page.locator('.mobile-tabs button[data-pane="viewer"]').click();
    assert(await page.locator('#femLegend').isVisible());
    assert(await page.evaluate(()=>{const r=document.getElementById('femLegend').getBoundingClientRect();return r.left>=0&&r.right<=innerWidth;}));
    await page.setViewportSize({width:1600,height:1000});
    await page.selectOption('#bridgeSelect','us52-mud');
    await page.waitForFunction(()=>window.bridgeManager.ready&&window.bridgeManager.data.id==='us52-mud');
    assert(await page.locator('#femLegend').isHidden());
    assert.equal(await page.evaluate(()=>window.bridgeManager.viewer.analysis),null);
    await page.locator('#openAnalysis').click();
    await page.waitForFunction(()=>window.bridgeAnalysis.info?.available===false);
    assert.equal(await page.locator('#femRun').count(),0);
    await page.goto(base+'/analysis-guide',{waitUntil:'domcontentloaded'});
    assert.equal(await page.locator('h1').innerText(),'Bridge FEM methods and demonstrations');
    assert(await page.locator('#minnich-demo').isVisible());
    assert.equal(errors.length,0,errors.join('\n'));
    console.log(JSON.stringify({passed:true,checks:['three real load cases','saved run switch','12 mapped girders','scaled vertical deformation','color reset','member selection','mobile overflow','bridge switch clears results','other bridges unavailable','method guide'],run_ids:runIds,page_errors:errors},null,2));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
