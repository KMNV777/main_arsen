#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка схем и документов процесса выпуска релиза ЕАРМ (итоговая редакция).

Данные — scripts/process_data.py. Результат:
  * docs/drawio/10-release-process.drawio — 4 страницы:
      1. Процесс (последовательность и параллельность по зонам ответственности);
      2. Ведение релизных веток;
      3. Дорожная карта (этапы, ответственные, SLA);
      4. Jira и метрики;
  * docs/svg/10-release-process-N.svg — статичные превью;
  * docs/release-process.md, docs/release-process-review.md.

Запуск:  python3 scripts/build_release_process.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import process_data as D
from drawio_kit import Cell, Page, page_svg, table, write_drawio

ROOT = Path(__file__).resolve().parents[1]
DRAWIO = ROOT / "docs" / "drawio" / "10-release-process.drawio"
SVG_DIR = ROOT / "docs" / "svg"
DOC = ROOT / "docs" / "release-process.md"
DOC_REVIEW = ROOT / "docs" / "release-process-review.md"

META = {"service": "⟨СЕРВИС⟩", "direction": "⟨ЕАРМ1–6⟩", "version": "⟨27.x.y⟩"}

# Палитра Nedra: индиго #140093, лайм #CFF85E, голубой #AAC3E3, бирюзовый #89C9C7, оранжевый #FF7500 / #FDAB64
INDIGO, LIME, SKY, TEAL, ORANGE, ORANGE_L = "#140093", "#CFF85E", "#AAC3E3", "#89C9C7", "#FF7500", "#FDAB64"
RED, GRAY, DARK = "#D64545", "#7F7F8F", "#1B1B3A"
LANE_FILL = {"ВНП": "#EEEBFA", "RO": "#ECEAF9", "QA": "#F1F0FB", "DEV": "#F6F5FD", "РИ": "#EFEDFB", "ИБ": "#E4F3F2", "ГПН": "#E6F0FB"}
LANE_LBL = {"ВНП": "#C9C4F0", "RO": "#D3CEF3", "QA": "#D8D4F4", "DEV": "#E5E2F8", "РИ": "#CFC9F2", "ИБ": TEAL, "ГПН": SKY}
LANE_STROKE = {"ВНП": INDIGO, "RO": INDIGO, "QA": INDIGO, "DEV": INDIGO, "РИ": INDIGO, "ИБ": "#019390", "ГПН": "#4895EB"}


def header(p: Page, subtitle: str) -> None:
    p.add("text", 10, 6, p.width - 20, 34,
          [(f"Процесс выпуска релиза ЕАРМ · Сервис: %service% · Направление: %direction% · Релиз: %version%   |   {subtitle}", "b")],
          fs=15, attrs=dict(META), id="title", align="left", fc=INDIGO)


# ===========================================================================
# Страница 1. Процесс
# ===========================================================================
LANES = [  # ключ, подпись, высота, строки {имя: смещение центра}
    ("ВНП", "НЕДРА\nВНП", 130, {"a": 65}),
    ("RO", "НЕДРА\nRelease owner · РП", 230, {"a": 62, "b": 170}),
    ("QA", "НЕДРА\nQA", 130, {"a": 65}),
    ("DEV", "НЕДРА\nМейнтейнеры · фича-команды", 130, {"a": 65}),
    ("РИ", "НЕДРА\nРелиз-инженер", 230, {"a": 62, "b": 170}),
    ("ИБ", "ИБ ГПН-ЦР", 130, {"a": 65}),
    ("ГПН", "ГПН-ЦР\nDevOps · релиз-инженер сервиса · админы БД и брокеров · сервис", 320, {"a": 62, "b": 170, "c": 278}),
]
# шаг → (дорожка, строка, колонка)
POS: Dict[int, Tuple[str, str, int]] = {
    1: ("ВНП", "a", 0), 2: ("RO", "a", 1), 3: ("РИ", "a", 2), 4: ("DEV", "a", 3), 5: ("QA", "a", 4), 6: ("ВНП", "a", 5), 7: ("РИ", "a", 6),
    8: ("QA", "a", 7), 9: ("РИ", "a", 7), 10: ("RO", "a", 7), 11: ("RO", "b", 7), 12: ("DEV", "a", 8), 13: ("РИ", "b", 8), 14: ("QA", "a", 9),
    15: ("ИБ", "a", 10), 16: ("РИ", "a", 11), 17: ("РИ", "a", 12), 18: ("ИБ", "a", 13), 19: ("ИБ", "a", 14),
    20: ("ГПН", "a", 15), 21: ("ГПН", "b", 15), 22: ("ГПН", "c", 15), 23: ("RO", "a", 16), 24: ("ВНП", "a", 16), 25: ("RO", "a", 17),
    26: ("RO", "a", 18), 27: ("ГПН", "a", 19), 28: ("ГПН", "a", 20), 29: ("ГПН", "b", 20), 30: ("ГПН", "c", 20), 31: ("ВНП", "a", 21), 32: ("RO", "a", 22),
}
GAPS = (7, 8, 9, 15, 16, 17, 20, 21)   # перед этими колонками — место под планки fork/join
PITCH, NW, NH, GAP = 190, 155, 88, 55


