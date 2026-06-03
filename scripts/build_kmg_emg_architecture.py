#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the COARSE (укрупнённая) combined КМГ + ЭМГ architecture diagram.

Общая архитектурная схема группы с явным выделением **двух сетевых контуров**
(корпоративная сеть КМГ и сеть ЭМГ). Чтобы схема была читаемой, системы
сгруппированы в **укрупнённые блоки** (по функциям), а интеграции проброшены
на уровне блоков — без множества пересечений. Кросс-сетевые потоки (ЭМГ ↔ КМГ)
выделены оранжевым и проходят через канал между контурами.

Покомпонентная детализация — в C4-схеме docs/svg/09-emg-c4-component.svg.

Источники: матрица интеграций (19 систем, docs/it-landscape-emg-registry.md) и
верхнеуровневая сводная архитектура «КМГ + ЭМГ + интеграции».

Запуск:
    pip install -r requirements.txt
    python3 scripts/build_kmg_emg_architecture.py
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from drawpyo import File, Page
from drawpyo.diagram.edges import Edge
from drawpyo.diagram.objects import Object

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "drawio"
SVG_DIR = ROOT / "docs" / "svg"
PNG_PREVIEW = "/opt/cursor/artifacts/kmg-emg-architecture-preview.png"

# ---------------------------------------------------------------------------
# Стили
# ---------------------------------------------------------------------------
NET_EMG_STYLE = (
    "rounded=1;html=1;fillColor=#EAF7EA;strokeColor=#2E7D32;strokeWidth=3;"
    "verticalAlign=top;align=left;fontStyle=1;fontSize=17;fontColor=#1B5E20;"
    "spacingLeft=18;spacingTop=12;"
)
NET_KMG_STYLE = (
    "rounded=1;html=1;fillColor=#EAF1FB;strokeColor=#1565C0;strokeWidth=3;"
    "verticalAlign=top;align=left;fontStyle=1;fontSize=17;fontColor=#0D3C78;"
    "spacingLeft=18;spacingTop=12;"
)
ACTOR_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#08427B;strokeColor=#073B6F;"
    "fontColor=#ffffff;fontStyle=1;verticalAlign=middle;align=center;fontSize=12;"
)

BLOCK_PALETTE = {
    "emg": ("#D5E8D4", "#5C9A4F"),
    "ot": ("#FFE6CC", "#D79B00"),
    "svc": ("#E6F4E6", "#82B366"),
    "id": ("#B0E3E6", "#0E8088"),
    "sap": ("#FFF2CC", "#D6B656"),
    "doc": ("#E1D5E7", "#9673A6"),
    "nsi": ("#EDEDED", "#8C8C8C"),
    "tr": ("#DAE8FC", "#6C8EBF"),
    "hr": ("#DAE8FC", "#6C8EBF"),
    "sec": ("#F8CECC", "#B85450"),
}

EDGE_SOLID = "#36506B"
EDGE_DASH = "#9673A6"
EDGE_LDAP = "#7E8896"
EDGE_CROSS = "#E8710A"


def block_style(kind: str) -> str:
    fill, stroke = BLOCK_PALETTE.get(kind, BLOCK_PALETTE["tr"])
    return (
        f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
        f"verticalAlign=top;align=left;fontStyle=0;fontSize=11;fontColor=#1A1A1A;"
        f"spacingLeft=12;spacingTop=10;spacingRight=10;strokeWidth=1.5;"
    )


def make_obj(**kwargs) -> Object:
    obj = Object(**kwargs)
    obj.style_attributes = []
    return obj


def L(f=0.5):
    return (0.0, f)


def R(f=0.5):
    return (1.0, f)


def T(f=0.5):
    return (f, 0.0)


def B(f=0.5):
    return (f, 1.0)


def _side_dir(frac):
    fx, fy = frac
    if fy == 0.0:
        return (0, -1)
    if fy == 1.0:
        return (0, 1)
    if fx == 0.0:
        return (-1, 0)
    return (1, 0)


