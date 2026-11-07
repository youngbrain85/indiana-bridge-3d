"""Write the `orientation` record (scripts/bridge_orientation.py) into each 3D-workspace bridge manifest.

    python scripts/record_orientation.py            # write, then check every bridge
    python scripts/record_orientation.py --check    # check only; exit 1 on any problem

Each entry was read from the plans during the November 2026 drawing review (docs/model-corrections.md section 3):
the compass direction of increasing station from the north arrow and the plan, a part whose side the plans name,
and the drawn skew direction. The record is inserted as text, so the rest of the manifest stays byte-identical.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bridge_orientation as bo  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

ORIENTATION = {
    'beechwood': dict(up_station='north', reference=('girder_A4', 'west'), skew_direction='none',
        evidence='Plans sheets 32-37: stations increase northward (South approach at the low-station end); '
                 'Beam Line No. 1 is the west beam (model girder 4).'),
    '21st-street-i465': dict(up_station='east', skew_direction='left',
        evidence='Sheet 40 and sheet 74 plans: north arrow up, stations increasing to the right; '
                 'sheets 1-2 "18 deg 00\'00" Skew Lt."'),
    'us421-wildcat': dict(up_station='northwest', reference=('haunch_A4', 'southwest'), skew_direction='none',
        evidence='Sheets 5, 16 and 20: north arrow to the lower right, Line "A" bears N 47 deg 15\' W, stations '
                 'increasing to the right; Beam No. 1 and the X-truss on the southwest (plan top).'),
    'us52-mud': dict(up_station='east', skew_direction='none',
        evidence='Sheet 21 general plan: stations increasing to the right (Bent 1 at 457+72), north arrow and the '
                 'westbound lane at the top; sheets 23 and 53 agree.'),
    'sr44-mud': dict(up_station='east', reference=('beam_1_segment_1', 'north'), skew_direction='right',
        evidence='Sheet 17 framing plan: Bent 1 to Bent 4 left to right, north arrow up, Beam 1 the top line; '
                 'sheets 1, 9, 12 and 32 "Skew 15 deg 00\'00" Rt."'),
    'sr8-yellow': dict(up_station='east', reference=('beam_0_6', 'north'),
        evidence='Sheet 5: north arrow up, Bent 1 on the west; sheet 11 framing plan: Beam 1 north; sheet 8: '
                 'Wing "A" south at Bent 1.'),
    'sr1-wabash': dict(up_station='north',
        evidence='Sheets 6 and 9: the north arrow points up-station, so the plan top (+Y) is west; 2026 sheet 11 '
                 'survey control agrees.'),
    'us50-tanners-eb': dict(up_station='east', reference=('bulbt_0_0', 'north'), skew_direction='left',
        evidence='2014 reconstruction sheets 20-23: FT barrier, Beam 1 and Line "A" on the north (left looking '
                 'up-station); north end of every support at the lower station, "Skew 20 deg Lt."'),
    'minnich-road': dict(up_station='south', reference=('plate_0_7', 'east'), skew_direction='left',
        evidence='Sheets 19 and 25: north arrow to page-left, stations increasing to the right, Girder 1 on the '
                 'east; sheets 1, 16 and 19 "Skew 56 deg 17\'55" Lt."'),
    'fletcher-avenue': dict(up_station='northwest', reference=('girder_0_7', 'southwest'), skew_direction='left',
        evidence='Sheet 55: north arrow to the lower right, stations increasing to the right; S8 framing plan and '
                 'sheet 59: Girder 1 at the upper (+Y) edge; sheets 1 and 54-56 "Skew 28 deg 47\'15" Lt."'),
    'sr10-i65': dict(up_station='east', skew_direction='none',
        evidence='Sheets 4 and 13 (PDF 24, 33) and 2026 sheet 11 (PDF 59): north up, Bent 1 (Sta. 1+492) west, '
                 'Bent 5 (1+555) east; Beam Line No. 1 on the north edge.'),
    'us35-deer': dict(up_station='east', reference=('beam_0_0', 'north'), skew_direction='right',
        evidence='Sheets 11, 13, 14 and 17: north arrow up, stations increasing to the right; Beam 1 and Wings B '
                 'and D north; sheets 1, 5, 10 and 11 "Skew 15 deg Rt."'),
    'us224-eight-mile': dict(up_station='east', skew_direction='left',
        evidence='Sheets 7 and 8: north up, stations increasing to the east; sheets 1 and 8 "30 deg Lt. Skew".'),
    'virginia-avenue': dict(up_station='northwest', reference=('beam_1', 'southwest'), skew_direction='left',
        evidence='General plan sheet 31, sheets 36-37 and existing sheet 10 (PDF 28): north arrow to the lower '
                 'right, stations increasing to the right; Girder No. 1 and the 16\'-1" south path at plan top; '
                 'sheets 1 and 30-32 "Skew 44 deg 19\'06" Lt."'),
    'sr44-little-blue': dict(up_station='northeast', skew_direction='left',
        evidence='Sheet 12 plan: stations increasing to the right, Line "PR-PR" bears N 61 deg 25\'34" E; '
                 'sheet 8 "Skew 45 deg Lt."'),
    'sr1-six-mile': dict(up_station=None,
        plus_y_note='Sheet 7 has no north arrow (the sheet 1 vicinity map shows S.R. 1 running north-south): +Y '
                    'is the plan top of sheet 7, with stations increasing to the right.',
        evidence='Sheet 7 plan; the skew direction is assumed (NBI gives its magnitude only).'),
}


def manifest_path(bid):
    return ROOT / 'data/bridges' / bid / 'model_manifest.json'


def insert(bid, entry):
    """Insert or replace the orientation record without re-serialising the rest of the manifest."""
    path = manifest_path(bid)
    raw = path.read_bytes()
    text = raw.decode('utf-8')
    data = json.loads(text)
    rec = bo.record(**entry)
    if data.get('orientation') == rec:
        return False
    crlf = '\r\n' in text
    nl = '\r\n' if crlf else '\n'
    ascii_only = all(ord(c) < 128 for c in text)
    if 'orientation' in data:
        data['orientation'] = rec
        body = json.dumps(data, indent=2, ensure_ascii=ascii_only)
        out = body.replace('\n', nl) + (nl if text.endswith(('\n', '\r\n')) else '')
    else:
        block = json.dumps({'orientation': rec}, indent=2, ensure_ascii=ascii_only)[1:-1].strip('\n')
        start = text.index('{') + 1
        out = text[:start] + nl + block.replace('\n', nl) + ',' + nl + text[start:].lstrip('\r\n')
    assert json.loads(out)['orientation'] == rec
    path.write_bytes(out.encode('utf-8'))
    return True


def ledger_skew(bid):
    path = ROOT / 'fem/collection' / f'{bid}.json'
    if path.is_file():
        return json.loads(path.read_text(encoding='utf-8')).get('values', {}).get('skew_dx_dy')
    return None


def check_all(entries=None):
    failed = 0
    for bid in ORIENTATION:
        data = json.loads(manifest_path(bid).read_text(encoding='utf-8'))
        if entries:
            data['orientation'] = bo.record(**entries[bid])
        problems = bo.check(data, ledger_skew(bid))
        print(f'{bid}: ' + ('ok' if not problems else '; '.join(problems)))
        failed += bool(problems)
    return failed


if __name__ == '__main__':
    if '--dry-run' in sys.argv:
        sys.exit(1 if check_all(ORIENTATION) else 0)
    if '--check' not in sys.argv:
        for bid, entry in ORIENTATION.items():
            if insert(bid, entry):
                print(f'{bid}: orientation recorded')
    sys.exit(1 if check_all() else 0)
