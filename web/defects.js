// Defects in the 3D workspace: shows what the inspection page saved on this device for the open bridge,
// placed on the model by the viewer (BridgeViewer.setDefects), with a details card in the inspector.
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; };
  // Element and defect wording comes from the inspection app's catalogue (inspect/catalog.js, in the viewer bundle).
  const book = () => window.BridgeInspection?.catalog || { CS_COLORS: {}, CS_NAMES: {}, DEFECTS: {}, FIELDS: {} };
  let data = null, viewer = null, hooks = null, catalog = null, defects = [], inspections = [], inspection = null, current = null, on = false, urls = [];

  const store = () => window.BridgeInspection?.store;

  async function attach(bridge, v, h) {
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
    button.title = inspection ? 'Show defects recorded with the inspection app (D)' : 'No inspection recorded on this device yet: use Inspect';
    let focus = null;
    try { focus = JSON.parse(localStorage.getItem('inspection-focus') || 'null'); } catch {}
    if (focus && focus.bridge === data.id && Date.now() - focus.at < 120000) {
      localStorage.removeItem('inspection-focus');
      const d = await store().get('defects', focus.defect);
      if (d) { inspection = inspections.find(i => i.id === d.inspection_id) || inspection; await show(true); select(d.id, true); return; }
    }
    if (on && inspection) await show(true); else sync();
  }

  function detach() { current = null; defects = []; for (const u of urls) URL.revokeObjectURL(u); urls = []; $('defectLegend').hidden = true; }

  async function load() {
    defects = inspection ? await store().defects(inspection.id) : [];
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

  function legend(placed) {
    const box = $('defectLegend');
    box.replaceChildren();
    const head = el('div', 'legend-head');
    const sel = el('select');
    sel.setAttribute('aria-label', 'Inspection shown');
    for (const i of inspections) sel.append(new Option(`${i.inspection_date} · ${i.inspection_type}`, i.id));
    sel.value = inspection?.id || '';
    sel.onchange = async () => { inspection = inspections.find(i => i.id === sel.value); current = null; await load(); hooks.refresh(); };
    head.append(sel);
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
    if (focus) viewer.focusDefect(id);
  }

  // Called by the workspace whenever it redraws the inspector: puts the defect card on top.
  async function render(host, selectedIds) {
    const d = defects.find(x => x.id === current);
    const part = d && data.parts.find(p => p.mesh_name === d.part);
    if (!d || !part || !selectedIds.includes(part.id)) { current = null; return; }
    const card = el('section', 'defect-details');
    const head = el('div', 'defect-head');
    const { CS_COLORS, CS_NAMES, DEFECTS, FIELDS } = book();
    const tag = el('span', 'defect-tag', `D${d.number}`); tag.style.background = CS_COLORS[d.cs];
    const title = el('div');
    title.append(el('h3', '', `${d.defect_code} ${DEFECTS[d.defect_code]?.name || ''}`), el('p', 'muted', `CS ${d.cs} ${CS_NAMES[d.cs]} · ${part.name}`));
    head.append(tag, title);
    card.append(head);
    const element = catalog.elements.find(e => e.code === d.element_code);
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
    card.append(dl);
    const photos = await store().photos(d.id);
    if (photos.length) {
      const grid = el('div', 'defect-photos');
      for (const p of photos) {
        if (!p.blob) continue;
        const u = URL.createObjectURL(p.blob); urls.push(u);
        const a = el('a'); a.href = u; a.target = '_blank'; a.rel = 'noopener';
        const img = el('img'); img.src = u; img.alt = p.file_name; a.append(img); grid.append(a);
      }
      card.append(grid);
    }
    const actions = el('div', 'defect-actions');
    const open = el('a', 'button', 'Open on sheet'); open.href = `${data.inspection.app_url}/${d.id}`; open.target = 'inspection';
    actions.append(open);
    card.append(actions);
    if (current !== d.id) return;
    host.querySelector('.defect-details')?.remove();
    host.prepend(card);
  }

  document.addEventListener('DOMContentLoaded', () => {
    $('defectsToggle').onclick = () => { if (!$('defectsToggle').disabled && viewer) show(!on); };
    addEventListener('keydown', e => {
      if ((e.key === 'd' || e.key === 'D') && !e.target.closest('input,textarea,select') && !$('defectsToggle').hidden && !$('defectsToggle').disabled) { e.preventDefault(); show(!on); }
    });
    // Defects saved in another tab (the inspection page) appear when this tab is shown again.
    document.addEventListener('visibilitychange', async () => {
      if (document.visibilityState !== 'visible' || !data?.inspection || !viewer) return;
      const before = inspection?.id;
      inspections = (await store().inspections(data.id)).filter(i => !i.deleted);
      inspection = inspections.find(i => i.id === before) || inspections[0] || null;
      $('defectsToggle').disabled = !inspection;
      if (on) await load();
      sync();
    });
  });

  window.bridgeDefects = { attach, detach, select, render };
})();
