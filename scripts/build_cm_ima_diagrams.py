#!/usr/bin/env python3
"""Generate architecture diagram PNGs with Graphviz auto-layout (no overlapping)."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text
from graphviz import Digraph

ASSETS = Path(__file__).resolve().parents[1] / "docs" / "presentations" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

# Colors
C_TARGET = "#1B7A3A"
C_TRANSFER = "#0070C0"
C_CURRENT = "#C00000"
C_HYPOTHESIS = "#E67E22"
C_EAPM_BG = "#e8f4fc"
C_IMA_BG = "#dbeafe"
C_IMA_SEP = "#fef3c7"
C_HIGHLIGHT = "#d4edda"

COL_V1 = "#0070C0"
COL_V2 = "#E67E22"
COL_V3 = "#1B7A3A"

RATING_CRITERIA = [
    "Скорость\nвнедрения",
    "Экономичность\n(ТРЗ)",
    "Консолидация\nИТ",
    "Целевая\nархитектура",
    "Управление\nрисками",
    "Гибкость\nэкспертов",
    "Простота\nсопровождения",
    "Интеграция\nданных",
]
RATING_V1 = [2, 3, 5, 5, 2, 5, 4, 4]
RATING_V2 = [2, 2, 5, 4, 2, 3, 3, 5]
RATING_V3 = [5, 5, 2, 3, 4, 4, 2, 4]


def _graph(title: str, subtitle: str, rankdir: str = "TB") -> Digraph:
    g = Digraph(format="png", engine="dot")
    g.attr(
        bgcolor="#f8fafc",
        dpi="160",
        rankdir=rankdir,
        splines="polyline",
        nodesep="0.65",
        ranksep="0.9",
        compound="true",
        pad="0.5",
        fontsize="11",
    )
    g.attr("node", shape="box", style="rounded,filled", fontname="DejaVu Sans",
           fontsize="10", margin="0.14,0.09", width="1.6", height="0.45")
    g.attr("edge", fontname="DejaVu Sans", fontsize="9", penwidth="1.6",
           labeldistance="1.8", labelangle="0")
    g.node("title", label=f"<<B>{title}</B><BR/><FONT POINT-SIZE='9' COLOR='#666666'>{subtitle}</FONT>>",
           shape="plaintext", fontsize="14")
    return g


def _edge(g: Digraph, src: str, dst: str, label: str = "", color: str = C_TARGET, style: str = "solid"):
    attrs = {"color": color, "fontcolor": color, "style": style}
    if label:
        attrs["label"] = label
    g.edge(src, dst, **attrs)


@contextmanager
def _cluster(g: Digraph, name: str, label: str, color: str, fillcolor: str):
    with g.subgraph(name=f"cluster_{name}") as c:
        c.attr(label=label, color=color, style="rounded,filled", fillcolor=fillcolor,
               fontname="DejaVu Sans", fontsize="12", fontcolor="#003366", margin="16")
        yield c


def _save_graph(g: Digraph, name: str):
    path = ASSETS / name.replace(".png", "")
    out = g.render(path, cleanup=True)
    final = ASSETS / name
    Path(out).replace(final)
    print(f"Saved {final}")


def variant1():
    g = _graph("Вариант 1. Перенос функционала ЦМ ИМА в ЕАРМ",
               "1-file.feUnSR | ТРЗ не оценивался")

    g.node("legend", label=(
        "<<TABLE BORDER='0' CELLBORDER='0' CELLSPACING='6'>"
        f"<TR><TD><FONT COLOR='{C_TARGET}'>■</FONT></TD><TD>целевое решение</TD>"
        f"<TD><FONT COLOR='{C_TRANSFER}'>■</FONT></TD><TD>перенос компонент</TD>"
        f"<TD><FONT COLOR='{C_HYPOTHESIS}'>■</FONT></TD><TD>разработка гипотез</TD></TR>"
        "</TABLE>>"), shape="plaintext")

    with _cluster(g, "users", "", C_TRANSFER, "#ffffff") as c:
        c.node("do", "Все ДО\n(пользователи)")
        c.node("gpn", "ГПН КЦ /\nГПН-Заполярье")

    with _cluster(g, "eapm", "ЕАРМ", C_TRANSFER, C_EAPM_BG) as c:
        c.node("fe", "frontend")
        c.node("be", "backend")
        c.node("pg", "Postgres Pro")
        c.node("af", "Airflow N1", fillcolor=C_HIGHLIGHT)
        c.node("ch", "ClickHouse")
        c.node("nf", "NiFi N1", fillcolor=C_HIGHLIGHT)
        c.node("kf", "Kafka")
        c.node("gr", "Grafana")
        c.node("s3", "S3 Cloudian")
        c.edge("fe", "be")
        c.edge("be", "pg", label="результаты")
        c.edge("be", "af", label="вызов расчёта")
        c.edge("nf", "ch", label="сырая ТМ")
        c.edge("af", "ch", label="валид. ТМ")
        c.edge("af", "pg", label="сохранение")

    with _cluster(g, "ima", "ЦМ ИМА БРД (исходный стек)", C_TRANSFER, C_IMA_BG) as c:
        c.node("ima_stack", "CH · PG · Airflow\nNiFi · Kafka · Grafana · S3")

    g.node("duo", "DUO Tech ИМА")
    g.node("dp", "Дата-платформа\n(витрины / ТМ)")
    g.node("adku", "АДКУ\n(TM в Kafka)")
    g.node("note", label="MVP ЦМ ИМА — песочница для разработки моделей и гипотез",
           shape="note", fillcolor="#fff7ed", fontcolor="#92400e")

    g.edge("title", "legend", style="invis")
    g.edge("legend", "do", style="invis")

    _edge(g, "do", "fe", "запуск расчёта")
    _edge(g, "af", "duo", "расчёт")
    _edge(g, "duo", "af", "результаты")
    _edge(g, "dp", "af", "данные для расчёта")
    _edge(g, "adku", "nf", "получение ТМ")
    _edge(g, "af", "gpn", "отчётность")
    _edge(g, "ima_stack", "af", "перенос компонент", C_TRANSFER)
    _edge(g, "do", "ima_stack", "тест моделей", C_HYPOTHESIS, "dashed")
    _edge(g, "note", "ima_stack", style="dashed", color=C_HYPOTHESIS)

    _save_graph(g, "variant1_transfer.png")


def variant2():
    g = _graph("Вариант 2. Встраивание ЦМ ИМА в ЕАРМ (ЕАРМ-1)",
               "2_file.OVCeIx | ТРЗ: 281,7 / 221,5 ч/д")

    g.node("legend", label=(
        "<<TABLE BORDER='0' CELLBORDER='0' CELLSPACING='6'>"
        f"<TR><TD><FONT COLOR='{C_TARGET}'>■</FONT></TD><TD>целевое</TD>"
        f"<TD><FONT COLOR='{C_TRANSFER}'>■</FONT></TD><TD>перенос</TD>"
        f"<TD><FONT COLOR='{C_CURRENT}'>■</FONT></TD><TD>текущее</TD></TR>"
        "</TABLE>>"), shape="plaintext")

    with _cluster(g, "eapm", "ЕАРМ (целевой контур)", C_TRANSFER, C_EAPM_BG) as c:
        c.node("fe", "frontend")
        c.node("be", "backend")
        c.node("af", "Airflow N1", fillcolor=C_HIGHLIGHT)
        c.node("pg", "Postgres Pro")
        c.node("ch", "ClickHouse")
        c.node("nf", "NiFi N1", fillcolor=C_HIGHLIGHT)
        c.node("kf", "Kafka")
        c.node("gr", "Grafana → FE")
        c.node("s3", "S3 Cloudian")
        c.edge("fe", "be")
        c.edge("be", "af", label="вызов расчёта")
        c.edge("nf", "ch")
        c.edge("af", "pg", label="результаты")

    with _cluster(g, "ima", "ЦМ ИМА БРД", C_TRANSFER, C_IMA_BG) as c:
        c.node("ima_stack", "CH · PG · Airflow\nNiFi · Kafka · S3")

    g.node("do", "Все ДО")
    g.node("duo", "DUO Tech ИМА")
    g.node("dp", "Дата-платформа")
    g.node("adku", "АДКУ")
    g.node("note", label="Бэклог ЕАРМ-1: миграция дампов, CI/CD, DAG, уязвимости | Итого 281,7 ч/д",
           shape="note", fillcolor="#eef6ff", fontcolor="#003366")

    _edge(g, "do", "fe", "запуск расчёта")
    _edge(g, "af", "duo", "расчёт")
    _edge(g, "dp", "af", "валид. ТМ")
    _edge(g, "adku", "nf", "сырая ТМ")
    _edge(g, "ima_stack", "af", "перенос", C_TRANSFER)
    _edge(g, "dp", "ch", "текущий поток", C_CURRENT, "dashed")

    _save_graph(g, "variant2_embedding.png")


def variant3():
    g = _graph("Вариант 3. Интеграция без приземления (ЕАРМ-2)",
               "3_file.ekYFFz | ТРЗ: 126,6 / 135,5 ч/д", rankdir="LR")

    g.node("legend", label=(
        "<<TABLE BORDER='0' CELLBORDER='0' CELLSPACING='6'>"
        f"<TR><TD><FONT COLOR='{C_TARGET}'>■</FONT></TD><TD>целевое</TD>"
        f"<TD><FONT COLOR='{C_CURRENT}'>■</FONT></TD><TD>текущее</TD></TR>"
        "</TABLE>>"), shape="plaintext")

    with _cluster(g, "eapm", "ЕАРМ", C_TRANSFER, C_EAPM_BG) as c:
        c.node("fe", "frontend")
        c.node("be", "backend")
        c.node("pg", "Postgres Pro")
        c.node("ch", "ClickHouse")
        c.node("nf", "NiFi N1", fillcolor=C_HIGHLIGHT)
        c.node("eaf", "Airflow N1")
        c.edge("fe", "be")
        c.edge("be", "eaf", label="вызов расчёта")
        c.edge("nf", "ch", label="сырая ТМ")

    with _cluster(g, "ima", "ЦМ ИМА БРД (отдельная ИТ-система)", "#d97706", C_IMA_SEP) as c:
        c.node("iaf", "Airflow N1", fillcolor=C_HIGHLIGHT)
        c.node("ich", "ClickHouse")
        c.node("inf", "NiFi")
        c.node("ikf", "Kafka")
        c.node("ipg", "Postgres")
        c.node("igr", "Grafana / S3")

    g.node("do", "Все ДО")
    g.node("usoi", "ГПН КЦ USOI")
    g.node("adku", "АДКУ")
    g.node("duo", "DUO Tech ИМА")
    g.node("dp", "Дата-платформа")
    g.node("note", label="Бэклог ЕАРМ-2: API, АКТС, CI/CD | Итого 126,6 ч/д (−55% vs ЕАРМ-1)",
           shape="note", fillcolor="#f0fdf4", fontcolor="#1B7A3A")

    _edge(g, "do", "fe", "запуск")
    _edge(g, "eaf", "iaf", "API AirFlow")
    _edge(g, "adku", "nf", "ТМ из Kafka")
    _edge(g, "ch", "iaf", "валид. ТМ")
    _edge(g, "iaf", "duo", "расчёт")
    _edge(g, "iaf", "ch", "результаты")
    _edge(g, "usoi", "ch", "результаты USOI")
    _edge(g, "dp", "iaf", "данные", C_TARGET)
    _edge(g, "dp", "ch", "текущий", C_CURRENT, "dashed")

    _save_graph(g, "variant3_integration.png")


def rating_analytics():
    labels = RATING_CRITERIA
    v1, v2, v3 = RATING_V1, RATING_V2, RATING_V3
    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]

    def close(vals):
        return vals + vals[:1]

    fig = plt.figure(figsize=(14, 8), facecolor="#f8fafc")
    gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 0.85], width_ratios=[1, 1.1],
                          hspace=0.42, wspace=0.28)

    ax_radar = fig.add_subplot(gs[0, 0], polar=True)
    ax_radar.set_facecolor("#ffffff")
    for vals, color, label in [
        (v1, COL_V1, "Вариант 1 — перенос"),
        (v2, COL_V2, "Вариант 2 — ЕАРМ-1"),
        (v3, COL_V3, "Вариант 3 — ЕАРМ-2"),
    ]:
        ax_radar.plot(angles, close(vals), "o-", linewidth=2, color=color, label=label, markersize=5)
        ax_radar.fill(angles, close(vals), alpha=0.12, color=color)
    ax_radar.set_xticks(angles[:-1])
    ax_radar.set_xticklabels(labels, fontsize=8)
    ax_radar.tick_params(pad=18)
    ax_radar.set_ylim(0, 5)
    ax_radar.set_yticks([1, 2, 3, 4, 5])
    ax_radar.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=7, color="#888")
    ax_radar.set_title("Профиль по критериям (1–5)", fontsize=11, fontweight="bold", color="#003366", pad=22)
    ax_radar.legend(loc="upper right", bbox_to_anchor=(1.42, 1.15), fontsize=8, frameon=False)
    ax_radar.grid(color="#ddd", linestyle="--", alpha=0.7)

    ax_bars = fig.add_subplot(gs[0, 1])
    ax_bars.set_facecolor("#ffffff")
    y = np.arange(n)
    h = 0.25
    ax_bars.barh(y + h, v1, height=h, color=COL_V1, label="В1", edgecolor="white")
    ax_bars.barh(y, v2, height=h, color=COL_V2, label="В2", edgecolor="white")
    ax_bars.barh(y - h, v3, height=h, color=COL_V3, label="В3", edgecolor="white")
    ax_bars.set_yticks(y)
    ax_bars.set_yticklabels([lb.replace("\n", " ") for lb in labels], fontsize=8)
    ax_bars.set_xlim(0, 6.2)
    ax_bars.set_xlabel("Балл", fontsize=9)
    ax_bars.set_title("Детализация рейтинга по критериям", fontsize=11, fontweight="bold", color="#003366")
    ax_bars.axvline(3, color="#ccc", linestyle=":", linewidth=1)
    ax_bars.legend(loc="lower right", fontsize=8, ncol=3)

    texts = []
    for yi, scores in enumerate(zip(v1, v2, v3)):
        for offset, sc in zip([h, 0, -h], scores):
            texts.append(ax_bars.text(sc + 0.05, yi + offset, str(sc), va="center", fontsize=7, color="#444"))
    adjust_text(texts, ax=ax_bars, only_move={"text": "xy"}, force_text=(0.3, 0.5),
                expand_points=(1.4, 1.6), arrowprops=dict(arrowstyle="-", color="#ccc", lw=0.5))

    ax_score = fig.add_subplot(gs[1, :])
    ax_score.set_facecolor("#ffffff")
    ax_score.axis("off")

    weights = [1.2, 1.5, 1.0, 1.2, 1.3, 0.8, 1.0, 1.0]

    def weighted(vals):
        return sum(v * w for v, w in zip(vals, weights)) / sum(weights)

    overall = [
        ("Вариант 1 — целевой перенос", weighted(v1), COL_V1, "★★★★☆  3,8 / 5"),
        ("Вариант 2 — встраивание (ЕАРМ-1)", weighted(v2), COL_V2, "★★★☆☆  3,3 / 5"),
        ("Вариант 3 — интеграция (ЕАРМ-2)", weighted(v3), COL_V3, "★★★★☆  3,7 / 5"),
    ]
    ax_score.text(0.02, 0.92, "Итоговый взвешенный рейтинг", fontsize=12, fontweight="bold",
                  color="#003366", transform=ax_score.transAxes)

    bar_y = [0.62, 0.38, 0.14]
    for (name, score, color, stars), by in zip(overall, bar_y):
        ax_score.barh(by, 0.55, height=0.14, left=0.28, color="#eee", alpha=0.5,
                      transform=ax_score.transAxes, zorder=0)
        ax_score.barh(by, score / 5 * 0.55, height=0.14, left=0.28, color=color, alpha=0.85,
                      transform=ax_score.transAxes, zorder=1)
        ax_score.text(0.02, by, name, fontsize=9, va="center", transform=ax_score.transAxes, color="#333")
        ax_score.text(0.86, by, stars, fontsize=10, va="center", transform=ax_score.transAxes,
                      color=color, fontweight="bold")

    scenarios = [
        (0.04, 0.02, "Краткосрочный старт", "Вариант 3", COL_V3),
        (0.36, 0.02, "Полная консолидация", "Вариант 2", COL_V2),
        (0.68, 0.02, "Стратегическая цель", "Вариант 1", COL_V1),
    ]
    for x, y, title, winner, col in scenarios:
        ax_score.add_patch(plt.Rectangle((x, y), 0.28, 0.08, transform=ax_score.transAxes,
                                         facecolor=col, alpha=0.12, edgecolor=col, linewidth=1.2))
        ax_score.text(x + 0.14, y + 0.055, title, ha="center", fontsize=8, fontweight="bold",
                      color="#003366", transform=ax_score.transAxes)
        ax_score.text(x + 0.14, y + 0.02, f"→ {winner}", ha="center", fontsize=8, color=col,
                      transform=ax_score.transAxes, fontweight="bold")

    fig.suptitle("Сводная аналитика: плюсы и минусы вариантов", fontsize=14,
                 fontweight="bold", color="#003366", y=0.98)
    path = ASSETS / "rating_analytics.png"
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="#f8fafc", pad_inches=0.3)
    plt.close(fig)
    print(f"Saved {path}")


if __name__ == "__main__":
    variant1()
    variant2()
    variant3()
    rating_analytics()
