#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the network-segmented КМГ + ЭМГ architecture diagram.

Схема построена по реальной сетевой топологии (КСПД КМГ, КСПД ЭМГ / АУП ЭМГ,
ТСПД НГДУ) с транспортами ЕСПД и провайдерским L2VPN. Системы распределены по
сетевым сегментам так, как они фактически размещены:

  * КСПД КМГ (корпоративная сеть КМГ): ИС КЦ КМГ (ABAI, ИСУН, SAP ERP),
    платформа Nedra Digital (MES Nedra, Data Loader, Twin, WWO, INFRAPLAN, Pipe),
    служба каталогов (AD), иные корпоративные сервисы.
  * КСПД ЭМГ (АУП ЭМГ): ИМ/MES ЭМГ, производственные серверы (Жулдыз, КГИС,
    SAS-FM, SAP-контур), бизнес-приложения (Alfresco, 1С, Directum, E-Pass,
    sPoint, Procu, AVR, ПК УП, Argus Pro, ИС УТО), ИБ (PetroLine, Solar Dozor,
    FUDO PAM, Exchange, Forcepoint).
  * ТСПД НГДУ: АСУ ТП «Кайнармунайгаз» (м/р В. Молдабек) и «Жылыоймунайгаз»
    (м/р С. Нуржанова, Прорва) — OPC/АСУТП/коллекторы, внутренняя сеть НГДУ.

Транспорт: КСПД КМГ ↔ КСПД ЭМГ через ЕСПД (МСЭ, криптошлюзы, маршрутизаторы);
КСПД ЭМГ ↔ ТСПД НГДУ через провайдерский L2VPN.

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

# --------------------------------------------------------------------------- геометрия
COMP_W, COMP_H = 158, 44
GAP_X, GAP_Y = 14, 10
PAD_SIDE, PAD_TOP, PAD_BOT = 14, 34, 12

# --------------------------------------------------------------------------- стили
NET_KMG = ("rounded=1;html=1;fillColor=#EAF1FB;strokeColor=#1565C0;strokeWidth=3;"
           "verticalAlign=top;align=left;fontStyle=1;fontSize=16;fontColor=#0D3C78;spacingLeft=16;spacingTop=10;")
NET_EMG = ("rounded=1;html=1;fillColor=#EAF7EA;strokeColor=#2E7D32;strokeWidth=3;"
           "verticalAlign=top;align=left;fontStyle=1;fontSize=16;fontColor=#1B5E20;spacingLeft=16;spacingTop=10;")
NET_NGDU = ("rounded=1;html=1;fillColor=#FFF4E5;strokeColor=#D9760A;strokeWidth=3;"
            "verticalAlign=top;align=left;fontStyle=1;fontSize=16;fontColor=#8A4B00;spacingLeft=16;spacingTop=10;")
CONTAINER = ("rounded=1;whiteSpace=wrap;html=1;fillColor=#F6F8FB;strokeColor=#8497B0;"
             "verticalAlign=top;align=left;fontStyle=1;fontSize=11;fontColor=#23364B;spacingLeft=8;spacingTop=5;")
CLOUD = ("ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#E8EAF6;strokeColor=#5C6BC0;"
         "fontSize=12;fontStyle=1;fontColor=#283593;verticalAlign=middle;align=center;")
ACTOR = ("rounded=1;whiteSpace=wrap;html=1;fillColor=#08427B;strokeColor=#073B6F;"
         "fontColor=#ffffff;fontStyle=1;verticalAlign=middle;align=center;fontSize=11;")

COMP_PALETTE = {
    "kc": ("#B3C7E6", "#3F5F8F"),     # ИС КЦ КМГ
    "nedra": ("#B0E3E6", "#0E8088"),  # платформа Nedra
    "id": ("#FFE0B2", "#E08A00"),     # служба каталогов / AD
    "corp": ("#DAE8FC", "#6C8EBF"),   # иные корп. сервисы КМГ
    "emg": ("#D5E8D4", "#5C9A4F"),    # ядро ЭМГ
    "srv": ("#C8E6C9", "#519657"),    # произв. серверы ЭМГ
    "app": ("#DCEAF7", "#6C8EBF"),    # бизнес-приложения ЭМГ
    "sec": ("#F8CECC", "#B85450"),    # ИБ
    "ot": ("#FFE6CC", "#D79B00"),     # АСУ ТП / OT
    "net": ("#ECEFF1", "#78909C"),    # сетевые узлы (периметр)
    "ext": ("#EEEEEE", "#9E9E9E"),    # внешние системы
}

