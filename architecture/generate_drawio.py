#!/usr/bin/env python3
"""Generate kmg-it-landscape.drawio with nodes and integration edges."""

import html
import xml.etree.ElementTree as ET
from xml.dom import minidom

# (id, label, x, y, w, h, style_suffix)
# style_suffix: user|ext|gov|src|app|app_test|app_out|layer|infra

def esc(s: str) -> str:
    return html.escape(s, quote=True)


def vertex(cid, label, x, y, w, h, kind="app", parent="1"):
    styles = {
        "user": "rounded=1;whiteSpace=wrap;html=1;fillColor=#E3F2FD;strokeColor=#1976D2;fontColor=#0D47A1;",
        "gov": "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF3E0;strokeColor=#E65100;fontColor=#BF360C;",
        "ext": "rounded=1;whiteSpace=wrap;html=1;fillColor=#FCE4EC;strokeColor=#C2185B;fontColor=#880E4F;",
        "src": "rounded=1;whiteSpace=wrap;html=1;fillColor=#F3E5F5;strokeColor=#7B1FA2;fontColor=#4A148C;",
        "app": "rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F5E9;strokeColor=#2E7D32;fontColor=#1B5E20;",
        "app_test": "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFDE7;strokeColor=#F9A825;fontColor=#F57F17;",
        "app_out": "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFEBEE;strokeColor=#C62828;fontColor=#B71C1C;",
        "buf": "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF8E1;strokeColor=#F9A825;fontColor=#F57F17;",
        "layer": "rounded=0;whiteSpace=wrap;html=1;fillColor=#ECEFF1;strokeColor=#455A64;fontColor=#263238;dashed=1;",
        "swim": "swimlane;horizontal=0;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontStyle=1;",
        "cons": "rounded=1;whiteSpace=wrap;html=1;fillColor=#E1F5FE;strokeColor=#01579B;fontColor=#01579B;",
    }
    st = styles.get(kind, styles["app"])
    return {
        "id": cid,
        "label": label,
        "x": x, "y": y, "w": w, "h": h,
        "style": st,
        "parent": parent,
    }


vertices = []

# --- Swimlane: Users ---
vertices.append(vertex("lane_users", "Пользователи и потребители", 40, 40, 2400, 120, "swim"))
for cid, lbl, x in [
    ("u1", "КЦ + 8 ДЗО Upstream<br/>(ABAI, 2947 польз.)", 60),
    ("u2", "48 ДЗО + ДОТОС<br/>(HSE / ИСОТ)", 320),
    ("u3", "43 ДЗО<br/>(Compliance)", 560),
    ("u4", "СД, Правление,<br/>корп. секретариат", 800),
    ("u5", "HR / ДУЧР / кандидаты", 1040),
    ("u6", "PMO, Finance, Legal,<br/>УДО, Закупки, PR", 1280),
    ("u7", "Внешние пользователи<br/>(сайты)", 1520),
]:
    vertices.append(vertex(cid, lbl, x, 80, 220, 60, "user", "lane_users"))

# --- Swimlane: External ---
vertices.append(vertex("lane_ext", "Внешние интеграции", 40, 180, 2400, 140, "swim"))
gov = [
    ("g_esedo", "ЕСЭДО", 60),
    ("g_nuc_tsp", "НУЦ РК TSP", 200),
    ("g_nuc_ocsp", "НУЦ РК OCSP", 340),
    ("g_egov", "data.egov.kz", 480),
    ("g_gbd", "ГБД ЮЛ / ГБД ФЛ", 620),
    ("g_nb", "nationalbank.kz", 760),
]
for cid, lbl, x in gov:
    vertices.append(vertex(cid, lbl, x, 220, 120, 50, "gov", "lane_ext"))
com = [
    ("c_comm", "Commodities-API", 920),
    ("c_kompra", "Kompra", 1080),
    ("c_hik", "HikVision<br/>(откл.)", 1220),
    ("c_qsam", "Qsamruk.kz", 1360),
]
for cid, lbl, x in com:
    vertices.append(vertex(cid, lbl, x, 220, 120, 50, "ext", "lane_ext"))

