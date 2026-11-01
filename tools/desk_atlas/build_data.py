"""Build SVG map fragments and chart data for the Amazon desk atlas."""
import io, json, math, os, sys, warnings, zipfile
from pathlib import Path

warnings.filterwarnings("ignore")

import geopandas as gp
import numpy as np
import pandas as pd
from shapely.geometry import Point, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
# Uses the legacy Drive data layout; point FINESST_ATLAS_DATA elsewhere on another machine.
ROOT = Path(os.environ.get("FINESST_ATLAS_DATA", REPO / "docs/proposal/2025/data"))
OUT = HERE / "build"
OUT.mkdir(exist_ok=True)

CAM = ROOT / "GIS/CD06_Camrex_1086/CD06_Camrex_1086/data"
sub = gp.read_file(CAM / "amztrbbas_v/amztrbbas_v/amztrbbas_v.shp").set_crs(4326, allow_override=True)
basin = unary_union(sub.geometry.buffer(0))
ne = gp.read_file(ROOT / "GIS/naturalearth/ne_50m_admin_0_countries.geojson")

# --- water-type classes -------------------------------------------------------
# sub-basin ids identified by towns that sit on each river (see notes in reply)
WHITE_SB = {16: "Madeira", 20: "Purus", 25: "Juruá", 24: "Japurá", 27: "Içá", 30: "Napo", 33: "Ucayali"}
BLACK_SB = {18: "Negro"}
CLEAR_SB = {9: "Tapajós", 5: "Xingu", 11: "Trombetas"}
NAME_OTHER = {"Rio Branco", "Guapore River"}
NAME_WHITE = {"Beni River", "Madre de Dios River", "Maranon River", "Ucayali River", "Amazon river", "Amazon River"}

sw = gp.read_file(ROOT / "GIS/SWORD_v17_shp/shp/SA/sa_sword_reaches_hb62_v17.shp")
sw = sw[sw["type"] != 6].copy()
pts = gp.GeoDataFrame(sw[["reach_id"]], geometry=gp.points_from_xy(sw.x, sw.y), crs=4326)
j = gp.sjoin(pts, sub[["BASINID", "geometry"]], how="left", predicate="within")
j = j[~j.index.duplicated()]
sw["sb"] = j["BASINID"]
sw = sw[sw.sb.notna()].copy()
sw["sb"] = sw.sb.astype(int)
AMAZON = {"Amazon river", "Amazon River"}
# main stem (and its side channels); the Negro and Madeira mouths are not main stem
sw["main"] = (sw.river_name.isin(AMAZON) | (sw.facc >= 1.4e6)
              | ((sw.facc >= 7e5) & ~sw.sb.isin([18, 16])))
sbmax = sw[~sw.main].groupby("sb").facc.max()
sw["trunk"] = ~sw.main & (sw.facc >= 0.25 * sw.sb.map(sbmax))


def wclass(r):
    if r.river_name in NAME_OTHER:
        return "other"
    if r.main or r.river_name in NAME_WHITE:
        return "white"
    if r.trunk:
        if r.sb in WHITE_SB:
            return "white"
        if r.sb in BLACK_SB:
            return "black"
        if r.sb in CLEAR_SB:
            return "clear"
    return "other"


sw["wc"] = sw.apply(wclass, axis=1)
print("class counts:", sw.wc.value_counts().to_dict())
print("Trombetas classes:", sw[sw.river_name == "Rio Trombetas"].wc.value_counts().to_dict(), "sbmax11", sbmax.get(11))


# --- projection helpers -------------------------------------------------------
class Proj:
    def __init__(self, lon0, lon1, lat0, lat1, s):
        self.lon0, self.lon1, self.lat0, self.lat1, self.s = lon0, lon1, lat0, lat1, s
        self.w = round((lon1 - lon0) * s)
        self.h = round((lat1 - lat0) * s)
        self.box = box(lon0, lat0, lon1, lat1)

    def xy(self, lon, lat):
        return (lon - self.lon0) * self.s, (self.lat1 - lat) * self.s

    def path(self, geom, closed=False):
        out = []
        for part in getattr(geom, "geoms", [geom]):
            rings = [part.exterior, *part.interiors] if part.geom_type == "Polygon" else [part]
            for ring in rings:
                cs = list(ring.coords)
                if len(cs) < 2:
                    continue
                p = [self.xy(x, y) for x, y, *_ in cs]
                seg = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in p)
                out.append(seg + ("Z" if closed and part.geom_type == "Polygon" else ""))
        return "".join(out)


