#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Минимальный «кит» для генерации многостраничных .drawio без внешних зависимостей.

Модель: Page → Cell (прямоугольник / ромб / эллипс / текст / полоса) и Edge (ломаная
с точными вершинами). Из одной модели получаем:
  * .drawio (mxfile, несколько страниц, несжатый XML — удобно диффить в git);
  * статичный SVG-превью тем же набором координат (для проверки раскладки и README).

Принципы (см. .claude/skills/drawio-diagrams/SKILL.md):
  * координаты задаются явно — раскладка детерминирована и воспроизводима;
  * связи крепятся к фигурам (source/target + exit/entry), поэтому при ручной правке
    в draw.io стрелки не «отваливаются»;
  * поля процесса (сервис, версия…) лежат в <object> и подставляются в заголовок
    через %placeholders%.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from html import escape
from typing import Dict, List, Optional, Sequence, Tuple

Pt = Tuple[float, float]
Line = Tuple[str, str]  # (text, fmt) fmt: n | b | s | i

FONT = "Helvetica, Arial, sans-serif"


# ---------------------------------------------------------------------------
# Оценка размеров текста (для высоты строк таблиц и переноса в SVG)
# ---------------------------------------------------------------------------
def wrap(text: str, width: float, fs: float, bold: bool = False) -> List[str]:
    per = max(4, int((width - 8) / (fs * (0.60 if bold else 0.56))))
    out: List[str] = []
    for para in text.split("\n"):
        words, cur = para.split(" "), ""
        for w in words:
            if not cur:
                cur = w
            elif len(cur) + 1 + len(w) <= per:
                cur += " " + w
            else:
                out.append(cur)
                cur = w
        out.append(cur)
    return out


def text_height(text: str, width: float, fs: float = 11, bold: bool = False) -> float:
    return len(wrap(text, width, fs, bold)) * (fs + 4) + 8


# ---------------------------------------------------------------------------
# Модель
# ---------------------------------------------------------------------------
@dataclass
class Cell:
    id: str
    kind: str                      # round | rect | diamond | ellipse | text | bar
    x: float
    y: float
    w: float
    h: float
    lines: List[Line] = field(default_factory=list)
    fill: Optional[str] = "#FFFFFF"
    stroke: Optional[str] = "#666666"
    sw: float = 1.0
    dash: bool = False
    fs: float = 11
    align: str = "center"          # left | center | right
    valign: str = "middle"         # top | middle | bottom
    fc: str = "#1B1B3A"
    opacity: Optional[int] = None  # 0..100 для заливки
    attrs: Dict[str, str] = field(default_factory=dict)  # <object> properties
    tooltip: str = ""

    def A(self, side: str, f: float = 0.5) -> Pt:
        if side == "L":
            return (self.x, self.y + self.h * f)
        if side == "R":
            return (self.x + self.w, self.y + self.h * f)
        if side == "T":
            return (self.x + self.w * f, self.y)
        return (self.x + self.w * f, self.y + self.h)

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2


@dataclass
class Edge:
    id: str
    pts: List[Pt]
    src: Optional[Cell] = None
    dst: Optional[Cell] = None
    src_a: Optional[Tuple[str, float]] = None
    dst_a: Optional[Tuple[str, float]] = None
    color: str = "#1B1B3A"
    sw: float = 1.5
    dash: bool = False
    dot: bool = False
    arrow: bool = True
    label: str = ""
    fs: float = 10
    lt: float = 0.5                # положение подписи вдоль ломаной (0..1)


