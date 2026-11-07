// Sheet geometry for the inspection app: canvas (mm) <-> view coordinates, which view and element a sketch is on,
// and AASHTO element quantities from the sketch. View coordinates (u, v) run 0..1 from the top-left of a view,
// v down the sheet; a view spans extent_m[0] x extent_m[1] metres of the model (see sheets.json "mapping").

export const FT = 0.3048;

export function viewRect(view, canvas) {
  const [px, py, pw, ph] = view.placement;
  return { x: px * canvas[0], y: py * canvas[1], w: pw * canvas[0], h: ph * canvas[1] };
}

export function toView([x, y], view, canvas) {
  const r = viewRect(view, canvas);
  return [(x - r.x) / r.w, (y - r.y) / r.h];
}

export function toCanvas([u, v], view, canvas) {
  const r = viewRect(view, canvas);
  return [r.x + u * r.w, r.y + v * r.h];
}

// The view holding most of a sketch. share = fraction of the points inside it (1 mm tolerance on the sheet).
export function assignView(points, sheet, canvas) {
  let best = null;
  for (const view of sheet.views) {
    const r = viewRect(view, canvas);
    const inside = points.filter(([x, y]) => x >= r.x - 1 && x <= r.x + r.w + 1 && y >= r.y - 1 && y <= r.y + r.h + 1).length;
    if (!best || inside > best.inside) best = { view, inside };
  }
  return best && best.inside ? { view: best.view, share: best.inside / points.length } : null;
}

// Even-odd point in polygon with holes (rings[0] outer, the rest holes).
export function inRings([x, y], rings) {
  let inside = false;
  for (const ring of rings) {
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      const [xi, yi] = ring[i], [xj, yj] = ring[j];
      if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) inside = !inside;
    }
  }
  return inside;
}

export function partAt(uv, view) {
  for (const region of view.regions) if (region.polygons.some(rings => inRings(uv, rings))) return region.part;
  return null;
}

// Points along a path, at most `step` apart (in view units), so long straight strokes are weighed fairly.
export function densify(path, step = 0.01, closed = false) {
  const out = [];
  const pts = closed && path.length > 2 ? [...path, path[0]] : path;
  for (let i = 0; i < pts.length - 1; i++) {
    const [a, b] = [pts[i], pts[i + 1]];
    const n = Math.max(1, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) / step));
    for (let k = 0; k < n; k++) out.push([a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n]);
  }
  out.push(pts[pts.length - 1]);
  return out;
}

