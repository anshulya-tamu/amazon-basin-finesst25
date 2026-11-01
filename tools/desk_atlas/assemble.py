"""Fill template.html with the built map fragments and chart data."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
B = HERE / "build"
hyd = json.loads((B / "hydro.json").read_text(encoding="utf-8"))

i = min(range(len(hyd["y23"])), key=lambda k: hyd["y23"][k])
doy, q = hyd["y23_doy"][i], hyd["y23"][i]
med = hyd["med"][doy - 1]
fill = {
    "{{MAP_A}}": (B / "mapA.svg").read_text(encoding="utf-8"),
    "{{MAP_B}}": (B / "mapB.svg").read_text(encoding="utf-8"),
    "{{HYDRO}}": json.dumps(hyd, separators=(",", ":")),
    "{{TAB_MEAN}}": "39,700",
    "{{MIN23}}": f"{round(q, -2):,.0f}",
    "{{PCT23}}": f"{round(100 * (med - q) / med)}",
}
html = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in fill.items():
    assert k in html, k
    html = html.replace(k, v)
out = HERE / "amazon-desk-atlas.html"
out.write_text(html, encoding="utf-8")
print(out, round(len(html) / 1024), "KB", "| min", fill["{{MIN23}}"], "pct", fill["{{PCT23}}"])
