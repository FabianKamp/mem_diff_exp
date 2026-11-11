"""Compose psychometric function and forest plot SVGs into a panel figure.

Layout: 2 rows (PD_PE_PF, PG) x 2 columns (psychometric, forest).
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "figures" / "pilots"
OUT = SRC / "model_panel.svg"

ROWS = ["PD_PE_PF", "PG"]
COLS = ["psychometric", "forest"]

# final sizes (mm)
PAGE_W, PAGE_H = 180.0, 120.0  # landscape
MARGIN = 5.0
GAP_X, GAP_Y = 6.0, 8.0
LABEL_ROW = 4.0  # space for panel labels

# column width ratio (equal since both plots are same size)
COL_RATIO = [0.5, 0.5]

# font sizes (pt)
TICK_PT, LABEL_PT, TITLE_PT, LEGEND_PT, PANEL_PT = 6.0, 7.0, 7.0, 6.0, 9.0
PT2MM = 25.4 / 72

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)
Q = lambda tag: f"{{{SVG_NS}}}{tag}"


def prefix_ids(svg_text, pfx):
    """Prefix all IDs to avoid collisions when combining SVGs."""
    ids = set(re.findall(r'\bid="([^"]+)"', svg_text))
    for i in sorted(ids, key=len, reverse=True):
        svg_text = re.sub(rf'\bid="{re.escape(i)}"', f'id="{pfx}{i}"', svg_text)
        svg_text = svg_text.replace(f"url(#{i})", f"url(#{pfx}{i})")
        svg_text = svg_text.replace(f'href="#{i}"', f'href="#{pfx}{i}"')
    return svg_text


def get_viewbox(root):
    """Extract viewBox dimensions."""
    vb = root.get("viewBox")
    if vb:
        parts = [float(x) for x in vb.split()]
        return parts[0], parts[1], parts[2], parts[3]
    # fallback to width/height
    w = float(re.sub(r"[^\d.]", "", root.get("width", "100")))
    h = float(re.sub(r"[^\d.]", "", root.get("height", "100")))
    return 0, 0, w, h


def load_svg(path, pfx):
    """Load SVG and return root element with prefixed IDs."""
    text = path.read_text()
    text = prefix_ids(text, pfx)
    return ET.fromstring(text)


def main():
    # calculate cell dimensions
    usable_w = PAGE_W - 2 * MARGIN - GAP_X
    usable_h = PAGE_H - 2 * MARGIN - GAP_Y

    cell_ws = [usable_w * r for r in COL_RATIO]
    cell_h = (usable_h - LABEL_ROW * 2) / 2

    # create output SVG
    out = ET.Element(Q("svg"), {
        "width": f"{PAGE_W}mm",
        "height": f"{PAGE_H}mm",
        "viewBox": f"0 0 {PAGE_W} {PAGE_H}",
        "version": "1.1",
    })

    # white background
    ET.SubElement(out, Q("rect"), {
        "x": "0", "y": "0",
        "width": str(PAGE_W), "height": str(PAGE_H),
        "fill": "#ffffff"
    })

    letters = iter("abcd")

    for ri, row_name in enumerate(ROWS):
        for ci, col_name in enumerate(COLS):
            # construct filename
            fname = f"{col_name}_{row_name}.svg"
            path = SRC / fname

            if not path.exists():
                print(f"Warning: {path} not found, skipping")
                continue

            # load SVG
            pfx = f"{row_name}_{col_name}_"
            root = load_svg(path, pfx)
            _, _, src_w, src_h = get_viewbox(root)

            # calculate position and scale
            cell_w = cell_ws[ci]
            x0 = MARGIN + sum(cell_ws[:ci]) + ci * GAP_X
            y0 = MARGIN + ri * (cell_h + GAP_Y + LABEL_ROW) + LABEL_ROW

            # scale to fit cell
            scale_x = cell_w / src_w
            scale_y = cell_h / src_h
            scale = min(scale_x, scale_y)

            # center in cell
            scaled_w = src_w * scale
            scaled_h = src_h * scale
            dx = (cell_w - scaled_w) / 2
            dy = (cell_h - scaled_h) / 2

            # create group with transform
            g = ET.SubElement(out, Q("g"), {
                "id": f"panel_{row_name}_{col_name}",
                "transform": f"translate({x0 + dx:.4f} {y0 + dy:.4f}) scale({scale:.6f})",
            })

            # copy children (skip metadata)
            for child in root:
                if child.tag != Q("metadata"):
                    g.append(child)

            # add panel label
            lab = ET.SubElement(out, Q("text"), {
                "x": f"{x0:.3f}",
                "y": f"{y0 - LABEL_ROW + 0.72 * PANEL_PT * PT2MM + 1:.3f}",
                "font-family": "Arial, Helvetica, sans-serif",
                "font-weight": "bold",
                "font-size": f"{PANEL_PT * PT2MM:.3f}",
                "fill": "#000000",
            })
            lab.text = next(letters)

    # write output
    ET.ElementTree(out).write(OUT, encoding="utf-8", xml_declaration=True)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
