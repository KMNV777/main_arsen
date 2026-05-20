#!/usr/bin/env python3
"""Generate draw.io C4 architecture diagrams for EMG IT landscape."""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from xml.dom import minidom

OUT = "/workspace/docs/emg-c4-architecture.drawio"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


STYLES = {
    "person": (
        "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;"
        "html=1;outlineConnect=0;fillColor=#E3F2FD;strokeColor=#1976D2;fontColor=#0D47A1;"
    ),
    "system": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F5E9;strokeColor=#2E7D32;"
        "fontColor=#1B5E20;fontStyle=1;"
    ),
    "ext": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#F3E5F5;strokeColor=#7B1FA2;"
        "fontColor=#4A148C;dashed=1;dashPattern=8 4;"
    ),
    "boundary": (
        "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#455A64;"
        "fontColor=#263238;dashed=1;verticalAlign=top;align=left;spacingLeft=10;"
        "fontStyle=1;fontSize=14;"
    ),
    "green": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#C8E6C9;strokeColor=#2E7D32;fontColor=#1B5E20;"
    ),
    "yellow": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF9C4;strokeColor=#F9A825;fontColor=#E65100;"
    ),
    "red": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFCDD2;strokeColor=#C62828;fontColor=#B71C1C;"
    ),
    "grey": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#ECEFF1;strokeColor=#78909C;fontColor=#37474F;"
    ),
    "cloud": (
        "ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#E1F5FE;strokeColor=#0277BD;"
        "fontColor=#01579B;"
    ),
    "onprem": (
        "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;"
        "size=12;fillColor=#FFF3E0;strokeColor=#E65100;fontColor=#BF360C;"
    ),
    "db": (
        "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;"
        "size=10;fillColor=#E8EAF6;strokeColor=#3949AB;fontColor=#1A237E;"
    ),
    "swim": (
        "swimlane;horizontal=0;whiteSpace=wrap;html=1;fillColor=#f5f5f5;"
        "strokeColor=#666666;fontStyle=1;startSize=30;"
    ),
    "title": (
        "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;"
        "whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=18;fontColor=#263238;"
    ),
    "legend": (
        "text;html=1;strokeColor=none;fillColor=#FAFAFA;align=left;verticalAlign=top;"
        "whiteSpace=wrap;rounded=1;fontSize=11;fontColor=#37474F;spacing=6;"
    ),
}


def v(cid, label, x, y, w, h, kind="green", parent="1"):
    return {
        "id": cid,
        "label": label,
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "style": STYLES.get(kind, STYLES["green"]),
        "parent": parent,
    }


def edge_style(dashed=False, color="#5C6BC0"):
    d = "dashed=1;" if dashed else ""
    return (
        f"edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
        f"html=1;fontSize=10;{d}strokeColor={color};endArrow=block;endFill=1;"
    )


def build_diagram(name: str, diagram_id: str, vertices: list, edges: list, page_w=2400, page_h=1600):
    model = {
        "vertices": vertices,
        "edges": edges,
        "id": diagram_id,
        "name": name,
        "page_w": page_w,
        "page_h": page_h,
    }
    return model


