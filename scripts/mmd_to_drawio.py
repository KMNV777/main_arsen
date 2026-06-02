#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert Mermaid (.mmd) diagrams to editable draw.io (.drawio) files."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from drawpyo import File, Page

from drawio_export import configure_drawio_file
from drawpyo.diagram.edges import Edge
from drawpyo.diagram.objects import Object

# draw.io fill/stroke for node categories
STYLES = {
    "emg": ("#d5e8d4", "#82b366"),
    "hub": ("#dae8fc", "#6c8ebf"),
    "ot": ("#fff2cc", "#d6b656"),
    "sec": ("#f8cecc", "#b85450"),
    "retired": ("#f5f5f5", "#999999"),
    "default": ("#ffffff", "#666666"),
}

NODE_STYLES = {
    "emg": {"fillColor": "#d5e8d4", "strokeColor": "#82b366"},
    "hub": {"fillColor": "#dae8fc", "strokeColor": "#6c8ebf"},
    "ot": {"fillColor": "#fff2cc", "strokeColor": "#d6b656"},
    "sec": {"fillColor": "#f8cecc", "strokeColor": "#b85450"},
}

CONTAINER_STYLE = (
    "swimlane;fontStyle=1;childLayout=stackLayout;horizontal=1;startSize=28;"
    "horizontalStack=0;resizeParent=1;collapsible=0;whiteSpace=wrap;html=1;"
    "fillColor=#f5f5f5;strokeColor=#666666;align=left;spacingLeft=8;"
)


EdgeSpec = Tuple[str, str, str, str]

EDGE_PATTERN = re.compile(r"\s*(<-->|-->|-\.->)\s*(?:\|([^|]*)\|\s*)?")
INLINE_NODE_PATTERNS = (
    re.compile(r'(\w+)\s*\[\("([^"]+)"\)\]'),
    re.compile(r'(\w+)\s*\["([^"]+)"\]'),
)


def clean_label(label: str) -> str:
    return label.replace("<br/>", "\n").replace("<br>", "\n").strip()


def extract_inline_nodes(line: str, nodes: Dict[str, str]) -> Tuple[str, List[str]]:
    declared: List[str] = []

    def remember(match: re.Match) -> str:
        nid, label = match.group(1), clean_label(match.group(2))
        nodes[nid] = label
        declared.append(nid)
        return nid

    for pattern in INLINE_NODE_PATTERNS:
        line = pattern.sub(remember, line)
    return line, declared


def endpoint_ids(expr: str) -> List[str]:
    ids: List[str] = []
    for part in expr.split("&"):
        part = part.strip()
        if re.fullmatch(r"[A-Za-z_]\w*", part):
            ids.append(part)
        else:
            ids.extend(re.findall(r"[A-Za-z_]\w*", part))
    return ids


def parse_edge_line(line: str) -> List[EdgeSpec]:
    parts: List[str] = []
    arrows: List[Tuple[str, str]] = []
    pos = 0

    for match in EDGE_PATTERN.finditer(line):
        parts.append(line[pos : match.start()].strip())
        arrows.append((match.group(1), clean_label(match.group(2) or "")))
        pos = match.end()
    if not arrows:
        return []

    parts.append(line[pos:].strip())
    if len(parts) != len(arrows) + 1:
        return []

    edges: List[EdgeSpec] = []
    for index, (kind, label) in enumerate(arrows):
        for src in endpoint_ids(parts[index]):
            for tgt in endpoint_ids(parts[index + 1]):
                if src != tgt:
                    edges.append((src, tgt, kind, label))
    return edges