def poly_paths(P, geoms, tol):
    d = []
    for g in geoms:
        g = g.intersection(P.box)
        if g.is_empty:
            continue
        g = g.simplify(tol, preserve_topology=True)
        if g.geom_type in ("Polygon", "MultiPolygon"):
            d.append(P.path(g, closed=True))
        elif g.geom_type == "GeometryCollection":
            for gg in g.geoms:
                if gg.geom_type in ("Polygon", "MultiPolygon"):
                    d.append(P.path(gg, closed=True))
    return "".join(d)


def line_paths(P, geoms, tol):
    d = []
    for g in geoms:
        g = g.intersection(P.box)
        if g.is_empty:
            continue
        g = g.simplify(tol)
        d.append(P.path(g))
    return "".join(d)


def bounds_lines(P, polys, tol):
    return line_paths(P, [p.boundary for p in polys], tol)


def angle_at(P, geom, lon, lat):
    """local direction of a line near (lon, lat), in screen degrees, kept readable"""
    g = geom if geom.geom_type == "LineString" else max(geom.geoms, key=lambda q: q.length)
    d = g.project(Point(lon, lat))
    a = g.interpolate(max(0, d - 0.15))
    b = g.interpolate(min(g.length, d + 0.15))
    x0, y0 = P.xy(a.x, a.y)
    x1, y1 = P.xy(b.x, b.y)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    if ang > 90:
        ang -= 180
    if ang < -90:
        ang += 180
    return ang


def river_label(P, cand, lon, lat, text, offset=7, cls="lbl-river", max_ang=60):
    """place a label on the reach nearest (lon, lat) from candidate reaches"""
    c = cand.copy()
    c["dist"] = c.geometry.distance(Point(lon, lat))
    r = c.sort_values("dist").iloc[0]
    # merge neighbours for a smoother direction estimate
    near = c[c.geometry.distance(r.geometry) < 0.4]
    geom = unary_union(near.geometry.values).simplify(0.02)
    from shapely.ops import linemerge
    try:
        geom = linemerge(geom)
    except Exception:
        pass
    p = geom.interpolate(geom.project(Point(lon, lat)))
    ang = angle_at(P, geom, p.x, p.y)
    ang = max(-max_ang, min(max_ang, ang))
    x, y = P.xy(p.x, p.y)
    nx, ny = -math.sin(math.radians(ang)), math.cos(math.radians(ang))
    x, y = x - nx * offset, y - ny * offset
    return f'<text class="{cls}" transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f})" text-anchor="middle">{text}</text>'


def bins(width, edges, widths):
    for e, w in zip(edges, widths):
        if width < e:
            return w
    return widths[-1]


def river_layers(P, df, edges, widths, tol):
    out = []
    for wc in ["other", "clear", "black", "white"]:
        sel = df[df.wc == wc]
        for e_w in sorted(set(widths)):
            s2 = sel[sel.width.apply(lambda w: bins(w, edges, widths)) == e_w]
            if s2.empty:
                continue
            d = line_paths(P, s2.geometry.values, tol)
            out.append(f'<path class="riv riv-{wc}" stroke-width="{e_w}" d="{d}"/>')
    return "\n".join(out)


def town(P, lon, lat, name, dx=5, dy=-5, anchor="start", cls="lbl-town", mark="dot"):
    x, y = P.xy(lon, lat)
    m = {
        "dot": f'<circle class="mk-town" cx="{x:.1f}" cy="{y:.1f}" r="3"/>',
        "cap": f'<rect class="mk-town" x="{x-3.5:.1f}" y="{y-3.5:.1f}" width="7" height="7" transform="rotate(45 {x:.1f} {y:.1f})"/>',
        "none": "",
    }[mark]
    return m + f'<text class="{cls}" x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{anchor}">{name}</text>'


def text(P, lon, lat, s, cls, anchor="middle", rot=0):
    x, y = P.xy(lon, lat)
    t = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else ""
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}"{t}>{s}</text>'


