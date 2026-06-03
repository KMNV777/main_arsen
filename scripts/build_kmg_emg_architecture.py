#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the combined КМГ + ЭМГ architecture diagram with network boundaries.

Общая архитектурная схема группы: явно выделены **корпоративная сеть КМГ**
(АО НК КМГ — общие корпоративные ИС) и **сеть ЭМГ** (АО «Эмбамунайгаз» —
цифровое ядро, промышленный контур OT и локальные сервисы). Между сетями и
внутри них «проброшены» интеграции систем и компонентов: кросс-сетевые потоки
выделены отдельным цветом и проходят через канал между контурами сетей.

Источники данных:
  * матрица интеграций (19 систем) — docs/it-landscape-emg-registry.md;
  * верхнеуровневая сводная архитектура «КМГ + ЭМГ + интеграции»;
  * компонентная C4-схема ЭМГ (docs/svg/09-emg-c4-component.svg) и ABAI.

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
# Геометрия
# ---------------------------------------------------------------------------
COMP_W, COMP_H = 176, 52
GAP_X, GAP_Y = 18, 14
PAD_SIDE, PAD_TOP, PAD_BOT = 16, 40, 14

# ---------------------------------------------------------------------------
# Стили
# ---------------------------------------------------------------------------
NET_EMG_STYLE = (
    "rounded=1;html=1;fillColor=#EAF7EA;strokeColor=#2E7D32;strokeWidth=3;"
    "verticalAlign=top;align=left;fontStyle=1;fontSize=16;fontColor=#1B5E20;"
    "spacingLeft=16;spacingTop=10;"
)
NET_KMG_STYLE = (
    "rounded=1;html=1;fillColor=#EAF1FB;strokeColor=#1565C0;strokeWidth=3;"
    "verticalAlign=top;align=left;fontStyle=1;fontSize=16;fontColor=#0D3C78;"
    "spacingLeft=16;spacingTop=10;"
)
CONTAINER_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#F4F7FB;strokeColor=#8497B0;"
    "verticalAlign=top;align=left;fontStyle=1;fontSize=11;fontColor=#23364B;"
    "spacingLeft=10;spacingTop=6;spacingRight=8;"
)
ACTOR_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#08427B;strokeColor=#073B6F;"
    "fontColor=#ffffff;fontStyle=1;verticalAlign=middle;align=center;fontSize=12;"
)

COMP_PALETTE = {
    "emg": ("#D5E8D4", "#82B366"),
    "ot": ("#FFE6CC", "#D79B00"),
    "svc": ("#D5E8D4", "#82B366"),
    "erp": ("#FFF2CC", "#D6B656"),
    "doc": ("#E1D5E7", "#9673A6"),
    "nsi": ("#F5F5F5", "#999999"),
    "sec": ("#F8CECC", "#B85450"),
    "id": ("#B0E3E6", "#0E8088"),
    "hr": ("#DAE8FC", "#6C8EBF"),
    "tr": ("#DAE8FC", "#6C8EBF"),
}

EDGE_SOLID = "#36506B"
EDGE_DASH = "#9673A6"
EDGE_LDAP = "#9AA4AE"
EDGE_CROSS = "#E8710A"


def comp_style(kind: str) -> str:
    if kind == "actor":
        return ACTOR_STYLE
    fill, stroke = COMP_PALETTE.get(kind, COMP_PALETTE["hr"])
    return (
        f"shape=module;jettyWidth=14;jettyHeight=6;whiteSpace=wrap;html=1;"
        f"fillColor={fill};strokeColor={stroke};fontSize=10;verticalAlign=middle;"
        f"align=center;spacingLeft=6;spacingRight=4;"
    )


def make_obj(**kwargs) -> Object:
    obj = Object(**kwargs)
    obj.style_attributes = []
    return obj