# --- Swimlane: Internal sources ---
vertices.append(vertex("lane_src", "Внутренние корпоративные источники", 40, 340, 2400, 120, "swim"))
sources = [
    ("s_sap", "SAP S/4HANA", 60),
    ("s_1c", "1С<br/>(ПНХЗ, ПКОП, Фин/HR)", 220),
    ("s_mes_a", "MES Honeywell АНПЗ", 400),
    ("s_mes_p", "MES ПНХЗ", 560),
    ("s_qlik", "QlikSense Кумколь", 720),
    ("s_scada", "SCADA ДЗО", 880),
    ("s_ish", "ИШ (НПЗ/ДАЦ)", 1020),
    ("s_khd", "КХД", 1140),
    ("s_kmgd", "KMG DATA", 1260),
    ("s_isaz", "ИСЭЗ", 1380),
    ("s_ad", "Active Directory КМГ", 1500),
    ("s_smtp", "SMTP", 1680),
    ("s_darcy", "Darcy (РИГИС)", 1800),
]
for cid, lbl, x in sources:
    vertices.append(vertex(cid, lbl, x, 380, 130, 50, "src", "lane_src"))

# SCADA buffers (between src and apps)
vertices.append(vertex("buf_emg", "MySQL ЭМГ", 880, 500, 100, 40, "buf"))
vertices.append(vertex("buf_ktm", "MySQL КТМ", 1000, 500, 100, 40, "buf"))
vertices.append(vertex("buf_kmg", "MySQL SCADA КМГ", 1120, 500, 130, 40, "buf"))

# --- Application layer swimlane ---
vertices.append(vertex("lane_app", "Прикладной слой (информационные системы)", 40, 560, 2400, 520, "swim"))

apps = [
    # Upstream
    ("a_abai", "ИС ABAI<br/>abai.kmg.kz<br/>17 модулей", 60, 600, 160, 70, "app"),
    # Doc
    ("a_sapfir", "САПФИР<br/>docs.kmg.kz", 260, 600, 140, 70, "app"),
    ("a_sdd", "СДД<br/>contract.kmg.kz", 420, 600, 130, 70, "app"),
    ("a_ea", "Электронный архив<br/>(ВЫВОД)", 570, 600, 140, 70, "app_out"),
    ("a_bm", "BoardMaps<br/>bsd.kmg.kz", 730, 600, 130, 70, "app"),
    # Analytics
    ("a_asdc", "АСДЦ<br/>iis.thkmg.kz", 900, 600, 120, 70, "app"),
    ("a_isup", "ИСУП<br/>pmo.kmg.kz", 1040, 600, 120, 70, "app"),
    ("a_pbi", "Power BI", 1180, 600, 90, 50, "cons"),
    # HSE
    ("a_isot", "ИСОТ / ЭНД<br/>hse.kmg.kz", 60, 700, 130, 70, "app"),
    ("a_aisem", "АИСЭМ<br/>aisem.kmg.kz", 210, 700, 120, 70, "app"),
    ("a_cc", "Compliance Control<br/>compliance.kmg.kz", 350, 700, 160, 70, "app"),
    # HR
    ("a_work", "Work<br/>work.kmg.kz", 540, 700, 110, 70, "app"),
    ("a_team", "Team<br/>kmg.kz", 670, 700, 100, 70, "app"),
    ("a_anpz", "Bitrix ANPZ<br/>anpz.kz", 790, 700, 110, 70, "app"),
    ("a_petro", "Bitrix Petrochem", 920, 700, 110, 60, "app"),
    ("a_kmkl", "Bitrix КМКЛ", 1050, 700, 110, 60, "app"),
    ("a_ijanet", "iJanet АНПЗ", 1180, 700, 100, 50, "cons"),
    # Proc / Log
    ("a_procu", "Procu/Price<br/>price.kmg.kz (ТЕСТ)", 1300, 600, 150, 70, "app_test"),
    ("a_uto", "ИС УТО / УТО ЭМГ", 1300, 700, 140, 70, "app"),
    # Corp
    ("a_intranet", "Интранет<br/>SharePoint", 1470, 600, 130, 70, "app"),
    ("a_sites", "Сайты КМГ<br/>kmg.kz, kpi.kz…", 1620, 600, 140, 70, "app"),
    # Other
    ("a_bda", "БДА", 1470, 700, 80, 50, "app"),
    ("a_sanau", "Санау (ВЫВОД)", 1570, 700, 110, 50, "app_out"),
    ("a_buro", "Бюро пропусков<br/>(ОТКЛЮЧЕНА)", 1700, 700, 140, 60, "app_out"),
    ("a_techlog", "Techlog", 1860, 500, 90, 40, "cons"),
    ("a_asr", "ASR", 570, 520, 70, 40, "cons"),
    ("a_backup", "pg-backupVM1/2", 60, 520, 120, 40, "cons"),
]