# ============================== MAP A: basin ==================================
A = Proj(-81.5, -46.0, -21.0, 6.5, 30)
sa = ne[ne.intersects(A.box)]
la = []
la.append(f'<rect class="ocean" x="0" y="0" width="{A.w}" height="{A.h}"/>')
la.append(f'<path class="land" d="{poly_paths(A, sa.geometry.values, 0.03)}"/>')
la.append(f'<path class="basin" d="{poly_paths(A, [basin], 0.02)}"/>')
la.append(f'<path class="border" d="{bounds_lines(A, sa.geometry.values, 0.03)}"/>')
la.append(f'<path class="subbasin" d="{bounds_lines(A, sub.geometry.values, 0.03)}"/>')
la.append(f'<path class="basin-edge" d="{bounds_lines(A, [basin], 0.02)}"/>')
y0 = A.xy(0, 0)[1]
la.append(f'<line class="equator" x1="0" y1="{y0:.1f}" x2="{A.w}" y2="{y0:.1f}"/>')
la.append(f'<text class="lbl-grid" x="6" y="{y0-5:.1f}">Equator 0°</text>')
ra = sw[(sw.width >= 200) | (sw.wc != "other") & (sw.width >= 100)]
la.append(river_layers(A, ra, [300, 800, 1600, 3000], [0.6, 1.0, 1.5, 2.1, 2.8], 0.012))
# study corridor box
x0, yA = A.xy(-70.6, -1.4)
x1, yB = A.xy(-59.4, -5.1)
la.append(f'<rect class="corridor" x="{x0:.1f}" y="{yA:.1f}" width="{x1-x0:.1f}" height="{yB-yA:.1f}"/>')
la.append(f'<text class="lbl-corridor" x="{x0:.1f}" y="{yB+15:.1f}">Study corridor (Plate 2)</text>')

main = sw[sw.wc == "white"]
L = []
L.append(river_label(A, main[(main.facc > 2_000_000)], -58.4, -3.0, "Amazonas", 9))
L.append(river_label(A, main[(main.facc > 700_000) & (main.x < -61)], -67.4, -3.0, "Solimões", 9))
for sb, (lon, lat, name, off) in {
    18: (-64.3, -0.55, "Negro", 8), 16: (-62.0, -6.3, "Madeira", 9), 20: (-66.3, -7.6, "Purus", 8),
    25: (-69.2, -6.2, "Juruá", 8), 24: (-71.5, -0.9, "Japurá / Caquetá", 8), 27: (-72.6, -1.8, "Içá / Putumayo", -8),
    30: (-75.6, -1.4, "Napo", 8), 33: (-74.6, -9.4, "Ucayali", 9), 9: (-56.6, -6.5, "Tapajós", 8),
    5: (-52.6, -6.5, "Xingu", 8), 11: (-57.0, 0.3, "Trombetas", 8),
}.items():
    cand = sw[(sw.sb == sb) & sw.trunk]
    L.append(river_label(A, cand, lon, lat, name, off, max_ang=50))
mar = sw[sw.river_name == "Maranon River"]
L.append(river_label(A, mar, -76.2, -4.6, "Marañón", 8))
bra = sw[sw.river_name == "Rio Branco"]
L.append(river_label(A, bra, -61.0, 1.3, "Branco", 8))
la += L
for lon, lat, n, dx, dy, an, mk in [
    (-73.25, -3.75, "Iquitos", -6, -6, "end", "dot"), (-69.94, -4.25, "Tabatinga", -6, 13, "end", "dot"),
    (-64.71, -3.35, "Tefé", 0, 15, "middle", "dot"), (-60.02, -3.12, "Manaus", 6, 14, "start", "dot"),
    (-54.71, -2.44, "Santarém", 0, 15, "middle", "dot"), (-48.49, -1.46, "Belém", 6, 4, "start", "dot"),
    (-51.07, 0.03, "Macapá", 6, -5, "start", "dot"), (-63.90, -8.76, "Porto Velho", 6, 4, "start", "dot"),
    (-60.67, 2.82, "Boa Vista", 6, 4, "start", "dot"), (-78.47, -0.18, "Quito", 6, 12, "start", "cap"),
    (-77.04, -12.05, "Lima", -6, 4, "end", "cap"), (-74.07, 4.71, "Bogotá", 6, 4, "start", "cap"),
    (-68.15, -16.50, "La Paz", 6, 4, "start", "cap"), (-71.97, -13.53, "Cusco", -6, 4, "end", "dot"),
]:
    la.append(town(A, lon, lat, n, dx, dy, an, mark=mk))
for lon, lat, s in [(-55.0, -16.8, "BRAZIL"), (-75.2, -10.6, "PERU"), (-72.6, 2.6, "COLOMBIA"),
                    (-79.3, -2.4, "ECUADOR"), (-64.6, -15.6, "BOLIVIA"), (-65.5, 5.6, "VENEZUELA"),
                    (-58.9, 4.6, "GUYANA"), (-55.9, 3.7, "SURINAME"), (-52.9, 3.0, "FR. GUIANA")]:
    la.append(text(A, lon, lat, s, "lbl-country"))