def _ortho_path(a, ad, b, bd):
    ax, ay = a
    bx, by = b
    if ad[0] != 0 and bd[0] != 0:
        mx = (ax + bx) / 2
        return [a, (mx, ay), (mx, by), b]
    if ad[1] != 0 and bd[1] != 0:
        my = (ay + by) / 2
        return [a, (ax, my), (bx, my), b]
    if ad[0] != 0 and bd[1] != 0:
        return [a, (bx, ay), b]
    return [a, (ax, by), b]


class Diagram:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.geo: Dict[int, Tuple[int, int, int, int]] = {}
        self.shapes: List[dict] = []
        self.polylines: List[dict] = []

    def _add(self, obj, x, y, w, h, role="shape", title=None, body=None):
        self.page.add_object(obj)
        self.geo[id(obj)] = (x, y, w, h)
        self.shapes.append({"x": x, "y": y, "w": w, "h": h, "style": obj.baseStyle,
                            "v": obj.value, "role": role, "title": title, "body": body})
        return obj

    def net(self, title, style, x, y, w, h):
        return self._add(make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=style),
                         x, y, w, h, role="net")

    def actor(self, title, x, y, w=240, h=64):
        return self._add(make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=ACTOR_STYLE),
                         x, y, w, h, role="actor")

    def block(self, title, systems, x, y, w, h, kind, per_line=2):
        body_lines = [" · ".join(systems[i:i + per_line]) for i in range(0, len(systems), per_line)]
        value = f"<b>{title}</b><br>" + "<br>".join(body_lines)
        obj = make_obj(value=value, position=(x, y), width=w, height=h, baseStyle=block_style(kind))
        self._add(obj, x, y, w, h, role="block", title=title, body=body_lines)
        return obj

    def text(self, value, x, y, w, h, style, role="text"):
        return self._add(make_obj(value=value, position=(x, y), width=w, height=h, baseStyle=style),
                         x, y, w, h, role=role)

    def anchor(self, obj, fx, fy):
        x, y, w, h = self.geo[id(obj)]
        return (x + fx * w, y + fy * h)

    def route(self, src, exit_frac, tgt, entry_frac, label="", dashed=False, ldap=False,
              bidir=False, cross=False, lpos: Optional[float] = None,
              waypoints: Optional[List[Tuple[int, int]]] = None):
        if cross:
            color, width = EDGE_CROSS, 2
        elif ldap:
            color, width = EDGE_LDAP, 1
        elif dashed:
            color, width = EDGE_DASH, 1
        else:
            color, width = EDGE_SOLID, 1
        edge = Edge(
            source=src, target=tgt, page=self.page, label=label,
            pattern="dashed_medium" if (dashed or ldap) else "solid",
            exitX=exit_frac[0], exitY=exit_frac[1], entryX=entry_frac[0], entryY=entry_frac[1],
            jumpStyle="arc", jumpSize=8, rounded=0,
        )
        edge.strokeColor = color
        if width != 1:
            edge.strokeWidth = width
        if lpos is not None:
            edge.label_position = max(-1.0, min(1.0, 2 * lpos - 1))
        if bidir:
            edge.line_end_source = "classic"
            edge.endFill_source = True
        if waypoints:
            for (wx, wy) in waypoints:
                edge.geometry.add_point(wx, wy)
        self.page.add_object(edge)
        a = self.anchor(src, *exit_frac)
        b = self.anchor(tgt, *entry_frac)
        pts = [a, *waypoints, b] if waypoints else _ortho_path(a, _side_dir(exit_frac), b, _side_dir(entry_frac))
        self.polylines.append({"pts": pts, "label": label, "dashed": dashed or ldap,
                               "color": color, "bidir": bidir, "width": width, "lpos": lpos})


