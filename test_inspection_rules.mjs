// Inspection app rules without a browser: condition-state suggestions against the MBEI thresholds, sheet
// geometry, AASHTO quantities, the element table, and the published Beechwood sheet set.
//   node --test test_inspection_rules.mjs
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { DEFECTS, ELEMENT_DEFECTS, FIELDS, suggestCS } from './inspect/catalog.js';
import { FT, assignView, currentView, elementFor, extentAlongM, inRings, partAt, planePoint, quantityFor, remapToView, simplify, toCanvas, toView } from './inspect/geometry.js';
import { elementSummary } from './inspect/summary.js';

const cs = (code, m) => suggestCS(code, m)?.cs ?? null;

test('RC cracking 1130: width and spacing thresholds, worst governs', () => {
  assert.equal(cs(1130, { width_in: 0.008 }), 1);
  assert.equal(cs(1130, { width_in: 0.012 }), 2);
  assert.equal(cs(1130, { width_in: 0.05 }), 2);
  assert.equal(cs(1130, { width_in: 0.051 }), 3);
  assert.equal(cs(1130, { spacing_ft: 3.5 }), 1);
  assert.equal(cs(1130, { spacing_ft: 1 }), 2);
  assert.equal(cs(1130, { spacing_ft: 0.8 }), 3);
  assert.equal(cs(1130, { width_in: 0.006, spacing_ft: 2 }), 2);
  assert.equal(cs(1130, {}), null);
});

test('PSC cracking 1110 uses the tighter widths', () => {
  assert.equal(cs(1110, { width_in: 0.0039 }), 1);
  assert.equal(cs(1110, { width_in: 0.004 }), 2);
  assert.equal(cs(1110, { width_in: 0.009 }), 2);
  assert.equal(cs(1110, { width_in: 0.0091 }), 3);
});

test('1080 spalls: more than 1 in deep or 6 in across is CS 3', () => {
  assert.equal(cs(1080, { form: 'delamination' }), 2);
  assert.equal(cs(1080, { form: 'patch_sound' }), 2);
  assert.equal(cs(1080, { form: 'patch_unsound' }), 3);
  assert.equal(cs(1080, { form: 'spall', depth_in: 1, diameter_in: 6 }), 2);
  assert.equal(cs(1080, { form: 'spall', depth_in: 1.01, diameter_in: 4 }), 3);
  assert.equal(cs(1080, { form: 'spall', depth_in: 0.5, diameter_in: 6.5 }), 3);
  assert.equal(cs(1080, { form: 'spall' }), null);
});

test('bearings and judgement-only defects; CS 4 is never suggested', () => {
  assert.equal(cs(2230, { bulging_pct: 14 }), 2);
  assert.equal(cs(2230, { bulging_pct: 15 }), 3);
  assert.equal(cs(2230, { bulging_pct: 2, split: true }), 3);
  assert.equal(cs(2240, { loss_pct: 9.9 }), 2);
  assert.equal(cs(2240, { loss_pct: 10 }), 3);
  assert.equal(cs(1090, { section_loss: 'measurable' }), 3);
  assert.equal(cs(1120, { severity: 'white' }), 2);
  for (const code of [4000, 6000, 7000]) assert.equal(cs(code, {}), null);
  for (const code of Object.keys(DEFECTS)) {
    assert.equal(DEFECTS[code].cs.length, 4, code);
    assert.ok(FIELDS[code], `${code} has a measurement list`);
    for (const m of [{ width_in: 9 }, { spacing_ft: 0 }, { form: 'spall', depth_in: 9 }, { bulging_pct: 99, split: true }, { loss_pct: 99 }])
      assert.notEqual(cs(code, m), 4, code);
  }
  for (const list of Object.values(ELEMENT_DEFECTS)) for (const code of list) assert.ok(DEFECTS[code], code);
});