# --- Page 1: System Context ---
def page_context():
    vertices = [
        v("title", "C4 Level 1 — System Context: АО «Эмбамунайгаз»", 40, 20, 700, 40, "title"),
        v("legend", (
            "🟢 в эксплуатации &nbsp;|&nbsp; 🟡 план развития &nbsp;|&nbsp; 🔴 отсутствует<br/>"
            "Источник: обследование ИТ-ландшафта ЭМГ"
        ), 1700, 20, 480, 70, "legend"),
        v("p_prod", "Производственный<br/>персонал", 120, 200, 80, 100, "person"),
        v("p_corp", "Корпоративные<br/>пользователи", 120, 380, 80, 100, "person"),
        v("p_mgmt", "Руководство", 120, 560, 80, 100, "person"),
        v("p_ext", "Внешние<br/>пользователи", 120, 740, 80, 100, "person"),
        v("emg", "ИТ-ландшафт ЭМГ<br/><br/>Корпоративные и производственные<br/>информационные системы", 520, 380, 360, 160, "system"),
        v("abai", "ИС ABAI<br/>(КМГ)<br/>БД скважин, отчёты", 1100, 180, 200, 90, "ext"),
        v("kmg_cc", "Корп. центр КМГ<br/>SMAX, план. КХД", 1100, 320, 200, 80, "ext"),
        v("kmg_eng", "КМГ Инжиниринг<br/>ABAI, ИСУН", 1100, 450, 200, 80, "ext"),
        v("qazcloud", "Qazcloud<br/>IaaS + ОЦИБ SOC", 1100, 580, 200, 80, "cloud"),
        v("samruk", "Самрук-Казына<br/>ИСЭЗ, ИСЗЗ", 1100, 710, 200, 80, "ext"),
        v("vendors", "Вендоры<br/>SAP, Schlumberger…", 1100, 840, 200, 80, "ext"),
    ]
    edges = [
        ("p_prod", "emg", "добыча, мониторинг"),
        ("p_corp", "emg", "учёт, СЭД, закупки"),
        ("p_mgmt", "emg", "отчётность"),
        ("p_ext", "emg", "emg.kz"),
        ("emg", "abai", "промысловые данные", False, "#2E7D32"),
        ("emg", "kmg_cc", "ITSM, отчётность"),
        ("emg", "kmg_eng", "ABAI, ИСУН"),
        ("emg", "qazcloud", "размещение, SOC"),
        ("emg", "samruk", "закупки"),
        ("emg", "vendors", "лицензии"),
        ("kmg_eng", "abai", "сопровождение", True, "#7B1FA2"),
    ]
    return build_diagram("01 — C4 Context", "emg-c4-context", vertices, edges)


