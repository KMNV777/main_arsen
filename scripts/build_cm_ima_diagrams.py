#!/usr/bin/env python3
"""Generate architecture diagram PNGs with Graphviz auto-layout (no overlapping)."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from graphviz import Digraph
from matplotlib.colors import LinearSegmentedColormap

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

RATING_CRITERIA_SHORT = [
    "Скорость внедрения",
    "Экономичность (ТРЗ)",
    "Консолидация ИТ",
    "Целевая архитектура",
    "Управление рисками",
    "Гибкость экспертов",
    "Простота сопровождения",
    "Интеграция данных",
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
    """Тепловая карта + итоговые баллы + блок методологии (без радара)."""
    labels = RATING_CRITERIA_SHORT
    v1, v2, v3 = RATING_V1, RATING_V2, RATING_V3
    matrix = np.array([v1, v2, v3]).T  # 8 × 3
    variants = ["Вариант 1\n(перенос)", "Вариант 2\n(ЕАРМ-1)", "Вариант 3\n(ЕАРМ-2)"]
    colors_list = [COL_V1, COL_V2, COL_V3]

    weights = np.array([1.2, 1.5, 1.0, 1.2, 1.3, 0.8, 1.0, 1.0])
    overall = [np.dot(matrix[:, j], weights) / weights.sum() for j in range(3)]

    cmap = LinearSegmentedColormap.from_list("corp", ["#E8EEF4", "#B3D4F0", "#0070C0", "#003366"])

    fig = plt.figure(figsize=(13.5, 7.2), facecolor="#F4F6F8")
    gs = fig.add_gridspec(3, 1, height_ratios=[2.6, 0.9, 1.1], hspace=0.38)

    # --- Heatmap ---
    ax_h = fig.add_subplot(gs[0])
    ax_h.set_facecolor("#FFFFFF")
    im = ax_h.imshow(matrix, cmap=cmap, vmin=1, vmax=5, aspect="auto")
    ax_h.set_xticks(range(3))
    ax_h.set_xticklabels(variants, fontsize=10, fontweight="bold")
    ax_h.set_yticks(range(len(labels)))
    ax_h.set_yticklabels(labels, fontsize=9)
    ax_h.set_title("Сравнительная матрица оценок (шкала 1–5)", fontsize=12,
                   fontweight="bold", color="#003366", pad=12)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = int(matrix[i, j])
            txt_color = "white" if val >= 4 else "#003366"
            ax_h.text(j, i, str(val), ha="center", va="center", fontsize=13,
                      fontweight="bold", color=txt_color)
    cbar = fig.colorbar(im, ax=ax_h, fraction=0.025, pad=0.02)
    cbar.set_label("Балл", fontsize=9)
    cbar.set_ticks([1, 2, 3, 4, 5])
    for spine in ax_h.spines.values():
        spine.set_visible(True)
        spine.set_color("#CCCCCC")

    # --- Overall scores ---
    ax_o = fig.add_subplot(gs[1])
    ax_o.set_facecolor("#FFFFFF")
    ax_o.set_xlim(0, 5.5)
    ax_o.set_ylim(-0.5, 2.5)
    ax_o.axis("off")
    ax_o.text(0, 2.15, "Итоговый взвешенный рейтинг", fontsize=11, fontweight="bold", color="#003366")
    names = ["В1 — целевой перенос", "В2 — встраивание (ЕАРМ-1)", "В3 — интеграция (ЕАРМ-2)"]
    for idx, (name, score, col) in enumerate(zip(names, overall, colors_list)):
        y = 1.5 - idx * 0.65
        ax_o.barh(y, 5, height=0.38, left=2.8, color="#E8EEF4", edgecolor="#CCCCCC", linewidth=0.5)
        ax_o.barh(y, score, height=0.38, left=2.8, color=col, alpha=0.9)
        ax_o.text(0, y, name, va="center", fontsize=9, color="#333333")
        stars = "★" * round(score) + "☆" * (5 - round(score))
        ax_o.text(2.8 + score + 0.12, y, f"{stars}  {score:.1f}/5", va="center", fontsize=9,
                  color=col, fontweight="bold")

    # --- Methodology ---
    ax_m = fig.add_subplot(gs[2])
    ax_m.set_facecolor("#E8EEF4")
    ax_m.axis("off")
    ax_m.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax_m.transAxes,
                                 facecolor="#E8EEF4", edgecolor="#003366", linewidth=1.2))
    methodology = (
        "Источник и методика оценок:\n"
        "• Экономичность (ТРЗ) — из бэклогов Excel: ЕАРМ-1 = 281,7 ч/д (2_file.OVCeIx), "
        "ЕАРМ-2 = 126,6 ч/д (3_file.ekYFFz); для В1 ТРЗ не оценивался → балл 3 (оценочно).\n"
        "• Остальные 7 критериев — экспертная оценка архитектурных схем (1-file.feUnSR, "
        "2_file.OVCeIx, 3_file.ekYFFz) по шкале 1 (низко) … 5 (высоко).\n"
        "• Итоговый балл = взвешенное среднее (веса: экономичность ×1,5; риски ×1,3; "
        "скорость ×1,2; архитектура ×1,2; остальные ×1,0).\n"
        "• Сценарии: краткосрочный старт → В3 | полная консолидация → В2 | стратегическая цель → В1"
    )
    ax_m.text(0.02, 0.95, methodology, transform=ax_m.transAxes, fontsize=8.5,
              color="#003366", va="top", ha="left", linespacing=1.45,
              bbox=dict(boxstyle="round,pad=0.4", facecolor="#E8EEF4", edgecolor="#003366"))

    path = ASSETS / "rating_analytics.png"
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="#F4F6F8", pad_inches=0.25)
    plt.close(fig)
    print(f"Saved {path}")


if __name__ == "__main__":
    variant1()
    variant2()
    variant3()
    rating_analytics()
