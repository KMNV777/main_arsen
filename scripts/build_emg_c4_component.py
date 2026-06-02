#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the unified C4 Component diagram for АО «Эмбамунайгаз» (ЭМГ).

Источники данных:
  * Матрица интеграций (последняя редакция, 19 систем) — docs/it-landscape-emg-registry.md
    и загруженный PDF перечня интеграций.
  * Верхнеуровневая («сводная») архитектура КМГ + ЭМГ + интеграции (изображение).
  * Черновик общего ландшафта корпоративных систем (изображение).

Стиль повторяет эталонный C4-генератор build_abai_c4_component.py:
контейнеры-контуры с узлами «component», связи с протоколами/форматами,
контурные зоны (dashed) и легенда. Все связи из матрицы интеграций проведены.
Граф непланарен, поэтому неизбежные пересечения помечаются «мостиками»
(jumpStyle=arc) и читаются однозначно.

Запуск:
    pip install -r requirements.txt
    python3 scripts/build_emg_c4_component.py
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from drawpyo import File, Page
from drawpyo.diagram.edges import Edge
from drawpyo.diagram.objects import Object

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "drawio"
SVG_DIR = ROOT / "docs" / "svg"
PNG_PREVIEW = "/opt/cursor/artifacts/emg-c4-component-preview.png"

# ---------------------------------------------------------------------------
# Геометрия
# ---------------------------------------------------------------------------
COMP_W, COMP_H = 188, 58
SIDE_W = 250
GAP_X, GAP_Y = 18, 16
PAD_SIDE, PAD_TOP, PAD_BOT = 18, 42, 16

# ---------------------------------------------------------------------------
# Стили
# ---------------------------------------------------------------------------
ZONE_STYLE = (
    "rounded=0;dashed=1;dashPattern=8 4;fillColor=none;strokeColor=#5A5A5A;"
    "verticalAlign=top;align=left;fontStyle=2;fontSize=13;fontColor=#5A5A5A;"
    "spacingLeft=10;spacingTop=6;html=1;"
)

CONTAINER_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#EEF2F7;strokeColor=#8497B0;"
    "verticalAlign=top;align=left;fontStyle=1;fontSize=12;fontColor=#23364B;"
    "spacingLeft=10;spacingTop=6;spacingRight=10;"
)

ACTOR_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#08427B;strokeColor=#073B6F;"
    "fontColor=#ffffff;fontStyle=1;verticalAlign=middle;align=center;fontSize=11;"
)

COMP_PALETTE = {
    "emg": ("#D5E8D4", "#82B366"),   # ядро цифровизации ЭМГ
    "ot": ("#FFE6CC", "#D79B00"),    # промышленный контур (OT)
    "corp": ("#DAE8FC", "#6C8EBF"),  # корпоративные ИС
    "sap": ("#FFF2CC", "#D6B656"),   # SAP / финансы
    "doc": ("#E1D5E7", "#9673A6"),   # документооборот / архив
    "sec": ("#F8CECC", "#B85450"),   # информационная безопасность
    "id": ("#B0E3E6", "#0E8088"),    # идентификация
    "nsi": ("#F5F5F5", "#999999"),   # НСИ / технические интеграции
}

EDGE_SOLID = "#36506B"
EDGE_DASH = "#9673A6"
EDGE_LDAP = "#9AA4AE"


def comp_style(kind: str) -> str:
    if kind == "actor":
        return ACTOR_STYLE
    fill, stroke = COMP_PALETTE.get(kind, COMP_PALETTE["corp"])
    return (
        f"shape=module;jettyWidth=14;jettyHeight=6;whiteSpace=wrap;html=1;"
        f"fillColor={fill};strokeColor={stroke};fontSize=10;verticalAlign=middle;"
        f"align=center;spacingLeft=6;spacingRight=4;"
    )


def make_obj(**kwargs) -> Object:
    """Create an Object whose style is exactly its ``baseStyle`` (no template defaults)."""
    obj = Object(**kwargs)
    obj.style_attributes = []
    return obj