def X(c: int) -> float:
    return 215 + c * PITCH + GAP * sum(1 for g in GAPS if g <= c)


def page_process() -> Page:
    W = int(X(22) + NW + 230)
    p = Page("1. Процесс", W, 1500)
    header(p, "последовательность и параллельность по зонам ответственности")
    LBL, PH_Y, PH_H = 150, 46, 40
    top: Dict[str, float] = {}
    y = PH_Y + PH_H
    for k, _, h, _ in LANES:
        top[k] = y
        y += h
    BOT = y
    p.height = int(BOT + 250)
    for k, lbl, h, _ in LANES:
        p.add("rect", 0, top[k], W, h, [], fill=LANE_FILL[k], stroke="#A0A0A0")
        p.add("rect", 0, top[k], LBL, h, [(lbl, "b")], fill=LANE_LBL[k], stroke="#A0A0A0", fs=11, fc=INDIGO)

    # фазы
    ph = [(LBL, X(2) - 18, "Подготовка", INDIGO, "#FFFFFF"),
          (X(2) - 18, X(7) - 80, "Спринт · 2 недели", LIME, INDIGO),
          (X(7) - 80, X(10) - 18, "Стабилизация на UAT (параллельно)", ORANGE_L, INDIGO),
          (X(10) - 18, X(15) - 70, "Релиз-борд (автоматизация)", INDIGO, "#FFFFFF"),
          (X(15) - 70, X(18) - 18, "PreProd", INDIGO, "#FFFFFF"),
          (X(18) - 18, W, "Прод и закрытие", INDIGO, "#FFFFFF")]
    for i, (a, b, t, fill, fc) in enumerate(ph):
        p.add("rect", a, PH_Y, b - a, PH_H, [(t, "b")], fill=fill, stroke="#FFFFFF", fs=12, fc=fc)
        if i:
            p.free([(a, PH_Y + PH_H), (a, BOT)], color="#9A9A9A", sw=1, dot=True, arrow=False)

    # зоны: спринт, стабилизация, релиз-борд
    p.add("rect", X(2) - 14, top["ВНП"], X(6) + 175 - (X(2) - 14), BOT - top["ВНП"], [], fill=LIME, stroke="#8AB800", dash=True, sw=1.2, opacity=14)
    p.text(X(2) - 8, top["ВНП"] + 2, 620, 16, [("СПРИНТ: старт → создание ветки → влитие задач → тестирование → демо → фича-фриз", "b")], fs=10, fc="#4F6600")
    p.add("rect", X(7) - 70, top["RO"], X(9) + NW + 22 - (X(7) - 70), top["ИБ"] - top["RO"], [], fill=ORANGE_L, stroke=ORANGE, dash=True, sw=1.5, opacity=18)
    p.text(X(7) - 64, top["RO"] + 2, 560, 16, [("ПАРАЛЛЕЛЬНО (между чёрными планками)", "b")], fs=10, fc="#B85500")
    p.add("rect", X(10) - 14, top["РИ"], X(14) + NW + 14 - (X(10) - 14), top["ГПН"] - top["РИ"], [], fill=None, stroke=ORANGE, dash=True, sw=2)
    p.text(X(10) - 8, top["РИ"] + 2, 760, 16, [("РЕЛИЗ-БОРД · автоматизированные шаги в зоне ответственности релиз-инженера НЕДРА", "b")], fs=10, fc="#B85500")

    cyy = {(k, r): top[k] + off for k, _, _, rows in LANES for r, off in rows.items()}
    nodes: Dict[int, Cell] = {}
    GRP_FILL = "#FFE9D2"
    for n, phs, name, a, doers, grp, sla, given, text in D.STEPS:
        lane, row, col = POS[n]
        others = [d for d in doers if d != a]
        l2 = "отв.: " + D.role_short(a)
        sla_s = D.sla_text(n).replace(" дн.", " дн").replace("в течение спринта", "спринт").replace("в последний день спринта", "посл. день")
        l3 = ("исп.: " + ", ".join(D.role_short(d) for d in others) + " · " if others else "") + "SLA " + sla_s
        fill = "#FFFFFF"
        if grp:
            fill = GRP_FILL
        if phs == 4:
            fill = "#F0FBD0"
        c = p.add("round", X(col), cyy[(lane, row)] - NH / 2, NW, NH, [(f"{n}  {name}", "b"), (l2, "s"), (l3, "s")],
                  id=f"s{n}", fill=fill, stroke=LANE_STROKE[lane], sw=1.3, fs=10.5, dash=(n == 18),
                  tooltip=f"{name}\nОтветственный: {D.role_name(a)}\nИсполнители: {', '.join(D.role_name(d) for d in doers)}\n{text}")
        nodes[n] = c

    def bar(before_col: int, y1: float, y2: float, ident: str) -> Cell:
        lo, hi = min(y1, y2), max(y1, y2)
        return p.add("bar", X(before_col) - 50, lo - 20, 8, hi - lo + 40, [], fill="#000000", stroke="#000000", id=ident)

    def cy(n: int) -> float:
        return nodes[n].cy

    start = p.add("ellipse", 171, cy(1) - 14, 28, 28, [], fill="#000000", stroke="#000000", id="start")
    end = p.add("ellipse", X(22) + NW + 40, cy(32) - 14, 28, 28, [], fill="#000000", stroke="#000000", id="end")
    F1 = bar(7, cy(10), cy(9), "F1")
    J1 = bar(8, cy(8), cy(13), "J1")
    J2 = bar(9, cy(14), cy(13), "J2")
    F2 = bar(15, cy(19), cy(22), "F2")
    S3 = bar(16, cy(24), cy(22), "S3")
    J4 = bar(17, cy(24), cy(23), "J4")
    F4 = bar(20, cy(28), cy(30), "F4")
    J5 = bar(21, cy(31), cy(30), "J5")

    def fr(b: Cell, yy: float) -> float:
        return (yy - b.y) / b.h

    L = p.link
    # --- подготовка и спринт
    L(start, "R", nodes[1], "L")
    L(nodes[1], "R", nodes[2], "T", "hv")
    L(nodes[2], "R", nodes[3], "T", "hv")
    L(nodes[3], "R", nodes[4], "B", "hv")
    L(nodes[4], "R", nodes[5], "B", "hv")
    L(nodes[5], "R", nodes[6], ("B", 0.3), "hv")
    nxt = p.add("round", X(6), cy(6) - 34, 150, 68, [("Не принято и не успели", "b"), ("→ следующий релиз (= следующий спринт)", "s")],
                fill="#FFE9D2", stroke=ORANGE, sw=1.5, fs=10)
    L(nodes[6], "R", nxt, "L", dash=True, color=ORANGE)
    L(nodes[6], ("B", 0.7), nodes[7], "L", "vh")
    # --- стабилизация
    L(nodes[7], "R", F1, ("L", fr(F1, cy(7))))
    for t in (10, 11, 8, 9):
        L(F1, ("R", fr(F1, cy(t))), nodes[t], "L")
    L(nodes[8], "R", J1, ("L", fr(J1, cy(8))))
    L(nodes[9], "R", J1, ("L", fr(J1, cy(9))))
    L(J1, ("R", fr(J1, cy(12))), nodes[12], "L")
    L(J1, ("R", fr(J1, cy(13))), nodes[13], "L")
    L(nodes[12], "R", J2, ("L", fr(J2, cy(12))))
    L(nodes[13], "R", J2, ("L", fr(J2, cy(13))))
    L(J2, ("R", fr(J2, cy(14))), nodes[14], "L")
    L(nodes[10], "R", nodes[15], ("T", 0.7), "hv", dash=True, color=GRAY, label="TOML → аудит", lt=0.5)
    L(nodes[14], "R", nodes[15], ("T", 0.3), "hv")
    L(nodes[14], "B", nodes[12], "T", "via", via=[(nodes[14].cx, top["DEV"] + 8), (nodes[12].cx, top["DEV"] + 8)],
      color=RED, dash=True, label="критические дефекты → фикс", lt=0.5)
    # --- релиз-борд
    L(nodes[15], "R", nodes[16], "B", "hv")
    L(nodes[16], "R", nodes[17], "L")
    L(nodes[17], "R", nodes[18], "T", "hv")
    L(nodes[18], "R", nodes[19], "L")
    L(nodes[17], ("B", 0.85), nodes[19], "T", "vhv", mid=top["ИБ"] + 12, dash=True, color=GRAY, label="ПСИ не нужен — пропуск", lt=0.5)
    L(nodes[15], "L", nodes[13], "B", "hv", color=RED, dash=True, label="замечания аудита", lt=0.5)
    # --- PreProd
    L(nodes[19], "R", F2, ("L", fr(F2, cy(19))))
    for t in (20, 21, 22):
        L(F2, ("R", fr(F2, cy(t))), nodes[t], "L")
        L(nodes[t], "R", S3, ("L", fr(S3, cy(t))))
    L(nodes[11], "R", S3, ("L", fr(S3, cy(11))), dash=True, color=GRAY, label="тест-план в ТестОпс ГПН-ЦР", lt=0.55)
    L(S3, ("R", fr(S3, cy(23))), nodes[23], "L")
    L(S3, ("R", fr(S3, cy(24))), nodes[24], "L")
    L(nodes[23], "R", J4, ("L", fr(J4, cy(23))))
    L(nodes[24], "R", J4, ("L", fr(J4, cy(24))))
    L(J4, ("R", fr(J4, cy(25))), nodes[25], "L")
    hf = p.add("round", X(17), cyy[("РИ", "a")] - 44, 160, 88, [("Hotfix: тот же процесс", "b"), ("критические дефекты PreProd → hotfix; релиз всё равно идёт в Прод", "s")],
               fill="#FFD2A6", stroke=ORANGE, sw=1.5, fs=10)
    L(nodes[25], "B", hf, "T", color=RED, dash=True, label="критические → hotfix", lt=0.25)
    # --- Прод
    L(nodes[25], "R", nodes[26], "L")
    L(nodes[26], "R", nodes[27], "T", "hv")
    L(nodes[27], "R", F4, ("L", fr(F4, cy(27))))
    for t in (28, 29, 30):
        L(F4, ("R", fr(F4, cy(t))), nodes[t], "L")
        L(nodes[t], "R", J5, ("L", fr(J5, cy(t))))
    L(J5, ("R", fr(J5, cy(31))), nodes[31], "L")
    L(nodes[31], "R", nodes[32], "T", "hv")
    L(nodes[32], "R", end, "L")

    # --- легенда и пояснения
    ly = BOT + 18
    p.add("rect", 0, BOT + 6, W, 210, [], fill="#FFFFFF", stroke="#A0A0A0")
    p.text(10, ly, 300, 18, [("Как читать схему", "b")], fs=12, fc=INDIGO)
    items = [("round", "#FFFFFF", INDIGO, False, "этап: в дорожке — ответственный; в подписи — исполнители и SLA"),
             ("round", "#FFE9D2", INDIGO, False, "параллельные этапы (между чёрными планками)"),
             ("round", "#F0FBD0", INDIGO, False, "автоматизированный шаг релиз-борда"),
             ("round", "#FFFFFF", INDIGO, True, "шаг, который пропускается, если не нужен (ПСИ ИБ)")]
    for i, (k, fl, st, ds, txt) in enumerate(items):
        yy = ly + 28 + i * 28
        p.add(k, 10, yy - 8, 34, 20, [], fill=fl, stroke=st, dash=ds, sw=1.4)
        p.text(52, yy - 6, 520, 18, [(txt, "n")], fs=10)
    p.free([(640, ly + 28), (700, ly + 28)], color=RED, dash=True)
    p.text(708, ly + 20, 560, 18, [("возврат на доработку", "n")], fs=10)
    p.free([(640, ly + 56), (700, ly + 56)], color=GRAY, dash=True)
    p.text(708, ly + 48, 560, 18, [("зависимость (нужно к началу следующего этапа)", "n")], fs=10)
    p.free([(640, ly + 84), (700, ly + 84)], color=ORANGE, dash=True)
    p.text(708, ly + 76, 560, 18, [("переход в следующий релиз / hotfix", "n")], fs=10)
    p.text(1300, ly, 3600, 190, [
        ("Основные правила", "b"),
        ("• Нумерация этапов сквозная, 1–32. Ветки вынесены на схему 2; даты и SLA по этапам — на схеме 3.", "n"),
        ("• Спринт 2 недели: создание релизной ветки в первый день → влитие задач → тестирование → демо (проводит QA, принимает ВНП) → фича-фриз в конце спринта. Что не успели — в следующий релиз.", "n"),
        ("• После фича-фриза параллельно идут регресс на UAT, скан уязвимостей, подготовка TOML и импорт тест-плана; затем параллельно устраняются баги и уязвимости; затем Smoke UAT.", "n"),
        ("• Релиз-борд (аудит → выкатка на UAT → функциональное тестирование → ПСИ ИБ → согласование трансфера) — в зоне релиз-инженера НЕДРА; ПСИ ИБ пропускается сразу, если не нужен.", "n"),
        ("• Go/No-Go нет: после регресса на PreProd релиз идёт в Прод; правки — только на уровне helm, критические дефекты — в hotfix. После деплоя Smoke PROD, БД и брокеры идут параллельно.", "n"),
        ("• Один этап — один ответственный; исполнители — только перечисленные роли, чужую работу никто не выполняет.", "n"),
    ], fs=10)
    return p