for item in apps:
    cid, lbl, x, y, w, h, kind = item
    vertices.append(vertex(cid, lbl, x, y, w, h, kind, "lane_app"))

# --- Bottom layers ---
vertices.append(vertex("layer_int", "Интеграционный слой<br/>RabbitMQ • Kafka • Redis • HAProxy • ELK • GitLab<br/>⚠ API Gateway — ОТСУТСТВУЕТ", 40, 1120, 700, 100, "layer"))
vertices.append(vertex("layer_data", "Данные<br/>PostgreSQL • MS SQL • MySQL • MongoDB<br/>Druid/Spark/Kafka/Hadoop • MinIO/SeaweedFS", 40, 1240, 700, 90, "layer"))
vertices.append(vertex("layer_infra", "Инфраструктура<br/>QazCloud Koshy • QazCloud Aqqol • On-Prem • GPU ABAI", 40, 1350, 700, 80, "layer"))

# Edges: (source_id, target_id, label, style)
edges = [
    # SCADA chain
    ("s_scada", "buf_emg", "dbLink 1–30 сек"),
    ("buf_emg", "buf_ktm", "dbLink ≤5 мин"),
    ("buf_ktm", "buf_kmg", "dbLink ≤5 мин"),
    ("buf_kmg", "a_abai", "dbLink→ETL 5–15 мин"),
    # External -> ABAI
    ("g_egov", "a_abai", "REST"),
    ("c_comm", "a_abai", "REST / сутки"),
    ("s_ad", "a_abai", "LDAP SSO"),
    ("s_darcy", "a_techlog", "API 1–10/сут"),
    ("a_abai", "a_backup", "pg_dump/WAL"),
    # ASDC in/out
    ("s_sap", "a_asdc", "SOAP 2ч"),
    ("s_1c", "a_asdc", "SOAP/XML 2ч"),
    ("s_mes_a", "a_asdc", "TCP byte 15мин"),
    ("s_mes_p", "a_asdc", "TCP byte 15мин"),
    ("s_qlik", "a_asdc", "TCP / сутки"),
    ("g_nb", "a_asdc", "HTTP/XML"),
    ("a_asdc", "s_ish", "REST"),
    ("a_asdc", "s_khd", "REST"),
    ("a_asdc", "s_kmgd", "MS SQL SP"),
    # SAPFIR
    ("g_esedo", "a_sapfir", "SOAP/XML 10мин"),
    ("a_sapfir", "g_esedo", "SOAP/XML 10мин"),
    ("s_ad", "a_sapfir", "LDAP"),
    ("s_smtp", "a_sapfir", "SMTP"),
    # SDD
    ("s_ad", "a_sdd", "LDAP"),
    ("s_smtp", "a_sdd", "SMTP"),
    ("g_nuc_tsp", "a_sdd", "REST ЭЦП"),
    ("g_nuc_ocsp", "a_sdd", "REST ЭЦП"),
    ("s_sap", "a_sdd", "BP RFC/REST"),
    ("s_sap", "a_sdd", "АВР REST"),
    ("a_sdd", "s_isaz", "REST+ЭЦП"),
    ("a_sdd", "a_asr", "HTTP/JSON"),
    ("a_sdd", "a_ea", "HTTP/JSON ≤1ч"),
    # BoardMaps
    ("s_ad", "a_bm", "LDAP"),
    ("s_smtp", "a_bm", "SMTP"),
    ("g_nuc_tsp", "a_bm", "TSP ЭЦП"),
    # Compliance
    ("c_kompra", "a_cc", "REST/JSON"),
    ("s_ad", "a_cc", "REST/JSON сутки"),
    ("s_sap", "a_cc", "SOAP 3×/сут"),
    # EA
    ("s_sap", "a_ea", "HTTP/JSON :1334"),
    # HR cluster
    ("s_ad", "a_team", "LDAP"),
    ("s_1c", "a_team", "API XML/JSON"),
    ("s_sap", "a_team", "API XML/JSON"),
    ("a_team", "s_1c", "отпуска/командир."),
    ("a_team", "a_work", "вакансии/ДИ"),
    ("a_work", "a_team", "этапы отбора"),
    ("c_qsam", "a_work", "редирект"),
    ("a_work", "c_qsam", "резюме/статусы"),
    ("s_ad", "a_anpz", "LDAP"),
    ("s_sap", "a_anpz", "API"),
    ("a_anpz", "a_ijanet", "API"),
    ("a_anpz", "a_work", "API"),
    ("s_ad", "a_petro", "LDAP"),
    ("s_sap", "a_petro", "API"),
    ("a_petro", "a_work", "API"),
    ("s_ad", "a_kmkl", "LDAP"),
    ("s_sap", "a_kmkl", "API"),
    ("a_kmkl", "a_work", "API"),
    # ISUP / Intranet
    ("s_ad", "a_isup", "LDAP/NTLM"),
    ("s_khd", "a_isup", "по запросу"),
    ("a_isup", "a_pbi", "автоподгрузка"),
    ("s_smtp", "a_isup", "SMTP"),
    ("s_ad", "a_intranet", "LDAP/NTLM"),
    ("s_smtp", "a_intranet", "SMTP"),
    # Procu
    ("s_sap", "a_procu", "SAP Price REST"),
    ("g_gbd", "a_procu", "ГБД ЮЛ REST"),
    # ISOT
    ("s_ad", "a_isot", "LDAP"),
    # Disabled
    ("g_gbd", "a_buro", "ГБД ФЛ ESB"),
    ("a_buro", "g_gbd", "ГБД ФЛ"),
    ("c_hik", "a_buro", "REST 3 сек"),
    ("a_buro", "c_hik", "REST 3 сек"),
    # Users -> key apps (logical)
    ("u1", "a_abai", "использует"),
    ("u2", "a_isot", "использует"),
    ("u3", "a_cc", "использует"),
    ("u4", "a_bm", "использует"),
    ("u5", "a_work", "использует"),
    ("u5", "a_team", "использует"),
    ("u6", "a_asdc", "использует"),
    ("u6", "a_sdd", "использует"),
    ("u6", "a_procu", "использует"),
    ("u7", "a_sites", "использует"),
    # Apps -> layers (aggregate)
    ("a_abai", "layer_int", ""),
    ("a_sdd", "layer_int", ""),
    ("a_abai", "layer_data", ""),
    ("a_asdc", "layer_data", ""),
    ("lane_app", "layer_infra", "хостинг"),
]