def container_dims(n_comps: int, cols: int, comp_w: int) -> Tuple[int, int]:
    rows = max(1, math.ceil(n_comps / cols))
    w = PAD_SIDE * 2 + cols * comp_w + (cols - 1) * GAP_X
    h = PAD_TOP + rows * COMP_H + (rows - 1) * GAP_Y + PAD_BOT
    return w, h


# ---------------------------------------------------------------------------
# Anchor helpers
# ---------------------------------------------------------------------------
def L(f: float = 0.5):
    return (0.0, f)


def R(f: float = 0.5):
    return (1.0, f)


def T(f: float = 0.5):
    return (f, 0.0)


def B(f: float = 0.5):
    return (f, 1.0)


def _side_dir(frac: Tuple[float, float]) -> Tuple[int, int]:
    fx, fy = frac
    if fy == 0.0:
        return (0, -1)
    if fy == 1.0:
        return (0, 1)
    if fx == 0.0:
        return (-1, 0)
    return (1, 0)


def _ortho_path(a, ad, b, bd):
    """Generate an orthogonal preview polyline between anchors a and b."""
    ax, ay = a
    bx, by = b
    if ad[0] != 0 and bd[0] != 0:        # both horizontal
        mx = (ax + bx) / 2
        return [a, (mx, ay), (mx, by), b]
    if ad[1] != 0 and bd[1] != 0:        # both vertical
        my = (ay + by) / 2
        return [a, (ax, my), (bx, my), b]
    if ad[0] != 0 and bd[1] != 0:        # exit horizontal, entry vertical
        return [a, (bx, ay), b]
    return [a, (ax, by), b]              # exit vertical, entry horizontal


class Diagram:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.geo: Dict[int, Tuple[int, int, int, int]] = {}
        self.shapes: List[dict] = []
        self.polylines: List[dict] = []

    def _add(self, obj: Object, x: int, y: int, w: int, h: int) -> Object:
        self.page.add_object(obj)
        self.geo[id(obj)] = (x, y, w, h)
        self.shapes.append({"x": x, "y": y, "w": w, "h": h, "style": obj.baseStyle, "v": obj.value})
        return obj

    def zone(self, title: str, x: int, y: int, w: int, h: int) -> Object:
        return self._add(make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=ZONE_STYLE), x, y, w, h)

    def container(
        self, title: str, x: int, y: int, comps: List[Tuple[str, str]], cols: int, comp_w: int = COMP_W
    ) -> Dict[str, Object]:
        w, h = container_dims(len(comps), cols, comp_w)
        self._add(make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=CONTAINER_STYLE), x, y, w, h)
        objs: Dict[str, Object] = {}
        for i, (label, kind) in enumerate(comps):
            col, row = i % cols, i // cols
            cx = x + PAD_SIDE + col * (comp_w + GAP_X)
            cy = y + PAD_TOP + row * (COMP_H + GAP_Y)
            value = label if kind == "actor" else f"«component»\n{label}"
            node = make_obj(value=value, position=(cx, cy), width=comp_w, height=COMP_H, baseStyle=comp_style(kind))
            self._add(node, cx, cy, comp_w, COMP_H)
            objs[label] = node
        return objs

    def bbox(self, objs: List[Object]) -> Tuple[int, int, int, int]:
        xs0 = min(self.geo[id(o)][0] for o in objs)
        ys0 = min(self.geo[id(o)][1] for o in objs)
        xs1 = max(self.geo[id(o)][0] + self.geo[id(o)][2] for o in objs)
        ys1 = max(self.geo[id(o)][1] + self.geo[id(o)][3] for o in objs)
        return xs0, ys0, xs1, ys1

    def anchor(self, obj: Object, fx: float, fy: float) -> Tuple[float, float]:
        x, y, w, h = self.geo[id(obj)]
        return (x + fx * w, y + fy * h)

    def route(
        self,
        src: Object,
        exit_frac: Tuple[float, float],
        tgt: Object,
        entry_frac: Tuple[float, float],
        label: str = "",
        dashed: bool = False,
        ldap: bool = False,
        bidir: bool = False,
        waypoints: Optional[List[Tuple[int, int]]] = None,
    ) -> None:
        color = EDGE_LDAP if ldap else (EDGE_DASH if dashed else EDGE_SOLID)
        edge = Edge(
            source=src,
            target=tgt,
            page=self.page,
            label=label,
            pattern="dashed_medium" if (dashed or ldap) else "solid",
            exitX=exit_frac[0],
            exitY=exit_frac[1],
            entryX=entry_frac[0],
            entryY=entry_frac[1],
            jumpStyle="arc",
            jumpSize=8,
            rounded=0,
        )
        edge.strokeColor = color
        if bidir:
            edge.line_end_source = "classic"
            edge.endFill_source = True
        if waypoints:
            for (wx, wy) in waypoints:
                edge.geometry.add_point(wx, wy)
        self.page.add_object(edge)

        a = self.anchor(src, *exit_frac)
        b = self.anchor(tgt, *entry_frac)
        if waypoints:
            pts = [a, *waypoints, b]
        else:
            pts = _ortho_path(a, _side_dir(exit_frac), b, _side_dir(entry_frac))
        self.polylines.append({"pts": pts, "label": label, "dashed": dashed or ldap, "color": color, "bidir": bidir})


