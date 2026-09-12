"""
lecture.py
==========
Visual asset generator for the lecture:

    Smart Systems
    5.1  Micro-electromechanical systems (MEMS)
    5.2  Smart and intelligent sensors

Every figure used by lecture.qmd is produced here and written into ./figures.

Static graphics are written as vector .svg (Matplotlib and hand-built SVG).
A single optional Manim animation is rendered to .mp4 when Manim is available;
a static SVG fallback is always produced.

Run with:

    python lecture.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# ---------------------------------------------------------------------------
# Paths and shared style
# ---------------------------------------------------------------------------

FIGDIR = Path("figures")
FIGDIR.mkdir(parents=True, exist_ok=True)

INK = "#10243a"
BLUE = "#1f4e79"
MIDBLUE = "#2e6da4"
LIGHTBLUE = "#dbe8f6"
PALEBLUE = "#eef4fb"
WARM = "#c46a12"
LIGHTWARM = "#fdf5ec"
GREEN = "#1e7a4d"
GREY = "#8895a5"
LIGHTGREY = "#c8d3de"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 18,
        "axes.titlesize": 23,
        "axes.titleweight": "bold",
        "axes.labelsize": 19,
        "xtick.labelsize": 17,
        "ytick.labelsize": 17,
        "legend.fontsize": 16,
        "axes.edgecolor": "#5c6b7a",
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": "#5c6b7a",
        "ytick.color": "#5c6b7a",
        "axes.grid": True,
        "grid.color": LIGHTGREY,
        "grid.linewidth": 0.9,
        "grid.linestyle": ":",
        "axes.axisbelow": True,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "svg.fonttype": "path",
        "figure.dpi": 120,
    }
)


def save_fig(fig, name: str) -> None:
    path = FIGDIR / name
    fig.savefig(path, format="svg")
    plt.close(fig)
    print(f"  wrote {path}")


# ---------------------------------------------------------------------------
# Minimal hand-built SVG toolkit (no external dependency)
# ---------------------------------------------------------------------------

FONT_STACK = "DejaVu Sans, Segoe UI, Helvetica, Arial, sans-serif"


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_open(width: int, height: int, bg: str = "#ffffff") -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'font-family="{FONT_STACK}">'
        "<defs>"
        f'<marker id="arw" viewBox="0 0 10 10" refX="10" refY="5" '
        f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{BLUE}"/></marker>'
        f'<marker id="arwW" viewBox="0 0 10 10" refX="10" refY="5" '
        f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{WARM}"/></marker>'
        f'<marker id="arwG" viewBox="0 0 10 10" refX="10" refY="5" '
        f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="#5c6b7a"/></marker>'
        "</defs>"
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{bg}"/>'
    )


def svg_close() -> str:
    return "</svg>"


def rect(x, y, w, h, fill="#ffffff", stroke="none", sw=3, rx=0, dash=None, opacity=1.0) -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" '
        f'stroke-width="{sw}"{d}/>'
    )


def line(x1, y1, x2, y2, stroke=BLUE, sw=3, dash=None, marker=None, marker_start=None) -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    ms = f' marker-start="url(#{marker_start})"' if marker_start else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
        f'stroke-width="{sw}" stroke-linecap="round"{d}{m}{ms}/>'
    )


def poly(points, stroke=BLUE, sw=3, fill="none", dash=None, marker=None) -> str:
    pts = " ".join(f"{p[0]},{p[1]}" for p in points)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    return (
        f'<polyline points="{pts}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"{d}{m}/>'
    )


def polygon(points, stroke=BLUE, sw=3, fill="#ffffff") -> str:
    pts = " ".join(f"{p[0]},{p[1]}" for p in points)
    return (
        f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{sw}" stroke-linejoin="round"/>'
    )


def path(d, stroke=BLUE, sw=3, fill="none", dash=None) -> str:
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
        f'stroke-linecap="round"{ds}/>'
    )


def circle(cx, cy, r, fill="#ffffff", stroke=BLUE, sw=3) -> str:
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{sw}"/>'
    )


def text(x, y, s, size=24, fill=INK, anchor="middle", weight="normal", style="normal") -> str:
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" font-weight="{weight}" font-style="{style}" '
        f'dominant-baseline="middle">{_esc(s)}</text>'
    )


def text_block(cx, cy, lines, size=24, fill=INK, anchor="middle", lh=1.25, weight="normal") -> str:
    if isinstance(lines, str):
        lines = [lines]
    n = len(lines)
    step = size * lh
    y0 = cy - (n - 1) * step / 2.0
    return "".join(
        text(cx, y0 + i * step, s, size=size, fill=fill, anchor=anchor, weight=weight)
        for i, s in enumerate(lines)
    )


def box(x, y, w, h, lines, sizes=None, fills=None, fill=LIGHTBLUE, stroke=BLUE,
        rx=12, sw=3, dash=None, gap=8) -> str:
    if isinstance(lines, str):
        lines = [lines]
    n = len(lines)
    if sizes is None:
        sizes = [26] * n
    elif isinstance(sizes, int):
        sizes = [sizes] * n
    if fills is None:
        fills = [INK] * n
    elif isinstance(fills, str):
        fills = [fills] * n

    out = [rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=rx, dash=dash)]
    total = sum(sizes) + gap * (n - 1)
    cy = y + h / 2.0 - total / 2.0
    for i in range(n):
        yc = cy + sizes[i] / 2.0
        out.append(text(x + w / 2.0, yc, lines[i], size=sizes[i], fill=fills[i]))
        cy += sizes[i] + gap
    return "".join(out)


def write_svg(name: str, body: str) -> None:
    path = FIGDIR / name
    path.write_text(body, encoding="utf-8")
    print(f"  wrote {path}")


# ---------------------------------------------------------------------------
# Figure 1 - the length scale of MEMS  (Matplotlib -> SVG)
# ---------------------------------------------------------------------------


def _fmt_len(v: float) -> str:
    if v < 1e-6:
        return f"{v * 1e9:.0f} nm"
    if v < 1e-3:
        return f"{v * 1e6:.0f} µm"
    return f"{v * 1e3:.0f} mm"


def make_mems_scale() -> None:
    names = [
        "DNA width",
        "Transistor gate length",
        "Virus",
        "MEMS comb-finger gap",
        "Red blood cell",
        "Human hair",
        "MEMS accelerometer die",
    ]
    sizes = np.array([2e-9, 1e-8, 1e-7, 2e-6, 8e-6, 7e-5, 3e-3])
    colors = [GREY, GREY, GREY, MIDBLUE, GREEN, GREEN, WARM]

    fig, ax = plt.subplots(figsize=(12, 6.75))
    y = np.arange(len(names))[::-1]
    xmin = 1e-9

    ax.barh(y, sizes - xmin, left=xmin, height=0.58, color=colors, zorder=3)

    ax.set_xscale("log")
    ax.set_xlim(1e-9, 3e-2)
    ax.set_ylim(-0.85, 7.1)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=17)
    ax.set_xlabel("Characteristic dimension (metres, logarithmic scale)")
    ax.set_title("The scale of MEMS: from nanometres to millimetres")

    for xv, lab in [(1e-9, "1 nm"), (1e-6, "1 µm"), (1e-3, "1 mm")]:
        ax.axvline(xv, color="#9aa8b8", lw=1.4, ls="--", zorder=1)
        ax.text(xv, 6.5, lab, ha="center", va="bottom", fontsize=15, color="#5c6b7a")

    for yy, s in zip(y, sizes):
        ax.text(s * 1.45, yy, _fmt_len(s), va="center", ha="left",
                fontsize=16, color=INK, zorder=4)

    ax.annotate(
        "",
        xy=(1e-3, -0.62),
        xytext=(1e-6, -0.62),
        arrowprops=dict(arrowstyle="<->", color=BLUE, lw=2.0),
    )
    ax.text(np.sqrt(1e-6 * 1e-3), -0.42, "typical MEMS design range",
            ha="center", va="bottom", fontsize=16, color=BLUE)

    ax.grid(axis="y", visible=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout(pad=1.5)
    save_fig(fig, "mems_scale.svg")


# ---------------------------------------------------------------------------
# Figure 2 - MEMS device families  (hand-built SVG)
# ---------------------------------------------------------------------------


def make_mems_family() -> None:
    W, H = 1600, 740
    p = [svg_open(W, H)]

    p.append(box(650, 30, 300, 80, "MEMS", sizes=32, fills="#ffffff",
                 fill=BLUE, stroke=BLUE))

    p.append(line(800, 110, 800, 170))
    p.append(line(440, 170, 1160, 170))
    p.append(line(440, 170, 440, 240))
    p.append(line(1160, 170, 1160, 240))

    p.append(box(180, 240, 520, 92,
                 ["Microsensors", "physical quantity  ->  electrical signal"],
                 sizes=[28, 21], fills=[INK, "#40546b"]))
    p.append(box(900, 240, 520, 92,
                 ["Microactuators", "electrical signal  ->  physical action"],
                 sizes=[28, 21], fills=[INK, "#40546b"]))

    p.append(line(440, 332, 440, 378))
    p.append(line(310, 378, 570, 378))
    p.append(line(310, 378, 310, 420))
    p.append(line(570, 378, 570, 420))

    left_children = [
        (195, 420, "Accelerometer", "airbag, ESC"),
        (455, 420, "Gyroscope", "yaw rate, rollover"),
        (195, 550, "Pressure sensor", "TPMS, MAP"),
        (455, 550, "Microphone", "voice, noise"),
    ]
    for x, y, t, s in left_children:
        p.append(box(x, y, 230, 92, [t, s], sizes=[24, 19],
                     fills=[INK, "#40546b"], fill=PALEBLUE))

    p.append(line(1160, 332, 1160, 378))
    p.append(line(1030, 378, 1290, 378))
    p.append(line(1030, 378, 1030, 420))
    p.append(line(1290, 378, 1290, 420))

    right_children = [
        (915, 420, "Micro-mirror", "projection, HUD"),
        (1175, 420, "Micro-pump", "valves, drug delivery"),
        (915, 550, "Micro-speaker", "hearing aids"),
        (1175, 550, "Inkjet printhead", "printing"),
    ]
    for x, y, t, s in right_children:
        p.append(box(x, y, 230, 92, [t, s], sizes=[24, 19],
                     fills=[INK, "#40546b"], fill=LIGHTWARM))

    p.append(text(800, 700,
                  "Both families are built with the same microfabrication toolbox.",
                  size=22, fill="#40546b"))

    p.append(svg_close())
    write_svg("mems_family.svg", "".join(p))


# ---------------------------------------------------------------------------
# Figure 3 - microfabrication flow  (hand-built SVG)
# ---------------------------------------------------------------------------


def make_microfab_flow() -> None:
    W, H = 1600, 580
    p = [svg_open(W, H)]

    steps = [
        ("Substrate", ["Silicon wafer,", "cleaned"]),
        ("Deposition", ["Thin film grown", "or deposited"]),
        ("Lithography", ["Pattern written", "into photoresist"]),
        ("Etching", ["Pattern transferred", "into the film"]),
        ("Release", ["Sacrificial layer", "removed"]),
        ("Package & test", ["Diced, sealed,", "characterised"]),
    ]

    bw, bh, gap = 210, 150, 56
    x0 = 30
    for i, (title, sub) in enumerate(steps):
        x = x0 + i * (bw + gap)
        p.append(box(x, 210, bw, bh, [title] + sub, sizes=[25, 18, 18],
                     fills=[INK, "#40546b", "#40546b"], fill=PALEBLUE))
        p.append(circle(x + bw / 2, 158, 26, fill=BLUE, stroke=BLUE))
        p.append(text(x + bw / 2, 158, str(i + 1), size=24, fill="#ffffff"))
        if i < len(steps) - 1:
            p.append(line(x + bw + 6, 285, x + bw + gap - 6, 285, sw=4, marker="arw"))

    p.append(rect(30, 430, 1540, 110, fill=LIGHTWARM, stroke=WARM, rx=14, sw=3))
    p.append(text(800, 466,
                  "Steps 2-4 are repeated for every structural layer.",
                  size=23, fill=INK))
    p.append(text(800, 506,
                  "Step 5 frees the moving parts - this is what makes the device mechanical.",
                  size=23, fill=INK))

    p.append(svg_close())
    write_svg("microfab_flow.svg", "".join(p))


# ---------------------------------------------------------------------------
# Figure 4 - bulk versus surface micromachining  (hand-built SVG)
# ---------------------------------------------------------------------------


def make_bulk_surface() -> None:
    W, H = 1600, 780
    p = [svg_open(W, H)]

    p.append(line(800, 30, 800, 750, stroke=LIGHTGREY, sw=2, dash="10,10"))

    # ---- left: bulk micromachining --------------------------------------
    p.append(text(430, 62, "Bulk micromachining", size=30, weight="bold"))
    p.append(text(430, 104, "the wafer itself is the mechanical material",
                  size=20, fill="#40546b"))

    p.append(rect(150, 380, 560, 260, fill="#c9d6e4", stroke="#34495e", sw=3))
    p.append(poly([(290, 640), (290, 420), (570, 420), (570, 640)],
                  stroke="#34495e", sw=3, dash="9,7"))
    p.append(rect(290, 380, 280, 40, fill="#e8a33d", stroke="#8a5410", sw=3))

    p.append(text(430, 165, "(a few micrometres thick)", size=19, fill="#40546b"))
    p.append(text(430, 195, "Thin silicon diaphragm", size=22, fill=INK))
    p.append(line(430, 215, 430, 375, stroke=BLUE, sw=2, dash="6,6"))

    p.append(line(430, 682, 430, 615, stroke=BLUE, sw=2, dash="6,6", marker="arw"))
    p.append(text(430, 706, "Cavity etched from the back of the wafer",
                  size=21, fill=INK))

    p.append(text_block(105, 510, ["Silicon", "wafer"], size=22, fill=INK, anchor="end"))

    # ---- right: surface micromachining ----------------------------------
    p.append(text(1190, 62, "Surface micromachining", size=30, weight="bold"))
    p.append(text(1190, 104, "thin films are built up, then partly removed",
                  size=20, fill="#40546b"))

    p.append(rect(900, 560, 580, 90, fill="#c9d6e4", stroke="#34495e", sw=3))
    p.append(rect(980, 490, 70, 70, fill="#e8a33d", stroke="#8a5410", sw=3))
    p.append(rect(980, 490, 400, 24, fill="#e8a33d", stroke="#8a5410", sw=3))
    p.append(rect(1050, 514, 330, 46, fill="#ffffff", stroke="#8a5410",
                  sw=2, dash="8,6"))

    p.append(text(1090, 452, "Structural layer (polysilicon)", size=21, fill=INK))
    p.append(text(1360, 448, "free to move", size=19, fill=WARM))
    p.append(line(1360, 470, 1360, 486, stroke=WARM, sw=3, marker="arwW"))
    p.append(text(1215, 537, "removed sacrificial layer", size=17, fill="#8a5410"))
    p.append(text(1190, 690, "Silicon substrate", size=22, fill=INK))

    p.append(svg_close())
    write_svg("bulk_surface.svg", "".join(p))


# ---------------------------------------------------------------------------
# Figure 5 - the three common transduction principles  (hand-built SVG)
# ---------------------------------------------------------------------------


def make_sensing_principles() -> None:
    W, H = 1600, 700
    p = [svg_open(W, H)]

    for x, title in [(40, "Capacitive"), (550, "Piezoresistive"), (1060, "Piezoelectric")]:
        p.append(rect(x, 50, 500, 590, fill="#fbfcfe", stroke=LIGHTGREY, sw=2, rx=18))
        p.append(text(x + 250, 96, title, size=28, weight="bold"))

    # ---- capacitive ------------------------------------------------------
    p.append(rect(140, 230, 300, 18, fill="#4a6fa5", stroke="#2c4a6e", sw=2))
    p.append(rect(140, 340, 300, 18, fill="#e8a33d", stroke="#8a5410", sw=2))
    p.append(text(290, 272, "+ + + + +", size=22, fill="#2c4a6e"))
    p.append(text(290, 316, "- - - - -", size=22, fill="#8a5410"))
    p.append(line(480, 340, 480, 248, stroke=WARM, sw=3,
                  marker="arwW", marker_start="arwW"))
    p.append(text(508, 294, "d", size=24, fill=INK))
    p.append(text(290, 460, "C = ε0 εr A / d", size=24, fill=INK))
    p.append(text(290, 520, "Displacement changes the gap d,", size=20, fill="#40546b"))
    p.append(text(290, 550, "so the capacitance changes.", size=20, fill="#40546b"))

    # ---- piezoresistive --------------------------------------------------
    p.append(rect(650, 322, 20, 60, fill="#8a99a8", stroke="#5c6b7a", sw=2))
    p.append(rect(930, 322, 20, 60, fill="#8a99a8", stroke="#5c6b7a", sw=2))
    p.append(rect(650, 300, 300, 22, fill="#b9c8d8", stroke="#5c6b7a", sw=2))
    p.append(line(800, 200, 800, 292, stroke=WARM, sw=4, marker="arwW"))
    p.append(text(830, 232, "F", size=24, fill=WARM))
    p.append(path("M 650 322 Q 800 400 950 322", stroke=WARM, sw=3, dash="8,6"))
    p.append(text(800, 460, "ΔR / R = G ε", size=24, fill=INK))
    p.append(text(800, 520, "Bending strains the beam;", size=20, fill="#40546b"))
    p.append(text(800, 550, "strain changes its resistance.", size=20, fill="#40546b"))

    # ---- piezoelectric ---------------------------------------------------
    p.append(rect(1230, 270, 160, 110, fill="#cfe3d4", stroke="#1e7a4d", sw=3))
    p.append(rect(1230, 252, 160, 18, fill="#aab4be", stroke="#5c6b7a", sw=2))
    p.append(rect(1230, 380, 160, 18, fill="#aab4be", stroke="#5c6b7a", sw=2))
    p.append(line(1310, 180, 1310, 244, stroke=WARM, sw=4, marker="arwW"))
    p.append(line(1310, 452, 1310, 406, stroke=WARM, sw=4, marker="arwW"))
    p.append(text(1345, 205, "F", size=22, fill=WARM))
    p.append(text(1345, 432, "F", size=22, fill=WARM))
    p.append(text(1195, 261, "+ + +", size=22, fill="#c0392b", anchor="end"))
    p.append(text(1195, 389, "- - -", size=22, fill="#2471a3", anchor="end"))
    p.append(poly([(1390, 261), (1455, 261), (1455, 300)], stroke=BLUE, sw=3))
    p.append(poly([(1390, 389), (1455, 389), (1455, 350)], stroke=BLUE, sw=3))
    p.append(rect(1420, 300, 70, 50, fill="#ffffff", stroke=BLUE, sw=3, rx=8))
    p.append(text(1455, 325, "V", size=24, fill=BLUE))
    p.append(text(1310, 520, "V ∝ applied stress", size=24, fill=INK))
    p.append(text(1310, 580, "Deformation displaces charge,", size=20, fill="#40546b"))
    p.append(text(1310, 610, "producing a voltage.", size=20, fill="#40546b"))

    p.append(svg_close())
    write_svg("sensing_principles.svg", "".join(p))


# ---------------------------------------------------------------------------
# Figure 6 - capacitive accelerometer behaviour  (Matplotlib -> SVG)
# ---------------------------------------------------------------------------


def make_capacitive_accel() -> None:
    u = np.linspace(0.0, 0.6, 400)

    fig, axes = plt.subplots(1, 2, figsize=(12, 6.75))

    ax = axes[0]
    ax.plot(u, 1.0 / (1.0 - u), color=BLUE, lw=3.2,
            label="Exact:  C / C$_0$ = 1/(1 − u)")
    ax.plot(u, 1.0 + u, color=WARM, lw=3.2, ls="--",
            label="Linear approximation:  1 + u")
    ax.set_xlabel("Normalised displacement  u = x / d$_0$")
    ax.set_ylabel("Normalised capacitance  C / C$_0$")
    ax.set_title("Single-ended: strongly non-linear")
    ax.set_xlim(0, 0.6)
    ax.set_ylim(1.0, 2.65)
    ax.legend(loc="upper left", frameon=False)
    ax.annotate("error grows quickly\nas the gap closes",
                xy=(0.52, 2.08), xytext=(0.14, 2.30),
                fontsize=15, color=INK,
                arrowprops=dict(arrowstyle="->", color="#5c6b7a", lw=1.8))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax = axes[1]
    ax.axvspan(0.0, 0.3, color=LIGHTBLUE, alpha=0.85, zorder=0)
    ax.plot(u, u / (1.0 - u ** 2), color=BLUE, lw=3.2,
            label="Exact:  ΔC / 2C$_0$ = u /(1 − u²)")
    ax.plot(u, u, color=WARM, lw=3.2, ls="--",
            label="Linear approximation:  u")
    ax.set_xlabel("Normalised displacement  u = x / d$_0$")
    ax.set_ylabel("Normalised differential capacitance")
    ax.set_title("Differential pair: nearly linear")
    ax.set_xlim(0, 0.6)
    ax.set_ylim(0, 1.05)
    ax.legend(loc="upper left", frameon=False)
    ax.text(0.15, 0.04, "usable range\nu < 0.3", ha="center", va="bottom",
            fontsize=15, color=MIDBLUE)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout(pad=1.6)
    save_fig(fig, "capacitive_accel.svg")


# ---------------------------------------------------------------------------
# Figure 7 - MEMS in the vehicle  (hand-built SVG)
# ---------------------------------------------------------------------------


def make_mems_automotive() -> None:
    W, H = 1600, 850
    p = [svg_open(W, H)]

    # wheels first so the body overlaps them slightly
    for cx in (540, 1080):
        p.append(circle(cx, 480, 60, fill="#2c3e50", stroke="#1b2836", sw=3))
        p.append(circle(cx, 480, 24, fill="#8a99a8", stroke="#5c6b7a", sw=2))

    # body and cabin
    p.append(rect(360, 300, 880, 140, fill="#4a6fa5", stroke="#2c4a6e", sw=3, rx=18))
    p.append(polygon([(540, 300), (680, 180), (940, 180), (1060, 300)],
                     stroke="#2c4a6e", sw=3, fill="#7fa8d4"))
    p.append(polygon([(575, 295), (695, 200), (925, 200), (1030, 295)],
                     stroke="#2c4a6e", sw=2, fill="#dceaf7"))

    markers = [
        (410, 390, "1"),
        (790, 370, "2"),
        (1080, 480, "3"),
        (470, 320, "4"),
        (890, 235, "5"),
        (680, 235, "6"),
    ]
    for mx, my, num in markers:
        p.append(circle(mx, my, 26, fill="#d9534f", stroke="#ffffff", sw=3))
        p.append(text(mx, my, num, size=24, fill="#ffffff"))

    legend = [
        (120, 620, "1", "Crash accelerometer — airbag trigger"),
        (120, 690, "2", "Yaw-rate gyroscope — ESC, rollover"),
        (120, 760, "3", "Tyre-pressure sensor (TPMS)"),
        (830, 620, "4", "Manifold absolute pressure (MAP)"),
        (830, 690, "5", "Microphone — hands-free, noise control"),
        (830, 760, "6", "Micro-mirror — head-up display (actuator)"),
    ]
    for mx, my, num, label in legend:
        p.append(circle(mx, my, 22, fill="#d9534f", stroke="#d9534f", sw=2))
        p.append(text(mx, my, num, size=21, fill="#ffffff"))
        p.append(text(mx + 40, my, label, size=24, fill=INK, anchor="start"))

    p.append(svg_close())
    write_svg("mems_automotive.svg", "".join(p))


# ---------------------------------------------------------------------------
# Figure 8 - from sensing element to intelligent sensor  (hand-built SVG)
# ---------------------------------------------------------------------------


def make_sensor_evolution() -> None:
    W, H = 740, 740
    p = [svg_open(1600, H)]

    stages = [
        ("1. Sensing element", [
            "Transduction only",
            "Analogue output (mV)",
        ]),
        ("2. Integrated sensor", [
            "Amplify + filter",
            "Temperature compensation",
            "Analogue output (0-5 V)",
        ]),
        ("3. Smart sensor", [
            "On-board ADC",
            "Calibration + linearisation",
            "Self-test and diagnostics",
            "Digital output (I2C / SPI)",
        ]),
        ("4. Intelligent sensor", [
            "Multiple sensing elements",
            "Sensor fusion",
            "Fault detection / isolation",
            "Local decision + output",
        ]),
    ]

    bw, gap = 340, 60
    x0 = 30
    for i, (title, items) in enumerate(stages):
        x = x0 + i * (bw + gap)
        p.append(rect(x, 220, bw, 60, fill=BLUE, stroke=BLUE, rx=12))
        p.append(text(x + bw / 2, 250, title, size=24, fill="#ffffff"))
        p.append(rect(x, 280, bw, 320, fill=PALEBLUE, stroke=BLUE, sw=3, rx=12))
        for j, it in enumerate(items):
            yy = 300 + j * 66
            p.append(rect(x + 20, yy, bw - 40, 54, fill="#ffffff",
                          stroke="#b9cde3", sw=2, rx=8))
            p.append(text(x + bw / 2, yy + 27, it, size=19, fill=INK))
        if i < len(stages) - 1:
            p.append(line(x + bw + 8, 410, x + bw + gap - 8, 410, sw=4, marker="arw"))

    p.append(text(800, 680,
                  "Each step adds capability — and also cost, power and design complexity.",
                  size=22, fill="#40546b"))

    p.append(svg_close())
    write_svg("sensor_evolution.svg", "".join(p))


# ---------------------------------------------------------------------------
# Figure 9 - smart sensor architecture  (hand-built SVG)
# ---------------------------------------------------------------------------


def make_smart_sensor_arch() -> None:
    W, H = 1600, 660
    p = [svg_open(W, H)]

    # dashed module boundary
    p.append(rect(150, 320, 1075, 280, fill="none", stroke=GREY,
                  sw=2, rx=16, dash="12,8"))
    p.append(text(168, 346, "Smart sensor module (single package)", size=19,
                  fill="#5c6b7a", anchor="start", style="italic"))

    # main processing chain
    p.append(box(180, 370, 210, 110, "Sensing element", sizes=20))
    p.append(box(450, 370, 210, 110, ["Signal", "conditioning"], sizes=[20, 20]))
    p.append(box(720, 370, 150, 110, "ADC", sizes=22))
    p.append(box(930, 370, 270, 110,
                 ["Microcontroller / DSP", "calibrate, compensate,", "self-test"],
                 sizes=[20, 16, 16]))
    p.append(box(1260, 370, 180, 110,
                 ["Digital interface", "I2C / SPI / CAN"], sizes=[18, 16]))

    # arrows
    p.append(line(60, 425, 175, 425, sw=4, marker="arw"))
    p.append(text(117, 395, "Measurand", size=19, fill=INK))
    p.append(line(395, 425, 445, 425, sw=4, marker="arw"))
    p.append(line(665, 425, 715, 425, sw=4, marker="arw"))
    p.append(line(875, 425, 925, 425, sw=4, marker="arw"))
    p.append(line(1205, 425, 1255, 425, sw=4, marker="arw"))
    p.append(line(1445, 425, 1560, 425, sw=4, marker="arw"))
    p.append(text(1500, 470, "to system bus", size=18, fill="#40546b"))

    # temperature input
    p.append(box(930, 190, 270, 80, ["On-chip temperature", "sensor"],
                 sizes=[19, 19]))
    p.append(line(1065, 275, 1065, 365, sw=3, marker="arw"))
    p.append(text(1085, 320, "compensation", size=18, fill="#40546b", anchor="start"))

    # self-test feedback loop
    p.append(poly([(1065, 480), (1065, 555), (285, 555), (285, 485)],
                  stroke=WARM, sw=3, marker="arwW"))
    p.append(text(675, 585, "self-test and excitation control",
                  size=20, fill=WARM))

    p.append(svg_close())
    write_svg("smart_sensor_arch.svg", "".join(p))


# ---------------------------------------------------------------------------
# Figure 10 - sensor fusion concept  (hand-built SVG)
# ---------------------------------------------------------------------------


def make_fusion_concept() -> None:
    W, H = 1600, 640
    p = [svg_open(W, H)]

    sensors = [
        ("Accelerometer", "fast, but drifts"),
        ("Gyroscope", "good short-term rate"),
        ("Magnetometer", "absolute heading, noisy"),
    ]
    targets = [(695, 275), (695, 320), (695, 365)]

    for i, (t, s) in enumerate(sensors):
        y = 100 + i * 160
        p.append(box(80, y, 330, 110, [t, s], sizes=[23, 18],
                     fills=[INK, "#40546b"]))
        p.append(line(415, y + 55, targets[i][0], targets[i][1],
                      sw=3, marker="arw"))

    p.append(box(700, 230, 420, 180,
                 ["Sensor fusion",
                  "Kalman filter / complementary filter",
                  "weighted combination of inputs"],
                 sizes=[26, 19, 18],
                 fills=[INK, "#40546b", "#40546b"]))

    p.append(line(1125, 320, 1255, 320, sw=4, marker="arw"))
    p.append(box(1260, 250, 300, 140,
                 ["Robust estimate", "attitude, position, motion"],
                 sizes=[22, 18], fills=[INK, "#40546b"], fill=LIGHTWARM))

    p.append(text(800, 585,
                  "Cross-checking several sensors reduces noise and allows faults to be detected.",
                  size=21, fill="#40546b"))

    p.append(svg_close())
    write_svg("fusion_concept.svg", "".join(p))


# ---------------------------------------------------------------------------
# Figure 11 - calibration and linearisation  (Matplotlib -> SVG)
# ---------------------------------------------------------------------------


def make_linearization() -> None:
    p_true = np.linspace(0.0, 100.0, 400)          # true pressure, kPa
    ideal = 0.040 * p_true                          # 0 - 4.00 V full scale
    fs = 4.0

    raw = ideal + 0.05 * fs * np.sin(np.pi * p_true / 100.0)
    calibrated = ideal + 0.0015 * fs * np.sin(2.0 * np.pi * p_true / 45.0)

    fig, axes = plt.subplots(1, 2, figsize=(12, 6.75))

    ax = axes[0]
    ax.plot(p_true, ideal, color=BLUE, lw=3.2, label="Ideal straight line")
    ax.plot(p_true, raw, color=WARM, lw=3.2, label="Raw sensor output")
    ax.set_xlabel("True pressure (kPa)")
    ax.set_ylabel("Output voltage (V)")
    ax.set_title("Sensor response")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 4.4)
    ax.legend(loc="upper left", frameon=False)
    ax.annotate("bow error\n≈ 5 % of full scale",
                xy=(50, 2.2), xytext=(62, 1.05),
                fontsize=15, color=INK,
                arrowprops=dict(arrowstyle="->", color="#5c6b7a", lw=1.8))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax = axes[1]
    err_raw = (raw - ideal) / fs * 100.0
    err_cal = (calibrated - ideal) / fs * 100.0
    ax.fill_between(p_true, -0.2, 0.2, color=LIGHTBLUE, alpha=0.9, zorder=0,
                    label="±0.2 % FS target band")
    ax.plot(p_true, err_raw, color=WARM, lw=3.2, label="Before calibration")
    ax.plot(p_true, err_cal, color=GREEN, lw=3.2, ls="--", label="After calibration")
    ax.axhline(0, color="#5c6b7a", lw=1.2)
    ax.set_xlabel("True pressure (kPa)")
    ax.set_ylabel("Error (% of full scale)")
    ax.set_title("Error before and after calibration")
    ax.set_xlim(0, 100)
    ax.set_ylim(-6.5, 6.5)
    ax.legend(loc="lower right", frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout(pad=1.6)
    save_fig(fig, "linearization.svg")


# ---------------------------------------------------------------------------
# Figure 12 - static fallback for the animation  (hand-built SVG)
# ---------------------------------------------------------------------------


def make_pipeline_static() -> None:
    W, H = 1600, 520
    p = [svg_open(W, H)]

    labels = [
        ("Sense", "transduction"),
        ("Condition", "amplify, filter"),
        ("Convert", "ADC"),
        ("Compute", "calibrate, linearise"),
    ]
    bw, gap = 310, 70
    x0 = 95
    for i, (t, s) in enumerate(labels):
        x = x0 + i * (bw + gap)
        p.append(box(x, 110, bw, 150, [t, s], sizes=[28, 20],
                     fills=[INK, "#40546b"]))
        if i < len(labels) - 1:
            p.append(line(x + bw + 8, 185, x + bw + gap - 8, 185, sw=4, marker="arw"))

    p.append(text(800, 370,
                  "Raw, noisy signal   ->   filtered, linearised, calibrated digital output",
                  size=24, fill="#40546b"))
    p.append(text(800, 430,
                  "Self-test and diagnostics run continuously inside the sensor.",
                  size=21, fill="#40546b"))

    p.append(svg_close())
    write_svg("smart_sensor_pipeline_static.svg", "".join(p))


# ---------------------------------------------------------------------------
# Optional Manim animation
# ---------------------------------------------------------------------------

try:  # pragma: no cover - depends on the local environment
    from manim import (  # type: ignore
        Axes,
        Arrow,
        Create,
        FadeIn,
        GrowArrow,
        ReplacementTransform,
        RIGHT,
        RoundedRectangle,
        Scene,
        Text,
        Transform,
        UP,
        VGroup,
        Write,
        tempconfig,
    )

    MANIM_AVAILABLE = True
except ImportError:  # pragma: no cover
    MANIM_AVAILABLE = False


if MANIM_AVAILABLE:  # pragma: no cover

    class SmartSensorPipeline(Scene):
        """A short animation: raw sensor signal becoming usable digital data."""

        def construct(self):
            self.camera.background_color = "#FFFFFF"
            ink = "#10243a"
            accent = "#1f4e79"
            panel = "#eaf1fb"
            warm = "#c46a12"

            title = Text("From raw signal to usable data", font_size=42, color=ink)
            title.to_edge(UP, buff=0.45)
            self.play(Write(title), run_time=1.0)

            labels = ["Sense", "Condition", "Convert", "Compute"]
            boxes = VGroup()
            for lab in labels:
                rect = RoundedRectangle(
                    corner_radius=0.18,
                    width=2.7,
                    height=1.25,
                    stroke_color=accent,
                    stroke_width=3,
                    fill_color=panel,
                    fill_opacity=1.0,
                )
                txt = Text(lab, font_size=26, color=ink).move_to(rect.get_center())
                boxes.add(VGroup(rect, txt))
            boxes.arrange(RIGHT, buff=0.85)
            boxes.next_to(title, DOWN, buff=0.6)

            arrows = VGroup()
            for i in range(len(boxes) - 1):
                arrows.add(
                    Arrow(
                        boxes[i].get_right(),
                        boxes[i + 1].get_left(),
                        buff=0.12,
                        stroke_width=4,
                        color=accent,
                        max_tip_length_to_length_ratio=0.3,
                    )
                )

            for i, b in enumerate(boxes):
                self.play(FadeIn(b, shift=RIGHT * 0.25), run_time=0.5)
                if i < len(arrows):
                    self.play(GrowArrow(arrows[i]), run_time=0.35)
            self.wait(0.3)

            axes = Axes(
                x_range=[0, 10, 2],
                y_range=[-1.8, 1.8, 1],
                x_length=9.5,
                y_length=2.2,
                axis_config={
                    "color": "#9aa8b8",
                    "stroke_width": 2,
                    "include_ticks": False,
                    "include_tip": False,
                },
            )
            axes.next_to(boxes, DOWN, buff=1.0)

            raw_curve = axes.plot(
                lambda x: np.sin(x) + 0.30 * np.sin(7.0 * x) + 0.15 * np.sin(13.0 * x),
                x_range=[0, 10],
                color=warm,
                stroke_width=3,
            )
            clean_curve = axes.plot(
                lambda x: np.sin(x),
                x_range=[0, 10],
                color=accent,
                stroke_width=5,
            )

            raw_label = Text("raw: noisy, drifting, uncalibrated",
                             font_size=22, color=warm)
            raw_label.next_to(axes, DOWN, buff=0.25)

            self.play(Create(raw_curve), run_time=1.6)
            self.play(FadeIn(raw_label, shift=UP * 0.2), run_time=0.5)
            self.wait(0.8)

            clean_label = Text("filtered, linearised, calibrated",
                               font_size=22, color=accent)
            clean_label.next_to(axes, DOWN, buff=0.25)

            self.play(Transform(raw_curve, clean_curve), run_time=1.6)
            self.play(ReplacementTransform(raw_label, clean_label), run_time=0.6)
            self.wait(0.6)

            status = Text("Self-test passed  |  Digital output ready",
                          font_size=24, color=ink)
            status.next_to(axes, DOWN, buff=1.0)
            self.play(FadeIn(status, shift=UP * 0.2), run_time=0.6)
            self.wait(1.2)


def render_manim() -> None:
    """Render the optional animation and copy it into ./figures."""
    if not MANIM_AVAILABLE:
        print("  [skip] Manim is not installed - no .mp4 asset produced.")
        return

    media_dir = Path("media")
    try:
        with tempconfig(
            {
                "media_dir": str(media_dir),
                "output_file": "smart_sensor_pipeline",
                "frame_rate": 30,
                "pixel_width": 1280,
                "pixel_height": 720,
                "background_color": "#FFFFFF",
                "verbosity": "WARNING",
            }
        ):
            SmartSensorPipeline().render()
    except Exception as exc:  # pragma: no cover
        print(f"  [warn] Manim rendering failed: {exc}")
        return

    matches = sorted(media_dir.rglob("smart_sensor_pipeline.mp4"))
    if not matches:  # pragma: no cover
        print("  [warn] Manim produced no .mp4 file.")
        return

    target = FIGDIR / "smart_sensor_pipeline.mp4"
    shutil.copyfile(matches[0], target)
    print(f"  wrote {target}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    print("Generating visual assets into ./figures ...")
    make_mems_scale()
    make_mems_family()
    make_microfab_flow()
    make_bulk_surface()
    make_sensing_principles()
    make_capacitive_accel()
    make_mems_automotive()
    make_sensor_evolution()
    make_smart_sensor_arch()
    make_fusion_concept()
    make_linearization()
    make_pipeline_static()
    render_manim()
    print("Done.")


if __name__ == "__main__":
    main()