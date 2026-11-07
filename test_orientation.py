"""Handedness rule: scripts/bridge_orientation.py and its use by bridge_geometry.Model.

The rule tests need only the standard library. The Model tests need numpy, trimesh and shapely and are skipped
without them.
"""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
import bridge_orientation as bo  # noqa: E402

try:
    import numpy as np
    import bridge_geometry as bg
except ImportError:  # pragma: no cover - CI installs only the catalogue dependencies
    bg = None


def part(pid, name, y0, y1, layer='deck', x0=-1.0, x1=1.0):
    return dict(id=pid, name=name, layer=layer, bounds_m=[[x0, y0, 0.0], [x1, y1, 1.0]])


class RuleTests(unittest.TestCase):
    def test_left_of_up_station(self):
        self.assertEqual(bo.left_of('east'), 'north')
        self.assertEqual(bo.left_of('north'), 'west')
        self.assertEqual(bo.left_of('south'), 'east')
        self.assertEqual(bo.left_of('northwest'), 'southwest')
        self.assertEqual(bo.opposite('southwest'), 'northeast')
        with self.assertRaises(ValueError):
            bo.left_of('up')

    def test_side_of_handles_diagonals_and_bridge_ends(self):
        self.assertEqual(bo.side_of('southwest', 'south'), 1)
        self.assertEqual(bo.side_of('southwest', 'north'), -1)
        self.assertEqual(bo.side_of('north', 'east'), 0)      # an east abutment is an end, not a side

    def test_consistent_manifest_passes(self):
        m = dict(skew_deg=30, orientation=bo.record('east', 'plan', ('beam_1', 'north'), 'left'),
                 parts=[part('beam_1', 'Beam 1', 4, 5), part('walk_s', 'South sidewalk', -6, -4),
                        part('abut_e', 'East abutment', -5, 5)])
        self.assertEqual(bo.check(m, -math.tan(math.radians(30))), [])

    def test_mirrored_model_is_caught(self):
        # US 35 before the review: Beam 1 (north) built at -Y with the skew sign of a left-handed frame.
        m = dict(skew_deg=15, orientation=bo.record('east', 'plan', ('beam_0_0', 'north'), 'right'),
                 parts=[part('beam_0_0', 'BT48x49 beam 1', -5, -4), part('wing', 'North wing wall', -7, -6)])
        problems = ' | '.join(bo.check(m))
        self.assertIn('reference beam_0_0 (north)', problems)
        self.assertIn('wrong side', problems)
        self.assertIn('drawn right skew', problems)

    def test_skew_sign_against_bearings_and_ledger(self):
        k = -math.tan(math.radians(20))
        bearings = [part(f'bearing_1_{j}', 'Bearing', y - .2, y + .2, 'bearings', k * y - .2, k * y + .2)
                    for j, y in enumerate([-4, 0, 4])]
        m = dict(skew_deg=20, orientation=bo.record('east', 'plan', skew_direction='left'), parts=bearings)
        self.assertEqual(bo.check(m, k), [])
        m['skew_deg'] = -20
        problems = ' | '.join(bo.check(m, k))
        self.assertIn('support lines run at dx/dy', problems)
        self.assertIn('FEM ledger skew_dx_dy', problems)

    def test_missing_record_and_unknown_north(self):
        self.assertEqual(bo.check(dict(parts=[])), ['no orientation record (bridge_orientation.record)'])
        with self.assertRaises(ValueError):
            bo.record(None, 'sheet 7')
        rec = bo.record(None, 'sheet 7', plus_y_note='plan top of sheet 7')
        self.assertIsNone(rec['plus_y'])
        self.assertEqual(bo.check(dict(parts=[], orientation=rec)), [])


@unittest.skipIf(bg is None, 'numpy, trimesh and shapely are needed for the Model tests')
class ModelTests(unittest.TestCase):
    def model(self, skew=20):
        m = bg.Model('test-bridge', 10.0, 8.0, skew, lambda x: np.zeros_like(np.asarray(x, float)) + 5)
        return m

    def build(self, m, beam_y):
        m.add('beam_1', 'Beam 1 (north)', 'deck', bg.box(-4, 4, beam_y - .3, beam_y + .3, 3, 4), [1])
        m.add('walk_south', 'South sidewalk', 'sidewalks', bg.box(-4, 4, -beam_y - .5, -beam_y + .5, 4, 4.2), [1])

    def save(self, m):
        out = Path(tempfile.mkdtemp())
        (out / 'drawings.pdf').write_bytes(b'%PDF-1.4\n')
        return out, m.save(out, dict(id=m.bid))

    def test_save_requires_an_orientation(self):
        m = self.model();self.build(m, 3)
        with self.assertRaisesRegex(RuntimeError, 'Model.orient'):
            self.save(m)

    def test_declared_frame_is_checked_on_save(self):
        m = self.model();self.build(m, -3)            # north beam put at -Y
        m.orient('east', 'plan', reference=('beam_1', 'north'), skew_direction='left')
        with self.assertRaisesRegex(RuntimeError, 'orientation check failed'):
            self.save(m)

    def test_drawing_frame_is_reflected_once(self):
        # Traced with +Y toward the drawing south: north is -Y and the skew sign is reversed while building.
        m = self.model(skew=-20)
        m.orient('east', 'plan', reference=('beam_1', 'north'), skew_direction='left', built_plus_y='south')
        self.assertEqual(m.side('north'), -1)
        self.build(m, 3 * m.side('north'))
        out, manifest = self.save(m)
        beam = next(p for p in manifest['parts'] if p['id'] == 'beam_1')
        self.assertGreater(beam['bounds_m'][0][1], 0)
        self.assertEqual(manifest['skew_deg'], 20)
        self.assertIn('converted', manifest['orientation'])
        self.assertEqual(bo.check(json.loads((out / 'model_manifest.json').read_text())), [])

    def test_corrected_model_is_not_overwritten(self):
        m = self.model();self.build(m, 3)
        m.orient('east', 'plan', reference=('beam_1', 'north'), skew_direction='left')
        out = Path(tempfile.mkdtemp())
        (out / 'drawings.pdf').write_bytes(b'%PDF-1.4\n')
        (out / 'model_manifest.json').write_text(json.dumps({'review_correction_record': {}}))
        with self.assertRaisesRegex(RuntimeError, 'would discard them'):
            m.save(out, dict(id=m.bid))


if __name__ == '__main__':
    unittest.main()