def parse_mermaid(text: str) -> Tuple[List[dict], Dict[str, str], List[EdgeSpec], str]:
    """Return subgraphs, nodes{id:label}, edges, direction."""
    direction = "TB"
    subgraphs: List[dict] = []
    nodes: Dict[str, str] = {}
    edges: List[EdgeSpec] = []
    sg_stack: List[str] = []

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("%%"):
            continue
        if line.startswith("flowchart "):
            direction = line.split()[-1].upper()
            continue
        if line.startswith("classDef") or line.startswith("class "):
            continue

        m = re.match(r'subgraph\s+(\w+)\s*\["([^"]+)"\]', line)
        if m:
            parent = sg_stack[-1] if sg_stack else None
            sg_stack.append(m.group(1))
            subgraphs.append({"id": m.group(1), "label": m.group(2), "parent": parent, "nodes": []})
            continue
        if re.match(r"direction\s+(TB|LR|BT|RL)", line, re.I):
            continue
        if line == "end":
            if sg_stack:
                sg_stack.pop()
            continue

        line, declared_nodes = extract_inline_nodes(line, nodes)
        if declared_nodes and sg_stack:
            current_sg = next(sg for sg in reversed(subgraphs) if sg["id"] == sg_stack[-1])
            for nid in declared_nodes:
                if nid not in current_sg["nodes"]:
                    current_sg["nodes"].append(nid)
        if declared_nodes and re.fullmatch(r"[A-Za-z_]\w*", line):
            continue

        parsed_edges = parse_edge_line(line)
        if parsed_edges:
            edges.extend(parsed_edges)
            continue

        m = re.match(r"(\w+)\s*&\s*(\w+)", line)
        if m and "-->" not in line and "<-->" not in line:
            continue

    subgraph_ids = {sg["id"] for sg in subgraphs}
    for a, b, _, _ in edges:
        for nid in (a, b):
            if nid not in nodes and nid not in subgraph_ids:
                nodes[nid] = nid

    return subgraphs, nodes, edges, direction

def node_category(nid: str, label: str) -> str:
    key = (nid + " " + label).upper()
    if any(x in key for x in ("ABAI", "ИМ", "UTOEMG", "ASDC", "ЭМГ", "CMV2")):
        return "emg"
    if any(x in key for x in ("SAP", "AD", "DIRECTORY", "ШИНА", "КХД", "АСУНСИ")):
        return "hub"
    if any(x in key for x in ("OPC", "MODBUS", "MYSQL", "POSTGRES", "ANALYTIC", "CRON", "ETL", "SDMO", "SCADA")):
        return "ot"
    if any(x in key for x in ("DLP", "FUDO", "EXCHANGE", "FORCEPOINT", "SOLAR", "PAM")):
        return "sec"
    return "default"