# --- Page 2: Container main ---
def page_container():
    vertices = [
        v("title", "C4 Level 2 — Container: ИТ-ландшафт ЭМГ", 40, 20, 600, 40, "title"),
        v("bound_emg", "АО «Эмбамунайгаз»", 280, 80, 1500, 900, "boundary"),
        # Users
        v("p_prod", "Производственный<br/>персонал", 40, 200, 70, 90, "person"),
        v("p_corp", "Корпоративные<br/>пользователи", 40, 400, 70, 90, "person"),
        v("p_mgmt", "Руководство", 40, 600, 70, 90, "person"),
        # Corporate row
        v("sap", "SAP ERP<br/>🟢 FI, CO, MM, PM, TOPO, MDM<br/>☁️ Qazcloud", 320, 140, 170, 80, "green", "bound_emg"),
        v("onec", "1С 8.2 Зарплата<br/>🟡 план замены<br/>☁️", 520, 140, 150, 80, "yellow", "bound_emg"),
        v("directum", "Directum СЭД<br/>🟢 ☁️", 700, 140, 140, 80, "green", "bound_emg"),
        v("alfresco", "Alfresco ECM<br/>🟢 ☁️", 870, 140, 140, 80, "green", "bound_emg"),
        v("advanta", "Advanta PM<br/>🟢 ☁️", 1040, 140, 130, 80, "green", "bound_emg"),
        v("portal", "Портал emg.kz<br/>🟢 ☁️", 1200, 140, 130, 80, "green", "bound_emg"),
        v("portal_int", "Внутр. портал<br/>🔴", 1360, 140, 120, 80, "red", "bound_emg"),
        # Production analytics
        v("ofm", "OFM / Жулдыз<br/>🟢 ☁️", 320, 260, 150, 70, "green", "bound_emg"),
        v("situational", "Ситуационный центр<br/>🟢 ☁️", 500, 260, 160, 70, "green", "bound_emg"),
        v("eng", "Инженерное ПО<br/>Petrel, ArcGIS, Revit…<br/>🟢 Workstation", 690, 260, 200, 70, "green", "bound_emg"),
        # OT
        v("scada", "АСУ ТП / SCADA<br/>WinCC, DeltaV, Mirol<br/>🟢 🏭", 320, 380, 200, 80, "green", "bound_emg"),
        v("rtdb", "БД реального времени<br/>Historian<br/>🟢 🏭", 550, 380, 180, 80, "green", "bound_emg"),
        v("monitor", "Мониторинг<br/>ArgusPro, Wialon, PetroLine<br/>🟢 🏭/☁️", 760, 380, 220, 80, "green", "bound_emg"),
        # IB
        v("ib", "ИБ: Kaspersky + Solar Dozor<br/>🟢", 1020, 380, 200, 80, "green", "bound_emg"),
        # Missing
        v("miss_plan", "🔴 Планирование<br/>добычи / ГТМ", 320, 520, 160, 70, "red", "bound_emg"),
        v("miss_anal", "🔴 Произв. аналитика<br/>ГНО, заводнение, ИМ", 510, 520, 180, 70, "red", "bound_emg"),
        v("miss_digital", "🔴 Цифровое<br/>месторождение", 720, 520, 150, 70, "red", "bound_emg"),
        v("miss_dwh", "🔴 КХД / BI<br/>(план КМГ)", 900, 520, 140, 70, "red", "bound_emg"),
        v("miss_esb", "🔴 ESB<br/>point-to-point", 1070, 520, 140, 70, "red", "bound_emg"),
        v("miss_eco", "🔴 Экомониторинг", 1240, 520, 130, 70, "red", "bound_emg"),
        v("miss_kpi", "🔴 Страт. KPI", 1400, 520, 120, 70, "red", "bound_emg"),
        # External
        v("abai", "ИС ABAI (КМГ)", 1900, 200, 180, 70, "ext"),
        v("smax", "SMAX ITSM (КМГ)<br/>🟢 с 2023", 1900, 320, 180, 70, "ext"),
        v("qazcloud", "Qazcloud IaaS + SOC", 1900, 440, 180, 70, "cloud"),
        v("kmg_eng", "КМГ Инжиниринг", 1900, 560, 180, 70, "ext"),
        v("samruk", "Самрук-Казына", 1900, 680, 180, 70, "ext"),
    ]
    edges = [
        ("p_prod", "scada", "HMI"),
        ("p_prod", "abai", "данные"),
        ("p_corp", "sap", "учёт"),
        ("p_corp", "smax", "ITSM"),
        ("p_mgmt", "situational", "дашборды"),
        ("p_mgmt", "ofm", "анализ"),
        ("scada", "rtdb", "телеметрия"),
        ("rtdb", "abai", "🔴 не подтв.", True, "#C62828"),
        ("sap", "abai", "p2p"),
        ("directum", "alfresco", "архив"),
        ("bound_emg", "qazcloud", "☁️ хостинг", True, "#0277BD"),
        ("kmg_eng", "abai", "сопровождение"),
    ]
    return build_diagram("02 — C4 Container", "emg-c4-container", vertices, edges, 2200, 1100)