def build() -> Tuple[File, Diagram]:
    f = File(file_name="10-kmg-emg-architecture.drawio", file_path=str(OUT_DIR))
    page = Page(file=f, name="Архитектура КМГ + ЭМГ (укрупнённая, сети и интеграции)", width=1980, height=1180)
    d = Diagram(page)

    # ---------------------------------------------------------------- сети (контуры)
    emg_net = d.net("Сеть ЭМГ — АО «Эмбамунайгаз»", NET_EMG_STYLE, 40, 180, 620, 820)
    kmg_net = d.net("Корпоративная сеть КМГ — АО НК «КазМунайГаз»", NET_KMG_STYLE, 720, 180, 1140, 820)

    # ---------------------------------------------------------------- организационный контур
    emg_org = d.actor("АО «Эмбамунайгаз»\n(владелец процессов ЭМГ)", 180, 40)
    kc = d.actor("КЦ КМГ\n(корпоративный центр)", 1010, 40)
    kmgi = d.actor("КМГ Инжиниринг (КМГИ)", 1380, 40)

    # ---------------------------------------------------------------- блоки ЭМГ
    e_core = d.block(
        "Цифровое ядро ЭМГ",
        ["ИС ABAI", "ИМ · 10.32.10.99", "АСДЦ", "ИС «УТО ЭМГ»"],
        70, 250, 520, 150, "emg", per_line=2,
    )
    e_ot = d.block(
        "Промышленный контур (OT) · телеметрия",
        ["ИСУН", "АСУТП / ТМ", "ТМ АГЗУ", "КУУН НПС-3", "СДМО", "KTM Floboss"],
        70, 440, 520, 170, "ot", per_line=3,
    )
    e_svc = d.block(
        "Локальные сервисы аналитики ЭМГ",
        ["Аналитика :8099", "packet_service", "Распознавание речи"],
        70, 650, 520, 140, "svc", per_line=2,
    )

    # ---------------------------------------------------------------- блоки КМГ
    # колонка A (у канала)
    a_tr = d.block(
        "Транспорт, ОТ и HSE",
        ["ИС «УТО»", "Argus Pro (GPS)", "ИСОТ / ЭНД"],
        750, 250, 330, 150, "tr", per_line=1,
    )
    a_doc = d.block(
        "Документооборот, архив, КХД",
        ["СЭД Directum / САПФИР", "Alfresco (ЭА)", "Электронный архив (Documentum)", "КХД АО НК КМГ"],
        750, 430, 330, 180, "doc", per_line=1,
    )
    # колонка B (центр)
    b_id = d.block(
        "Идентификация (каталог)",
        ["Active Directory (LDAP)"],
        1110, 230, 330, 110, "id", per_line=1,
    )
    b_sap = d.block(
        "SAP ERP и финансы",
        ["SAP ERP", "AVR", "SAS-FM", "FC", "1С (зарплата)", "Нацбанк", "БВУ", "Platts", "ИС ЭСФ", "СИЗ"],
        1110, 370, 330, 240, "sap", per_line=2,
    )
    b_nsi = d.block(
        "НСИ и закупки",
        ["АСУ НСИ", "ИСЭЗ", "Procu / Price", "СДД", "sPoint"],
        1110, 640, 330, 150, "nsi", per_line=2,
    )
    # колонка C (справа)
    c_sec = d.block(
        "Информационная безопасность",
        ["Solar Dozor (DLP)", "Forcepoint Web Gateway", "FUDO PAM", "MS Exchange", "Жулдыз"],
        1470, 250, 330, 170, "sec", per_line=1,
    )
    c_hr = d.block(
        "Кадры и корпоративные порталы",
        ["ПК «Управление персоналом»", "E-Pass", "Портал Team", "Интранет",
         "ИСУП", "Compliance", "БДА", "КГИС"],
        1470, 450, 330, 210, "hr", per_line=2,
    )

    # ---------------------------------------------------------------- владение (организация)
    d.route(emg_org, B(0.5), emg_net, T(0.4), "владеет / эксплуатирует", dashed=True)
    d.route(kc, B(0.5), kmg_net, T(0.25), "корпоративный центр", dashed=True)
    d.route(kmgi, B(0.5), kmg_net, T(0.55), "инжиниринг / проекты", dashed=True)

    # ---------------------------------------------------------------- внутри ЭМГ
    d.route(e_ot, T(0.5), e_core, B(0.5), "телеметрия: OPC UA/DA, Modbus TCP, SQL")
    d.route(e_core, L(0.5), e_svc, L(0.5), "REST :8099 / пакеты / речь",
            waypoints=[(56, 325), (56, 720)])

    # ---------------------------------------------------------------- КРОСС-СЕТЕВЫЕ (ЭМГ ↔ КМГ)
    d.route(e_core, R(0.4), a_tr, L(0.5), "транспорт → SAP; СИЗ/добыча → ИСОТ",
            cross=True, lpos=0.42, waypoints=[(688, 310), (688, 325)])
    d.route(e_core, R(0.6), a_doc, L(0.4), "данные добычи, отчёты",
            cross=True, lpos=0.44, waypoints=[(700, 340), (700, 502)])
    d.route(e_core, R(0.5), b_id, L(0.5), "LDAP (учётные записи ЭМГ)",
            cross=True, lpos=0.2, waypoints=[(676, 325), (676, 415), (1100, 415), (1100, 295)])

    # ---------------------------------------------------------------- внутри КМГ (укрупнённо)
    d.route(a_tr, R(0.5), b_sap, L(0.2), "SOAP XML (транспорт)", bidir=True,
            waypoints=[(1088, 325), (1088, 418)])
    d.route(a_doc, R(0.5), b_sap, L(0.5), "API (договоры/акты)", bidir=True,
            waypoints=[(1092, 520), (1092, 490)])
    d.route(b_sap, B(0.5), b_nsi, T(0.5), "SAP PO / XML · API", bidir=True)
    d.route(b_sap, R(0.5), c_hr, L(0.4), "табельные / зарплата", bidir=True,
            waypoints=[(1455, 490), (1455, 534)])
    d.route(b_nsi, L(0.5), a_doc, R(0.8), "sPoint → КХД (API JSON)",
            waypoints=[(1096, 715), (1096, 574)])
    d.route(c_sec, L(0.5), b_id, R(0.5), "LDAP / доступ", ldap=True, lpos=0.5,
            waypoints=[(1455, 335), (1455, 295)])

    # ---------------------------------------------------------------- легенда
    legend = make_obj(
        value="Легенда", position=(40, 1030), width=1180, height=130,
        baseStyle=("rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#999999;"
                   "verticalAlign=top;align=left;fontStyle=1;spacingLeft=10;spacingTop=6;"),
    )
    d._add(legend, 40, 1030, 1180, 130, role="legend")
    legend_items = [
        ("Цифровое ядро / сервисы ЭМГ", "emg"), ("Промышленный контур (OT)", "ot"),
        ("SAP ERP и финансы", "sap"), ("Документооборот / архив / КХД", "doc"),
        ("НСИ и закупки", "nsi"), ("Информационная безопасность", "sec"),
        ("Идентификация (AD)", "id"), ("Транспорт / кадры / порталы", "tr"),
    ]
    for i, (label, kind) in enumerate(legend_items):
        col, row = i % 4, i // 4
        sx, sy = 60 + col * 290, 1070 + row * 40
        fill, stroke = BLOCK_PALETTE[kind]
        d.text("", sx, sy, 28, 18,
               f"rounded=1;html=1;fillColor={fill};strokeColor={stroke};", role="swatch")
        d.text(label, sx + 34, sy, 250, 18,
               "text;html=1;align=left;verticalAlign=middle;fontSize=11;")

    note = make_obj(
        value=(
            "Контуры сетей: зелёный — сеть ЭМГ, синий — корпоративная сеть КМГ.\n"
            "Оранжевая линия — кросс-сетевая интеграция (ЭМГ ↔ КМГ) через канал между сетями.\n"
            "Двойная стрелка — двусторонний обмен (↔). Серый пунктир — LDAP (единый каталог AD;\n"
            "в нём аутентифицируются все ИС КМГ и ЭМГ). Фиолетовый пунктир — владение.\n"
            "Системы сгруппированы в укрупнённые блоки; покомпонентная детализация интеграций —\n"
            "в C4-схеме docs/svg/09-emg-c4-component.svg."
        ),
        position=(1240, 1030), width=700, height=130,
        baseStyle="text;html=1;align=left;verticalAlign=top;fontSize=10;fontColor=#5A5A5A;spacingLeft=8;spacingTop=8;",
    )
    d._add(note, 1240, 1030, 700, 130, role="note")

    return f, d


