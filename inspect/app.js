// Inspection app: record defects on the bridge's inspection sheets, with AASHTO element/defect codes,
// condition states, quantities and photos. Saved on the device first; synced to Supabase when set up.
import { CS_COLORS, CS_NAMES, DEFECTS, ELEMENT_DEFECTS, FIELDS, MATERIAL_ORDER, suggestCS } from './catalog.js';
import { FT, assignView, elementFor, maxDimM, planePoint, quantityFor, round, toCanvas, toView, viewRect } from './geometry.js';
import { SheetCanvas } from './sheet.js';
import * as store from './store.js';
import { preparePhoto, photoURL } from './photos.js';
import { Cloud } from './sync.js';
import { elementSummary } from './summary.js';

const $ = id => document.getElementById(id);
const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; };
const btn = (text, fn, cls = '') => { const b = el('button', cls, text); b.type = 'button'; b.onclick = fn; return b; };
const fmt = (n, d = 1) => new Intl.NumberFormat('en-US', { maximumFractionDigits: d }).format(n);
const today = () => new Date().toLocaleDateString('en-CA');
const INSPECTION_TYPES = ['Routine', 'Initial', 'In-Depth', 'Damage', 'Special', 'Underwater', 'NSTM (fracture critical)', 'Service'];
const CRACK = { 109: 1110 };            // PSC members use 1110; other concrete 1130
const PICKS = [
  { key: 'crack', name: 'Cracking', note: '1130 RC · 1110 PSC', kind: 'line', material: 'Concrete' },
  ...[1080, 1090, 1100, 1120, 1190, 1000, 2210, 2220, 2230, 2240, 4000, 6000, 7000]
    .map(code => ({ key: String(code), code, name: DEFECTS[code].name, note: String(code), kind: DEFECTS[code].kind, material: DEFECTS[code].material })),
];