# --- Page 3: Data ---
def page_data():
    vertices = [
        v("title", "C4 Level 2 — Данные и интеграции ЭМГ", 40, 20, 550, 40, "title"),
        v("bound", "Контур данных", 200, 80, 1700, 750, "boundary"),
        v("abai_db", "ABAI: Базы данных<br/>🟢 скважины, добыча<br/>6/58 отчётов", 240, 140, 200, 90, "green", "bound"),
        v("abai_aux", "ABAI: расчёты<br/>🟡 вспомог.", 480, 140, 160, 80, "yellow", "bound"),
        v("abai_nsi", "ИС АСУ НСИ<br/>🟡", 670, 140, 140, 80, "yellow", "bound"),
        v("abai_lab", "Лабораторные<br/>🟡", 840, 140, 140, 80, "yellow", "bound"),
        v("abai_pass", "Паспортизация<br/>🟡 + SAP PM", 1010, 140, 160, 80, "yellow", "bound"),
        v("sap_db", "SAP ERP БД<br/>🟢", 240, 280, 160, 80, "green", "bound"),
        v("onec_db", "1С 8.2 БД<br/>🟡", 430, 280, 140, 80, "yellow", "bound"),
        v("alf_db", "Alfresco<br/>🟢", 600, 280, 140, 80, "green", "bound"),
        v("rtdb", "Historian RTDB<br/>🟢 🏭", 770, 280, 160, 80, "green", "bound"),
        v("tbd", "ТБД (архив)<br/>⚫ с IV кв. 2024", 960, 280, 160, 80, "grey", "bound"),
        v("miss_mdm", "🔴 MDM / Data Office", 240, 420, 180, 70, "red", "bound"),
        v("miss_dwh", "🔴 КХД / Data Lake<br/>(план КМГ)", 450, 420, 180, 70, "red", "bound"),
        v("miss_esb", "🔴 ESB / API Gateway", 660, 420, 180, 70, "red", "bound"),
        v("kmg_eng", "КМГ Инжиниринг<br/>разработка ABAI", 1200, 140, 180, 80, "ext"),
        v("p_analyst", "Аналитик", 40, 200, 70, 90, "person"),
    ]
    edges = [
        ("p_analyst", "abai_db", "отчёты"),
        ("abai_db", "abai_aux", ""),
        ("abai_db", "abai_nsi", "НСИ"),
        ("abai_db", "abai_lab", ""),
        ("abai_db", "abai_pass", ""),
        ("sap_db", "abai_db", "p2p"),
        ("onec_db", "sap_db", "🔴 источник?", True, "#C62828"),
        ("rtdb", "abai_db", "🔴 не подтв.", True, "#C62828"),
        ("tbd", "abai_db", "миграция"),
        ("kmg_eng", "abai_db", "52 отчёта"),
    ]
    return build_diagram("03 — C4 Data", "emg-c4-data", vertices, edges)


# --- Page 4: ABAI components ---
def page_abai():
    vertices = [
        v("title", "C4 Level 3 — Component: ИС ABAI (использование ЭМГ)", 40, 20, 600, 40, "title"),
        v("bound", "ИС ABAI (централизованная, КМГ)", 200, 80, 1400, 600, "boundary"),
        v("db_mod", "Модуль «Базы данных»<br/>🟢 скважины, эксплуатация", 240, 150, 220, 80, "green", "bound"),
        v("reports", "Отчётный модуль<br/>🟡 6/58 форм", 500, 150, 180, 80, "yellow", "bound"),
        v("calc", "Аналит. расчёты<br/>🟡", 720, 150, 150, 80, "yellow", "bound"),
        v("nsi", "ИС АСУ НСИ<br/>🟡", 900, 150, 140, 80, "yellow", "bound"),
        v("lab", "Лабораторные<br/>🟡", 1080, 150, 140, 80, "yellow", "bound"),
        v("passport", "Паспортизация<br/>🟡", 1260, 150, 150, 80, "yellow", "bound"),
        v("gtm", "Анализ ГТМ<br/>🔴", 240, 300, 140, 70, "red", "bound"),
        v("gno", "Подбор ГНО<br/>🔴", 410, 300, 140, 70, "red", "bound"),
        v("water", "Заводнение<br/>🔴", 580, 300, 140, 70, "red", "bound"),
        v("im", "Система ИМ<br/>🔴", 750, 300, 140, 70, "red", "bound"),
        v("support", "Service Desk<br/>🟢", 920, 300, 150, 70, "green", "bound"),
        v("p_eng", "Инженер ЭМГ", 40, 200, 70, 90, "person"),
        v("p_rep", "Отчётность", 40, 400, 70, 90, "person"),
        v("kmg_eng", "КМГ Инжиниринг", 1700, 200, 180, 80, "ext"),
        v("sap", "SAP ERP PM", 1700, 350, 150, 70, "ext"),
        v("scada", "SCADA/DCS", 1700, 480, 150, 70, "ext"),
    ]
    edges = [
        ("p_eng", "db_mod", "данные"),
        ("p_eng", "calc", "расчёты"),
        ("p_rep", "reports", "отчёты"),
        ("p_rep", "support", "заявки"),
        ("db_mod", "reports", ""),
        ("db_mod", "calc", ""),
        ("db_mod", "nsi", ""),
        ("passport", "sap", "p2p"),
        ("scada", "db_mod", "🔴", True, "#C62828"),
        ("kmg_eng", "db_mod", "сопровождение"),
        ("kmg_eng", "reports", "доработка"),
    ]
    return build_diagram("04 — C4 ABAI", "emg-c4-abai", vertices, edges)