// The inspectable part under most of a sketch: {part, share, counts}. An area also counts its interior samples.
export function elementFor(path, view, kind) {
  const samples = densify(path, 0.005, kind === 'area');
  if (kind === 'area' && path.length > 2) {
    const xs = path.map(p => p[0]), ys = path.map(p => p[1]);
    const [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
    for (let i = 1; i < 8; i++) for (let j = 1; j < 8; j++) {
      const p = [x0 + (x1 - x0) * i / 8, y0 + (y1 - y0) * j / 8];
      if (inRings(p, [path])) samples.push(p);
    }
  }
  const counts = {};
  for (const p of samples) { const part = partAt(p, view); if (part) counts[part] = (counts[part] || 0) + 1; }
  const part = Object.keys(counts).sort((a, b) => counts[b] - counts[a])[0] || null;
  return { part, share: part ? counts[part] / samples.length : 0, counts };
}

export const metres = (path, view) => path.map(([u, v]) => [u * view.extent_m[0], v * view.extent_m[1]]);

export function lengthM(path, view) {
  const m = metres(path, view);
  let total = 0;
  for (let i = 1; i < m.length; i++) total += Math.hypot(m[i][0] - m[i - 1][0], m[i][1] - m[i - 1][1]);
  return total;
}

export function areaM2(path, view) {
  const m = metres(path, view);
  let a = 0;
  for (let i = 0, j = m.length - 1; i < m.length; j = i++) a += (m[j][0] + m[i][0]) * (m[j][1] - m[i][1]);
  return Math.abs(a) / 2;
}

export function maxDimM(path, view) {
  const m = metres(path, view);
  let d = 0;
  for (let i = 0; i < m.length; i++) for (let j = i + 1; j < m.length; j++) d = Math.max(d, Math.hypot(m[i][0] - m[j][0], m[i][1] - m[j][1]));
  return d;
}

// Extent of the sketch along a member axis (glTF world vector), e.g. the length of girder a defect affects.
export function extentAlongM(path, view, axis) {
  const [U, V, [ex, ey]] = [view.u, view.v, view.extent_m];
  const dots = path.map(([u, v]) => [0, 1, 2].reduce((s, k) => s + (u * ex * U[k] + v * ey * V[k]) * axis[k], 0));
  return Math.max(...dots) - Math.min(...dots);
}

// AASHTO quantity of a defect on its element, in the element's unit, with the rule used.
export function quantityFor({ kind, path, view, unit, axis }) {
  if (unit === 'each') return { quantity: 1, basis: 'One element affected' };
  if (unit === 'ft') {
    if (kind === 'point' || !axis) return { quantity: 1, basis: 'Point defect: 1 ft of the member' };
    const ft = extentAlongM(path, view, axis) / FT;
    return { quantity: Math.max(1, Math.round(ft)), basis: `Length of member affected: ${ft.toFixed(1)} ft` };
  }
  // sq ft (decks): outlined area, or a 1 ft wide band along a traced line.
  if (kind === 'area') {
    const sqft = areaM2(path, view) / (FT * FT);
    return { quantity: Math.max(1, Math.round(sqft)), basis: `Outlined area: ${sqft.toFixed(1)} sq ft` };
  }
  if (kind === 'line') {
    const ft = lengthM(path, view) / FT;
    return { quantity: Math.max(1, Math.round(ft)), basis: `Traced length ${ft.toFixed(1)} ft × 1 ft band` };
  }
  return { quantity: 1, basis: 'Point defect: 1 sq ft' };
}

// Ramer-Douglas-Peucker simplification (tolerance in the same units as the points).
export function simplify(points, tol) {
  if (points.length < 3) return points.slice();
  const keep = new Uint8Array(points.length);
  keep[0] = keep[points.length - 1] = 1;
  const stack = [[0, points.length - 1]];
  while (stack.length) {
    const [a, b] = stack.pop();
    const [ax, ay] = points[a], [bx, by] = points[b];
    const len = Math.hypot(bx - ax, by - ay) || 1e-12;
    let worst = -1, index = -1;
    for (let i = a + 1; i < b; i++) {
      const d = Math.abs((bx - ax) * (ay - points[i][1]) - (ax - points[i][0]) * (by - ay)) / len;
      if (d > worst) { worst = d; index = i; }
    }
    if (worst > tol) { keep[index] = 1; stack.push([a, index], [index, b]); }
  }
  return points.filter((_, i) => keep[i]);
}

// The 3D world point (before the ray cast) of a view coordinate.
export function planePoint([u, v], view) {
  const [ex, ey] = view.extent_m;
  return [0, 1, 2].map(k => view.origin[k] + u * ex * view.u[k] + v * ey * view.v[k]);
}

export function round(points, digits = 5) {
  const f = 10 ** digits;
  return points.map(p => p.map(c => Math.round(c * f) / f));
}

const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];

// A path in one view's coordinates, in another view's coordinates. Both views must look the same way (equal
// normals): each point goes to the world plane of `from` and is projected onto the plane of `to`.
export function remapToView(path, from, to) {
  const [ex, ey] = to.extent_m;
  return path.map(uv => {
    const p = planePoint(uv, from), d = [0, 1, 2].map(k => p[k] - to.origin[k]);
    return [Math.round(dot(d, to.u) / ex * 1e5) / 1e5, Math.round(dot(d, to.v) / ey * 1e5) / 1e5];
  });
}

// The current sheet and view of a defect. View frames never move under a view id: when a rebuild of the sheets
// changes a view, the old frame is kept in catalog.retired_views with the view that replaces it. A defect drawn on
// a retired view is returned on its replacement, with its path mapped (the stored record is left as it is).
export function currentView(d, catalog) {
  const find = id => { for (const sheet of catalog.sheets) { const view = sheet.views.find(v => v.id === id); if (view) return { sheet, view }; } return null; };
  const here = catalog.sheets.find(s => s.id === d.sheet_id)?.views.find(v => v.id === d.view_id);
  if (here) return { defect: d, view: here };
  const moved = find(d.view_id);
  if (moved) return { defect: { ...d, sheet_id: moved.sheet.id }, view: moved.view };
  const retired = catalog.retired_views || {};
  let from = retired[d.view_id], id = from?.replaced_by;
  for (let hops = 0; id && retired[id] && hops < 20; hops++) id = retired[id].replaced_by;
  const next = id && find(id);
  if (!from || !next) return { defect: d, view: null, frame: from || null };
  return { defect: { ...d, sheet_id: next.sheet.id, view_id: next.view.id, path: remapToView(d.path, from, next.view) },
    view: next.view, remapped: d.view_id };
}
