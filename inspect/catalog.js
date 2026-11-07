// AASHTO Manual for Bridge Element Inspection (MBEI, 2nd edition 2019): the elements and defects used by the
// inspection app, with condition-state (CS) wording condensed from the defect tables and the rules the app uses
// to suggest a condition state from field measurements. CS4 is never suggested: it means the defect warrants a
// structural review, which is the inspector's call.

export const CS_COLORS = { 1: '#2f8a4e', 2: '#d9a400', 3: '#e0661b', 4: '#c4242a' };
export const CS_NAMES = { 1: 'Good', 2: 'Fair', 3: 'Poor', 4: 'Severe' };

// kind: how the defect is sketched. line = traced polyline, area = outlined polygon, point = one tap.
export const DEFECTS = {
  1080: { name: 'Delamination / Spall / Patched Area', short: 'Spall / delam.', material: 'Concrete', kind: 'area',
    cs: ['None.', 'Delaminated. Spall 1 in. or less deep or 6 in. or less in diameter. Patched area that is sound.',
      'Spall greater than 1 in. deep or greater than 6 in. diameter. Patched area that is unsound or showing distress. Does not warrant structural review.',
      'The condition warrants a structural review.'] },
  1090: { name: 'Exposed Rebar', short: 'Exposed rebar', material: 'Concrete', kind: 'line',
    cs: ['None.', 'Present without measurable section loss.', 'Present with measurable section loss, but does not warrant structural review.',
      'The condition warrants a structural review.'] },
  1100: { name: 'Exposed Prestressing', short: 'Exposed strand', material: 'Concrete', kind: 'line',
    cs: ['None.', 'Present without section loss.', 'Present with section loss, but does not warrant structural review.',
      'The condition warrants a structural review.'] },
  1110: { name: 'Cracking (PSC)', short: 'Crack (PSC)', material: 'Concrete', kind: 'line',
    cs: ['Width less than 0.004 in. or spacing greater than 3.0 ft.', 'Width 0.004–0.009 in. or spacing of 1.0–3.0 ft.',
      'Width greater than 0.009 in. or spacing of less than 1 ft.', 'The condition warrants a structural review.'] },
  1120: { name: 'Efflorescence / Rust Staining', short: 'Efflorescence', material: 'Concrete', kind: 'area',
    cs: ['None.', 'Surface white without build-up or leaching without rust staining.', 'Heavy build-up with rust staining.',
      'The condition warrants a structural review.'] },
  1130: { name: 'Cracking (RC and Other)', short: 'Crack (RC)', material: 'Concrete', kind: 'line',
    cs: ['Width less than 0.012 in. or spacing greater than 3.0 ft.', 'Width 0.012–0.05 in. or spacing of 1.0–3.0 ft.',
      'Width greater than 0.05 in. or spacing of less than 1 ft.', 'The condition warrants a structural review.'] },
  1190: { name: 'Abrasion / Wear (PSC/RC)', short: 'Abrasion', material: 'Concrete', kind: 'area',
    cs: ['No abrasion or wearing.', 'Abrasion or wearing has exposed coarse aggregate but the aggregate remains secure in the concrete.',
      'Coarse aggregate is loose or has popped out of the concrete matrix due to abrasion or wear.', 'The condition warrants a structural review.'] },
  1000: { name: 'Corrosion', short: 'Corrosion', material: 'Steel', kind: 'area',
    cs: ['None.', 'Freckled rust. Corrosion of the steel has initiated.', 'Section loss is evident or pack rust is present but does not warrant structural review.',
      'The condition warrants a structural review.'] },
  2210: { name: 'Movement', short: 'Movement', material: 'Bearing', kind: 'point',
    cs: ['Free to move.', 'Minor restriction.', 'Restricted, but not warranting structural review.', 'The condition warrants a structural review.'] },
  2220: { name: 'Alignment', short: 'Alignment', material: 'Bearing', kind: 'point',
    cs: ['Lateral and vertical alignment is as expected for the temperature conditions.', 'Tolerable lateral or vertical alignment that is inconsistent with the temperature conditions.',
      'Approaching the limits of lateral or vertical alignment for the bearing but does not warrant structural review.', 'The condition warrants a structural review.'] },
  2230: { name: 'Bulging, Splitting or Tearing', short: 'Bulging / tearing', material: 'Bearing', kind: 'point',
    cs: ['None.', 'Bulging less than 15% of the thickness.', 'Bulging 15% or more of the thickness. Splitting or tearing. Bearing surfaces are not parallel. Does not warrant structural review.',
      'The condition warrants a structural review.'] },
  2240: { name: 'Loss of Bearing Area', short: 'Loss of area', material: 'Bearing', kind: 'point',
    cs: ['None.', 'Less than 10%.', '10% or more but does not warrant structural review.', 'The condition warrants a structural review.'] },
  4000: { name: 'Settlement', short: 'Settlement', material: 'General', kind: 'point',
    cs: ['None.', 'Exists within tolerable limits or arrested with no observed structural distress.', 'Exceeds tolerable limits but does not warrant structural review.',
      'The condition warrants a structural review.'] },
  6000: { name: 'Scour', short: 'Scour', material: 'General', kind: 'point',
    cs: ['None.', 'Exists within tolerable limits or has been arrested with effective countermeasures.', 'Exceeds the tolerable limits but is less than the critical limits determined by scour evaluation and does not warrant structural review.',
      'The condition warrants a structural review.'] },
  7000: { name: 'Damage', short: 'Impact damage', material: 'General', kind: 'area',
    cs: ['Not applicable.', 'The element has impact damage; the specific damage is captured in CS 2 under the appropriate material defect.',
      'The element has impact damage; the specific damage is captured in CS 3 under the appropriate material defect.',
      'The element has impact damage; the specific damage is captured in CS 4 under the appropriate material defect.'] },
};