# --- Page 5: OT ---
def page_ot():
    vertices = [
        v("title", "C4 Level 3 — Component: АСУ ТП и мониторинг (🏭 ЦОД)", 40, 20, 620, 40, "title"),
        v("bound", "Производственный контур", 200, 80, 1500, 550, "boundary"),
        v("wincc", "WinCC SCADA<br/>🟢", 240, 140, 130, 70, "green", "bound"),
        v("deltav", "DCS DeltaV<br/>🟢", 400, 140, 130, 70, "green", "bound"),
        v("mirol", "СДМО Mirol<br/>🟢", 560, 140, 130, 70, "green", "bound"),
        v("wincc_oa", "WINCC OA<br/>🟢", 720, 140, 130, 70, "green", "bound"),
        v("rtdb", "Historian RTDB<br/>🟢", 900, 140, 150, 70, "green", "bound"),
        v("askue", "АСКУЭ<br/>🟢", 240, 260, 120, 60, "green", "bound"),
        v("petrol", "PetroLine<br/>🟢", 390, 260, 120, 60, "green", "bound"),
        v("video", "Видеонаблюдение<br/>🟢", 540, 260, 140, 60, "green", "bound"),
        v("argus", "ArgusPro GPS<br/>🟢 с 2025", 710, 260, 140, 60, "green", "bound"),
        v("wialon", "Wialon<br/>🟢", 880, 260, 110, 60, "green", "bound"),
        v("p_op", "Оператор", 40, 180, 70, 90, "person"),
        v("abai", "ИС ABAI", 1750, 200, 150, 70, "ext"),
        v("sap", "SAP TOPO", 1750, 350, 150, 70, "ext"),
    ]
    edges = [
        ("p_op", "wincc", ""),
        ("wincc", "rtdb", ""),
        ("deltav", "rtdb", ""),
        ("mirol", "rtdb", ""),
        ("wincc_oa", "rtdb", ""),
        ("askue", "rtdb", ""),
        ("rtdb", "abai", "🔴", True, "#C62828"),
        ("rtdb", "sap", "🔴", True, "#C62828"),
    ]
    return build_diagram("05 — C4 OT/SCADA", "emg-c4-ot", vertices, edges)


# --- Page 6: Deployment ---
def page_deployment():
    vertices = [
        v("title", "C4 Deployment — размещение систем ЭМГ", 40, 20, 500, 40, "title"),
        v("qaz_lane", "Qazcloud IaaS (VMware)", 200, 100, 700, 400, "swim"),
        v("sap", "SAP ERP", 230, 160, 140, 60, "green", "qaz_lane"),
        v("onec", "1С 8.2", 400, 160, 120, 60, "yellow", "qaz_lane"),
        v("directum", "Directum", 550, 160, 120, 60, "green", "qaz_lane"),
        v("alfresco", "Alfresco", 230, 260, 120, 60, "green", "qaz_lane"),
        v("portal", "Портал emg.kz", 380, 260, 130, 60, "green", "qaz_lane"),
        v("ib", "Kaspersky + DLP", 550, 260, 150, 60, "green", "qaz_lane"),
        v("onprem_lane", "Собственный ЦОД ЭМГ", 200, 550, 700, 350, "swim"),
        v("scada_cl", "Кластер АСУ ТП", 230, 600, 300, 80, "onprem", "onprem_lane"),
        v("mon_cl", "Мониторинг (ArgusPro, PetroLine)", 560, 600, 280, 80, "onprem", "onprem_lane"),
        v("kmg_lane", "Инфраструктура КМГ", 1000, 100, 400, 300, "swim"),
        v("abai", "ИС ABAI", 1030, 160, 160, 70, "ext", "kmg_lane"),
        v("smax", "SMAX ITSM", 1030, 280, 160, 70, "ext", "kmg_lane"),
        v("soc", "ОЦИБ SOC", 1030, 400, 160, 60, "cloud", "kmg_lane"),
    ]
    edges = [
        ("onprem_lane", "qaz_lane", "VPN / защищённые каналы"),
        ("qaz_lane", "kmg_lane", "корп. интеграции"),
        ("ib", "soc", "события ИБ"),
    ]
    return build_diagram("06 — C4 Deployment", "emg-c4-deploy", vertices, edges)