# ===========================================================================
# Страница 2. Ведение релизных веток
# ===========================================================================
def page_branches() -> Page:
    W, H = 2200, 1000
    p = Page("2. Ведение релизных веток", W, H)
    header(p, "ведение релизных веток: от старта спринта до фича-фриза")
    SPR = [(180, 780, "Спринт N · 2 недели"), (780, 1380, "Спринт N+1 · 2 недели"), (1380, 1980, "Спринт N+2 · 2 недели")]
    for i, (a, b, t) in enumerate(SPR):
        p.add("rect", a, 56, b - a, 34, [(t, "b")], fill=INDIGO, stroke="#FFFFFF", fs=12, fc="#FFFFFF")
        p.add("rect", a, 90, b - a, 520, [], fill="#F4F6FB" if i % 2 else "#ECEAF9", stroke="#C9D2E6", sw=1)
    p.text(20, 118, 150, 40, [("master", "b")], fs=13, fc=INDIGO)
    my = 140
    p.free([(170, my), (2100, my)], sw=4, arrow=False, color=INDIGO)

    def release(y: float, x0: float, xs: float, xend: float, label: str, col: str) -> None:
        p.free([(x0, my), (x0 + 30, y), (xs, y)], sw=3.5, color=col, arrow=False)
        p.add("ellipse", x0 + 22, y - 8, 16, 16, [], fill="#FFFFFF", stroke=col, sw=2)
        for i in range(1, 5):
            p.add("ellipse", x0 + 60 + i * 100 - 5, y - 5, 10, 10, [], fill=col, stroke=col)
        p.add("bar", xs - 4, y - 18, 8, 36, [], fill=RED, stroke=RED)
        p.free([(xs, y), (xend, y)], sw=4, color=col, arrow=False, dash=True)
        p.add("ellipse", xend + 6, y - 15, 30, 30, [("Прод", "b")], fill=LIME, stroke=INDIGO, sw=2, fs=8)
        p.text(x0 + 70, y - 36, 420, 18, [(label, "b")], fs=11, fc=col)

    y1, y2, y3 = 250, 400, 550
    release(y1, 180, 770, 1600, "release/<сервис>/N", INDIGO)
    release(y2, 780, 1370, 2050, "release/<сервис>/N+1", "#019390")
    release(y3, 1380, 1970, 2150, "release/<сервис>/N+2", "#4895EB")
    p.text(185, y1 + 22, 130, 30, [("старт спринта: сбор ветки", "n")], fs=9, fc=DARK)
    p.text(300, y1 + 22, 180, 18, [("влитие задач", "n")], fs=9, fc=DARK)
    p.text(480, y1 + 22, 260, 18, [("тестирование и демо (QA · ВНП)", "n")], fs=9, fc=DARK)
    p.text(690, y1 - 58, 180, 30, [("фича-фриз\n(конец спринта)", "b")], fs=9, fc=RED)
    p.text(800, y1 + 14, 780, 18, [("стабилизация и выкат: регресс UAT → устранение → Smoke UAT → релиз-борд → PreProd → деплой в Прод", "n")], fs=9, fc=DARK)
    p.free([(770, y1 + 8), (800, y2 - 20)], color=ORANGE, dash=True, sw=2, arrow=True)
    p.text(808, y1 + 48, 380, 44, [("не принято и не успели →\nследующий релиз (= следующий спринт)", "b")], fs=10, fc="#B85500")
    p.free([(1370, y2 + 8), (1400, y3 - 20)], color=ORANGE, dash=True, sw=2, arrow=True)
    p.text(1408, y2 + 48, 380, 44, [("не принято и не успели →\nследующий релиз (= следующий спринт)", "b")], fs=10, fc="#B85500")
    hy = 600
    p.free([(1606, y1 + 16), (1640, hy), (1900, hy)], sw=2.5, color=RED, arrow=True)
    p.text(1650, hy - 22, 520, 18, [("hotfix/* — от ветки Прода; тот же процесс", "b")], fs=10, fc=RED)
    p.text(180, 625, 1900, 20, [("Допускается вести несколько релизных веток параллельно: ветка N+1 создаётся на старте следующего спринта, пока ветка N проходит стабилизацию и выкат.", "b")], fs=11, fc=INDIGO)
    p.text(180, 655, 1950, 20, [("Соответствие этапам схемы 1:  3 — сбор ветки · 4 — влитие задач · 5 — тестирование · 6 — демо и приёмка · 7 — фича-фриз · 8–14 — стабилизация на UAT · 15–19 — релиз-борд · 20–25 — PreProd · 27 — деплой в Прод", "n")], fs=10, fc=DARK)
    rows = [["Шаг", "Правило"]] + [[a, b] for a, b in D.BRANCH_RULES]
    table(p, 20, 700, [220, 1700], rows, fs=11)
    return p


