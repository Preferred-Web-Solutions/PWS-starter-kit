"""Apple-Maps-style service-area map from U.S. Census TIGER data (public domain).

A TOOL, not a required feature: use it only when a business travels to customers and a map
genuinely helps (most trades). Restaurants usually need an address block instead.

    from render_map import MapSpec, render, rasterize
    spec = MapSpec(bbox=(-82.24, 40.60, -81.56, 41.06), fill='#1c9cd8', stroke='#0b6fa4')
    coverage = spec.coverage(D, [('counties', ['Wayne']), ('places', ['Orrville city'])], grow=40, shrink=30)
    svg, labels = render(D, spec, coverage, towns=[('Wooster', -81.935, 40.805, 1), ...], shields=[...])

D is the JSON saved by fetch_tiger.js (layers: primary, secondary, local, hline, harea, places, cdp, cousub, counties).
Town tuples: (label, lon, lat, kind) with kind 1=big, 0=normal, 2=state/county label, 3=minor (hidden on narrow screens).
Shield tuples: (text, route NAME as in TIGER e.g. 'I- 71' or 'US Hwy 30', near_lon, near_lat, kind 'i'|'us'|'sr').
"""
import json, math
from dataclasses import dataclass
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

C = dict(land='#f2efe9', urban='#ebe7df', water='#a7d1f2', local='#ffffff', localcase='#dedad2',
         sec='#ffffff', seccase='#cfc9be', hw='#f8d27c', hwcase='#e0ae4f', county='#b9b2a6')