def build() -> Tuple[File, Diagram]:
    f = File(file_name="09-emg-c4-component.drawio", file_path=str(OUT_DIR))
    page = Page(file=f, name="C4 Component — ЭМГ", width=2240, height=1320)
    d = Diagram(page)

    # ------------------------------------------------------------------ containers
    org = d.container(
        "Организационный контур (владельцы процессов)",
        40, 40,
        [("КЦ КМГ", "actor"), ("АО «Эмбамунайгаз»", "actor"), ("КМГИ", "actor")],
        cols=1, comp_w=SIDE_W,
    )

    core = d.container(
        "Ядро цифровизации ЭМГ",
        40, 400,
        [
            ("ИС ABAI", "emg"),
            ("ИС «УТО ЭМГ»", "emg"),
            ("АСДЦ", "emg"),
        ],
        cols=2,
    )

    im_band = d.container(
        "Интеллектуальное месторождение (ИМ) · OT-хаб",
        40, 620,
        [("ИМ · cmv2 · 10.32.10.99", "emg")],
        cols=1, comp_w=394,
    )

    ot = d.container(
        "Промышленный контур (OT) · телеметрия",
        40, 800,
        [
            ("ИСУН", "ot"),
            ("АСУТП / ТМ", "ot"),
            ("ТМ АГЗУ", "ot"),
            ("КУУН НПС-3", "ot"),
            ("СДМО", "ot"),
            ("KTM Floboss", "ot"),
        ],
        cols=2,
    )

    corp = d.container(
        "Бизнес-системы и корпоративные порталы",
        560, 92,
        [
            ("СЭД Directum /\nСАПФИР", "corp"),
            ("ИСОТ / ЭНД", "corp"),
            ("СДД", "corp"),
            ("Procu / Price", "corp"),
            ("БДА", "corp"),
            ("Портал Team", "corp"),
            ("Интранет", "corp"),
            ("ИСУП", "corp"),
            ("Compliance", "corp"),
            ("ИС «УТО»", "corp"),
            ("sPoint", "corp"),
            ("КГИС", "corp"),
            ("Argus Pro\n(GPS)", "corp"),
        ],
        cols=3,
    )

    doc = d.container(
        "Документооборот и архив",
        560, 536,
        [("Alfresco (ЭА)", "doc"), ("Электронный архив\nDocumentum / Азия-Софт", "doc")],
        cols=2,
    )

    sap = d.container(
        "SAP ERP — корпоративный хаб",
        1260, 92,
        [("SAP ERP", "sap"), ("AVR", "sap")],
        cols=2,
    )

    fin = d.container(
        "Финансы и планирование",
        1260, 240,
        [
            ("SAS-FM", "sap"),
            ("FC · фин.\nконсолидация", "sap"),
            ("Нацбанк", "sap"),
            ("БВУ (банк)", "sap"),
            ("Platts.com", "sap"),
            ("ИС ЭСФ", "sap"),
            ("1С (зарплата)", "sap"),
            ("СИЗ", "sap"),
        ],
        cols=2,
    )

    hr = d.container(
        "Кадры и персонал",
        1260, 610,
        [("ПК «Управление\nперсоналом»", "corp"), ("E-Pass", "corp")],
        cols=2,
    )

    idz = d.container(
        "Служба каталогов",
        1730, 92,
        [("Active Directory\n(LDAP)", "id")],
        cols=1, comp_w=SIDE_W,
    )

    sec = d.container(
        "Информационная безопасность",
        1730, 240,
        [
            ("Solar Dozor\n(DLP)", "sec"),
            ("Forcepoint\nWeb Gateway", "sec"),
            ("FUDO PAM", "sec"),
            ("MS Exchange", "sec"),
            ("Жулдыз", "sec"),
        ],
        cols=2,
    )

    nsi = d.container(
        "Технические интеграции / НСИ",
        1730, 536,
        [("КХД АО НК КМГ", "nsi"), ("АСУ НСИ", "nsi"), ("ИСЭЗ", "nsi")],
        cols=1, comp_w=SIDE_W,
    )

    # ------------------------------------------------------------------ zones (фон)
    def add_zone(title: str, members: List[Object], pad: int = 16, top_band: int = 52) -> None:
        x0, y0, x1, y1 = d.bbox(members)
        d.zone(title, x0 - pad, y0 - pad - top_band, (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad + top_band)

    add_zone(
        "Цифровой контур ЭМГ · ядро + промышленный (OT)",
        list(core.values()) + list(im_band.values()) + list(ot.values()), top_band=44,
    )
    add_zone(
        "Корпоративные информационные системы группы КМГ",
        list(corp.values()) + list(doc.values()) + list(sap.values()) + list(fin.values()) + list(hr.values()),
    )
    add_zone(
        "Идентификация, информационная безопасность и технические интеграции",
        list(idz.values()) + list(sec.values()) + list(nsi.values()),
    )

    # ------------------------------------------------------------------ связи
    IM = im_band["ИМ · cmv2 · 10.32.10.99"]
    AD = idz["Active Directory\n(LDAP)"]
    SAP = sap["SAP ERP"]
    UTO = corp["ИС «УТО»"]

    # --- OT → ИМ (раздел 19): чистые полосы; нижние ряды обходят верхние ---
    # столбец 0 (центр ~152) обходит слева, столбец 1 (центр ~358) — справа
    d.route(ot["ИСУН"], T(0.5), IM, B(0.24), "OPC DA·2ч")
    d.route(ot["АСУТП / ТМ"], T(0.5), IM, B(0.76), "OPC UA·5м")
    d.route(ot["ТМ АГЗУ"], T(0.5), IM, B(0.10), "АГЗУ·5м",
            waypoints=[(152, 908), (48, 908), (48, 758), (97, 758)])
    d.route(ot["СДМО"], T(0.5), IM, B(0.18), "MySQL·1ч",
            waypoints=[(152, 982), (52, 982), (52, 746), (129, 746)])
    d.route(ot["КУУН НПС-3"], T(0.5), IM, B(0.90), "Modbus·2ч",
            waypoints=[(358, 908), (462, 908), (462, 758), (413, 758)])
    d.route(ot["KTM Floboss"], T(0.5), IM, B(0.82), "SQL",
            waypoints=[(358, 982), (470, 982), (470, 746), (381, 746)])
    d.route(core["ИС ABAI"], B(0.3), IM, T(0.3), "SQL read · 08:00/13:30/18:00")
    d.route(core["АСДЦ"], B(0.5), IM, T(0.7), "диспетчеризация", dashed=True)

    # --- ИС «УТО ЭМГ» → ИС «УТО» (локальный контур) ---
    d.route(core["ИС «УТО ЭМГ»"], R(0.5), UTO, L(0.5), "локальный контур → УТО")

    # --- Организационный контур (владение / governance) ---
    d.route(org["АО «Эмбамунайгаз»"], B(0.5), core["ИС ABAI"], T(0.5), "владеет / эксплуатирует", dashed=True)
    d.route(org["КЦ КМГ"], R(0.5), SAP, L(0.2), "корпоративный учёт", dashed=True)
    d.route(org["КМГИ"], R(0.5), corp["ИСУП"], L(0.5), "проекты", dashed=True)

    # --- SAP ERP — хаб предприятия (раздел 18) ---
    # верхний ряд финансов — короткие связи сверху
    d.route(fin["SAS-FM"], T(0.5), SAP, B(0.20), "RFC / .sas7bdat / CSV")
    d.route(SAP, B(0.80), fin["FC · фин.\nконсолидация"], T(0.5), "CSV (ЕКП)")
    # левый столбец финансов — через левый коридор, вход слева
    d.route(fin["Нацбанк"], L(0.5), SAP, B(0.15), "XML (курсы)",
            waypoints=[(1240, 385), (1240, 206), (1306, 206)])
    d.route(SAP, B(0.22), fin["Platts.com"], L(0.5), "API (котировки)",
            waypoints=[(1319, 212), (1226, 212), (1226, 459)])
    d.route(SAP, B(0.30), fin["1С (зарплата)"], L(0.5), "CSV (зарплата)",
            waypoints=[(1334, 218), (1212, 218), (1212, 533)])
    # правый столбец финансов — через правый коридор, вход справа
    d.route(SAP, B(0.70), fin["БВУ (банк)"], R(0.5), "MT940 / MT103", bidir=True,
            waypoints=[(1410, 224), (1700, 224), (1700, 385)])
    d.route(SAP, B(0.78), fin["ИС ЭСФ"], R(0.5), "XML (ЭСФ)", bidir=True,
            waypoints=[(1425, 230), (1712, 230), (1712, 459)])
    d.route(SAP, B(0.62), fin["СИЗ"], R(0.5), "XLSX",
            waypoints=[(1395, 236), (1722, 236), (1722, 533)])
    # AVR (в контейнере SAP)
    d.route(sap["AVR"], L(0.5), SAP, R(0.5), "API XML", bidir=True)
    # ИС «УТО» ↔ SAP — через нижний коридор корпоративной зоны
    d.route(UTO, B(0.5), SAP, B(0.55), "SOAP XML", bidir=True,
            waypoints=[(672, 520), (1245, 520), (1245, 200)])
    # Электронный архив / Documentum ↔ SAP
    d.route(doc["Электронный архив\nDocumentum / Азия-Софт"], R(0.5), SAP, B(0.50),
            "API (договоры/акты)", bidir=True, waypoints=[(1235, 607), (1235, 200)])
    # SAP → АСУТП/ТМ (данные оборудования, SCADA) — нижний периметр
    d.route(SAP, L(0.9), ot["АСУТП / ТМ"], R(0.5), "API XML (SCADA)",
            waypoints=[(1255, 186), (1255, 1092), (520, 1092), (520, 871)])
    # SAP ↔ АСУ НСИ — правый коридор
    d.route(SAP, R(0.6), nsi["АСУ НСИ"], L(0.4), "SAP PO / XML", bidir=True,
            waypoints=[(1716, 169), (1716, 675)])

    # --- Кадры ---
    d.route(hr["ПК «Управление\nперсоналом»"], R(0.7), SAP, B(0.95), "SOAP / DB · табельные",
            bidir=True, waypoints=[(1724, 693), (1724, 205)])
    d.route(hr["ПК «Управление\nперсоналом»"], L(0.5),
            doc["Электронный архив\nDocumentum / Азия-Софт"], R(0.7), "CMIS XML")
    d.route(hr["ПК «Управление\nперсоналом»"], L(0.85), corp["Портал Team"], R(0.5),
            "DB (корп. портал)", dashed=True, waypoints=[(1228, 701), (1228, 237)])

    # --- Procu / закупки ---
    d.route(corp["Procu / Price"], R(0.5), nsi["АСУ НСИ"], L(0.4), "API JSON", bidir=True)
    d.route(corp["Procu / Price"], R(0.4), nsi["ИСЭЗ"], L(0.5), "API JSON", bidir=True)

    # --- КХД (sPoint, САПФИР) ---
    d.route(corp["sPoint"], R(0.5), nsi["КХД АО НК КМГ"], L(0.3), "API JSON")
    d.route(corp["СЭД Directum /\nСАПФИР"], R(0.2), nsi["КХД АО НК КМГ"], L(0.6), "REST JSON")

    # --- Argus Pro → ИС «УТО» ---
    d.route(corp["Argus Pro\n(GPS)"], L(0.5), UTO, B(0.5), "REST JSON")

    # --- ИБ: Exchange/Forcepoint → Solar Dozor ---
    d.route(sec["MS Exchange"], L(0.5), sec["Solar Dozor\n(DLP)"], R(0.5), "BCC (почта)", dashed=True)
    d.route(sec["Forcepoint\nWeb Gateway"], B(0.5), sec["Solar Dozor\n(DLP)"], R(0.8), "ICAP (веб)", dashed=True)

    # --- LDAP → Active Directory (единый каталог учётных записей) ---
    ldap_left = [
        ("СЭД Directum /\nСАПФИР", 0.18),
        ("ИСОТ / ЭНД", 0.30),
        ("СДД", 0.42),
        ("Procu / Price", 0.54),
        ("Портал Team", 0.66),
        ("Интранет", 0.78),
        ("Compliance", 0.86),
        ("КГИС", 0.94),
    ]
    for i, (lbl, ey) in enumerate(ldap_left):
        d.route(corp[lbl], R(0.5 if i % 2 == 0 else 0.7), AD, L(ey), "LDAP" if i == 0 else "", ldap=True)
    d.route(doc["Alfresco (ЭА)"], R(0.5), AD, L(0.5), "LDAP", ldap=True)
    d.route(sec["Solar Dozor\n(DLP)"], T(0.5), AD, B(0.25), "LDAP", ldap=True)
    d.route(sec["FUDO PAM"], T(0.5), AD, B(0.55), "LDAP", ldap=True)
    d.route(sec["Жулдыз"], T(0.5), AD, B(0.75), "", ldap=True)
    d.route(hr["E-Pass"], T(0.5), AD, B(0.9), "LDAP", ldap=True)

    # ------------------------------------------------------------------ легенда
    legend = make_obj(
        value="Легенда",
        position=(40, 1130),
        width=1660, height=160,
        baseStyle=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#999999;"
            "verticalAlign=top;align=left;fontStyle=1;spacingLeft=10;spacingTop=6;"
        ),
    )
    d._add(legend, 40, 1130, 1660, 160)

    legend_items = [
        ("Ядро цифровизации ЭМГ", "emg"),
        ("Промышленный контур (OT)", "ot"),
        ("Корпоративные ИС", "corp"),
        ("SAP / финансы / планирование", "sap"),
        ("Документооборот / архив", "doc"),
        ("Информационная безопасность", "sec"),
        ("Идентификация (AD)", "id"),
        ("НСИ / технические интеграции", "nsi"),
    ]
    for i, (label, kind) in enumerate(legend_items):
        col, row = i % 4, i // 4
        sx, sy = 60 + col * 410, 1172 + row * 46
        d._add(make_obj(value="", position=(sx, sy), width=32, height=22, baseStyle=comp_style(kind)), sx, sy, 32, 22)
        cx2, cy2 = 100 + col * 410, 1172 + row * 46
        d._add(
            make_obj(value=label, position=(cx2, cy2), width=300, height=22,
                     baseStyle="text;html=1;align=left;verticalAlign=middle;fontSize=11;"),
            cx2, cy2, 300, 22,
        )

    note = make_obj(
        value=(
            "Сплошная линия — синхронный вызов / поток данных (с протоколом и форматом).\n"
            "Двойная стрелка — двусторонний обмен (↔).\n"
            "Фиолетовый пунктир — асинхронные / служебные потоки (диспетчеризация, владение).\n"
            "Серый пунктир — LDAP-аутентификация через Active Directory.\n"
            "«Мостик»-дужка на линии — пересечение без соединения."
        ),
        position=(1730, 1130),
        width=446, height=160,
        baseStyle="text;html=1;align=left;verticalAlign=top;fontSize=10;fontColor=#5A5A5A;spacingLeft=8;spacingTop=8;",
    )
    d._add(note, 1730, 1130, 446, 160)

    return f, d