const CONCRETE = [1080, 1090, 1120, 1130, 7000];
const SUB = [...CONCRETE, 4000, 6000];
// Defects that apply to each element (MBEI element-defect lists, limited to what Beechwood has).
export const ELEMENT_DEFECTS = {
  12: [...CONCRETE, 1190],
  109: [1080, 1090, 1100, 1110, 1120, 7000],
  205: SUB, 210: SUB, 215: SUB,
  234: [...CONCRETE, 4000],
  310: [2210, 2220, 2230, 2240, 1000, 7000],
  331: CONCRETE,
};

// Measurement inputs per defect. Values are stored in US customary units, as MBEI uses them.
export const FIELDS = {
  1080: [{ key: 'form', label: 'Type', type: 'choice', options: [['delamination', 'Delamination'], ['spall', 'Spall'], ['patch_sound', 'Patch, sound'], ['patch_unsound', 'Patch, unsound or distressed']] },
    { key: 'depth_in', label: 'Spall depth', unit: 'in', type: 'number', step: 0.25, when: m => m.form === 'spall' },
    { key: 'diameter_in', label: 'Spall diameter', unit: 'in', type: 'number', step: 0.5, auto: 'size_in', when: m => m.form === 'spall' }],
  1090: [{ key: 'section_loss', label: 'Section loss', type: 'choice', options: [['none', 'None measurable'], ['measurable', 'Measurable']] }],
  1100: [{ key: 'section_loss', label: 'Section loss', type: 'choice', options: [['none', 'None'], ['measurable', 'Section loss']] }],
  1110: [{ key: 'width_in', label: 'Crack width', unit: 'in', type: 'number', step: 0.001, presets: [0.002, 0.006, 0.012] },
    { key: 'spacing_ft', label: 'Crack spacing (pattern cracking)', unit: 'ft', type: 'number', step: 0.5, optional: true }],
  1130: [{ key: 'width_in', label: 'Crack width', unit: 'in', type: 'number', step: 0.001, presets: [0.008, 0.02, 0.06] },
    { key: 'spacing_ft', label: 'Crack spacing (pattern cracking)', unit: 'ft', type: 'number', step: 0.5, optional: true }],
  1120: [{ key: 'severity', label: 'Appearance', type: 'choice', options: [['white', 'White, no build-up'], ['heavy', 'Heavy build-up or rust staining']] }],
  1190: [{ key: 'aggregate', label: 'Coarse aggregate', type: 'choice', options: [['exposed', 'Exposed, secure'], ['loose', 'Loose or popped out']] }],
  1000: [{ key: 'level', label: 'Corrosion', type: 'choice', options: [['freckled', 'Freckled rust'], ['section_loss', 'Section loss or pack rust']] }],
  2210: [{ key: 'restriction', label: 'Movement', type: 'choice', options: [['minor', 'Minor restriction'], ['restricted', 'Restricted']] }],
  2220: [{ key: 'alignment', label: 'Alignment', type: 'choice', options: [['tolerable', 'Tolerable, not as expected'], ['near_limit', 'Approaching the limits']] }],
  2230: [{ key: 'bulging_pct', label: 'Bulging', unit: '% of thickness', type: 'number', step: 1 },
    { key: 'split', label: 'Splitting or tearing, or surfaces not parallel', type: 'check' }],
  2240: [{ key: 'loss_pct', label: 'Loss of bearing area', unit: '%', type: 'number', step: 1 }],
  4000: [], 6000: [], 7000: [],
};