const state = {
  bridge: (location.hash.match(/^#([a-z0-9-]+)/) || [, 'beechwood'])[1],
  catalog: null, sheet: null, inspection: null, inspections: [], defects: [], photoCounts: {},
  selected: null, draft: null, panel: 'list', scope: 'sheet', pick: null, cloud: new Cloud(), syncing: false,
};
let canvas;

function toast(text, kind = '') {
  const t = $('toast');
  t.textContent = text; t.className = 'toast show ' + kind;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => { t.className = 'toast'; }, 3600);
}

const part = id => state.catalog.parts[id] || { label: id, element: null };
const element = code => state.catalog.elements.find(e => e.code === Number(code));
const sheetById = id => state.catalog.sheets.find(s => s.id === id);
const viewById = (sheet, id) => sheet?.views.find(v => v.id === id);
const fitDefect = (code, elementCode) => {
  if (code === 'crack' || code === 1130 || code === 1110) return CRACK[elementCode] || 1130;
  return Number(code);
};

// ---------------------------------------------------------------- start-up
async function init() {
  canvas = new SheetCanvas($('sheetHost'), { onSketch, onPick: id => selectDefect(id, true), onZoom: k => { $('zoomLevel').textContent = Math.round(k / 2.2 * 100) + '%'; } });
  const response = await fetch(`./inspection/${state.bridge}/sheets.json`);
  if (!response.ok) { $('stageEmpty').textContent = 'This bridge has no inspection sheets yet.'; $('stageEmpty').hidden = false; return; }
  state.catalog = await response.json();
  $('bridgeName').textContent = state.catalog.title;
  document.title = `Inspection · ${state.catalog.title}`;
  $('open3d').href = `./#bridge/${state.bridge}`;
  const config = (await store.setting('cloud')) || window.INSPECT_CLOUD || null;
  state.cloud.configure(config);
  state.penOnly = !!(await store.setting('pen_only'));
  canvas.penSeen = state.penOnly;
  bindChrome();
  await loadInspections();
  const last = await store.setting(`sheet:${state.bridge}`);
  renderSheetList();
  await openSheet(sheetById(last) ? last : state.catalog.sheets[0].id);
  updateStatus();
  const wanted = location.hash.match(/^#[a-z0-9-]+\/([0-9a-f-]{36})$/);
  if (wanted) {
    const d = await store.get('defects', wanted[1]);
    if (d && !d.deleted) {
      if (d.inspection_id !== state.inspection?.id) await loadInspections(d.inspection_id);
      await selectDefect(d.id, true);
    }
  }
  if (!state.inspection) newInspectionDialog(true);
  // Fetch every sheet once so the offline cache has them all.
  setTimeout(() => { for (const s of state.catalog.sheets) fetch(`./inspection/${state.bridge}/${s.svg}`).catch(() => {}); }, 2500);
  if ('serviceWorker' in navigator && location.protocol !== 'file:') navigator.serviceWorker.register('./inspect-sw.js', { scope: './inspect' }).catch(() => {});
}

async function loadInspections(selectId) {
  state.inspections = await store.inspections(state.bridge);
  const remembered = selectId || (await store.setting(`inspection:${state.bridge}`));
  state.inspection = state.inspections.find(i => i.id === remembered) || state.inspections[0] || null;
  const sel = $('inspectionSelect');
  sel.replaceChildren(...state.inspections.map(i => { const o = el('option', '', `${i.inspection_date} · ${i.inspection_type}${i.inspectors ? ' · ' + i.inspectors : ''}`); o.value = i.id; return o; }));
  const add = el('option', '', 'New inspection…'); add.value = '__new'; sel.append(add);
  if (state.inspection) sel.value = state.inspection.id;
  await loadDefects();
}

async function loadDefects() {
  state.defects = state.inspection ? await store.defects(state.inspection.id) : [];
  // Numbers of deleted defects are not reused.
  state.allNumbers = state.inspection ? (await store.all('defects', 'inspection_id', state.inspection.id)).map(d => d.number) : [];
  const photos = state.inspection ? await store.inspectionPhotos(state.inspection.id) : [];
  state.photoCounts = {};
  for (const p of photos) state.photoCounts[p.defect_id] = (state.photoCounts[p.defect_id] || 0) + 1;
  renderSheetList();
  drawDefects();
  renderPanel();
}

function bindChrome() {
  $('inspectionSelect').onchange = async e => {
    if (e.target.value === '__new') { e.target.value = state.inspection?.id || ''; newInspectionDialog(); return; }
    await store.setting(`inspection:${state.bridge}`, e.target.value);
    state.selected = null;
    await loadInspections(e.target.value);
  };
  $('zoomIn').onclick = () => canvas.zoomBy(1.4);
  $('zoomOut').onclick = () => canvas.zoomBy(1 / 1.4);
  $('zoomFit').onclick = () => canvas.fit();
  $('sheetPick').onchange = e => openSheet(e.target.value);
  $('summaryButton').onclick = () => { state.panel = state.panel === 'summary' ? 'list' : 'summary'; renderPanel(); };
  $('settingsButton').onclick = settingsDialog;
  $('syncButton').onclick = sync;
  $('cancelDraw').onclick = () => cancelDraft();
  $('panTool').onclick = () => setTool('pan');
  $('drawTool').onclick = () => setTool('draw');
  addEventListener('keydown', e => {
    if (e.target.closest('input,textarea,select,dialog')) return;
    if (e.key === 'Escape' && state.panel === 'draw') cancelDraft();
    if (e.key === '+' || e.key === '=') canvas.zoomBy(1.4);
    if (e.key === '-') canvas.zoomBy(1 / 1.4);
    if (e.key === '0') canvas.fit();
  });
  addEventListener('online', updateStatus); addEventListener('offline', updateStatus);
}

// ---------------------------------------------------------------- sheets
function renderSheetList() {
  if (!state.catalog) return;
  const counts = {};
  for (const d of state.defects) counts[d.sheet_id] = (counts[d.sheet_id] || 0) + 1;
  const list = $('sheetList');
  list.replaceChildren(...state.catalog.sheets.map(s => {
    const b = btn('', () => openSheet(s.id), 'sheet-item' + (state.sheet?.id === s.id ? ' active' : ''));
    b.setAttribute('aria-current', state.sheet?.id === s.id ? 'page' : 'false');
    b.append(el('span', 'sheet-code', s.id), el('span', 'sheet-title', s.title));
    if (counts[s.id]) b.append(el('span', 'sheet-count', counts[s.id]));
    return b;
  }));
  $('sheetPick').replaceChildren(...state.catalog.sheets.map(s => { const o = el('option', '', `${s.id} · ${s.title}${counts[s.id] ? ` (${counts[s.id]})` : ''}`); o.value = s.id; return o; }));
  if (state.sheet) $('sheetPick').value = state.sheet.id;
  $('sheetCount').textContent = state.catalog.sheets.length;
}

async function openSheet(id) {
  const sheet = sheetById(id);
  if (!sheet) return;
  if (state.panel === 'draw') cancelDraft();
  state.sheet = sheet;
  await store.setting(`sheet:${state.bridge}`, id);
  const text = await (await fetch(`./inspection/${state.bridge}/${sheet.svg}`)).text();
  canvas.load(text, state.catalog.canvas_mm);
  renderSheetList();
  drawDefects();
  if (state.panel === 'list') renderPanel();
  $('stageTitle').textContent = `${sheet.id} · ${sheet.title}`;
}

function defectPoints(d) {
  const view = viewById(sheetById(d.sheet_id), d.view_id);
  return view ? d.path.map(p => toCanvas(p, view, state.catalog.canvas_mm)) : [];
}

function drawDefects() {
  if (!state.sheet || !canvas) return;
  const list = state.defects.filter(d => d.sheet_id === state.sheet.id && d.id !== state.draft?.id)
    .map(d => ({ id: d.id, number: d.number, kind: d.kind, cs: d.cs, code: d.defect_code, points: defectPoints(d), selected: d.id === state.selected }));
  if (state.draft?.path && state.draft.sheet_id === state.sheet.id) {
    const view = viewById(state.sheet, state.draft.view_id);
    list.push({ id: 'draft', number: state.draft.number, kind: state.draft.kind, cs: state.draft.cs, code: state.draft.defect_code,
      points: state.draft.path.map(p => toCanvas(p, view, state.catalog.canvas_mm)), selected: true });
  }
  canvas.showDefects(list);
}

// ---------------------------------------------------------------- defects: pick, draw, form
function startDefect() {
  if (!state.inspection) { newInspectionDialog(); return; }
  state.selected = null;
  state.panel = 'pick';
  drawDefects();
  renderPanel();
}

function choosePick(pick) {
  state.pick = pick;
  state.panel = 'draw';
  setTool('draw');
  const verb = { line: 'Trace the crack or bar along its length', area: 'Outline the affected area', point: 'Tap the location' }[pick.kind];
  $('drawHint').textContent = `${verb}. Pinch or two fingers to move the sheet.`;
  $('drawBanner').hidden = false;
  document.body.dataset.drawing = '1';
  renderPanel();
}

function setTool(tool) {
  const kind = state.panel === 'draw' ? state.pick.kind : null;
  canvas.setMode(tool === 'draw' && kind ? 'draw' : 'pan', kind);
  $('panTool').setAttribute('aria-pressed', String(canvas.mode === 'pan'));
  $('drawTool').setAttribute('aria-pressed', String(canvas.mode === 'draw'));
  $('drawTool').disabled = !kind;
}

function cancelDraft() {
  state.draft = null; state.pick = null; state.panel = 'list';
  $('drawBanner').hidden = true; delete document.body.dataset.drawing;
  setTool('pan');
  canvas.clearLive();
  drawDefects();
  renderPanel();
}

function onSketch(points, kind, problem) {
  if (!points) { if (problem) toast(kind === 'area' ? 'Outline a larger area.' : 'Draw a longer stroke, or zoom in.'); return; }
  const hit = assignView(points, state.sheet, state.catalog.canvas_mm);
  if (!hit || hit.share < 0.6) { canvas.clearLive(); toast('Keep the sketch inside one view.', 'warn'); return; }
  const view = hit.view;
  const path = round(points.map(p => toView(p, view, state.catalog.canvas_mm)).map(([u, v]) => [Math.min(1, Math.max(0, u)), Math.min(1, Math.max(0, v))]));
  const found = elementFor(path, view, kind);
  if (!found.part) { canvas.clearLive(); toast('Draw on a shaded surface: those are the inspected elements.', 'warn'); return; }
  canvas.clearLive();
  const p = part(found.part);
  const code = fitDefect(state.pick.code || state.pick.key, p.element);
  const number = Math.max(0, ...state.defects.map(d => d.number), ...(state.allNumbers || [])) + 1;
  state.draft = {
    id: store.uuid(), inspection_id: state.inspection.id, bridge_id: state.bridge, number,
    sheet_id: state.sheet.id, view_id: view.id, part: found.part, part_auto: true, element_code: p.element,
    defect_code: code, kind, path, measurements: {}, quantity: null, unit: element(p.element)?.unit, quantity_manual: false,
    cs: null, cs_suggested: null, cs_basis: '', cs_reason: '', structural_review: false, notes: '',
    created_at: store.now(), updated_at: store.now(), deleted: false, isNew: true, newPhotos: [], removedPhotos: [],
  };
  if (code === 1080 && kind === 'area') state.draft.measurements.form = '';
  recompute(state.draft);
  $('drawBanner').hidden = true; delete document.body.dataset.drawing;
  setTool('pan');
  state.panel = 'form';
  drawDefects();
  renderPanel();
}

function recompute(d) {
  const sheet = sheetById(d.sheet_id), view = viewById(sheet, d.view_id), p = part(d.part);
  const e = element(p.element);
  d.element_code = p.element; d.unit = e?.unit;
  if (!d.quantity_manual) {
    const q = quantityFor({ kind: d.kind, path: d.path, view, unit: e?.unit, axis: p.axis });
    d.quantity = q.quantity; d.quantity_basis = q.basis;
  }
  const size = maxDimM(d.path, view) / FT * 12;
  d.auto = { size_in: Math.round(size * 2) / 2 };
  const s = suggestCS(d.defect_code, d.measurements);
  d.cs_suggested = s?.cs || null; d.cs_basis = s?.basis || '';
  if (!d.cs_chosen) d.cs = d.cs_suggested;
  d.location = locationText(d.path, view);
}

function locationText(path, view) {
  const n = path.length;
  const c = path.reduce((a, p) => [a[0] + p[0] / n, a[1] + p[1] / n], [0, 0]);
  const g = planePoint(c, view);
  const datum = state.catalog.datum;
  const sta = datum.station_ft_at_origin + g[0] / FT;
  const offset = -g[2] / FT;
  const elv = datum.elevation_ft_at_origin + g[1] / FT;
  const staText = `STA ${Math.floor(sta / 100)}+${(sta % 100).toFixed(1).padStart(4, '0')}`;
  const offText = `${fmt(Math.abs(offset))} ft ${offset >= 0 ? 'LT' : 'RT'}`;
  const elText = `EL ${fmt(elv)}`;
  const N = view.normal.map(Math.abs);
  if (N[1] > 0.9) return `${staText} · ${offText}`;            // plan or underside
  if (N[0] > 0.9) return `${offText} · ${elText}`;             // bent or end bent face
  return `${staText} · ${elText}`;                              // elevation of a girder or barrier
}

async function selectDefect(id, frame = false) {
  if (state.panel === 'draw' || state.panel === 'form' && state.draft?.isNew) return;
  const d = state.defects.find(x => x.id === id);
  if (!d) return;
  if (d.sheet_id !== state.sheet.id) await openSheet(d.sheet_id);
  state.selected = id;
  const photos = await store.photos(id);
  state.draft = { ...structuredClone({ ...d }), cs_chosen: true, newPhotos: [], removedPhotos: [], photos };
  recompute(state.draft);
  state.panel = 'form';
  drawDefects();
  renderPanel();
  if (frame) {
    const pts = defectPoints(d);
    const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
    const box = [Math.min(...xs), Math.min(...ys), Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)];
    if (box[2] < 30 && box[3] < 30) canvas.frame([box[0] - 15, box[1] - 10, box[2] + 30, box[3] + 20]);
  }
}

async function saveDraft() {
  const d = state.draft;
  if (!d.cs) { toast('Choose a condition state.', 'warn'); return; }
  if (!(d.quantity > 0)) { toast('Enter the quantity.', 'warn'); return; }
  if (d.cs_suggested && d.cs !== d.cs_suggested && !d.cs_reason.trim()) { toast('Give a reason for changing the suggested condition state.', 'warn'); $('csReason')?.focus(); return; }
  const record = { ...d, updated_at: store.now(), structural_review: d.cs === 4 || d.structural_review };
  for (const k of ['isNew', 'newPhotos', 'removedPhotos', 'photos', 'auto', 'cs_chosen', 'part_auto']) delete record[k];
  await store.put('defects', record);
  if (d.newPhotos.length) await store.put('photos', d.newPhotos.map(p => ({ ...p, defect_id: record.id })));
  for (const p of d.removedPhotos) await store.put('photos', { ...p, deleted: true, updated_at: store.now() });
  toast(`D${record.number} saved${record.cs === 4 ? ' · CS 4: report it as a critical finding per agency procedure' : ''}.`, record.cs === 4 ? 'warn' : 'ok');
  state.draft = null; state.selected = record.id; state.panel = 'list'; state.pick = null;
  await loadDefects();
  updateStatus();
}

async function deleteDraft() {
  const d = state.draft;
  if (!confirm(`Delete defect D${d.number}? It stays in the cloud history as deleted.`)) return;
  const record = { ...state.defects.find(x => x.id === d.id), deleted: true, updated_at: store.now() };
  await store.put('defects', record);
  state.draft = null; state.selected = null; state.panel = 'list';
  await loadDefects();
  updateStatus();
}

// ---------------------------------------------------------------- panel
function renderPanel() {
  const panel = $('panel');
  document.body.dataset.panel = state.panel;
  panel.replaceChildren();
  if (!state.catalog) return;
  if (state.panel === 'pick') return renderPicker(panel);
  if (state.panel === 'draw') return renderDrawing(panel);
  if (state.panel === 'form' && state.draft) return renderForm(panel);
  if (state.panel === 'summary') return renderSummary(panel);
  renderList(panel);
}

function head(panel, title, sub, actions = []) {
  const h = el('div', 'panel-head');
  const t = el('div'); t.append(el('h2', '', title)); if (sub) t.append(el('p', 'muted small', sub));
  h.append(t, ...actions);
  panel.append(h);
}

function renderList(panel) {
  const scope = state.scope;
  const items = state.defects.filter(d => scope === 'all' || d.sheet_id === state.sheet?.id);
  head(panel, scope === 'all' ? 'All defects' : 'Defects on this sheet', state.inspection ? `${state.inspection.inspection_date} · ${state.inspection.inspection_type}` : 'No inspection yet');
  const actions = el('div', 'panel-actions');
  actions.append(btn('Add defect', startDefect, 'primary wide'));
  const tabs = el('div', 'segmented small');
  for (const [key, label] of [['sheet', 'This sheet'], ['all', `All (${state.defects.length})`]]) {
    const b = btn(label, () => { state.scope = key; renderPanel(); }, scope === key ? 'active' : '');
    b.setAttribute('aria-pressed', String(scope === key));
    tabs.append(b);
  }
  actions.append(tabs);
  panel.append(actions);
  const list = el('div', 'defect-list');
  if (!items.length) {
    list.append(el('p', 'empty', state.inspection ? 'No defects recorded here yet. Choose Add defect, pick what you found, then draw it on the sheet.' : 'Start an inspection to record defects.'));
  }
  for (const d of items) {
    const card = btn('', () => selectDefect(d.id, true), 'defect-card' + (d.id === state.selected ? ' selected' : ''));
    const tag = el('span', 'cs-tag', `D${d.number}`); tag.style.setProperty('--cs', CS_COLORS[d.cs]);
    const body = el('span', 'card-body');
    body.append(el('span', 'card-title', `${d.defect_code} ${DEFECTS[d.defect_code]?.short || ''}`),
      el('span', 'card-meta', `${part(d.part).label} · CS ${d.cs} · ${fmt(d.quantity, 0)} ${d.unit}${state.photoCounts[d.id] ? ` · ${state.photoCounts[d.id]} photo${state.photoCounts[d.id] > 1 ? 's' : ''}` : ''}`));
    if (scope === 'all') body.append(el('span', 'card-meta', `Sheet ${d.sheet_id} · ${d.location || ''}`));
    card.append(tag, body);
    list.append(card);
  }
  panel.append(list);
}

function renderPicker(panel) {
  head(panel, 'What did you find?', 'Pick the defect, then draw it on the sheet. The element is found from where you draw.',
    [btn('Cancel', cancelDraft, 'text-button')]);
  const wrap = el('div', 'picker');
  for (const material of MATERIAL_ORDER) {
    const group = PICKS.filter(p => p.material === material);
    if (!group.length) continue;
    wrap.append(el('h3', 'picker-group', material));
    const grid = el('div', 'picker-grid');
    for (const p of group) {
      const b = btn('', () => choosePick(p), 'pick');
      b.append(el('span', 'pick-icon ' + p.kind), el('span', 'pick-name', p.name), el('span', 'pick-code', p.note));
      grid.append(b);
    }
    wrap.append(grid);
  }
  panel.append(wrap);
}

function renderDrawing(panel) {
  head(panel, state.pick.name, `${state.pick.kind === 'line' ? 'Trace it' : state.pick.kind === 'area' ? 'Outline it' : 'Tap it'} on the sheet.`, [btn('Cancel', cancelDraft, 'text-button')]);
  const tips = el('ul', 'tips');
  for (const t of ['Pen, mouse or one finger draws. Two fingers move and zoom.', 'After you use a pen, fingers only move the sheet (palm rejection).',
    'Draw on a shaded surface. Grey outlines are context only.', 'Zoom in for small defects: the drawing keeps its full precision.']) tips.append(el('li', '', t));
  panel.append(tips);
}

function field(label, control, extra) {
  const f = el('label', 'field');
  f.append(el('span', 'field-label', label), control);
  if (extra) f.append(extra);
  return f;
}

function renderForm(panel) {
  const d = state.draft;
  const p = part(d.part), e = element(p.element);
  const sheet = sheetById(d.sheet_id), view = viewById(sheet, d.view_id);
  head(panel, `${d.isNew ? 'New defect' : 'Defect'} D${d.number}`, `${sheet.id} · ${view.label}`,
    [btn('Close', d.isNew ? cancelDraft : () => { state.draft = null; state.panel = 'list'; drawDefects(); renderPanel(); }, 'text-button')]);
  const form = el('form', 'defect-form');
  form.onsubmit = ev => { ev.preventDefault(); saveDraft(); };

  // Element (found from the sketch) and defect.
  const partSel = el('select');
  for (const id of view.parts) { const o = el('option', '', `${part(id).label} · ${part(id).element}`); o.value = id; partSel.append(o); }
  partSel.value = d.part;
  partSel.onchange = () => { d.part = partSel.value; d.part_auto = false; d.defect_code = fitDefect(d.defect_code, part(d.part).element); recompute(d); renderPanel(); };
  const elemNote = el('span', 'field-note', `${e?.code} ${e?.name}${d.part_auto ? ' · found from the sketch' : ''}`);
  form.append(field('Element', partSel, elemNote));

  const allowed = ELEMENT_DEFECTS[p.element] || Object.keys(DEFECTS).map(Number);
  const defSel = el('select');
  for (const code of allowed) { const o = el('option', '', `${code} ${DEFECTS[code].name}`); o.value = code; defSel.append(o); }
  if (!allowed.includes(Number(d.defect_code))) { const o = el('option', '', `${d.defect_code} ${DEFECTS[d.defect_code]?.name} (not listed for this element)`); o.value = d.defect_code; defSel.append(o); }
  defSel.value = d.defect_code;
  defSel.onchange = () => { d.defect_code = Number(defSel.value); d.measurements = {}; d.cs_chosen = false; recompute(d); renderPanel(); };
  form.append(field('Defect', defSel));

  // Measurements.
  const fields = (FIELDS[d.defect_code] || []).filter(f => !f.when || f.when(d.measurements));
  if (fields.length) {
    const box = el('fieldset', 'measure');
    box.append(el('legend', '', 'Measurements'));
    for (const f of fields) box.append(measureControl(d, f));
    form.append(box);
  }

  // Quantity.
  const qty = el('input'); qty.type = 'number'; qty.min = '0'; qty.step = '1'; qty.value = d.quantity ?? ''; qty.inputMode = 'decimal';
  qty.oninput = () => { d.quantity = Number(qty.value); d.quantity_manual = true; qtyNote.textContent = 'Entered by the inspector'; };
  const qtyRow = el('div', 'input-unit'); qtyRow.append(qty, el('span', 'unit', d.unit || ''));
  const qtyNote = el('span', 'field-note', d.quantity_manual ? 'Entered by the inspector' : d.quantity_basis);
  if (d.quantity_manual) qtyNote.append(' · ', btn('Use sketch', () => { d.quantity_manual = false; recompute(d); renderPanel(); }, 'text-button'));
  form.append(field(`Quantity (element total ${fmt(e?.total || 0, 0)} ${e?.unit || ''})`, qtyRow, qtyNote));

  // Condition state.
  const cs = el('fieldset', 'cs-field');
  cs.append(el('legend', '', 'Condition state'));
  const chips = el('div', 'cs-chips');
  for (const n of [1, 2, 3, 4]) {
    const b = btn('', () => { d.cs = n; d.cs_chosen = true; if (n === 4) d.structural_review = true; renderPanel(); }, 'cs-chip' + (d.cs === n ? ' active' : ''));
    b.style.setProperty('--cs', CS_COLORS[n]);
    b.setAttribute('aria-pressed', String(d.cs === n));
    b.append(el('b', '', `CS ${n}`), el('span', '', CS_NAMES[n]));
    if (d.cs_suggested === n) b.append(el('i', 'suggested', 'Suggested'));
    chips.append(b);
  }
  cs.append(chips);
  const desc = DEFECTS[d.defect_code]?.cs[(d.cs || d.cs_suggested || 1) - 1];
  cs.append(el('p', 'cs-desc', d.cs ? desc : (d.cs_suggested ? '' : 'Enter the measurements for a suggestion, or choose the condition state.')));
  if (d.cs_suggested && d.cs && d.cs !== d.cs_suggested) {
    const reason = el('textarea'); reason.id = 'csReason'; reason.rows = 2; reason.value = d.cs_reason; reason.placeholder = 'Why the condition state differs from the measured suggestion';
    reason.oninput = () => { d.cs_reason = reason.value; };
    cs.append(field('Reason for the change', reason));
  }
  if (d.cs === 4) cs.append(el('p', 'critical', 'CS 4 warrants a structural review. Report it as a critical finding following agency procedure.'));
  form.append(cs);

  form.append(field('Location', el('output', 'location', d.location)));
  const notes = el('textarea'); notes.rows = 3; notes.value = d.notes; notes.placeholder = 'What you saw, and anything the next inspector should check';
  notes.oninput = () => { d.notes = notes.value; };
  form.append(field('Notes', notes));

  // Photos.
  const photos = el('fieldset', 'photos');
  photos.append(el('legend', '', 'Photos'));
  const grid = el('div', 'photo-grid');
  for (const ph of [...(d.photos || []).filter(x => !d.removedPhotos.includes(x)), ...d.newPhotos]) grid.append(photoTile(d, ph));
  photos.append(grid);
  const take = el('label', 'button photo-add');
  const camera = el('input'); camera.type = 'file'; camera.accept = 'image/*'; camera.capture = 'environment'; camera.hidden = true;
  take.append('Take photo', camera);
  const pick = el('label', 'button photo-add');
  const files = el('input'); files.type = 'file'; files.accept = 'image/*'; files.multiple = true; files.hidden = true;
  pick.append('Add from files', files);
  const addFiles = async list => {
    for (const f of list) {
      try { d.newPhotos.push(await preparePhoto(f, { defect: d.id, inspection: d.inspection_id, sheet: d.sheet_id, code: d.defect_code, number: d.number })); }
      catch { toast(`Could not read ${f.name}.`, 'warn'); }
    }
    renderPanel();
  };
  camera.onchange = () => addFiles([...camera.files]);
  files.onchange = () => addFiles([...files.files]);
  const row = el('div', 'photo-actions'); row.append(take, pick);
  photos.append(row);
  form.append(photos);

  const actions = el('div', 'form-actions');
  const save = el('button', 'primary', d.isNew ? 'Save defect' : 'Save changes'); save.type = 'submit';
  actions.append(save);
  if (!d.isNew) actions.append(btn('Delete', deleteDraft, 'danger'));
  actions.append(btn('Show in 3D', () => openIn3D(d), 'text-button'));
  form.append(actions);
  panel.append(form);
}

function measureControl(d, f) {
  const m = d.measurements;
  const changed = () => { d.cs_chosen = false; recompute(d); renderPanel(); };
  if (f.type === 'choice') {
    const seg = el('div', 'segmented choice');
    for (const [value, label] of f.options) {
      const b = btn(label, () => { m[f.key] = value; changed(); }, m[f.key] === value ? 'active' : '');
      b.setAttribute('aria-pressed', String(m[f.key] === value));
      seg.append(b);
    }
    return field(f.label, seg);
  }
  if (f.type === 'check') {
    const c = el('input'); c.type = 'checkbox'; c.checked = !!m[f.key];
    c.onchange = () => { m[f.key] = c.checked; changed(); };
    const l = el('label', 'check'); l.append(c, f.label);
    return l;
  }
  const input = el('input'); input.type = 'number'; input.step = f.step; input.min = '0'; input.inputMode = 'decimal';
  if (m[f.key] === undefined && f.auto && d.auto?.[f.auto]) m[f.key] = d.auto[f.auto];
  input.value = m[f.key] ?? '';
  input.onchange = () => { m[f.key] = input.value === '' ? null : Number(input.value); changed(); };
  const row = el('div', 'input-unit'); row.append(input, el('span', 'unit', f.unit));
  const extra = el('span', 'field-note');
  if (f.presets) for (const v of f.presets) extra.append(btn(`${v}`, () => { m[f.key] = v; changed(); }, 'preset'));
  if (f.auto) extra.append(' From the sketch; measure and correct it.');
  return field(`${f.label}`, row, extra);
}

function photoTile(d, ph) {
  const tile = el('figure', 'photo');
  const img = el('img'); img.alt = ph.file_name; img.loading = 'lazy';
  const url = photoURL(ph);
  if (url) img.src = url;
  else state.cloud.photoBlob(ph).then(b => { if (b) img.src = photoURL({ ...ph, blob: b }); });
  const cap = el('figcaption', '', ph.file_name.split('_').slice(0, 2).join(' '));
  const remove = btn('×', () => {
    if (d.newPhotos.includes(ph)) d.newPhotos = d.newPhotos.filter(x => x !== ph);
    else d.removedPhotos.push(ph);
    renderPanel();
  }, 'photo-remove');
  remove.setAttribute('aria-label', 'Remove photo');
  tile.append(img, cap, remove);
  img.onclick = () => { if (img.src) window.open(img.src, '_blank'); };
  return tile;
}

function openIn3D(d) {
  try { localStorage.setItem('inspection-focus', JSON.stringify({ bridge: state.bridge, defect: d.id, at: Date.now() })); } catch {}
  window.open(`./#bridge/${state.bridge}`, 'bridge3d');
}

// ---------------------------------------------------------------- element summary (AASHTO element CS table)
function renderSummary(panel) {
  head(panel, 'Element condition states', 'AASHTO element quantities by condition state for this inspection', [btn('Back', () => { state.panel = 'list'; renderPanel(); }, 'text-button')]);
  const rows = elementSummary(state.catalog.elements, state.defects);
  const table = el('table', 'summary');
  table.innerHTML = '<thead><tr><th>Element</th><th>Total</th><th>CS1</th><th>CS2</th><th>CS3</th><th>CS4</th></tr></thead>';
  const body = el('tbody');
  for (const r of rows) {
    const tr = el('tr', 'element-row');
    const name = el('td'); name.append(el('b', '', String(r.code)), ` ${r.name}`, el('small', '', ` ${r.unit}`));
    tr.append(name, el('td', 'num', fmt(r.total, 0)), ...r.cs.map((q, i) => { const td = el('td', 'num' + (q && i ? ' hot' : ''), fmt(q, 0)); if (q && i) td.style.setProperty('--cs', CS_COLORS[i + 1]); return td; }));
    body.append(tr);
    for (const def of r.defects) {
      const sub = el('tr', 'defect-row');
      sub.append(el('td', '', `${def.code} ${DEFECTS[def.code]?.short || ''}`), el('td'), ...def.cs.map((q, i) => el('td', 'num', i && q ? fmt(q, 0) : '')));
      body.append(sub);
    }
    if (r.over) { const w = el('tr', 'warn-row'); const td = el('td', '', 'Defect quantities exceed the element total: check for double counting.'); td.colSpan = 6; w.append(td); body.append(w); }
  }
  table.append(body);
  const wrap = el('div', 'table-wrap'); wrap.append(table);
  panel.append(wrap);
  const actions = el('div', 'form-actions');
  actions.append(btn('Download CSV', () => downloadCSV(rows)), btn('Download backup', exportBackup));
  panel.append(actions);
  panel.append(el('p', 'muted small pad', 'CS 1 is the element total less the defect quantities in CS 2 to 4. Where defects overlap, record the worst condition only once.'));
}

function download(name, blob) {
  const a = el('a'); a.href = URL.createObjectURL(blob); a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}

function csv(rows) { return rows.map(r => r.map(v => { const s = String(v ?? ''); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; }).join(',')).join('\r\n'); }

function downloadCSV(rows) {
  const i = state.inspection;
  const out = [['Bridge', state.catalog.structure_id, state.catalog.title], ['Inspection', i.inspection_date, i.inspection_type, i.inspectors], [],
    ['Element', 'Name', 'Unit', 'Total', 'CS1', 'CS2', 'CS3', 'CS4']];
  for (const r of rows) {
    out.push([r.code, r.name, r.unit, r.total, ...r.cs.map(q => Math.round(q))]);
    for (const d of r.defects) out.push([`${r.code}/${d.code}`, DEFECTS[d.code]?.name, r.unit, '', ...d.cs.map((q, k) => k ? Math.round(q) : '')]);
  }
  out.push([], ['Defect', 'Sheet', 'View', 'Member', 'Element', 'Defect code', 'Defect', 'CS', 'Quantity', 'Unit', 'Location', 'Measurements', 'Notes', 'CS basis', 'CS change reason']);
  for (const d of state.defects) out.push([`D${d.number}`, d.sheet_id, d.view_id, part(d.part).label, d.element_code, d.defect_code, DEFECTS[d.defect_code]?.name, d.cs,
    d.quantity, d.unit, d.location, JSON.stringify(d.measurements), d.notes, d.cs_basis, d.cs_reason]);
  download(`${state.bridge}_${i.inspection_date}_elements.csv`, new Blob(['﻿' + csv(out)], { type: 'text/csv' }));
}

async function exportBackup() {
  const i = state.inspection;
  const photos = await store.inspectionPhotos(i.id);
  const data = await Promise.all(photos.map(async p => {
    const { blob, ...meta } = p;
    if (!blob) return meta;
    const b64 = await new Promise(r => { const f = new FileReader(); f.onload = () => r(f.result); f.readAsDataURL(blob); });
    return { ...meta, data_url: b64 };
  }));
  const all = await store.all('defects', 'inspection_id', i.id);
  const backup = { format: 'bridge-inspection-backup', version: 1, exported_at: store.now(), bridge: state.bridge, sheets_sha256: state.catalog.source.sha256, inspection: i, defects: all, photos: data };
  download(`${state.bridge}_${i.inspection_date}_inspection_backup.json`, new Blob([JSON.stringify(backup)], { type: 'application/json' }));
}

async function importBackup(file) {
  const backup = JSON.parse(await file.text());
  if (backup.format !== 'bridge-inspection-backup' || backup.bridge !== state.bridge) throw Error('This file is not an inspection backup for this bridge.');
  await store.put('inspections', backup.inspection);
  await store.put('defects', backup.defects);
  const photos = await Promise.all(backup.photos.map(async p => {
    const { data_url, ...meta } = p;
    return data_url ? { ...meta, blob: await (await fetch(data_url)).blob(), uploaded: false } : meta;
  }));
  if (photos.length) await store.put('photos', photos);
  await loadInspections(backup.inspection.id);
  toast(`Imported ${backup.defects.length} defects and ${photos.length} photos.`, 'ok');
}

// ---------------------------------------------------------------- dialogs
function dialog(title, build, { required = false } = {}) {
  const dlg = $('dialog');
  dlg.replaceChildren();
  const form = el('form', 'dialog-body'); form.method = 'dialog';
  form.append(el('h2', '', title));
  build(form, dlg);
  dlg.append(form);
  dlg.oncancel = e => { if (required) e.preventDefault(); };
  dlg.showModal();
  return dlg;
}

function newInspectionDialog(first = false) {
  dialog(first ? 'Start an inspection' : 'New inspection', (form, dlg) => {
    if (first) form.append(el('p', 'muted', 'Defects are recorded against an inspection. Everything is saved on this device first.'));
    const date = el('input'); date.type = 'date'; date.value = today(); date.required = true;
    const type = el('select'); for (const t of INSPECTION_TYPES) type.append(new Option(t, t));
    const who = el('input'); who.type = 'text'; who.placeholder = 'Team leader and inspectors'; who.autocomplete = 'name';
    const notes = el('textarea'); notes.rows = 2; notes.placeholder = 'Weather, access, equipment';
    form.append(field('Date', date), field('Type', type), field('Inspectors', who), field('Notes', notes));
    const actions = el('div', 'form-actions');
    const ok = el('button', 'primary', 'Start inspection'); ok.type = 'submit';
    actions.append(ok);
    if (state.inspection) actions.append(btn('Cancel', () => dlg.close()));
    form.append(actions);
    form.onsubmit = async e => {
      e.preventDefault();
      const rec = { id: store.uuid(), bridge_id: state.bridge, inspection_date: date.value, inspection_type: type.value,
        inspectors: who.value.trim(), notes: notes.value.trim(), status: 'open', created_at: store.now(), updated_at: store.now(), deleted: false };
      await store.put('inspections', rec);
      await store.setting(`inspection:${state.bridge}`, rec.id);
      dlg.close();
      await loadInspections(rec.id);
      updateStatus();
    };
  }, { required: first });
}

function settingsDialog() {
  dialog('Settings', async (form, dlg) => {
    form.append(el('h3', '', 'Cloud sync (Supabase)'));
    form.append(el('p', 'muted small', 'Use the project URL and the publishable (anon) key from Supabase Project Settings → API. Never enter the service_role key here.'));
    const cfg = state.cloud.config || {};
    const url = el('input'); url.type = 'url'; url.placeholder = 'https://<project>.supabase.co'; url.value = cfg.url || '';
    const key = el('input'); key.type = 'text'; key.placeholder = 'Publishable or anon key'; key.value = cfg.key || ''; key.spellcheck = false;
    form.append(field('Project URL', url), field('Publishable key', key));
    const user = state.cloud.ready ? await state.cloud.user() : null;
    const authBox = el('div', 'auth');
    if (user) {
      authBox.append(el('p', '', `Signed in as ${user.email}`), btn('Sign out', async () => { await state.cloud.signOut(); dlg.close(); updateStatus(); }));
    } else {
      const email = el('input'); email.type = 'email'; email.placeholder = 'Email'; email.autocomplete = 'username';
      const pass = el('input'); pass.type = 'password'; pass.placeholder = 'Password'; pass.autocomplete = 'current-password';
      authBox.append(field('Email', email), field('Password', pass), btn('Sign in', async () => {
        try {
          await saveCloud(url.value, key.value);
          await state.cloud.signIn(email.value, pass.value);
          toast('Signed in. Syncing…', 'ok'); dlg.close(); updateStatus(); sync();
        } catch (e) { toast(e.message || 'Sign-in failed.', 'warn'); }
      }, 'primary'));
    }
    form.append(authBox);
    form.append(el('h3', '', 'Drawing'));
    const pen = el('input'); pen.type = 'checkbox'; pen.checked = state.penOnly;
    pen.onchange = async () => { state.penOnly = pen.checked; canvas.penSeen = pen.checked; await store.setting('pen_only', pen.checked); };
    const l = el('label', 'check'); l.append(pen, 'Pen only: fingers never draw (set automatically after the first pen stroke)');
    form.append(l);
    form.append(el('h3', '', 'Backup'));
    const file = el('input'); file.type = 'file'; file.accept = 'application/json'; file.hidden = true;
    file.onchange = async () => { try { await importBackup(file.files[0]); dlg.close(); } catch (e) { toast(e.message, 'warn'); } };
    const imp = el('label', 'button'); imp.append('Import backup', file);
    const row = el('div', 'form-actions');
    row.append(btn('Download backup', exportBackup), imp);
    form.append(row);
    const actions = el('div', 'form-actions end');
    actions.append(btn('Save cloud settings', async () => { await saveCloud(url.value, key.value); dlg.close(); updateStatus(); }), btn('Close', () => dlg.close()));
    form.append(actions);
  });
}

function isSecretKey(key) {
  if (key.startsWith('sb_secret_')) return true;
  try { return JSON.parse(atob(key.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))).role === 'service_role'; } catch { return false; }
}