def render_svg(d: Diagram, svg_path: Path) -> bool:
    """Faithful static SVG/PNG preview drawn from the exact anchored polylines."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
    except Exception as exc:  # pragma: no cover - optional dependency
        print(f"SKIP svg preview ({exc})")
        return False

    def color(style: str, key: str, default: str) -> str:
        m = re.search(rf"{key}=(#[0-9A-Fa-f]{{6}}|none)", style)
        return m.group(1) if m else default

    fig, ax = plt.subplots(figsize=(22.4, 13.2))
    ax.set_xlim(0, 2240)
    ax.set_ylim(0, 1320)
    ax.invert_yaxis()
    ax.axis("off")

    def z(s: dict) -> int:
        st = s["style"]
        if "dashed=1;dashPattern" in st:
            return 0
        if "fillColor=#EEF2F7" in st:
            return 1
        return 2

    for s in sorted(d.shapes, key=z):
        st = s["style"]
        fill = color(st, "fillColor", "#ffffff")
        module = "shape=module" in st
        actor = "fillColor=#08427B" in st
        ax.add_patch(
            Rectangle(
                (s["x"], s["y"]), s["w"], s["h"],
                facecolor="none" if fill == "none" else fill,
                edgecolor=color(st, "strokeColor", "#666666"),
                linewidth=1.2, linestyle="--" if "dashed=1" in st else "-",
                zorder=2 if module else 1,
            )
        )
        txt = s["v"].replace("&#xa;", "\n").replace("&lt;", "<").replace("&gt;", ">") if s["v"] else ""
        top = "verticalAlign=top" in st
        ax.text(
            (s["x"] + 8) if top else s["x"] + s["w"] / 2,
            (s["y"] + 6) if top else s["y"] + s["h"] / 2,
            txt, ha="left" if top else "center", va="top" if top else "center",
            fontsize=7 if module else (8 if not top else 8.5),
            color="#ffffff" if actor else "#000000",
            fontweight="bold" if (actor or top) else "normal", zorder=3,
        )

    for e in d.polylines:
        pts = e["pts"]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        c = e["color"]
        ax.plot(xs, ys, color=c, lw=1.0, ls="--" if e["dashed"] else "-", zorder=4, alpha=0.9)
        ax.annotate("", xy=pts[-1], xytext=pts[-2],
                    arrowprops=dict(arrowstyle="->", color=c, lw=1.0), zorder=4)
        if e.get("bidir"):
            ax.annotate("", xy=pts[0], xytext=pts[1],
                        arrowprops=dict(arrowstyle="->", color=c, lw=1.0), zorder=4)
        if e["label"]:
            mid = pts[len(pts) // 2]
            ax.text(mid[0], mid[1], e["label"], fontsize=5.5, color="#16407a",
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
    print(f"OK 09-emg-c4-component -> {out}")
    render_svg(d, SVG_DIR / "09-emg-c4-component.svg")


if __name__ == "__main__":
    main()
