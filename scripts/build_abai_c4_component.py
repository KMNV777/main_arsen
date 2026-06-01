#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the C4 Component diagram for the ABAI information system (ИС ABAI).

Source data: текущая ИТ-архитектура ИС «ABAI» (KMGE), диаграмма взаимодействия
IT-ландшафта (рис. 4.2.2). Стиль повторяет пример C4-диаграммы Nedra Digital Twin:
контейнеры-хосты с инфраструктурой (IP), узлы «component», связи с протоколами и
портами, контурные зоны и легенда.

Связи разведены вручную по выделенным каналам (вертикальные «шины» между
колонками и горизонтальные коридоры между рядами), чтобы пересечений было как
можно меньше. Граф зависимостей непланарен, поэтому единичные неизбежные
пересечения помечаются «мостиками» (jumpStyle=arc) для читаемости.

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
SIDE_W = 230
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

COMP_PALETTE = {
    "web": ("#DAE8FC", "#6C8EBF"),
    "app": ("#D5E8D4", "#82B366"),
    "data": ("#FFF2CC", "#D6B656"),
    "db": ("#FFE6CC", "#D79B00"),
    "tool": ("#F5F5F5", "#999999"),
    "obs": ("#E1D5E7", "#9673A6"),
}

EDGE_SOLID = "#36506B"
EDGE_DASH = "#9673A6"


def comp_style(kind: str) -> str:
    fill, stroke = COMP_PALETTE.get(kind, COMP_PALETTE["app"])
    return (
        f"shape=module;jettyWidth=14;jettyHeight=6;whiteSpace=wrap;html=1;"
        f"fillColor={fill};strokeColor={stroke};fontSize=11;verticalAlign=middle;"
        f"align=center;spacingLeft=6;spacingRight=4;"
    )


def make_obj(**kwargs) -> Object:
    """Create an Object whose style is exactly its ``baseStyle``.

    drawpyo otherwise appends template defaults (``rounded=0;dashed=0``) that
    would override the dashed zones and rounded containers defined in baseStyle.
    """
    obj = Object(**kwargs)
    obj.style_attributes = []
    return obj


def container_dims(n_comps: int, cols: int, comp_w: int) -> Tuple[int, int]:
    rows = max(1, math.ceil(n_comps / cols))
    w = PAD_SIDE * 2 + cols * comp_w + (cols - 1) * GAP_X
    h = PAD_TOP + rows * COMP_H + (rows - 1) * GAP_Y + PAD_BOT
    return w, h


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

    def person(self, title: str, x: int, y: int, w: int = 220, h: int = 80) -> Object:
        return self._add(make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=PERSON_STYLE), x, y, w, h)

    def container(
        self, title: str, x: int, y: int, comps: List[Tuple[str, str]], cols: int, comp_w: int = COMP_W
    ) -> Tuple[Object, Dict[str, Object]]:
        w, h = container_dims(len(comps), cols, comp_w)
        box = self._add(make_obj(value=title, position=(x, y), width=w, height=h, baseStyle=CONTAINER_STYLE), x, y, w, h)
        objs: Dict[str, Object] = {}
        for i, (label, kind) in enumerate(comps):
            col, row = i % cols, i // cols
            cx = x + PAD_SIDE + col * (comp_w + GAP_X)
            cy = y + PAD_TOP + row * (COMP_H + GAP_Y)
            node = make_obj(
                value=f"«component»\n{label}", position=(cx, cy), width=comp_w, height=COMP_H, baseStyle=comp_style(kind)
            )
            self._add(node, cx, cy, comp_w, COMP_H)
            objs[label] = node
        return box, objs

    def anchor(self, obj: Object, fx: float, fy: float) -> Tuple[float, float]:
        x, y, w, h = self.geo[id(obj)]
        return (x + fx * w, y + fy * h)

    def route(
        self,
        src: Object,
        exit_frac: Tuple[float, float],
        tgt: Object,
        entry_frac: Tuple[float, float],
        waypoints: List[Tuple[int, int]],
        label: str = "",
        dashed: bool = False,
    ) -> None:
        edge = Edge(
            source=src,
            target=tgt,
            page=self.page,
            label=label,
            pattern="dashed_medium" if dashed else "solid",
            exitX=exit_frac[0],
            exitY=exit_frac[1],
            entryX=entry_frac[0],
            entryY=entry_frac[1],
            jumpStyle="arc",
            jumpSize=10,
            rounded=0,
        )
        edge.strokeColor = EDGE_DASH if dashed else EDGE_SOLID
        for (wx, wy) in waypoints:
            edge.geometry.add_point(wx, wy)
        self.page.add_object(edge)
        a = self.anchor(src, *exit_frac)
        b = self.anchor(tgt, *entry_frac)
        self.polylines.append({"pts": [a, *waypoints, b], "label": label, "dashed": dashed})