def render_svg(d: Diagram, svg_path: Path) -> bool:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle, FancyBboxPatch
    except Exception as exc:  # pragma: no cover
        print(f"SKIP svg preview ({exc})")
        return False

    def color(style, key, default):
        m = re.search(rf"{key}=(#[0-9A-Fa-f]{{6}}|none)", style)
        return m.group(1) if m else default

    fig, ax = plt.subplots(figsize=(19.8, 11.8))
    ax.set_xlim(0, 1980)
    ax.set_ylim(0, 1180)
    ax.invert_yaxis()
    ax.axis("off")

    order = {"net": 0, "block": 1, "legend": 1, "actor": 2, "swatch": 2, "text": 2, "note": 2}
    for s in sorted(d.shapes, key=lambda s: order.get(s["role"], 1)):
        st = s["style"]
        role = s["role"]
        fill = color(st, "fillColor", "#ffffff")
        net = role == "net"
        actor = role == "actor"
        ax.add_patch(Rectangle(
            (s["x"], s["y"]), s["w"], s["h"],
            facecolor="none" if fill == "none" else fill,
            edgecolor=color(st, "strokeColor", "#666666"),
            linewidth=2.6 if net else (1.4 if role in ("block", "legend") else 1.0),
            zorder=order.get(role, 1),
        ))
        if role == "block":
            ax.text(s["x"] + 12, s["y"] + 10, s["title"], ha="left", va="top",
                    fontsize=11.5, fontweight="bold", color="#13243a", zorder=3)
            for j, line in enumerate(s["body"]):
                ax.text(s["x"] + 12, s["y"] + 34 + j * 18, line, ha="left", va="top",
                        fontsize=9, color="#222222", zorder=3)
            continue
        txt = (s["v"].replace("&#xa;", "\n").replace("&lt;", "<").replace("&gt;", ">")) if s["v"] else ""
        top = "verticalAlign=top" in st
        ax.text(
            (s["x"] + 12) if top else s["x"] + s["w"] / 2,
            (s["y"] + 9) if top else s["y"] + s["h"] / 2,
            txt, ha="left" if top else "center", va="top" if top else "center",
            fontsize=13 if net else (8.5 if role == "note" else (11 if top else 10)),
            color="#ffffff" if actor else (color(st, "fontColor", "#000000") if (net or top) else "#000000"),
            fontweight="bold" if (actor or net or (top and role != "note")) else "normal", zorder=3,
        )

    for e in d.polylines:
        pts = e["pts"]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        c = e["color"]
        lw = 1.1 + 0.8 * (e["width"] - 1)
        ax.plot(xs, ys, color=c, lw=lw, ls="--" if e["dashed"] else "-", zorder=4, alpha=0.95)
        ax.annotate("", xy=pts[-1], xytext=pts[-2],
                    arrowprops=dict(arrowstyle="->", color=c, lw=lw), zorder=4)
        if e.get("bidir"):
            ax.annotate("", xy=pts[0], xytext=pts[1],
                        arrowprops=dict(arrowstyle="->", color=c, lw=lw), zorder=4)
        if e["label"]:
            if e.get("lpos") is not None:
                seglens = [((pts[i + 1][0] - pts[i][0]) ** 2 + (pts[i + 1][1] - pts[i][1]) ** 2) ** 0.5
                           for i in range(len(pts) - 1)]
                total = sum(seglens) or 1.0
                target = e["lpos"] * total
                acc = 0.0
                mid = pts[len(pts) // 2]
                for i, sl in enumerate(seglens):
                    if acc + sl >= target:
                        t = (target - acc) / (sl or 1.0)
                        mid = (pts[i][0] + t * (pts[i + 1][0] - pts[i][0]),
                               pts[i][1] + t * (pts[i + 1][1] - pts[i][1]))
                        break
                    acc += sl
            else:
                mid = pts[len(pts) // 2]
            ax.text(mid[0], mid[1], e["label"], fontsize=7, color="#12325f",
                    ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#cccccc", alpha=0.9), zorder=5)

    svg_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(svg_path, format="svg", bbox_inches="tight")
    try:
        fig.savefig(PNG_PREVIEW, dpi=120, bbox_inches="tight")
    except Exception:
        pass
    plt.close(fig)
    print(f"OK svg preview -> {svg_path}")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    f, d = build()
    out = f.write(overwrite=True)
    print(f"OK 10-kmg-emg-architecture -> {out}")
    render_svg(d, SVG_DIR / "10-kmg-emg-architecture.svg")


if __name__ == "__main__":
    main()