async function saveCloud(url, key) {
  const config = url.trim() && key.trim() ? { url: url.trim(), key: key.trim() } : null;
  if (config && !/^https:\/\/[^/]+$/.test(config.url.replace(/\/+$/, ''))) throw Error('The project URL should look like https://<project>.supabase.co');
  if (config && isSecretKey(config.key)) throw Error('That is a secret (service_role) key. Use the publishable (anon) key.');
  await store.setting('cloud', config);
  state.cloud.configure(config);
}

// ---------------------------------------------------------------- status and sync
async function updateStatus() {
  const pending = (await store.outbox()).length;
  const user = state.cloud.ready ? await state.cloud.user() : null;
  const pill = $('syncStatus');
  let text, cls;
  if (!state.cloud.ready) { text = pending ? `Saved on this device · ${pending} not backed up` : 'Saved on this device'; cls = 'local'; }
  else if (!user) { text = 'Sign in to sync'; cls = 'warn'; }
  else if (!navigator.onLine) { text = `Offline · ${pending} to sync`; cls = 'warn'; }
  else if (pending) { text = `${pending} to sync`; cls = 'warn'; }
  else { const last = await store.setting('last_sync'); text = last ? `Synced ${new Date(last).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : 'Ready to sync'; cls = 'ok'; }
  pill.textContent = state.syncing ? 'Syncing…' : text;
  pill.className = 'status-pill ' + cls;
  $('syncButton').hidden = !(state.cloud.ready && user);
}

async function sync() {
  if (state.syncing) return;
  state.syncing = true; updateStatus();
  try {
    const { pushed, pulled } = await state.cloud.sync(state.bridge, msg => { $('syncStatus').textContent = msg; });
    toast(`Synced: sent ${pushed}, received ${pulled}.`, 'ok');
    await loadInspections(state.inspection?.id);
  } catch (e) { toast(e.message || 'Sync failed.', 'warn'); }
  state.syncing = false;
  updateStatus();
}

window.addEventListener('DOMContentLoaded', () => init().catch(e => { console.error(e); toast(e.message || String(e), 'warn'); }));
window.__inspect = { state, store, elementSummary };
