#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the C4 Component diagram of the КМГ + ЭМГ landscape (by network segment).

C4-нотация поверх реальной сетевой топологии: системы показаны как
«component» и сгруппированы по сетевым границам (КСПД КМГ, КСПД ЭМГ / АУП,
ТСПД НГДУ). Связи — отношения C4 с протоколом/форматом. Сетевая обвязка
(МСЭ, криптошлюзы, маршрутизаторы, облака ЕСПД/L2VPN) на C4-схеме не
показывается — транспорт отражён в подписях связей и заголовках границ.

Запуск:
    pip install -r requirements.txt
    python3 scripts/build_kmg_emg_c4_component.py
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
PNG_PREVIEW = "/opt/cursor/artifacts/kmg-emg-c4-component-preview.png"

# --------------------------------------------------------------------------- геометрия
COMP_W, COMP_H = 158, 50
GAP_X, GAP_Y = 14, 10
PAD_SIDE, PAD_TOP, PAD_BOT = 14, 34, 12

# --------------------------------------------------------------------------- стили (C4)
BND_KMG = ("rounded=1;html=1;dashed=1;dashPattern=10 6;fillColor=#F2F6FC;strokeColor=#1565C0;strokeWidth=2;"
           "verticalAlign=top;align=left;fontStyle=1;fontSize=15;fontColor=#0D3C78;spacingLeft=14;spacingTop=8;")
BND_EMG = ("rounded=1;html=1;dashed=1;dashPattern=10 6;fillColor=#F1FAF1;strokeColor=#2E7D32;strokeWidth=2;"
           "verticalAlign=top;align=left;fontStyle=1;fontSize=15;fontColor=#1B5E20;spacingLeft=14;spacingTop=8;")
BND_NGDU = ("rounded=1;html=1;dashed=1;dashPattern=10 6;fillColor=#FFF8EF;strokeColor=#D9760A;strokeWidth=2;"
            "verticalAlign=top;align=left;fontStyle=1;fontSize=15;fontColor=#8A4B00;spacingLeft=14;spacingTop=8;")
BND_EXT = ("rounded=1;html=1;dashed=1;dashPattern=10 6;fillColor=#F5F5F5;strokeColor=#9E9E9E;strokeWidth=2;"
           "verticalAlign=top;align=left;fontStyle=1;fontSize=13;fontColor=#555;spacingLeft=12;spacingTop=8;")
CONTAINER = ("rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#8497B0;"
             "verticalAlign=top;align=left;fontStyle=1;fontSize=11;fontColor=#23364B;spacingLeft=8;spacingTop=5;")
PERSON = ("rounded=0;whiteSpace=wrap;html=1;shape=umlActor;fillColor=#08427B;strokeColor=#073B6F;"
          "fontColor=#08427B;fontStyle=1;verticalLabelPosition=bottom;verticalAlign=top;fontSize=11;")
PERSON_BOX = ("rounded=12;whiteSpace=wrap;html=1;fillColor=#08427B;strokeColor=#073B6F;"
              "fontColor=#ffffff;fontStyle=1;verticalAlign=middle;align=center;fontSize=11;")

COMP_PALETTE = {
    "kc": ("#B3C7E6", "#3F5F8F"), "nedra": ("#B0E3E6", "#0E8088"), "id": ("#FFE0B2", "#E08A00"),
    "corp": ("#DAE8FC", "#6C8EBF"), "emg": ("#D5E8D4", "#5C9A4F"), "srv": ("#C8E6C9", "#519657"),
    "app": ("#DCEAF7", "#6C8EBF"), "sec": ("#F8CECC", "#B85450"), "ot": ("#FFE6CC", "#D79B00"),
    "ext": ("#EEEEEE", "#9E9E9E"),
}

EDGE_INT = "#1565C0"
EDGE_OT = "#E8710A"
EDGE_LDAP = "#7E8896"


def comp_style(kind):
    fill, stroke = COMP_PALETTE.get(kind, COMP_PALETTE["app"])
    return (f"shape=module;jettyWidth=12;jettyHeight=6;whiteSpace=wrap;html=1;fillColor={fill};"
            f"strokeColor={stroke};fontSize=8;verticalAlign=middle;align=center;spacingLeft=4;spacingRight=2;")


def make_obj(**kwargs):
    obj = Object(**kwargs)
    obj.style_attributes = []
    return obj