def container_dims(n: int, cols: int, w: int) -> Tuple[int, int]:
    rows = max(1, -(-n // cols))
    W = PAD_SIDE * 2 + cols * w + (cols - 1) * GAP_X
    H = PAD_TOP + rows * COMP_H + (rows - 1) * GAP_Y + PAD_BOT
    return W, H


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

    def _add(self, obj, x, y, w, h):
        self.page.add_object(obj)
        self.geo[id(obj)] = (x, y, w, h)
        self.shapes.append({"x": x, "y": y, "w": w, "h": h, "style": obj.baseStyle, "v": obj.value})
        return obj

    def net(self, title, style, x, y, w, h):
        return self._add(make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=style), x, y, w, h)

    def actor(self, title, x, y, w=240, h=64):
        return self._add(make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=ACTOR_STYLE), x, y, w, h)

    def container(self, title, x, y, comps, cols, comp_w=COMP_W):
        w, h = container_dims(len(comps), cols, comp_w)
        box = self._add(make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=CONTAINER_STYLE), x, y, w, h)
        objs: Dict[str, Object] = {}
        for i, (label, kind) in enumerate(comps):
            col, row = i % cols, i // cols
            cx = x + PAD_SIDE + col * (comp_w + GAP_X)
            cy = y + PAD_TOP + row * (COMP_H + GAP_Y)
            node = make_obj(value=f"«component»\n{label}", position=(cx, cy), width=comp_w, height=COMP_H,
                            baseStyle=comp_style(kind))
            self._add(node, cx, cy, comp_w, COMP_H)
            objs[label] = node
        return box, objs

    def anchor(self, obj, fx, fy):
        x, y, w, h = self.geo[id(obj)]
        return (x + fx * w, y + fy * h)

    def route(self, src, exit_frac, tgt, entry_frac, label="", dashed=False, ldap=False,
              bidir=False, cross=False, waypoints: Optional[List[Tuple[int, int]]] = None):
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
                               "color": color, "bidir": bidir, "width": width})


