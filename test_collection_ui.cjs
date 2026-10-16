/* Focused presentation regressions; no HTTP server, browser, or FEM runtime needed. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {test} = require('node:test');

class Element {
  constructor(tag) {
    this.tagName = tag;
    this.children = [];
    this.textContent = '';
    this.hidden = false;
    this.disabled = false;
    this.classList = {add() {}};
  }
  append(...items) { this.children.push(...items); }
  prepend(...items) { this.children.unshift(...items); }
  replaceChildren(...items) { this.children = items; }
  setAttribute(name, value) { this[name] = value; }
}

function descendants(element) {
  return [element, ...element.children.flatMap(descendants)];
}
function text(element) {
  return descendants(element).map(n => n.textContent).filter(Boolean).join(' | ');
}
function ledger(prefix, support) {
  return {
    analyzed_component_ids: ['arch_0'],
    analytical_family: 'arch',
    display_scope: prefix + ' barrel scope',
    modeled_state: prefix + ' model state',
    foundation_labels: {fixed: prefix + ' clamped springings', elastic: prefix + ' elastic springings'},
    values: {arches: [{u0_m: support}, {u0_m: support + 5}]},
    sources: {drawing: {title: prefix + ' drawing', url: '/' + prefix + '.pdf'}},
    evidence: [{fields: ['arches.u0_m'], status: 'assumed', source: 'drawing',
      note: prefix + ' geometry evidence', pdf_pages: [7]}],
    assumptions: [prefix + ' exclusions'],
  };
}

function harness(currentInputs = false) {
  const host = new Element('div'), legend = new Element('div');
  legend.id = 'femLegend';
  legend.hidden = true;
  const document = {
    createElement: tag => new Element(tag),
    getElementById: id => [host, legend].flatMap(descendants).find(n => n.id === id),
  };
  const context = {window: {}, document};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(path.join(__dirname, 'web/analysis.js'), 'utf8'), context);
  const panel = context.window.bridgeAnalysis;
  const saved = ledger('SAVED', -12.5), current = ledger('CURRENT', -99);
  current.analyzed_component_ids.push('arch_1');
  const settings = {case: 'demo_uniform', pressure_kPa: 1, concrete_E_GPa: 30,
    steel_E_GPa: 200, bearing_kz_MNpm: 800, load_factor: 1, foundation: 'fixed'};
  panel.host = host;
  panel.selected = [];
  panel.options = {...settings};
  panel.info = {available: true, demonstration: true, ledger: current, runs: [],
    cases: {demo_uniform: 'Pressure increment'}, defaults: {...settings},
    parameters: {concrete_E_GPa: {label: 'Concrete E (GPa)', min: 10, max: 50, step: 1}}};
  panel.run = {id: '1'.repeat(32), status: 'completed', current_inputs: currentInputs,
    input_hash: 'frozen-hash', settings: {...settings}};
  panel.result = {
    bridge_id: 'sr1-wabash', demonstration: true, case: 'demo_uniform', case_title: 'Saved pressure increment',
    settings: {...settings}, snapshot: {ledger: saved},
    max_stress_MPa: 1, max_deflection_mm: 2, total_load_kN: 3, total_reaction_kN: 3,
    node_count: 4, element_count: 1, equilibrium: [{force_error: 0, moment_error: 0}],
    solver: {name: 'OpenSees', version: 'test', python: 'test'},
    verification: {benchmarks: [], mesh_refinement: [], mesh_warnings: []},
    family_summary: {arch: {member_count: 1, max_stress_MPa: 1}},
    members: [{component_id: 'sr1-wabash:arch_0', family: 'arch', span: 'A',
      peak: {stress_MPa: 1, x_m: 0}}],
    mesh: {nodes: [{id: 1, xyz_m: [0, 0, 0]}]},
    displacement_note: 'Saved incremental response',
  };
  // Model the viewer's public state transitions, without implementing its renderer.
  const view = {rootVisible: true, mesh: null, colors: null, fits: [], clearCount: 0};
  panel.viewer = {
    showAnalysisMesh(mesh) { view.mesh = mesh; view.rootVisible = !mesh; },
    clearAnalysis() { view.mesh = null; view.rootVisible = true; view.colors = null; view.clearCount++; },
    setAnalysis(result) { view.mesh = null; view.rootVisible = true; view.colors = result; },
    fit(ids) { view.fits.push(ids); },
  };
  panel.onSelect = () => {};
  return {panel, host, legend, view, saved, current, byId: id => document.getElementById(id)};
}

test('archived results show frozen geometry, evidence links, scope, and support labels', () => {
  const h = harness(false);
  h.panel.render();
  const visible = text(h.host);
  assert.match(visible, /1 mapped components · SAVED barrel scope/);
  assert.match(visible, /SAVED model state/);
  assert.match(visible, /Displayed run: frozen inputs and evidence/);
  assert.match(visible, /arches\.u0_m: \[-12\.5,-7\.5\]/);
  assert.match(visible, /SAVED geometry evidence/);
  assert.match(visible, /SAVED exclusions/);
  assert.doesNotMatch(visible, /CURRENT (barrel scope|model state|geometry evidence|exclusions)/);
  const resultCase = descendants(h.host).find(n => n.className === 'fem-result-case');
  assert.match(text(resultCase), /SAVED clamped springings/);
  const pageLink = descendants(h.host).find(n => n.tagName === 'a' && n.textContent === 'PDF p. 7');
  assert.equal(pageLink.href, '/SAVED.pdf#page=7');
  assert.equal(h.byId('femToggle').disabled, true);
  assert.equal(h.byId('femScale').disabled, true);
});

test('returning from an archived FE mesh restores the model without applying stale fields', () => {
  const h = harness(false);
  h.panel.render();
  h.byId('femMesh').onclick();
  assert.equal(h.view.mesh, h.panel.result.mesh);
  assert.equal(h.view.rootVisible, false);
  assert.equal(h.legend.hidden, false);
  h.byId('femMeshBack').onclick();
  assert.equal(h.view.rootVisible, true);
  assert.equal(h.view.mesh, null);
  assert.equal(h.view.colors, null);
  assert.equal(h.panel.applied, false);
  assert.equal(h.legend.hidden, true, 'The FE mesh legend must disappear when the GLB returns.');
  assert.equal(h.view.fits.length, 1);
  assert.equal(h.view.fits[0], undefined, 'An archived result must not constrain fitting to obsolete IDs.');
});

test('returning from a current FE mesh restores current result fields', () => {
  const h = harness(true);
  h.panel.render();
  h.byId('femMesh').onclick();
  h.byId('femMeshBack').onclick();
  assert.equal(h.view.rootVisible, true);
  assert.equal(h.view.mesh, null);
  assert.equal(h.view.colors, h.panel.result);
  assert.equal(h.panel.applied, true);
  assert.equal(h.legend.hidden, false);
  assert.doesNotMatch(text(h.legend), /Actual FE mesh/);
  assert.equal(Array.from(h.view.fits[0]).join(','), 'sr1-wabash:arch_0');
});

test('without a displayed result, the evidence describes the current model', () => {
  const h = harness();
  h.panel.result = null;
  h.panel.run = null;
  h.panel.render();
  const visible = text(h.host);
  assert.match(visible, /2 mapped components · CURRENT barrel scope/);
  assert.match(visible, /arches\.u0_m: \[-99,-94\]/);
  assert.match(visible, /CURRENT exclusions/);
  assert.doesNotMatch(visible, /SAVED/);
});