la.append(text(A, -48.6, 4.4, "Atlantic Ocean", "lbl-sea"))
la.append(text(A, -80.0, -15.0, "Pacific Ocean", "lbl-sea", rot=-60))
la.append(text(A, -76.9, -7.6, "A N D E S", "lbl-relief", rot=62))
la.append(text(A, -54.3, -13.6, "Brazilian Shield", "lbl-relief"))
la.append(text(A, -57.6, 1.2, "Guiana Shield", "lbl-relief"))
# scale bar 500 km at ~ -18 lat
kmdeg = 111.32 * math.cos(math.radians(18))
sx, sy = A.xy(-80.6, -19.8)
sl = 500 / kmdeg * A.s
la.append(f'<g class="scale"><line x1="{sx:.1f}" y1="{sy:.1f}" x2="{sx+sl:.1f}" y2="{sy:.1f}"/>'
          f'<line x1="{sx:.1f}" y1="{sy-4:.1f}" x2="{sx:.1f}" y2="{sy+4:.1f}"/><line x1="{sx+sl:.1f}" y1="{sy-4:.1f}" x2="{sx+sl:.1f}" y2="{sy+4:.1f}"/>'
          f'<text x="{sx:.1f}" y="{sy-8:.1f}">0</text><text x="{sx+sl:.1f}" y="{sy-8:.1f}" text-anchor="middle">500 km</text></g>')
svgA = (f'<svg class="map" viewBox="0 0 {A.w} {A.h}" role="img" aria-labelledby="mapA-t">'
        f'<title id="mapA-t">Amazon basin with major rivers coloured by water type</title>' + "\n".join(la) + "</svg>")
(OUT / "mapA.svg").write_text(svgA, encoding="utf-8")
print("mapA", A.w, A.h, round(len(svgA) / 1024), "KB")

# ============================== MAP B: corridor ===============================
B = Proj(-70.6, -59.4, -5.1, -1.4, 100)
rb = sw[sw.intersects(B.box) & (sw.width >= 60)].copy()
lakes = gp.read_file(ROOT / "GIS/HydroLAKES_polys_v10_shp/HydroLAKES_polys_v10_shp/HydroLAKES_polys_v10.shp",
                     bbox=(-70.6, -5.1, -59.4, -1.4), columns=["Hylak_id", "Lake_name", "Lake_area"])
lakes = lakes[lakes.Lake_area >= 3]
print("lakes in corridor:", len(lakes), lakes.sort_values("Lake_area", ascending=False).head(12)[["Lake_name", "Lake_area"]].to_dict("records"))
lb = []
lb.append(f'<rect class="land" x="0" y="0" width="{B.w}" height="{B.h}"/>')
lb.append(f'<path class="subbasin" d="{bounds_lines(B, sub.geometry.values, 0.01)}"/>')
lb.append(f'<path class="lake" d="{poly_paths(B, lakes.geometry.values, 0.004)}"/>')
# rivers at true width: 1 px ~ 1.1 km at this scale
out = []
for wc in ["other", "clear", "black", "white"]:
    sel = rb[rb.wc == wc]
    for wpx in [0.6, 0.9, 1.3, 1.8, 2.4, 3.2, 4.2]:
        def pick(w):
            v = max(0.6, w / 1100)
            return min([0.6, 0.9, 1.3, 1.8, 2.4, 3.2, 4.2], key=lambda q: abs(q - v))
        s2 = sel[sel.width.apply(pick) == wpx]
        if len(s2):
            out.append(f'<path class="riv riv-{wc}" stroke-width="{wpx}" d="{line_paths(B, s2.geometry.values, 0.003)}"/>')
lb += out
LB = []
mainB = rb[(rb.wc == "white") & (rb.facc > 700_000)]
LB.append(river_label(B, mainB, -68.9, -3.6, "Rio Solimões", 11, "lbl-river lg"))
LB.append(river_label(B, mainB, -62.4, -3.75, "Rio Solimões", 11, "lbl-river lg"))
for sb, lon, lat, name, off in [(18, -61.3, -2.3, "Rio Negro", 12), (20, -61.9, -4.6, "Rio Purus", 9),
                                (25, -66.6, -3.9, "Rio Juruá", 8), (24, -67.6, -1.62, "Rio Japurá", 8),
                                (27, -69.0, -2.6, "Rio Içá", 8), (29, -70.1, -4.75, "Rio Javari", -8),
                                (26, -67.6, -3.9, "Rio Jutaí", 8), (16, -59.75, -4.4, "Rio Madeira", 8),
                                (23, -64.95, -4.45, "Rio Tefé", 8)]:
    cand = rb[(rb.sb == sb) & rb.trunk]
    if len(cand):
        LB.append(river_label(B, cand, lon, lat, name, off))