# ---------------------------------------------------------------------------
# Anchor side helpers
# ---------------------------------------------------------------------------
def L(f: float = 0.5):
    return (0.0, f)


def R(f: float = 0.5):
    return (1.0, f)


def T(f: float = 0.5):
    return (f, 0.0)


def B(f: float = 0.5):
    return (f, 1.0)


def build() -> Tuple[File, Diagram]:
    f = File(file_name="08-abai-c4-component.drawio", file_path=str(OUT_DIR))
    page = Page(file=f, name="C4 Component — ИС ABAI", width=1820, height=1760)
    d = Diagram(page)

    # --- Зоны (фон) ----------------------------------------------------------
    d.zone("Прикладной контур ИС ABAI · Intranet / VPN DMZ (HTTPS)", 40, 150, 1300, 400)
    d.zone("Платформа данных и обработки · Hadoop / Spark / Kafka / Airflow / БД / MinIO", 40, 590, 1300, 920)
    d.zone("DevOps, наблюдаемость и инструменты", 1360, 150, 320, 1360)

    # --- Пользователь --------------------------------------------------------
    person = d.person("Пользователь ЭМГ\n(браузер / АРМ)", 70, 40)

    # --- Веб-приложение (порядок задаёт сетку: коннекторы наружу — в правой колонке) ---
    _, web = d.container(
        "Веб-приложение ИС ABAI · 172.20.103.77\nNginx, Node.js",
        70,
        200,
        [
            ("Nginx\n(веб-сервер)", "web"),       # c0r0
            ("Формы ввода\nLaravel PHP", "web"),   # c1r0  (→ backend)
            ("Node.js", "web"),                    # c0r1
            ("Frontend\nVue.js · Leaflet.js · plotly", "web"),  # c1r1 (→ backend)
            ("MySQL\n(локальная БД)", "db"),       # c0r2
        ],
        cols=2,
    )

    _, be = d.container(
        "ИС ABAI · Backend · 172.20.103.203\nMVC — Laravel / Django · PHP / Python",
        700,
        200,
        [
            ("View", "app"),          # c0r0
            ("Controller", "app"),    # c1r0
            ("Model", "app"),         # c2r0
            ("ORM", "app"),           # c0r1
            ("DB Connector", "app"),  # c1r1   (c2r1 пусто)
        ],
        cols=3,
    )

    _, af = d.container(
        "Apache Airflow · ETL · 172.20.102.82\nпланировщик и оркестрация",
        70,
        620,
        [
            ("Web server", "data"),     # c0r0
            ("Scheduler\n(DAG)", "data"),  # c1r0
            ("Worker", "data"),         # c2r0  (→ Kafka / → Spark)
            ("Broker", "data"),         # c0r1
            ("Metadata DB", "db"),      # c1r1  (c2r1 пусто)
        ],
        cols=3,
    )

    _, kf = d.container(
        "Apache Kafka cluster · 172.20.102.45\nброкер сообщений",
        700,
        620,
        [
            ("Kafka Broker", "data"),   # c0r0
            ("ZooKeeper", "data"),      # c1r0
            ("Streams Messaging\nManager · 10.82.1.31", "data"),  # c2r0
            ("Producer", "data"),       # c0r1
            ("Consumer", "data"),       # c1r1  (→ Spark)
        ],
        cols=3,
    )

    _, sp = d.container(
        "Apache Spark / Livy · 10.82.1.12\nML · Computer Vision (Nvidia CUDA)",
        70,
        940,
        [
            ("Apache Spark", "data"),   # c0r0
            ("Apache Livy", "data"),    # c1r0
            ("Spark Job\n(Scala)", "data"),  # c2r0  (→ Hadoop)
            ("Spark Job\n(Python)", "data"), # c0r1  (→ БД)
            ("Spark Job\n(SQL)", "data"),    # c1r1  (→ MinIO)
        ],
        cols=3,
    )

    _, hd = d.container(
        "Hadoop кластер · распределённая обработка\nCloudera",
        700,
        940,
        [
            ("NameNode · YARN\n10.82.1.1", "data"),   # c0r0
            ("DataNode 1\nMapReduce / Spark", "data"),  # c1r0
            ("DataNode 2\nMapReduce / Spark", "data"),  # c2r0
            ("DataNode 3\nMapReduce / Spark", "data"),  # c0r1
            ("Cloudera Manager\n10.82.1.2", "data"),    # c1r1
        ],
        cols=3,
    )

    _, db = d.container(
        "Базы данных",
        70,
        1260,
        [
            ("OLTP PostgreSQL\n10.82.1.28", "db"),
            ("OLTP PostgreSQL\nmaster/slave · 10.82.1.29", "db"),
            ("OLAP Druid\n10.82.1.20", "db"),
        ],
        cols=3,
    )

    _, mn = d.container(
        "MinIO Object Storage (S3) · 172.20.102.54",
        700,
        1260,
        [
            ("MinIO Console", "db"),       # c0r0
            ("S3 Node 1\n10.82.2.36", "db"),  # c1r0
            ("S3 Node 2\n10.82.2.37", "db"),  # c2r0
            ("S3 Node 3\n10.82.2.38", "db"),  # c0r1
            ("S3 Node 4\n10.82.2.39", "db"),  # c1r1
        ],
        cols=3,
    )

    _, elk = d.container(
        "Аудит и журналирование (ELK)",
        1380,
        200,
        [("Logstash", "obs"), ("Elasticsearch", "obs"), ("Kibana", "obs")],
        cols=1,
        comp_w=SIDE_W,
    )

    _, dev = d.container(
        "DevOps · качество кода",
        1380,
        620,
        [
            ("GitLab · полирепозиторий\nDEV 172.20.103.31", "tool"),
            ("SonarQube CE\n10.82.4.29", "tool"),
            ("Dependency-Track\n10.82.4.30", "tool"),
            ("Sentry\n10.82.4.65", "tool"),
            ("Docker\n172.20.102.23", "tool"),
        ],
        cols=1,
        comp_w=SIDE_W,
    )

    _, pm = d.container(
        "Управление проектом · визуализация",
        1380,
        1260,
        [("YouTrack", "tool"), ("SuperSET", "obs")],
        cols=1,
        comp_w=SIDE_W,
    )

    # --- Связи (разведены по каналам) ---------------------------------------
    # Пользователь → веб
    d.route(person, B(0.5), web["Nginx\n(веб-сервер)"], T(0.5), [(180, 185), (175, 185)], "HTTPS:443")

    # Веб → Backend.Controller (через средний гаттер и верхний коридор)
    d.route(
        web["Frontend\nVue.js · Leaflet.js · plotly"], R(0.5), be["Controller"], T(0.45),
        [(672, 372), (672, 170), (986, 170)], "REST / HTTPS",
    )
    d.route(
        web["Формы ввода\nLaravel PHP"], R(0.5), be["Controller"], T(0.6),
        [(662, 282), (662, 160), (1012, 160)], "REST",
    )

    # Backend.Controller → Airflow (вниз в коридор HC12, влево, в Web server)
    d.route(
        be["Controller"], B(0.5), af["Web server"], T(0.5),
        [(995, 540), (175, 540)], "REST (DAG trigger)",
    )

    # Backend.DB Connector → БД (левая дальняя шина)
    d.route(
        be["DB Connector"], B(0.4), db["OLTP PostgreSQL\n10.82.1.28"], L(0.5),
        [(978, 470), (55, 470), (55, 1342)], "ODBC:5432",
    )
    d.route(
        be["DB Connector"], B(0.6), db["OLAP Druid\n10.82.1.20"], T(0.459),
        [(1012, 500), (48, 500), (48, 1230), (548, 1230)], "SQL",
    )

    # Backend.Model → MinIO (правая шина, правее «шины логов»)
    d.route(
        be["Model"], R(0.5), mn["MinIO Console"], T(0.4),
        [(1344, 282), (1344, 1232), (788, 1232)], "S3 / HTTPS",
    )

    # Airflow.Worker → Kafka.Producer
    d.route(
        af["Worker"], R(0.5), kf["Producer"], L(0.5),
        [(686, 702), (686, 792)], "produce",
    )

    # Airflow.Worker → Spark.Livy (submit job)
    d.route(
        af["Worker"], B(0.5), sp["Apache Livy"], T(0.5),
        [(555, 885), (365, 885)], "submit job (Livy REST)",
    )

    # Kafka.Consumer → Spark.Apache Spark (stream)
    d.route(
        kf["Consumer"], B(0.5), sp["Apache Spark"], T(0.5),
        [(995, 900), (175, 900)], "consume / stream",
    )

    # Spark.Job(Scala) → Hadoop.NameNode
    d.route(
        sp["Spark Job\n(Scala)"], R(0.5), hd["NameNode · YARN\n10.82.1.1"], L(0.5),
        [(686, 1022)], "YARN / HDFS",
    )

    # Spark.Job(Python) → БД.Druid
    d.route(
        sp["Spark Job\n(Python)"], B(0.5), db["OLAP Druid\n10.82.1.20"], T(0.6),
        [(175, 1210), (572, 1210)], "write OLAP",
    )

    # Spark.Job(SQL) → MinIO.Console
    d.route(
        sp["Spark Job\n(SQL)"], B(0.5), mn["MinIO Console"], T(0.6),
        [(365, 1220), (822, 1220)], "read/write S3",
    )

    # Hadoop DataNode 1 → NameNode (внутри, пунктир)
    d.route(
        hd["DataNode 1\nMapReduce / Spark"], L(0.5), hd["NameNode · YARN\n10.82.1.1"], R(0.5),
        [], "HDFS", dashed=True,
    )

    # SuperSET → БД.Druid (витрины)
    d.route(
        pm["SuperSET"], L(0.5), db["OLAP Druid\n10.82.1.20"], R(0.5),
        [(1345, 1432), (1345, 1245), (640, 1245), (640, 1342)], "SQL (витрины)",
    )

    # ----- Логи в ELK (вложенные вертикали в правом гаттере) -----
    d.route(
        be["DB Connector"], R(0.5), elk["Logstash"], L(0.78),
        [(1316, 372), (1316, 300)], "logs", dashed=True,
    )
    d.route(
        af["Scheduler\n(DAG)"], T(0.5), elk["Logstash"], L(0.86),
        [(365, 560), (1324, 560), (1324, 305)], "logs", dashed=True,
    )
    d.route(
        sp["Spark Job\n(Scala)"], T(0.5), elk["Logstash"], L(0.94),
        [(555, 865), (1332, 865), (1332, 310)], "logs", dashed=True,
    )

    # ELK внутр.
    d.route(elk["Logstash"], B(0.5), elk["Elasticsearch"], T(0.5), [], "ingest")
    d.route(elk["Elasticsearch"], B(0.5), elk["Kibana"], T(0.5), [], "query")

    # DevOps внутр.
    d.route(dev["GitLab · полирепозиторий\nDEV 172.20.103.31"], B(0.5), dev["SonarQube CE\n10.82.4.29"], T(0.5), [], "code scan")
    d.route(dev["SonarQube CE\n10.82.4.29"], B(0.5), dev["Dependency-Track\n10.82.4.30"], T(0.5), [], "SBOM")

    # Backend → Sentry (errors)
    d.route(
        be["Model"], B(0.5), dev["Sentry\n10.82.4.65"], L(0.5),
        [(1185, 575), (1352, 575), (1352, 972)], "errors", dashed=True,
    )

    # --- Легенда -------------------------------------------------------------
    legend = make_obj(
        value="Легенда",
        position=(70, 1540),
        width=1270,
        height=150,
        baseStyle=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#999999;"
            "verticalAlign=top;align=left;fontStyle=1;spacingLeft=10;spacingTop=6;"
        ),
    )
    d._add(legend, 70, 1540, 1270, 150)

    legend_items = [
        ("Презентация / веб", "web"),
        ("Приложение (MVC)", "app"),
        ("Платформа данных / обработка", "data"),
        ("Хранилища / БД", "db"),
        ("Наблюдаемость / аудит", "obs"),
        ("DevOps / инструменты", "tool"),
    ]
    for i, (label, kind) in enumerate(legend_items):
        col, row = i % 3, i // 3
        sx, sy = 90 + col * 420, 1582 + row * 50
        d._add(make_obj(value="", position=(sx, sy), width=34, height=24, baseStyle=comp_style(kind)), sx, sy, 34, 24)
        cx2, cy2 = 132 + col * 420, 1582 + row * 50
        d._add(
            make_obj(value=label, position=(cx2, cy2), width=270, height=24,
                     baseStyle="text;html=1;align=left;verticalAlign=middle;fontSize=11;"),
            cx2, cy2, 270, 24,
        )

    note = make_obj(
        value=(
            "Сплошная линия — синхронный вызов / поток данных (с протоколом и портом).\n"
            "Пунктир — асинхронные / служебные потоки (логи, репликация HDFS, ошибки).\n"
            "«Мостик» на линии — пересечение без соединения."
        ),
        position=(1380, 1560),
        width=300,
        height=120,
        baseStyle="text;html=1;align=left;verticalAlign=top;fontSize=10;fontColor=#5A5A5A;",
    )
    d._add(note, 1380, 1560, 300, 120)

    return f, d


