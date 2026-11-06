// AASHTO element condition-state table: each element's quantity split by condition state. Defect quantities fill
// CS 2 to 4; CS 1 is what is left of the element total. Overlapping defects must be recorded once (worst CS).
export function elementSummary(elements, defects) {
  return elements.map(e => {
    const mine = defects.filter(d => d.element_code === e.code && !d.deleted);
    const cs = [0, 0, 0, 0];
    const byDefect = {};
    for (const d of mine) {
      cs[d.cs - 1] += d.quantity;
      byDefect[d.defect_code] ??= [0, 0, 0, 0];
      byDefect[d.defect_code][d.cs - 1] += d.quantity;
    }
    const recorded = cs[1] + cs[2] + cs[3];
    cs[0] = Math.max(0, e.total - recorded);
    return { ...e, cs, over: recorded > e.total, defects: Object.entries(byDefect).map(([code, q]) => ({ code: Number(code), cs: q })) };
  });
}