const square = [[0, 0], [1, 0], [1, 1], [0, 1]];
const view = { id: 'V', placement: [0.1, 0.2, 0.5, 0.25], extent_m: [20, 4], origin: [10, 5, -2], u: [1, 0, 0], v: [0, -1, 0], normal: [0, 0, 1],
  parts: ['beam', 'slab'], regions: [{ part: 'beam', polygons: [[[[0, 0.5], [1, 0.5], [1, 1], [0, 1]]]] }, { part: 'slab', polygons: [[square, [[0.4, 0.6], [0.6, 0.6], [0.6, 0.9], [0.4, 0.9]]]] }] };

test('canvas and view coordinates, and the published 3D mapping', () => {
  const canvas = [420, 297];
  const p = toCanvas([0.25, 0.5], view, canvas);
  assert.deepEqual(p.map(c => +c.toFixed(6)), [94.5, 96.525]);
  assert.deepEqual(toView(p, view, canvas).map(c => +c.toFixed(9)), [0.25, 0.5]);
  // P = origin + u * extent0 * U + v * extent1 * V
  assert.deepEqual(planePoint([0.25, 0.5], view), [15, 3, -2]);
  assert.equal(assignView([p, p, [0, 0]], { views: [view] }, canvas).share, 2 / 3);
});

test('regions: holes, priority order and the element under a sketch', () => {
  assert.equal(inRings([0.5, 0.75], view.regions[1].polygons[0]), false, 'inside the hole');
  assert.equal(partAt([0.5, 0.75], view), 'beam', 'first region wins');
  assert.equal(partAt([0.5, 0.2], view), 'slab');
  assert.equal(elementFor([[0.1, 0.2], [0.9, 0.3]], view, 'line').part, 'slab');
  const area = elementFor([[0.1, 0.55], [0.9, 0.55], [0.9, 0.95], [0.1, 0.95]], view, 'area');
  assert.equal(area.part, 'beam');
  assert.ok(area.share > 0.9);
});

test('AASHTO quantities: length along the member, outlined area, 1 ft band, each', () => {
  const path = [[0.1, 0.5], [0.4, 0.6]];        // 6 m along U, 0.4 m across
  assert.ok(Math.abs(extentAlongM(path, view, [1, 0, 0]) - 6) < 1e-9);
  assert.deepEqual(quantityFor({ kind: 'line', path, view, unit: 'ft', axis: [1, 0, 0] }).quantity, Math.round(6 / FT));
  const rect = [[0, 0], [0.05, 0], [0.05, 0.25], [0, 0.25]];   // 1 m x 1 m
  assert.equal(quantityFor({ kind: 'area', path: rect, view, unit: 'sq ft' }).quantity, Math.round(1 / FT / FT));
  assert.equal(quantityFor({ kind: 'line', path: [[0, 0], [0.1, 0]], view, unit: 'sq ft' }).quantity, Math.round(2 / FT));
  assert.equal(quantityFor({ kind: 'point', path: [[0.5, 0.5]], view, unit: 'each' }).quantity, 1);
  assert.equal(quantityFor({ kind: 'line', path: [[0, 0], [0.001, 0]], view, unit: 'ft', axis: [1, 0, 0] }).quantity, 1, 'at least 1 ft');
});

test('retired views: defects map onto the replacement view through the world plane', () => {
  // The old view covered 20 m from x = 10; the new one covers 30 m from x = 5 at another depth, same direction.
  const next = { ...view, id: 'V2', extent_m: [30, 4], origin: [5, 5, -3] };
  const catalog = { sheets: [{ id: 'S2', views: [next] }], retired_views: { V: { ...view, sheet_id: 'S1', replaced_by: 'V0' }, V0: { replaced_by: 'V2' } } };
  assert.deepEqual(remapToView([[0.25, 0.5]], view, next), [[0.33333, 0.5]]);
  const d = { id: 'd', sheet_id: 'S1', view_id: 'V', path: [[0, 0], [1, 1]] };
  const found = currentView(d, catalog);
  assert.equal(found.view, next);
  assert.equal(found.remapped, 'V');
  assert.deepEqual([found.defect.sheet_id, found.defect.view_id], ['S2', 'V2']);
  assert.deepEqual(found.defect.path, [[0.16667, 0], [0.83333, 1]]);
  assert.deepEqual(d.path, [[0, 0], [1, 1]], 'the stored record is not changed');
  assert.equal(currentView({ ...d, sheet_id: 'S2', view_id: 'V2' }, catalog).defect.path, d.path, 'current views are left alone');
  assert.equal(currentView({ ...d, view_id: 'gone' }, catalog).view, null);
});

