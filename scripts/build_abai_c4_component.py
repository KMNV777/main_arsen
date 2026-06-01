#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the C4 Component diagram for the ABAI information system (ИС ABAI).

Source data: текущая ИТ-архитектура ИС «ABAI» (KMGE), диаграмма взаимодействия
IT-ландшафта (рис. 4.2.2). Стиль повторяет пример C4-диаграммы Nedra Digital Twin:
контейнеры-хосты с инфраструктурой (IP), узлы «component», связи с протоколами и
портами, контурные зоны и легенда.

Запуск:
    pip install -r requirements.txt
    python3 scripts/build_abai_c4_component.py
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, List, Tuple

from drawpyo import File, Page
from drawpyo.diagram.edges import Edge
from drawpyo.diagram.objects import Object

OUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "drawio"
SVG_DIR = Path(__file__).resolve().parents[1] / "docs" / "svg"

# ---------------------------------------------------------------------------
# Геометрия
# ---------------------------------------------------------------------------
COMP_W, COMP_H = 170, 64
GAP_X, GAP_Y = 20, 26
PAD_SIDE, PAD_TOP, PAD_BOT = 20, 50, 20

# ---------------------------------------------------------------------------
# Стили
# ---------------------------------------------------------------------------
PERSON_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#08427B;strokeColor=#073B6F;"
    "fontColor=#ffffff;fontStyle=1;verticalAlign=middle;align=center;"
)

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

# Цвета узлов «component» по слою C4
COMP_PALETTE = {
    "web": ("#DAE8FC", "#6C8EBF"),   # презентация / веб
    "app": ("#D5E8D4", "#82B366"),   # приложение / бизнес-логика
    "data": ("#FFF2CC", "#D6B656"),  # платформа данных / обработка
    "db": ("#FFE6CC", "#D79B00"),    # хранилища / БД
    "tool": ("#F5F5F5", "#999999"),  # DevOps / инструменты
    "obs": ("#E1D5E7", "#9673A6"),   # наблюдаемость / аудит
}


def make_obj(**kwargs) -> Object:
    """Create an Object whose style is exactly its ``baseStyle``.

    drawpyo otherwise appends template defaults (``rounded=0;dashed=0``) that
    would override the dashed zones and rounded containers defined in baseStyle.
    """
    obj = Object(**kwargs)
    obj.style_attributes = []
    return obj


def comp_style(kind: str) -> str:
    fill, stroke = COMP_PALETTE.get(kind, COMP_PALETTE["app"])
    return (
        f"shape=module;jettyWidth=14;jettyHeight=6;whiteSpace=wrap;html=1;"
        f"fillColor={fill};strokeColor={stroke};fontSize=11;verticalAlign=middle;"
        f"align=center;spacingLeft=6;spacingRight=4;"
    )


def container_dims(n_comps: int, cols: int, comp_w: int = COMP_W) -> Tuple[int, int]:
    rows = max(1, math.ceil(n_comps / cols))
    w = PAD_SIDE * 2 + cols * comp_w + (cols - 1) * GAP_X
    h = PAD_TOP + rows * COMP_H + (rows - 1) * GAP_Y + PAD_BOT
    return w, h


class Diagram:
    def __init__(self, page: Page) -> None:
        self.page = page

    def zone(self, title: str, x: int, y: int, w: int, h: int) -> Object:
        obj = make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=ZONE_STYLE)
        self.page.add_object(obj)
        return obj

    def container(
        self,
        title: str,
        x: int,
        y: int,
        comps: List[Tuple[str, str]],
        cols: int,
        comp_w: int = COMP_W,
    ) -> Tuple[Object, Dict[str, Object], Tuple[int, int, int, int]]:
        w, h = container_dims(len(comps), cols, comp_w)
        box = make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=CONTAINER_STYLE)
        self.page.add_object(box)

        objs: Dict[str, Object] = {}
        for i, (label, kind) in enumerate(comps):
            col = i % cols
            row = i // cols
            cx = x + PAD_SIDE + col * (comp_w + GAP_X)
            cy = y + PAD_TOP + row * (COMP_H + GAP_Y)
            node = make_obj(
                value=f"«component»\n{label}",
                position=(cx, cy),
                width=comp_w,
                height=COMP_H,
                baseStyle=comp_style(kind),
            )
            self.page.add_object(node)
            objs[label] = node
        return box, objs, (x, y, w, h)

    def person(self, title: str, x: int, y: int, w: int = 220, h: int = 80) -> Object:
        obj = make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=PERSON_STYLE)
        self.page.add_object(obj)
        return obj

    def edge(self, src: Object, tgt: Object, label: str = "", dashed: bool = False) -> None:
        e = Edge(
            source=src,
            target=tgt,
            page=self.page,
            label=label,
            pattern="dashed_medium" if dashed else "solid",
        )
        self.page.add_object(e)


