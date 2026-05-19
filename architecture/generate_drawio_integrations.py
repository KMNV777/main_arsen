#!/usr/bin/env python3
"""Generate kmg-integrations.drawio — all integration flows from registry."""

import xml.etree.ElementTree as ET
from xml.dom import minidom

FLOWS = [
    ("SCADA ДЗО", "MySQL ЭМГ", "dbLink RT", "ABAI-SCADA"),
    ("MySQL ЭМГ", "MySQL КТМ", "dbLink ≤5м", "ABAI-SCADA"),
    ("MySQL КТМ", "MySQL SCADA КМГ", "dbLink ≤5м", "ABAI-SCADA"),
    ("MySQL SCADA КМГ", "ИС ABAI", "ETL→abaiprot", "ABAI-SCADA"),
    ("data.egov.kz", "ИС ABAI", "REST", "ABAI"),
    ("Commodities-API", "ИС ABAI", "REST/сутки", "ABAI"),
    ("AD КМГ", "ИС ABAI", "LDAP SSO", "ABAI"),
    ("Модули ABAI", "Модули ABAI", "общая БД PG", "ABAI"),
    ("abaiprot", "pg-backup VM", "pg_dump", "ABAI"),
    ("Darcy", "Techlog", "API", "ABAI"),
    ("SAP АНПЗ", "АСДЦ", "SOAP 2ч", "АСДЦ"),
    ("1С ПНХЗ", "АСДЦ", "SOAP 2ч", "АСДЦ"),
    ("1С ПКОП", "АСДЦ", "SOAP 2ч", "АСДЦ"),
    ("MES АНПЗ", "АСДЦ", "TCP 15м", "АСДЦ"),
    ("MES ПНХЗ", "АСДЦ", "TCP 15м", "АСДЦ"),
    ("QlikSense", "АСДЦ", "TCP/сутки", "АСДЦ"),
    ("nationalbank.kz", "АСДЦ", "HTTP/XML", "АСДЦ"),
    ("АСДЦ", "ИШ", "REST", "АСДЦ"),
    ("АСДЦ", "КХД", "REST", "АСДЦ"),
    ("АСДЦ", "KMG DATA", "MS SQL SP", "АСДЦ"),
    ("САПФИР", "ЕСЭДО", "SOAP 10м", "САПФИР"),
    ("ЕСЭДО", "САПФИР", "SOAP 10м", "САПФИР"),
    ("AD КМГ", "САПФИР", "LDAP", "САПФИР"),
    ("SMTP", "САПФИР", "почта", "САПФИР"),
    ("Directum Ario", "САПФИР", "захват", "САПФИР"),
    ("AD КМГ", "СДД", "LDAP", "СДД"),
    ("SMTP", "СДД", "уведомления", "СДД"),
    ("НУЦ TSP", "СДД", "REST", "СДД"),
    ("НУЦ OCSP", "СДД", "REST", "СДД"),
    ("SAP S/4", "СДД", "BP/АВР", "СДД"),
    ("СДД", "ИСЭЗ", "REST+ЭЦП", "СДД"),
    ("СДД", "ASR", "HTTP/JSON", "СДД"),
    ("СДД", "Электронный архив", "HTTP/JSON", "СДД"),
    ("SAP S/4", "Электронный архив", "HTTP :1334", "ЭА"),
    ("Kompra", "Compliance Control", "REST", "Compliance"),
    ("AD КМГ", "Compliance Control", "REST/сутки", "Compliance"),
    ("SAP", "Compliance Control", "SOAP 3×/сут", "Compliance"),
    ("AD КМГ", "BoardMaps", "LDAP", "BoardMaps"),
    ("SMTP", "BoardMaps", "SMTP", "BoardMaps"),
    ("НУЦ TSP", "BoardMaps", "ЭЦП", "BoardMaps"),
    ("AD КМГ", "Team", "LDAP", "HR"),
    ("1С", "Team", "API", "HR"),
    ("SAP КМГ", "Team", "API", "HR"),
    ("Team", "1С", "отпуска/АО", "HR"),
    ("Team", "Work", "вакансии", "HR"),
    ("Work", "Team", "этапы", "HR"),
    ("Qsamruk.kz", "Work", "редирект", "HR"),
    ("Work", "Qsamruk.kz", "резюме", "HR"),
    ("Прокторинг", "Work", "REST", "HR"),
    ("AD", "Bitrix ANPZ", "LDAP", "HR"),
    ("SAP", "Bitrix ANPZ", "API", "HR"),
    ("Bitrix ANPZ", "iJanet", "API", "HR"),
    ("Bitrix ANPZ", "Work", "API", "HR"),
    ("AD", "Bitrix Petrochem", "LDAP", "HR"),
    ("SAP", "Bitrix Petrochem", "API", "HR"),
    ("Bitrix Petrochem", "Work", "API", "HR"),
    ("AD", "Bitrix КМКЛ", "LDAP", "HR"),
    ("SAP", "Bitrix КМКЛ", "API", "HR"),
    ("Bitrix КМКЛ", "Work", "API", "HR"),
    ("AD КМГ", "ИСУП", "LDAP", "ИСУП"),
    ("КХД", "ИСУП", "запрос", "ИСУП"),
    ("ИСУП", "Power BI", "дашборды", "ИСУП"),
    ("SMTP", "ИСУП", "SMTP", "ИСУП"),
    ("AD КМГ", "Интранет SP", "LDAP", "ИСУП"),
    ("SMTP", "Интранет SP", "SMTP", "ИСУП"),
    ("SAP Price", "Procu/Price", "REST", "Закупки"),
    ("ГБД ЮЛ", "Procu/Price", "REST", "Закупки"),
    ("AD КМГ", "ИСОТ", "LDAP", "HSE"),
    ("ГБД ФЛ", "Бюро пропусков", "ESB", "откл."),
    ("HikVision", "Бюро пропусков", "REST 3с", "откл."),
]

