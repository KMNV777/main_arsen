#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert Mermaid (.mmd) diagrams to editable draw.io (.drawio) files."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from drawpyo import File, Page
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


def parse_mermaid(text: str) -> Tuple[List[dict], Dict[str, str], List[Tuple[str, str, str]], str]:
    """Return subgraphs, nodes{id:label}, edges, direction."""
    direction = "TB"
    subgraphs: List[dict] = []
    nodes: Dict[str, str] = {}
    edges: List[Tuple[str, str, str]] = []
    current_sg: Optional[str] = None
    node_to_sg: Dict[str, str] = {}

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
            current_sg = m.group(1)
            subgraphs.append({"id": m.group(1), "label": m.group(2), "nodes": []})
            continue
        if re.match(r"direction\s+(TB|LR|BT|RL)", line, re.I):
            continue
        if line == "end":
            current_sg = None
            continue

        m = re.match(r'(\w+)\s*\[\("([^"]+)"\)\]', line)
        if m:
            nid, label = m.group(1), m.group(2)
            nodes[nid] = label
            if current_sg:
                node_to_sg[nid] = current_sg
                subgraphs[-1]["nodes"].append(nid)
            continue

        m = re.match(r'(\w+)\s*\["([^"]+)"\]', line)
        if m:
            nid, label = m.group(1), m.group(2).replace("<br/>", "\n").replace("<br>", "\n")
            nodes[nid] = label
            if current_sg:
                node_to_sg[nid] = current_sg
                subgraphs[-1]["nodes"].append(nid)
            continue

        m = re.match(
            r'(\w+)\s*(-->|<-->|-\.->)\s*(?:\|"?([^"|]+)"?\|\s*)?(\w+)',
            line,
        )
        if m:
            edges.append((m.group(1), m.group(4), m.group(2)))
            continue

        m = re.match(r"(\w+)\s*&\s*(\w+)", line)
        if m and "-->" not in line and "<-->" not in line:
            continue

    # nodes only in edges
    for a, b, _ in edges:
        for nid in (a, b):
            if nid not in nodes:
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
    edges: List[Tuple[str, str, str]],
    direction: str,
    page_w: int = 2400,
    page_h: int = 1800,
) -> File:
    f = File(file_name=f"{title}.drawio", file_path=str(OUT_DIR))
    page = Page(file=f, name=title, width=page_w, height=page_h)

    obj_map: Dict[str, Object] = {}
    containers: Dict[str, Object] = {}

    margin_x, margin_y = 40, 40
    sg_w = page_w - 80
    col_w, row_h, node_w, node_h = 200, 90, 180, 56
    cols = max(3, min(6, sg_w // col_w))

    y_cursor = margin_y

    if subgraphs:
        for sg in subgraphs:
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
        for sg in subgraphs:
            placed.update(sg["nodes"])
        orphan = [n for n in nodes if n not in placed]
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

    for src, tgt, kind in edges:
        if src not in obj_map or tgt not in obj_map:
            continue
        pattern = "dashed_medium" if kind == "-.->" else "solid"
        edge = Edge(
            source=obj_map[src],
            target=obj_map[tgt],
            page=page,
            pattern=pattern,
        )
        if kind == "<-->":
            edge = Edge(
                source=obj_map[tgt],
                target=obj_map[src],
                page=page,
                pattern=pattern,
            )
            page.add_object(edge)
        page.add_object(edge)

    return f


def build_it_landscape_drawio() -> File:
    """Layered IT landscape (matches 06-it-landscape-general.svg)."""
    f = File(file_name="06-it-landscape-general.drawio", file_path=str(OUT_DIR))
    page = Page(file=f, name="ИТ-ландшафт ЭМГ", width=1520, height=1280)

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
                dx += dw + 8
        else:
            nx = 40
            for it in items:
                cat = "emg" if "Эмбамунайгаз" in it or it == "ИС ABAI" else "default"
                if "SAP" in it or "Directory" in it or "Шина" in it:
                    cat = "hub"
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
                nx += 180

        y += height + 16

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
    for mmd in sorted(mmd_dir.glob("*.mmd")):
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