def build() -> File:
    f = File(file_name="08-abai-c4-component.drawio", file_path=str(OUT_DIR))
    page = Page(file=f, name="C4 Component — ИС ABAI", width=1780, height=1560)
    d = Diagram(page)

    # --- Зоны (фон) ----------------------------------------------------------
    d.zone("Прикладной контур ИС ABAI · Intranet / VPN DMZ (HTTPS)", 40, 150, 1280, 380)
    d.zone(
        "Платформа данных и обработки · Hadoop / Spark / Kafka / Airflow / БД / MinIO",
        40,
        548,
        1280,
        780,
    )
    d.zone("DevOps, наблюдаемость и инструменты", 1340, 150, 320, 1178)

    # --- Пользователь --------------------------------------------------------
    person = d.person("Пользователь ЭМГ\n(браузер / АРМ)", 70, 40)

    # --- Веб-приложение ------------------------------------------------------
    _, web, _ = d.container(
        "Веб-приложение ИС ABAI · 172.20.103.77\nNginx, Node.js",
        70,
        200,
        [
            ("Nginx\n(веб-сервер)", "web"),
            ("Node.js", "web"),
            ("Frontend\nVue.js · Leaflet.js · plotly", "web"),
            ("Формы ввода\nLaravel PHP", "web"),
            ("MySQL\n(локальная БД)", "db"),
        ],
        cols=2,
    )

    # --- Backend ИС ABAI -----------------------------------------------------
    _, be, _ = d.container(
        "ИС ABAI · Backend · 172.20.103.203\nMVC — Laravel / Django · PHP / Python",
        700,
        200,
        [
            ("View", "app"),
            ("Controller", "app"),
            ("Model", "app"),
            ("ORM", "app"),
            ("DB Connector", "app"),
        ],
        cols=3,
    )

    # --- Apache Airflow ------------------------------------------------------
    _, af, _ = d.container(
        "Apache Airflow · ETL · 172.20.102.82\nпланировщик и оркестрация",
        70,
        600,
        [
            ("Web server", "data"),
            ("Scheduler\n(DAG)", "data"),
            ("Worker", "data"),
            ("Broker", "data"),
            ("Metadata DB", "db"),
        ],
        cols=3,
    )

    # --- Apache Kafka --------------------------------------------------------
    _, kf, _ = d.container(
        "Apache Kafka cluster · 172.20.102.45\nброкер сообщений",
        700,
        600,
        [
            ("Kafka Broker", "data"),
            ("ZooKeeper", "data"),
            ("Streams Messaging\nManager · 10.82.1.31", "data"),
            ("Producer", "data"),
            ("Consumer", "data"),
        ],
        cols=3,
    )

    # --- Apache Spark / Livy -------------------------------------------------
    _, sp, _ = d.container(
        "Apache Spark / Livy · 10.82.1.12\nML · Computer Vision (Nvidia CUDA)",
        70,
        840,
        [
            ("Apache Spark", "data"),
            ("Apache Livy", "data"),
            ("Spark Job\n(Scala)", "data"),
            ("Spark Job\n(Python)", "data"),
            ("Spark Job\n(SQL)", "data"),
        ],
        cols=3,
    )

    # --- Hadoop --------------------------------------------------------------
    _, hd, _ = d.container(
        "Hadoop кластер · распределённая обработка\nCloudera",
        700,
        840,
        [
            ("NameNode · YARN\n10.82.1.1", "data"),
            ("DataNode 1\nMapReduce / Spark", "data"),
            ("DataNode 2\nMapReduce / Spark", "data"),
            ("DataNode 3\nMapReduce / Spark", "data"),
            ("Cloudera Manager\n10.82.1.2", "data"),
        ],
        cols=3,
    )

    # --- Базы данных ---------------------------------------------------------
    _, db, _ = d.container(
        "Базы данных",
        70,
        1080,
        [
            ("OLTP PostgreSQL\n10.82.1.28", "db"),
            ("OLTP PostgreSQL\nmaster/slave · 10.82.1.29", "db"),
            ("OLAP Druid\n10.82.1.20", "db"),
        ],
        cols=3,
    )

    # --- MinIO ---------------------------------------------------------------
    _, mn, _ = d.container(
        "MinIO Object Storage (S3) · 172.20.102.54",
        700,
        1080,
        [
            ("MinIO Console", "db"),
            ("S3 Node 1\n10.82.2.36", "db"),
            ("S3 Node 2\n10.82.2.37", "db"),
            ("S3 Node 3\n10.82.2.38", "db"),
            ("S3 Node 4\n10.82.2.39", "db"),
        ],
        cols=3,
    )

    # --- ELK -----------------------------------------------------------------
    _, elk, _ = d.container(
        "Аудит и журналирование (ELK)",
        1360,
        200,
        [
            ("Logstash", "obs"),
            ("Elasticsearch", "obs"),
            ("Kibana", "obs"),
        ],
        cols=1,
        comp_w=230,
    )

    # --- DevOps / качество кода ----------------------------------------------
    _, dev, _ = d.container(
        "DevOps · качество кода",
        1360,
        560,
        [
            ("GitLab · полирепозиторий\nDEV 172.20.103.31", "tool"),
            ("SonarQube CE\n10.82.4.29", "tool"),
            ("Dependency-Track\n10.82.4.30", "tool"),
            ("Sentry\n10.82.4.65", "tool"),
            ("Docker\n172.20.102.23", "tool"),
        ],
        cols=1,
        comp_w=230,
    )

    # --- Управление проектом / визуализация ----------------------------------
    _, pm, _ = d.container(
        "Управление проектом · визуализация",
        1360,
        1080,
        [
            ("YouTrack", "tool"),
            ("SuperSET", "obs"),
        ],
        cols=1,
        comp_w=230,
    )

    # --- Связи ---------------------------------------------------------------
    d.edge(person, web["Nginx\n(веб-сервер)"], "HTTPS:443")
    d.edge(web["Frontend\nVue.js · Leaflet.js · plotly"], be["Controller"], "REST / HTTPS")
    d.edge(web["Формы ввода\nLaravel PHP"], be["Controller"], "REST")

    d.edge(be["DB Connector"], db["OLTP PostgreSQL\n10.82.1.28"], "ODBC:5432")
    d.edge(be["DB Connector"], db["OLAP Druid\n10.82.1.20"], "SQL")
    d.edge(be["Model"], mn["MinIO Console"], "S3 / HTTPS")
    d.edge(be["Controller"], af["Web server"], "REST (DAG trigger)")

    d.edge(af["Worker"], kf["Producer"], "produce")
    d.edge(af["Scheduler\n(DAG)"], sp["Apache Livy"], "submit job (Livy REST)")
    d.edge(kf["Consumer"], sp["Apache Spark"], "consume / stream")

    d.edge(sp["Apache Spark"], hd["NameNode · YARN\n10.82.1.1"], "YARN / HDFS")
    d.edge(sp["Apache Spark"], db["OLAP Druid\n10.82.1.20"], "write OLAP")
    d.edge(sp["Apache Spark"], mn["MinIO Console"], "read/write S3")
    d.edge(hd["DataNode 1\nMapReduce / Spark"], hd["NameNode · YARN\n10.82.1.1"], "HDFS", dashed=True)

    d.edge(pm["SuperSET"], db["OLAP Druid\n10.82.1.20"], "SQL (витрины)")

    d.edge(be["Controller"], elk["Logstash"], "logs", dashed=True)
    d.edge(af["Web server"], elk["Logstash"], "logs", dashed=True)
    d.edge(sp["Apache Spark"], elk["Logstash"], "logs", dashed=True)
    d.edge(elk["Logstash"], elk["Elasticsearch"], "ingest")
    d.edge(elk["Elasticsearch"], elk["Kibana"], "query")

    d.edge(dev["GitLab · полирепозиторий\nDEV 172.20.103.31"], dev["SonarQube CE\n10.82.4.29"], "code scan")
    d.edge(dev["SonarQube CE\n10.82.4.29"], dev["Dependency-Track\n10.82.4.30"], "SBOM")
    d.edge(be["Controller"], dev["Sentry\n10.82.4.65"], "errors", dashed=True)

    # --- Легенда -------------------------------------------------------------
    legend = make_obj(
        value="Легенда",
        position=(70, 1360),
        width=1280,
        height=140,
        baseStyle=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#999999;"
            "verticalAlign=top;align=left;fontStyle=1;spacingLeft=10;spacingTop=6;"
        ),
    )
    page.add_object(legend)

    legend_items = [
        ("Презентация / веб", "web"),
        ("Приложение (MVC)", "app"),
        ("Платформа данных / обработка", "data"),
        ("Хранилища / БД", "db"),
        ("Наблюдаемость / аудит", "obs"),
        ("DevOps / инструменты", "tool"),
    ]
    for i, (label, kind) in enumerate(legend_items):
        col = i % 3
        row = i // 3
        swatch = make_obj(
            value="",
            position=(90 + col * 420, 1400 + row * 50),
            width=34,
            height=24,
            baseStyle=comp_style(kind),
        )
        page.add_object(swatch)
        cap = make_obj(
            value=label,
            position=(132 + col * 420, 1400 + row * 50),
            width=270,
            height=24,
            baseStyle="text;html=1;align=left;verticalAlign=middle;fontSize=11;",
        )
        page.add_object(cap)

    note = make_obj(
        value=(
            "Сплошная линия — синхронный вызов / поток данных (с протоколом и портом).\n"
            "Пунктир — асинхронные / служебные потоки (логи, репликация HDFS, ошибки)."
        ),
        position=(1360, 1360),
        width=400,
        height=140,
        baseStyle="text;html=1;align=left;verticalAlign=top;fontSize=10;fontColor=#5A5A5A;",
    )
    page.add_object(note)

    return f