EDGE_NET = "#37474F"     # транспорт / сеть
EDGE_INT = "#1565C0"     # интеграция (данные)
EDGE_OT = "#E8710A"      # телеметрия OT
EDGE_LDAP = "#7E8896"    # LDAP


def comp_style(kind: str) -> str:
    fill, stroke = COMP_PALETTE.get(kind, COMP_PALETTE["app"])
    return (f"shape=module;jettyWidth=12;jettyHeight=6;whiteSpace=wrap;html=1;"
            f"fillColor={fill};strokeColor={stroke};fontSize=9;verticalAlign=middle;align=center;"
            f"spacingLeft=4;spacingRight=2;")


def make_obj(**kwargs) -> Object:
    obj = Object(**kwargs)
    obj.style_attributes = []
    return obj


def container_dims(n, cols, w):
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


def _ortho(a, ad, b, bd):
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
    def __init__(self, page):
        self.page = page
        self.geo = {}
        self.shapes = []
        self.polylines = []

    def _add(self, obj, x, y, w, h, role="shape", title=None, body=None):
        self.page.add_object(obj)
        self.geo[id(obj)] = (x, y, w, h)
        self.shapes.append({"x": x, "y": y, "w": w, "h": h, "style": obj.baseStyle,
                            "v": obj.value, "role": role, "title": title, "body": body})
        return obj

    def net(self, title, style, x, y, w, h):
        return self._add(make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=style), x, y, w, h, "net")

    def cloud(self, title, x, y, w, h):
        return self._add(make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=CLOUD), x, y, w, h, "cloud")

    def actor(self, title, x, y, w=200, h=60):
        return self._add(make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=ACTOR), x, y, w, h, "actor")

    def container(self, title, x, y, comps, cols, comp_w=COMP_W):
        w, h = container_dims(len(comps), cols, comp_w)
        box = self._add(make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=CONTAINER), x, y, w, h, "container")
        objs = {}
        for i, (label, kind) in enumerate(comps):
            col, row = i % cols, i // cols
            cx = x + PAD_SIDE + col * (comp_w + GAP_X)
            cy = y + PAD_TOP + row * (COMP_H + GAP_Y)
            node = make_obj(value=label, position=(cx, cy), width=comp_w, height=COMP_H, baseStyle=comp_style(kind))
            self._add(node, cx, cy, comp_w, COMP_H, "comp")
            objs[label] = node
        return box, objs

    def anchor(self, obj, fx, fy):
        x, y, w, h = self.geo[id(obj)]
        return (x + fx * w, y + fy * h)

    def route(self, src, ef, tgt, en, label="", kind="int", bidir=False, dashed=False,
              lpos=None, waypoints: Optional[List[Tuple[int, int]]] = None):
        color = {"net": EDGE_NET, "int": EDGE_INT, "ot": EDGE_OT, "ldap": EDGE_LDAP}[kind]
        width = 2 if kind == "net" else (1 if kind == "ldap" else 1)
        dash = dashed or kind == "ldap"
        edge = Edge(source=src, target=tgt, page=self.page, label=label,
                    pattern="dashed_medium" if dash else "solid",
                    exitX=ef[0], exitY=ef[1], entryX=en[0], entryY=en[1],
                    jumpStyle="arc", jumpSize=8, rounded=0)
        edge.strokeColor = color
        if width != 1:
            edge.strokeWidth = width
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
        pts = [a, *waypoints, b] if waypoints else _ortho(a, _side_dir(ef), b, _side_dir(en))
        self.polylines.append({"pts": pts, "label": label, "dashed": dash, "color": color,
                               "bidir": bidir, "width": width, "lpos": lpos})


