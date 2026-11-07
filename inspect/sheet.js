// Sheet canvas: one SVG holding the inspection sheet and a defect overlay, in sheet millimetres. Zoom and pan
// change the viewBox, so lines stay sharp at any zoom. Drawing: pen, mouse or one finger draws in draw mode;
// two fingers always pan and zoom. Once a pen has been used, fingers no longer draw (palm rejection).
import { CS_COLORS } from './catalog.js';
import { simplify } from './geometry.js';

const NS = 'http://www.w3.org/2000/svg';
const make = (tag, attrs = {}, parent) => {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) if (v !== undefined && v !== null) n.setAttribute(k, v);
  if (parent) parent.append(n);
  return n;
};

export class SheetCanvas {
  constructor(host, { onSketch, onPick, onZoom } = {}) {
    this.host = host; this.onSketch = onSketch; this.onPick = onPick; this.onZoom = onZoom;
    this.canvas = [420, 297];
    this.svg = make('svg', { class: 'sheet-svg', role: 'img', 'aria-label': 'Inspection sheet' }, host);
    this.sheetLayer = make('g', { class: 'sheet-layer' }, this.svg);
    this.highlight = make('g', { class: 'highlight-layer' }, this.svg);
    this.defectLayer = make('g', { class: 'defect-layer' }, this.svg);
    this.liveLayer = make('g', { class: 'live-layer' }, this.svg);
    this.vb = { x: 0, y: 0, w: 420, h: 297 };
    this.mode = 'pan';
    this.kind = null;
    this.penSeen = false;
    this.pointers = new Map();
    this.stroke = null;
    this.bind();
    new ResizeObserver(() => this.fit(true)).observe(host);
  }

  load(svgText, canvas = [420, 297]) {
    this.canvas = canvas;
    const doc = new DOMParser().parseFromString(svgText, 'image/svg+xml');
    const root = doc.documentElement;
    // The sheet's own stylesheet is scoped to the sheet layer so it cannot style the page (and vice versa).
    for (const style of root.querySelectorAll('style')) {
      style.textContent = style.textContent.replace(/(^|\})\s*([^{}]+)\{/g, (m, end, sel) =>
        `${end}${sel.split(',').map(x => '.sheet-layer ' + x.trim()).join(',')}{`);
    }
    this.sheetLayer.replaceChildren(...[...root.childNodes].map(n => document.importNode(n, true)));
    this.fit();
  }

  size() { const r = this.host.getBoundingClientRect(); return [Math.max(1, r.width), Math.max(1, r.height)]; }

  fit(keepCentre = false) {
    const [W, H] = this.size(), [cw, ch] = this.canvas;
    if (keepCentre && this.fitted) {
      const cx = this.vb.x + this.vb.w / 2, cy = this.vb.y + this.vb.h / 2;
      this.vb.h = this.vb.w * H / W;
      this.vb.x = cx - this.vb.w / 2; this.vb.y = cy - this.vb.h / 2;
    } else {
      const k = Math.min(W / cw, H / ch) * 0.97;
      this.vb = { w: W / k, h: H / k, x: cw / 2 - W / k / 2, y: ch / 2 - H / k / 2 };
      this.fitted = true;
    }
    this.apply();
  }

  // Frame a sheet rectangle (mm), e.g. one view or one defect.
  frame([x, y, w, h], pad = 6) {
    const [W, H] = this.size();
    const k = Math.min(W / (w + 2 * pad), H / (h + 2 * pad));
    this.vb = { w: W / k, h: H / k, x: x + w / 2 - W / k / 2, y: y + h / 2 - H / k / 2 };
    this.apply();
  }

  zoomBy(f, at) {
    const [W, H] = this.size();
    const [mx, my] = at || [this.vb.x + this.vb.w / 2, this.vb.y + this.vb.h / 2];
    const w = Math.min(Math.max(this.vb.w / f, 6), this.canvas[0] * 3);
    const g = w / this.vb.w;
    this.vb = { x: mx - (mx - this.vb.x) * g, y: my - (my - this.vb.y) * g, w, h: w * H / W };
    this.apply();
  }

  apply() {
    const { x, y, w, h } = this.vb;
    this.svg.setAttribute('viewBox', `${x} ${y} ${w} ${h}`);
    this.scaleTags?.();
    this.onZoom?.(this.size()[0] / w);
  }

