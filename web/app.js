/* Local asset explorer. All component selections use stable DB IDs. */
(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  const button=(text,fn,cls='')=>{const n=el('button',cls,text);n.onclick=fn;return n;};
  const anchor=(text,url,cls='button')=>{const n=el('a',cls,text);n.href=url;return n;};
  const safeExternal=url=>{try{return ['http:','https:'].includes(new URL(url).protocol);}catch{return false;}};
  const fmt=n=>new Intl.NumberFormat('en-US',{maximumFractionDigits:3}).format(n);
  const dimensionValue=n=>n!==0&&Math.abs(n)<.000001?n.toExponential(4):new Intl.NumberFormat('en-US',{maximumFractionDigits:6}).format(n);
  const countyName=name=>name.replace(/\s+County$/i,'');
  const badge=b=>el('span','badge '+b.detail_status,b.detail_status==='complete'?'Exterior details complete':'More detail needed');
  const workspaceBridges=()=>catalog.bridges.filter(b=>b.workspace_enabled);
  const bridgeLink=b=>(b.workspace_enabled?'#bridge/':'#map/')+b.id;
  const error=message=>{$('globalError').textContent=message;$('globalError').hidden=false;};
  let catalog,data,viewer,selected=[],selectionLabel='',tab='properties',request=0,detailAbort,ready=false;
  let workspaceMode='model',activeCategory=null,registerPage=1,registerCategory=null,returnMode=null,railFor=null,zoomed=false;
  // Deep links: #bridge/<id>[/<mode>[/<page>]]; "members" is the Data mode.
  const MODE_SLUG={model:'model',drawings:'drawings',analysis:'analysis',members:'data'},SLUG_MODE={model:'model',drawings:'drawings',analysis:'analysis',data:'members'};
  const workspaceHash=()=>'#bridge/'+data.id+(workspaceMode==='model'?'':'/'+MODE_SLUG[workspaceMode])+(workspaceMode==='drawings'?'/'+drawingPage:'');
  let map,stateBounds,counties,countyLabels,markers,roads,roadTimer,filtered=[],drawingPage=1,drawingRequest=0;
  // Each screen has one h1: the list title on the map, the bridge name in the top bar in a workspace.
  function titleTag(tag){const old=$('bridgeTitle');if(old.tagName===tag.toUpperCase())return;const n=document.createElement(tag);n.id='bridgeTitle';n.className='bridge-title';n.textContent=old.textContent;old.replaceWith(n);}
  async function api(path,options){const r=await fetch(path,options);if(!r.ok)throw Error('Could not load data ('+r.status+').');return r.json();}
  function propertyList(items){const dl=el('dl','property-list');for(const [key,value] of items){if(value===null||value===undefined||value===''||(Array.isArray(value)&&!value.length))continue;const row=el('div');row.append(el('dt','',key),el('dd','',typeof value==='object'?JSON.stringify(value):String(value)));dl.append(row);}return dl;}
  // Phones keep the 3D view on screen; one row of tabs switches the panel under it. Coverage is a tab of the inspector.
  function mobilePane(pane){const panel=pane==='coverage'?'inspector':pane;document.querySelector('.workbench').dataset.pane=panel;const shown=panel==='inspector'&&workspaceMode==='model'&&tab==='coverage'?'coverage':panel;document.querySelectorAll('.mobile-tabs button').forEach(b=>b.classList.toggle('active',b.dataset.pane===shown));requestAnimationFrame(()=>viewer?.resize());}
  document.querySelectorAll('.mobile-tabs button').forEach(b=>b.onclick=()=>{if(workspaceMode==='model'&&b.dataset.pane!=='tree')setTab(b.dataset.pane==='coverage'?'coverage':'properties');mobilePane(b.dataset.pane);});
  // Keyboard: / search, 1-4 modes, F fit, Esc clear the selection. Ignored while typing, with modifiers, or with a dialog or menu open.
  document.addEventListener('keydown',e=>{if(e.defaultPrevented||e.ctrlKey||e.metaKey||e.altKey)return;const t=e.target;
    if(t.closest?.('input,select,textarea,[contenteditable]')){if(e.key==='Escape'&&t.type==='search')t.blur();return;}
    if(document.querySelector('.export-menu').open)return;
    const inWorkspace=!$('detailView').hidden;
    if(e.key==='/'){const field=!inWorkspace?$('bridgeSearch'):workspaceMode==='members'?$('registerSearch'):$('partSearch');if(field?.offsetParent){e.preventDefault();field.focus();field.select();}return;}
    if(!inWorkspace)return;
    const mode={'1':'model','2':'drawings','3':'analysis','4':'members'}[e.key];if(mode){e.preventDefault();openWorkspace(mode);return;}
    if(workspaceMode==='drawings'&&['ArrowLeft','ArrowRight','PageUp','PageDown'].includes(e.key)){e.preventDefault();drawingPage+=e.key==='ArrowRight'||e.key==='PageDown'?1:-1;renderDrawing();return;}
    if((e.key==='f'||e.key==='F')&&ready&&['model','analysis'].includes(workspaceMode)){e.preventDefault();viewer.fit(selected.length?selected:null);return;}
    if(e.key==='Escape'&&ready&&selected.length)selectParts([]);
  });
  async function init(){catalog=await api('/api/catalog');$('stats').textContent=catalog.summary.bridges+' bridges · '+workspaceBridges().length+' with a 3D workspace · '+fmt(catalog.summary.components)+' components';
    for(const name of [...new Set(catalog.bridges.map(b=>b.county))].sort()){const o=el('option','',name);o.value=name;$('countyFilter').append(o);}
    ['bridgeSearch','countyFilter','statusFilter'].forEach(id=>$(id).addEventListener('input',filterCatalog));
    for(const b of workspaceBridges()){const option=el('option','',b.name);option.value=b.id;$('bridgeSelect').append(option);}
    // The collection map is the first screen; bridge links (#bridge/<id>) still open a workspace directly.
    if(!location.hash)history.replaceState(null,'','#map');
    filterCatalog();await initMap();route();window.addEventListener('hashchange',route);
  }
  function filterCatalog(){const q=$('bridgeSearch').value.trim().toLowerCase(),county=$('countyFilter').value,status=$('statusFilter').value;
    filtered=catalog.bridges.filter(b=>(!county||b.county===county)&&(!status||b.detail_status===status)&&(!q||[b.name,b.structure_id,b.county,b.waterway,b.designation].join(' ').toLowerCase().includes(q)));
    $('resultCount').textContent=filtered.length+' bridges';$('bridgeList').replaceChildren();
    if(!filtered.length)$('bridgeList').append(el('p','empty','No bridges match these filters.'));
    for(const b of filtered){
      const card=el('article','bridge-card'+(b.workspace_enabled?'':' map-only')),info=el('div','card-info');card.dataset.bridge=b.id;
      const title=el('h2');if(b.workspace_enabled)title.append(anchor(b.name,bridgeLink(b),'open-bridge'));else title.textContent=b.name;
      info.append(title,el('p','card-meta',b.county+' County · '+(b.workspace_enabled?fmt(b.component_count)+' components':(b.waterway||b.structure_type||'Location record'))));
      const status=el('div','card-status');status.append(b.workspace_enabled?badge(b):el('span','badge map-only-badge','Map only'),button('Show on map',()=>focusBridge(b),'text-button locate'));info.append(status);
      if(b.workspace_enabled){const img=el('img','thumb');img.src=b.thumbnail_url;img.alt='';img.loading='lazy';card.append(img);}else card.append(el('span','thumb thumb-empty'));
      card.append(info);$('bridgeList').append(card);
    }
    if(map)drawMarkers();
  }
  // Width the floating list covers on the map's left edge (0 when the list stacks under the map).
  const listInset=()=>innerWidth<=900?0:document.querySelector('.catalog').offsetWidth+24;
  async function initMap(){const [states,countyData]=await Promise.all([api('/map/states.json'),api('/map/counties.json')]);
    map=L.map('map',{minZoom:5,maxZoom:19,zoomSnap:.25,preferCanvas:true,maxBoundsViscosity:1,zoomControl:false});L.control.zoom({position:'topright'}).addTo(map);
    map.attributionControl.setPrefix('Leaflet');map.attributionControl.addAttribution('U.S. Census Bureau · Boundaries');
    // Map colours come from the CSS tokens so the map follows the light/dark theme.
    const token=name=>getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    const state=states.features.find(f=>f.properties.STATE==='18');const outline=L.geoJSON(state,{interactive:false,style:{color:token('--map-outline'),weight:2.4,fill:false}}).addTo(map);stateBounds=outline.getBounds();map.setMaxBounds(stateBounds.pad(.4));
    map.createPane('stateMask');map.getPane('stateMask').style.zIndex=350;map.getPane('stateMask').style.pointerEvents='none';
    const polys=state.geometry.type==='MultiPolygon'?state.geometry.coordinates:[state.geometry.coordinates];const rings=polys.flatMap(p=>p.map(r=>r.map(([x,y])=>[y,x])));
    const mask=L.polygon([[[-85,-180],[-85,180],[85,180],[85,-180]],...rings],{pane:'stateMask',interactive:false,stroke:false,fillColor:token('--map-ground'),fillOpacity:1,fillRule:'evenodd',smoothFactor:0}).addTo(map);
    const countyStyle=f=>({color:token('--map-county'),weight:1.2,fillColor:token('--map-county-fill'),fillOpacity:catalog.bridges.some(b=>b.county===countyName(f.properties.NAME))?.15:0});
    counties=L.geoJSON(countyData,{style:countyStyle,onEachFeature:(f,l)=>l.bindTooltip(f.properties.NAME,{sticky:true})}).addTo(map);
    countyLabels=L.layerGroup().addTo(map);markers=L.layerGroup().addTo(map);
    matchMedia('(prefers-color-scheme: dark)').addEventListener('change',()=>{outline.setStyle({color:token('--map-outline')});mask.setStyle({fillColor:token('--map-ground')});counties.setStyle(countyStyle);});
    function labels(){countyLabels.clearLayers();if(!$('countyToggle').checked)return;const occupied=[];for(const f of countyData.features){const p=f.properties;const active=catalog.bridges.some(b=>b.county===countyName(p.NAME));if(map.getZoom()<8.5&&!active)continue;const ll=L.latLng(Number(p.INTPTLAT),Number(p.INTPTLON));if(!map.getBounds().contains(ll))continue;const pos=map.latLngToContainerPoint(ll);if(occupied.some(q=>Math.abs(pos.x-q.x)<62&&Math.abs(pos.y-q.y)<19))continue;occupied.push(pos);const n=el('span','county-label',countyName(p.NAME));L.marker(ll,{icon:L.divIcon({html:n,className:'',iconSize:[80,16],iconAnchor:[40,8]}),interactive:false}).addTo(countyLabels);}}
    // Panning translates every marker equally; only zooming changes the cluster distances.
    map.on('zoomend moveend',event=>{labels();if(event.type==='zoomend')drawMarkers();if(roads)roads.setParams({layers:roadLayers()});});
    $('fitState').onclick=()=>{map.closePopup();map.fitBounds(stateBounds,{paddingTopLeft:innerWidth<=900?[30,60]:[listInset()+40,64],paddingBottomRight:innerWidth<=900?[30,90]:[60,96],animate:false});};
    $('fitResults').onclick=()=>{map.closePopup();if(filtered.length)map.fitBounds(L.latLngBounds(filtered.map(b=>[b.latitude,b.longitude])),{paddingTopLeft:[listInset()+60,80],paddingBottomRight:[60,100],maxZoom:filtered.length===1?15:10,animate:false});};
    $('roadsToggle').onchange=setRoads;$('countyToggle').onchange=()=>{if($('countyToggle').checked)counties.addTo(map);else counties.remove();labels();};
    $('fitState').click();setRoads();drawMarkers();labels();L.control.scale({imperial:false}).addTo(map);
    let lastMapSize='';new ResizeObserver(()=>{const stage=document.querySelector('.map-stage');if(document.getElementById('mapView').hidden)return;if(!stage.clientWidth||!stage.clientHeight)return;const size=stage.clientWidth+':'+stage.clientHeight;if(lastMapSize&&lastMapSize!==size){map.invalidateSize();$('fitState').click();}lastMapSize=size;}).observe(document.querySelector('.map-stage'));
  }
  function roadLayers(){return map.getZoom()<10?'7,8,9,10,11,31,32':'7,8,9,10,11,18,19,20,21,22,23,24,31,32,37,38';}
  function setRoads(){clearTimeout(roadTimer);if(roads){roads.remove();roads=null;}if(!$('roadsToggle').checked){$('mapStatus').textContent='Boundary map · Available offline';return;}
    $('mapStatus').textContent='Connecting to road map…';const layer=L.tileLayer.wms('https://carto.nationalmap.gov/arcgis/services/transportation/MapServer/WMSServer',{layers:roadLayers(),tileSize:512,format:'image/png',transparent:true,version:'1.1.1',minZoom:5,maxZoom:19,noWrap:true,bounds:stateBounds,opacity:.72,keepBuffer:1,attribution:'<a href="https://www.usgs.gov/programs/national-geospatial-program/national-map" target="_blank" rel="noopener">USGS · Roads</a>'});roads=layer;let loaded=0;
    layer.on('tileload',()=>{if(roads!==layer)return;loaded++;clearTimeout(roadTimer);$('mapStatus').textContent='Road map · USGS The National Map';});
    layer.on('tileerror',()=>{if(roads===layer)$('mapStatus').textContent='Road service delayed · Bridges and county boundaries remain available';});
    roadTimer=setTimeout(()=>{if(roads===layer&&!loaded){layer.remove();roads=null;$('mapStatus').textContent='Road service unavailable · Toggle Roads to retry';}},15000);layer.addTo(map);
  }
  function drawMarkers(){if(!markers)return;let openId;markers.eachLayer(marker=>{if(marker.isPopupOpen())openId=marker.options.bridgeIds[0];});markers.clearLayers();const clusters=[];for(const b of filtered){const point=map.latLngToContainerPoint([b.latitude,b.longitude]);const cluster=clusters.find(c=>c.point.distanceTo(point)<27);if(cluster)cluster.bridges.push(b);else clusters.push({point,bridges:[b]});}
    for(const c of clusters){const b=c.bridges[0],html=c.bridges.length===1?el('span','bridge-pin '+b.detail_status+(b.workspace_enabled?'':' map-only')):el('span','cluster-pin',c.bridges.length);const popup=el('div');for(const item of c.bridges){const row=el('div');row.dataset.bridge=item.id;row.append(el('strong','',item.name),badge(item));if(item.workspace_enabled)row.append(anchor('Open workspace',bridgeLink(item),'button primary'));else row.append(el('p','map-only-note','Map only'),propertyList([['County',item.county],['Structure ID',item.structure_id],['Crossing',item.waterway],['Structure type',item.structure_type]]));popup.append(row);}if(c.bridges.length>1)popup.append(button('Zoom to this area',()=>{map.closePopup();map.fitBounds(L.latLngBounds(c.bridges.map(b=>[b.latitude,b.longitude])),{padding:[80,80],maxZoom:17,animate:false});}));
      L.marker([b.latitude,b.longitude],{bridgeIds:c.bridges.map(x=>x.id),title:c.bridges.map(x=>x.name).join(', '),icon:L.divIcon({html,className:'',iconSize:[22,22],iconAnchor:[11,11]})}).bindPopup(popup,{maxHeight:Math.max(120,map.getSize().y-170),autoPanPaddingTopLeft:[listInset()+12,60],autoPanPaddingBottomRight:[12,24]}).addTo(markers);
    }
    // Retain the selected record when zooming changes the marker clusters.
    if(openId)markers.eachLayer(marker=>{if(marker.options.bridgeIds.includes(openId))marker.openPopup();});
  }
  function focusBridge(b){map.closePopup();map.setView([b.latitude,b.longitude],15,{animate:false});const inset=listInset();if(inset)map.panBy([-inset/2,0],{animate:false});markers.eachLayer(marker=>{if(marker.options.bridgeIds.includes(b.id))marker.openPopup();});if(innerWidth<=900)$('map').scrollIntoView({block:'start'});}
  async function route(){let match=location.hash.match(/^#bridge\/([a-z0-9-]+)(?:\/(model|drawings|analysis|data)(?:\/(\d+))?)?$/);
    // Same bridge, another mode or page: switch in place without reloading the model.
    if(match&&ready&&data?.id===match[1]){returnMode=null;workspaceMode=SLUG_MODE[match[2]||'model'];if(match[3])drawingPage=Number(match[3]);activateWorkspace();return;}
    if(match){workspaceMode=SLUG_MODE[match[2]||'model'];drawingPage=match[3]?Number(match[3]):1;}
    const seq=++request;window.bridgeAnalysis.reset();detailAbort?.abort();$('globalError').hidden=true;returnMode=null;railFor=null;
    if(match&&catalog.bridges.some(b=>b.id===match[1]&&!b.workspace_enabled)){history.replaceState(null,'','#map/'+match[1]);match=null;}
    if(!match){$('mapView').hidden=false;$('detailView').hidden=true;ready=false;viewer?.cancel();document.body.dataset.screen='map';document.title='Indiana Bridge 3D';titleTag('span');$('crumb').hidden=true;$('modes').hidden=true;$('modelDownload').hidden=true;$('csvDownload').hidden=true;const focus=catalog.bridges.find(b=>location.hash==='#map/'+b.id);if(focus){['bridgeSearch','countyFilter','statusFilter'].forEach(id=>$(id).value='');filterCatalog();}requestAnimationFrame(()=>{if(seq!==request)return;map?.invalidateSize();if(focus)focusBridge(focus);});return;}
    const bid=match[1];$('mapView').hidden=true;$('detailView').hidden=false;ready=false;selected=[];data=null;viewer?.cancel();$('memberTree').replaceChildren();$('inspector').replaceChildren();titleTag('h1');$('bridgeTitle').textContent=catalog.bridges.find(b=>b.id===bid)?.name||'Loading bridge…';$('crumb').hidden=false;$('modes').hidden=false;$('detailBadge').replaceChildren();$('modelDownload').removeAttribute('href');$('modelDownload').hidden=true;$('csvDownload').hidden=true;$('partSearch').value='';$('viewerStatus').hidden=false;$('viewerStatus').textContent='Loading bridge data…';$('partCount').textContent='';$('visibleCount').textContent='';mobilePane('inspector');
    activeCategory=null;registerPage=1;registerCategory=null;$('registerSearch').value='';document.body.dataset.screen='review';document.body.dataset.mode=workspaceMode;$('bridgeSelect').value=bid;
    detailAbort=new AbortController();try{const result=await api('/api/bridges/'+bid,{signal:detailAbort.signal});if(seq!==request)return;data=result;$('bridgeTitle').textContent=data.name;document.title=data.name+' · Indiana Bridge 3D';$('detailBadge').append(badge(data));$('modelDownload').href=data.model.url;$('modelDownload').download=bid+'.glb';$('modelDownload').hidden=false;$('csvDownload').href='/export/'+bid+'.csv';$('csvDownload').hidden=false;$('partCount').textContent=fmt(data.parts.length);prepareWorkspace();renderTree();tab='properties';setTab(tab);$('deckOpacity').value=100;$('opacityValue').textContent='100%';$('clipEnabled').checked=false;$('clipPosition').value=100;$('clipPosition').disabled=true;$('clipPosition').hidden=true;
      if(!viewer)viewer=new window.BridgeViewer($('canvasHost'),id=>selectParts([id]),state=>{$('visibleCount').textContent=fmt(state.visible)+' / '+fmt(state.total)+' visible';$('clearIsolation').hidden=!state.isolated;});
      const success=await viewer.load(data,text=>{if(seq===request)$('viewerStatus').textContent=text;});if(!success||seq!==request)return;ready=true;$('viewerStatus').hidden=true;renderCategoryChips();renderTree();renderInspector();activateWorkspace();document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view==='iso'));
      if(new URLSearchParams(location.search).get('fem')==='1')openWorkspace('analysis');
    }catch(e){if(e.name==='AbortError'||seq!==request)return;$('viewerStatus').textContent=e.message;error(e.message);}
  }
  function selectParts(ids,label='',focus=false){if(!ready)return;selected=ids;selectionLabel=label;viewer.select(ids);if(focus){viewer.show(ids);viewer.fit(ids);}renderInspector();if(ids.length===1){const p=data.parts.find(p=>p.id===ids[0]);if(p&&!matchesPart(p)){activeCategory=null;$('partSearch').value='';renderCategoryChips();renderTree();}}document.querySelectorAll('.part-button').forEach(b=>b.classList.toggle('selected',ids.includes(b.dataset.id)));document.querySelectorAll('#registerBody tr[data-id]').forEach(tr=>tr.classList.toggle('selected',ids.includes(tr.dataset.id)));
    if(ids.length===1){const p=data.parts.find(p=>p.id===ids[0]);const group=document.querySelector('[data-group="'+CSS.escape(p.group_id)+'"]');if(group){group.closest('.assembly').open=true;group.open=true;populateGroup(group,p.group_id);group.querySelector('[data-id="'+CSS.escape(p.id)+'"]')?.scrollIntoView({block:'nearest'});}}
  }
  const partsFor=gid=>data.parts.filter(p=>p.group_id===gid);
  function matchesPart(p){const q=$('partSearch').value.trim().toLowerCase();return (!activeCategory||categoryFor(p.layer)===activeCategory)&&(!q||[p.name,p.source_id,p.basis,p.location_label].join(' ').toLowerCase().includes(q));}
  // UI categories group existing source layers only; source IDs and database records stay unchanged.
  const categories=[
    {key:'deck',label:'Deck',layers:['deck','wearing','road_surface','haunches','joints','approaches','sidewalks']},
    {key:'superstructure',label:'Primary structure',layers:['girders','box_beams','arches','diaphragms','floor_system','steel','bracing','truss_chords','truss_web','gussets','lacing','repairs','fasteners']},
    {key:'substructure',label:'Substructure',layers:['abutments','piers','foundations','frame_walls','headwalls','walls','casing','fill']},
    {key:'bearings',label:'Bearings',layers:['bearings']},
    {key:'accessories',label:'Accessories',layers:['rails','transitions','drainage','access','monuments','ornament','site','detail_markers']}
  ];
  const categoryFor=layer=>categories.find(c=>c.layers.includes(layer))?.key||'accessories';
  function visibilityCheck(parts,label){const check=el('input');check.type='checkbox';check.setAttribute('aria-label',label+' visible');check.disabled=!ready;const visible=parts.filter(p=>!viewer?.hidden.has(p.id)&&(!viewer?.isolated||viewer.isolated.has(p.id))).length;check.checked=visible===parts.length;check.indeterminate=visible>0&&visible<parts.length;check.onclick=e=>e.stopPropagation();check.onchange=()=>{if(!ready)return;if(check.checked)viewer.show(parts.map(p=>p.id));else viewer.hide(parts.map(p=>p.id));activeCategory=null;renderCategoryChips();renderTree();};return check;}
  function renderTree(){
    if(!data)return;
    const oldGroups=new Set([...document.querySelectorAll('.group[open]')].map(n=>n.dataset.group));
    const oldCategories=new Set([...document.querySelectorAll('.assembly[open]')].map(n=>n.dataset.category));
    const searching=!!$('partSearch').value.trim();$('memberTree').replaceChildren();let found=0;
    for(const category of categories){
      const groups=data.groups.filter(g=>categoryFor(g.source_layer)===category.key&&partsFor(g.id).some(matchesPart));if(!groups.length)continue;
      const all=data.parts.filter(p=>categoryFor(p.layer)===category.key),filtered=all.filter(matchesPart);found+=filtered.length;
      const assembly=el('details','assembly');assembly.dataset.category=category.key;
      const heading=el('summary','assembly-summary');heading.append(visibilityCheck(all,category.label),el('span','',category.label),el('small','',fmt(filtered.length)));assembly.append(heading);
      for(const g of groups){const parts=partsFor(g.id).filter(matchesPart),details=el('details','group');details.dataset.group=g.id;
        const summary=el('summary');summary.append(visibilityCheck(partsFor(g.id),g.label),el('span','group-title',g.label),el('small','',parts.length));details.append(summary);
        details.addEventListener('toggle',e=>{if(e.target===details&&details.open)populateGroup(details,g.id);});assembly.append(details);
        if(oldGroups.has(g.id)||searching){details.open=true;populateGroup(details,g.id);}
      }
      assembly.open=oldCategories.has(category.key)||searching||activeCategory===category.key;$('memberTree').append(assembly);
    }
    if(!found)$('memberTree').append(el('p','empty','No matching components.'));
    $('treeHint').textContent=searching?found+' matches':'Expand a category for details';
  }
  function populateGroup(details,gid){if(!data)return;details.querySelectorAll(':scope > :not(summary)').forEach(n=>n.remove());const all=partsFor(gid),ids=all.map(p=>p.id),group=data.groups.find(g=>g.id===gid);const actions=el('div','group-actions');for(const [label,fn] of [['Select group',()=>selectParts(ids,group.label)],['Isolate group',()=>{activeCategory=null;selectParts(ids,group.label);viewer.isolate(ids);renderCategoryChips();renderTree();}],['Zoom',()=>{selectParts(ids,group.label,true);}]]){const b=button(label,()=>{if(ready)fn();});b.disabled=!ready;actions.append(b);}details.append(actions);
    const parts=all.filter(matchesPart),locations=new Map();for(const p of parts){const loc=p.location_label||'Common / location not specified';if(!locations.has(loc))locations.set(loc,[]);locations.get(loc).push(p);}
    for(const [label,items] of locations){const section=el('div','location-group');if(locations.size>1||items[0].location_label)section.append(el('div','location-heading',label));let shown=0;const add=()=>{section.querySelector('.load-more')?.remove();const target=Math.max(shown+60,items.findIndex(p=>selected.includes(p.id))+1);for(const p of items.slice(shown,target)){const b=button(p.name,()=>selectParts([p.id]),'part-button');b.dataset.id=p.id;b.title=p.source_id;b.disabled=!ready;b.classList.toggle('selected',selected.includes(p.id));b.classList.toggle('is-hidden',viewer?.hidden.has(p.id));section.append(b);}shown=Math.min(target,items.length);if(shown<items.length)section.append(button((items.length-shown)+' more',add,'load-more'));};add();details.append(section);}
  }
  $('partSearch').oninput=renderTree;
  $('showAll').onclick=()=>{if(ready){$('memberTree').replaceChildren();applyCategory(null);}};
  $('clearIsolation').onclick=()=>{if(ready)applyCategory(null);};
  $('fitModel').onclick=()=>{if(ready)viewer.fit();};
  document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{if(!ready)return;viewer.fit(null,b.dataset.view);document.querySelectorAll('[data-view]').forEach(x=>x.classList.toggle('active',x===b));});
  $('deckOpacity').oninput=()=>{if(!ready)return;viewer.setDeckOpacity(+$('deckOpacity').value/100);$('opacityValue').textContent=$('deckOpacity').value+'%';};
  const clip=()=>{if(!ready)return;$('clipPosition').disabled=!$('clipEnabled').checked;$('clipPosition').hidden=!$('clipEnabled').checked;viewer.setClip($('clipEnabled').checked,+$('clipPosition').value);};$('clipEnabled').onchange=clip;$('clipPosition').oninput=clip;
  function setTab(value){tab=value;document.querySelectorAll('[data-tab]').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.tab===value)));if(document.querySelector('.workbench').dataset.pane==='inspector')mobilePane('inspector');renderInspector();}
  document.querySelectorAll('[data-tab]').forEach(b=>{b.onclick=()=>setTab(b.dataset.tab);b.onkeydown=e=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();const tabs=[...document.querySelectorAll('[data-tab]')];const i=tabs.indexOf(b),next=e.key==='Home'?0:e.key==='End'?tabs.length-1:(i+(e.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;tabs[next].focus();tabs[next].click();};});
  function pageLinks(pages){const row=el('div','page-links');for(const page of [...new Set(pages)].sort((a,b)=>a-b))row.append(button('p. '+page,()=>openDrawing(page)));return row;}
  function supplementalLinks(parts){
    const box=el('div','supplemental-links'),seen=new Set();
    for(const p of parts)for(const item of [...(p.supplementary_sources||[]),...(p.source_refs||[])]){
      const id=String(item.document_id||item.source_id),ref=data.references.find(r=>String(r.metadata?.id)===id);
      if(!ref||ref.metadata?.sha256===data.documents[0]?.sha256)continue;
      const url=ref.local_url||(safeExternal(ref.url)?ref.url:null);if(!url)continue;
      for(const page of item.pdf_pages||[]){const key=id+':'+page;if(seen.has(key))continue;seen.add(key);
        const a=anchor('Source '+id+' · p. '+page,url+'#page='+page,'reference-link');a.target='_blank';a.rel='noopener';a.title=ref.metadata?.title||ref.title;box.append(a);
      }
    }
    if(seen.size)box.prepend(el('h3','','Supplemental source pages'));
    return box;
  }
  function selectionActions(){const actions=el('div','inspector-actions');const toModel=()=>{if(!['model','analysis'].includes(workspaceMode)){returnMode=null;openWorkspace('model');}};for(const [label,fn] of [['Focus selection',()=>{toModel();viewer.show(selected);viewer.fit(selected);}],['Isolate selection',()=>{toModel();activeCategory=null;viewer.isolate(selected);renderCategoryChips();renderTree();}],['Hide',()=>{viewer.hide(selected);renderTree();}],['Clear selection',()=>selectParts([])]]){const b=button(label,()=>{if(ready)fn();});b.disabled=!ready;actions.append(b);}return actions;}
  // Coverage statuses mix codes (not_modeled) with source phrases; show both as sentences. Gaps get the one warning colour.
  const statusLabel=s=>{if(!s)return 'Source reference';const t=/^[a-z_]+$/.test(s)?s.replace(/_/g,' '):s;return t.charAt(0).toUpperCase()+t.slice(1);};
  const GAPS=new Set(['not_modeled','missing','Additional source documents needed','Product unconfirmed; placeholder envelope']);
  const isGap=item=>GAPS.has(item.status);
  const statusPill=item=>el('span','coverage-status'+(isGap(item)?' gap':''),statusLabel(item.status));
  function coverageRow(item){const row=el('article','coverage-row');row.append(el('h3','',item.feature),statusPill(item),el('p','',item.detail));if(item.sources.length)row.append(el('small','','Source: '+item.sources.join(', ')));return row;}
  function coverageLines(items,limit){const list=el('div','coverage-list');for(const item of [...items].sort((a,b)=>isGap(b)-isGap(a)).slice(0,limit)){const row=el('div','coverage-line');row.append(el('span','',item.feature),statusPill(item));list.append(row);}return list;}
  const linkedCoverage=ids=>{const linked=new Set(data.coverage_links.filter(x=>ids.includes(x.component_id)).map(x=>x.coverage_id));return data.coverage.filter(x=>linked.has(x.id));};
  // Dimension keys carry their unit as a suffix (depth_in, centre_y_m): show a readable label and the unit; the source key stays in the tooltip.
  const UNITS={in:'in',ft:'ft',m:'m',mm:'mm',deg:'°',pct:'%',percent:'%'};
  function dimensionList(dims){const dl=el('dl','property-list dimensions');for(const [key,value] of Object.entries(dims)){const m=key.match(/^(.+)_(in|ft|m|mm|deg|pct|percent)$/),name=(m?m[1]:key).replace(/_/g,' '),numeric=typeof value==='number',row=el('div'),dt=el('dt','',name.charAt(0).toUpperCase()+name.slice(1)),dd=el('dd',numeric?'num':'');dt.title='Source field: '+key;dd.append(numeric?dimensionValue(value):typeof value==='object'?JSON.stringify(value):String(value));if(m&&numeric)dd.append(el('span','unit',(['deg','pct','percent'].includes(m[2])?'':' ')+UNITS[m[2]]));row.append(dt,dd);dl.append(row);}return dl;}
  // The first pages a component cites show as thumbnails, the rest as page buttons; each page appears once.
  const pageThumb=page=>'/api/drawing/'+data.id+'/'+page+'-thumb.png';
  function pageThumbs(pages,limit=4){const list=[...new Set(pages)].sort((a,b)=>a-b),wrap=el('div','page-stack'),grid=el('div','page-thumbs');for(const page of list.slice(0,limit)){const b=el('button','page-thumb');b.type='button';const img=el('img');img.src=pageThumb(page);img.alt='';img.loading='lazy';b.append(img,el('span','','p. '+page));b.onclick=()=>openDrawing(page);grid.append(b);}wrap.append(grid);if(list.length>limit)wrap.append(pageLinks(list.slice(limit)));return wrap;}
  // With nothing selected the panel answers "how complete is this model, and what is still missing?" first.
  function renderOverview(host){const gaps=data.coverage.filter(isGap);host.append(el('p','kicker','Bridge overview'),el('h2','',data.name));const status=el('div','status-line');status.append(badge(data));host.append(status,el('p','lead',data.detail_note));
    if(gaps.length)host.append(el('h3','','Not modeled or missing ('+gaps.length+')'),coverageLines(gaps,5));
    if(data.coverage.length)host.append(button('All coverage ('+data.coverage.length+')',()=>setTab('coverage'),'text-button more-link'));
    host.append(el('h3','','Bridge'),propertyList([['Structure ID',data.structure_id],['County',data.county],['Type',data.structure_type],['Crossing',data.waterway],['Maintenance agency / source',data.maintenance||data.owner],['Ownership / maintenance year',data.ownership_data_year],['Modeled spans',data.spans],['Modeled deck length',data.deck_length_m?fmt(data.deck_length_m)+' m':null],['Model scope',data.scope],['Model version',data.revision],['Location',data.latitude.toFixed(6)+', '+data.longitude.toFixed(6)]]));
    if(data.location_source.note)host.append(el('h3','','Location source'),el('p','source-note',data.location_source.note));
    host.append(el('p','empty','Select a component in the tree or the model to see its dimensions and source drawings.'));}
  // Drawings mode, right panel: what this sheet is and which modeled components cite it.
  function printedSheet(page){for(const p of data.parts){const i=p.pdf_pages.indexOf(page);if(i>=0&&p.sheets.length===p.pdf_pages.length)return p.sheets[i];}return null;}
  function renderSheetInfo(host,parts){const doc=data.documents[0];if(!doc){host.append(el('p','empty','No drawing set is registered for this bridge.'));return;}
    const linked=data.parts.filter(p=>p.pdf_pages.includes(drawingPage)),sheet=printedSheet(drawingPage);
    host.append(el('p','kicker',doc.title),el('h2','','PDF page '+drawingPage),el('p','small muted',(sheet!==null?'Printed sheet '+sheet+' · ':'')+fmt(doc.page_count)+' pages in the set'));
    if(parts.length){const pages=[...new Set(parts.flatMap(p=>p.pdf_pages))].sort((a,b)=>a-b);host.append(el('h3','',parts.length===1?'Pages citing '+parts[0].name:'Pages citing the selection'),pages.length?pageLinks(pages):el('p','empty','No PDF pages are linked to the selection.'));}
    host.append(el('h3','','Components on this page'+(linked.length?' ('+fmt(linked.length)+')':'')));
    if(!linked.length)host.append(el('p','empty','No modeled component cites this page.'));
    else{const groups=new Map();for(const p of linked){const g=data.groups.find(x=>x.id===p.group_id)?.label||'Other';if(!groups.has(g))groups.set(g,[]);groups.get(g).push(p);}
      const list=el('div','linked-list');for(const [g,items] of groups){list.append(el('p','linked-group',g+' · '+items.length));for(const p of items.slice(0,40)){const b=button(p.name,()=>selectParts([p.id]),'linked-part'+(selected.includes(p.id)?' selected':''));b.title=p.source_id;list.append(b);}if(items.length>40)list.append(el('p','small muted','+ '+(items.length-40)+' more in this group'));}
      const ids=linked.map(p=>p.id);host.append(list,button('Show these in 3D',()=>{returnMode=null;openWorkspace('model');activeCategory=null;selectParts(ids,'Components on PDF page '+drawingPage);viewer.isolate(ids);viewer.fit(ids);renderCategoryChips();renderTree();},'primary'));}
    if(data.source_note)host.append(el('h3','','Drawing notes'),el('p','source-note',data.source_note));
    if(data.references.length){host.append(el('h3','','Standards and references used by the model'));for(const ref of data.references){if(!safeExternal(ref.url))continue;const a=anchor(ref.metadata?.title||ref.title,ref.local_url||ref.url,'reference-link');a.target='_blank';a.rel='noopener';const row=el('p','small');row.append(a);host.append(row);}}
  }
  // The page list renders once per bridge; its thumbnails load as they scroll into view.
  function renderPageRail(){if(!data?.documents.length||railFor===data.id)return;railFor=data.id;const doc=data.documents[0],rail=$('pageRail'),counts=new Map();for(const p of data.parts)for(const pg of p.pdf_pages)counts.set(pg,(counts.get(pg)||0)+1);
    $('pageRailCount').textContent=fmt(doc.page_count);rail.replaceChildren();
    for(let page=1;page<=doc.page_count;page++){const n=counts.get(page)||0,b=el('button','rail-page'),img=el('img');b.type='button';b.dataset.page=page;img.loading='lazy';img.src=pageThumb(page);img.alt='';b.append(img,el('span','','p. '+page),el('small','',n?n+' linked':'—'));b.setAttribute('aria-label','PDF page '+page+(n?', '+n+' linked components':''));b.onclick=()=>{drawingPage=page;renderDrawing();};rail.append(b);}}
  function renderInspector(){const host=$('inspector');window.bridgeAnalysis.detach();host.classList.remove('fem-inspector');host.replaceChildren();if(!data)return;const parts=selected.map(id=>data.parts.find(p=>p.id===id)).filter(Boolean);const p=parts.length===1?parts[0]:null;
    if(tab==='analysis'){window.bridgeAnalysis.mount(host,data,viewer,selected,ids=>selectParts(ids));return;}
    if(tab==='properties'){
      if(!parts.length){renderOverview(host);return;}
      host.append(el('p','kicker',p?(data.groups.find(g=>g.id===p.group_id)?.label||'Component'):'Member group'),el('h2','',p?p.name:selectionLabel||parts.length+' components'),el('p','id-line',p?p.source_id:parts.length+' components selected'),selectionActions());
      if(p){host.append(propertyList([['Specified location',p.location_label],['Location basis',p.location_basis],['Modeling basis',p.basis]]));if(p.note)host.append(el('h3','','Component notes'),el('p','source-note',p.note));if(Object.keys(p.dimensions).length)host.append(el('h3','','Source dimensions'),dimensionList(p.dimensions));if(p.pdf_pages.length)host.append(el('h3','','Drawings'),pageThumbs(p.pdf_pages));host.append(supplementalLinks([p]));if(p.sheets.length)host.append(el('p','small muted','Printed sheet '+p.sheets.join(', ')));const cover=linkedCoverage([p.id]);if(cover.length)host.append(el('h3','','Coverage'),coverageLines(cover,3),button(cover.length>3?'All linked coverage ('+cover.length+')':'Open coverage',()=>setTab('coverage'),'text-button more-link'));if(p.volume_m3!==null)host.append(el('h3','','Model geometry'),propertyList([['Individual geometry volume',dimensionValue(p.volume_m3)+' m³']]),el('p','small muted','Assembly boundaries may overlap. This is not a quantity takeoff value.'));}
      else{const pages=parts.flatMap(p=>p.pdf_pages);host.append(el('p','source-note','Group actions include all members, regardless of search results or collapsed tree branches.'));if(pages.length)host.append(el('h3','','Related drawings'),pageLinks(pages));host.append(supplementalLinks(parts));}
    }else if(tab==='drawings'){renderSheetInfo(host,parts);
    }else{
      host.append(el('h2','','Detail coverage'),badge(data),el('p','source-note',data.detail_note));let items=data.coverage;if(parts.length){const linked=new Set(data.coverage_links.filter(x=>selected.includes(x.component_id)).map(x=>x.coverage_id));if(linked.size){items=items.filter(x=>linked.has(x.id));host.append(el('p','small muted','These coverage items are directly linked to the selected components.'));}else host.append(el('p','small muted','No component-specific coverage links exist; bridge-wide coverage is shown.'));}
      for(const item of [...items].sort((a,b)=>isGap(b)-isGap(a)))host.append(coverageRow(item));
      if(data.assumptions.length){host.append(el('h3','','Assumptions and source limitations'));const list=el('ul','assumptions');for(const note of data.assumptions)list.append(el('li','',note));host.append(list);}
    }
  }
  // Page buttons anywhere open the Drawings mode; coming from another mode shows a way back.
  function openDrawing(page){if(!data?.documents.length)return;drawingPage=Math.max(1,Math.min(page,data.documents[0].page_count));if(workspaceMode==='drawings'){renderDrawing();return;}returnMode=workspaceMode;openWorkspace('drawings');}
  function applyZoom(){$('drawingImage').classList.toggle('zoomed',zoomed);$('zoomToggle').setAttribute('aria-pressed',String(zoomed));$('zoomToggle').textContent=zoomed?'Fit width':'Actual size';}
  function renderDrawing(){if(!data?.documents.length)return;const doc=data.documents[0],seq=++drawingRequest;drawingPage=Math.max(1,Math.min(Math.floor(drawingPage)||1,doc.page_count));
    $('drawingTitle').textContent=data.name+' · PDF page '+drawingPage;$('pageNumber').value=drawingPage;$('pageNumber').max=doc.page_count;$('pageTotal').textContent='of '+fmt(doc.page_count);$('pdfOriginal').href=doc.url+'#page='+drawingPage;$('prevPage').disabled=drawingPage===1;$('nextPage').disabled=drawingPage===doc.page_count;$('closeDrawing').hidden=!returnMode;$('closeDrawing').textContent='← Back to '+({members:'Data',analysis:'Analysis'}[returnMode]||'3D');
    $('drawingLoading').hidden=false;$('drawingLoading').textContent='Loading drawing…';$('drawingImage').hidden=true;applyZoom();$('drawingSheet').scrollTo(0,0);
    $('drawingImage').onload=()=>{if(seq!==drawingRequest)return;$('drawingLoading').hidden=true;$('drawingImage').hidden=false;};$('drawingImage').onerror=()=>{if(seq===drawingRequest)$('drawingLoading').textContent='Drawing preview unavailable. Open the original PDF.';};$('drawingImage').src='/api/drawing/'+data.id+'/'+drawingPage+'.png';$('drawingImage').alt=data.name+', PDF page '+drawingPage;
    document.querySelectorAll('.rail-page').forEach(b=>{const on=Number(b.dataset.page)===drawingPage;b.classList.toggle('active',on);if(on){b.setAttribute('aria-current','page');b.scrollIntoView({block:'nearest',inline:'nearest'});}else b.removeAttribute('aria-current');});
    if(workspaceMode==='drawings'){history.replaceState(null,'',workspaceHash());if(tab==='drawings')renderInspector();}}
  $('closeDrawing').onclick=()=>{const back=returnMode||'model';returnMode=null;openWorkspace(back);};$('zoomToggle').onclick=()=>{zoomed=!zoomed;applyZoom();};$('prevPage').onclick=()=>{drawingPage--;renderDrawing();};$('nextPage').onclick=()=>{drawingPage++;renderDrawing();};$('pageNumber').onchange=()=>{const n=Number($('pageNumber').value);drawingPage=Number.isFinite(n)?Math.max(1,Math.min(Math.floor(n),data.documents[0].page_count)):1;renderDrawing();};$('drawingImage').onclick=()=>{zoomed=!zoomed;applyZoom();};
  function applyCategory(key){if(!ready)return;activeCategory=key;$('partSearch').value='';selected=[];selectionLabel='';viewer.select([]);if(key)viewer.isolate(data.parts.filter(p=>categoryFor(p.layer)===key).map(p=>p.id));else{viewer.showAll();viewer.fit();}renderCategoryChips();renderTree();renderInspector();}
  function renderCategoryChips(){if(!data)return;const host=$('categoryChips');host.replaceChildren();const choices=[{key:null,label:'All'},...categories.filter(c=>data.parts.some(p=>categoryFor(p.layer)===c.key))];for(const item of choices){const b=button(item.label,()=>applyCategory(item.key));b.dataset.categoryFilter=item.key||'all';b.disabled=!ready;b.title=item.key?item.label+' only in the model and tree':'Show all components in the model and tree';const pressed=activeCategory===item.key&&(item.key!==null||!viewer?.isolated);b.classList.toggle('active',pressed);b.setAttribute('aria-pressed',String(pressed));host.append(b);}}
  function prepareWorkspace(){renderCategoryChips();$('registerExport').href='/export/'+data.id+'.csv';$('registerGroup').replaceChildren();const all=el('option','','All types');all.value='';$('registerGroup').append(all);for(const g of data.groups){const o=el('option','',g.label);o.value=g.id;$('registerGroup').append(o);}}
  // Modes share the side panels: Model shows Details/Coverage, Drawings and Analysis take over the right panel, Data shows the register.
  function activateWorkspace(){document.body.dataset.screen='review';document.body.dataset.mode=workspaceMode;document.querySelectorAll('[data-workspace]').forEach(b=>{const on=b.dataset.workspace===workspaceMode;b.classList.toggle('active',on);if(on)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
    const workbench=document.querySelector('.workbench'),register=workspaceMode==='members',sheets=workspaceMode==='drawings';document.querySelector('.mobile-tabs').hidden=register||sheets;document.querySelector('.inspector-tabs').hidden=workspaceMode!=='model';document.querySelector('.mobile-tabs [data-pane="inspector"]').textContent={model:'Details',analysis:'Analysis'}[workspaceMode]||'Details';document.querySelector('.mobile-tabs [data-pane="coverage"]').hidden=workspaceMode!=='model';
    if(data)history.replaceState(null,'',workspaceHash());
    if(workspaceMode!=='model'){workbench.classList.remove('inspector-closed');$('toggleInspector').setAttribute('aria-pressed','true');}
    if(register){mobilePane('inspector');setTab('properties');renderRegisterTabs();renderRegister();return;}
    if(sheets){mobilePane('inspector');renderPageRail();renderDrawing();setTab('drawings');return;}
    if(workspaceMode!=='model'){setTab(workspaceMode);mobilePane('inspector');}else{if(!['properties','coverage'].includes(tab))setTab('properties');}requestAnimationFrame(()=>{viewer?.resize();if(ready)viewer.fit(selected.length?selected:null);});}
  function openWorkspace(mode){workspaceMode=mode;if(!data||$('detailView').hidden){const bid=$('bridgeSelect').value||workspaceBridges()[0]?.id;if(bid)location.hash='#bridge/'+bid;return;}activateWorkspace();}
  document.querySelectorAll('[data-workspace]').forEach(b=>b.onclick=()=>{returnMode=null;openWorkspace(b.dataset.workspace);});
  $('bridgeSelect').onchange=()=>{location.hash='#bridge/'+$('bridgeSelect').value+(workspaceMode==='model'?'':'/'+MODE_SLUG[workspaceMode]);};
  const exportMenu=document.querySelector('.export-menu');exportMenu.addEventListener('click',e=>{if(e.target.closest('a'))exportMenu.open=false;});document.addEventListener('click',e=>{if(exportMenu.open&&!exportMenu.contains(e.target))exportMenu.open=false;});document.addEventListener('keydown',e=>{if(e.key==='Escape'&&exportMenu.open){exportMenu.open=false;exportMenu.querySelector('summary').focus();}});
  $('toggleTree').onclick=()=>togglePanel('tree');$('toggleInspector').onclick=()=>togglePanel('inspector');
  function togglePanel(name){const workbench=document.querySelector('.workbench');workbench.classList.toggle(name+'-closed');$(name==='tree'?'toggleTree':'toggleInspector').setAttribute('aria-pressed',String(!workbench.classList.contains(name+'-closed')));requestAnimationFrame(()=>{viewer?.resize();if(ready)viewer.fit();});}
  // Data mode: category tabs over the register; a row click shows the component in the inspector beside it.
  function renderRegisterTabs(){const host=$('registerTabs');host.replaceChildren();const counts=new Map();for(const p of data.parts){const k=categoryFor(p.layer);counts.set(k,(counts.get(k)||0)+1);}
    for(const item of [{key:null,label:'All',n:data.parts.length},...categories.filter(c=>counts.get(c.key)).map(c=>({...c,n:counts.get(c.key)}))]){const b=el('button');b.type='button';b.setAttribute('role','tab');b.setAttribute('aria-selected',String(registerCategory===item.key));b.append(item.label,el('span','tab-count',fmt(item.n)));b.onclick=()=>{registerCategory=item.key;registerPage=1;$('registerGroup').value='';renderRegisterTabs();renderRegister();};host.append(b);}
    const groupSelect=$('registerGroup'),current=groupSelect.value;groupSelect.replaceChildren();const all=el('option','','All types');all.value='';groupSelect.append(all);for(const g of data.groups){if(registerCategory&&categoryFor(g.source_layer)!==registerCategory)continue;const o=el('option','',g.label);o.value=g.id;groupSelect.append(o);}groupSelect.value=[...groupSelect.options].some(o=>o.value===current)?current:'';}
  function selectRow(p){if(innerWidth<=900){openWorkspace('model');activeCategory=null;$('partSearch').value='';renderCategoryChips();renderTree();selectParts([p.id],'',true);return;}selectParts([p.id]);}
  function renderRegister(){if(!data)return;const query=$('registerSearch').value.trim().toLowerCase(),group=$('registerGroup').value;const rows=data.parts.filter(p=>(!registerCategory||categoryFor(p.layer)===registerCategory)&&(!group||p.group_id===group)&&(!query||[p.source_id,p.name,p.basis,p.location_label].join(' ').toLowerCase().includes(query)));const pages=Math.max(1,Math.ceil(rows.length/50));registerPage=Math.max(1,Math.min(registerPage,pages));$('registerCount').textContent=(rows.length===data.parts.length?fmt(rows.length):fmt(rows.length)+' of '+fmt(data.parts.length))+' components';$('registerPage').textContent=fmt((registerPage-1)*50+(rows.length?1:0))+'–'+fmt(Math.min(registerPage*50,rows.length))+' of '+fmt(rows.length);$('registerPrev').disabled=registerPage===1;$('registerNext').disabled=registerPage===pages;$('registerBody').replaceChildren();for(const p of rows.slice((registerPage-1)*50,registerPage*50)){const tr=el('tr'+(selected.includes(p.id)?' selected':''));tr.dataset.id=p.id;tr.onclick=e=>{if(!e.target.closest('a,button'))selectRow(p);};const name=el('td','name-cell');const open=button(p.name,()=>selectRow(p),'row-link');open.title='Show details';open.disabled=!ready;name.append(open,el('code','',p.source_id));tr.append(name,el('td','',data.groups.find(g=>g.id===p.group_id)?.label),el('td','',p.location_label||'—'),el('td','',p.basis));const drawings=el('td');drawings.append(p.pdf_pages.length?pageLinks(p.pdf_pages):el('span','muted','—'));drawings.append(supplementalLinks([p]));tr.append(drawings);$('registerBody').append(tr);}if(!rows.length){const tr=el('tr'),td=el('td','empty','No matching components.');td.colSpan=5;tr.append(td);$('registerBody').append(tr);}}
  ['registerSearch','registerGroup'].forEach(id=>$(id).oninput=()=>{registerPage=1;renderRegister();});$('registerPrev').onclick=()=>{registerPage--;renderRegister();document.querySelector('.register-table-wrap').scrollTop=0;};$('registerNext').onclick=()=>{registerPage++;renderRegister();document.querySelector('.register-table-wrap').scrollTop=0;};
  // Read-only hooks used by automated verification of real model loading and selection.
  window.bridgeManager={get ready(){return ready;},get data(){return data;},get viewer(){return viewer;},get selected(){return [...selected];},select:selectParts};
  init().catch(e=>error(e.message));
})();