def build():
    f = File(file_name="10-kmg-emg-architecture.drawio", file_path=str(OUT_DIR))
    page = Page(file=f, name="Архитектура КМГ + ЭМГ (сетевые контуры и интеграции)", width=2400, height=1940)
    d = Diagram(page)

    # ===================================================================== сети (контуры)
    kmg_net = d.net("КСПД КМГ — корпоративная сеть АО НК «КазМунайГаз»", NET_KMG, 40, 90, 1880, 410)
    emg_net = d.net("КСПД ЭМГ — АУП АО «Эмбамунайгаз»", NET_EMG, 40, 580, 1880, 540)
    ngdu_net = d.net("ТСПД НГДУ — производственная сеть (АСУ ТП месторождений)", NET_NGDU, 40, 1200, 1880, 470)

    # ===================================================================== транспорт и внешние
    espd = d.cloud("ЕСПД\n(корпоративная\nсеть передачи данных)", 2000, 300, 300, 130)
    l2vpn = d.cloud("Провайдер\nL2VPN", 2000, 1270, 300, 120)
    dig = d.actor("ТОО «КМГ Digital»\n(пользователи)", 1980, 110, 340, 64)
    eng = d.actor("ТОО «КМГ Инжиниринг»\n(пользователи)", 1980, 190, 340, 64)
    ext_box, ext = d.container(
        "Внешние системы (интернет)", 1980, 640,
        [("Нацбанк", "ext"), ("БВУ (банки)", "ext"), ("ИС ЭСФ", "ext"), ("Platts.com", "ext"), ("СИЗ", "ext")],
        cols=1, comp_w=300,
    )

    # ===================================================================== КСПД КМГ
    _, kc = d.container(
        "ИС КЦ КМГ", 70, 150,
        [("ИС ABAI", "kc"), ("ИСУН", "kc"), ("SAP ERP", "kc")], cols=1, comp_w=170,
    )
    _, nedra = d.container(
        "Платформа Nedra Digital", 300, 150,
        [("MES Nedra Digital", "nedra"), ("Data Loader", "nedra"), ("Twin", "nedra"),
         ("WWO", "nedra"), ("INFRAPLAN", "nedra"), ("Pipe", "nedra")], cols=2, comp_w=150,
    )
    _, idk = d.container(
        "Служба каталогов", 706, 150,
        [("Active Directory\n(сервер аутентификации)", "id")], cols=1, comp_w=210,
    )
    _, kmgsvc = d.container(
        "Иные корпоративные сервисы КМГ", 968, 150,
        [("ИСОТ / ЭНД", "corp"), ("Портал Team", "corp"), ("Интранет", "corp"), ("ИСУП", "corp"),
         ("Compliance", "corp"), ("КХД АО НК КМГ", "corp"), ("АСУ НСИ", "corp"), ("ИСЭЗ", "corp")],
        cols=2, comp_w=150,
    )
    kperim, _ = d.container(
        "Периметр КМГ", 1374, 150,
        [("Маршрутизатор", "net"), ("МСЭ", "net"), ("Криптошлюз", "net")], cols=1, comp_w=150,
    )
    kc_users = d.actor("Пользователи\nКЦ КМГ", 1580, 170, 180, 60)

    # ===================================================================== КСПД ЭМГ
    _, ecore = d.container(
        "Ядро ЭМГ · OT-хаб", 70, 640,
        [("ИМ · cmv2\n10.32.10.99", "emg"), ("MES система ЭМГ", "emg"), ("АСДЦ", "emg")], cols=1, comp_w=180,
    )
    _, esrv = d.container(
        "Производственные серверы ЭМГ", 310, 640,
        [("Жулдыз", "srv"), ("КГИС", "srv"), ("SAS-FM", "srv"), ("SAP (контур ЭМГ)", "srv")], cols=2, comp_w=150,
    )
    eapp_box, eapp = d.container(
        "Бизнес-приложения ЭМГ", 700, 640,
        [("Alfresco (ЭА)", "app"), ("1С (зарплата)", "app"), ("Directum / САПФИР", "app"),
         ("E-Pass", "app"), ("sPoint", "app"), ("Procu / Price", "app"),
         ("AVR+", "app"), ("ПК «Управление\nперсоналом»", "app"), ("Argus Pro", "app"), ("ИС «УТО ЭМГ»", "app")],
        cols=2, comp_w=158,
    )
    _, esec = d.container(
        "Информационная безопасность ЭМГ", 1090, 640,
        [("PetroLine", "sec"), ("Solar Dozor\n(DLP)", "sec"), ("FUDO PAM", "sec"),
         ("MS Exchange", "sec"), ("Forcepoint WG", "sec")], cols=2, comp_w=150,
    )
    eperim, _ = d.container(
        "Периметр ЭМГ", 1470, 640,
        [("Маршрутизатор", "net"), ("МСЭ", "net"), ("Криптошлюз", "net")], cols=1, comp_w=150,
    )
    emg_users = d.actor("Пользователи\nАУП ЭМГ", 1676, 660, 180, 60)

    # ===================================================================== ТСПД НГДУ
    ninner, _ = d.container(
        "Внутренняя сеть НГДУ", 70, 1260,
        [("Edge-сервер сбора данных", "net"), ("Switch", "net"), ("МСЭ", "net"),
         ("Криптошлюз", "net"), ("Маршрутизатор", "net")], cols=1, comp_w=210,
    )
    asu_kn, _ = d.container(
        "АСУ ТП «Кайнармунайгаз» · В. Молдабек", 360, 1260,
        [("OPC server", "ot"), ("АСУТП сервер", "ot"), ("КУУН НПС-3", "ot"),
         ("ТМ АГЗУ", "ot"), ("СДМО", "ot"), ("Коллектор данных", "ot")], cols=2, comp_w=158,
    )
    asu_zh, _ = d.container(
        "АСУ ТП «Жылыоймунайгаз» · С. Нуржанова, Прорва", 930, 1260,
        [("OPC server", "ot"), ("АСУТП сервер", "ot"), ("КУУН", "ot"), ("Коллектор данных", "ot")],
        cols=2, comp_w=158,
    )

    # короткие имена
    ABAI = kc["ИС ABAI"]
    SAP = kc["SAP ERP"]
    AD = idk["Active Directory\n(сервер аутентификации)"]
    KHD = kmgsvc["КХД АО НК КМГ"]
    NSI = kmgsvc["АСУ НСИ"]
    ISEZ = kmgsvc["ИСЭЗ"]
    ISOT = kmgsvc["ИСОТ / ЭНД"]
    IM = ecore["ИМ · cmv2\n10.32.10.99"]
    ESAP = esrv["SAP (контур ЭМГ)"]
    SPOINT = eapp["sPoint"]
    PROCU = eapp["Procu / Price"]
    DIRECTUM = eapp["Directum / САПФИР"]
    UTOE = eapp["ИС «УТО ЭМГ»"]

    # ===================================================================== ТРАНСПОРТ (сеть)
    d.route(kperim, R(0.5), espd, L(0.35), "КСПД КМГ → ЕСПД", kind="net",
            waypoints=[(1900, 245), (1900, 346)])
    d.route(eperim, R(0.5), espd, L(0.75), "КСПД ЭМГ → ЕСПД", kind="net",
            waypoints=[(1920, 740), (1920, 398)])
    d.route(dig, B(0.5), espd, T(0.4), "", kind="net")
    d.route(eng, B(0.5), espd, T(0.65), "", kind="net")
    d.route(eperim, B(0.5), l2vpn, T(0.35), "КСПД ЭМГ → L2VPN", kind="net",
            waypoints=[(1554, 1155), (2105, 1155), (2105, 1270)])
    d.route(ninner, T(0.85), l2vpn, L(0.4), "ТСПД НГДУ → L2VPN", kind="net",
            waypoints=[(272, 1248), (1930, 1248), (1930, 1318)])

    # ===================================================================== ИНТЕГРАЦИИ (данные)
    # OT-телеметрия НГДУ → ИМ (через L2VPN)
    d.route(asu_kn, T(0.3), IM, B(0.4), "OPC UA/DA, Modbus, SQL", kind="ot",
            waypoints=[(420, 1150), (150, 1150), (150, 880)])
    d.route(asu_zh, T(0.5), IM, B(0.6), "OPC UA / SQL", kind="ot",
            waypoints=[(835, 1140), (170, 1140), (170, 884)])
    # ABAI (КМГ) → ИМ (ЭМГ): фонд скважин (через ЕСПД)
    d.route(ABAI, L(0.5), IM, T(0.5), "SQL · фонд скважин · 08:00/13:30/18:00", kind="int", lpos=0.34,
            waypoints=[(52, 172), (52, 600), (160, 600)])
    # SAP ERP (КМГ) ↔ SAP-контур ЭМГ: финансы/кадры
    d.route(SAP, L(0.5), ESAP, T(0.5), "SAP PO · SOAP · RFC · CSV · API XML", kind="int", bidir=True, lpos=0.46,
            waypoints=[(60, 322), (60, 612), (385, 612)])
    # AD (КМГ) → приложения/ИБ ЭМГ: LDAP
    d.route(AD, B(0.5), eapp_box, T(0.5), "LDAP — единый каталог", kind="ldap",
            waypoints=[(811, 540), (779, 540), (779, 612)])
    # sPoint / Directum (ЭМГ) → КХД (КМГ)
    d.route(SPOINT, R(0.5), KHD, B(0.5), "REST / API JSON", kind="int",
            waypoints=[(1320, 745), (1320, 520), (1118, 520), (1118, 408)])
    # Procu (ЭМГ) ↔ АСУ НСИ / ИСЭЗ (КМГ)
    d.route(PROCU, R(0.5), NSI, B(0.5), "API JSON", kind="int", bidir=True,
            waypoints=[(1335, 723), (1335, 500), (1043, 500), (1043, 408)])
    # ИС УТО ЭМГ → SAP ERP (КМГ) — транспорт
    d.route(UTOE, R(0.6), SAP, B(0.5), "ИС УТО → SAP (SOAP XML)", kind="int",
            waypoints=[(1350, 766), (1350, 470), (66, 470), (66, 338)])
    # SAP ERP (КМГ) ↔ внешние (Нацбанк/БВУ/ЭСФ/Platts) — нижний коридор КСПД КМГ
    d.route(SAP, R(0.5), ext_box, L(0.2), "курсы · выписки · ЭСФ · котировки", kind="int", bidir=True,
            waypoints=[(254, 462), (1948, 462), (1948, 700)])
    # ABAI (КМГ) → ИСОТ (КМГ): нарушения СИЗ, добыча (внутри КМГ)
    d.route(ABAI, R(0.4), ISOT, L(0.5), "СИЗ / нарушения / добыча", kind="int",
            waypoints=[(940, 180), (940, 196)])

    # ===================================================================== легенда
    legend = make_obj(value="Легенда", position=(40, 1710), width=2300, height=120,
                      baseStyle=("rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#999999;"
                                 "verticalAlign=top;align=left;fontStyle=1;spacingLeft=10;spacingTop=6;"))
    d._add(legend, 40, 1710, 2300, 120, "legend")
    seg_items = [("ИС КЦ КМГ", "kc"), ("Платформа Nedra", "nedra"), ("Служба каталогов (AD)", "id"),
                 ("Корпоративные сервисы КМГ", "corp"), ("Ядро ЭМГ / OT-хаб", "emg"),
                 ("Произв. серверы ЭМГ", "srv"), ("Бизнес-приложения ЭМГ", "app"),
                 ("Информационная безопасность", "sec"), ("АСУ ТП / OT (ТСПД)", "ot"),
                 ("Сетевые узлы (периметр)", "net"), ("Внешние системы", "ext")]
    for i, (label, kind) in enumerate(seg_items):
        col, row = i % 4, i // 4
        sx, sy = 60 + col * 360, 1748 + row * 26
        fill, stroke = COMP_PALETTE[kind]
        d._add(make_obj(value="", position=(sx, sy), width=26, height=16,
                        baseStyle=f"rounded=0;html=1;fillColor={fill};strokeColor={stroke};"), sx, sy, 26, 16, "swatch")
        d._add(make_obj(value=label, position=(sx + 32, sy), width=300, height=16,
                        baseStyle="text;html=1;align=left;verticalAlign=middle;fontSize=10;"), sx + 32, sy, 300, 16, "text")

    note = make_obj(
        value=("Контуры: синий — КСПД КМГ, зелёный — КСПД ЭМГ (АУП), оранжевый — ТСПД НГДУ.  "
               "Серые толстые линии — сетевой транспорт (ЕСПД, L2VPN) через МСЭ/криптошлюзы/маршрутизаторы.  "
               "Синие линии — интеграции данных (с протоколом), оранжевые — телеметрия OT, серый пунктир — LDAP.  "
               "ABAI, ИСУН, SAP ERP и платформа Nedra размещены в КСПД КМГ; ЭМГ обращается к ним по ЕСПД."),
        position=(40, 1840), width=2300, height=70,
        baseStyle="text;html=1;align=left;verticalAlign=top;fontSize=10;fontColor=#5A5A5A;spacingLeft=8;spacingTop=4;")
    d._add(note, 40, 1840, 2300, 70, "text")

    return f, d


