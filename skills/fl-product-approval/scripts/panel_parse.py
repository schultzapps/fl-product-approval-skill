"""Parse Kawneer-style load tables laid out as side-by-side panels:
   [Tributary Width | Mullion Height | value columns...]  with the height label vertically centred in a block of width rows."""
import re
NUM = re.compile(r'^\d+(\.\d+)?$')
VAL = re.compile(r'^(\d+(\.\d+)?|-)$')

def panels(words):
    """Return panel x-ranges from the 'Tributary' header words, left to right."""
    heads = sorted((w for w in words if w['text'] == 'Tributary'), key=lambda w: w['x0'])
    xs = [w['x0'] for w in heads]
    out = []
    for i, x in enumerate(xs):
        right = xs[i + 1] - 4 if i + 1 < len(xs) else 10**6
        out.append((x - 4, right))
    return out

def parse_panel(words, x0, x1, ncols, ymin=0, ymax=10**6):
    pw = [w for w in words if x0 <= w['x0'] < x1 and ymin <= w['top'] < ymax]
    hdr_h = [w for w in pw if w['text'] == 'Height']
    hdr_w = [w for w in pw if w['text'] == 'Width']
    if not hdr_h or not hdr_w:
        raise ValueError('panel header (Width/Height) not found')
    hx = (hdr_h[0]['x0'] + hdr_h[0]['x1']) / 2
    wx = (hdr_w[0]['x0'] + hdr_w[0]['x1']) / 2
    ystart = max(hdr_h[0]['bottom'], hdr_w[0]['bottom'])
    body = [w for w in pw if w['top'] > ystart - 1]
    widths = [w for w in body if abs((w['x0'] + w['x1']) / 2 - wx) < 14 and NUM.match(w['text'])]
    heights = [w for w in body if abs((w['x0'] + w['x1']) / 2 - hx) < 16 and NUM.match(w['text']) and w not in widths]
    vals = [w for w in body if (w['x0'] + w['x1']) / 2 > hx + 18 and VAL.match(w['text'])]
    widths.sort(key=lambda w: w['top'])
    rows = []
    for w in widths:
        line = sorted((v for v in vals if abs(v['top'] - w['top']) < 3), key=lambda v: v['x0'])
        if len(line) != ncols:
            raise ValueError(f"row width={w['text']} @y={w['top']:.0f} has {len(line)} values, expected {ncols}: {[v['text'] for v in line]}")
        rows.append({'width': float(w['text']), 'top': w['top'], 'vals': [None if v['text'] == '-' else float(v['text']) for v in line]})
    blocks, cur = [], []
    for r in rows:
        if cur and r['width'] <= cur[-1]['width']:
            blocks.append(cur); cur = []
        cur.append(r)
    if cur: blocks.append(cur)
    # assign each height label to the block whose y-span contains it (nearest block centre as tie-break)
    assigned = {i: [] for i in range(len(blocks))}
    for h in heights:
        cy = (h['top'] + h['bottom']) / 2
        best = min(range(len(blocks)), key=lambda i: 0 if blocks[i][0]['top'] - 6 <= cy <= blocks[i][-1]['top'] + 10 else min(abs(cy - blocks[i][0]['top']), abs(cy - blocks[i][-1]['top'])) + 1000)
        assigned[best].append(float(h['text']))
    out = []
    for i, b in enumerate(blocks):
        hs = assigned[i]
        if len(hs) != 1:
            raise ValueError(f'block {i} (widths {b[0]["width"]}..{b[-1]["width"]}) has height labels {hs}')
        out.append({'height': hs[0], 'rows': [{'width': r['width'], 'vals': r['vals']} for r in b]})
    return out
