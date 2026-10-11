"""Linear longitudinal beam pilot. SI throughout; tension and sagging positive.

Run only in a dedicated process: the OpenSees domain is process-global.
"""
import argparse
import hashlib
import importlib.metadata
import json
import math
import platform
from pathlib import Path

FT = 0.3048
IN = 0.0254
LBF = 4.4482216152605
PSI = LBF / IN**2
PSF = LBF / FT**2
CASES = {
    'uniform': '1 kPa full-width test load (after composite action)',
    'wearing': '35 psf future wearing surface (after composite action)',
    'girder_weight': 'Bare girder self-weight increment (before composite action)',
}


def settings(raw):
    if not isinstance(raw, dict) or set(raw) - {'case', 'end_restraint', 'load_factor'}:
        raise ValueError('Only case, end_restraint and load_factor may be supplied.')
    result = {'case': raw.get('case', 'uniform'),
              'end_restraint': raw.get('end_restraint', 'free'),
              'load_factor': raw.get('load_factor', 1.0)}
    if not isinstance(result['case'], str) or result['case'] not in CASES or result['end_restraint'] not in ('free', 'fixed'):
        raise ValueError('Unknown load case or end restraint.')
    value = result['load_factor']
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0.1 <= value <= 5:
        raise ValueError('Load multiplier must be a finite number from 0.1 to 5.')
    if result['case'] == 'girder_weight' and result['end_restraint'] != 'free':
        raise ValueError('Bare girders use individual simple bearings; select free end rotation.')
    return result


def polygon_properties(points):
    """Signed Green-theorem integrals, returned in positive physical units."""
    area2 = first_y = second_y = 0.0
    for (x, y), (u, v) in zip(points, points[1:] + points[:1]):
        cross = x*v-u*y
        area2 += cross
        first_y += (y+v)*cross
        second_y += (y*y+y*v+v*v)*cross
    area = area2/2
    centroid = first_y/(6*area)
    inertia = second_y/12-area*centroid**2
    return abs(area), centroid, abs(inertia)


def concrete_E(fc_psi, v):
    # FHWA-HIF-22-025, PDF 79 / printed 65. Output Pa.
    return 120000*v['aggregate_factor_K1']*(v['concrete_unit_weight_pcf']/1000)**2*(fc_psi/1000)**0.33*1000*PSI


def section(v, width_ft=None):
    area, y, inertia = polygon_properties([[x*IN, z*IN] for x, z in v['girder_profile_in']])
    eg = concrete_E(v['girder_fc_psi'], v)
    ed = concrete_E(v['deck_fc_psi'], v)
    h = max(p[1] for p in v['girder_profile_in'])*IN
    layers = [(area, y, inertia, eg)]
    if width_ft is not None:
        th = v['haunch_in']*IN
        td = v['deck_structural_thickness_in']*IN
        bh = 49*IN
        bd = width_ft*FT
        layers += [(bh*th, h+th/2, bh*th**3/12, ed),
                   (bd*td, h+th+td/2, bd*td**3/12, ed)]
    ea = sum(a*e for a, z, i, e in layers)
    neutral = sum(a*e*z for a, z, i, e in layers)/ea
    ei = sum(e*(i+a*(z-neutral)**2) for a, z, i, e in layers)
    return {'girder_area_m2': area, 'girder_centroid_m': y, 'girder_I_m4': inertia,
            'E_girder_Pa': eg, 'E_deck_Pa': ed, 'EA_N': ea, 'EI_Nm2': ei,
            'neutral_axis_m': neutral, 'girder_top_m': h, 'tributary_width_ft': width_ft,
            'deck_top_m': h+(v['haunch_in']+v['deck_structural_thickness_in'])*IN if width_ft is not None else None}