test('stroke simplification keeps the ends and the corners', () => {
  const pts = [[0, 0], [1, 0.001], [2, 0], [2, 1], [2.001, 2]];
  assert.deepEqual(simplify(pts, 0.01), [[0, 0], [2, 0], [2.001, 2]]);
});

test('element table: CS 1 is the remainder; over-allocation is flagged', () => {
  const elements = [{ code: 12, total: 100, unit: 'sq ft' }, { code: 310, total: 2, unit: 'each' }];
  const rows = elementSummary(elements, [
    { element_code: 12, defect_code: 1130, cs: 2, quantity: 10 }, { element_code: 12, defect_code: 1080, cs: 3, quantity: 5 },
    { element_code: 12, defect_code: 1080, cs: 3, quantity: 50, deleted: true },
    { element_code: 310, defect_code: 2230, cs: 4, quantity: 1 }, { element_code: 310, defect_code: 2240, cs: 3, quantity: 2 }]);
  assert.deepEqual(rows[0].cs, [85, 10, 5, 0]);
  assert.equal(rows[0].over, false);
  assert.deepEqual(rows[1].cs, [0, 0, 2, 1]);
  assert.equal(rows[1].over, true);
});

test('Beechwood sheets: every region resolves to its own inspectable part', () => {
  const sheets = JSON.parse(readFileSync(new URL('./data/bridges/beechwood/inspection/sheets.json', import.meta.url)));
  assert.equal(sheets.sheets.length, 13);
  for (const sheet of sheets.sheets) for (const v of sheet.views) for (const region of v.regions) {
    assert.ok(sheets.parts[region.part], region.part);
    assert.ok(ELEMENT_DEFECTS[sheets.parts[region.part].element], `${region.part}: element has a defect list`);
    // A point well inside each polygon's bounding box centre, if inside, must resolve to this part or one listed earlier.
    for (const rings of region.polygons) {
      const xs = rings[0].map(p => p[0]), ys = rings[0].map(p => p[1]);
      const c = [(Math.min(...xs) + Math.max(...xs)) / 2, (Math.min(...ys) + Math.max(...ys)) / 2];
      if (!inRings(c, rings)) continue;
      const found = partAt(c, v);
      assert.ok(v.regions.findIndex(r => r.part === found) <= v.regions.findIndex(r => r.part === region.part), `${v.id}: ${region.part}`);
    }
  }
});

test('Beechwood retired views: each is replaced by a current view looking the same way', () => {
  const sheets = JSON.parse(readFileSync(new URL('./data/bridges/beechwood/inspection/sheets.json', import.meta.url)));
  const current = new Map(sheets.sheets.flatMap(s => s.views.map(v => [v.id, v])));
  const retired = Object.entries(sheets.retired_views || {});
  assert.ok(retired.length, 'the first rebuild retired the old girder, bent and end-bent views');
  for (const [id, old] of retired) {
    assert.ok(!current.has(id), `${id} is both current and retired`);
    const found = currentView({ sheet_id: old.sheet_id, view_id: id, path: [[0.5, 0.5]] }, sheets);
    assert.ok(found.view, `${id}: no replacement`);
    assert.deepEqual(found.view.normal, old.normal, `${id}: replacement looks another way`);
    const [u, v] = found.defect.path[0];
    assert.ok(u >= 0 && u <= 1 && v >= 0 && v <= 1, `${id}: its centre falls outside ${found.view.id}`);
  }
});
