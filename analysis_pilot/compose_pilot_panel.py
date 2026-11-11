"""Compose the six pilot SVGs (figures/pilots) into one A5-landscape panel figure.

Layout: 3 rows (PA_PB, PD_PE_PF, PG) x 2 columns (vs_*, mixed_*).
Text stays live (editable). Because each plot is shrunk to fit its cell, font sizes
are rescaled so that the *final* sizes are TICK_PT / LABEL_PT, and tick labels,
axis labels and legend are repositioned to make room for the larger text.
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "figures" / "pilots"
OUT = SRC / "pilots_panel.svg"

ROWS = ["PA_PB", "PD_PE_PF", "PG"]
COLS = ["vs", "mixed"]

# final sizes
PAGE_W, PAGE_H = 210.0, 148.0          # A5 landscape, mm
MARGIN, GAP, LABEL_ROW = 4.0, 4.0, 3.0  # mm
TICK_PT, LABEL_PT, TITLE_PT, LEGEND_PT, PANEL_PT = 6.0, 7.0, 7.0, 6.0, 8.0
PT2MM = 25.4 / 72

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)
Q = lambda tag: f"{{{SVG_NS}}}{tag}"

# Arial advance widths (em) for the characters in tick labels
CHAR_W = {**{d: 0.556 for d in "0123456789"}, ".": 0.278, "-": 0.333, "−": 0.584}


def text_width(s, size):
    return sum(CHAR_W.get(c, 0.6) for c in s) * size


def set_style(el, **kv):
    style = el.get("style", "")
    for k, v in kv.items():
        k = k.replace("_", "-")
        if re.search(rf"{k}:\s*[^;]+", style):
            style = re.sub(rf"{k}:\s*[^;]+", f"{k}: {v}", style)
        else:
            style += f"; {k}: {v}"
    el.set("style", style)


def move_text(t, x=None, y=None):
    x = float(t.get("x")) if x is None else x
    y = float(t.get("y")) if y is None else y
    t.set("x", f"{x:.4f}")
    t.set("y", f"{y:.4f}")
    rot = re.search(r"rotate\((-?[\d.]+)", t.get("transform", "rotate(0"))
    t.set("transform", f"rotate({rot.group(1)} {x:.4f} {y:.4f})")


def prefix_ids(svg_text, pfx):
    ids = set(re.findall(r'\bid="([^"]+)"', svg_text))
    for i in sorted(ids, key=len, reverse=True):
        svg_text = re.sub(rf'\bid="{re.escape(i)}"', f'id="{pfx}{i}"', svg_text)
        svg_text = svg_text.replace(f"url(#{i})", f"url(#{pfx}{i})")
        svg_text = svg_text.replace(f'href="#{i}"', f'href="#{pfx}{i}"')
    return svg_text


def classify(root, pfx):
    """Return dict of text roles -> list of <text> elements (matplotlib layout)."""
    roles = {"xtick": [], "ytick": [], "xlabel": None, "ylabel": None, "title": None, "legend": []}
    axes = root.find(f".//{Q('g')}[@id='{pfx}axes_1']")
    legend = axes.find(f".//{Q('g')}[@id='{pfx}legend_1']")
    legend_texts = set(legend.iter(Q("text"))) if legend is not None else set()
    roles["legend"] = list(legend_texts)
    xaxis = axes.find(f"{Q('g')}[@id='{pfx}matplotlib.axis_1']")
    yaxis = axes.find(f"{Q('g')}[@id='{pfx}matplotlib.axis_2']")
    xt = list(xaxis.iter(Q("text")))
    yt = list(yaxis.iter(Q("text")))
    roles["xtick"], roles["xlabel"] = xt[:-1], xt[-1]
    roles["ytick"], roles["ylabel"] = yt[:-1], yt[-1]
    others = [t for t in axes.findall(f"{Q('g')}/{Q('text')}") if t not in legend_texts]
    roles["title"] = others[0] if others else None
    return roles, legend


def layout_panel(path, s):
    """Rescale/reposition text for final scale s (final pt per source unit).
    Returns (root, bbox) with bbox in source units."""
    root = ET.fromstring(prefix_ids(path.read_text(), path.stem + "_"))
    roles, legend = classify(root, path.stem + "_")
    F, FL, FT, FG = TICK_PT / s, LABEL_PT / s, TITLE_PT / s, LEGEND_PT / s
    tick_len, pad = 3.5, 3.5

    # axes frame from the y ticks: tick baseline = tick pos + 0.36*10 (orig 10 px)
    old_fs = float(re.search(r"font-size:\s*([\d.]+)", roles["xtick"][0].get("style")).group(1))
    x_tick_base_old = float(roles["xtick"][0].get("y"))
    axes_bottom = x_tick_base_old - 0.72 * old_fs - pad - tick_len
    y_tick_right = float(roles["ytick"][0].get("x"))
    title_base = float(roles["title"].get("y")) if roles["title"] is not None else None
    W = float(root.get("viewBox").split()[2])

    # x ticks
    xb = axes_bottom + tick_len + pad + 0.72 * F
    for t in roles["xtick"]:
        set_style(t, font_size=f"{F:.3f}px")
        move_text(t, y=xb)
    # x label
    xlb = xb + 0.21 * F + 2.5 / s + 0.72 * FL
    set_style(roles["xlabel"], font_size=f"{FL:.3f}px")
    move_text(roles["xlabel"], y=xlb)
    # y ticks (baseline offset from tick position grows with font size)
    for t in roles["ytick"]:
        set_style(t, font_size=f"{F:.3f}px")
        y_old = float(t.get("y"))
        move_text(t, y=y_old - 0.36 * old_fs + 0.36 * F)
    wmax = max(text_width(t.text, F) for t in roles["ytick"])
    ylx = y_tick_right - wmax - 2.5 / s - 0.21 * FL
    set_style(roles["ylabel"], font_size=f"{FL:.3f}px")
    move_text(roles["ylabel"], x=ylx)
    # title
    if roles["title"] is not None:
        set_style(roles["title"], font_size=f"{FT:.3f}px")
    # legend: scale the whole legend group about its top-right corner
    if legend is not None:
        leg_fs = float(re.search(r"font-size:\s*([\d.]+)", roles["legend"][-1].get("style")).group(1))
        f = FG / leg_fs
        nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", legend.find(f".//{Q('path')}").get("d"))]
        xs, ys = nums[0::2], nums[1::2]
        # anchor at the legend corner nearest the axes corner it sits in
        vb_h = float(root.get("viewBox").split()[3])
        cx = max(xs) if (min(xs) + max(xs)) / 2 > W / 2 else min(xs)
        cy = min(ys) if (min(ys) + max(ys)) / 2 < vb_h / 2 else max(ys)
        legend.set("transform", f"translate({cx:.4f} {cy:.4f}) scale({f:.4f}) translate({-cx:.4f} {-cy:.4f})")

    left = ylx - 0.72 * FL
    top = (title_base - 0.72 * FT) if title_base is not None else 0
    bottom = xlb + 0.21 * FL
    return root, (left, top, W, bottom)


def fit(path, cell_w_mm, cell_h_mm):
    s = cell_w_mm / PT2MM / 853  # initial guess
    for _ in range(20):
        _, (l, t, r, b) = layout_panel(path, s)
        s_new = min(cell_w_mm / PT2MM / (r - l), cell_h_mm / PT2MM / (b - t))
        if abs(s_new - s) < 1e-6:
            break
        s = s_new
    return s


def main():
    cell_w = (PAGE_W - 2 * MARGIN - GAP) / 2
    row_h = (PAGE_H - 2 * MARGIN - 2 * GAP) / 3
    cell_h = row_h - LABEL_ROW

    paths = [[SRC / f"{c}_{r}.svg" for c in COLS] for r in ROWS]
    # one common scale for all panels so every panel has identical text/line sizes
    s = min(fit(p, cell_w, cell_h) for row in paths for p in row)

    out = ET.Element(Q("svg"), {
        "width": f"{PAGE_W}mm", "height": f"{PAGE_H}mm",
        "viewBox": f"0 0 {PAGE_W} {PAGE_H}", "version": "1.1",
    })
    ET.SubElement(out, Q("rect"), {"x": "0", "y": "0", "width": str(PAGE_W),
                                   "height": str(PAGE_H), "fill": "#ffffff"})
    letters = iter("abcdef")
    k = s * PT2MM  # mm per source unit
    for ri, row in enumerate(paths):
        for ci, p in enumerate(row):
            root, (l, t, r, b) = layout_panel(p, s)
            x0 = MARGIN + ci * (cell_w + GAP)
            y0 = MARGIN + ri * (row_h + GAP)
            # centre the plot horizontally in its cell
            dx = (cell_w - (r - l) * k) / 2
            g = ET.SubElement(out, Q("g"), {
                "id": f"panel_{p.stem}",
                "transform": f"translate({x0 + dx:.4f} {y0 + LABEL_ROW:.4f}) scale({k:.6f}) translate({-l:.4f} {-t:.4f})",
            })
            for child in root:
                if child.tag != Q("metadata"):
                    g.append(child)
            lab = ET.SubElement(out, Q("text"), {
                "x": f"{x0:.3f}", "y": f"{y0 + 0.72 * PANEL_PT * PT2MM:.3f}",
                "font-family": "Arial, Helvetica, sans-serif", "font-weight": "bold",
                "font-size": f"{PANEL_PT * PT2MM:.3f}", "fill": "#000000",
            })
            lab.text = next(letters)

    ET.ElementTree(out).write(OUT, encoding="utf-8", xml_declaration=True)
    print(f"Saved {OUT}  (scale {s:.4f} pt/unit, ticks {TICK_PT} pt, labels {LABEL_PT} pt)")


if __name__ == "__main__":
    main()