def render_diagram(diagram: dict) -> ET.Element:
    diagram_el = ET.Element("diagram", {
        "id": diagram["id"],
        "name": diagram["name"],
    })
    model = ET.SubElement(diagram_el, "mxGraphModel", {
        "dx": "1800",
        "dy": "1000",
        "grid": "1",
        "gridSize": "10",
        "guides": "1",
        "tooltips": "1",
        "connect": "1",
        "arrows": "1",
        "fold": "1",
        "page": "1",
        "pageScale": "1",
        "pageWidth": str(diagram["page_w"]),
        "pageHeight": str(diagram["page_h"]),
        "math": "0",
        "shadow": "0",
    })
    groot = ET.SubElement(model, "root")
    ET.SubElement(groot, "mxCell", {"id": "0"})
    ET.SubElement(groot, "mxCell", {"id": "1", "parent": "0"})

    prefix = diagram["id"][:8]

    def nid(cid: str) -> str:
        return f"{prefix}_{cid}"

    id_map = {}

    for vert in diagram["vertices"]:
        uid = nid(vert["id"])
        id_map[vert["id"]] = uid
        parent = "1"
        if vert["parent"] != "1":
            parent = id_map.get(vert["parent"], nid(vert["parent"]))

        cell = ET.SubElement(groot, "mxCell", {
            "id": uid,
            "value": vert["label"],
            "style": vert["style"],
            "vertex": "1",
            "parent": parent,
        })
        geo = ET.SubElement(cell, "mxGeometry", {
            "x": str(vert["x"]),
            "y": str(vert["y"]),
            "width": str(vert["w"]),
            "height": str(vert["h"]),
            "as": "geometry",
        })
        if parent != "1":
            geo.set("relative", "0")

    edge_id = 0
    for item in diagram["edges"]:
        if len(item) == 3:
            src, tgt, lbl = item
            dashed, color = False, "#5C6BC0"
        elif len(item) == 4:
            src, tgt, lbl, dashed = item
            color = "#5C6BC0"
        else:
            src, tgt, lbl, dashed, color = item

        edge_id += 1
        eid = f"{prefix}_e{edge_id}"
        cell = ET.SubElement(groot, "mxCell", {
            "id": eid,
            "value": lbl,
            "style": edge_style(dashed, color),
            "edge": "1",
            "parent": "1",
            "source": id_map[src],
            "target": id_map[tgt],
        })
        ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})

    return diagram_el


def build_mxfile() -> ET.Element:
    pages = [
        page_context(),
        page_container(),
        page_data(),
        page_abai(),
        page_ot(),
        page_deployment(),
    ]
    root = ET.Element("mxfile", {
        "host": "app.diagrams.net",
        "agent": "EMG-C4-Generator",
        "version": "22.1.0",
        "type": "device",
        "pages": str(len(pages)),
    })
    for page in pages:
        root.append(render_diagram(page))
    return root


def main():
    tree = build_mxfile()
    rough = ET.tostring(tree, encoding="unicode")
    xml = minidom.parseString(rough).toprettyxml(indent="  ")
    lines = [ln for ln in xml.split("\n") if ln.strip()]
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Written {OUT} ({len(lines)} lines, 6 pages)")


if __name__ == "__main__":
    main()
