#!/usr/bin/env python3
"""
Add integration edges to an existing draw.io file (compressed or uncompressed).
Usage:
  python3 merge_drawio_edges.py input.drawio [-o output.drawio]
  python3 merge_drawio_edges.py --url-fragment viewer_fragment.txt [-o "ИТ Ландшафт КМГ.drawio"]
"""

from __future__ import annotations

import argparse
import base64
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

from generate_drawio_integrations import FLOWS

# Extra edges from passports (not all in FLOWS)
EXTRA_FLOWS = [
    ("Directum Ario", "САПФИР", "захват", "САПФИР"),
    ("НУЦ TSP", "BoardMaps", "ЭЦП", "BoardMaps"),
    ("НУЦ OCSP", "СДД", "REST", "СДД"),
    ("SAP S/4HANA", "СДД", "BP/АВР", "СДД"),
    ("ИСЭЗ", "СДД", "АВР ЭЦП", "СДД"),  # reverse label fix below
]

ALL_FLOWS = list(FLOWS)


def decompress_diagram(text: str) -> str:
    text = text.strip()
    if text.startswith("<mxGraphModel") or text.startswith("<root"):
        return text if text.startswith("<mxGraphModel") else f"<mxGraphModel>{text}</mxGraphModel>"
    # URL-encoded base64
    if "%" in text[:30]:
        text = urllib.parse.unquote(text)
    text = re.sub(r"\s+", "", text)
    raw = base64.b64decode(text)
    for wbits in (-zlib.MAX_WBITS, zlib.MAX_WBITS):
        try:
            out = zlib.decompress(raw, wbits).decode("utf-8")
            if out.startswith("%3C") or out.startswith("%3c"):
                out = urllib.parse.unquote(out)
            return out
        except zlib.error:
            continue
    raise ValueError("Cannot decompress diagram payload")


def compress_diagram(xml: str) -> str:
    xml = xml.strip()
    if not xml.startswith("<mxGraphModel"):
        raise ValueError("Expected mxGraphModel XML")
    co = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=-zlib.MAX_WBITS)
    compressed = co.compress(xml.encode("utf-8")) + co.flush()
    return base64.b64encode(compressed).decode("ascii")


def load_drawio(path: Path) -> tuple[ET.Element, str, str | None]:
    """Returns (mxfile_root, diagram_id, diagram_name)."""
    raw = path.read_text(encoding="utf-8")
    root = ET.fromstring(raw)
    diagram = root.find("diagram")
    if diagram is None:
        raise ValueError("No <diagram> in mxfile")
    return root, diagram.get("id", "page1"), diagram.get("name", "Страница-1")


def get_model_xml(root: ET.Element) -> str:
    diagram = root.find("diagram")
    if diagram is None:
        raise ValueError("No diagram")
    # Uncompressed: mxGraphModel as child
    for child in diagram:
        if child.tag == "mxGraphModel":
            return ET.tostring(child, encoding="unicode")
    if diagram.text and diagram.text.strip():
        return decompress_diagram(diagram.text)
    raise ValueError("Empty diagram")


def set_model_xml(root: ET.Element, model_xml: str, diagram_id: str, diagram_name: str):
    # Remove old diagrams
    for d in list(root.findall("diagram")):
        root.remove(d)
    diagram = ET.SubElement(root, "diagram", {"id": diagram_id, "name": diagram_name})
    diagram.text = compress_diagram(model_xml)