def build_diagram(
    title: str,
    subgraphs: List[dict],
    nodes: Dict[str, str],
    edges: List[EdgeSpec],
    direction: str,
    page_w: int = 2400,
    page_h: int = 1800,
) -> File:
    f = configure_drawio_file(File(file_name=f"{title}.drawio", file_path=str(OUT_DIR)))
    page = Page(file=f, name=title, width=page_w, height=page_h)

    obj_map: Dict[str, Object] = {}
    containers: Dict[str, Object] = {}

    margin_x, margin_y = 40, 40
    sg_w = page_w - 80
    col_w, row_h, node_w, node_h = 200, 90, 180, 56
    cols = max(3, min(6, sg_w // col_w))

    y_cursor = margin_y

    visible_subgraphs = [sg for sg in subgraphs if sg["nodes"]]

    if visible_subgraphs:
        for sg in visible_subgraphs:
            sg_nodes = [n for n in sg["nodes"] if n in nodes]
            if not sg_nodes:
                sg_nodes = []
            rows = max(1, (len(sg_nodes) + cols - 1) // cols)
            box_h = 40 + rows * row_h + 20

            container = Object(
                value=sg["label"],
                position=(margin_x, y_cursor),
                width=sg_w,
                height=box_h,
                baseStyle=CONTAINER_STYLE,
            )
            page.add_object(container)
            containers[sg["id"]] = container
            obj_map[sg["id"]] = container

            for i, nid in enumerate(sg_nodes):
                col = i % cols
                row = i // cols
                x = margin_x + 20 + col * col_w
                y = y_cursor + 50 + row * row_h
                cat = node_category(nid, nodes[nid])
                style = NODE_STYLES.get(cat, {})
                obj = Object(
                    value=nodes[nid],
                    position=(x, y),
                    width=node_w,
                    height=node_h,
                    parent=container,
                    fillColor=style.get("fillColor"),
                    strokeColor=style.get("strokeColor"),
                    rounded=1,
                )
                page.add_object(obj)
                obj_map[nid] = obj

            y_cursor += box_h + 30

        placed = set()
        for sg in visible_subgraphs:
            placed.update(sg["nodes"])
        subgraph_ids = {sg["id"] for sg in subgraphs}
        orphan = [n for n in nodes if n not in placed and n not in subgraph_ids]
        if orphan:
            rows = max(1, (len(orphan) + cols - 1) // cols)
            box_h = 40 + rows * row_h + 20
            container = Object(
                value="Прочие",
                position=(margin_x, y_cursor),
                width=sg_w,
                height=box_h,
                baseStyle=CONTAINER_STYLE,
            )
            page.add_object(container)
            for i, nid in enumerate(orphan):
                col = i % cols
                row = i // cols
                obj = Object(
                    value=nodes[nid],
                    position=(margin_x + 20 + col * col_w, y_cursor + 50 + row * row_h),
                    width=node_w,
                    height=node_h,
                    parent=container,
                    rounded=1,
                )
                page.add_object(obj)
                obj_map[nid] = obj
    else:
        # flat layout (hub diagrams)
        items = list(nodes.items())
        if direction == "LR":
            cx, cy = margin_x, margin_y + 200
            for i, (nid, label) in enumerate(items):
                obj = Object(
                    value=label,
                    position=(cx + i * 220, cy),
                    width=node_w,
                    height=node_h,
                    rounded=1,
                    **NODE_STYLES.get(node_category(nid, label), {}),
                )
                page.add_object(obj)
                obj_map[nid] = obj
        else:
            cols = min(4, max(2, int(len(items) ** 0.5) + 1))
            for i, (nid, label) in enumerate(items):
                col = i % cols
                row = i // cols
                obj = Object(
                    value=label,
                    position=(margin_x + col * col_w, margin_y + row * row_h),
                    width=node_w,
                    height=node_h,
                    rounded=1,
                    **NODE_STYLES.get(node_category(nid, label), {}),
                )
                page.add_object(obj)
                obj_map[nid] = obj

    for src, tgt, kind, label in edges:
        if src not in obj_map or tgt not in obj_map:
            continue
        pattern = "dashed_medium" if kind == "-.->" else "solid"
        edge = Edge(
            source=obj_map[src],
            target=obj_map[tgt],
            page=page,
            pattern=pattern,
            label=label,
        )
        if kind == "<-->":
            edge = Edge(
                source=obj_map[tgt],
                target=obj_map[src],
                page=page,
                pattern=pattern,
                label=label,
            )
            page.add_object(edge)
        page.add_object(edge)

    return f


def build_it_landscape_drawio() -> File:
    """Layered IT landscape (matches 06-it-landscape-general.svg)."""
    f = configure_drawio_file(File(file_name="06-it-landscape-general.drawio", file_path=str(OUT_DIR)))
    page = Page(file=f, name="ИТ-ландшафт ЭМГ", width=1520, height=1280)
    obj_map: Dict[str, Object] = {}

    layers = [
        ("L0 · Организация", 108, ["КЦ КМГ", "АО «Эмбамунайгаз»", "КМГИ"], "#f5f5f5", None),
        ("L1 · Порталы", 118, ["Team", "Интранет", "ИСУП", "Compliance", "BoardMaps"], "#f5f5f5", None),
        (
            "L2 · Бизнес-приложения",
            520,
            [],
            "#ffffff",
            [
                ("Производство", ["№3 ИС ABAI", "№19 ИМ", "АСДЦ", "sPoint", "SCADA"], "emg"),
                ("Транспорт", ["ИС УТО ЭМГ", "№13 ИС УТО", "№7 Argus Pro"], "emg"),
                ("Финансы", ["№18 SAP ERP", "№9 SAS-FM", "№8 1С", "№17 AVR+SAP", "FC · БВУ"], "hub"),
                ("Закупки", ["Procu/Price", "СДД", "ИСЭЗ"], "default"),
                ("Документы", ["№2 Directum", "№14 Alfresco", "ЭА"], "default"),
                ("Кадры / HSE", ["№12 Упр. персоналом", "№6 E-Pass", "№10 Жулдыз", "ИСОТ/ЭНД"], "default"),
                ("ГИС", ["№15 КГИС", "БДА"], "default"),
            ],
        ),
        (
            "L3 · Платформа и интеграция",
            118,
            ["Active Directory", "Шина интеграций", "АСУНСИ", "КХД КМГ", "ИС ЭСФ", "Platts", "Нацбанк"],
            "#e3f2fd",
            None,
        ),
        (
            "L4 · OT-контур (№19)",
            118,
            ["№19 ИМ cmv2", "OPC DA/UA · Modbus", "PostgreSQL/MySQL", "Аналитика ЭМГ", "ИСУН · АСУТП · КОА"],
            "#fff8e1",
            None,
        ),
        ("L5 · ИБ", 88, ["Solar Dozor", "FUDOPAM", "Forcepoint", "Exchange"], "#ffebee", None),
    ]

    y = 30
    for layer_def in layers:
        title, height, items, bg, domains = layer_def
        container = Object(
            value=title,
            position=(24, y),
            width=1472,
            height=height,
            baseStyle=CONTAINER_STYLE.replace("fillColor=#f5f5f5", f"fillColor={bg}"),
        )
        page.add_object(container)

        if domains:
            dx = 40
            dw = 200
            for name, dom_items, cat in domains:
                sub = Object(
                    value=name,
                    position=(dx, y + 36),
                    width=dw,
                    height=height - 50,
                    baseStyle="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#999999;verticalAlign=top;fontStyle=1;",
                    parent=container,
                )
                page.add_object(sub)
                sty = NODE_STYLES.get(cat, {})
                for j, it in enumerate(dom_items):
                    o = Object(
                        value=it,
                        position=(dx + 8, y + 58 + j * 32),
                        width=dw - 16,
                        height=28,
                        parent=sub,
                        rounded=1,
                        fillColor=sty.get("fillColor", "#ffffff"),
                        strokeColor=sty.get("strokeColor", "#666666"),
                    )
                    page.add_object(o)
                    obj_map[it] = o
                dx += dw + 8
        else:
            nx = 40
            for it in items:
                cat = "emg" if "Эмбамунайгаз" in it or it == "ИС ABAI" else "default"
                if "SAP" in it or "Directory" in it or "Шина" in it:
                    cat = "hub"
                if any(sec in it for sec in ("Solar", "FUDOPAM", "Forcepoint", "Exchange")):
                    cat = "sec"
                if any(ot in it for ot in ("OPC", "PostgreSQL", "Аналитика", "ИСУН")):
                    cat = "ot"
                sty = NODE_STYLES.get(cat, {})
                o = Object(
                    value=it,
                    position=(nx, y + 44),
                    width=160,
                    height=40,
                    parent=container,
                    rounded=1,
                    fillColor=sty.get("fillColor"),
                    strokeColor=sty.get("strokeColor"),
                )
                page.add_object(o)
                obj_map[it] = o
                nx += 180

        y += height + 16

    def add_edge(src: str, tgt: str, label: str = "", kind: str = "-->") -> None:
        if src not in obj_map or tgt not in obj_map:
            return
        pattern = "dashed_medium" if kind == "-.->" else "solid"
        edge = Edge(source=obj_map[src], target=obj_map[tgt], page=page, pattern=pattern, label=label)
        page.add_object(edge)
        if kind == "<-->":
            reverse = Edge(source=obj_map[tgt], target=obj_map[src], page=page, pattern=pattern, label=label)
            page.add_object(reverse)

    landscape_edges = [
        ("АО «Эмбамунайгаз»", "№3 ИС ABAI", "цифровой контур", "-->"),
        ("АО «Эмбамунайгаз»", "№19 ИМ", "промыслы", "-->"),
        ("№3 ИС ABAI", "№19 ИМ", "SQL", "-->"),
        ("№19 ИМ", "№19 ИМ cmv2", "OT-хаб", "-->"),
        ("№19 ИМ cmv2", "OPC DA/UA · Modbus", "OPC/Modbus", "-->"),
        ("№19 ИМ cmv2", "PostgreSQL/MySQL", "SQL", "-->"),
        ("№19 ИМ cmv2", "Аналитика ЭМГ", "API", "-->"),
        ("№19 ИМ cmv2", "ИСУН · АСУТП · КОА", "polling", "-->"),
        ("ИС УТО ЭМГ", "№13 ИС УТО", "операции", "-->"),
        ("№7 Argus Pro", "№13 ИС УТО", "REST", "-->"),
        ("№13 ИС УТО", "№18 SAP ERP", "SOAP XML", "<-->"),
        ("№18 SAP ERP", "Шина интеграций", "SAP PO/API", "<-->"),
        ("№18 SAP ERP", "АСУНСИ", "НСИ", "<-->"),
        ("№9 SAS-FM", "№18 SAP ERP", "RFC/CSV", "-->"),
        ("№8 1С", "№18 SAP ERP", "CSV", "-->"),
        ("№17 AVR+SAP", "№18 SAP ERP", "API XML", "<-->"),
        ("FC · БВУ", "№18 SAP ERP", "MT940/API", "-->"),
        ("Procu/Price", "АСУНСИ", "API JSON", "<-->"),
        ("Procu/Price", "ИСЭЗ", "закупки", "-->"),
        ("sPoint", "КХД КМГ", "API JSON", "-->"),
        ("№2 Directum", "Active Directory", "LDAP", "-->"),
        ("№14 Alfresco", "Active Directory", "LDAP", "-->"),
        ("№6 E-Pass", "Active Directory", "LDAP", "-->"),
        ("№10 Жулдыз", "Active Directory", "LDAP", "-->"),
        ("№15 КГИС", "Active Directory", "LDAP", "-->"),
        ("Procu/Price", "Active Directory", "LDAP", "-->"),
        ("FUDOPAM", "Active Directory", "LDAP", "-->"),
        ("Exchange", "Solar Dozor", "BCC", "-->"),
        ("Forcepoint", "Solar Dozor", "ICAP", "-->"),
    ]
    for src, tgt, label, kind in landscape_edges:
        add_edge(src, tgt, label, kind)

    return f


def convert_mmd(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    subgraphs, nodes, edges, direction = parse_mermaid(text)
    title = path.stem
    page_h = 1200 + len(subgraphs) * 220
    f = build_diagram(title, subgraphs, nodes, edges, direction, page_h=page_h)
    return f.write(overwrite=True)


def main() -> None:
    global OUT_DIR
    OUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "drawio"
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    mmd_dir = Path(__file__).resolve().parents[1] / "docs" / "svg"
    # Эти .mmd — справочные; .drawio собираются отдельными генераторами
    skip_mmd = {"08-kmg-emg-corporate-networks.mmd"}
    for mmd in sorted(mmd_dir.glob("*.mmd")):
        if mmd.name in skip_mmd:
            print(f"SKIP {mmd.name} (use scripts/build_kmg_emg_network_diagram.py)")
            continue
        out = convert_mmd(mmd)
        print(f"OK {mmd.name} -> {out}")

    landscape_path = build_it_landscape_drawio().write(overwrite=True)
    print(f"OK 06-it-landscape-general -> {landscape_path}")

    # Duplicate for docs/it-landscape-emg-general.svg companion
    general = build_it_landscape_drawio()
    general.file_name = "it-landscape-emg-general.drawio"
    general_path = general.write(overwrite=True)
    print(f"OK it-landscape-emg-general -> {general_path}")

    detailed_mmd = Path(__file__).resolve().parents[1] / "docs" / "it-landscape-emg.mmd"
    if detailed_mmd.exists():
        text = detailed_mmd.read_text(encoding="utf-8")
        subgraphs, nodes, edges, direction = parse_mermaid(text)
        f = build_diagram(
            "07-it-landscape-mermaid-detailed",
            subgraphs,
            nodes,
            edges,
            direction,
            page_w=2800,
            page_h=2400,
        )
        detailed_path = f.write(overwrite=True)
        print(f"OK {detailed_mmd.name} -> {detailed_path}")


if __name__ == "__main__":
    main()
