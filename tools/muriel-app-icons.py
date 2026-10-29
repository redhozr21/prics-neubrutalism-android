"""Makes Muriel's Home-button icons (assets/app-icons/) from Riff's: every Riff logo shape in an icon (the long
M/C path, also used for its glow, mask and outline) is swapped for Muriel's sparkle (assets/mark.svg), fitted
into the same box, so the backgrounds and decorations stay and the logo is Muriel's.
Usage: python3 tools/muriel-app-icons.py <dir with Riff's NN-name.svg files> [out dir]"""
import os, re, sys

# Muriel's mark (assets/mark.svg, 1024 box): the big four-point star and the small one top right
STAR = [((500, 160), [((543.2, 476.8), (860, 520)), ((543.2, 563.2), (500, 880)), ((456.8, 563.2), (140, 520)), ((456.8, 476.8), (500, 160))]),
        ((780, 154), [((791.5, 238.5), (876, 250)), ((791.5, 261.5), (780, 346)), ((768.5, 261.5), (684, 250)), ((768.5, 238.5), (780, 154))])]
SX0, SY0, SX1, SY1 = 140, 154, 876, 880
GROW = 1.12  # the star's points are thin: a little bigger than the round logo it replaces reads the same size

def fmt(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')

def star_path(x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    s = min(w / (SX1 - SX0), h / (SY1 - SY0)) * GROW
    ox = x0 + (w - (SX1 - SX0) * s) / 2 - SX0 * s
    oy = y0 + (h - (SY1 - SY0) * s) / 2 - SY0 * s
    pt = lambda p: '%s %s' % (fmt(ox + p[0] * s), fmt(oy + p[1] * s))
    return ''.join('M' + pt(m) + ''.join('Q' + pt(c) + ' ' + pt(e) for c, e in segs) + 'Z' for m, segs in STAR)

def is_logo(d):
    return len(d) > 1500 and re.fullmatch(r'[MCZ0-9.\s,-]+', d) is not None

def swap(d):
    nums = [float(n) for n in re.findall(r'-?\d*\.?\d+', d)]
    xs, ys = nums[0::2], nums[1::2]
    return star_path(min(xs), min(ys), max(xs), max(ys))

def convert(svg):
    return re.sub(r'\bd="([^"]+)"', lambda m: 'd="%s"' % swap(m.group(1)) if is_logo(m.group(1)) else m.group(0), svg)

if __name__ == '__main__':
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '..', 'assets', 'app-icons')
    os.makedirs(out, exist_ok=True)
    for f in sorted(os.listdir(src)):
        if not re.match(r'\d\d-[\w-]+\.svg$', f):
            continue
        svg = open(os.path.join(src, f), encoding='utf-8').read()
        new = convert(svg)
        if new == svg:
            print('no logo found in', f)
            continue
        open(os.path.join(out, f), 'w', encoding='utf-8', newline='').write(new)
        print('wrote', f)
