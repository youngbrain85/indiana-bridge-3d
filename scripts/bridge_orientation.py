"""Handedness rule for every bridge model in this collection.

Native frame of every model (metres, right-handed):
    X   increasing station ("up-station")
    +Y  the side to the LEFT when looking up-station
    Z   up
The GLB stores (X, Z, -Y). That is a proper rotation, so a model built in this frame is never mirrored.

How models came out mirrored: a generator traced the plan in page coordinates, where the page's y axis runs down
(US 35 and US 224, "Y toward the drawing south"), or placed the north side or Girder 1 at -Y by habit (US 50 EB,
Virginia Avenue). Neither can be checked afterwards unless the generator says what it meant. So a generator now
declares the compass direction of increasing station, read from the plan and its north arrow, and every
transverse side follows from it: +Y is that direction turned 90 degrees to the left.

Skew sign: skew_deg > 0 is a LEFT skew ("Lt." on the plans): looking up-station, the left (+Y) end of each
support line is down-station. A support line is x = u - tan(skew_deg) * y (bridge_geometry.Model.sx), and a FEM
ledger's skew_dx_dy is -tan(skew_deg). Checked against the drawn "Lt."/"Rt." callouts of the collection: US 35
(15 deg Rt.), US 224 (30 deg Lt.), US 50 EB (20 deg Lt.), Virginia Avenue, Fletcher Avenue, Minnich Road,
21st Street and SR 44 Little Blue (Lt.), SR 44 Mud (15 deg Rt.).

This module has no third-party dependencies, so the checker and the tests can import it anywhere.
"""
import math
import re

COMPASS = ('north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest')
FRAME = 'right-handed: X increasing station, +Y left looking up-station, Z up; GLB (X, Z, -Y)'
SKEW_RULE = ('skew_deg > 0 is a left skew: looking up-station, the +Y end of each support line is down-station '
             '(x = u - tan(skew_deg) * y)')
WORD = re.compile(r'\b(north|south)(east|west)?\b|\b(east|west)\b', re.I)


def _index(compass):
    if compass not in COMPASS:
        raise ValueError(f'Unknown compass direction {compass!r}; use one of {", ".join(COMPASS)}')
    return COMPASS.index(compass)


def left_of(up_station):
    """The compass side to the left looking along up_station (90 degrees anticlockwise in plan)."""
    return COMPASS[(_index(up_station) - 2) % 8]


def opposite(compass):
    return COMPASS[(_index(compass) + 4) % 8]


def _angle(a, b):
    d = abs(_index(a) - _index(b)) * 45 % 360
    return min(d, 360 - d)


def side_of(plus_y, compass):
    """+1 when compass lies on the +Y side (within 45 degrees of plus_y), -1 on the -Y side, 0 when it is along
    the bridge (north/south words on an east-west bridge name ends, not sides)."""
    a = _angle(plus_y, compass)
    return 1 if a <= 45 else -1 if a >= 135 else 0


def record(up_station, evidence, reference=None, skew_direction=None, plus_y_note=None):
    """The `orientation` entry of a model manifest.

    up_station: compass direction of increasing station on the plan (nearest of eight points), or None when the
        plans have no north arrow; then plus_y_note must say how the +Y side was fixed (e.g. "plan top on sheet 7,
        stations increasing to the right").
    evidence: the sheets that show it (north arrow, plan, typical section labels).
    reference: optional (part_id, compass) of a part whose side the drawings name, e.g. ('beam_0_0', 'north').
    skew_direction: 'left', 'right' or 'none' as drawn ("Lt."/"Rt."), or None when the plans do not say.
    """
    if up_station is None and not plus_y_note:
        raise ValueError('Without a north arrow, say how +Y was fixed (plus_y_note).')
    if skew_direction not in (None, 'left', 'right', 'none'):
        raise ValueError("skew_direction must be 'left', 'right', 'none' or None")
    out = dict(frame=FRAME, up_station=up_station,
               plus_y=left_of(up_station) if up_station else None,
               minus_y=opposite(left_of(up_station)) if up_station else None)
    if plus_y_note:
        out['plus_y_note'] = plus_y_note
    if reference:
        part, compass = reference
        _index(compass)
        out['reference'] = dict(part_id=part, side=compass)
    out.update(skew_direction=skew_direction, skew_rule=SKEW_RULE, evidence=evidence)
    return out


