#!/usr/bin/env python3
"""Write viewer/bridges.json from blender/bridge_gen.py (cameras, sun) + bridges/*/bridge.json (names, facts, photos).
Run after changing cameras or bridge data:  python3 tools/make_viewer_config.py"""
import json, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'blender'))
import bridge_gen as bg   # noqa: E402  (imports bpy)

def to_viewer(p):   # Blender (x, y, z) -> glTF/three (x, z, -y)
    return [round(p[0], 2), round(p[2], 2), round(-p[1], 2)]

out = {}
for bid, B in bg.BRIDGES.items():
    J = json.load(open(os.path.join(ROOT, 'bridges', B['folder'], 'bridge.json')))
    photos = json.load(open(os.path.join(ROOT, 'bridges', B['folder'], 'photos', 'index.json')))
    pairs = json.load(open(os.path.join(ROOT, 'bridges', B['folder'], 'verification', 'pairs.json')))['pairs']
    winter = B['ground'].get('season') == 'winter'
    g = J['geometry_ft']
    facts = [J['type']['main'], f"{len(g['spans'])} spans: {' + '.join(str(s['length']) for s in g['spans'])} ft ({g['structure_length']} ft structure length)",
             f"deck {g['deck_width_out_to_out']} ft out-to-out, {g['roadway_width']} ft roadway, skew {g.get('skew_deg', 0)}°",
             f"{J['type']['service_on']}; crosses {J['type']['service_under']}", f"built {J['history'][0][0]}, inspected {J['inspection']['date']}"]
    out[bid] = dict(
        id=bid, folder=B['folder'], name=J['name'], asset=J['asset_name'], county=J['location']['county'],
        model=f"../bridges/{B['folder']}/model/bridge_{bid}_lite.glb", model_full=f"../bridges/{B['folder']}/model/bridge_{bid}.glb",
        renders=f"../bridges/{B['folder']}/renders/", report=f"../bridges/{B['folder']}/report_text.txt",
        sun=dict(elev=28 if winter else 42, rot=200), winter=winter, length=sum(B['spans']), width=B['W'],
        cameras={k: dict(pos=to_viewer(v[0]), tgt=to_viewer(v[1]), lens=v[2]) for k, v in B['cameras'].items()},
        facts=facts, notes=J.get('model_notes', []),
        photos=[dict(file=f"../bridges/{B['folder']}/photos/{p['photo']}", caption=next((q['caption'] for q in photos if q['file'] == p['photo']), ''), view=p['view']) for p in pairs])
json.dump(out, open(os.path.join(ROOT, 'viewer', 'bridges.json'), 'w'), indent=1)
print('wrote viewer/bridges.json', list(out))
