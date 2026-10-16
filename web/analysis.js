/* Finite-element results are separate from visual model completeness. */
(() => {
  const node=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
  const fmt=(n,d=3)=>Number(n).toLocaleString('en-US',{maximumFractionDigits:d});
  const action=(text,fn)=>{const b=node('button',text);b.type='button';b.onclick=fn;return b;};
  const link=(text,url)=>{const a=node('a',text,'reference-link');a.href=url;a.target='_blank';a.rel='noopener';return a;};
  async function api(url,options){const r=await fetch(url,options),v=await r.json();if(!r.ok)throw Error(v.error||'Analysis request failed.');return v;}
  class AnalysisPanel {
    constructor(){this.epoch=0;this.field='stress_MPa';this.scale=0;this.family='all';this.options={case:'global_uniform',end_restraint:'free',load_factor:1,foundation:'tip',prestress_factor:.8};}
    reset(){this.epoch++;clearTimeout(this.timer);this.viewer?.clearAnalysis();this.host=null;this.info=null;this.result=null;this.run=null;this.message='';this.applied=false;this.loading=false;this.pending=false;this.field='stress_MPa';this.family='all';this.scale=0;const legend=document.getElementById('femLegend');if(legend)legend.hidden=true;}
    detach(){this.host=null;}
    mount(host,data,viewer,selected,onSelect){this.host=host;this.data=data;this.viewer=viewer;this.selected=selected;this.onSelect=onSelect;if(this.info){this.render();return;}this.render();if(this.loading)return;this.loading=true;const epoch=this.epoch;
      api('/api/analysis/'+data.id).then(async info=>{if(epoch!==this.epoch)return;this.info=info;this.loading=false;this.run=info.latest;
        this.options={...(this.run?.settings||info.defaults||{case:'global_uniform',end_restraint:'free',load_factor:1,foundation:'tip',prestress_factor:.8})};if(info.demonstration)this.family=info.default_family||'girder';this.render();
        if(this.run?.status==='completed')await this.loadResult(this.run.id,epoch);
        else if(this.run&&['queued','running'].includes(this.run.status))this.poll(this.run.id,epoch);
      }).catch(e=>{if(epoch===this.epoch){this.loading=false;this.message=e.message;this.render();}});
    }
    async start(){if(this.pending)return;this.pending=true;this.message='';const epoch=this.epoch;this.render();
      try{const run=await api('/api/analysis/'+this.data.id+'/runs',{method:'POST',headers:{'Content-Type':'application/json','X-Bridge-Analysis':'1'},body:JSON.stringify(this.options)});if(epoch!==this.epoch)return;
        this.run=run;this.result=null;this.viewer.clearAnalysis();this.applied=false;this.updateLegend();this.render();this.poll(run.id,epoch);
      }catch(e){if(epoch===this.epoch)this.message=e.message;}finally{if(epoch===this.epoch){this.pending=false;this.render();}}
    }
    async poll(id,epoch){clearTimeout(this.timer);try{const run=await api('/api/analysis/runs/'+id);if(epoch!==this.epoch)return;this.run=run;this.render();
      if(run.status==='completed')await this.loadResult(id,epoch);
      else if(run.status==='failed'){this.message=run.error;this.render();}
      else this.timer=setTimeout(()=>this.poll(id,epoch),700);
    }catch(e){if(epoch===this.epoch){this.message=e.message;this.render();}}}
    async loadResult(id,epoch){const result=await api('/api/analysis/runs/'+id+'/result.json');if(epoch!==this.epoch||this.run?.id!==id)return;this.result=result;
      const info=await api('/api/analysis/'+this.data.id);if(epoch!==this.epoch||this.run?.id!==id)return;this.info=info;
      if(this.run.current_inputs){this.apply();this.viewer.fit(result.members.map(m=>m.component_id));}
      else{this.message='Archived result: current inputs differ. Rerun before applying colors to this model.';this.applied=false;}
      this.render();
    }
    apply(){if(!this.result||!this.run.current_inputs)return;this.viewer.setAnalysis(this.result,this.field,this.scale,this.family);this.applied=true;this.updateLegend();}
    updateLegend(){const legend=document.getElementById('femLegend');legend.hidden=!this.applied;if(!this.applied)return;
      const stress=this.field==='stress_MPa';legend.replaceChildren(node('b',stress?(this.result.family_summary?'Nominal stress magnitude':'Incremental girder stress |σ|'):'Vertical displacement |δ|'),node('span',this.result.case_title),node('div',undefined,'fem-color-ramp'));
      const ends=node('div',undefined,'fem-legend-ends');ends.append(node('span','0'),node('span',fmt(this.viewer.analysis?.max||0)+(stress?' MPa':' mm')));legend.append(ends,node('small','Gray: not analyzed · '+(this.scale?'Deformation ×'+this.scale:'Original geometry')),node('small',this.result.family_summary?'Frame / shell / mean bearing pressure · No safety rating':'Nominal beam response · Not total stress or a safety rating'));
      if(this.result.demonstration)legend.prepend(node('b','ASSUMED-INPUT DEMONSTRATION','fem-demo-label'));
    }
    render(){if(!this.host)return;const h=this.host;h.replaceChildren();h.classList.add('fem-inspector');
      h.append(node('div','STRUCTURAL ANALYSIS','eyebrow'),node('h2','Bridge FEM'));
      if(this.message)h.append(node('p',this.message,'fem-error'));
      if(!this.info){h.append(node('p',this.loading?'Loading inputs…':'Preparing inputs…'));return;}
      if(!this.info.available){h.append(node('p',this.info.reason,'source-note'));return;}
      const demo=!!this.info.demonstration,whole=demo||this.options.case.startsWith('global_');
      if(demo){const ledger=this.displayLedger(),note=node('div',undefined,'fem-demo-notice');note.id='femDemoNotice';note.append(node('b','Assumed-input demonstration'),node('p',ledger.analyzed_component_ids.length+' mapped components · '+(ledger.display_scope||'deck, girders, cross frames, bearings, caps and columns')+'. Missing properties and support conditions are intentionally assumed. This is not the actual bridge response.'),node('small',(ledger.modeled_state||'Proposed 2026 geometry')+' · pressure increment only · no safety rating'));h.append(note);}
      else h.append(node('p',whole?'Connected deck, girders, diaphragms, bearings, caps, columns, walls, piles and shafts. Gross elastic research model.':'12 girders · longitudinal beam pilot. Selected load increment only.','source-note'));
      const busy=this.pending||['queued','running'].includes(this.run?.status);
      const form=node('div',undefined,'fem-form');
      const label=node('label','Load case'),select=node('select');select.id='femCase';select.disabled=busy;
      for(const [value,text] of Object.entries(this.info.cases)){const o=node('option',text);o.value=value;select.append(o);}select.value=this.options.case;
      select.onchange=()=>{this.options.case=select.value;this.family='all';if(!demo){if(select.value==='girder_weight'||select.value.startsWith('global_'))this.options.end_restraint='free';if(select.value.startsWith('global_')){this.options.foundation||='tip';this.options.prestress_factor||=.8;}else{delete this.options.foundation;delete this.options.prestress_factor;}}this.render();};label.append(select);form.append(label);
      const supportLabel=node('label','End-rotation assumption'),support=node('select');support.id='femSupport';support.disabled=busy||this.options.case==='girder_weight'||whole;
      for(const [value,text] of [['free','Free rotation'],['fixed','Fully restrained rotation']]){const o=node('option',text);o.value=value;support.append(o);}support.value=this.options.end_restraint;support.onchange=()=>{this.options.end_restraint=support.value;this.render();};supportLabel.append(support);if(!whole)form.append(supportLabel);if(demo)this.demoControls(form,busy);else if(whole)this.globalControls(form,busy);
      const multiplier=node('label',this.options.case==='global_staged'?'Scale all loads, including prestress':'Load multiplier (research scenario)'),input=node('input');input.id='femFactor';input.type='number';input.min='.1';input.max='5';input.step='.1';input.value=this.options.load_factor;input.disabled=busy;input.oninput=()=>{this.options.load_factor=Number(input.value);this.showInputChanges();};multiplier.append(input);form.append(multiplier);
      const run=action(busy?'Analysis running…':demo?'Run demonstration':'Run analysis',()=>this.start());run.id='femRun';run.className='primary';run.disabled=busy;form.append(run);h.append(form);
      if(this.run){const status=node('p',this.run.status==='completed'?(this.result?.verification.mesh_warnings?.length?'Equilibrium passed · Local peaks need refinement':'Numerical checks passed · Not field validated'):this.run.status==='failed'?'Analysis failed':this.run.status==='queued'?'Queued':'Solving and checking equilibrium…','fem-status');status.id='femRunStatus';status.setAttribute('role','status');h.append(status);if(this.run.error)h.append(node('p',this.run.error,'fem-error'));}
      const history=(this.info.runs||[]).filter(r=>r.status==='completed');
      if(history.length){const label=node('label','Saved runs'),choices=node('select');label.className='fem-form';choices.id='femHistory';choices.disabled=busy;const blank=node('option','Select a saved run');blank.value='';choices.append(blank);
        for(const run of history){const o=node('option',new Date(run.created_utc).toLocaleTimeString('en-US')+' · '+run.settings.case+' · '+(demo?run.settings.pressure_kPa+' kPa / '+run.settings.foundation:run.settings.end_restraint)+' · '+run.settings.load_factor+'×');o.value=run.id;choices.append(o);}choices.value=history.some(r=>r.id===this.run?.id)?this.run.id:'';
        choices.onchange=async()=>{if(!choices.value)return;const epoch=this.epoch;try{const run=await api('/api/analysis/runs/'+choices.value);if(epoch!==this.epoch)return;this.viewer.clearAnalysis();this.applied=false;this.updateLegend();this.run=run;this.options={...run.settings};this.family='all';this.result=null;this.message='';await this.loadResult(run.id,epoch);}catch(e){if(epoch===this.epoch){this.message=e.message;this.render();}}};label.append(choices);h.append(label);
      }
      if(this.result)this.renderResults(h);
      this.renderInputs(h);
      h.append(link('Method, scope and reproducibility ↗','/analysis-guide'));
    }
    controlsDiffer(){return !!this.result&&Object.entries(this.result.settings).some(([k,v])=>this.options[k]!==v);}
    showInputChanges(){const note=document.getElementById('femDirty');if(note)note.hidden=!this.controlsDiffer();}
    renderResults(h){const r=this.result;h.append(node('h3',r.demonstration?'Demonstration result':'Displayed result'),node('p',r.case_title+' · '+(r.demonstration?r.settings.pressure_kPa+' kPa · ':'')+r.settings.load_factor+'× · '+(r.family_summary?(this.displayLedger().foundation_labels?.[r.settings.foundation]||r.settings.foundation+' foundation scenario'):r.settings.end_restraint+' end rotation'),'fem-result-case'));
      const dirty=node('p','Controls differ from the displayed run. Run analysis to calculate those settings.','source-note');dirty.id='femDirty';dirty.hidden=!this.controlsDiffer();h.append(dirty);
      if(r.demonstration){const values=Object.entries(this.info.parameters).filter(([k])=>!['pressure_kPa','load_factor'].includes(k)).map(([k,p])=>p.label+': '+fmt(r.settings[k]));h.append(node('p','Run assumptions: '+values.join('; ')+'.','source-note'));}
      const metrics=node('dl',undefined,'property-list');for(const [name,value] of [[r.family_summary?'Largest nominal stress (all families)':'Peak |girder fiber stress|',fmt(r.max_stress_MPa)+' MPa'],['Peak |vertical displacement|',fmt(r.max_deflection_mm)+' mm'],['Applied / reaction',fmt(r.total_load_kN,2)+' / '+fmt(r.total_reaction_kN,2)+' kN'],['Elements / nodes',r.element_count+' / '+r.node_count]]){const row=node('div');row.append(node('dt',name),node('dd',value));metrics.append(row);}h.append(metrics);
      if(r.family_summary)this.globalResults(h,r);const visuals=node('div',undefined,'fem-form'),fieldLabel=node('label','Color field'),field=node('select');field.id='femField';for(const [v,t] of [['stress_MPa',r.family_summary?'Nominal stress magnitude':'Max |top/bottom girder stress|'],['deflection_mm','Absolute vertical displacement']]){const o=node('option',t);o.value=v;field.append(o);}field.value=this.field;field.disabled=!this.run.current_inputs;field.onchange=()=>{this.field=field.value;this.apply();};fieldLabel.append(field);visuals.append(fieldLabel);
      const deformation=node('label','Deformation display'),scale=node('select');scale.id='femScale';for(const v of [0,1,20,100,300]){const o=node('option',v?'Magnified ×'+v:'Original geometry');o.value=v;scale.append(o);}scale.value=this.scale;scale.disabled=!this.run.current_inputs||r.case==='global_staged';scale.onchange=()=>{this.scale=Number(scale.value);this.apply();};deformation.append(scale);visuals.append(deformation);
      const toggle=action(this.applied?'Clear result colors':'Show result colors',()=>{if(this.applied){this.viewer.clearAnalysis();this.applied=false;this.updateLegend();}else this.apply();this.render();});toggle.id='femToggle';toggle.disabled=!this.run.current_inputs;visuals.append(toggle,action(r.family_summary?'Focus analyzed members':'Focus analyzed girders',()=>this.viewer.fit(r.members.map(m=>m.component_id))));h.append(visuals);
      const ranked=r.members.filter(m=>this.family==='all'||m.family===this.family).sort((a,b)=>b.peak.stress_MPa-a.peak.stress_MPa);h.append(node('h3','Locations with larger nominal stress'));
      const list=node('div',undefined,'fem-hotspots');for(const m of ranked.slice(0,4)){const b=action(m.component_id.split(':')[1]+' · '+fmt(m.peak.stress_MPa)+' MPa',()=>this.onSelect([m.component_id]));b.append(node('small','x = '+fmt(m.peak.x_m)+' m · span '+m.span));list.append(b);}h.append(list);
      const selected=r.members.find(m=>this.selected.includes(m.component_id));if(selected){h.append(node('h3',selected.component_id.split(':')[1]),node('p',(r.family_summary?'At this member’s peak: largest signed value ':'At this member’s peak: top ')+fmt(selected.peak.top_MPa)+(r.family_summary?' MPa; smallest signed value ':' MPa; bottom ')+fmt(selected.peak.bottom_MPa)+' MPa. Positive = tension.','source-note'));}
      if(r.support_sensitivity){const s=r.support_sensitivity;h.append(node('h3','Support sensitivity'),node('p',s.end_restraint+' end rotation: '+fmt(s.max_stress_MPa)+' MPa and '+fmt(s.max_deflection_mm)+' mm. Alternative idealization; actual support stiffness is unverified.','source-note'));}
      const verification=node('details',undefined,'fem-details');verification.append(node('summary','Numerical verification'));
      const maxError=Math.max(...r.equilibrium.map(c=>Math.max(c.force_error,c.moment_error)));
      verification.append(node('p',r.verification.benchmarks.length+' analytical checks passed. Maximum equilibrium relative error '+maxError.toExponential(2)+'.'));
      for(const c of r.verification.mesh_refinement)verification.append(node('p',c.quantity+': '+fmt(100*c.relative_change,5)+'% change (limit '+fmt(c.tolerance*100)+'%). '+(c.passed?'Within tolerance.':'NOT CONVERGED.')));
      if(r.verification.mesh_warnings?.length)verification.append(node('p','Unconverged peaks: '+r.verification.mesh_warnings.join(', '),'fem-error'));verification.append(node('p',r.solver.name+' '+r.solver.version+' · Python '+r.solver.python),node('p','Input hash: '+this.run.input_hash));h.append(verification);
      const downloads=node('div',undefined,'fem-downloads');downloads.append(link('Run JSON ↓','/api/analysis/runs/'+this.run.id+'/result.json'),link('Samples CSV ↓','/api/analysis/runs/'+this.run.id+'/samples.csv'));h.append(downloads);
    }
    globalControls(form,busy){
      const label=node('label','Foundation idealization (unverified)'),select=node('select');select.id='femFoundation';select.disabled=busy;
      for(const [value,text] of [['tip','Fixed estimated tips'],['rock','Rigid rock-line restraint']]){const o=node('option',text);o.value=value;select.append(o);}select.value=this.options.foundation||'tip';select.onchange=()=>{this.options.foundation=select.value;this.render();};label.append(select);form.append(label);
      if(this.options.case==='global_staged'){const l=node('label','Retained jacking force (assumed)'),p=node('select');p.id='femPrestress';p.disabled=busy;for(const v of [.7,.8,.9]){const o=node('option',Math.round(v*100)+'% retained');o.value=v;p.append(o);}p.value=this.options.prestress_factor||.8;p.onchange=()=>{this.options.prestress_factor=Number(p.value);this.render();};l.append(p);form.append(l);}
    }
    globalResults(h,r){
      h.append(node('p',r.displacement_note,'source-note'));
      const label=node('label','Component family'),filter=node('select');label.className='fem-form';filter.id='femFamily';
      for(const value of ['all',...Object.keys(r.family_summary)]){const o=node('option',value==='all'?'All analyzed members':value);o.value=value;filter.append(o);}filter.value=this.family;filter.onchange=()=>{this.family=filter.value;this.apply();this.render();};label.append(filter);h.append(label);
      const table=node('table',undefined,'fem-table'),thead=node('thead'),tr=node('tr');for(const text of ['Family','Parts','Peak MPa'])tr.append(node('th',text));thead.append(tr);table.append(thead);const body=node('tbody');
      for(const [family,s] of Object.entries(r.family_summary)){const row=node('tr');row.append(node('td',family),node('td',String(s.member_count)),node('td',fmt(s.max_stress_MPa)));body.append(row);}table.append(body);h.append(table,node('p','Shell: principal surface stress. Beam: axial + biaxial fiber stress. Bearing: mean pressure. Material strengths and failure modes differ.','source-note'));
      const meshControls=node('div',undefined,'fem-downloads');
      const show=action('View actual FE mesh',()=>{this.viewer.showAnalysisMesh(r.mesh);const legend=document.getElementById('femLegend');if(r.demonstration){legend.hidden=false;legend.replaceChildren(node('b','ASSUMED-INPUT DEMONSTRATION','fem-demo-label'),node('span','Actual FE mesh · undeformed'),node('small','Unverified structural inputs · no safety rating'));}else legend.hidden=true;});show.id='femMesh';meshControls.append(show);
      if(r.mesh_pre)meshControls.append(action('Before deck cure: FE mesh',()=>{this.viewer.showAnalysisMesh(r.mesh_pre);document.getElementById('femLegend').hidden=true;}));
      const back=action('Return to 3D results',()=>{this.viewer.clearAnalysis();this.applied=false;this.updateLegend();if(this.run.current_inputs){this.apply();this.viewer.fit(r.members.map(m=>m.component_id));}else this.viewer.fit();});back.id='femMeshBack';meshControls.append(back);h.append(meshControls,node('p','FE mesh: analytical reference geometry; cyan elements, tan rigid offsets, orange support nodes. Undeformed geometry.','source-note'));
      if(r.stage_results){h.append(node('h3','Construction-stage increments'));for(const s of r.stage_results)h.append(node('p',s.name+': '+fmt(s.total_load_kN,1)+' kN applied / '+fmt(s.total_reaction_kN,1)+' kN reaction','source-note'));}
      if(r.sensitivity?.length){const sensitivity=node('details',undefined,'fem-details');sensitivity.append(node('summary',r.demonstration?'Assumed support sensitivity':'Foundation / prestress sensitivity'));for(const s of r.sensitivity)sensitivity.append(node('p',s.label+': peak vertical displacement '+fmt(s.max_deflection_mm)+' mm.','source-note'));h.append(sensitivity);}
      if(!r.demonstration)h.append(link('Drawing-confirmed model corrections ↗','/model-corrections'));
    }
    demoControls(form,busy){
      const details=node('details',undefined,'fem-details');details.id='femAssumedProperties';details.append(node('summary','Edit assumed materials and supports'));
      for(const [key,p] of Object.entries(this.info.parameters)){
        if(key==='load_factor')continue;
        const label=node('label',p.label),input=node('input');input.id='fem_'+key;input.type='number';input.min=p.min;input.max=p.max;input.step=p.step;input.value=this.options[key];input.disabled=busy;
        input.oninput=()=>{this.options[key]=Number(input.value);this.showInputChanges();};label.append(input);(key==='pressure_kPa'?form:details).append(label);
      }
      const label=node('label',this.info.ledger.analytical_family==='arch'?'Assumed arch springings':'Assumed support bases'),select=node('select');select.id='femFoundation';select.disabled=busy;
      for(const [v,t] of Object.entries(this.info.ledger.foundation_labels||{fixed:'Fixed bases',elastic:'Elastic springs (assumed)'})){const o=node('option',t);o.value=v;select.append(o);}select.value=this.options.foundation;select.onchange=()=>{this.options.foundation=select.value;this.showInputChanges();};label.append(select);details.append(label);
      const reset=action('Restore demonstration defaults',()=>{this.options={...this.info.defaults};this.render();});reset.id='femDefaults';reset.disabled=busy;details.append(reset,node('p','These values change the analytical model only. The displayed GLB and its detail status stay unchanged.','source-note'));form.append(details);
    }
    displayLedger(){return this.result?.snapshot?.ledger||this.info.ledger;}
    evidenceField(key){const walk=(value,keys)=>!keys.length?value:Array.isArray(value)?value.map(v=>walk(v,keys)):walk(value?.[keys[0]],keys.slice(1));return walk(this.displayLedger().values,key.split('.'));}
    evidenceValue(value){if(value===undefined)return 'See frozen ledger';const text=JSON.stringify(value);return text.length<=220?text:(Array.isArray(value)?value.length+' entries':Object.keys(value).length+' fields')+' (see run JSON)';}
    demoInputs(h){
      const ledger=this.displayLedger(),details=node('details',undefined,'fem-details');details.append(node('summary',this.result?'Displayed run: frozen inputs and evidence':'Geometry, fixed assumptions and evidence'));
      for(const row of ledger.evidence){const card=node('article',undefined,'fem-evidence');card.append(node('b',row.status.replaceAll('_',' ')));for(const f of row.fields)card.append(node('div',f+': '+(f==='support_geometry'?Object.keys(ledger.values[f]).length+' unverified cap / column envelopes (see run JSON)':this.evidenceValue(this.evidenceField(f)))));card.append(node('p',row.note));const s=ledger.sources[row.source];if(row.pdf_pages)for(const p of row.pdf_pages)card.append(link('PDF p. '+p,s.url+'#page='+p));else card.append(link(s.title,s.url));details.append(card);}h.append(details);
      const scope=node('details',undefined,'fem-details');scope.append(node('summary','Demonstration assumptions and exclusions'));const ul=node('ul');for(const text of ledger.assumptions)ul.append(node('li',text));scope.append(ul);h.append(scope);
    }
    renderInputs(h){const ledger=this.displayLedger(),details=node('details',undefined,'fem-details');details.append(node('summary',this.result?'Displayed run: frozen inputs and evidence':'Materials, inputs and sources'));
      if(this.info.demonstration){this.demoInputs(h);return;}
      if(!this.result||this.run.current_inputs)details.append(node('p','Derived E: girder '+fmt(this.info.derived.girder_E_GPa)+' GPa; deck '+fmt(this.info.derived.deck_E_GPa)+' GPa. These are estimates, not test results.'));
      for(const row of ledger.evidence){const card=node('article',undefined,'fem-evidence');card.append(node('b',row.status.replaceAll('_',' ')));for(const f of row.fields)card.append(node('div',f+': '+this.evidenceValue(this.evidenceField(f))));card.append(node('p',row.note));const s=ledger.sources[row.source];if(row.pdf_pages)for(const p of row.pdf_pages)card.append(link('PDF p. '+p,s.url+'#page='+p));else card.append(link(s.title,s.url));details.append(card);}if((this.result?.case||this.options.case).startsWith('global_'))for(const row of ledger.global.evidence){const card=node('article',undefined,'fem-evidence');card.append(node('b',row.status.replaceAll('_',' ')));for(const f of row.fields)card.append(node('div',f+': '+JSON.stringify(ledger.global.values[f])));card.append(node('p',row.note));for(const p of row.pdf_pages||[])card.append(link('PDF p. '+p,ledger.sources.plans.url+'#page='+p));details.append(card);}h.append(details);
      const scope=node('details',undefined,'fem-details');scope.append(node('summary','Assumptions and excluded effects'));const ul=node('ul');for(const text of ((this.result?.case||this.options.case).startsWith('global_')?ledger.global.assumptions:ledger.assumptions))ul.append(node('li',text));scope.append(ul);h.append(scope);
    }
  }
  window.bridgeAnalysis=new AnalysisPanel();
})();