def render_svg(d, svg_path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle, Ellipse
    except Exception as exc:  # pragma: no cover
        print(f"SKIP svg preview ({exc})")
        return False

    def color(style, key, default):
        m = re.search(rf"{key}=(#[0-9A-Fa-f]{{6}}|none)", style)
        return m.group(1) if m else default

    fig, ax = plt.subplots(figsize=(24.0, 19.4))
    ax.set_xlim(0, 2400)
    ax.set_ylim(0, 1940)
    ax.invert_yaxis()
    ax.axis("off")

    order = {"net": 0, "container": 1, "legend": 1, "cloud": 2, "comp": 2, "actor": 2, "swatch": 2, "text": 2}
    for s in sorted(d.shapes, key=lambda s: order.get(s["role"], 1)):
        st, role = s["style"], s["role"]
        fill = color(st, "fillColor", "#ffffff")
        netband = role == "net"
        actor = role == "actor"
        comp = role == "comp"
        cloud = role == "cloud"
        if cloud:
            ax.add_patch(Ellipse((s["x"] + s["w"] / 2, s["y"] + s["h"] / 2), s["w"], s["h"],
                                 facecolor=fill, edgecolor=color(st, "strokeColor", "#5C6BC0"), lw=1.6, zorder=2))
        else:
            ax.add_patch(Rectangle((s["x"], s["y"]), s["w"], s["h"],
                                   facecolor="none" if fill == "none" else fill,
                                   edgecolor=color(st, "strokeColor", "#666"),
                                   linewidth=2.6 if netband else (1.3 if role in ("container", "legend") else 1.0),
                                   zorder=order.get(role, 1)))
        txt = (s["v"].replace("&#xa;", "\n").replace("&lt;", "<").replace("&gt;", ">")) if s["v"] else ""
        top = "verticalAlign=top" in st
        ax.text((s["x"] + 10) if top else s["x"] + s["w"] / 2,
                (s["y"] + 7) if top else s["y"] + s["h"] / 2,
                txt, ha="left" if top else "center", va="top" if top else "center",
                fontsize=8 if comp else (14 if netband else (11 if top else 9.5)),
                color="#fff" if actor else (color(st, "fontColor", "#000") if (netband or top or cloud) else "#000"),
                fontweight="bold" if (actor or netband or top or cloud) else "normal", zorder=3)

    for e in d.polylines:
        pts = e["pts"]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        c = e["color"]
        lw = 1.1 + 0.9 * (e["width"] - 1)
        ax.plot(xs, ys, color=c, lw=lw, ls="--" if e["dashed"] else "-", zorder=4, alpha=0.95)
        ax.annotate("", xy=pts[-1], xytext=pts[-2], arrowprops=dict(arrowstyle="->", color=c, lw=lw), zorder=4)
        if e["bidir"]:
            ax.annotate("", xy=pts[0], xytext=pts[1], arrowprops=dict(arrowstyle="->", color=c, lw=lw), zorder=4)
        if e["label"]:
            if e.get("lpos") is not None:
                seg = [((pts[i + 1][0] - pts[i][0]) ** 2 + (pts[i + 1][1] - pts[i][1]) ** 2) ** 0.5 for i in range(len(pts) - 1)]
                tot = sum(seg) or 1.0
                tgt = e["lpos"] * tot
                acc = 0.0
                mid = pts[len(pts) // 2]
                for i, sl in enumerate(seg):
                    if acc + sl >= tgt:
                        t = (tgt - acc) / (sl or 1.0)
                        mid = (pts[i][0] + t * (pts[i + 1][0] - pts[i][0]), pts[i][1] + t * (pts[i + 1][1] - pts[i][1]))
                        break
                    acc += sl
            else:
                mid = pts[len(pts) // 2]
            ax.text(mid[0], mid[1], e["label"], fontsize=7, color="#12325f", ha="center", va="center",
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
    print(f"OK 10-kmg-emg-architecture -> {out}")
    render_svg(d, SVG_DIR / "10-kmg-emg-architecture.svg")


if __name__ == "__main__":
    main()