@dataclass
class MapSpec:
    bbox: tuple            # (lon0, lat0, lon1, lat1)
    fill: str              # coverage fill (brand color)
    stroke: str            # coverage outline (darker brand color)
    width: int = 1400
    fill_opacity: float = .16

    def __post_init__(self):
        lon0, lat0, lon1, lat1 = self.bbox
        self.k = math.cos(math.radians((lat0 + lat1) / 2))
        self.s = self.width / ((lon1 - lon0) * self.k)
        self.height = round(self.width * (lat1 - lat0) / ((lon1 - lon0) * self.k))

    def P(self, lon, lat):
        lon0, lat0, lon1, lat1 = self.bbox
        return ((lon - lon0) * self.k * self.s, (lat1 - lat) * self.s)

    def pct(self, lon, lat):
        x, y = self.P(lon, lat)
        return round(100 * x / self.width, 2), round(100 * y / self.height, 2)

    def px_per_mile(self):
        return self.s / 69.0 * 1  # 1 degree latitude ~ 69 miles

    def shapes(self, g):
        polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        return [Polygon([self.P(*c) for c in poly[0]], [[self.P(*c) for c in h] for h in poly[1:]]).buffer(0) for poly in polys]

    def coverage(self, D, picks, grow=60, shrink=48, round_px=20, keep=.04):
        """picks: [(layer, [NAME, ...])]. Returns SVG path data for ONE smooth combined area
        (buffered out then in so gaps between towns close; tiny islands dropped)."""
        parts = []
        for layer, names in picks:
            for f in D[layer]:
                if f['properties'].get('NAME') in names and f.get('geometry'):
                    parts += self.shapes(f['geometry'])
        u = unary_union(parts).buffer(grow, join_style=1).buffer(-shrink, join_style=1)
        u = u.buffer(-round_px, join_style=1).buffer(round_px, join_style=1)
        gs = list(u.geoms) if isinstance(u, MultiPolygon) else [u]
        big = max(g.area for g in gs)
        gs = [Polygon(g.exterior).simplify(1.5) for g in gs if g.area > keep * big]
        return ''.join('M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in g.exterior.coords) + 'Z' for g in gs)


def render(D, spec: MapSpec, cov, towns=(), shields=(), county_lines=True):
    P = spec.P
    def line(c): return 'M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in (P(*p) for p in c))
    def poly(g):
        ps = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        return ''.join(line(r) + 'Z' for p in ps for r in p)
    def lines(feats, pred=lambda f: True):
        out = ''
        for f in feats:
            g = f.get('geometry')
            if not g or not pred(f): continue
            if g['type'] == 'LineString': out += line(g['coordinates'])
            elif g['type'] == 'MultiLineString': out += ''.join(line(c) for c in g['coordinates'])
        return out
    W, H = spec.width, spec.height
    urban = ''.join(poly(f['geometry']) for f in D.get('places', []) + D.get('cdp', []) if f.get('geometry'))
    loc = lines(D.get('local', []), lambda f: f['properties'].get('MTFCC') == 'S1400')
    ramps = lines(D.get('local', []), lambda f: f['properties'].get('MTFCC') == 'S1630')
    sec = lines(D.get('secondary', [])); pri = lines(D.get('primary', []))
    cty = ''.join(poly(f['geometry']) for f in D.get('counties', []) if f.get('geometry')) if county_lines else ''
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           f'<rect width="{W}" height="{H}" fill="{C["land"]}"/>',
           f'<path d="{urban}" fill="{C["urban"]}" fill-rule="evenodd"/>',
           f'<path d="{cov}" fill="{spec.fill}" fill-opacity="{spec.fill_opacity}"/>',
           f'<path d="{lines(D.get("hline", []))}" fill="none" stroke="{C["water"]}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>',
           f'<path d="{"".join(poly(f["geometry"]) for f in D.get("harea", []) if f.get("geometry"))}" fill="{C["water"]}" stroke="{C["water"]}" stroke-width="1"/>',
           f'<path d="{cty}" fill="none" stroke="{C["county"]}" stroke-width="1.6" stroke-dasharray="7 5"/>' if cty else '',
           '<g fill="none" stroke-linecap="round" stroke-linejoin="round">',
           f'<path d="{loc}" stroke="{C["localcase"]}" stroke-width="2.2"/>',
           f'<path d="{sec}" stroke="{C["seccase"]}" stroke-width="5.5"/>',
           f'<path d="{ramps}" stroke="{C["hwcase"]}" stroke-width="3.2"/>',
           f'<path d="{pri}" stroke="{C["hwcase"]}" stroke-width="8"/>',
           f'<path d="{loc}" stroke="{C["local"]}" stroke-width="1.2"/>',
           f'<path d="{sec}" stroke="{C["sec"]}" stroke-width="3.6"/>',
           f'<path d="{ramps}" stroke="{C["hw"]}" stroke-width="1.8"/>',
           f'<path d="{pri}" stroke="{C["hw"]}" stroke-width="5.6"/>',
           '</g>',
           f'<path d="{cov}" fill="none" stroke="{spec.stroke}" stroke-width="3.4" stroke-linejoin="round"/>',
           '</svg>']
    def shield_at(name, want, layers=('primary', 'secondary')):
        best = None
        lon0, lat0, lon1, lat1 = spec.bbox
        for layer in layers:
            for f in D.get(layer, []):
                if (f['properties'].get('NAME') or '').replace(' ', '') != name.replace(' ', ''): continue
                g = f.get('geometry') or {}
                cs = g.get('coordinates', [])
                if g.get('type') == 'MultiLineString': cs = [p for part in cs for p in part]
                for lo, la in cs:
                    if lon0 + .02 < lo < lon1 - .02 and lat0 + .02 < la < lat1 - .02:
                        d = abs(lo - want[0]) + abs(la - want[1])
                        if best is None or d < best[0]: best = (d, lo, la)
        return spec.pct(best[1], best[2]) if best else spec.pct(*want)
    labels = dict(w=W, h=H,
                  towns=[dict(name=n, x=spec.pct(a, b)[0], y=spec.pct(a, b)[1], k=k) for n, a, b, k in towns],
                  shields=[dict(t=t, k=k, p=shield_at(nm, (lo, la))) for t, nm, lo, la, k in shields],
                  mile_pct=round(100 * spec.s / 69.0 / W, 3))
    return '\n'.join(s for s in svg if s), labels


def rasterize(svg_path, out_prefix, widths=(700, 1400)):
    """SVG -> WebP at each width using the preinstalled Playwright Chromium (needs Pillow for WebP)."""
    import subprocess, os, tempfile
    from PIL import Image
    js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1400,height:1400}}}});
await p.goto('file://{os.path.abspath(svg_path)}');const s=await p.$('svg');await s.screenshot({{path:'{out_prefix}-full.png'}});await b.close()}})();"""
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
        f.write(js); jsf = f.name
    subprocess.run(['node', jsf], check=True)
    im = Image.open(f'{out_prefix}-full.png').convert('RGB')
    for w in widths:
        im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(f'{out_prefix}-{w}.webp', quality=80, method=6)
    os.remove(f'{out_prefix}-full.png')