  toSheet(e) {
    const r = this.svg.getBoundingClientRect();
    return [this.vb.x + (e.clientX - r.left) / r.width * this.vb.w, this.vb.y + (e.clientY - r.top) / r.height * this.vb.h];
  }

  setMode(mode, kind = null) {
    this.mode = mode; this.kind = kind;
    this.host.dataset.mode = mode;
    this.cancelStroke();
  }

  cancelStroke() { this.stroke = null; this.liveLayer.replaceChildren(); }

  bind() {
    const s = this.svg;
    s.addEventListener('contextmenu', e => e.preventDefault());
    s.addEventListener('wheel', e => {
      e.preventDefault();
      this.zoomBy(Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0018)), this.toSheet(e));
    }, { passive: false });
    s.addEventListener('pointerdown', e => {
      if (e.pointerType === 'pen') this.penSeen = true;
      s.setPointerCapture(e.pointerId);
      this.pointers.set(e.pointerId, { x: e.clientX, y: e.clientY, type: e.pointerType, start: [e.clientX, e.clientY], target: e.target });
      const touches = [...this.pointers.values()].filter(p => p.type === 'touch');
      if (touches.length >= 2) { // two fingers: pinch, and drop any finger stroke
        if (this.stroke?.type === 'touch') this.cancelStroke();
        this.pinch = this.pinchState();
        return;
      }
      const draws = this.mode === 'draw' && (e.pointerType === 'pen' || (e.pointerType === 'mouse' && e.button === 0) ||
        (e.pointerType === 'touch' && !this.penSeen));
      if (draws && !this.stroke) {
        this.stroke = { id: e.pointerId, type: e.pointerType, points: [this.toSheet(e)] };
        this.drawLive();
      }
    });
    s.addEventListener('pointermove', e => {
      const p = this.pointers.get(e.pointerId);
      if (!p) return;
      const dx = e.clientX - p.x, dy = e.clientY - p.y;
      p.x = e.clientX; p.y = e.clientY;
      if (this.pinch && p.type === 'touch') { this.updatePinch(); return; }
      if (this.stroke?.id === e.pointerId) {
        const events = e.getCoalescedEvents ? e.getCoalescedEvents() : [e];
        for (const ev of events.length ? events : [e]) this.stroke.points.push(this.toSheet(ev));
        this.drawLive();
        return;
      }
      if (this.stroke) return;
      // Pan: any drag in pan mode, or right/middle mouse and fingers in draw mode (when fingers do not draw).
      const [W] = this.size();
      const k = this.vb.w / W;
      this.vb.x -= dx * k; this.vb.y -= dy * k;
      this.apply();
    });
    const end = e => {
      const p = this.pointers.get(e.pointerId);
      this.pointers.delete(e.pointerId);
      if (this.pinch && [...this.pointers.values()].filter(q => q.type === 'touch').length < 2) this.pinch = null;
      if (this.stroke?.id === e.pointerId) {
        const stroke = this.stroke;
        this.stroke = null;
        if (e.type === 'pointercancel') { this.liveLayer.replaceChildren(); return; }
        this.finish(stroke);
        return;
      }
      if (p && e.type === 'pointerup' && Math.hypot(e.clientX - p.start[0], e.clientY - p.start[1]) < 6) {
        const hit = (p.target.closest && p.target.closest('[data-defect]')) || null;
        if (hit && this.mode === 'pan') this.onPick?.(hit.dataset.defect);
      }
    };
    s.addEventListener('pointerup', end);
    s.addEventListener('pointercancel', end);
  }

  pinchState() {
    const t = [...this.pointers.values()].filter(p => p.type === 'touch').slice(0, 2);
    const mid = { clientX: (t[0].x + t[1].x) / 2, clientY: (t[0].y + t[1].y) / 2 };
    return { dist: Math.hypot(t[0].x - t[1].x, t[0].y - t[1].y), at: this.toSheet(mid), vb: { ...this.vb } };
  }

  updatePinch() {
    const t = [...this.pointers.values()].filter(p => p.type === 'touch').slice(0, 2);
    if (t.length < 2) return;
    const dist = Math.hypot(t[0].x - t[1].x, t[0].y - t[1].y);
    const [W, H] = this.size();
    const r = this.svg.getBoundingClientRect();
    const start = this.pinch;
    const w = Math.min(Math.max(start.vb.w * start.dist / Math.max(dist, 1), 6), this.canvas[0] * 3);
    const mx = ((t[0].x + t[1].x) / 2 - r.left) / W, my = ((t[0].y + t[1].y) / 2 - r.top) / H;
    // Keep the sheet point that started under the fingers under their midpoint.
    this.vb = { w, h: w * H / W, x: start.at[0] - mx * w, y: start.at[1] - my * w * H / W };
    this.apply();
  }

  drawLive() {
    const pts = this.stroke.points;
    const d = pts.map(p => p.map(c => c.toFixed(2)).join(',')).join(' ');
    this.liveLayer.replaceChildren();
    if (this.kind === 'area') make('polygon', { points: d, class: 'live area' }, this.liveLayer);
    else if (this.kind === 'point') make('circle', { cx: pts.at(-1)[0], cy: pts.at(-1)[1], r: 1.4, class: 'live point' }, this.liveLayer);
    else make('polyline', { points: d, class: 'live line' }, this.liveLayer);
  }

  finish(stroke) {
    const [W] = this.size();
    const mmPerPx = this.vb.w / W;
    let pts = stroke.points;
    if (this.kind === 'point') pts = [pts.at(-1)];
    else pts = simplify(pts, 1.2 * mmPerPx);
    const span = Math.max(...pts.map(p => Math.hypot(p[0] - pts[0][0], p[1] - pts[0][1])));
    if (this.kind !== 'point' && (pts.length < 2 || span < 4 * mmPerPx)) {
      // A tap in line/area mode is not a sketch.
      this.liveLayer.replaceChildren();
      this.onSketch?.(null, this.kind, 'too-short');
      return;
    }
    if (this.kind === 'area' && pts.length < 3) { this.liveLayer.replaceChildren(); this.onSketch?.(null, this.kind, 'too-short'); return; }
    this.onSketch?.(pts, this.kind);
  }

  // defects: [{id, number, kind, cs, points (sheet mm), selected, code}]
  showDefects(list) {
    this.defectLayer.replaceChildren();
    for (const d of list) {
      const g = make('g', { class: 'defect' + (d.selected ? ' selected' : ''), 'data-defect': d.id, style: `--cs:${CS_COLORS[d.cs] || '#6b7378'}` }, this.defectLayer);
      const pts = d.points.map(p => p.map(c => c.toFixed(2)).join(',')).join(' ');
      if (d.kind === 'point') {
        make('circle', { cx: d.points[0][0], cy: d.points[0][1], r: 1.5, class: 'mark' }, g);
      } else if (d.kind === 'area') {
        make('polygon', { points: pts, class: 'shape area' + (d.code == 1120 ? ' dashed' : '') }, g);
      } else {
        make('polyline', { points: pts, class: 'hit' }, g);
        make('polyline', { points: pts, class: 'shape line' }, g);
      }
      const [lx, ly] = d.points.reduce((a, p) => (p[1] < a[1] ? p : a), d.points[0]);
      const label = make('g', { class: 'tag' }, g);
      label.dataset.at = `${(lx + 0.6).toFixed(2)},${(ly - 0.6).toFixed(2)}`;
      make('rect', { x: 0, y: -2.3, width: 1.25 * String(d.number).length + 2.1, height: 2.8, rx: .6 }, label);
      const t = make('text', { x: 1.05, y: -.35 }, label);
      t.textContent = d.number;
    }
    this.scaleTags();
  }

  // Number tags keep about the same size on screen at every zoom.
  scaleTags() {
    const k = this.size()[0] / this.vb.w;
    const s = Math.min(4, Math.max(0.4, 5.7 / k));
    for (const tag of this.defectLayer.querySelectorAll('.tag')) tag.setAttribute('transform', `translate(${tag.dataset.at}) scale(${s.toFixed(3)})`);
  }

  showHighlight(rects) {
    this.highlight.replaceChildren();
    for (const r of rects) make('rect', { x: r.x, y: r.y, width: r.w, height: r.h, class: 'view-highlight' }, this.highlight);
  }

  clearLive() { this.liveLayer.replaceChildren(); }
}
