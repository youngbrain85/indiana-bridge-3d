// Inspection data in the 3D workspace: what the inspection page saved on this device for the open bridge.
// The viewer places each defect on its member (BridgeViewer.setDefects); they show by default and the Defects
// button (D) hides them. The Inspection data mode lists the same defects and the AASHTO element condition states.
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; };
  const num = n => new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(n);
  // Element quantities are whole units, as in the inspection app's element table.
  const whole = n => new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(n);
  // Element and defect wording comes from the inspection app's catalogue (inspect/catalog.js, in the viewer bundle).
  const book = () => window.BridgeInspection?.catalog || { CS_COLORS: {}, CS_NAMES: {}, DEFECTS: {}, FIELDS: {} };
  const store = () => window.BridgeInspection?.store;
  let data = null, viewer = null, hooks = null, catalog = null, defects = [], loadedFor = null, inspections = [], inspection = null, current = null, on = true, urls = [];
  let pending = Promise.resolve(), table = null;

  function attach(bridge, v, h) { pending = attachNow(bridge, v, h); return pending; }

  async function attachNow(bridge, v, h) {
    detach();
    data = bridge; viewer = v; hooks = h;
    const button = $('defectsToggle'), link = $('inspectLink');
    if (!data.inspection || !store()) { button.hidden = true; link.hidden = true; return; }
    link.href = data.inspection.app_url; link.hidden = false; button.hidden = false;
    try {
      catalog = await (await fetch(data.inspection.sheets_url)).json();
      inspections = (await store().inspections(data.id)).filter(i => !i.deleted);
    } catch { inspections = []; }
    if (data !== bridge) return;
    inspection = inspections[0] || null;
    button.disabled = !inspection;
    button.title = inspection ? 'Show or hide the defects recorded with the inspection app (D)' : 'No inspection recorded on this device yet: use Inspect';
    let focus = null;
    try { focus = JSON.parse(localStorage.getItem('inspection-focus') || 'null'); } catch {}
    if (focus && focus.bridge === data.id && Date.now() - focus.at < 120000) {
      localStorage.removeItem('inspection-focus');
      const d = await store().get('defects', focus.defect);
      if (d) { inspection = inspections.find(i => i.id === d.inspection_id) || inspection; await show(true); select(d.id, true); return; }
    }
    if (on && inspection) await show(true); else sync();
  }

  function detach() { current = null; defects = []; loadedFor = null; catalog = null; inspections = []; inspection = null; table = null; for (const u of urls) URL.revokeObjectURL(u); urls = []; $('defectLegend').hidden = true; }

  async function fetchDefects() {
    if (loadedFor === (inspection?.id || null)) return;
    defects = inspection ? await store().defects(inspection.id) : [];
    loadedFor = inspection?.id || null;
  }

  async function load() {
    await fetchDefects();
    const placed = viewer.setDefects(defects, catalog);
    legend(placed);
  }

  async function show(value) {
    on = value;
    if (on) await load();
    viewer.showDefects(on);
    sync();
  }

  function sync() {
    const b = $('defectsToggle');
    b.setAttribute('aria-pressed', String(on && !b.disabled));
    $('defectLegend').hidden = !(on && inspection);
  }

  // Another inspection chosen (on the canvas legend or above the table): reload, redraw everything that shows it.
  async function choose(id) {
    inspection = inspections.find(i => i.id === id) || null; current = null; loadedFor = null;
    if (on) await load(); else await fetchDefects();
    hooks.refresh();
    if (table?.isConnected) renderData(table);
  }

  function inspectionSelect(label) {
    const sel = el('select');
    sel.setAttribute('aria-label', label);
    for (const i of inspections) sel.append(new Option(`${i.inspection_date} · ${i.inspection_type}`, i.id));
    sel.value = inspection?.id || '';
    sel.onchange = () => choose(sel.value);
    return sel;
  }

  function legend(placed) {
    const box = $('defectLegend');
    box.replaceChildren();
    const head = el('div', 'legend-head');
    head.append(inspectionSelect('Inspection shown'));
    box.append(head);
    const keys = el('div', 'legend-keys');
    const { CS_COLORS, CS_NAMES } = book();
    for (const n of [1, 2, 3, 4]) {
      const k = el('span', 'legend-key'); const dot = el('i'); dot.style.background = CS_COLORS[n];
      k.append(dot, `CS ${n} ${CS_NAMES[n]}`); keys.append(k);
    }
    box.append(keys);
    box.append(el('small', '', `${placed} of ${defects.length} defect${defects.length === 1 ? '' : 's'} placed · saved on this device`));
  }

  function select(id, focus = false) {
    const d = defects.find(x => x.id === id);
    if (!d) return;
    current = id;
    const part = data.parts.find(p => p.mesh_name === d.part);
    hooks.selectParts(part ? [part.id] : [], `D${d.number}`);
    table?.querySelectorAll('tr[data-defect]').forEach(tr => tr.classList.toggle('selected', tr.dataset.defect === id));
    if (focus) viewer.focusDefect(id);
  }

  // From the Inspection data mode: the model view, with the defects shown and this one in front of the camera.
  async function showIn3D(id) {
    if (!on) await show(true);
    hooks.openModel(() => select(id, true));
  }

  const elementOf = d => catalog?.elements.find(e => e.code === d.element_code);
  const csDot = cs => { const { CS_COLORS, CS_NAMES } = book(); const s = el('span', 'cs-mark'); const dot = el('i'); dot.style.background = CS_COLORS[cs]; s.append(dot, `CS ${cs} ${CS_NAMES[cs] || ''}`.trim()); return s; };

  async function card(d, extra) {
    const part = data.parts.find(p => p.mesh_name === d.part);
    const box = el('section', 'defect-details');
    const head = el('div', 'defect-head');
    const { CS_COLORS, CS_NAMES, DEFECTS, FIELDS } = book();
    const tag = el('span', 'defect-tag', `D${d.number}`); tag.style.background = CS_COLORS[d.cs];
    const title = el('div');
    title.append(el('h3', '', `${d.defect_code} ${DEFECTS[d.defect_code]?.name || ''}`), el('p', 'muted', `CS ${d.cs} ${CS_NAMES[d.cs]}${part ? ' · ' + part.name : ''}`));
    head.append(tag, title);
    box.append(head);
    const element = elementOf(d);
    const rows = [['Element', `${d.element_code} ${element?.name || ''}`], ['Quantity', `${d.quantity} ${d.unit}`], ['Location', d.location],
      ['Sheet', `${d.sheet_id} · ${d.view_id}`], ['Inspection', `${inspection.inspection_date} · ${inspection.inspection_type}${inspection.inspectors ? ' · ' + inspection.inspectors : ''}`]];
    for (const f of FIELDS[d.defect_code] || []) {
      const v = d.measurements?.[f.key];
      if (v === null || v === '' || v === undefined || v === false) continue;
      const text = f.type === 'choice' ? (f.options.find(o => o[0] === v)?.[1] || v) : f.type === 'check' ? 'Yes' : `${v} ${f.unit || ''}`.trim();
      rows.push([f.label, text]);
    }
    if (d.cs_reason) rows.push(['CS change', d.cs_reason]);
    if (d.notes) rows.push(['Notes', d.notes]);
    const dl = el('dl', 'property-list');
    for (const [k, v] of rows) { if (!v) continue; const row = el('div'); row.append(el('dt', '', k), el('dd', '', v)); dl.append(row); }
    box.append(dl);
    const photos = await store().photos(d.id);
    if (photos.length) {
      const grid = el('div', 'defect-photos');
      for (const p of photos) {
        if (!p.blob) continue;
        const u = URL.createObjectURL(p.blob); urls.push(u);
        const a = el('a'); a.href = u; a.target = '_blank'; a.rel = 'noopener';
        const img = el('img'); img.src = u; img.alt = p.file_name; a.append(img); grid.append(a);
      }
      box.append(grid);
    }
    const actions = el('div', 'defect-actions');
    if (extra) actions.append(extra);
    const open = el('a', 'button', 'Open on sheet'); open.href = `${data.inspection.app_url}/${d.id}`; open.target = 'inspection';
    actions.append(open);
    box.append(actions);
    return box;
  }

  // Model mode: called whenever the workspace redraws the inspector; puts the selected defect's card on top.
  async function render(host, selectedIds) {
    const d = defects.find(x => x.id === current);
    const part = d && data.parts.find(p => p.mesh_name === d.part);
    if (!d || !part || !selectedIds.includes(part.id)) { current = null; return; }
    const box = await card(d);
    if (current !== d.id) return;
    host.querySelector('.defect-details')?.remove();
    host.prepend(box);
  }

  // Inspection data mode, right panel: the chosen defect, or what this inspection is.
  async function renderPanel(host, selectedIds) {
    await pending;
    let d = defects.find(x => x.id === current);
    const part = d && data.parts.find(p => p.mesh_name === d.part);
    // Clearing the selection (Esc, or another component chosen) also lets go of the defect.
    if (d && part && !selectedIds.includes(part.id)) { d = null; current = null; table?.querySelectorAll('tr.selected').forEach(tr => tr.classList.remove('selected')); }
    if (d) {
      const go = el('button', 'primary', 'Show in 3D'); go.type = 'button'; go.onclick = () => showIn3D(d.id);
      const box = await card(d, go);
      if (current !== d.id || document.body.dataset.mode !== 'inspection') return;
      host.replaceChildren(box);
      return;
    }
    if (document.body.dataset.mode !== 'inspection') return;
    host.replaceChildren();
    if (!inspection) { host.append(el('p', 'kicker', 'Inspection'), el('h2', '', 'No inspection yet'), el('p', 'empty', data?.inspection ? 'Defects recorded with the inspection app on this device appear here.' : 'This bridge has no inspection sheets yet.')); return; }
    host.append(el('p', 'kicker', 'Inspection'), el('h2', '', `${inspection.inspection_date} · ${inspection.inspection_type}`));
    const dl = el('dl', 'property-list');
    for (const [k, v] of [['Inspectors', inspection.inspectors], ['Status', inspection.status], ['Notes', inspection.notes], ['Defects', String(defects.length)], ['Saved', 'On this device']]) {
      if (!v) continue; const row = el('div'); row.append(el('dt', '', k), el('dd', '', v)); dl.append(row);
    }
    host.append(dl, el('p', 'empty', 'Select a defect in the table to see its measurements and photos.'));
  }

  // Inspection data mode, main area: the defects of one inspection, then each element's condition-state quantities.
  async function renderData(host) {
    table = host;
    await pending;
    if (host !== table) return;
    await fetchDefects();
    const photos = inspection ? await store().inspectionPhotos(inspection.id) : [];
    if (host !== table) return;
    host.replaceChildren();
    const heading = el('div', 'insp-heading'), titles = el('div');
    titles.append(el('h2', '', 'Inspection data'), el('p', 'muted', 'Defects recorded on the inspection sheets, saved on this device.'));
    heading.append(titles);
    const tools = el('div', 'insp-tools');
    if (inspections.length) tools.append(inspectionSelect('Inspection'));
    if (data?.inspection) { const a = el('a', 'button', 'Open inspection app'); a.href = data.inspection.app_url; a.target = 'inspection'; tools.append(a); }
    heading.append(tools);
    host.append(heading);
    const empty = (text, action) => { const box = el('div', 'insp-empty'); box.append(el('p', '', text)); if (action) box.append(action); host.append(box); };
    if (!data?.inspection) { empty('This bridge has no inspection sheets yet. Inspection data appears here once its sheets are made and defects are recorded on them.'); return; }
    if (!inspection) { const a = el('a', 'button primary', 'Start an inspection'); a.href = data.inspection.app_url; a.target = 'inspection'; empty('No inspection is recorded on this device yet.', a); return; }
    const { CS_COLORS, CS_NAMES, DEFECTS } = book();
    const counts = new Map(); for (const p of photos) counts.set(p.defect_id, (counts.get(p.defect_id) || 0) + 1);
    const figures = el('dl', 'insp-figures');
    for (const [k, v] of [['Defects', defects.length], ['Elements with defects', new Set(defects.map(d => d.element_code)).size], ['Poor or severe (CS 3–4)', defects.filter(d => d.cs >= 3).length], ['Photos', photos.length]]) {
      const row = el('div'); row.append(el('dt', '', k), el('dd', '', num(v))); figures.append(row);
    }
    host.append(figures);
    const wrap = el('div', 'insp-scroll');
    wrap.append(el('h3', '', `Defects (${defects.length})`));
    if (!defects.length) wrap.append(el('p', 'insp-empty', 'No defects recorded in this inspection yet.'));
    else {
      const t = el('table', 'insp-table'), head = el('tr');
      for (const [text, cls] of [['No.'], ['Element'], ['Defect'], ['Condition'], ['Quantity', 'num'], ['Location'], ['Sheet'], ['Photos', 'num']]) head.append(el('th', cls || '', text));
      const thead = el('thead'); thead.append(head); t.append(thead);
      const body = el('tbody');
      for (const d of defects) {
        const tr = el('tr'); tr.dataset.defect = d.id; tr.tabIndex = 0; tr.classList.toggle('selected', d.id === current);
        const element = elementOf(d), tag = el('span', 'defect-tag', `D${d.number}`); tag.style.background = CS_COLORS[d.cs];
        const first = el('td'); first.append(tag);
        const elementCell = el('td'); elementCell.append(el('span', '', `${d.element_code} ${element?.name || ''}`.trim()));
        tr.append(first, elementCell, el('td', '', `${d.defect_code} ${DEFECTS[d.defect_code]?.name || ''}`.trim()));
        const cs = el('td'); cs.append(csDot(d.cs)); tr.append(cs);
        tr.append(el('td', 'num', `${num(d.quantity)} ${d.unit}`), el('td', 'muted', d.location || '—'), el('td', 'muted', d.sheet_id), el('td', 'num', String(counts.get(d.id) || 0)));
        const pick = () => { if (innerWidth <= 900) showIn3D(d.id); else select(d.id, false); };
        tr.onclick = pick; tr.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(); } };
        body.append(tr);
      }
      t.append(body); wrap.append(t);
    }
    // AASHTO element condition states: each element's total split by CS; CS 1 is what the defects leave.
    const summary = catalog ? window.BridgeInspection.elementSummary(catalog.elements, defects) : [];
    wrap.append(el('h3', '', 'Element condition states'));
    const t = el('table', 'insp-table insp-elements'), head = el('tr');
    head.append(el('th', '', 'Element'), el('th', 'num', 'Total'));
    for (const n of [1, 2, 3, 4]) { const th = el('th', 'num'); th.append(csDot(n)); head.append(th); }
    const thead = el('thead'); thead.append(head); t.append(thead);
    const body = el('tbody');
    for (const e of summary) {
      const tr = el('tr'); tr.append(el('td', '', `${e.code} ${e.name}`), el('td', 'num', `${whole(e.total)} ${e.unit}`));
      for (const q of e.cs) tr.append(el('td', 'num' + (q ? '' : ' muted'), whole(q)));
      if (e.over) tr.classList.add('over');
      body.append(tr);
    }
    t.append(body); wrap.append(t);
    wrap.append(el('p', 'small muted', `CS 1 ${CS_NAMES[1]} is the element total less the recorded defect quantities. Quantities in each element's unit, rounded to whole units.`));
    host.append(wrap);
  }

  document.addEventListener('DOMContentLoaded', () => {
    $('defectsToggle').onclick = () => { if (!$('defectsToggle').disabled && viewer) show(!on); };
    addEventListener('keydown', e => {
      if ((e.key === 'd' || e.key === 'D') && !e.ctrlKey && !e.metaKey && !e.altKey && !e.target.closest('input,textarea,select') && !$('defectsToggle').hidden && !$('defectsToggle').disabled && $('defectsToggle').offsetParent) { e.preventDefault(); show(!on); }
    });
    // Defects saved in another tab (the inspection page) appear when this tab is shown again.
    document.addEventListener('visibilitychange', async () => {
      if (document.visibilityState !== 'visible' || !data?.inspection || !viewer) return;
      const before = inspection?.id;
      inspections = (await store().inspections(data.id)).filter(i => !i.deleted);
      inspection = inspections.find(i => i.id === before) || inspections[0] || null;
      loadedFor = undefined;
      $('defectsToggle').disabled = !inspection;
      if (on) await load(); else await fetchDefects();
      sync();
      if (table?.isConnected) renderData(table);
    });
  });

  window.bridgeDefects = { attach, detach, select, render, renderPanel, renderData };
})();