class Page:
    def __init__(self, name: str, width: int, height: int) -> None:
        self.name, self.width, self.height = name, width, height
        self.cells: List[Cell] = []
        self.edges: List[Edge] = []
        self._n = 1

    def nid(self, p: str = "c") -> str:
        self._n += 1
        return f"{p}{self._n}"

    # -- фигуры ------------------------------------------------------------
    def add(self, kind: str, x: float, y: float, w: float, h: float, lines=None, id: str = "", **kw) -> Cell:
        if isinstance(lines, str):
            lines = [(lines, "n")]
        c = Cell(id or self.nid(), kind, x, y, w, h, list(lines or []), **kw)
        self.cells.append(c)
        return c

    def text(self, x, y, w, h, lines, **kw) -> Cell:
        kw.setdefault("fill", None)
        kw.setdefault("stroke", None)
        kw.setdefault("align", "left")
        return self.add("text", x, y, w, h, lines, **kw)

    # -- связи ---------------------------------------------------------------
    def link(self, a: Cell, sa: Tuple[str, float] | str, b: Cell, sb: Tuple[str, float] | str,
             mode: str = "direct", mid: Optional[float] = None, via: Sequence[Pt] = (), **kw) -> Edge:
        sa = (sa, 0.5) if isinstance(sa, str) else sa
        sb = (sb, 0.5) if isinstance(sb, str) else sb
        s, e = a.A(*sa), b.A(*sb)
        if mode == "direct":
            p = [s, e]
        elif mode == "hv":
            p = [s, (e[0], s[1]), e]
        elif mode == "vh":
            p = [s, (s[0], e[1]), e]
        elif mode == "hvh":
            m = mid if mid is not None else (s[0] + e[0]) / 2
            p = [s, (m, s[1]), (m, e[1]), e]
        elif mode == "vhv":
            m = mid if mid is not None else (s[1] + e[1]) / 2
            p = [s, (s[0], m), (e[0], m), e]
        elif mode == "via":
            p = [s, *via, e]
        else:
            raise ValueError(mode)
        ed = Edge(self.nid("e"), _dedupe(p), a, b, sa, sb, **kw)
        self.edges.append(ed)
        return ed

    def free(self, pts: Sequence[Pt], **kw) -> Edge:
        ed = Edge(self.nid("e"), list(pts), **kw)
        self.edges.append(ed)
        return ed


def _dedupe(p: List[Pt]) -> List[Pt]:
    out = [p[0]]
    for q in p[1:]:
        if abs(q[0] - out[-1][0]) > 0.01 or abs(q[1] - out[-1][1]) > 0.01:
            out.append(q)
    return out


# ---------------------------------------------------------------------------
# draw.io XML
# ---------------------------------------------------------------------------
def _html(lines: List[Line], fs: float) -> str:
    out = []
    for t, f in lines:
        t = escape(t, quote=False).replace("\n", "<br>")
        if f == "b":
            t = f"<b>{t}</b>"
        elif f == "s":
            t = f'<font style="font-size:{int(fs - 2)}px" color="#666666">{t}</font>'
        elif f == "i":
            t = f"<i>{t}</i>"
        out.append(t)
    return "<br>".join(out)


def _style(c: Cell) -> str:
    base = {
        "round": "rounded=1;arcSize=10;whiteSpace=wrap;html=1;",
        "rect": "rounded=0;whiteSpace=wrap;html=1;",
        "diamond": "rhombus;whiteSpace=wrap;html=1;",
        "ellipse": "ellipse;whiteSpace=wrap;html=1;",
        "text": "text;html=1;whiteSpace=wrap;",
        "bar": "rounded=0;html=1;",
    }[c.kind]
    s = base
    s += f"fillColor={c.fill or 'none'};strokeColor={c.stroke or 'none'};strokeWidth={c.sw:g};"
    if c.opacity is not None:
        s += f"fillOpacity={c.opacity};"
    if c.dash:
        s += "dashed=1;dashPattern=6 3;"
    s += f"fontSize={c.fs:g};fontColor={c.fc};align={c.align};verticalAlign={c.valign};"
    s += "spacingLeft=4;spacingRight=4;spacingTop=2;spacingBottom=2;"
    return s


def _estyle(e: Edge) -> str:
    s = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;jumpStyle=arc;jumpSize=8;orthogonalLoop=1;"
    s += f"strokeColor={e.color};strokeWidth={e.sw:g};fontSize={e.fs:g};fontColor={e.color};"
    s += "labelBackgroundColor=#FFFFFF;"
    if e.dash:
        s += "dashed=1;dashPattern=6 3;"
    if e.dot:
        s += "dashed=1;dashPattern=2 3;"
    s += "endArrow=classic;endFill=1;" if e.arrow else "endArrow=none;"
    if e.src_a:
        sd, f = e.src_a
        x, y = {"L": (0, f), "R": (1, f), "T": (f, 0), "B": (f, 1)}[sd]
        s += f"exitX={x:g};exitY={y:g};exitDx=0;exitDy=0;"
    if e.dst_a:
        sd, f = e.dst_a
        x, y = {"L": (0, f), "R": (1, f), "T": (f, 0), "B": (f, 1)}[sd]
        s += f"entryX={x:g};entryY={y:g};entryDx=0;entryDy=0;"
    return s


