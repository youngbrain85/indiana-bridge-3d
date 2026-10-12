"""One-time, drawing-confirmed correction, preserving unrelated GLB buffers.

Requires numpy, trimesh and manifold3d only to regenerate the two wall solids.
PDF 38 / printed sheet 37: 5 ft 6 in + 22 ft + 5 ft 6 in = 33 ft cap.
"""
import hashlib
import json
import struct
from pathlib import Path
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/bridges/beechwood'


def correct():
    mp=BASE/'model_manifest.json'; manifest=json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('geometry_correction')=='column-spacing-22ft':
        print('Already corrected.'); return
    path=BASE/'model.glb'; original=path.read_bytes()
    length=struct.unpack_from('<I',original,12)[0]; gltf=json.loads(original[20:20+length])
    binary=bytearray(original[28+length:]); before=hashlib.sha256(original).hexdigest()
    parts={p['id']:p for p in manifest['parts']}; meshes={m['name']:m for m in gltf['meshes']}
    def read(ai):
        a=gltf['accessors'][ai]; view=gltf['bufferViews'][a['bufferView']]
        dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
        count={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']]
        return np.frombuffer(binary,dtype=dtype,count=a['count']*count,offset=view.get('byteOffset',0)+a.get('byteOffset',0)).copy().reshape(-1,count)
    def append(array,kind,component):
        while len(binary)%4: binary.append(0)
        data=array.tobytes(); view=len(gltf['bufferViews'])
        gltf['bufferViews'].append(dict(buffer=0,byteOffset=len(binary),byteLength=len(data))); binary.extend(data)
        a=dict(bufferView=view,componentType=component,count=len(array),type=kind)
        if kind=='VEC3': a.update(min=array.min(axis=0).tolist(),max=array.max(axis=0).tolist())
        gltf['accessors'].append(a); return len(gltf['accessors'])-1
    solids={}; changes=[]
    for bent in (2,3):
        for side in ['L','R']:
            for kind in ['column','shaft','socket','casing']:
                cid=f'b{bent}_{kind}_{side}'; p=parts[cid]; mesh=meshes[cid]; prim=mesh['primitives'][0]
                vertices=read(prim['attributes']['POSITION']); faces=read(prim['indices']).reshape(-1,3)
                old_center=float((vertices[:,1].min()+vertices[:,1].max())/2)
                target=(11 if side=='L' else -11)*.3048
                if abs(abs(old_center)-8.75*.3048)>1e-5: raise ValueError('Unexpected original column-line position.')
                vertices[:,1]+=target-old_center
                solid=trimesh.Trimesh(vertices=vertices,faces=faces,process=False); solids[cid]=solid
                prim['attributes']['POSITION']=append(vertices.astype('<f4'),'VEC3',5126)
                p['bounds_m']=solid.bounds.round(6).tolist(); p['dimensions']['transverse_center_ft']=11 if side=='L' else -11
                p['note']=(p.get('note','')+' Corrected to 22 ft column center spacing, PDF 38 / sheet 37.').strip()
                mesh['extras'].update(p); changes.append(cid)
        cid=f'b{bent}_wall'; p=parts[cid]; mesh=meshes[cid]; prim=mesh['primitives'][0]
        x=(80 if bent==2 else 170)*.3048; height=(413.13-390)*.3048
        wall=trimesh.creation.box(extents=[.3048,22*.3048,height]); wall.apply_translation([x,0,height/2])
        wall=trimesh.boolean.difference([wall,solids[f'b{bent}_column_L'],solids[f'b{bent}_column_R']],engine='manifold')
        if not wall.is_watertight or wall.volume<=0: raise ValueError('Invalid regenerated debris wall.')
        color=read(prim['attributes']['COLOR_0'])[0]
        prim['attributes']={'POSITION':append(wall.vertices.astype('<f4'),'VEC3',5126),
                            'COLOR_0':append(np.tile(color,(len(wall.vertices),1)).astype('u1'),'VEC4',5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized']=True
        prim['indices']=append(wall.faces.reshape(-1,1).astype('<u4'),'SCALAR',5125)
        p.update(bounds_m=wall.bounds.round(6).tolist(),volume_m3=round(wall.volume,6),
                 note='Rebuilt between corrected column lines; circular-column intersections removed. PDF 38 / sheet 37.')
        p['dimensions'].update(column_center_spacing_ft=22,clear_width_at_centerline_ft=17.5)
        mesh['extras'].update(p); changes.append(cid)
    gltf['buffers'][0]['byteLength']=len(binary)
    while len(binary)%4: binary.append(0)
    encoded=json.dumps(gltf,ensure_ascii=True,separators=(',',':')).encode()
    encoded+=b' '*((-len(encoded))%4)
    out=struct.pack('<III',0x46546c67,2,28+len(encoded)+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary
    backup=ROOT/'data/fem_research'; backup.mkdir(exist_ok=True)
    (backup/'beechwood_before_column_correction.glb').write_bytes(original)
    (backup/'manifest_before_column_correction.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)
    manifest['geometry_correction']='column-spacing-22ft'; manifest['revision']='2.1-column-spacing'
    manifest['geometry_correction_record']=dict(source_pdf_page=38,printed_sheet=37,old_spacing_ft=17.5,new_spacing_ft=22,changed_parts=changes,before_glb_sha256=before,after_glb_sha256=hashlib.sha256(out).hexdigest())
    mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest['geometry_correction_record']))


if __name__=='__main__': correct()