def build() -> Tuple[File, Diagram]:
    f = File(file_name="10-kmg-emg-architecture.drawio", file_path=str(OUT_DIR))
    page = Page(file=f, name="Архитектура КМГ + ЭМГ (сети и интеграции)", width=2760, height=1420)
    d = Diagram(page)

    # ---------------------------------------------------------------- сети (контуры)
    # широкий канал (800..1060) между сетями и широкие коридоры между колонками,
    # чтобы каждая связь шла по своей полосе и линии не накладывались.
    emg_net = d.net("Сеть ЭМГ — АО «Эмбамунайгаз»",
                    NET_EMG_STYLE, 40, 200, 760, 1000)
    kmg_net = d.net("Корпоративная сеть КМГ — АО НК «КазМунайГаз»",
                    NET_KMG_STYLE, 1060, 200, 1602, 1000)

    # ---------------------------------------------------------------- организационный контур
    emg_org = d.actor("АО «Эмбамунайгаз»\n(владелец процессов ЭМГ)", 300, 60)
    kc = d.actor("КЦ КМГ\n(корпоративный центр)", 1350, 60)
    kmgi = d.actor("КМГ Инжиниринг\n(КМГИ)", 1850, 60)

    # ---------------------------------------------------------------- ЭМГ: контейнеры
    _, core = d.container(
        "Ядро цифровизации ЭМГ", 70, 270,
        [("ИС ABAI", "emg"), ("ИС «УТО ЭМГ»", "emg"), ("АСДЦ", "emg"), ("ИМ · cmv2\n10.32.10.99", "emg")],
        cols=1, comp_w=260,
    )
    ot_box, ot = d.container(
        "Промышленный контур (OT) · телеметрия", 70, 610,
        [("ИСУН", "ot"), ("АСУТП / ТМ", "ot"), ("ТМ АГЗУ", "ot"),
         ("КУУН НПС-3", "ot"), ("СДМО", "ot"), ("KTM Floboss", "ot")],
        cols=2,
    )
    _, svc = d.container(
        "Локальные сервисы аналитики ЭМГ", 70, 884,
        [("Аналитика ЭМГ\n108.181.186.12:8099", "svc"),
         ("packet_service\n10.32.10.90:8951", "svc"),
         ("Распознавание речи\n10.32.10.90:8777", "svc")],
        cols=1, comp_w=360,
    )

    # ---------------------------------------------------------------- КМГ: контейнеры
    _, idc = d.container(
        "Идентификация (каталог)", 1090, 270,
        [("Active Directory\n(LDAP)", "id")], cols=1, comp_w=300,
    )
    _, tr = d.container(
        "Транспорт, ОТ и HSE", 1090, 430,
        [("ИС «УТО»", "tr"), ("Argus Pro (GPS)", "tr"), ("ИСОТ / ЭНД", "tr")],
        cols=1, comp_w=300,
    )
    _, dk = d.container(
        "Документооборот, архив, КХД", 1090, 720,
        [("СЭД Directum /\nСАПФИР", "doc"), ("Alfresco (ЭА)", "doc"),
         ("Электронный архив\n(Азия-Софт)", "doc"), ("КХД АО НК КМГ", "doc")],
        cols=1, comp_w=300,
    )
    _, erp = d.container(
        "ERP и финансы (SAP ERP — хаб группы)",
        1592, 270,
        [("SAP ERP", "erp"), ("AVR", "erp"), ("SAS-FM", "erp"), ("FC · фин.\nконсолидация", "erp"),
         ("1С (зарплата)", "erp"), ("Нацбанк", "erp"), ("БВУ (банк)", "erp"), ("Platts.com", "erp"),
         ("ИС ЭСФ", "erp"), ("СИЗ", "erp")],
        cols=2,
    )
    _, nsi = d.container(
        "НСИ и закупки", 1592, 700,
        [("АСУ НСИ", "nsi"), ("ИСЭЗ", "nsi"), ("Procu / Price", "nsi"), ("СДД", "nsi"), ("sPoint", "nsi")],
        cols=2,
    )
    _, sec = d.container(
        "Информационная безопасность", 2192, 270,
        [("Solar Dozor\n(DLP)", "sec"), ("Forcepoint\nWeb Gateway", "sec"), ("FUDO PAM", "sec"),
         ("MS Exchange", "sec"), ("Жулдыз", "sec")],
        cols=2,
    )
    _, hrp = d.container(
        "Кадры и корпоративные порталы", 2192, 560,
        [("ПК «Управление\nперсоналом»", "hr"), ("E-Pass", "hr"), ("Портал Team", "hr"),
         ("Интранет", "hr"), ("ИСУП", "hr"), ("Compliance", "hr"), ("БДА", "hr"), ("КГИС", "hr")],
        cols=2,
    )

    # короткие имена
    ABAI = core["ИС ABAI"]
    ASDC = core["АСДЦ"]
    UTOE = core["ИС «УТО ЭМГ»"]
    IM = core["ИМ · cmv2\n10.32.10.99"]
    AD = idc["Active Directory\n(LDAP)"]
    UTO = tr["ИС «УТО»"]
    ISOT = tr["ИСОТ / ЭНД"]
    ARGUS = tr["Argus Pro (GPS)"]
    SAPFIR = dk["СЭД Directum /\nСАПФИР"]
    DOCM = dk["Электронный архив\n(Азия-Софт)"]
    KHD = dk["КХД АО НК КМГ"]
    SAP = erp["SAP ERP"]
    AVR = erp["AVR"]
    SASFM = erp["SAS-FM"]
    NSI = nsi["АСУ НСИ"]
    ISEZ = nsi["ИСЭЗ"]
    PROCU = nsi["Procu / Price"]
    SPOINT = nsi["sPoint"]
    PKUP = hrp["ПК «Управление\nперсоналом»"]
    EPASS = hrp["E-Pass"]
    SOLAR = sec["Solar Dozor\n(DLP)"]
    FORCE = sec["Forcepoint\nWeb Gateway"]
    EXCH = sec["MS Exchange"]

    # ---------------------------------------------------------------- владение (организация)
    d.route(emg_org, B(0.5), emg_net, T(0.4), "владеет / эксплуатирует", dashed=True)
    d.route(kc, B(0.5), kmg_net, T(0.22), "корпоративный центр", dashed=True)
    d.route(kmgi, B(0.5), kmg_net, T(0.5), "инжиниринг / проекты", dashed=True)

    # ---------------------------------------------------------------- внутри ЭМГ
    d.route(ot_box, T(0.4), IM, B(0.5), "телеметрия: OPC UA/DA, Modbus TCP, SQL (раздел 19)")
    d.route(ABAI, R(0.5), IM, R(0.5), "SQL — фонд скважин, режимы",
            waypoints=[(600, 336), (600, 534)])
    d.route(ASDC, B(0.5), IM, T(0.5), "диспетчеризация", dashed=True)
    d.route(IM, L(0.5), svc["Аналитика ЭМГ\n108.181.186.12:8099"], L(0.5),
            "REST JSON :8099 / пакеты / речь", waypoints=[(56, 534), (56, 950)])

    # ---------------------------------------------------------------- КРОСС-СЕТЕВЫЕ (ЭМГ ↔ КМГ) — отдельные полосы канала
    d.route(UTOE, R(0.5), UTO, L(0.5), "локальный контур → SAP", cross=True,
            waypoints=[(840, 402), (840, 496)])
    d.route(ABAI, R(0.6), ISOT, L(0.5), "СИЗ / нарушения / добыча", cross=True,
            waypoints=[(890, 346), (890, 628)])
    d.route(ABAI, R(0.4), SAPFIR, L(0.5), "пользователи / отчёты", cross=True, dashed=True,
            waypoints=[(940, 331), (940, 786)])
    d.route(ABAI, R(0.7), KHD, L(0.5), "данные добычи", cross=True,
            waypoints=[(990, 352), (990, 984)])
    d.route(ABAI, R(0.3), AD, L(0.5), "LDAP (учётные записи ЭМГ)", cross=True,
            waypoints=[(1040, 326), (1040, 336)])

    # ---------------------------------------------------------------- внутри КМГ
    # колонка A ↔ колонка B (SAP) — коридор gutter1 (1422..1592), отдельные полосы
    d.route(UTO, R(0.5), SAP, L(0.5), "SOAP XML", bidir=True,
            waypoints=[(1490, 496), (1490, 336)])
    d.route(ARGUS, R(0.5), UTO, R(0.5), "REST JSON (GPS)", waypoints=[(1450, 562), (1450, 496)])
    d.route(SAP, R(0.5), AVR, L(0.5), "API XML", bidir=True)
    d.route(SASFM, L(0.5), SAP, L(0.7), "RFC / .sas7bdat / CSV",
            waypoints=[(1576, 402), (1576, 346)])
    d.route(DOCM, R(0.5), SAP, L(0.6), "API (договоры/акты)", bidir=True,
            waypoints=[(1530, 918), (1530, 341)])
    d.route(SPOINT, L(0.5), KHD, R(0.5), "sPoint → КХД (API JSON)",
            waypoints=[(1564, 898), (1564, 984)])
    d.route(SAPFIR, L(0.5), KHD, L(0.5), "REST JSON", waypoints=[(1080, 786), (1080, 984)])
    # колонка B ↔ колонка C — коридор gutter2 (2022..2192), отдельные полосы
    d.route(SAP, R(0.6), NSI, T(0.5), "SAP PO / XML", bidir=True,
            waypoints=[(2050, 346), (2050, 712), (1696, 712)])
    d.route(PKUP, L(0.5), SAP, T(0.5), "SOAP / DB · табельные", bidir=True,
            waypoints=[(2130, 626), (2130, 250), (1696, 250)])
    d.route(PROCU, R(0.3), ISEZ, R(0.5), "API JSON", bidir=True,
            waypoints=[(2090, 825), (2090, 766)])
    d.route(PROCU, T(0.5), NSI, B(0.5), "API JSON", bidir=True)

    # ---------------------------------------------------------------- ИБ
    d.route(EXCH, L(0.5), SOLAR, R(0.8), "BCC (почта)", dashed=True,
            waypoints=[(2393, 402), (2393, 352)])
    d.route(FORCE, L(0.5), SOLAR, R(0.3), "ICAP (веб)", dashed=True)

    # ---------------------------------------------------------------- LDAP → AD (единый каталог)
    d.route(SOLAR, T(0.5), AD, B(0.3), "LDAP", ldap=True,
            waypoints=[(2296, 228), (1196, 228)])
    d.route(EPASS, R(0.5), AD, B(0.6), "LDAP", ldap=True,
            waypoints=[(2650, 626), (2650, 234), (1286, 234)])
    d.route(SAPFIR, L(0.8), AD, L(0.7), "LDAP", ldap=True,
            waypoints=[(1075, 802), (1075, 346)])

    # ---------------------------------------------------------------- легенда
    legend = make_obj(
        value="Легенда", position=(40, 1240), width=1640, height=150,
        baseStyle=("rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#999999;"
                   "verticalAlign=top;align=left;fontStyle=1;spacingLeft=10;spacingTop=6;"),
    )
    d._add(legend, 40, 1240, 1640, 150)
    legend_items = [
        ("Ядро / сервисы ЭМГ", "emg"), ("Промышленный контур (OT)", "ot"),
        ("ERP / финансы (SAP)", "erp"), ("Документооборот / архив", "doc"),
        ("НСИ / закупки", "nsi"), ("Информационная безопасность", "sec"),
        ("Идентификация (AD)", "id"), ("Кадры / транспорт / порталы", "hr"),
    ]
    for i, (label, kind) in enumerate(legend_items):
        col, row = i % 4, i // 4
        sx, sy = 60 + col * 405, 1280 + row * 44
        d._add(make_obj(value="", position=(sx, sy), width=30, height=20, baseStyle=comp_style(kind)), sx, sy, 30, 20)
        tx, ty = 98 + col * 405, 1280 + row * 44
        d._add(make_obj(value=label, position=(tx, ty), width=290, height=20,
                        baseStyle="text;html=1;align=left;verticalAlign=middle;fontSize=11;"), tx, ty, 290, 20)

    note = make_obj(
        value=(
            "Контуры сетей: зелёный — сеть ЭМГ, синий — корпоративная сеть КМГ.\n"
            "Оранжевая линия — кросс-сетевая интеграция (ЭМГ ↔ КМГ) через канал между сетями.\n"
            "Двойная стрелка — двусторонний обмен (↔). Серый пунктир — LDAP (единый каталог AD).\n"
            "Фиолетовый пунктир — служебные / асинхронные потоки (диспетчеризация, владение).\n"
            "Покомпонентная детализация интеграций — в C4-схеме docs/svg/09-emg-c4-component.svg."
        ),
        position=(1740, 1240), width=940, height=150,
        baseStyle="text;html=1;align=left;verticalAlign=top;fontSize=10;fontColor=#5A5A5A;spacingLeft=8;spacingTop=8;",
    )
    d._add(note, 1740, 1240, 940, 150)

    return f, d