def render_svg(drawio_path: Path, svg_path: Path) -> bool:
    """Best-effort static SVG preview of the .drawio (requires matplotlib).

    The editable source of truth is the .drawio file; this SVG is a viewable
    companion consistent with the other diagrams in ``docs/svg/``.
    """
    try:
        import re
        import xml.etree.ElementTree as ET

        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
    except Exception as exc:  # pragma: no cover - optional dependency
        print(f"SKIP svg preview ({exc})")
        return False

    tree = ET.parse(drawio_path)
    model = tree.find(".//mxGraphModel")
    pw = float(model.get("pageWidth", 1780))
    ph = float(model.get("pageHeight", 1560))

    cells: Dict[str, dict] = {}
    edges: List[Tuple[str, str, str]] = []
    for c in tree.iter("mxCell"):
        style = c.get("style", "") or ""
        geo = c.find("mxGeometry")
        if c.get("edge") == "1":
            edges.append((c.get("source"), c.get("target"), c.get("value", "")))
            continue
        if geo is not None and c.get("vertex") == "1" and geo.get("width"):
            cells[c.get("id")] = {
                "v": c.get("value", ""),
                "x": float(geo.get("x", 0)),
                "y": float(geo.get("y", 0)),
                "w": float(geo.get("width", 0)),
                "h": float(geo.get("height", 0)),
                "style": style,
            }

    def color(style: str, key: str, default: str) -> str:
        m = re.search(rf"{key}=(#[0-9A-Fa-f]{{6}}|none)", style)
        return m.group(1) if m else default

    fig, ax = plt.subplots(figsize=(pw / 100, ph / 100))
    ax.set_xlim(0, pw)
    ax.set_ylim(0, ph)
    ax.invert_yaxis()
    ax.axis("off")

    def z_order(c: dict) -> int:
        if "dashed=1;dashPattern" in c["style"]:
            return 0
        if "fillColor=#EEF2F7" in c["style"]:
            return 1
        return 2

    for c in sorted(cells.values(), key=z_order):
        s = c["style"]
        fill = color(s, "fillColor", "#ffffff")
        module = "shape=module" in s
        ax.add_patch(
            Rectangle(
                (c["x"], c["y"]),
                c["w"],
                c["h"],
                facecolor="none" if fill == "none" else fill,
                edgecolor=color(s, "strokeColor", "#666666"),
                linewidth=1.3,
                linestyle="--" if "dashed=1" in s else "-",
                zorder=2 if module else 1,
            )
        )
        txt = c["v"].replace("&#xa;", "\n").replace("&lt;", "<").replace("&gt;", ">")
        top = "verticalAlign=top" in s
        ax.text(
            (c["x"] + 8) if top else c["x"] + c["w"] / 2,
            (c["y"] + 6) if top else c["y"] + c["h"] / 2,
            txt,
            ha="left" if top else "center",
            va="top" if top else "center",
            fontsize=7 if module else 9,
            zorder=3,
        )

    def center(cid: str):
        c = cells.get(cid)
        return (c["x"] + c["w"] / 2, c["y"] + c["h"] / 2) if c else None

    for src, tgt, lbl in edges:
        a, b = center(src), center(tgt)
        if not a or not b:
            continue
        ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="->", color="#444", lw=1), zorder=4)
        if lbl:
            ax.text(
                (a[0] + b[0]) / 2,
                (a[1] + b[1]) / 2,
                lbl,
                fontsize=6,
                color="#16407a",
                ha="center",
                va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85),
                zorder=5,
            )

    svg_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(svg_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print(f"OK svg preview -> {svg_path}")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = build().write(overwrite=True)
    print(f"OK 08-abai-c4-component -> {out}")
    render_svg(Path(out), SVG_DIR / "08-abai-c4-component.svg")


if __name__ == "__main__":
    main()