def build_mxfile():
    root = ET.Element("mxfile", {
        "host": "app.diagrams.net",
        "agent": "KMG-IT-Landscape-Generator",
        "version": "22.1.0",
        "type": "device",
    })
    diagram = ET.SubElement(root, "diagram", {
        "id": "kmg-landscape",
        "name": "ИТ-ландшафт КМГ — связи",
    })
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": "2000", "dy": "1200", "grid": "1", "gridSize": "10",
        "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
        "fold": "1", "page": "1", "pageScale": "1",
        "pageWidth": "2500", "pageHeight": "1600",
        "math": "0", "shadow": "0",
    })
    groot = ET.SubElement(model, "root")
    ET.SubElement(groot, "mxCell", {"id": "0"})
    ET.SubElement(groot, "mxCell", {"id": "1", "parent": "0"})

    for v in vertices:
        cell = ET.SubElement(groot, "mxCell", {
            "id": v["id"],
            "value": v["label"],
            "style": v["style"],
            "vertex": "1",
            "parent": v["parent"],
        })
        geo = ET.SubElement(cell, "mxGeometry", {
            "x": str(v["x"]), "y": str(v["y"]),
            "width": str(v["w"]), "height": str(v["h"]),
            "as": "geometry",
        })
        if v["parent"] != "1":
            geo.set("relative", "0")

    edge_id = 0
    for src, tgt, lbl in edges:
        edge_id += 1
        eid = f"e{edge_id}"
        dashed = "dashed=1;" if "использует" in lbl or lbl == "" else ""
        cell = ET.SubElement(groot, "mxCell", {
            "id": eid,
            "value": lbl,
            "style": (
                f"edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;"
                f"jettySize=auto;html=1;fontSize=10;{dashed}"
                "strokeColor=#5C6BC0;endArrow=block;endFill=1;"
            ),
            "edge": "1",
            "parent": "1",
            "source": src,
            "target": tgt,
        })
        ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})

    return root


def prettify(elem):
    rough = ET.tostring(elem, encoding="unicode")
    return minidom.parseString(rough).toprettyxml(indent="  ")


if __name__ == "__main__":
    out = "/workspace/architecture/kmg-it-landscape.drawio"
    tree = build_mxfile()
    xml = prettify(tree)
    # remove extra blank lines from minidom
    lines = [ln for ln in xml.split("\n") if ln.strip()]
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Written {out} with {len(vertices)} vertices and {len(edges)} edges")