def render_svg(d: Diagram, svg_path: Path) -> bool:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
    except Exception as exc:  # pragma: no cover
        print(f"SKIP svg preview ({exc})")
        return False

    def color(style, key, default):
        m = re.search(rf"{key}=(#[0-9A-Fa-f]{{6}}|none)", style)
        return m.group(1) if m else default

    fig, ax = plt.subplots(figsize=(27.6, 14.2))
    ax.set_xlim(0, 2760)
    ax.set_ylim(0, 1420)
    ax.invert_yaxis()
    ax.axis("off")

    def z(s):
        st = s["style"]
        if "strokeWidth=3" in st:
            return 0
        if "fillColor=#F4F7FB" in st:
            return 1
        return 2

    for s in sorted(d.shapes, key=z):
        st = s["style"]
        fill = color(st, "fillColor", "#ffffff")
        module = "shape=module" in st
        actor = "fillColor=#08427B" in st
        net = "strokeWidth=3" in st
        ax.add_patch(Rectangle(
            (s["x"], s["y"]), s["w"], s["h"],
            facecolor="none" if fill == "none" else fill,
            edgecolor=color(st, "strokeColor", "#666666"),
            linewidth=2.4 if net else 1.1, zorder=(0 if net else (2 if module else 1)),
        ))
        txt = (s["v"].replace("&#xa;", "\n").replace("&lt;", "<").replace("&gt;", ">")) if s["v"] else ""
        top = "verticalAlign=top" in st
        ax.text(
            (s["x"] + 10) if top else s["x"] + s["w"] / 2,
            (s["y"] + 8) if top else s["y"] + s["h"] / 2,
            txt, ha="left" if top else "center", va="top" if top else "center",
            fontsize=8 if module else (12 if net else (9 if top else 9)),
            color="#ffffff" if actor else (color(st, "fontColor", "#000000") if (net or top) else "#000000"),
            fontweight="bold" if (actor or top or net) else "normal", zorder=3,
        )

    for e in d.polylines:
        pts = e["pts"]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        c = e["color"]
        lw = 1.0 + 0.7 * (e["width"] - 1)
        ax.plot(xs, ys, color=c, lw=lw, ls="--" if e["dashed"] else "-", zorder=4, alpha=0.95)
        ax.annotate("", xy=pts[-1], xytext=pts[-2],
                    arrowprops=dict(arrowstyle="->", color=c, lw=lw), zorder=4)
        if e.get("bidir"):
            ax.annotate("", xy=pts[0], xytext=pts[1],
                        arrowprops=dict(arrowstyle="->", color=c, lw=lw), zorder=4)
        if e["label"]:
            mid = pts[len(pts) // 2]
            ax.text(mid[0], mid[1], e["label"], fontsize=6, color="#16407a",
                    ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85), zorder=5)

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