def beam_solution(breaks, supports, ea, ei, q, n=24, fixed_ends=False):
    """Straight 2D beam, downward q N/m; breaks include every support.

    Subdivide each break interval, including any load-bearing end overhangs.
    Recover exact in-element uniform-load moment parabola from end forces;
    recover displacement with the particular quartic as well as Hermite terms.
    """
    import openseespy.opensees as ops
    ops.wipe()
    ops.model('basic', '-ndm', 2, '-ndf', 3)
    xs = []
    longest = max(b-a for a,b in zip(breaks,breaks[1:]))
    for a, b in zip(breaks, breaks[1:]):
        # Do not over-refine the short end overhangs into ill-conditioned millimeter elements.
        count = max(1, round(n*(b-a)/longest))
        xs.extend(a+(b-a)*i/count for i in range(count))
    xs.append(breaks[-1])
    support_indices = [min(range(len(xs)), key=lambda i: abs(xs[i]-x)) for x in supports]
    for i, x in enumerate(xs):
        ops.node(i+1, x, 0)
        if i in support_indices:
            ops.fix(i+1, int(i == support_indices[0]), 1,
                    int(fixed_ends and i in (support_indices[0], support_indices[-1])))
    ops.geomTransf('Linear', 1)
    # E=1 with A=EA and I=EI keeps the transformed section dimensionally correct.
    for i in range(len(xs)-1):
        ops.element('elasticBeamColumn', i+1, i+1, i+2, ea, 1.0, ei, 1)
    ops.timeSeries('Constant', 1)
    ops.pattern('Plain', 1, 1)
    for i in range(len(xs)-1):
        ops.eleLoad('-ele', i+1, '-type', '-beamUniform', -q)
    ops.constraints('Plain')
    ops.numberer('RCM')
    ops.system('BandGeneral')
    ops.algorithm('Linear')
    ops.integrator('LoadControl', 1)
    ops.analysis('Static')
    code = ops.analyze(1)
    if code != 0:
        raise RuntimeError(f'OpenSees analysis failed ({code}).')
    ops.reactions()
    reactions = [{'x_m': xs[i], 'vertical_N': ops.nodeReaction(i+1, 2),
                  'moment_Nm': ops.nodeReaction(i+1, 3)} for i in support_indices]
    samples = []
    for i, (a, b) in enumerate(zip(xs, xs[1:])):
        length = b-a
        forces = ops.eleResponse(i+1, 'localForce')
        d0, d1 = ops.nodeDisp(i+1), ops.nodeDisp(i+2)
        # Include the shear-zero station, so bending moment extrema are not missed.
        ts = {0.0, .25, .5, .75, 1.0}
        if q and 0 < forces[1]/q < length:
            ts.add(forces[1]/q/length)
        for t in sorted(ts):
            s = t*length
            moment = -forces[2]+forces[1]*s-q*s*s/2
            hermite = ((1-3*t*t+2*t**3)*d0[1]+length*(t-2*t*t+t**3)*d0[2]
                       +(3*t*t-2*t**3)*d1[1]+length*(-t*t+t**3)*d1[2])
            displacement = hermite-q*s*s*(length-s)**2/(24*ei)
            samples.append({'x_m': a+s, 'moment_Nm': moment,
                            'shear_N': forces[1]-q*s, 'vertical_m': displacement})
    total_load = q*(breaks[-1]-breaks[0])
    load_moment = total_load*(breaks[0]+breaks[-1])/2
    vertical = sum(r['vertical_N'] for r in reactions)
    moment_reaction = sum(r['vertical_N']*r['x_m']+r['moment_Nm'] for r in reactions)
    result = {'samples': samples, 'reactions': reactions, 'load_N': total_load,
              'node_count': len(xs), 'element_count': len(xs)-1,
              'force_error': abs(vertical-total_load)/max(abs(total_load), 1),
              'moment_error': abs(moment_reaction-load_moment)/max(abs(load_moment), abs(total_load*(breaks[-1]-breaks[0])), 1)}
    ops.wipe()
    return result


def peak(sol, field):
    return max(abs(p[field]) for p in sol['samples'])