lb += LB
bal = lakes[lakes.Lake_name == "Balbina Reservoir"]
if len(bal):
    rp = bal.geometry.iloc[0].intersection(B.box).representative_point()
    lb.append(text(B, rp.x - 0.05, rp.y + 0.05, "Balbina Res.", "lbl-lake", anchor="end"))
for lon, lat, s, cls in [(-64.80, -3.55, "Lago Tefé", "lbl-lake"), (-63.36, -4.38, "Lago Coari", "lbl-lake"),
                         (-60.26, -3.53, "Lago Janauacá", "lbl-lake"), (-65.55, -2.40, "Mamirauá", "lbl-region"),
                         (-65.55, -2.53, "Reserve", "lbl-region")]:
    lb.append(text(B, lon, lat, s, cls))
# meeting of the waters
mx, my = B.xy(-59.87, -3.14)
lb.append(f'<text class="lbl-note" x="{mx:.1f}" y="{my-14:.1f}" text-anchor="middle">Meeting of</text>'
          f'<text class="lbl-note" x="{mx:.1f}" y="{my-4:.1f}" text-anchor="middle">the Waters</text>')
# in-situ 2023 sites (Fleischmann et al. 2025 table S1)
for lon, lat in [(-64.7304, -3.3416), (-63.2294, -4.0291), (-60.2294, -3.3840)]:
    x, y = B.xy(lon, lat)
    lb.append(f'<circle class="mk-site" cx="{x:.1f}" cy="{y:.1f}" r="4.5"/>')
# towns
for lon, lat, n, dx, dy, an in [(-69.94, -4.25, "Tabatinga / Leticia", 8, 4, "start"), (-70.03, -4.38, "Benjamin Constant", 6, 16, "start"),
                                (-67.94, -3.10, "Sto. Antônio do Içá", 0, -9, "middle"), (-66.09, -2.51, "Fonte Boa", -7, 4, "end"),
                                (-64.71, -3.35, "Tefé", 7, -6, "start"), (-63.14, -4.09, "Coari", 7, 13, "start"),
                                (-62.06, -3.84, "Codajás", 0, 15, "middle"), (-60.62, -3.30, "Manacapuru", -6, 15, "end"),
                                (-60.02, -3.12, "Manaus", 0, -22, "middle")]:
    lb.append(town(B, lon, lat, n, dx, dy, an))
# gauges (ANA, plotted at the town) and INMET stations
for lon, lat, code in [(-69.94, -4.25, "10100000"), (-67.94, -3.10, ""), (-66.09, -2.51, ""), (-60.62, -3.30, "14100000")]:
    x, y = B.xy(lon, lat)
    lb.append(f'<path class="mk-gauge" d="M{x:.1f} {y-12:.1f} l5 -9 l-10 0 Z"/>')
    if code:
        lb.append(f'<text class="lbl-code" x="{x:.1f}" y="{y-24:.1f}" text-anchor="middle">{code}</text>')
for lon, lat, code, dx in [(-70.03, -4.38, "82410", -16), (-64.71, -3.35, "82317", 6), (-60.02, -3.12, "82331", 6)]:
    x, y = B.xy(lon, lat)
    anc, tx = ("end", x + dx - 3) if dx < 0 else ("start", x + dx + 10)
    lb.append(f'<rect class="mk-met" x="{x+dx:.1f}" y="{y+4:.1f}" width="7" height="7"/>'
              f'<text class="lbl-code" x="{tx:.1f}" y="{y+11:.1f}" text-anchor="{anc}">{code}</text>')
# flow arrow + scale
fx, fy = B.xy(-68.0, -4.75)
lb.append(f'<g class="flow"><line x1="{fx:.1f}" y1="{fy:.1f}" x2="{fx+60:.1f}" y2="{fy:.1f}"/><path d="M{fx+60:.1f} {fy:.1f} l-7 -4 l0 8 Z"/>'
          f'<text x="{fx+30:.1f}" y="{fy-6:.1f}" text-anchor="middle">flow</text></g>')
