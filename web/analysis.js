/* Finite-element results are separate from visual model completeness.
   The panel answers "what does this run show?" first: the load case and Run on top, then the displayed result's
   peaks, its colour controls and the members with the largest stress. Settings, member families, numerical checks
   and the evidence ledger stay one click away in folded sections. */
(() => {
  const node=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
  const fmt=(n,d=3)=>Number(n).toLocaleString('en-US',{maximumFractionDigits:d});
  const action=(text,fn)=>{const b=node('button',text);b.type='button';b.onclick=fn;return b;};
  const link=(text,url)=>{const a=node('a',text,'reference-link');a.href=url;a.target='_blank';a.rel='noopener';return a;};
  const field=(text,control)=>{const label=node('label',text);label.append(control);return label;};
  const choice=(id,pairs,value)=>{const s=node('select');s.id=id;for(const [v,t] of pairs){const o=node('option',t);o.value=v;s.append(o);}s.value=value;return s;};
  // GitHub Pages build: precomputed runs only; run status lives at runs/<id>.json.
  const STATIC=document.documentElement?.dataset?.static==='1';
  const runUrl=id=>'/api/analysis/runs/'+id+(STATIC?'.json':'');
  async function api(url,options){if(STATIC&&options?.method==='POST')throw Error('This GitHub Pages viewer is read-only and shows precomputed results. Run the app locally (python server.py) to calculate new settings.');const r=await fetch(url,options),v=await r.json();if(!r.ok)throw Error(v.error||'Analysis request failed.');return v;}
  const DEFAULTS={case:'global_uniform',end_restraint:'free',load_factor:1,foundation:'tip',prestress_factor:.8};
  class AnalysisPanel {
    constructor(){this.epoch=0;this.field='stress_MPa';this.scale=0;this.family='all';this.options={...DEFAULTS};this.open={};}
    reset(){this.epoch++;clearTimeout(this.timer);this.viewer?.clearAnalysis();this.host=null;this.info=null;this.result=null;this.run=null;this.message='';this.applied=false;this.loading=false;this.pending=false;this.away=false;this.restore=false;this.meshView=false;this.open={};this.field='stress_MPa';this.family='all';this.scale=0;const legend=document.getElementById('femLegend');if(legend)legend.hidden=true;}
    detach(){this.host=null;}
    // Leaving Analysis gives the model back its own look (no result colours, deformation or FE mesh);
    // the result returns when Analysis opens again.
    suspend(){this.away=true;if(this.applied||this.meshView){this.restore=this.restore||this.applied;this.viewer?.clearAnalysis();this.applied=false;}this.meshView=false;this.updateLegend();}
    resume(){this.away=false;const again=this.restore&&this.result&&this.run?.current_inputs;this.restore=false;if(again)this.apply();}
    mount(host,data,viewer,selected,onSelect){this.host=host;this.data=data;this.viewer=viewer;this.selected=selected;this.onSelect=onSelect;this.render();if(this.info||this.loading)return;this.loading=true;const epoch=this.epoch;
      api('/api/analysis/'+data.id).then(async info=>{if(epoch!==this.epoch)return;this.info=info;this.loading=false;this.run=info.latest;
        this.options={...(this.run?.settings||info.defaults||DEFAULTS)};if(info.demonstration)this.family=info.default_family||'girder';this.render();
        if(this.run?.status==='completed')await this.loadResult(this.run.id,epoch);
        else if(this.run&&['queued','running'].includes(this.run.status))this.poll(this.run.id,epoch);
      }).catch(e=>{if(epoch===this.epoch){this.loading=false;this.message=e.message;this.render();}});
    }
    async start(){if(this.pending)return;this.pending=true;this.message='';const epoch=this.epoch;this.render();
      try{const run=await api('/api/analysis/'+this.data.id+'/runs',{method:'POST',headers:{'Content-Type':'application/json','X-Bridge-Analysis':'1'},body:JSON.stringify(this.options)});if(epoch!==this.epoch)return;
        this.run=run;this.result=null;this.viewer.clearAnalysis();this.applied=false;this.meshView=false;this.updateLegend();this.render();this.poll(run.id,epoch);
      }catch(e){if(epoch===this.epoch)this.message=e.message;}finally{if(epoch===this.epoch){this.pending=false;this.render();}}
    }
    async poll(id,epoch){clearTimeout(this.timer);try{const run=await api(runUrl(id));if(epoch!==this.epoch)return;this.run=run;this.render();
      if(run.status==='completed')await this.loadResult(id,epoch);
      else if(run.status==='failed'){this.message=run.error;this.render();}
      else this.timer=setTimeout(()=>this.poll(id,epoch),700);
    }catch(e){if(epoch===this.epoch){this.message=e.message;this.render();}}}
    async loadResult(id,epoch){const result=await api('/api/analysis/runs/'+id+'/result.json');if(epoch!==this.epoch||this.run?.id!==id)return;this.result=result;
      const info=await api('/api/analysis/'+this.data.id);if(epoch!==this.epoch||this.run?.id!==id)return;this.info=info;
      if(this.run.current_inputs){if(this.away)this.restore=true;else{this.apply();this.viewer.fit(result.members.map(m=>m.component_id));}}
      else{this.message='Archived result: current inputs differ. Rerun before applying colors to this model.';this.applied=false;}
      this.render();
    }
    apply(){if(!this.result||!this.run.current_inputs)return;this.viewer.setAnalysis(this.result,this.field,this.scale,this.family);this.applied=true;this.meshView=false;this.updateLegend();}
    updateLegend(){const legend=document.getElementById('femLegend');if(!legend)return;legend.hidden=!this.applied;if(!this.applied)return;
      const stress=this.field==='stress_MPa';legend.replaceChildren(node('b',stress?(this.result.family_summary?'Nominal stress magnitude':'Incremental girder stress |σ|'):'Vertical displacement |δ|'),node('span',this.result.case_title),node('div',undefined,'fem-color-ramp'));
      const ends=node('div',undefined,'fem-legend-ends');ends.append(node('span','0'),node('span',fmt(this.viewer.analysis?.max||0)+(stress?' MPa':' mm')));legend.append(ends,node('small','Gray: not analyzed · '+(this.scale?'Deformation ×'+this.scale:'Original geometry')),node('small',this.result.family_summary?'Frame / shell / mean bearing pressure · No safety rating':'Nominal beam response · Not total stress or a safety rating'));
      if(this.result.demonstration)legend.prepend(node('b','ASSUMED-INPUT DEMONSTRATION','fem-demo-label'));
    }
    // A folded section keeps the state the user left it in when the panel redraws.
    section(id,title){const d=node('details',undefined,'fem-details');d.id=id;d.open=!!this.open[id];d.ontoggle=()=>{this.open[id]=d.open;};d.append(node('summary',title));return d;}
    render(){if(!this.host)return;const h=this.host;
      h.querySelectorAll?.('details[id]').forEach(d=>{this.open[d.id]=d.open;});
      h.replaceChildren();h.classList.add('fem-inspector');h.append(node('h2','Structural analysis'));
      if(!this.info){if(this.message)h.append(node('p',this.message,'fem-error'));h.append(node('p',this.loading?'Loading inputs…':'Preparing inputs…','empty'));return;}
      if(!this.info.available){h.append(node('p',this.info.reason,'source-note'));return;}
      const demo=!!this.info.demonstration,whole=demo||this.options.case.startsWith('global_'),busy=this.pending||['queued','running'].includes(this.run?.status);
      if(demo){const ledger=this.displayLedger(),note=node('p',undefined,'fem-demo-notice');note.id='femDemoNotice';note.append(node('b','Assumed-input demonstration'),node('span',' · not the actual bridge response'));
        h.append(note,node('p',ledger.analyzed_component_ids.length+' mapped components · '+(ledger.display_scope||'deck, girders, cross frames, bearings, caps and columns')+' · '+(ledger.modeled_state||'Proposed 2026 geometry'),'fem-scope'));}
      else h.append(node('p',whole?'Whole bridge: deck, girders, diaphragms, bearings, caps, columns, walls, piles and shafts. Gross elastic research model.':'12 girders · longitudinal beam pilot · selected load increment only.','fem-scope'));
      // Load case (and, for a demonstration, its pressure) with Run: the one job of this panel.
      const row=node('div',undefined,'fem-run'),select=choice('femCase',Object.entries(this.info.cases),this.options.case);select.disabled=busy;
      select.onchange=()=>{this.options.case=select.value;this.family='all';if(!demo){if(select.value==='girder_weight'||select.value.startsWith('global_'))this.options.end_restraint='free';if(select.value.startsWith('global_')){this.options.foundation||='tip';this.options.prestress_factor||=.8;}else{delete this.options.foundation;delete this.options.prestress_factor;}}this.render();};
      row.append(field('Load case',select));
      if(demo&&this.info.parameters.pressure_kPa)row.append(this.number('pressure_kPa',this.info.parameters.pressure_kPa,busy));
      const run=action(busy?'Analysis running…':demo?'Run demonstration':'Run analysis',()=>this.start());run.id='femRun';run.className='primary';run.disabled=busy||STATIC;if(STATIC)run.title='Read-only GitHub Pages viewer: choose a saved run below.';row.append(run);h.append(row);
      const dirty=node('p','Settings differ from the result shown. Run to calculate them.','fem-note');dirty.id='femDirty';dirty.hidden=!this.controlsDiffer();h.append(dirty);
      if(this.run&&this.run.status!=='completed'){const status=node('p',this.run.status==='failed'?'Analysis failed':this.run.status==='queued'?'Queued':'Solving and checking equilibrium…','fem-status');status.id='femRunStatus';status.setAttribute('role','status');h.append(status);}
      if(this.message)h.append(node('p',this.message,'fem-error'));
      h.append(this.settings(demo,whole,busy));
      if(this.result)this.renderResults(h,busy);else{const saved=this.history(busy);if(saved)h.append(saved);}
      h.append(this.inputs());
      const links=node('div',undefined,'fem-links');links.append(link('Method, scope and reproducibility ↗','/analysis-guide'));if(this.result?.family_summary&&!this.result.demonstration)links.append(link('Drawing-confirmed model corrections ↗','/model-corrections'));h.append(links);
    }
    number(key,p,busy){const input=node('input');input.id='fem_'+key;input.type='number';input.min=p.min;input.max=p.max;input.step=p.step;input.value=this.options[key];input.disabled=busy;input.oninput=()=>{this.options[key]=Number(input.value);this.showInputChanges();};return field(p.label,input);}
    // Everything that changes a run besides the load case.
    settings(demo,whole,busy){const d=this.section('femSettings',demo?'Load, materials and supports':'Load and support settings'),form=node('div',undefined,'fem-form');
      const factor=node('input');factor.id='femFactor';factor.type='number';factor.min='.1';factor.max='5';factor.step='.1';factor.value=this.options.load_factor;factor.disabled=busy;factor.oninput=()=>{this.options.load_factor=Number(factor.value);this.showInputChanges();};
      form.append(field(this.options.case==='global_staged'?'Scale all loads, including prestress':'Load multiplier (research scenario)',factor));
      if(demo){for(const [key,p] of Object.entries(this.info.parameters))if(!['pressure_kPa','load_factor'].includes(key))form.append(this.number(key,p,busy));
        const bases=choice('femFoundation',Object.entries(this.info.ledger.foundation_labels||{fixed:'Fixed bases',elastic:'Elastic springs (assumed)'}),this.options.foundation);bases.disabled=busy;bases.onchange=()=>{this.options.foundation=bases.value;this.showInputChanges();};
        form.append(field(this.info.ledger.analytical_family==='arch'?'Assumed arch springings':'Assumed support bases',bases));
        const reset=action('Restore demonstration defaults',()=>{this.options={...this.info.defaults};this.render();});reset.id='femDefaults';reset.disabled=busy;form.append(reset,node('p','These values change the analytical model only. The displayed GLB and its detail status stay unchanged.','fem-note'));}
      else if(whole){const f=choice('femFoundation',[['tip','Fixed estimated tips'],['rock','Rigid rock-line restraint']],this.options.foundation||'tip');f.disabled=busy;f.onchange=()=>{this.options.foundation=f.value;this.render();};form.append(field('Foundation idealization (unverified)',f));
        if(this.options.case==='global_staged'){const p=choice('femPrestress',[.7,.8,.9].map(v=>[v,Math.round(v*100)+'% retained']),this.options.prestress_factor||.8);p.disabled=busy;p.onchange=()=>{this.options.prestress_factor=Number(p.value);this.render();};form.append(field('Retained jacking force (assumed)',p));}}
      else{const s=choice('femSupport',[['free','Free rotation'],['fixed','Fully restrained rotation']],this.options.end_restraint);s.disabled=busy||this.options.case==='girder_weight';s.onchange=()=>{this.options.end_restraint=s.value;this.render();};form.append(field('End-rotation assumption',s));}
      d.append(form);return d;}
    history(busy){const runs=(this.info.runs||[]).filter(r=>r.status==='completed');if(!runs.length)return null;
      const pick=choice('femHistory',[['','Select a saved run'],...runs.map(r=>[r.id,(this.info.cases[r.settings.case]||r.settings.case)+' · '+(r.settings.pressure_kPa!==undefined?r.settings.pressure_kPa+' kPa · ':'')+r.settings.load_factor+'× · '+new Date(r.created_utc).toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit'})])],runs.some(r=>r.id===this.run?.id)?this.run.id:'');pick.disabled=busy;
      pick.onchange=async()=>{if(!pick.value)return;const epoch=this.epoch;try{const run=await api(runUrl(pick.value));if(epoch!==this.epoch)return;this.viewer.clearAnalysis();this.applied=false;this.meshView=false;this.updateLegend();this.run=run;this.options={...run.settings};this.family='all';this.result=null;this.message='';await this.loadResult(run.id,epoch);}catch(e){if(epoch===this.epoch){this.message=e.message;this.render();}}};
      const label=field(this.result?'Run shown':'Saved runs',pick);label.className='fem-saved';return label;}
    controlsDiffer(){return !!this.result&&Object.entries(this.result.settings).some(([k,v])=>this.options[k]!==v);}
    showInputChanges(){const note=document.getElementById('femDirty');if(note)note.hidden=!this.controlsDiffer();}
    renderResults(h,busy){const r=this.result,current=!!this.run.current_inputs,box=node('section',undefined,'fem-result');
      box.append(node('h3',r.demonstration?'Demonstration result':'Result'));const saved=this.history(busy);if(saved)box.append(saved);
      box.append(node('p',r.case_title+' · '+(r.demonstration?r.settings.pressure_kPa+' kPa · ':'')+r.settings.load_factor+'× · '+(r.family_summary?(this.displayLedger().foundation_labels?.[r.settings.foundation]||r.settings.foundation+' foundation scenario'):r.settings.end_restraint+' end rotation'),'fem-result-case'));
      const peaks=node('dl',undefined,'fem-peaks');for(const [name,value,unit] of [[r.family_summary?'Peak stress':'Peak girder stress',fmt(r.max_stress_MPa),'MPa'],['Peak displacement',fmt(r.max_deflection_mm),'mm']]){const row=node('div'),dd=node('dd',value);dd.append(node('span',' '+unit,'unit'));row.append(node('dt',name),dd);peaks.append(row);}box.append(peaks);
      const checks=node('p',r.verification.mesh_warnings?.length?'Equilibrium passed · local peaks need mesh refinement':'Numerical checks passed · not field validated','fem-status');checks.id='femRunStatus';checks.setAttribute('role','status');box.append(checks);
      // What the colours on the model show.
      const view=node('div',undefined,'fem-view'),locked=!current||this.meshView;
      const color=choice('femField',[['stress_MPa','Stress'],['deflection_mm','Displacement']],this.field);color.disabled=locked;color.onchange=()=>{this.field=color.value;this.apply();};view.append(field('Color by',color));
      const scale=choice('femScale',[0,1,20,100,300].map(v=>[v,v?'×'+v:'None']),this.scale);scale.disabled=locked||r.case==='global_staged';scale.onchange=()=>{this.scale=Number(scale.value);this.apply();};view.append(field('Deformation',scale));
      if(r.family_summary){const members=choice('femFamily',['all',...Object.keys(r.family_summary)].map(v=>[v,v==='all'?'All analyzed members':v]),this.family);members.disabled=this.meshView;members.onchange=()=>{this.family=members.value;this.apply();this.render();};const l=field('Members',members);l.className='wide';view.append(l);}
      box.append(view);
      const buttons=node('div',undefined,'fem-actions');
      if(this.meshView){if(r.mesh_pre)buttons.append(action('Before deck cure',()=>{this.viewer.showAnalysisMesh(r.mesh_pre);document.getElementById('femLegend').hidden=true;}));
        const back=action('Back to results',()=>{this.viewer.clearAnalysis();this.applied=false;this.meshView=false;this.updateLegend();if(current){this.apply();this.viewer.fit(r.members.map(m=>m.component_id));}else this.viewer.fit();this.render();});back.id='femMeshBack';buttons.append(back);}
      else{const toggle=action(this.applied?'Hide colors':'Show colors',()=>{if(this.applied){this.viewer.clearAnalysis();this.applied=false;this.updateLegend();}else this.apply();this.render();});toggle.id='femToggle';toggle.disabled=!current;buttons.append(toggle);
        if(r.mesh){const mesh=action('FE mesh',()=>{this.viewer.showAnalysisMesh(r.mesh);this.meshView=true;const legend=document.getElementById('femLegend');if(r.demonstration){legend.hidden=false;legend.replaceChildren(node('b','ASSUMED-INPUT DEMONSTRATION','fem-demo-label'),node('span','Actual FE mesh · undeformed'),node('small','Unverified structural inputs · no safety rating'));}else legend.hidden=true;this.render();});mesh.id='femMesh';mesh.title='Analytical reference geometry: cyan elements, tan rigid offsets, orange support nodes. Undeformed.';buttons.append(mesh);}
        buttons.append(action('Focus',()=>this.viewer.fit(r.members.map(m=>m.component_id))));}
      box.append(buttons);
      const ranked=r.members.filter(m=>this.family==='all'||m.family===this.family).sort((a,b)=>b.peak.stress_MPa-a.peak.stress_MPa);
      if(ranked.length){box.append(node('h3','Largest stress'));const list=node('div',undefined,'fem-hotspots');for(const m of ranked.slice(0,4)){const b=action(undefined,()=>this.onSelect([m.component_id]));const name=node('span',m.component_id.split(':')[1]);name.append(node('small','x = '+fmt(m.peak.x_m,1)+' m · span '+m.span));b.append(name,node('b',fmt(m.peak.stress_MPa)+' MPa'));list.append(b);}box.append(list);}
      const selected=r.members.find(m=>this.selected.includes(m.component_id));if(selected)box.append(node('p',selected.component_id.split(':')[1]+(r.family_summary?' at its peak: largest signed value ':' at its peak: top ')+fmt(selected.peak.top_MPa)+(r.family_summary?' MPa; smallest ':' MPa; bottom ')+fmt(selected.peak.bottom_MPa)+' MPa. Positive = tension.','fem-note'));
      h.append(box);
      if(r.family_summary)h.append(this.families(r));
      h.append(this.checks(r));
    }
    families(r){const d=this.section('femFamilies','Results by member family');
      const table=node('table',undefined,'fem-table'),thead=node('thead'),tr=node('tr');for(const text of ['Family','Parts','Peak MPa'])tr.append(node('th',text));thead.append(tr);table.append(thead);const body=node('tbody');
      for(const [family,s] of Object.entries(r.family_summary)){const row=node('tr');row.append(node('td',family),node('td',String(s.member_count)),node('td',fmt(s.max_stress_MPa)));body.append(row);}table.append(body);
      d.append(table,node('p','Shell: principal surface stress. Beam: axial + biaxial fiber stress. Bearing: mean pressure. Material strengths and failure modes differ.','fem-note'),node('p',r.displacement_note,'fem-note'));
      if(r.stage_results){d.append(node('h4','Construction-stage increments'));for(const s of r.stage_results)d.append(node('p',s.name+': '+fmt(s.total_load_kN,1)+' kN applied / '+fmt(s.total_reaction_kN,1)+' kN reaction','fem-note'));}
      return d;}
    checks(r){const d=this.section('femChecks','Checks and downloads');
      const maxError=Math.max(...r.equilibrium.map(c=>Math.max(c.force_error,c.moment_error)));
      d.append(node('p','Applied / reaction: '+fmt(r.total_load_kN,2)+' / '+fmt(r.total_reaction_kN,2)+' kN · '+r.element_count+' elements, '+r.node_count+' nodes.'),node('p',r.verification.benchmarks.length+' analytical checks passed. Maximum equilibrium relative error '+maxError.toExponential(2)+'.'));
      for(const c of r.verification.mesh_refinement)d.append(node('p',c.quantity+': '+fmt(100*c.relative_change,5)+'% change (limit '+fmt(c.tolerance*100)+'%). '+(c.passed?'Within tolerance.':'NOT CONVERGED.')));
      if(r.verification.mesh_warnings?.length)d.append(node('p','Unconverged peaks: '+r.verification.mesh_warnings.join(', '),'fem-error'));
      if(r.support_sensitivity){const s=r.support_sensitivity;d.append(node('p','Support sensitivity: '+s.end_restraint+' end rotation gives '+fmt(s.max_stress_MPa)+' MPa and '+fmt(s.max_deflection_mm)+' mm. Alternative idealization; actual support stiffness is unverified.'));}
      for(const s of r.sensitivity||[])d.append(node('p',(r.demonstration?'Assumed support sensitivity':'Sensitivity')+' · '+s.label+': peak vertical displacement '+fmt(s.max_deflection_mm)+' mm.'));
      if(r.demonstration){const values=Object.entries(this.info.parameters).filter(([k])=>!['pressure_kPa','load_factor'].includes(k)).map(([k,p])=>p.label+': '+fmt(r.settings[k]));d.append(node('p','Run assumptions: '+values.join('; ')+'.'));}
      d.append(node('p',r.solver.name+' '+r.solver.version+' · Python '+r.solver.python),node('p','Input hash: '+this.run.input_hash));
      const downloads=node('div',undefined,'fem-downloads');downloads.append(link('Run JSON ↓','/api/analysis/runs/'+this.run.id+'/result.json'),link('Samples CSV ↓','/api/analysis/runs/'+this.run.id+'/samples.csv'));d.append(downloads);
      return d;}
    displayLedger(){return this.result?.snapshot?.ledger||this.info.ledger;}
    evidenceField(key){const walk=(value,keys)=>!keys.length?value:Array.isArray(value)?value.map(v=>walk(v,keys)):walk(value?.[keys[0]],keys.slice(1));return walk(this.displayLedger().values,key.split('.'));}
    evidenceValue(value){if(value===undefined)return 'See frozen ledger';const text=JSON.stringify(value);return text.length<=220?text:(Array.isArray(value)?value.length+' entries':Object.keys(value).length+' fields')+' (see run JSON)';}
    evidence(d,rows,sources,value){for(const row of rows){const card=node('article',undefined,'fem-evidence');card.append(node('b',row.status.replaceAll('_',' ')));for(const f of row.fields)card.append(node('div',f+': '+value(f)));card.append(node('p',row.note));const s=sources[row.source]||sources.plans;if(row.pdf_pages)for(const p of row.pdf_pages)card.append(link('PDF p. '+p,s.url+'#page='+p));else card.append(link(s.title,s.url));d.append(card);}}
    // The evidence ledger and the assumptions of the displayed run (or, before a run, of the current model).
    inputs(){const ledger=this.displayLedger(),demo=!!this.info.demonstration,global=!demo&&(this.result?.case||this.options.case).startsWith('global_');
      const d=this.section('femInputs',this.result?'Displayed run: frozen inputs and evidence':demo?'Geometry, fixed assumptions and evidence':'Materials, inputs and sources');
      if(demo)this.evidence(d,ledger.evidence,ledger.sources,f=>f==='support_geometry'?Object.keys(ledger.values[f]).length+' unverified cap / column envelopes (see run JSON)':this.evidenceValue(this.evidenceField(f)));
      else{if(!this.result||this.run.current_inputs)d.append(node('p','Derived E: girder '+fmt(this.info.derived.girder_E_GPa)+' GPa; deck '+fmt(this.info.derived.deck_E_GPa)+' GPa. These are estimates, not test results.'));
        this.evidence(d,ledger.evidence,ledger.sources,f=>this.evidenceValue(this.evidenceField(f)));if(global)this.evidence(d,ledger.global.evidence,ledger.sources,f=>JSON.stringify(ledger.global.values[f]));}
      d.append(node('h4',demo?'Demonstration assumptions and exclusions':'Assumptions and excluded effects'));const ul=node('ul');for(const text of (global?ledger.global.assumptions:ledger.assumptions))ul.append(node('li',text));d.append(ul);
      return d;}
  }
  window.bridgeAnalysis=new AnalysisPanel();
})();