def _q(v: str) -> str:
    return escape(v, quote=True)


def page_xml(p: Page) -> str:
    o = [f'<diagram id="{_q(p.name)}" name="{_q(p.name)}">',
         f'<mxGraphModel dx="1600" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" '
         f'arrows="1" fold="1" page="1" pageScale="1" pageWidth="{p.width}" pageHeight="{p.height}" math="0" shadow="0">',
         '<root><mxCell id="0"/><mxCell id="1" parent="0"/>']
    for c in p.cells:
        val = _html(c.lines, c.fs)
        geo = (f'<mxGeometry x="{c.x:g}" y="{c.y:g}" width="{c.w:g}" height="{c.h:g}" as="geometry"/>')
        if c.attrs:
            at = " ".join(f'{k}="{_q(v)}"' for k, v in c.attrs.items())
            o.append(f'<object label="{_q(val)}" placeholders="1" {at} id="{c.id}">'
                     f'<mxCell style="{_q(_style(c))}" vertex="1" parent="1">{geo}</mxCell></object>')
        else:
            tip = f' tooltip="{_q(c.tooltip)}"' if c.tooltip else ""
            o.append(f'<mxCell id="{c.id}" value="{_q(val)}" style="{_q(_style(c))}" vertex="1" parent="1"{tip}>{geo}</mxCell>')
    for e in p.edges:
        s, t = e.pts[0], e.pts[-1]
        inner = "".join(f'<mxPoint x="{x:g}" y="{y:g}"/>' for x, y in e.pts[1:-1])
        arr = f'<Array as="points">{inner}</Array>' if inner else ""
        if e.src and e.dst:
            ref = f' source="{e.src.id}" target="{e.dst.id}"'
            pts = ""
        else:
            ref = ""
            pts = (f'<mxPoint x="{s[0]:g}" y="{s[1]:g}" as="sourcePoint"/>'
                   f'<mxPoint x="{t[0]:g}" y="{t[1]:g}" as="targetPoint"/>')
        o.append(f'<mxCell id="{e.id}" value="{_q(e.label)}" style="{_q(_estyle(e))}" edge="1" parent="1"{ref}>'
                 f'<mxGeometry x="{2 * e.lt - 1:g}" relative="1" as="geometry">{pts}{arr}</mxGeometry></mxCell>')
    o.append("</root></mxGraphModel></diagram>")
    return "".join(o)