# ===========================================================================
# Страница 3. Дорожная карта
# ===========================================================================
def page_roadmap() -> Page:
    sched0 = D.schedule(False)
    sched1 = D.schedule(True)
    W = 2200
    p = Page("3. Дорожная карта", W, 300 + 40 * len(D.STAGES))
    header(p, "дорожная карта релизного цикла: этапы, ответственные, SLA")
    cols = [430, 380, 150]
    x0 = 20 + sum(cols) + 20
    PX = 22.0
    y = 70
    cx = 20
    for i, h in enumerate(["Этап", "Ответственный", "SLA"]):
        p.add("rect", cx, y, cols[i], 40, [(h, "b")], fill=INDIGO, stroke="#FFFFFF", fs=11, fc="#FFFFFF")
        cx += cols[i]
    total = int(max(v[1] for v in sched1.values())) + 2
    for d in range(0, total, 5):
        p.add("rect", x0 + d * PX, y, 5 * PX, 40, [(f"день {d}", "b")], fill=INDIGO if (d // 5) % 2 == 0 else "#2A1FA8", stroke="#FFFFFF", fs=10, fc="#FFFFFF")
    ry = y + 40
    colr = {"НЕДРА": INDIGO, "ИБ": "#019390", "ГПН-ЦР": "#4895EB"}
    for i, (name, steps, resp, sla, contour) in enumerate(D.STAGES):
        h = 40
        fill = "#FFFFFF" if i % 2 == 0 else "#F4F6FB"
        cx = 20
        for j, t in enumerate((name, resp, sla)):
            p.add("rect", cx, ry, cols[j], h, [(t, "b" if j == 0 else "n")], fill=fill, stroke="#C9D2E6", fs=10, align="left", fc=DARK)
            cx += cols[j]
        p.add("rect", x0, ry, total * PX, h, [], fill=fill, stroke="#E4E8F2", sw=0.5)
        s0 = min(sched0[n][0] for n in steps)
        e0 = max(sched0[n][1] for n in steps)
        if steps == [18]:
            s0, e0 = sched1[18][0], sched1[18][1]
            p.add("rect", x0 + s0 * PX, ry + 8, (e0 - s0) * PX, h - 16, [("если нужен · до 5 дн.", "n")], fill="#FFFFFF", stroke=colr[contour], dash=True, sw=1.5, fs=9, fc=DARK)
        else:
            w = max((e0 - s0) * PX, 10)
            is_sprint = steps[0] == 4
            lab = f"{int(e0 - s0)} дн." if e0 > s0 else "в день"
            p.add("rect", x0 + s0 * PX, ry + 8, w, h - 16, [(lab, "b")] if w > 50 else [], fill=LIME if is_sprint else colr[contour],
                  stroke="#FFFFFF", fs=9, fc=INDIGO if is_sprint else "#FFFFFF")
        ry += h
    for d in range(0, total + 1, 5):
        p.free([(x0 + d * PX, y + 40), (x0 + d * PX, ry)], color="#B7BFD6", sw=0.8, dot=True, arrow=False)
    p.text(20, ry + 14, W - 40, 60, [
        (f"Срок релиза по SLA: около {D.total_days(False):g} рабочих дней ({D.total_days(False) / 5:.1f} недели) без ПСИ ИБ и около {D.total_days(True):g} ({D.total_days(True) / 5:.1f}) с ПСИ ИБ. Спринт — 10 рабочих дней.", "b"),
        ("Один этап — один ответственный; исполнители указаны в таблице этапов (схема 1 и документ). Цвета: НЕДРА — индиго, ИБ — бирюзовый, ГПН-ЦР — голубой, спринт — лайм.", "n"),
    ], fs=11, fc=DARK)
    return p


# ===========================================================================
# Страница 4. Jira и метрики
# ===========================================================================
def page_jira() -> Page:
    W, H = 1500, 1000
    p = Page("4. Jira и метрики", W, H)
    header(p, "учёт в Jira и метрики релиза")
    p.text(20, 52, 800, 22, [("Как этапы ложатся в Jira", "b")], fs=14, fc=INDIGO)
    b1 = p.add("round", 20, 84, 320, 120, [("Релизный Epic (квартал)", "b"), ("обязательный объём спринтов; в нём — релизные работы", "n")],
               fill="#E4E1F7", stroke=INDIGO, fs=11, align="left", valign="top")
    b2 = p.add("round", 400, 84, 320, 120, [("Fix Version (релиз)", "b"), ("состав релиза: только Story и Bug; источник строки календаря", "n")],
               fill="#FFE9D2", stroke=ORANGE_L, fs=11, align="left", valign="top")
    b3 = p.add("round", 780, 84, 340, 120, [("Задача этапа", "b"), ("по одной на каждый этап (1–32): оценка, исполнитель, результат; возврат — новая задача", "n")],
               fill="#F0FBD0", stroke="#8AB800", fs=11, align="left", valign="top")
    b4 = p.add("round", 1180, 84, 300, 120, [("Подзадача сервиса", "b"), ("поле «Сервис» — для этапов по сервису", "n")],
               fill="#E6F0FB", stroke="#4895EB", fs=11, align="left", valign="top")
    p.link(b1, "R", b2, "L")
    p.link(b2, "R", b3, "L")
    p.link(b3, "R", b4, "L")
    st = [p.add("round", 20 + i * 230, 250, 150, 50, [(t, "b")], fill=f, stroke=s, fs=11)
          for i, (t, f, s) in enumerate([("Ожидает", "#F4F6FB", GRAY), ("В работе", "#FFE9D2", ORANGE_L), ("Готово", "#F0FBD0", "#8AB800")])]
    p.link(st[0], "R", st[1], "L", label="старт")
    p.link(st[1], "R", st[2], "L", label="финиш")
    p.text(740, 252, 740, 50, [("Старт и финиш задачи этапа — источник времени этапа и ожидания. Календарь и паспорт в Confluence — витрина, не источник метрик.", "n")], fs=10, fc=DARK)
    p.text(20, 330, 800, 22, [("Метрики", "b")], fs=14, fc=INDIGO)
    rows = [["Метрика", "Влияние", "Формула", "Ответственный"]] + [list(m) for m in D.METRICS]
    yb = table(p, 20, 360, [300, 380, 520, 260], rows, fs=11)
    p.height = int(yb + 40)
    return p


# ===========================================================================
# Документы
# ===========================================================================
def build_doc() -> str:
    import sections as S
    o = ["# Процесс выпуска релиза ЕАРМ — итоговая редакция", "",
         "> Схемы: [`drawio/10-release-process.drawio`](drawio/10-release-process.drawio) (4 страницы: процесс, ветки, дорожная карта, Jira и метрики). "
         "Единый отчёт для ревью — [`release-process-full.html`](release-process-full.html). Файлы генерирует `scripts/build_release_process.py`.", "",
         "## Принятые решения", "",
         "- Ветка — от master на старте спринта; допускается несколько веток параллельно. Фича-фриз — в конце спринта; не успели — в следующий релиз (спринт). Scope freeze нет.",
         "- Демо проводит QA, принимает ВНП.", "- Релиз-борд: аудит → выкатка на UAT → функциональное тестирование → ПСИ ИБ → согласование трансфера на ПРОД (ЗО релиз-инженера НЕДРА).",
         "- Go/No-Go нет; критические дефекты — в hotfix; hotfix — тот же процесс.", "- Smoke PROD, БД и брокеры — параллельно.", "",
         "## Этапы", "", "| № | Этап | Ответственный | Исполнители | SLA |", "|---|---|---|---|---|"]
    for n, ph, name, a, doers, grp, sla, given, text in D.STEPS:
        o.append(f"| {n} | {name}{' (параллельно)' if grp else ''} | {D.role_name(a)} | {S.doers_text(n)} | {D.sla_text(n)}{'' if given else ' *'} |")
    o += ["", "\\* SLA предложен.", "", "## Описание этапов", ""]
    for n, ph, name, a, doers, grp, sla, given, text in D.STEPS:
        o.append(f"**{n}. {name}** — {D.sla_text(n)}. {text}")
        o.append("")
    o += ["## Критический путь", "", D.critical_path_text(), "", "## Решения", "", "| Шаг | Ответственный |", "|---|---|"]
    o += [f"| {a} | {b} |" for a, b in D.DECISIONS]
    o += ["", "## Метрики", "", "| Метрика | Влияние | Формула | Ответственный |", "|---|---|---|---|"]
    o += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in D.METRICS]
    o += ["", "## Нужно подтвердить", ""] + [f"- {x}" for x in D.CONFIRM]
    return "\n".join(o) + "\n"


def build_resolved_doc() -> str:
    o = ["# Расхождения документов и как они устранены", "",
         "Сверены: эталонный процесс (Confluence), Релизная политика ЕАРМ, ДК выпуска релизов, «Доступы для релизов», «Менеджмент команд разработки», карточки ролевой модели. "
         "Все расхождения учтены в итоговой схеме — [`release-process.md`](release-process.md).", "",
         "| Расхождение | Как устранено в итоговой схеме | Документ |", "|---|---|---|"]
    o += [f"| {a} | {b} | {c} |" for a, b, c in D.RESOLVED]
    o += ["", "## Остаётся подтвердить", ""] + [f"- {x}" for x in D.CONFIRM]
    return "\n".join(o) + "\n"


# ===========================================================================
# HTML-отчёт
# ===========================================================================
def build_html(pages: List[Page], extra=None, trz=None, title: str = "Процесс выпуска релиза ЕАРМ", comments: bool = False) -> str:
    import html_theme as TH
    import sections as S
    from html import escape as e

    titles = ["1. Процесс", "2. Ветки", "3. Дорожная карта", "4. Jira и метрики"]
    figs = []
    for i, pg in enumerate(pages, 1):
        sv = page_svg(pg)
        for k, v in META.items():
            sv = sv.replace(f"%{k}%", v)
        sv = sv.replace('id="m', f'id="f{i}m').replace("url(#m", f"url(#f{i}m")
        figs.append(f'<figure id="fig{i}" data-w="{pg.width}"><div class="zoom"><button data-z="0.25">25%</button><button data-z="0.5">50%</button>'
                    f'<button data-z="1">100%</button><button data-z="fit">По ширине</button><span class="muted">{e(titles[i - 1])}</span></div>'
                    f'<div class="canvas">{sv}</div></figure>')
    sections = [
        ("overview", "Обзор", S.overview_html()),
        ("diagrams", "Схемы", "<p class='muted'>Исходник — <code>docs/drawio/10-release-process.drawio</code>; здесь статичные копии с масштабированием.</p>" + "".join(figs)),
        ("steps", "Этапы: ответственные и SLA", S.registry_html()),
        ("roadmap", "Дорожная карта", "<p>Этапы, ответственные и SLA (схема 3):</p>" + S.roadmap_html()),
        ("text", "Описание этапов и критический путь", S.sla_html()),
        ("branches", "Ведение релизных веток", S.branches_html()),
        ("roles", "Роли: кто за что отвечает", S.roles_text_html()),
        ("decisions", "Кто принимает решения", S.decisions_html()),
        ("jira", "Jira и Confluence", S.jira_html()),
        ("metrics", "Метрики", S.metrics_html()),
        ("resolved", "Расхождения и как они устранены", S.resolved_html()),
        ("trz", "ТРЗ и FTE по ролям", trz or "<p>См. калькулятор.</p>"),
        ("open", "Нужно подтвердить", S.confirm_html()),
    ]
    if extra:
        sections = sections + list(extra)
    nav = "".join(f'<a href="#{i}">{e(t)}</a>' for i, t, _ in sections)
    cm = lambda i: (f'<div class="cm"><label for="cm-{i}">Ваши правки к разделу</label><textarea id="cm-{i}" data-k="{i}" rows="3" placeholder="Что изменить, добавить, убрать…"></textarea></div>' if comments else "")
    body = "".join(f'<section id="{i}"><h2>{e(t)}</h2>{c}{cm(i)}</section>' for i, t, c in sections)
    fb = ('<div class="fb"><span>Правок в разделах: <b id="fb-n">0</b></span><button id="fb-dl">Скачать правки (.txt)</button>'
          '<button id="fb-cp">Копировать правки</button><span class="muted">Правки сохраняются в браузере; перед отправкой нажмите «Скачать» или «Копировать».</span></div>') if comments else ""
    js = TH.JS_FIG + (TH.JS_FEEDBACK if comments else "")
    return (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(title)}</title><style>{TH.CSS}</style></head><body>'
            f'<header class="top"><h1>{e(title)}</h1><div class="muted">Схема, этапы, роли, SLA, метрики, ТРЗ и FTE · сгенерировано <code>scripts/build_release_process.py</code></div></header>'
            f'<nav><div class="in">{nav}</div></nav><main>{body}</main>{fb}<script>{js}</script></body></html>')


def main() -> None:
    pages = [page_process(), page_branches(), page_roadmap(), page_jira()]
    DRAWIO.parent.mkdir(parents=True, exist_ok=True)
    write_drawio(pages, str(DRAWIO))
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    for old in SVG_DIR.glob("10-release-process-*.svg"):
        old.unlink()
    for i, pg in enumerate(pages, 1):
        svg = page_svg(pg)
        for k, v in META.items():
            svg = svg.replace(f"%{k}%", v)
        (SVG_DIR / f"10-release-process-{i}.svg").write_text(svg, encoding="utf-8")
    DOC.write_text(build_doc(), encoding="utf-8")
    DOC_REVIEW.write_text(build_resolved_doc(), encoding="utf-8")
    print("OK:", DRAWIO, f"steps={len(D.STEPS)}")


if __name__ == "__main__":
    main()
