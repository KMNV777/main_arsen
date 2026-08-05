#!/usr/bin/env python3
"""Generate architecture diagram PNGs for CM IMA / EAPM presentation."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ASSETS = Path(__file__).resolve().parents[1] / "docs" / "presentations" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

FONT = "DejaVu Sans"


def box(ax, x, y, w, h, text, fc="#ffffff", ec="#0070C0", highlight=False, fs=9):
    ec_use = "#1B7A3A" if highlight else ec
    lw = 2.2 if highlight else 1.2
    fc_use = "#d4edda" if highlight else fc
    patch = FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.02",
        linewidth=lw, edgecolor=ec_use, facecolor=fc_use,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, wrap=True)


def arrow(ax, x1, y1, x2, y2, color="#1B7A3A", style="-", lw=1.8):
    arr = FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12,
        linewidth=lw, color=color, linestyle=style,
    )
    ax.add_patch(arr)


def save(fig, name: str):
    path = ASSETS / name
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="#f8fafc")
    plt.close(fig)
    print(f"Saved {path}")


def variant1():
    fig, ax = plt.subplots(figsize=(12, 6.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.8)
    ax.axis("off")
    ax.set_facecolor("#f8fafc")
    fig.patch.set_facecolor("#f8fafc")

    ax.text(6, 6.45, "Вариант 1. Перенос функционала ЦМ ИМА в ЕАРМ", ha="center", fontsize=14, fontweight="bold", color="#003366")
    ax.text(6, 6.15, "1-file.feUnSR | ТРЗ не оценивался", ha="center", fontsize=9, color="#666")

    box(ax, 0.3, 5.5, 11.4, 0.35, "", fc="#fff")
    ax.text(1.0, 5.67, "■ целевое", color="#1B7A3A", fontsize=8)
    ax.text(3.0, 5.67, "■ перенос компонент", color="#0070C0", fontsize=8)
    ax.text(5.5, 5.67, "■ разработка гипотез", color="#E67E22", fontsize=8)

    box(ax, 2.8, 2.8, 5.5, 2.0, "", fc="#e8f4fc", ec="#0070C0")
    ax.text(5.55, 4.55, "ЕАРМ", ha="center", fontsize=12, fontweight="bold", color="#003366")
    box(ax, 3.1, 3.9, 0.9, 0.35, "frontend")
    box(ax, 4.2, 3.9, 0.9, 0.35, "backend")
    box(ax, 5.3, 3.9, 1.1, 0.35, "Postgres")
    box(ax, 6.6, 3.9, 1.1, 0.35, "Airflow N1", highlight=True)
    box(ax, 3.1, 3.3, 1.0, 0.35, "ClickHouse")
    box(ax, 4.3, 3.3, 0.8, 0.35, "NiFi N1", highlight=True)
    box(ax, 5.3, 3.3, 0.7, 0.35, "Kafka")
    box(ax, 6.2, 3.3, 0.9, 0.35, "Grafana")
    box(ax, 3.1, 2.95, 2.0, 0.3, "S3 Cloudian")

    box(ax, 8.8, 2.8, 2.8, 2.0, "", fc="#dbeafe", ec="#0070C0")
    ax.text(10.2, 4.55, "ЦМ ИМА БРД", ha="center", fontsize=11, fontweight="bold")
    ax.text(10.2, 3.8, "исходный стек\n→ перенос", ha="center", fontsize=8)

    box(ax, 0.3, 3.2, 1.8, 0.9, "Все ДО\nзапуск расчёта")
    box(ax, 0.3, 1.8, 1.8, 0.7, "ГПН КЦ /\nЗаполярье")
    box(ax, 2.8, 0.5, 1.7, 0.7, "DUO Tech ИМА")
    box(ax, 5.0, 0.5, 1.8, 0.7, "Дата-платформа")
    box(ax, 7.5, 0.5, 1.4, 0.7, "АДКУ / Kafka")

    arrow(ax, 2.1, 3.65, 3.1, 4.05, "#1B7A3A")
    arrow(ax, 7.1, 3.9, 3.65, 1.2, "#1B7A3A")
    arrow(ax, 8.8, 3.7, 8.3, 3.5, "#0070C0", lw=2.5)
    arrow(ax, 1.2, 3.1, 3.5, 3.0, "#E67E22")
    arrow(ax, 7.1, 4.25, 1.2, 2.2, "#1B7A3A")

    ax.text(0.4, 0.2, "MVP ЦМ ИМА — песочница для разработки моделей (оранжевый контур)", fontsize=8, color="#92400e")
    save(fig, "variant1_transfer.png")


def variant2():
    fig, ax = plt.subplots(figsize=(12, 6.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.8)
    ax.axis("off")
    ax.set_facecolor("#f8fafc")

    ax.text(6, 6.45, "Вариант 2. Встраивание ЦМ ИМА в ЕАРМ (ЕАРМ-1)", ha="center", fontsize=14, fontweight="bold", color="#003366")
    ax.text(6, 6.15, "2_file.OVCeIx | ТРЗ: 281,7 / 221,5 ч/д", ha="center", fontsize=9, color="#666")

    box(ax, 2.5, 2.7, 5.8, 2.2, "", fc="#e8f4fc", ec="#0070C0")
    ax.text(5.4, 4.65, "ЕАРМ (целевой контур)", ha="center", fontsize=12, fontweight="bold")
    box(ax, 2.8, 3.9, 0.85, 0.32, "frontend")
    box(ax, 3.85, 3.9, 0.85, 0.32, "backend")
    box(ax, 4.9, 3.9, 1.0, 0.32, "Airflow N1", highlight=True)
    box(ax, 6.1, 3.9, 0.95, 0.32, "Postgres")
    box(ax, 2.8, 3.4, 1.0, 0.32, "ClickHouse")
    box(ax, 4.0, 3.4, 0.8, 0.32, "NiFi N1", highlight=True)
    box(ax, 5.0, 3.4, 0.7, 0.32, "Kafka")
    box(ax, 5.9, 3.4, 0.9, 0.32, "Grafana→FE")
    box(ax, 2.8, 2.95, 1.8, 0.32, "S3 Cloudian")

    box(ax, 8.8, 2.9, 2.8, 1.6, "", fc="#dbeafe", ec="#0070C0")
    ax.text(10.2, 4.2, "ЦМ ИМА БРД", ha="center", fontsize=11, fontweight="bold")
    ax.text(10.2, 3.5, "CH, PG, Airflow,\nNiFi, Kafka, S3", ha="center", fontsize=8)

    arrow(ax, 8.8, 3.6, 8.3, 3.5, "#0070C0", lw=2.5)
    ax.text(8.35, 3.75, "перенос", fontsize=7, color="#0070C0")

    box(ax, 0.3, 3.3, 1.7, 0.8, "Все ДО")
    box(ax, 2.5, 0.5, 1.6, 0.65, "DUO Tech")
    box(ax, 4.5, 0.5, 1.8, 0.65, "Дата-платформа")
    box(ax, 7.0, 0.5, 1.4, 0.65, "АДКУ")

    arrow(ax, 2.0, 3.7, 2.8, 4.0, "#1B7A3A")
    arrow(ax, 5.4, 3.9, 3.3, 1.15, "#1B7A3A")
    arrow(ax, 7.7, 1.15, 4.4, 3.4, "#1B7A3A")
    arrow(ax, 5.4, 1.15, 5.4, 3.4, "#C00000", style="--")

    ax.text(0.4, 0.15, "Бэклог ЕАРМ-1: миграция дампов, CI/CD, DAG, уязвимости, документация | Итого 281,7 ч/д", fontsize=8, color="#003366")
    save(fig, "variant2_embedding.png")


def variant3():
    fig, ax = plt.subplots(figsize=(12, 6.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.8)
    ax.axis("off")
    ax.set_facecolor("#f8fafc")

    ax.text(6, 6.45, "Вариант 3. Интеграция без приземления (ЕАРМ-2)", ha="center", fontsize=14, fontweight="bold", color="#003366")
    ax.text(6, 6.15, "3_file.ekYFFz | ТРЗ: 126,6 / 135,5 ч/д", ha="center", fontsize=9, color="#666")

    box(ax, 0.4, 2.8, 4.3, 2.0, "", fc="#e8f4fc", ec="#0070C0")
    ax.text(2.55, 4.55, "ЕАРМ", ha="center", fontsize=12, fontweight="bold")
    box(ax, 0.7, 3.9, 0.8, 0.3, "frontend")
    box(ax, 1.7, 3.9, 0.8, 0.3, "backend")
    box(ax, 2.7, 3.9, 0.8, 0.3, "Postgres")
    box(ax, 0.7, 3.4, 1.0, 0.3, "ClickHouse")
    box(ax, 1.9, 3.4, 0.8, 0.3, "NiFi N1", highlight=True)
    box(ax, 2.9, 3.4, 1.0, 0.3, "Airflow N1")

    box(ax, 7.0, 2.8, 4.5, 2.0, "", fc="#fef3c7", ec="#d97706")
    ax.text(9.25, 4.55, "ЦМ ИМА БРД (отдельная ИТ-система)", ha="center", fontsize=11, fontweight="bold", color="#92400e")
    box(ax, 7.3, 3.9, 1.0, 0.3, "Airflow N1", highlight=True)
    box(ax, 8.5, 3.9, 0.9, 0.3, "ClickHouse")
    box(ax, 9.6, 3.9, 0.7, 0.3, "NiFi")
    box(ax, 10.5, 3.9, 0.7, 0.3, "Kafka")
    box(ax, 8.5, 3.4, 0.9, 0.3, "Postgres")
    box(ax, 9.6, 3.4, 1.2, 0.3, "Grafana / S3")

    box(ax, 0.4, 0.5, 1.4, 0.65, "Все ДО")
    box(ax, 2.2, 0.5, 1.6, 0.65, "ГПН КЦ USOI")
    box(ax, 4.2, 0.5, 1.3, 0.65, "АДКУ")
    box(ax, 5.8, 0.5, 1.5, 0.65, "DUO Tech")
    box(ax, 7.8, 0.5, 1.8, 0.65, "Дата-платформа")

    arrow(ax, 1.8, 3.7, 2.1, 4.05, "#1B7A3A")
    arrow(ax, 3.5, 4.05, 7.3, 4.05, "#1B7A3A", lw=2.2)
    ax.text(5.4, 4.2, "вызов API AirFlow", ha="center", fontsize=7, color="#1B7A3A")
    arrow(ax, 4.85, 1.15, 2.3, 3.4, "#1B7A3A")
    arrow(ax, 1.7, 3.55, 7.3, 3.95, "#1B7A3A")
    ax.text(4.5, 3.75, "валидированная ТМ", ha="center", fontsize=7, color="#1B7A3A")
    arrow(ax, 7.8, 3.85, 3.9, 3.55, "#1B7A3A")
    ax.text(5.8, 3.65, "результаты", ha="center", fontsize=7, color="#1B7A3A")
    arrow(ax, 8.7, 1.15, 8.0, 3.85, "#C00000", style="--")

    ax.text(0.4, 0.12, "Бэклог ЕАРМ-2: API контракты, АКТС, CI/CD, МСЭ, документация | Итого 126,6 ч/д (−55% vs ЕАРМ-1)", fontsize=8, color="#1B7A3A")
    save(fig, "variant3_integration.png")


if __name__ == "__main__":
    variant1()
    variant2()
    variant3()
