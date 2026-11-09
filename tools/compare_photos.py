#!/usr/bin/env python3
"""
Build render-vs-photo comparison sheets for visual review (by a person or a vision model such as GPT/Codex).

    python3 tools/compare_photos.py --all
    python3 tools/compare_photos.py 07620 [--renders bridges/07620_sr28_little_wea/renders]

Reads bridges/<folder>/verification/pairs.json (render view <-> inspection photo + what to check) and writes
    bridges/<folder>/verification/compare_<view>.jpg      one pair per sheet, render left / photo right
    bridges/<folder>/verification/compare_sheet.jpg       all pairs stacked
    bridges/<folder>/verification/compare_index.json      the pairs that were produced (for scripted review)
Only Pillow is required.
"""
import argparse, json, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGES_DIR = os.path.join(ROOT, 'bridges')
PANEL_W = 960

def font(size):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
              'C:/Windows/Fonts/arial.ttf', '/System/Library/Fonts/Helvetica.ttc'):
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def fit(im, w, h):
    im = im.convert('RGB'); r = min(w / im.width, h / im.height)
    im = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
    canvas = Image.new('RGB', (w, h), (24, 24, 24)); canvas.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return canvas

def wrap(draw, text, f, width):
    words = text.split(); lines = []; cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=f) <= width: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def sheet_for(folder, renders_dir):
    vd = os.path.join(BRIDGES_DIR, folder, 'verification'); pj = os.path.join(vd, 'pairs.json')
    if not os.path.exists(pj): print(f'[{folder}] no pairs.json'); return []
    P = json.load(open(pj)); caps = {p['file']: p['caption'] for p in json.load(open(os.path.join(BRIDGES_DIR, folder, 'photos', 'index.json')))}
    f1, f2 = font(22), font(17); made = []; panels = []
    for pr in P['pairs']:
        rp = os.path.join(renders_dir, pr['view'] + '.png'); pp = os.path.join(BRIDGES_DIR, folder, 'photos', pr['photo'])
        if not os.path.exists(rp): print(f'[{folder}] render missing: {rp}'); continue
        if not os.path.exists(pp): print(f'[{folder}] photo missing: {pp}'); continue
        H = 540
        left = fit(Image.open(rp), PANEL_W, H); right = fit(Image.open(pp), PANEL_W, H)
        txt = Image.new('RGB', (2 * PANEL_W, 1), (255, 255, 255)); d = ImageDraw.Draw(txt)
        lines = wrap(d, 'CHECK: ' + pr.get('check', ''), f2, 2 * PANEL_W - 40)
        th = 40 + 26 * len(lines) + 10
        im = Image.new('RGB', (2 * PANEL_W, H + th), (250, 250, 250)); im.paste(left, (0, th)); im.paste(right, (PANEL_W, th))
        d = ImageDraw.Draw(im)
        d.text((12, 8), f"RENDER  {pr['view']}", font=f1, fill=(20, 20, 20))
        d.text((PANEL_W + 12, 8), f"PHOTO  {pr['photo']}  —  {caps.get(pr['photo'], '')}", font=f1, fill=(20, 20, 20))
        for i, ln in enumerate(lines): d.text((12, 38 + 26 * i), ln, font=f2, fill=(60, 60, 60))
        out = os.path.join(vd, f"compare_{pr['view']}.jpg"); im.save(out, quality=86); panels.append(im)
        made.append(dict(view=pr['view'], photo=pr['photo'], caption=caps.get(pr['photo'], ''), check=pr.get('check', ''), sheet=os.path.relpath(out, ROOT), render=os.path.relpath(rp, ROOT)))
    if panels:
        total = sum(p.height for p in panels) + 8 * (len(panels) - 1)
        big = Image.new('RGB', (2 * PANEL_W, total), (200, 200, 200)); y = 0
        for p in panels: big.paste(p, (0, y)); y += p.height + 8
        big.save(os.path.join(vd, 'compare_sheet.jpg'), quality=82)
    json.dump(dict(notes=P.get('notes', ''), pairs=made), open(os.path.join(vd, 'compare_index.json'), 'w'), indent=1)
    print(f'[{folder}] {len(made)} comparison sheets -> {os.path.relpath(vd, ROOT)}')
    return made

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('ids', nargs='*'); ap.add_argument('--all', action='store_true'); ap.add_argument('--renders', help='renders directory (default bridges/<folder>/renders)')
    a = ap.parse_args()
    folders = sorted(d for d in os.listdir(BRIDGES_DIR) if os.path.isdir(os.path.join(BRIDGES_DIR, d)) and d[:5].isdigit())
    if not a.all and a.ids: folders = [f for f in folders if f[:5] in a.ids or f[:5].lstrip('0') in [i.lstrip('0') for i in a.ids]]
    n = 0
    for f in folders:
        rd = a.renders or os.path.join(BRIDGES_DIR, f, 'renders')
        n += len(sheet_for(f, rd))
    return 0 if n else 1

if __name__ == '__main__':
    sys.exit(main())