def benchmarks():
    l, q, ei = 12.0, 17000.0, 2.4e9
    checks = []
    def check(name, actual, expected, tolerance=1e-6):
        error = abs(actual-expected)/max(abs(expected), 1e-12)
        checks.append({'name': name, 'actual': actual, 'expected': expected,
                       'relative_error': error, 'tolerance': tolerance, 'passed': error < tolerance})
    for fixed in (False, True):
        s = beam_solution([0,l], [0,l], 8e9, ei, q, 8, fixed)
        prefix = 'Fixed beam' if fixed else 'Simple beam'
        check(prefix+' midspan deflection (m)', peak(s,'vertical_m'), q*l**4/(384*ei)*(1 if fixed else 5))
        check(prefix+' peak moment (Nm)', peak(s,'moment_Nm'), q*l*l/(12 if fixed else 8))
        check(prefix+' left reaction (N)', s['reactions'][0]['vertical_N'], q*l/2)
    c = beam_solution([0,l,2*l], [0,l,2*l], 8e9, ei, q, 8)
    at_pier = next(p for p in c['samples'] if abs(p['x_m']-l)<1e-9)
    check('Two-span internal hogging moment (Nm)', at_pier['moment_Nm'], -q*l*l/8)
    check('Two-span middle reaction (N)', c['reactions'][1]['vertical_N'], 5*q*l/4)
    check('Rectangle polygon area (m2)', polygon_properties([[0,0],[2,0],[2,3],[0,3]])[0], 6)
    check('Rectangle centroidal inertia (m4)', polygon_properties([[0,0],[2,0],[2,3],[0,3]])[2], 4.5)
    if not all(c['passed'] for c in checks):
        raise RuntimeError('Analytical benchmark failed.')
    return checks


def run_model(ledger, options, n=24):
    v = ledger['values']
    case = options['case']
    composite = case != 'girder_weight'
    widths = [(v['deck_width_ft']-3*v['girder_spacing_ft'])/2+v['girder_spacing_ft']/2,
              v['girder_spacing_ft'], v['girder_spacing_ft'],
              (v['deck_width_ft']-3*v['girder_spacing_ft'])/2+v['girder_spacing_ft']/2]
    load_widths = widths.copy()
    if case == 'wearing':
        delta = (v['deck_width_ft']-v['roadway_width_ft'])/2
        load_widths[0] -= delta
        load_widths[-1] -= delta
    members, checks, all_reactions = [], [], []
    total_load = 0.0
    node_count = element_count = 0
    for line in range(4):
        sec = section(v, widths[line] if composite else None)
        q = (v['test_pressure_kPa']*1000 if case == 'uniform' else v['wearing_psf']*PSF)*load_widths[line]*FT
        if not composite:
            q = sec['girder_area_m2']*v['concrete_unit_weight_pcf']*LBF/FT**3
        q *= options['load_factor']
        blocks = [None] if composite else range(3)
        for block in blocks:
            if composite:
                supports = [x*FT for x in v['bent_x_ft']]
                breaks = supports
            else:
                supports = [x*FT for x in v['bearing_x_ft'][block]]
                breaks = sorted(set([x*FT for x in v['beam_extents_ft'][block]]+supports))
            sol = beam_solution(breaks, supports, sec['EA_N'], sec['EI_Nm2'], q, n, options['end_restraint']=='fixed')
            checks.append({'line': line+1, 'span': block, 'force_error': sol['force_error'], 'moment_error': sol['moment_error']})
            total_load += sol['load_N']
            node_count += sol['node_count']
            element_count += sol['element_count']
            all_reactions.extend(dict(r, line=line+1, span=block) for r in sol['reactions'])
            for span in (range(3) if composite else [block]):
                lo, hi = (v['bent_x_ft'][span:span+2] if composite else v['beam_extents_ft'][span])
                samples = []
                # Deduplicate the coincident element endpoints, retaining their equal moment/displacement.
                previous_x = None
                for p in sol['samples']:
                    if not lo*FT-1e-8 <= p['x_m'] <= hi*FT+1e-8 or (previous_x is not None and abs(p['x_m']-previous_x)<1e-10):
                        continue
                    previous_x = p['x_m']
                    curvature = p['moment_Nm']/sec['EI_Nm2']
                    top = -sec['E_girder_Pa']*curvature*(sec['girder_top_m']-sec['neutral_axis_m'])/1e6
                    bottom = sec['E_girder_Pa']*curvature*sec['neutral_axis_m']/1e6
                    samples.append({'x_m': p['x_m'], 'deflection_mm': -p['vertical_m']*1000,
                                    'moment_kNm': p['moment_Nm']/1000,
                                    'top_MPa': top, 'bottom_MPa': bottom,
                                    'stress_MPa': max(abs(top), abs(bottom))})
                mid = f'beechwood:girder_{"ABC"[span]}{line+1}'
                hotspot = max(samples, key=lambda p:p['stress_MPa'])
                members.append({'component_id': mid, 'line': line+1, 'span': 'ABC'[span],
                                'section': sec, 'line_load_Npm': q, 'samples': samples,
                                'peak': hotspot, 'max_deflection_mm': max(abs(p['deflection_mm']) for p in samples)})
    return {'members': members, 'reactions': all_reactions, 'equilibrium': checks,
            'total_load_kN': total_load/1000, 'total_reaction_kN': sum(r['vertical_N'] for r in all_reactions)/1000,
            'node_count': node_count, 'element_count': element_count,
            'max_stress_MPa': max(m['peak']['stress_MPa'] for m in members),
            'max_deflection_mm': max(m['max_deflection_mm'] for m in members)}