def write_drawio(pages: Sequence[Page], path: str) -> None:
    xml = ('<mxfile host="app.diagrams.net" agent="drawio_kit.py" version="24.7.0">'
           + "".join(page_xml(p) for p in pages) + "</mxfile>\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)


# ---------------------------------------------------------------------------
# SVG-превью
# ---------------------------------------------------------------------------
def _subst(t: str, attrs: Dict[str, str]) -> str:
    for k, v in attrs.items():
        t = t.replace(f"%{k}%", v)
    return t


def _poly_mid(pts: List[Pt], t: float = 0.5) -> Pt:
    segs = [(math.dist(a, b), a, b) for a, b in zip(pts, pts[1:])]
    half = sum(s[0] for s in segs) * t
    for d, a, b in segs:
        if half <= d:
            t = half / d if d else 0
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        half -= d
    return pts[-1]


def page_svg(p: Page) -> str:
    colors = sorted({e.color for e in p.edges})
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{p.width}" height="{p.height}" '
         f'viewBox="0 0 {p.width} {p.height}" font-family="{FONT}">',
         f'<rect width="{p.width}" height="{p.height}" fill="#FFFFFF"/>', "<defs>"]
    for i, col in enumerate(colors):
        o.append(f'<marker id="m{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                 f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>')
    o.append("</defs>")
    for c in p.cells:
        fill = c.fill or "none"
        stroke = c.stroke or "none"
        da = ' stroke-dasharray="6 3"' if c.dash else ""
        op = f' fill-opacity="{c.opacity / 100}"' if c.opacity is not None else ""
        common = f'fill="{fill}"{op} stroke="{stroke}" stroke-width="{c.sw:g}"{da}'
        if c.kind in ("round", "rect", "bar", "text"):
            rx = ' rx="8"' if c.kind == "round" else ""
            if c.kind != "text" or c.fill or c.stroke:
                o.append(f'<rect x="{c.x:g}" y="{c.y:g}" width="{c.w:g}" height="{c.h:g}"{rx} {common}/>')
        elif c.kind == "diamond":
            pts = f"{c.cx:g},{c.y:g} {c.x + c.w:g},{c.cy:g} {c.cx:g},{c.y + c.h:g} {c.x:g},{c.cy:g}"
            o.append(f'<polygon points="{pts}" {common}/>')
        elif c.kind == "ellipse":
            o.append(f'<ellipse cx="{c.cx:g}" cy="{c.cy:g}" rx="{c.w / 2:g}" ry="{c.h / 2:g}" {common}/>')
        # текст
        rows: List[Tuple[str, str]] = []
        for t, f in c.lines:
            t = _subst(t, c.attrs)
            fsz = c.fs - 2 if f == "s" else c.fs
            inner_w = c.w * (0.62 if c.kind == "diamond" else 1)
            for ln in wrap(t, inner_w - 4, fsz, f == "b"):
                rows.append((ln, f))
        if not rows:
            continue
        lh = c.fs + 3
        total = len(rows) * lh
        if c.valign == "top":
            y0 = c.y + 4 + c.fs
        elif c.valign == "bottom":
            y0 = c.y + c.h - total - 2 + c.fs
        else:
            y0 = c.cy - total / 2 + c.fs - 1
        if c.align == "left":
            tx, anchor = c.x + 5, "start"
        elif c.align == "right":
            tx, anchor = c.x + c.w - 5, "end"
        else:
            tx, anchor = c.cx, "middle"
        for i, (ln, f) in enumerate(rows):
            fsz = c.fs - 2 if f == "s" else c.fs
            wgt = ' font-weight="bold"' if f == "b" else ""
            st = ' font-style="italic"' if f == "i" else ""
            col = "#666666" if f == "s" else c.fc
            o.append(f'<text x="{tx:g}" y="{y0 + i * lh:g}" font-size="{fsz:g}" fill="{col}" text-anchor="{anchor}"{wgt}{st}>{escape(ln, quote=False)}</text>')
    for e in p.edges:
        da = ' stroke-dasharray="6 3"' if e.dash else (' stroke-dasharray="2 3"' if e.dot else "")
        mk = f' marker-end="url(#m{colors.index(e.color)})"' if e.arrow else ""
        pts = " ".join(f"{x:g},{y:g}" for x, y in e.pts)
        o.append(f'<polyline points="{pts}" fill="none" stroke="{e.color}" stroke-width="{e.sw:g}"{da}{mk}/>')
        if e.label:
            mx, my = _poly_mid(e.pts, e.lt)
            w = len(e.label) * e.fs * 0.56 + 6
            o.append(f'<rect x="{mx - w / 2:g}" y="{my - e.fs / 2 - 3:g}" width="{w:g}" height="{e.fs + 6:g}" fill="#FFFFFF"/>')
            o.append(f'<text x="{mx:g}" y="{my + e.fs / 2 - 1:g}" font-size="{e.fs:g}" fill="{e.color}" text-anchor="middle">{escape(e.label, quote=False)}</text>')
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------------------
# Таблицы из прямоугольников
# ---------------------------------------------------------------------------
def table(p: Page, x: float, y: float, cols: Sequence[float], rows: Sequence[Sequence[str]],
          header: bool = True, fs: float = 11, hfill: str = "#140093", hstroke: str = "#140093", hfc: str = "#FFFFFF",
          fills: Optional[Dict[Tuple[int, int], str]] = None, min_h: float = 24,
          bold_first_col: bool = False, align: str = "left") -> float:
    """Рисует таблицу; возвращает нижнюю границу (y)."""
    fills = fills or {}
    cy = y
    for r, row in enumerate(rows):
        h = max([min_h] + [text_height(t, cols[i], fs, header and r == 0) for i, t in enumerate(row)])
        cx = x
        for i, t in enumerate(row):
            head = header and r == 0
            fmt = "b" if head or (bold_first_col and i == 0) else "n"
            p.add("rect", cx, cy, cols[i], h, [(t, fmt)] if t else [],
                  fill=fills.get((r, i), hfill if head else "#FFFFFF"),
                  stroke=hstroke if head else "#B0B0B0", fs=fs, align=align, valign="middle",
                  fc=hfc if (head and (r, i) not in fills) else "#1B1B3A")
            cx += cols[i]
        cy += h
    return cy