def container_dims(n, cols, w):
    rows = max(1, -(-n // cols))
    return (PAD_SIDE * 2 + cols * w + (cols - 1) * GAP_X,
            PAD_TOP + rows * COMP_H + (rows - 1) * GAP_Y + PAD_BOT)


def L(f=0.5):
    return (0.0, f)


def R(f=0.5):
    return (1.0, f)


def T(f=0.5):
    return (f, 0.0)


def B(f=0.5):
    return (f, 1.0)


def _sd(frac):
    fx, fy = frac
    if fy == 0.0:
        return (0, -1)
    if fy == 1.0:
        return (0, 1)
    if fx == 0.0:
        return (-1, 0)
    return (1, 0)


def _ortho(a, ad, b, bd):
    ax, ay = a
    bx, by = b
    if ad[0] and bd[0]:
        mx = (ax + bx) / 2
        return [a, (mx, ay), (mx, by), b]
    if ad[1] and bd[1]:
        my = (ay + by) / 2
        return [a, (ax, my), (bx, my), b]
    if ad[0] and bd[1]:
        return [a, (bx, ay), b]
    return [a, (ax, by), b]


class Diagram:
    def __init__(self, page):
        self.page = page
        self.geo = {}
        self.shapes = []
        self.polylines = []

    def _add(self, obj, x, y, w, h, role="shape"):
        self.page.add_object(obj)
        self.geo[id(obj)] = (x, y, w, h)
        self.shapes.append({"x": x, "y": y, "w": w, "h": h, "style": obj.baseStyle, "v": obj.value, "role": role})
        return obj

    def boundary(self, title, style, x, y, w, h):
        return self._add(make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=style), x, y, w, h, "bnd")

    def person(self, title, x, y, w=210, h=70):
        return self._add(make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=PERSON_BOX), x, y, w, h, "person")

    def container(self, title, x, y, comps, cols, comp_w=COMP_W):
        w, h = container_dims(len(comps), cols, comp_w)
        box = self._add(make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=CONTAINER), x, y, w, h, "container")
        objs = {}
        for i, (label, kind) in enumerate(comps):
            col, row = i % cols, i // cols
            cx = x + PAD_SIDE + col * (comp_w + GAP_X)
            cy = y + PAD_TOP + row * (COMP_H + GAP_Y)
            node = make_obj(value=f"«component»\n{label}", position=(cx, cy), width=comp_w, height=COMP_H,
                            baseStyle=comp_style(kind))
            self._add(node, cx, cy, comp_w, COMP_H, "comp")
            objs[label] = node
        return box, objs

    def anchor(self, obj, fx, fy):
        x, y, w, h = self.geo[id(obj)]
        return (x + fx * w, y + fy * h)

    def route(self, src, ef, tgt, en, label="", kind="int", bidir=False, lpos=None,
              waypoints: Optional[List[Tuple[int, int]]] = None):
        color = {"int": EDGE_INT, "ot": EDGE_OT, "ldap": EDGE_LDAP}[kind]
        dash = kind == "ldap"
        edge = Edge(source=src, target=tgt, page=self.page, label=label,
                    pattern="dashed_medium" if dash else "solid",
                    exitX=ef[0], exitY=ef[1], entryX=en[0], entryY=en[1],
                    jumpStyle="arc", jumpSize=8, rounded=0)
        edge.strokeColor = color
        if lpos is not None:
            edge.label_position = max(-1.0, min(1.0, 2 * lpos - 1))
        if bidir:
            edge.line_end_source = "classic"
            edge.endFill_source = True
        if waypoints:
            for wx, wy in waypoints:
                edge.geometry.add_point(wx, wy)
        self.page.add_object(edge)
        a = self.anchor(src, *ef)
        b = self.anchor(tgt, *en)
        pts = [a, *waypoints, b] if waypoints else _ortho(a, _sd(ef), b, _sd(en))
        self.polylines.append({"pts": pts, "label": label, "dashed": dash, "color": color,
                               "bidir": bidir, "lpos": lpos})


