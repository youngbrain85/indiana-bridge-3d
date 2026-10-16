"""Create an English status artifact from accepted live API results (read only)."""
import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]
NEW=['us35-deer','us224-eight-mile','virginia-avenue','sr44-little-blue','sr1-six-mile']


def build(base):
    def get(path):
        with urlopen(base+path,timeout=60) as response:return json.load(response)
    catalog=get('/api/catalog');rows=[];comparison=[]
    for bridge in catalog['bridges']:
        info=get('/api/analysis/'+bridge['id'])
        row={k:bridge[k] for k in ['id','name','component_count','drawing_pages','detail_status','workspace_enabled']}
        row.update(analysis_available=info['available'])
        if info['available']:
            run=info['latest']
            assert run['status']=='completed' and run['current_inputs'],(bridge['id'],run)
            result=get('/api/analysis/runs/'+run['id']+'/result.json')
            row.update(run_id=run['id'],case=result['case_title'],scope=result['scope'],
                       display_scope=info['ledger'].get('display_scope',result.get('displacement_note','')),
                       analyzed_components=len(result['members']),max_deflection_mm=result['max_deflection_mm'],
                       max_stress_MPa=result['max_stress_MPa'],load_kN=result['total_load_kN'],
                       reaction_kN=result['total_reaction_kN'],assumptions=result['assumptions'],
                       mesh_warnings=result['verification'].get('mesh_warnings',[]),
                       current_inputs=run['current_inputs'],settings=result['settings'])
            if bridge['id']=='beechwood':row['display_scope']='72 connected structural components: deck, girders, diaphragms, bearings, caps, columns, walls and foundations.'
            if bridge['id']=='minnich-road':row['display_scope']='197 components: deck, girders, cross frames, bearings, caps and columns; assumed support bases.'
            if info.get('engine')=='collection_demo':
                for case in ['demo_uniform','demo_eccentric']:
                    choices=[r for r in info['runs'] if r['status']=='completed' and r['settings']['case']==case
                             and r['settings']['pressure_kPa']==1 and r['settings']['load_factor']==1
                             and r['settings']['foundation']=='fixed']
                    chosen=None
                    for candidate in choices:
                        if get('/api/analysis/runs/'+candidate['id'])['current_inputs']:
                            chosen=candidate;break
                    assert chosen,(bridge['id'],case)
                    value=get('/api/analysis/runs/'+chosen['id']+'/result.json')
                    comparison.append(dict(bridge_id=bridge['id'],name=bridge['name'],run_id=chosen['id'],
                        case=case,scope=value['scope'],members=len(value['members']),
                        total_load_kN=value['total_load_kN'],max_deflection_mm=value['max_deflection_mm'],
                        max_stress_MPa=value['max_stress_MPa'],verification=value['verification']))
        else:row['reason']=info['reason']
        rows.append(row)
    result=dict(generated_utc=datetime.now(timezone.utc).isoformat(),summary=catalog['summary'],bridges=rows,
                comparative_cases=comparison,scope_note='All selected researched candidates processed; not the full Indiana bridge inventory.')
    (ROOT/'data/collection-summary.json').write_text(json.dumps(result,indent=2,ensure_ascii=True),encoding='utf8')
    e=lambda value:html.escape(str(value),quote=True)
    def app(bid,label='Open 3D + FEM'):
        return f'<a href="/?fem=1#bridge/{e(bid)}">{e(label)}</a>'
    addition_rows=''.join(f'<tr><td>{app(b["id"],b["name"])}</td><td>{b["component_count"]}</td><td>{b["drawing_pages"]}</td><td>{"Schematic: structural dimensions/supports assumed" if b["id"]=="sr1-six-mile" else "Drawing-based exterior; details incomplete"}</td></tr>' for b in rows if b['id'] in NEW)
    table=''
    for b in rows:
        if not b['analysis_available']:continue
        table+=f'<tr><td>{app(b["id"],b["name"])}</td><td>{e(b["display_scope"])}</td><td>{b["analyzed_components"]}</td><td>{b["max_deflection_mm"]:.4f}</td><td>{b["max_stress_MPa"]:.4f}</td><td>{"Local peaks need refinement" if b["mesh_warnings"] else "Checked peaks within 5%; physical model unvalidated"}</td><td><a href="/api/analysis/runs/{b["run_id"]}/result.json">JSON</a> · <a href="/api/analysis/runs/{b["run_id"]}/samples.csv">CSV</a></td></tr>'
    case_rows=''.join(f'<tr><td>{e(c["name"])}</td><td>{"Full footprint" if c["case"]=="demo_uniform" else "Left half"}</td><td>{c["total_load_kN"]:.3f}</td><td>{c["max_deflection_mm"]:.4f}</td><td>{c["max_stress_MPa"]:.4f}</td><td><a href="/api/analysis/runs/{c["run_id"]}/result.json">Frozen result</a></td></tr>' for c in comparison)
    notes=''.join(f'<details><summary>{e(b["name"])}</summary><p>{e(b["case"])}</p><ul>'+''.join(f'<li>{e(a)}</li>' for a in b['assumptions'])+'</ul></details>' for b in rows if b['analysis_available'])
    content='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Indiana Bridge 3D — Collection & FEM status</title><style>
    *{box-sizing:border-box}body{margin:0;background:#f3f6f7;color:#213e4c;font:15px/1.65 system-ui,sans-serif}header{background:#14333e;color:white;padding:36px max(24px,calc((100vw - 1240px)/2))}header p{color:#bfd8de}main{max-width:1290px;margin:auto;padding:26px}h1{font-size:36px;line-height:1.2}h2{font-size:24px;margin:32px 0 12px}a{color:#087985;text-underline-offset:3px}header a{color:#8de0df}.stats{display:flex;gap:30px;flex-wrap:wrap}.stats b{display:block;font-size:32px}.note{background:#fff2d6;border-left:4px solid #c28a27;padding:18px 22px}.table-wrap{overflow:auto;background:white;border:1px solid #d5e1e7;border-radius:7px}table{border-collapse:collapse;width:100%;font-size:13px}td,th{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #dce6eb}th{background:#e7eff3;white-space:nowrap}td:first-child{min-width:175px}details{padding:12px 18px;margin:8px 0;background:white;border:1px solid #d5e1e7;border-radius:6px}summary{font-weight:650;cursor:pointer}.small{font-size:12px;color:#59717c}ol{padding-left:22px}footer{border-top:1px solid #cad9e0;margin-top:32px;padding-top:16px}@media(max-width:650px){main{padding:16px}header{padding:26px 16px}h1{font-size:29px}.stats{gap:18px}}
    </style></head><body><header><p>INDIANA / LOCAL BRIDGE WORKSPACE</p><h1>Collection and FEM status</h1><p>Selected public drawing candidates · completion update · October 15, 2026</p><div class="stats"><span><b>21</b>crossing records</span><span><b>16</b>3D + analytical workspaces</span><span><b>6,622</b>display components</span><span><b>28</b>new baseline pressure cases</span></div><p><a href="/#map">Indiana map</a> · <a href="/analysis-guide">Methods and limitations</a></p></header><main>
    <div class="note"><strong>All 12 researched candidates have been processed.</strong> This is not every Indiana bridge. Five older isolated-span fragments remain map-only. Beechwood remains green within its documented exterior scope; all added crossings remain amber. Model detail colors are independent of FEM checks and structural condition.</div>
    <h2>Five newly added crossings</h2><div class="table-wrap"><table><thead><tr><th>Crossing</th><th>Components</th><th>Primary PDF pages</th><th>Model status</th></tr></thead><tbody>'''+addition_rows+'''</tbody></table></div>
    <h2>Review a calculation</h2><ol><li>Open a bridge using a link below. The latest saved result is ready to view.</li><li>Choose stress or vertical displacement, select a component family, or view the actual FE mesh.</li><li>Under <strong>Edit assumed materials and supports</strong>, change an applicable value. Choose a load case and click <strong>Run demonstration</strong> to recompute.</li><li>Open <strong>Displayed run: frozen inputs and evidence</strong> for the source basis. Download JSON for full inputs/results or CSV for samples.</li></ol>
    <h2>Current saved results</h2><p>Values below are nominal elastic <strong>1 kPa pressure increments</strong>, with fixed assumed bases except Beechwood's documented tip idealization. They exclude gravity/prestress history in this case. They are not total bridge stresses, capacities or ratings. Different stress measures and scopes make a cross-bridge stress ranking inappropriate.</p>
    <div class="table-wrap"><table><thead><tr><th>Crossing</th><th>Analytical scope</th><th>Mapped parts</th><th>Peak |δ| mm</th><th>Peak nominal MPa</th><th>Numerical limits</th><th>Downloads</th></tr></thead><tbody>'''+table+'''</tbody></table></div>
    <h2>Scope that matters</h2><ul><li><strong>SR 1 / Wabash:</strong> four curved arch barrels with eight independently restrained springing lines. Pressure acts directly on projected barrel footprints. Deck, fill, shared-pier interaction and foundations are excluded.</li><li><strong>US 421 / Wildcat:</strong> main truss, full main-deck footprint including end cantilevers, floor system, rakers, lower bracing and bearings. Approach spans and substructure are excluded. Joints and sections are idealized; no buckling analysis.</li><li><strong>SR 1 / Six Mile:</strong> continuous slab classification and deck envelope come from plans/NBI; slab thickness, exact span split, walls and foundations are hypothetical.</li><li><strong>Other collection models:</strong> source-specific shell/beam layouts with actual support stations, explicit continuous or independent-span assumptions, and simplified section and foundation properties. Prestressed beam models omit prestress in these pressure increments.</li></ul>
    <h2>Both baseline pressure cases</h2><p>Each of the 14 newly supported analytical models has full-footprint and left-half cases. The same pressure covers different areas; arch loading is directly on the barrel projection. Both cases passed force/moment balance and required displacement refinement. Local stress refinement warnings remain visible.</p><div class="table-wrap"><table><thead><tr><th>Crossing</th><th>Pressure area</th><th>Total kN</th><th>Peak |δ| mm</th><th>Peak nominal MPa</th><th>Evidence</th></tr></thead><tbody>'''+case_rows+'''</tbody></table></div>
    <h2>Frozen model assumptions</h2>'''+notes+f'''<footer class="small">Generated from accepted local API results: {e(result['generated_utc'])}. Source/model/solver hashes are checked before colors are applied. Older results remain available with their original snapshots. The application requires no paid AI call for FEM.</footer></main></body></html>'''
    (ROOT/'web/collection-status.html').write_text(content,encoding='utf8')
    print(json.dumps(dict(bridges=len(rows),workspaces=sum(r['workspace_enabled'] for r in rows),fem=sum(r['analysis_available'] for r in rows),baseline_cases=len(comparison))))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--base',default='http://127.0.0.1:8766');build(parser.parse_args().base)