def normalize_label(s: str) -> str:
    s = re.sub(r"<br\s*/?>", " ", s or "", flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").strip().lower()
    s = re.sub(r"\s+", " ", s)
    # aliases for matching user's diagram labels
    aliases = {
        "ис abai": "ис abai",
        "abai": "ис abai",
        "17 модулей abai": "ис abai",
        "scada-серверы дзо": "scada дзо",
        "scada серверы дзо": "scada дзо",
        "sap s/4hana": "sap s/4",
        "нуц рк tsp": "нуц tsp",
        "нуц рк ocsp": "нуц ocsp",
        "compliance control compliance": "compliance control",
        "procu / price": "procu/price",
        "work work.kmg": "work",
        "team (bitrix24)": "team",
        "сапфир (directum rx)": "сапфир",
        "интранет (sharepoint)": "интранет sharepoint",
        "bitrix anpz / petrochem": "bitrix anpz",
        "mes honeywell": "mes анпз",
        "mysql / mariadb": "mysql scada",
        "scada-буферы": "mysql scada",
        "scada — цепочка mysql dblink": "mysql scada",
        "иш, кхд, kmg data": "асдц",
        "1с (пнхз": "1с",
        "active directory кмг": "ad кмг",
        "сапфир": "сапфир",
        "directum": "сапфир",
        "сапфир (directum rx)": "сапфир",
        "сдд": "сдд",
        "асдц": "асдц",
        "iis.thkmg": "асдц",
        "team": "team",
        "kmg.kz": "team",
        "work": "work",
        "work.kmg": "work",
        "compliance control": "compliance control",
        "boardmaps": "boardmaps",
        "интранет": "интранет sharepoint",
        "sharepoint": "интранет sharepoint",
        "procu": "procu/price",
        "price": "procu/price",
        "электронный архив": "электронный архив",
        "эа": "электронный архив",
        "исот": "исот",
        "hse": "исот",
        "ad кмг": "ad кмг",
        "active directory": "ad кмг",
        "ad": "ad кмг",
        "sap s/4hana": "sap s/4",
        "sap s/4": "sap s/4",
        "sap": "sap s/4",
        "sap анпз": "sap анпз",
        "sap кмг": "sap кмг",
        "1с": "1с",
        "1с пнхз": "1с пнхз",
        "1с пкоп": "1с пкоп",
        "есэдо": "есэдо",
        "нуц rk tsp": "нуц tsp",
        "нуц tsp": "нуц tsp",
        "нуц rk ocsp": "нуц ocsp",
        "нуц ocsp": "нуц ocsp",
        "mysql эмг": "mysql эмг",
        "mysql ктм": "mysql ктм",
        "mysql scada": "mysql scada сервер кмг",
        "scada": "scada дзо",
        "scada дзо": "scada дзо",
    }
    for k, v in aliases.items():
        if k in s:
            s = v
            break
    return s


# Map flow endpoint names -> normalized keys
FLOW_ALIASES = {
    "ИС ABAI": "ис abai",
    "ИС «ABAI»": "ис abai",
    "ABAI": "ис abai",
    "САПФИР": "сапфир",
    "САПФИР (Directum RX)": "сапфир",
    "СДД": "сдд",
    "АСДЦ": "асдц",
    "Team": "team",
    "Team (kmg.kz)": "team",
    "Work": "work",
    "Work (work.kmg.kz)": "work",
    "Compliance Control": "compliance control",
    "BoardMaps": "boardmaps",
    "Интранет SP": "интранет sharepoint",
    "Интранет SharePoint": "интранет sharepoint",
    "Procu/Price": "procu/price",
    "Электронный архив": "электронный архив",
    "ИСОТ": "исот",
    "ИСОТ / ЭНД": "исот",
    "AD КМГ": "ad кмг",
    "AD": "ad кмг",
    "Active Directory КМГ": "ad кмг",
    "Active Directory": "ad кмг",
    "SAP S/4HANA": "sap s/4",
    "SAP S/4": "sap s/4",
    "SAP": "sap s/4",
    "SAP АНПЗ": "sap анпз",
    "SAP КМГ": "sap кмг",
    "SAP Price": "sap price",
    "1С": "1с",
    "1С ПНХЗ": "1с пнхз",
    "1С ПКОП": "1с пкоп",
    "1С (Финансы/HR)": "1с",
    "ЕСЭДО": "есэдо",
    "НУЦ TSP": "нуц tsp",
    "НУЦ OCSP": "нуц ocsp",
    "SCADA ДЗО": "scada дзо",
    "MySQL ЭМГ": "mysql эмг",
    "MySQL КТМ": "mysql ктм",
    "MySQL SCADA КМГ": "mysql scada",
    "MySQL ЭМГ": "mysql scada",
    "MySQL КТМ": "mysql scada",
    "Bitrix ANPZ": "bitrix anpz",
    "Bitrix Petrochem": "bitrix petrochem",
    "Bitrix КМКЛ": "bitrix кмкл",
    "ИСУП": "исуп",
    "Power BI": "power bi",
    "ИСЭЗ": "исэз",
    "ASR": "asr",
    "iJanet": "ijanet",
    "iJanet АНПЗ": "ijanet",
    "ИШ": "иш",
    "КХД": "кхд",
    "KMG DATA": "kmg data",
    "MES АНПЗ": "mes анпз",
    "MES ПНХЗ": "mes анпз",
    "MES Honeywell АНПЗ": "mes анпз",
    "MES Honeywell (АНПЗ, ПНХЗ)": "mes анпз",
    "QlikSense": "qliksense",
    "QlikSense Кумколь": "qliksense",
    "nationalbank.kz": "nationalbank.kz",
    "data.egov.kz": "data.egov.kz",
    "Commodities-API": "commodities-api",
    "Kompra": "kompra",
    "Qsamruk.kz": "qsamruk.kz",
    "ГБД ЮЛ": "гбд юл",
    "ГБД ФЛ": "гбд фл",
    "HikVision": "hikvision",
    "Бюро пропусков": "бюро пропусков",
    "Directum Ario": "directum ario",
    "SMTP": "smtp",
    "Darcy": "darcy",
    "Techlog": "techlog",
    "abaiprot": "abaiprot",
    "pg-backup VM": "pg-backup vm",
    "Модули ABAI": "модули abai",
    "Прокторинг": "прокторинг",
}


def flow_key(name: str) -> str:
    name = name.strip()
    if name in FLOW_ALIASES:
        return FLOW_ALIASES[name]
    return normalize_label(name)


def build_vertex_index(model_root: ET.Element) -> dict[str, list[str]]:
    """normalized_label -> [cell ids]"""
    index: dict[str, list[str]] = {}
    for cell in model_root.iter("mxCell"):
        if cell.get("vertex") != "1":
            continue
        val = cell.get("value") or ""
        if not val or cell.get("style", "").find("swimlane") >= 0:
            continue
        key = normalize_label(val)
        if not key:
            continue
        # also register FLOW_ALIASES reverse
        cid = cell.get("id")
        if cid:
            index.setdefault(key, []).append(cid)
            # partial match keys
            for token in re.split(r"[\s/()]+", key):
                if len(token) >= 4:
                    index.setdefault(token, []).append(cid)
    return index


# When user diagram uses aggregate nodes (no separate MySQL buffers, etc.)
FALLBACK_VERTEX: dict[str, str] = {
    "mysql scada": "LtTv1nw5aFLaXrCluBzj-104",  # MySQL / MariaDB … SCADA-буферы
    "mysql scada сервер кмг": "LtTv1nw5aFLaXrCluBzj-104",
    "mysql эмг": "LtTv1nw5aFLaXrCluBzj-104",
    "mysql ктм": "LtTv1nw5aFLaXrCluBzj-104",
    "scada дзо": "LtTv1nw5aFLaXrCluBzj-22",
    "sap анпз": "LtTv1nw5aFLaXrCluBzj-18",
    "sap кмг": "LtTv1nw5aFLaXrCluBzj-18",
    "sap s/4": "LtTv1nw5aFLaXrCluBzj-18",
    "sap": "LtTv1nw5aFLaXrCluBzj-18",
    "sap price": "LtTv1nw5aFLaXrCluBzj-18",
    "1с": "LtTv1nw5aFLaXrCluBzj-16",
    "1с пнхз": "LtTv1nw5aFLaXrCluBzj-16",
    "1с пкоп": "LtTv1nw5aFLaXrCluBzj-16",
    "ad": "LtTv1nw5aFLaXrCluBzj-15",
    "ad кмг": "LtTv1nw5aFLaXrCluBzj-15",
    "ис abai": "LtTv1nw5aFLaXrCluBzj-62",
    "сапфир": "LtTv1nw5aFLaXrCluBzj-58",
    "сдд": "LtTv1nw5aFLaXrCluBzj-59",
    "work": "LtTv1nw5aFLaXrCluBzj-50",
    "team": "LtTv1nw5aFLaXrCluBzj-45",
    "boardmaps": "LtTv1nw5aFLaXrCluBzj-61",
    "procu/price": "LtTv1nw5aFLaXrCluBzj-41",
    "исот": "LtTv1nw5aFLaXrCluBzj-47",
    "compliance control": "LtTv1nw5aFLaXrCluBzj-49",
    "асдц": "LtTv1nw5aFLaXrCluBzj-56",
    "исуп": "LtTv1nw5aFLaXrCluBzj-57",
    "интранет sharepoint": "LtTv1nw5aFLaXrCluBzj-40",
    "электронный архив": "LtTv1nw5aFLaXrCluBzj-60",
    "есэдо": "LtTv1nw5aFLaXrCluBzj-31",
    "нуц tsp": "LtTv1nw5aFLaXrCluBzj-32",
    "нуц ocsp": "LtTv1nw5aFLaXrCluBzj-32",
    "bitrix anpz": "LtTv1nw5aFLaXrCluBzj-46",
    "bitrix petrochem": "LtTv1nw5aFLaXrCluBzj-46",
    "bitrix кмкл": "LtTv1nw5aFLaXrCluBzj-46",
    "mes анпз": "LtTv1nw5aFLaXrCluBzj-19",
    "mes пнхз": "LtTv1nw5aFLaXrCluBzj-19",
    "иш": "LtTv1nw5aFLaXrCluBzj-20",
    "кхд": "LtTv1nw5aFLaXrCluBzj-20",
    "kmg data": "LtTv1nw5aFLaXrCluBzj-20",
    "исэз": "LtTv1nw5aFLaXrCluBzj-21",
    "smtp": "LtTv1nw5aFLaXrCluBzj-14",
    "qliksense": "LtTv1nw5aFLaXrCluBzj-17",
    "directum ario": "LtTv1nw5aFLaXrCluBzj-58",
    "darcy": "LtTv1nw5aFLaXrCluBzj-62",
    "techlog": "LtTv1nw5aFLaXrCluBzj-62",
    "pg-backup vm": "LtTv1nw5aFLaXrCluBzj-101",
    "модули abai": "LtTv1nw5aFLaXrCluBzj-62",
    "abaiprot": "LtTv1nw5aFLaXrCluBzj-101",
    "ijanet": "LtTv1nw5aFLaXrCluBzj-46",
    "power bi": "LtTv1nw5aFLaXrCluBzj-57",
    "asr": "LtTv1nw5aFLaXrCluBzj-59",
    "прокторинг": "LtTv1nw5aFLaXrCluBzj-50",
}


def resolve_id(name: str, index: dict[str, list[str]]) -> str | None:
    k = flow_key(name)
    if k in FALLBACK_VERTEX:
        return FALLBACK_VERTEX[k]
    if k in index and index[k]:
        return index[k][0]
    # substring search
    for label, ids in index.items():
        if k in label or label in k:
            return ids[0]
    for token in k.split():
        if len(token) >= 4 and token in index:
            return index[token][0]
    if k in FALLBACK_VERTEX:
        return FALLBACK_VERTEX[k]
    return None


def add_edges(model_xml: str, flows: list[tuple], dry_run: bool = False) -> tuple[str, int, int]:
    root = ET.fromstring(model_xml if model_xml.strip().startswith("<") else f"<wrap>{model_xml}</wrap>")
    if root.tag == "wrap":
        model_root = root.find("mxGraphModel")
        if model_root is None:
            model_root = root[0]
    else:
        model_root = root if root.tag == "mxGraphModel" else root.find("mxGraphModel")

    if model_root is None:
        raise ValueError("mxGraphModel not found")

    # find root layer parent id (usually "1")
    parent_id = "1"
    for cell in model_root.iter("mxCell"):
        if cell.get("id") == "1":
            parent_id = "1"
            break

    index = build_vertex_index(model_root)
    existing = set()
    for cell in model_root.iter("mxCell"):
        if cell.get("edge") == "1":
            existing.add((cell.get("source"), cell.get("target"), (cell.get("value") or "")))

    added = 0
    skipped = 0
    edge_id = 90000
    for src_name, tgt_name, lbl, _grp in flows:
        sid = resolve_id(src_name, index)
        tid = resolve_id(tgt_name, index)
        if not sid or not tid:
            skipped += 1
            continue
        if (sid, tid, lbl) in existing:
            continue
        edge_id += 1
        eid = f"edge_{edge_id}"
        edge = ET.Element(
            "mxCell",
            {
                "id": eid,
                "value": lbl,
                "style": (
                    "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;"
                    "jettySize=auto;html=1;fontSize=9;strokeColor=#1565C0;"
                    "strokeWidth=1;endArrow=block;endFill=1;"
                ),
                "edge": "1",
                "parent": parent_id,
                "source": sid,
                "target": tid,
            },
        )
        ET.SubElement(edge, "mxGeometry", {"relative": "1", "as": "geometry"})
        # append to root's children - find <root> element
        for r in model_root.findall("root"):
            r.append(edge)
            break
        else:
            model_root.append(edge)
        existing.add((sid, tid, lbl))
        added += 1

    out = ET.tostring(model_root, encoding="unicode")
    return out, added, skipped


def decode_url_fragment(fragment: str) -> ET.Element:
    fragment = fragment.strip()
    if fragment.startswith("#R"):
        fragment = fragment[2:]
    if fragment.startswith("http"):
        fragment = fragment.split("#R", 1)[-1]
    if fragment.startswith("%3C") or fragment.startswith("%3c"):
        fragment = urllib.parse.unquote(fragment)
    elif "%3Cmxfile" in fragment[:20] or "%3cmxfile" in fragment[:20].lower():
        fragment = urllib.parse.unquote(fragment)
    if not fragment.startswith("<"):
        fragment = "<mxfile>" + fragment + "</mxfile>"
    return ET.fromstring(fragment)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?", help="Input .drawio file")
    ap.add_argument("-o", "--output", help="Output .drawio file")
    ap.add_argument("--url-fragment", help="File with viewer URL or #R fragment")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.url_fragment:
        frag = Path(args.url_fragment).read_text(encoding="utf-8")
        root = decode_url_fragment(frag)
        diagram = root.find("diagram")
        did = diagram.get("id", "page1")
        dname = diagram.get("name", "ИТ Ландшафт КМГ")
        model_xml = get_model_xml(root)
    elif args.input:
        path = Path(args.input)
        root, did, dname = load_drawio(path)
        model_xml = get_model_xml(root)
    else:
        ap.error("Provide input.drawio or --url-fragment")

    new_model, added, skipped = add_edges(model_xml, ALL_FLOWS, args.dry_run)
    print(f"Edges added: {added}, skipped (no matching node): {skipped}")

    if args.dry_run:
        return

    out_path = Path(args.output or args.input or "ИТ Ландшафт КМГ.drawio")
    set_model_xml(root, new_model, did, dname)
    # rebuild mxfile wrapper
    if root.tag != "mxfile":
        mxfile = ET.Element(
            "mxfile",
            {
                "host": "app.diagrams.net",
                "agent": "merge_drawio_edges",
                "version": "22.1.0",
                "type": "device",
            },
        )
        for child in root:
            mxfile.append(child)
        root = mxfile

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(out_path, encoding="utf-8", xml_declaration=True)
    print(f"Written: {out_path}")


if __name__ == "__main__":
    main()