def render_svg(d: Diagram, svg_path: Path) -> bool:
    """Faithful static SVG preview drawn from the exact anchored polylines."""
    try:
        import re

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

    fig, ax = plt.subplots(figsize=(18.2, 17.6))
    ax.set_xlim(0, 1820)
    ax.set_ylim(0, 1760)
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
        ax.add_patch(
            Rectangle(
                (s["x"], s["y"]), s["w"], s["h"],
                facecolor="none" if fill == "none" else fill,
                edgecolor=color(st, "strokeColor", "#666666"),
                linewidth=1.3, linestyle="--" if "dashed=1" in st else "-",
                zorder=2 if module else 1,
            )
        )
        txt = s["v"].replace("&#xa;", "\n").replace("&lt;", "<").replace("&gt;", ">")
        top = "verticalAlign=top" in st
        ax.text(
            (s["x"] + 8) if top else s["x"] + s["w"] / 2,
            (s["y"] + 6) if top else s["y"] + s["h"] / 2,
            txt, ha="left" if top else "center", va="top" if top else "center",
            fontsize=7 if module else 9, zorder=3,
        )

    for e in d.polylines:
        pts = e["pts"]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax.plot(xs, ys, color=EDGE_DASH if e["dashed"] else EDGE_SOLID,
                lw=1.1, ls="--" if e["dashed"] else "-", zorder=4)
        ax.annotate("", xy=pts[-1], xytext=pts[-2],
                    arrowprops=dict(arrowstyle="->", color=EDGE_DASH if e["dashed"] else EDGE_SOLID, lw=1.1), zorder=4)
        if e["label"]:
            mid = pts[len(pts) // 2]
            ax.text(mid[0], mid[1], e["label"], fontsize=6, color="#16407a",
                    ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85), zorder=5)

    svg_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(svg_path, format="svg", bbox_inches="tight")
    fig.savefig("/opt/cursor/artifacts/abai-c4-component-preview.png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"OK svg preview -> {svg_path}")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    f, d = build()
    out = f.write(overwrite=True)
    print(f"OK 08-abai-c4-component -> {out}")
    render_svg(d, SVG_DIR / "08-abai-c4-component.svg")


if __name__ == "__main__":
    main()