const num = v => (v === '' || v === null || v === undefined || Number.isNaN(Number(v))) ? null : Number(v);
const worst = (...a) => Math.max(...a.filter(Boolean));

// Suggested condition state from the measurements, with the MBEI wording that decided it.
// Returns {cs, basis} or null when the defect needs the inspector's judgement (or measurements are missing).
export function suggestCS(code, m = {}) {
  const d = DEFECTS[code];
  const pick = (cs, basis) => ({ cs, basis: basis || d.cs[cs - 1] });
  switch (Number(code)) {
    case 1080: {
      if (m.form === 'delamination' || m.form === 'patch_sound') return pick(2);
      if (m.form === 'patch_unsound') return pick(3);
      if (m.form === 'spall') {
        const depth = num(m.depth_in), dia = num(m.diameter_in);
        if (depth === null && dia === null) return null;
        return (depth !== null && depth > 1) || (dia !== null && dia > 6) ? pick(3) : pick(2);
      }
      return null;
    }
    case 1090: case 1100:
      return m.section_loss === 'measurable' ? pick(3) : m.section_loss === 'none' ? pick(2) : null;
    case 1110: case 1130: {
      const w = num(m.width_in), s = num(m.spacing_ft);
      if (w === null && s === null) return null;
      const [lo, hi] = code == 1110 ? [0.004, 0.009] : [0.012, 0.05];
      const byWidth = w === null ? null : w < lo ? 1 : w <= hi ? 2 : 3;
      const bySpacing = s === null ? null : s > 3 ? 1 : s >= 1 ? 2 : 3;
      return pick(worst(byWidth, bySpacing));
    }
    case 1120: return m.severity === 'heavy' ? pick(3) : m.severity === 'white' ? pick(2) : null;
    case 1190: return m.aggregate === 'loose' ? pick(3) : m.aggregate === 'exposed' ? pick(2) : null;
    case 1000: return m.level === 'section_loss' ? pick(3) : m.level === 'freckled' ? pick(2) : null;
    case 2210: return m.restriction === 'restricted' ? pick(3) : m.restriction === 'minor' ? pick(2) : null;
    case 2220: return m.alignment === 'near_limit' ? pick(3) : m.alignment === 'tolerable' ? pick(2) : null;
    case 2230: {
      const b = num(m.bulging_pct);
      if (m.split) return pick(3);
      if (b === null) return null;
      return b >= 15 ? pick(3) : b > 0 ? pick(2) : pick(1);
    }
    case 2240: {
      const l = num(m.loss_pct);
      if (l === null) return null;
      return l >= 10 ? pick(3) : l > 0 ? pick(2) : pick(1);
    }
    default: return null;
  }
}

export function defectsFor(elementCode) {
  return (ELEMENT_DEFECTS[elementCode] || Object.keys(DEFECTS).map(Number)).map(code => ({ code, ...DEFECTS[code] }));
}

export const MATERIAL_ORDER = ['Concrete', 'Steel', 'Bearing', 'General'];