GROUP_ORDER = [
    "ABAI-SCADA", "ABAI", "АСДЦ", "САПФИР", "СДД", "ЭА",
    "Compliance", "BoardMaps", "HR", "ИСУП", "Закупки", "HSE", "откл.",
]


def build():
    root = ET.Element("mxfile", {"host": "app.diagrams.net", "version": "22.1.0"})
    diagram = ET.SubElement(root, "diagram", {"id": "integrations", "name": "Потоки интеграций КМГ"})
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": "2400", "dy": "1800", "grid": "1", "gridSize": "10",
        "pageWidth": "1400", "pageHeight": "3400", "pageScale": "1",
    })
    groot = ET.SubElement(model, "root")
    ET.SubElement(groot, "mxCell", {"id": "0"})
    ET.SubElement(groot, "mxCell", {"id": "1", "parent": "0"})

    y_base = 40
    row_h = 320
    node_ids = {}
    nid_counter = 0

    for gi, grp in enumerate(GROUP_ORDER):
        gy = y_base + gi * row_h
        # group swimlane
        lane_id = f"lane_{gi}"
        lane = ET.SubElement(groot, "mxCell", {
            "id": lane_id,
            "value": grp,
            "style": (
                "swimlane;horizontal=0;startSize=28;fillColor=#f5f5f5;"
                "strokeColor=#666666;fontStyle=1;fontSize=12;"
            ),
            "vertex": "1", "parent": "1",
        })
        ET.SubElement(lane, "mxGeometry", {
            "x": "40", "y": str(gy), "width": "1320", "height": str(row_h - 20),
            "as": "geometry",
        })

        flows_in_grp = [f for f in FLOWS if f[3] == grp]
        seen = set()
        ordered_nodes = []
        for src, tgt, _, _ in flows_in_grp:
            for n in (src, tgt):
                if n not in seen:
                    seen.add(n)
                    ordered_nodes.append(n)

        for ni, name in enumerate(ordered_nodes):
            nid_counter += 1
            nid = f"n{nid_counter}"
            node_ids[name] = nid
            col = ni % 4
            row = ni // 4
            x = 20 + col * 310
            yy = 40 + row * 55
            cell = ET.SubElement(groot, "mxCell", {
                "id": nid,
                "value": name,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F5E9;strokeColor=#2E7D32;fontSize=11;",
                "vertex": "1", "parent": lane_id,
            })
            ET.SubElement(cell, "mxGeometry", {
                "x": str(x), "y": str(yy), "width": "140", "height": "44", "as": "geometry",
            })

        for ei, (src, tgt, lbl, _) in enumerate(flows_in_grp):
            if src not in node_ids or tgt not in node_ids:
                continue
            cell = ET.SubElement(groot, "mxCell", {
                "id": f"e_{gi}_{ei}",
                "value": lbl,
                "style": (
                    "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;fontSize=9;"
                    "strokeColor=#3949AB;endArrow=block;"
                ),
                "edge": "1", "parent": lane_id,
                "source": node_ids[src], "target": node_ids[tgt],
            })
            geo = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
            if src == tgt:
                ET.SubElement(geo, "Array", {"as": "points"})

    return root


if __name__ == "__main__":
    out = "/workspace/architecture/kmg-integrations.drawio"
    xml = minidom.parseString(ET.tostring(build(), encoding="unicode")).toprettyxml(indent="  ")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(ln for ln in xml.split("\n") if ln.strip()))
    print(f"Written {out}")