def _centre_y(part):
    (x0, y0, z0), (x1, y1, z1) = part['bounds_m']
    return (y0 + y1) / 2, y0, y1


def support_skew_slopes(parts):
    """dx/dy of each support line, from bearings grouped by id (the id without its last index)."""
    lines = {}
    for p in parts:
        if p.get('layer') != 'bearings' or 'bounds_m' not in p:
            continue
        key = re.sub(r'_-?\d+$', '', p['id'])
        if key == p['id']:
            continue
        (x0, y0, _), (x1, y1, _) = p['bounds_m']
        lines.setdefault(key, []).append(((x0 + x1) / 2, (y0 + y1) / 2))
    slopes = []
    for pts in lines.values():
        ys = [y for _, y in pts]
        if len(pts) < 3 or max(ys) - min(ys) < 1:
            continue
        n = len(pts); my = sum(ys) / n; mx = sum(x for x, _ in pts) / n
        slopes.append(sum((y - my) * (x - mx) for x, y in pts) / sum((y - my) ** 2 for y in ys))
    return slopes


def check(manifest, ledger_skew_dx_dy=None):
    """Problems with a manifest's handedness and skew sign; an empty list when everything agrees."""
    o = manifest.get('orientation')
    if not o:
        return ['no orientation record (bridge_orientation.record)']
    problems = []
    if o.get('frame') != FRAME:
        problems.append(f'frame is {o.get("frame")!r}, not the collection frame')
    up, plus_y = o.get('up_station'), o.get('plus_y')
    if up and plus_y != left_of(up):
        problems.append(f'plus_y {plus_y} is not left of up-station {up}')
    if not up and not o.get('plus_y_note'):
        problems.append('no up-station and no plus_y_note')
    parts = {p['id']: p for p in manifest.get('parts', [])}
    ref = o.get('reference')
    if ref and plus_y:
        part = parts.get(ref['part_id'])
        if not part:
            problems.append(f'reference part {ref["part_id"]} is not in the manifest')
        else:
            want = side_of(plus_y, ref['side'])
            y = _centre_y(part)[0]
            if want == 0 or y * want <= 0:
                problems.append(f'reference {ref["part_id"]} ({ref["side"]}) is at Y = {y:.3f}')
    if plus_y:
        wrong = []
        for p in parts.values():
            if 'bounds_m' not in p:
                continue
            y, y0, y1 = _centre_y(p)
            if abs(y) < 0.5 or y0 * y1 <= 0:
                continue  # on or across the centre line
            m = WORD.search(p.get('name') or '')
            if not m:
                continue
            want = side_of(plus_y, m.group(0).lower())
            if want and y * want < 0:
                wrong.append(f'{p["id"]} "{p.get("name")}" at Y = {y:.2f}')
        if wrong:
            problems.append(f'{len(wrong)} part name(s) on the wrong side: ' + '; '.join(wrong[:5]))
    skew = manifest.get('skew_deg') or 0
    direction = o.get('skew_direction')
    if direction == 'left' and not skew > 0 or direction == 'right' and not skew < 0 \
            or direction == 'none' and abs(skew) > 0.5:
        problems.append(f'skew_deg {skew} does not match the drawn {direction} skew ({SKEW_RULE})')
    k = -math.tan(math.radians(skew))
    slopes = support_skew_slopes(parts.values())
    if slopes and abs(skew) > 1:
        bad = [s for s in slopes if abs(s - k) > 0.02 * max(1, abs(k))]
        if bad:
            problems.append(f'support lines run at dx/dy {bad[0]:.4f}, not -tan(skew_deg) = {k:.4f}')
    if ledger_skew_dx_dy is not None and abs(ledger_skew_dx_dy - k) > 1e-3 * max(1, abs(k)):
        problems.append(f'FEM ledger skew_dx_dy {ledger_skew_dx_dy:.4f} is not -tan(skew_deg) = {k:.4f}')
    return problems