def build():
    f = File(file_name="11-kmg-emg-c4-component.drawio", file_path=str(OUT_DIR))
    page = Page(file=f, name="C4 Component — КМГ + ЭМГ (по сетевым контурам)", width=2400, height=1640)
    d = Diagram(page)

    # ===================================================================== границы (C4 boundaries)
    d.boundary("Граница сети: КСПД КМГ — корпоративная сеть АО НК «КазМунайГаз» (доступ ЭМГ по ЕСПД)", BND_KMG, 40, 120, 1880, 410)
    d.boundary("Граница сети: КСПД ЭМГ — АУП АО «Эмбамунайгаз»", BND_EMG, 40, 610, 1880, 540)
    d.boundary("Граница сети: ТСПД НГДУ — производственная сеть (доступ по L2VPN)", BND_NGDU, 40, 1230, 1880, 350)
    d.boundary("Внешние системы (интернет)", BND_EXT, 1960, 610, 380, 360)

    # ===================================================================== person
    user = d.person("Пользователи\nАУП ЭМГ / КЦ КМГ\n[АРМ, браузер]", 980, 30, 280, 70)

    # ===================================================================== КСПД КМГ
    _, kc = d.container("ИС КЦ КМГ", 70, 180,
                        [("ИС ABAI", "kc"), ("ИСУН", "kc"), ("SAP ERP", "kc")], cols=1, comp_w=170)
    _, nedra = d.container("Платформа Nedra Digital", 300, 180,
                           [("MES Nedra Digital", "nedra"), ("Data Loader", "nedra"), ("Twin", "nedra"),
                            ("WWO", "nedra"), ("INFRAPLAN", "nedra"), ("Pipe", "nedra")], cols=2, comp_w=150)
    _, idk = d.container("Служба каталогов", 706, 180,
                         [("Active Directory", "id")], cols=1, comp_w=210)
    _, kmgsvc = d.container("Иные корпоративные сервисы КМГ", 968, 180,
                            [("ИСОТ / ЭНД", "corp"), ("Портал Team", "corp"), ("Интранет", "corp"), ("ИСУП", "corp"),
                             ("Compliance", "corp"), ("КХД АО НК КМГ", "corp"), ("АСУ НСИ", "corp"), ("ИСЭЗ", "corp")],
                            cols=2, comp_w=150)

    # ===================================================================== внешние
    _, ext = d.container("Контрагенты и котировки", 1990, 660,
                         [("Нацбанк", "ext"), ("БВУ (банки)", "ext"), ("ИС ЭСФ", "ext"),
                          ("Platts.com", "ext"), ("СИЗ", "ext")], cols=1, comp_w=300)

    # ===================================================================== КСПД ЭМГ
    _, ecore = d.container("Ядро ЭМГ · OT-хаб", 70, 670,
                           [("ИМ · cmv2\n10.32.10.99", "emg"), ("MES система ЭМГ", "emg"), ("АСДЦ", "emg")],
                           cols=1, comp_w=180)
    _, esrv = d.container("Производственные серверы ЭМГ", 310, 670,
                          [("Жулдыз", "srv"), ("КГИС", "srv"), ("SAS-FM", "srv"), ("SAP (контур ЭМГ)", "srv")],
                          cols=2, comp_w=150)
    eapp_box, eapp = d.container("Бизнес-приложения ЭМГ", 700, 670,
                                 [("Alfresco (ЭА)", "app"), ("1С (зарплата)", "app"), ("Directum / САПФИР", "app"),
                                  ("E-Pass", "app"), ("sPoint", "app"), ("Procu / Price", "app"),
                                  ("AVR+", "app"), ("ПК «Управление\nперсоналом»", "app"),
                                  ("Argus Pro", "app"), ("ИС «УТО ЭМГ»", "app")], cols=2, comp_w=158)
    _, esec = d.container("Информационная безопасность ЭМГ", 1090, 670,
                          [("PetroLine", "sec"), ("Solar Dozor", "sec"), ("FUDO PAM", "sec"),
                           ("MS Exchange", "sec"), ("Forcepoint WG", "sec")], cols=2, comp_w=150)

    # ===================================================================== ТСПД НГДУ
    asu_kn, _ = d.container("АСУ ТП «Кайнармунайгаз» (В. Молдабек)", 70, 1290,
                            [("OPC server", "ot"), ("АСУТП сервер", "ot"), ("КУУН НПС-3", "ot"),
                             ("ТМ АГЗУ", "ot"), ("СДМО", "ot"), ("Коллектор данных", "ot")], cols=2, comp_w=158)
    asu_zh, _ = d.container("АСУ ТП «Жылыоймунайгаз» (С. Нуржанова, Прорва)", 680, 1290,
                            [("OPC server", "ot"), ("АСУТП сервер", "ot"), ("КУУН", "ot"),
                             ("Коллектор данных", "ot")], cols=2, comp_w=158)

    # короткие имена
    ABAI = kc["ИС ABAI"]
    SAP = kc["SAP ERP"]
    AD = idk["Active Directory"]
    KHD = kmgsvc["КХД АО НК КМГ"]
    NSI = kmgsvc["АСУ НСИ"]
    ISEZ = kmgsvc["ИСЭЗ"]
    ISOT = kmgsvc["ИСОТ / ЭНД"]
    IM = ecore["ИМ · cmv2\n10.32.10.99"]
    ESAP = esrv["SAP (контур ЭМГ)"]
    SPOINT = eapp["sPoint"]
    PROCU = eapp["Procu / Price"]
    UTOE = eapp["ИС «УТО ЭМГ»"]

    # ===================================================================== связи C4
    # Person
    d.route(user, B(0.5), ABAI, T(0.5), "Работает с [HTTPS]", kind="int",
            waypoints=[(1120, 110), (158, 110), (158, 180)])
    d.route(user, B(0.5), eapp_box, T(0.5), "Работает с [HTTPS]", kind="int",
            waypoints=[(1120, 120), (779, 120), (779, 670)])
    # OT-телеметрия → ИМ (по L2VPN)
    d.route(asu_kn, T(0.5), IM, B(0.4), "Передаёт телеметрию [OPC UA/DA, Modbus, SQL]", kind="ot",
            waypoints=[(249, 1180), (150, 1180), (150, 920)])
    d.route(asu_zh, T(0.5), IM, B(0.6), "Передаёт телеметрию [OPC UA / SQL]", kind="ot",
            waypoints=[(859, 1170), (172, 1170), (172, 924)])
    # ABAI → ИМ (по ЕСПД)
    d.route(ABAI, L(0.5), IM, T(0.5), "Фонд скважин, режимы [SQL · 08:00/13:30/18:00]", kind="int", lpos=0.34,
            waypoints=[(52, 205), (52, 640), (160, 640)])
    # SAP-контур ЭМГ ↔ SAP ERP (по ЕСПД)
    d.route(SAP, L(0.5), ESAP, T(0.5), "Финансы/кадры [SAP PO · SOAP · RFC · CSV · API]", kind="int", bidir=True, lpos=0.46,
            waypoints=[(60, 355), (60, 642), (385, 642)])
    # приложения ЭМГ → AD (LDAP)
    d.route(AD, B(0.5), eapp_box, T(0.5), "Аутентификация [LDAP]", kind="ldap",
            waypoints=[(811, 560), (815, 560), (815, 642)])
    # sPoint → КХД
    d.route(SPOINT, R(0.5), KHD, B(0.5), "Наряды-допуски [REST/API JSON]", kind="int",
            waypoints=[(1330, 779), (1330, 560), (1118, 560), (1118, 438)])
    # Procu ↔ АСУ НСИ
    d.route(PROCU, R(0.5), NSI, B(0.5), "НСИ/закупки [API JSON]", kind="int", bidir=True,
            waypoints=[(1345, 753), (1345, 540), (1043, 540), (1043, 438)])
    # ИС УТО ЭМГ → SAP ERP
    d.route(UTOE, R(0.6), SAP, B(0.5), "Транспорт → SAP [SOAP XML]", kind="int",
            waypoints=[(1360, 804), (1360, 500), (66, 500), (66, 372)])
    # SAP ERP ↔ внешние
    d.route(SAP, R(0.5), ext["Нацбанк"], L(0.5), "Курсы, выписки, ЭСФ, котировки [XML/MT940/API]", kind="int", bidir=True,
            waypoints=[(258, 496), (1958, 496), (1958, 700), (1990, 700)])
    # ABAI → ИСОТ (внутри КМГ)
    d.route(ABAI, R(0.4), ISOT, L(0.5), "СИЗ, нарушения, добыча [REST/SMTP]", kind="int",
            waypoints=[(940, 212), (940, 222)])

    # ===================================================================== легенда
    legend = make_obj(value="Легенда C4", position=(40, 1600), width=2300, height=30,
                      baseStyle=("rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#999999;"
                                 "verticalAlign=middle;align=left;fontStyle=1;spacingLeft=10;fontSize=11;"))
    d._add(legend, 40, 1600, 2300, 30, "legend")
    note = make_obj(
        value=("«component» — система (узел C4).  Пунктирные рамки — границы сетей (КСПД КМГ / ЭМГ / ТСПД НГДУ) и внешний контур.  "
               "Синие стрелки — интеграции данных (с протоколом), оранжевые — телеметрия OT, серый пунктир — LDAP, двойная стрелка — двусторонний обмен.  "
               "Цвет узла = функциональная группа.  Транспорт между сетями: КМГ↔ЭМГ — ЕСПД, ЭМГ↔НГДУ — L2VPN (на C4 показан подписями связей)."),
        position=(360, 1600), width=1980, height=30,
        baseStyle="text;html=1;align=left;verticalAlign=middle;fontSize=10;fontColor=#5A5A5A;spacingLeft=8;")
    d._add(note, 360, 1600, 1980, 30, "text")

    return f, d