kmdeg = 111.32 * math.cos(math.radians(3.3))
sx, sy = B.xy(-69.4, -4.98)
sl = 100 / kmdeg * B.s
lb.append(f'<g class="scale"><line x1="{sx:.1f}" y1="{sy:.1f}" x2="{sx+sl:.1f}" y2="{sy:.1f}"/>'
          f'<line x1="{sx:.1f}" y1="{sy-4:.1f}" x2="{sx:.1f}" y2="{sy+4:.1f}"/><line x1="{sx+sl:.1f}" y1="{sy-4:.1f}" x2="{sx+sl:.1f}" y2="{sy+4:.1f}"/>'
          f'<text x="{sx:.1f}" y="{sy-8:.1f}" text-anchor="middle">0</text><text x="{sx+sl:.1f}" y="{sy-8:.1f}" text-anchor="middle">100 km</text></g>')
svgB = (f'<svg class="map" viewBox="0 0 {B.w} {B.h}" role="img" aria-labelledby="mapB-t">'
        f'<title id="mapB-t">Central Solimões corridor from Tabatinga to Manaus</title>' + "\n".join(lb) + "</svg>")
(OUT / "mapB.svg").write_text(svgB, encoding="utf-8")
print("mapB", B.w, B.h, round(len(svgB) / 1024), "KB")

# ============================== hydrograph ====================================
z = zipfile.ZipFile(ROOT / "in_situ/Estacao_10100000_TXT_2025-01-29T20_28_41.808Z.zip")
t = z.read("10100000_Vazoes.txt").decode("latin-1").splitlines()
h = [i for i, l in enumerate(t) if l.startswith("EstacaoCodigo")][0]
v = pd.read_csv(io.StringIO("\n".join(t[h:])), sep=";", decimal=",", dtype=str)
v["Data"] = pd.to_datetime(v["Data"], format="%d/%m/%Y")
v["lvl"] = v.NivelConsistencia.astype(int)
v = v.sort_values(["Data", "lvl"]).drop_duplicates("Data", keep="last")  # prefer consisted (2) data
rows = []
for _, r in v.iterrows():
    for d in range(1, 32):
        c = f"Vazao{d:02d}"
        if c in r and isinstance(r[c], str) and r[c].strip():
            try:
                day = r.Data.replace(day=d)
            except ValueError:
                continue
            rows.append((day, float(r[c].replace(",", ".")), r.lvl))
q = pd.DataFrame(rows, columns=["date", "q", "lvl"]).set_index("date").sort_index()
q = q[~q.index.duplicated(keep="last")]
print("daily Q", q.index.min().date(), q.index.max().date(), len(q))
q["doy"] = np.minimum(q.index.dayofyear, 365)
base = q[(q.index.year >= 1995) & (q.index.year <= 2022)]
yrs = base.index.year.unique()
clim = base.groupby("doy").q.agg(p10=lambda s: s.quantile(0.1), med="median", p90=lambda s: s.quantile(0.9),
                                 mn="min", mx="max")
clim = clim.rolling(7, center=True, min_periods=1).mean()
y23 = q[q.index.year == 2023]
print("2023 days", len(y23), "levels", y23.lvl.value_counts().to_dict())
hyd = {
    "doy": clim.index.tolist(),
    "p10": clim.p10.round(0).tolist(), "med": clim.med.round(0).tolist(), "p90": clim.p90.round(0).tolist(),
    "mn": clim.mn.round(0).tolist(), "mx": clim.mx.round(0).tolist(),
    "y23_doy": y23.doy.tolist(), "y23": y23.q.round(0).tolist(),
    "nyears": int(len(yrs)), "years": [int(yrs.min()), int(yrs.max())],
}
(OUT / "hydro.json").write_text(json.dumps(hyd), encoding="utf-8")
mon = base.groupby(base.index.month).q.median()
print("Tabatinga median Q by month:", mon.round(-2).astype(int).to_dict())
print("Tabatinga mean Q 1995-2022:", round(base.q.mean(), -2), "min", base.q.min(), "max", base.q.max())
m23 = y23.groupby(y23.index.month).q.mean()
print("2023 monthly mean:", m23.round(-2).astype(int).to_dict())
print("2023 min:", y23.q.min(), y23.q.idxmin().date(), "| climatological median at that doy:",
      clim.med.loc[y23.q.idxmin().dayofyear])

# Manaus rainfall
mr = pd.read_csv(ROOT / "manaus/manaus-brazil-climate-data.csv", skiprows=1, encoding="utf-8-sig")
mr.columns = [c.strip() for c in mr.columns]
print(mr.head(14).to_string())