def solve(snapshot):
    import openseespy.opensees as ops
    ledger = snapshot['ledger']
    options = settings(snapshot['settings'])
    tests = benchmarks()
    coarse = run_model(ledger, options, 24)
    fine = run_model(ledger, options, 48)
    convergence = []
    for field in ('max_stress_MPa','max_deflection_mm'):
        error = abs(coarse[field]-fine[field])/max(fine[field],1e-12)
        convergence.append({'quantity': field, 'coarse': coarse[field], 'fine': fine[field], 'relative_change': error, 'tolerance': .01, 'passed': error < .01})
    equilibrium_ok = all(max(c['force_error'], c['moment_error']) < 1e-7 for c in fine['equilibrium'])
    if not equilibrium_ok or not all(c['passed'] for c in convergence):
        raise RuntimeError('Equilibrium or mesh-refinement acceptance criterion failed.')
    v = ledger['values']
    sec = section(v)
    package_versions = {}
    for name in ['openseespy','openseespywin','openseespylinux','openseespymac']:
        try:
            package_versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            pass
    fine.update({'schema_version':1, 'bridge_id':'beechwood', 'case':options['case'],
                 'case_title':CASES[options['case']], 'settings':options, 'scope':'incremental_nominal_beam_response',
                 'solver':{'name':'OpenSees', 'version':ops.version(), 'packages':package_versions, 'python':platform.python_version(), 'platform':platform.platform()},
                 'units':{'length':'m','force':'kN','moment':'kN m','stress':'MPa','displacement':'mm'},
                 'sign_convention':'Girder normal stress: positive tension, negative compression; deflection positive down; moment positive sagging.',
                 'verification':{'passed':True,'field_validated':False,'benchmarks':tests,'mesh_refinement':convergence,'equilibrium_tolerance':1e-7},
                 'quantities':{'girder_area_m2':sec['girder_area_m2'], 'girder_I_m4':sec['girder_I_m4'],
                               'girder_volume_m3':sec['girder_area_m2']*4*sum(b-a for a,b in v['beam_extents_ft'])*FT,
                               'deck_gross_prism_m3':v['deck_width_ft']*v['deck_length_ft']*FT**2*v['deck_total_thickness_in']*IN,
                               'note':'Derived nominal prisms, not procurement takeoffs; excludes joints, local end details and embedded steel. Deck quantity is not a load in these cases.'},
                 'assumptions':ledger['assumptions'], 'snapshot':snapshot})
    if options['case'] != 'girder_weight':
        alternative = dict(options, end_restraint='fixed' if options['end_restraint']=='free' else 'free')
        sensitivity = run_model(ledger, alternative, 48)
        if any(max(c['force_error'], c['moment_error']) >= 1e-7 for c in sensitivity['equilibrium']):
            raise RuntimeError('Alternative support equilibrium failed.')
        fine['support_sensitivity'] = {k:sensitivity[k] for k in ('max_stress_MPa','max_deflection_mm','total_load_kN','total_reaction_kN')}
        fine['support_sensitivity']['end_restraint'] = alternative['end_restraint']
    return fine


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding='utf-8'))
    if hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != payload['solver_code_sha256']:
        raise RuntimeError('Solver source changed after the input snapshot was created.')
    result = solve(payload)
    encoded = json.dumps(result, ensure_ascii=True, allow_nan=False, separators=(',',':'))
    temp = args.output.with_suffix('.tmp')
    temp.write_text(encoded, encoding='utf-8')
    temp.replace(args.output)
    print(json.dumps({k:result[k] for k in ['max_stress_MPa','max_deflection_mm','total_load_kN','total_reaction_kN']}))