def render_svg(d, svg_path):
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

    fig, ax = plt.subplots(figsize=(24.0, 16.4))
    ax.set_xlim(0, 2400)
    ax.set_ylim(0, 1640)
    ax.invert_yaxis()
    ax.axis("off")

    order = {"bnd": 0, "container": 1, "legend": 1, "comp": 2, "person": 2, "text": 2}
    for s in sorted(d.shapes, key=lambda s: order.get(s["role"], 1)):
        st, role = s["style"], s["role"]
        fill = color(st, "fillColor", "#fff")
        bnd = role == "bnd"
        person = role == "person"
        comp = role == "comp"
        ax.add_patch(Rectangle((s["x"], s["y"]), s["w"], s["h"],
                               facecolor="none" if fill == "none" else fill,
                               edgecolor=color(st, "strokeColor", "#666"),
                               linewidth=2.0 if bnd else (1.3 if role in ("container", "legend") else 1.0),
                               linestyle="--" if bnd else "-",
                               zorder=order.get(role, 1)))
        txt = (s["v"].replace("&#xa;", "\n").replace("&lt;", "<").replace("&gt;", ">")) if s["v"] else ""
        top = "verticalAlign=top" in st
        ax.text((s["x"] + 10) if top else s["x"] + s["w"] / 2,
                (s["y"] + 7) if top else s["y"] + s["h"] / 2,
                txt, ha="left" if top else "center", va="top" if top else "center",
                fontsize=7.5 if comp else (13 if bnd else (10.5 if top else 9.5)),
                color="#fff" if person else (color(st, "fontColor", "#000") if (bnd or top) else "#000"),
                fontweight="bold" if (person or bnd or top) else "normal", zorder=3)

    for e in d.polylines:
        pts = e["pts"]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        c = e["color"]
        ax.plot(xs, ys, color=c, lw=1.2, ls="--" if e["dashed"] else "-", zorder=4, alpha=0.95)
        ax.annotate("", xy=pts[-1], xytext=pts[-2], arrowprops=dict(arrowstyle="->", color=c, lw=1.2), zorder=4)
        if e["bidir"]:
            ax.annotate("", xy=pts[0], xytext=pts[1], arrowprops=dict(arrowstyle="->", color=c, lw=1.2), zorder=4)
        if e["label"]:
            if e.get("lpos") is not None:
                seg = [((pts[i + 1][0] - pts[i][0]) ** 2 + (pts[i + 1][1] - pts[i][1]) ** 2) ** 0.5 for i in range(len(pts) - 1)]
                tot = sum(seg) or 1.0
                tg = e["lpos"] * tot
                acc = 0.0
                mid = pts[len(pts) // 2]
                for i, sl in enumerate(seg):
                    if acc + sl >= tg:
                        t = (tg - acc) / (sl or 1.0)
                        mid = (pts[i][0] + t * (pts[i + 1][0] - pts[i][0]), pts[i][1] + t * (pts[i + 1][1] - pts[i][1]))
                        break
                    acc += sl
            else:
                mid = pts[len(pts) // 2]
            ax.text(mid[0], mid[1], e["label"], fontsize=6.5, color="#12325f", ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.14", fc="white", ec="#cccccc", alpha=0.9), zorder=5)

    svg_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(svg_path, format="svg", bbox_inches="tight")
    try:
        fig.savefig(PNG_PREVIEW, dpi=110, bbox_inches="tight")
    except Exception:
        pass
    plt.close(fig)
    print(f"OK svg preview -> {svg_path}")
    return True


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    f, d = build()
    out = f.write(overwrite=True)
    print(f"OK 11-kmg-emg-c4-component -> {out}")
    render_svg(d, SVG_DIR / "11-kmg-emg-c4-component.svg")


if __name__ == "__main__":
    main()
