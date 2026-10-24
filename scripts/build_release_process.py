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
LANE_FILL = {"СВК": "#E6F0FB", "ВНП": "#EEEBFA", "RO": "#ECEAF9", "QA": "#F1F0FB", "DEV": "#F6F5FD", "РИ": "#EFEDFB", "ИБ": "#E4F3F2", "ГПН": "#E6F0FB"}
LANE_LBL = {"СВК": SKY, "ВНП": "#C9C4F0", "RO": "#D3CEF3", "QA": "#D8D4F4", "DEV": "#E5E2F8", "РИ": "#CFC9F2", "ИБ": TEAL, "ГПН": SKY}
LANE_STROKE = {"СВК": "#4895EB", "ВНП": INDIGO, "RO": INDIGO, "QA": INDIGO, "DEV": INDIGO, "РИ": INDIGO, "ИБ": "#019390", "ГПН": "#4895EB"}


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
    ("DEV", "НЕДРА\nМейнтейнеры · фича-команды", 230, {"a": 62, "b": 170}),
    ("РИ", "НЕДРА\nРелиз-инженер\n(инициация и уведомления)", 230, {"a": 62, "b": 170}),
    ("ИБ", "ГПН-ЦР\nИБ ГПН", 130, {"a": 65}),
    ("ГПН", "ГПН-ЦР\nDevOps · релиз-инженер ГПН · админы БД и брокеров", 320, {"a": 62, "b": 170, "c": 278}),
    ("СВК", "ГПН-ЦР\nТестировщик сервиса", 130, {"a": 65}),
]
_P = {  # ключ этапа → (дорожка, строка, колонка)
    "prior": ("ВНП", "a", 0), "plan": ("RO", "b", 1), "ticket": ("RO", "a", 2), "confirm": ("ВНП", "a", 3),
    "dev": ("DEV", "a", 4), "scan": ("DEV", "b", 4), "test": ("QA", "a", 4), "notes": ("RO", "b", 4),
    "demo": ("ВНП", "a", 5), "exclude": ("RO", "b", 6), "freeze": ("РИ", "a", 7),
    "regress": ("QA", "a", 8), "gate": ("РИ", "b", 8), "toml": ("RO", "a", 8), "testplan": ("RO", "b", 8),
    "fix": ("DEV", "a", 9), "smoke": ("QA", "a", 10),
    "init": ("РИ", "a", 11), "audit": ("ИБ", "a", 12), "uatdeploy": ("ГПН", "a", 13), "functest": ("ГПН", "a", 14), "psi": ("ИБ", "a", 15), "transfer": ("ИБ", "a", 16),
    "notify": ("РИ", "a", 17), "preprod": ("ГПН", "a", 18), "db": ("ГПН", "b", 18), "brokers": ("ГПН", "c", 18), "pregress": ("СВК", "a", 19), "preport": ("СВК", "a", 20),
    "orgnotify": ("RO", "a", 21), "prod": ("ГПН", "a", 22), "smokeprod": ("СВК", "a", 23), "dbpost": ("ГПН", "b", 23), "brpost": ("ГПН", "c", 23), "comm": ("ВНП", "a", 24), "close": ("RO", "a", 25),
}
POS: Dict[int, Tuple[str, str, int]] = {D.ID[k]: v for k, v in _P.items()}
GAPS = (4, 5, 8, 9, 18, 19, 23, 24)   # перед этими колонками — место под планки fork/join
PITCH, NW, NH, GAP = 190, 155, 88, 55


def X(c: int) -> float:
    return 215 + c * PITCH + GAP * sum(1 for g in GAPS if g <= c)


def page_process() -> Page:
    I = D.ID
    W = int(X(25) + NW + 230)
    p = Page("1. Процесс", W, 1500)
    header(p, "последовательность и параллельность по зонам ответственности")
    LBL, PH_Y, PH_H = 150, 46, 40
    top: Dict[str, float] = {}
    y = PH_Y + PH_H
    for k, _, h, _ in LANES:
        top[k] = y
        y += h
    BOT = y
    p.height = int(BOT + 260)
    for k, lbl, h, _ in LANES:
        p.add("rect", 0, top[k], W, h, [], fill=LANE_FILL[k], stroke="#A0A0A0")
        p.add("rect", 0, top[k], LBL, h, [(lbl, "b")], fill=LANE_LBL[k], stroke="#A0A0A0", fs=11, fc=INDIGO)

    ph = [(LBL, X(4) - 70, "Планирование спринта", INDIGO, "#FFFFFF"),
          (X(4) - 70, X(8) - 80, "Спринт · 2 недели", LIME, INDIGO),
          (X(8) - 80, X(11) - 18, "Стабилизация на UAT", ORANGE_L, INDIGO),
          (X(11) - 18, X(17) - 18, "Релиз-борд (контур ГПН)", INDIGO, "#FFFFFF"),
          (X(17) - 18, X(21) - 18, "PreProd", INDIGO, "#FFFFFF"),
          (X(21) - 18, W, "Прод и закрытие", INDIGO, "#FFFFFF")]
    for i, (a, b, t, fill, fc) in enumerate(ph):
        p.add("rect", a, PH_Y, b - a, PH_H, [(t, "b")], fill=fill, stroke="#FFFFFF", fs=12, fc=fc)
        if i:
            p.free([(a, PH_Y + PH_H), (a, BOT)], color="#9A9A9A", sw=1, dot=True, arrow=False)

    # зоны
    p.add("rect", X(4) - 64, top["ВНП"], X(7) + NW + 14 - (X(4) - 64), BOT - top["ВНП"], [], fill=LIME, stroke="#8AB800", dash=True, sw=1.2, opacity=14)
    p.text(X(4) - 58, top["ВНП"] + 2, 900, 16, [("СПРИНТ: параллельно разработка · скан в CI · тестирование · release notes → демо → вывод не принятых → фича-фриз (тег)", "b")], fs=10, fc="#4F6600")
    p.add("rect", X(8) - 70, top["RO"], NW + 92, top["ИБ"] - top["RO"], [], fill=ORANGE_L, stroke=ORANGE, dash=True, sw=1.5, opacity=18)
    p.text(X(8) - 64, top["RO"] + 2, 300, 16, [("ПАРАЛЛЕЛЬНО ДРУГ ДРУГУ", "b")], fs=10, fc="#B85500")
    p.add("rect", X(11) - 14, top["РИ"], X(16) + NW + 14 - (X(11) - 14), top["ГПН"] + 120 - top["РИ"], [], fill=None, stroke=ORANGE, dash=True, sw=2)
    p.text(X(11) - 8, top["ГПН"] + 100, 1100, 16, [("РЕЛИЗ-БОРД В ПОРЯДКЕ БОРДА · НЕДРА только инициирует (запуск и документ для ПСИ), шаги выполняет контур ГПН", "b")], fs=10, fc="#B85500")
    p.add("rect", X(18) - 70, top["ГПН"], NW + 92, top["СВК"] - top["ГПН"], [], fill=ORANGE_L, stroke=ORANGE, dash=True, sw=1.5, opacity=18)
    p.text(X(18) - 64, top["ГПН"] + 2, 200, 16, [("ПАРАЛЛЕЛЬНО", "b")], fs=10, fc="#B85500")
    p.add("rect", X(23) - 70, top["ГПН"], NW + 92, top["СВК"] + 130 - top["ГПН"], [], fill=ORANGE_L, stroke=ORANGE, dash=True, sw=1.5, opacity=18)
    p.text(X(23) - 64, top["ГПН"] + 2, 200, 16, [("ПАРАЛЛЕЛЬНО", "b")], fs=10, fc="#B85500")

    cyy = {(k, r): top[k] + off for k, _, _, rows in LANES for r, off in rows.items()}
    nodes: Dict[int, Cell] = {}
    GRP_FILL = "#FFE9D2"
    for n, phs, name, a, doers, grp, sla, given, text in D.STEPS:
        lane, row, col = POS[n]
        others = [d for d in doers if d != a]
        l2 = "отв.: " + D.role_short(a)
        sla_s = D.sla_text(n).replace(" дн.", " дн").replace("в течение спринта", "спринт").replace("в последний день спринта", "посл. день").replace("в день демо", "в день демо")
        l3 = ("исп.: " + ", ".join(D.role_short(d) for d in others) + " · " if others else "") + "SLA " + sla_s
        fill = "#FFFFFF"
        if grp:
            fill = GRP_FILL
        if phs == 4:
            fill = "#F0FBD0"
        c = p.add("round", X(col), cyy[(lane, row)] - NH / 2, NW, NH, [(f"{n}  {name}", "b"), (l2, "s"), (l3, "s")],
                  id=f"s{n}", fill=fill, stroke=LANE_STROKE[lane], sw=1.3, fs=10, dash=(n == I["psi"]),
                  tooltip=f"{name}\nОтветственный: {D.role_name(a)}\nИсполнители: {', '.join(D.role_name(d) for d in doers)}\n{text}")
        nodes[n] = c

    def bar(before_col: int, y1: float, y2: float, ident: str) -> Cell:
        lo, hi = min(y1, y2), max(y1, y2)
        return p.add("bar", X(before_col) - 50, lo - 20, 8, hi - lo + 40, [], fill="#000000", stroke="#000000", id=ident)

    N = {k: nodes[I[k]] for k in I}
    cy = lambda k: N[k].cy
    start = p.add("ellipse", 171, cy("prior") - 14, 28, 28, [], fill="#000000", stroke="#000000", id="start")
    end = p.add("ellipse", X(25) + NW + 40, cy("close") - 14, 28, 28, [], fill="#000000", stroke="#000000", id="end")
    F0 = bar(4, cy("confirm"), max(cy(k) for k in ("dev", "scan", "test", "notes")), "F0")
    J0 = bar(5, cy("demo"), max(cy(k) for k in ("dev", "scan", "test")), "J0")
    F1 = bar(8, cy("toml"), cy("gate"), "F1")
    J1 = bar(9, cy("regress"), cy("gate"), "J1")
    F2 = bar(18, cy("notify"), cy("brokers"), "F2")
    J2 = bar(19, cy("preprod"), cy("pregress"), "J2")
    F3 = bar(23, cy("prod"), cy("smokeprod"), "F3")
    J3 = bar(24, cy("comm"), cy("smokeprod"), "J3")

    def fr(b: Cell, yy: float) -> float:
        return min(max((yy - b.y) / b.h, 0.02), 0.98)

    L = p.link
    L(start, "R", N["prior"], "L")
    L(N["prior"], "R", N["plan"], "T", "hv")
    L(N["plan"], "R", N["ticket"], "B", "hv")
    L(N["ticket"], "R", N["confirm"], "B", "hv")
    L(N["confirm"], "R", F0, ("L", fr(F0, cy("confirm"))))
    for k in ("dev", "scan", "test", "notes"):
        L(F0, ("R", fr(F0, cy(k))), N[k], "L")
    for k in ("dev", "scan", "test"):
        L(N[k], "R", J0, ("L", fr(J0, cy(k))))
    L(J0, ("R", fr(J0, cy("demo"))), N["demo"], "L")
    L(N["demo"], "R", N["exclude"], "T", "hv")
    L(N["exclude"], "R", N["freeze"], ("T", 0.35), "hv")
    L(N["notes"], "B", N["freeze"], ("T", 0.7), "via", via=[(N["notes"].cx, top["QA"] - 8), (N["freeze"].x + NW * 0.7, top["QA"] - 8)], dash=True, color=GRAY, label="к фризу готово", lt=0.5)
    # стабилизация
    L(N["freeze"], "R", F1, ("L", fr(F1, cy("freeze"))))
    for k in ("toml", "regress", "testplan", "gate"):
        L(F1, ("R", fr(F1, cy(k))), N[k], "L")
    L(N["regress"], "R", J1, ("L", fr(J1, cy("regress"))))
    L(N["gate"], "R", J1, ("L", fr(J1, cy("gate"))))
    L(J1, ("R", fr(J1, cy("fix"))), N["fix"], "L")
    L(N["fix"], "R", N["smoke"], "B", "hv")
    L(N["smoke"], "B", N["fix"], "T", "via", via=[(N["smoke"].cx, top["DEV"] + 8), (N["fix"].cx, top["DEV"] + 8)], color=RED, dash=True, label="критические дефекты → фикс", lt=0.5)
    L(N["toml"], "R", N["init"], "T", "hv", dash=True, color=GRAY, label="TOML → релиз-борд", lt=0.5)
    L(N["smoke"], "R", N["init"], ("T", 0.3), "hv")
    # релиз-борд
    L(N["init"], "R", N["audit"], "T", "hv")
    L(N["audit"], "R", N["uatdeploy"], "T", "hv")
    L(N["uatdeploy"], "R", N["functest"], "L")
    L(N["functest"], "R", N["psi"], "B", "hv")
    L(N["psi"], "R", N["transfer"], "L")
    L(N["functest"], ("T", 0.85), N["transfer"], ("B", 0.5), "vhv", mid=top["ГПН"] - 10, dash=True, color=GRAY, label="ПСИ не нужен — пропуск", lt=0.5)
    L(N["audit"], "L", N["fix"], "B", "hv", color=RED, dash=True, label="замечания аудита", lt=0.5)
    # PreProd
    L(N["transfer"], "R", N["notify"], "B", "hv")
    L(N["notify"], "R", F2, ("L", fr(F2, cy("notify"))))
    for k in ("preprod", "db", "brokers"):
        L(F2, ("R", fr(F2, cy(k))), N[k], "L")
        L(N[k], "R", J2, ("L", fr(J2, cy(k))))
    L(N["testplan"], "R", J2, ("L", fr(J2, cy("testplan") if cy("testplan") < J2.y + J2.h else J2.y)), "hv", dash=True, color=GRAY, label="тест-план в ТестОпс ГПН-ЦР", lt=0.55)
    L(J2, ("R", fr(J2, cy("pregress"))), N["pregress"], "L")
    L(N["pregress"], "R", N["preport"], "L")
    hf = p.add("round", X(20), cyy[("РИ", "b")] - 44, 160, 88, [("Hotfix: тот же процесс", "b"), ("Blocker и критические дефекты PreProd → hotfix; релиз всё равно идёт в Прод", "s")],
               fill="#FFD2A6", stroke=ORANGE, sw=1.5, fs=10)
    L(N["preport"], "T", hf, "B", color=RED, dash=True, label="критические → hotfix", lt=0.3)
    # Прод
    L(N["preport"], "R", N["orgnotify"], "B", "hv")
    L(N["orgnotify"], "R", N["prod"], "T", "hv")
    L(N["prod"], "R", F3, ("L", fr(F3, cy("prod"))))
    for k in ("smokeprod", "dbpost", "brpost"):
        L(F3, ("R", fr(F3, cy(k))), N[k], "L")
        L(N[k], "R", J3, ("L", fr(J3, cy(k))))
    L(J3, ("R", fr(J3, cy("comm"))), N["comm"], "L")
    L(N["comm"], "R", N["close"], "T", "hv")
    L(N["close"], "R", end, "L")

    # легенда и пояснения
    ly = BOT + 18
    p.add("rect", 0, BOT + 6, W, 220, [], fill="#FFFFFF", stroke="#A0A0A0")
    p.text(10, ly, 300, 18, [("Как читать схему", "b")], fs=12, fc=INDIGO)
    items = [("round", "#FFFFFF", INDIGO, False, "этап: в дорожке — ответственный (роль компании, где идёт этап); в подписи — исполнители и SLA"),
             ("round", "#FFE9D2", INDIGO, False, "параллельные этапы (между чёрными планками)"),
             ("round", "#F0FBD0", INDIGO, False, "шаг релиз-борда"),
             ("round", "#FFFFFF", INDIGO, True, "шаг, который пропускается, если не нужен (ПСИ ИБ)")]
    for i, (k, fl, st, ds, txt) in enumerate(items):
        yy = ly + 28 + i * 28
        p.add(k, 10, yy - 8, 34, 20, [], fill=fl, stroke=st, dash=ds, sw=1.4)
        p.text(52, yy - 6, 620, 18, [(txt, "n")], fs=10)
    p.free([(740, ly + 28), (800, ly + 28)], color=RED, dash=True)
    p.text(808, ly + 20, 560, 18, [("возврат на доработку", "n")], fs=10)
    p.free([(740, ly + 56), (800, ly + 56)], color=GRAY, dash=True)
    p.text(808, ly + 48, 560, 18, [("зависимость (нужно к началу следующего этапа)", "n")], fs=10)
    p.text(1500, ly, 3600, 200, [
        ("Основные правила", "b"),
        (f"• Нумерация этапов сквозная, 1–{D.N_STEPS}. Код и релизы — схема 2 (master, теги); даты и SLA по этапам — схема 3.", "n"),
        ("• Планирование: приоритеты (ВНП) → оценка и спринт (РП с командой) → релизный тикет (Release owner) → подтверждение состава (ВНП).", "n"),
        ("• Спринт: параллельно разработка, скан и устранение уязвимостей в CI, тестирование, release notes; затем демо (QA проводит, ВНП принимает), вывод не принятых задач, фича-фриз = тег релиза.", "n"),
        ("• Стабилизация: параллельно друг другу регресс UAT, финальный скан по тегу, TOML (release notes и changelog уже готовы) и тест-план; затем устранение, Smoke UAT.", "n"),
        ("• Релиз-борд — в порядке борда; релиз-инженер НЕДРА инициирует (запуск, документ для ПСИ) и уведомляет ГПН о начале работ на PreProd; остальное — роли ГПН.", "n"),
        ("• Go/No-Go нет: после регресса PreProd релиз идёт в Прод всегда; правки — только helm, Blocker и критические дефекты — hotfix. После деплоя Smoke PROD, БД и брокеры параллельно, затем окно наблюдения.", "n"),
    ], fs=10)
    return p


# ===========================================================================
# Страница 2. Код и релизы: master + теги
# ===========================================================================
def page_branches() -> Page:
    W, H = 2200, 1180
    p = Page("2. Код и релизы", W, H)
    header(p, "код и релизы: master, git-теги с ID релиза, супер-фича-ветки")
    SPR = [(180, 780, "Спринт N · 2 недели"), (780, 1380, "Спринт N+1 · 2 недели"), (1380, 1980, "Спринт N+2 · 2 недели")]
    for i, (a, b, t) in enumerate(SPR):
        p.add("rect", a, 56, b - a, 34, [(t, "b")], fill=INDIGO, stroke="#FFFFFF", fs=12, fc="#FFFFFF")
        p.add("rect", a, 90, b - a, 640, [], fill="#F4F6FB" if i % 2 else "#ECEAF9", stroke="#C9D2E6", sw=1)
    p.text(20, 130, 150, 40, [("master\n(репозиторий сервиса)", "b")], fs=12, fc=INDIGO)
    my = 160
    p.free([(170, my), (2100, my)], sw=5, arrow=False, color=INDIGO)
    for x in range(230, 2060, 70):                                   # PR-слияния
        p.add("ellipse", x - 5, my - 5, 10, 10, [], fill=INDIGO, stroke=INDIGO)
    p.text(185, my + 12, 560, 16, [("PR с ревью; незавершённое — за feature flag", "n")], fs=9, fc=DARK)

    def tag(x: float, label: str, col: str, y0: float = my) -> None:
        p.add("bar", x - 4, y0 - 24, 8, 48, [], fill=col, stroke=col)
        p.text(x - 90, y0 - 66, 190, 34, [(label, "b")], fs=9, fc=col, align="center")

    # релиз N
    p.add("round", 520, 250, 250, 44, [("Не принято на демо → вывод из релиза", "b"), ("revert PR / отключение флага", "s")], fill="#FFE9D2", stroke=ORANGE, sw=1.5, fs=9)
    p.free([(700, 250), (700, my + 6)], color=ORANGE, dash=True, sw=1.5, arrow=True)
    tag(775, "тег EARM-N\nфича-фриз (релиз-кандидат)", RED)
    p.free([(775, my + 26), (775, 300), (1100, 300)], color=ORANGE, sw=2, arrow=False, dash=True)
    p.text(790, 304, 700, 34, [("стабилизация N: регресс UAT → фиксы (в master или в ветку от тега) → итоговый тег (код-фриз) → релиз-борд → PreProd → Прод", "n")], fs=9, fc=DARK)
    tag(1180, "тег EARM-N (код-фриз)\nберёт релиз-борд", "#019390")
    p.add("ellipse", 1250, my - 17, 34, 34, [("Прод", "b")], fill=LIME, stroke=INDIGO, sw=2, fs=8)
    # релиз N+1
    tag(1375, "тег EARM-N+1\nфича-фриз", RED)
    p.free([(1375, my + 26), (1375, 380), (1700, 380)], color=ORANGE, sw=2, arrow=False, dash=True)
    p.text(1390, 384, 700, 34, [("стабилизация N+1; новые фичи спринта N+2 вливаются в master за флагом", "n")], fs=9, fc=DARK)
    tag(1780, "тег EARM-N+1\n(код-фриз)", "#019390")
    tag(1975, "тег EARM-N+2\nфича-фриз", RED)
    # супер-фича-ветка
    sy = 480
    p.free([(300, my + 4), (340, sy), (1000, sy)], sw=3.5, color="#904EE2", arrow=False)
    for x in (480, 620, 760, 900):
        p.add("ellipse", x - 5, sy - 5, 10, 10, [], fill="#904EE2", stroke="#904EE2")
    p.free([(1000, sy), (1040, my + 6)], sw=3.5, color="#904EE2", arrow=True)
    p.text(345, sy + 10, 700, 34, [("супер-фича-ветка (опционально): PR с ревью как обычно → пакет правок тестируется целиком", "b")], fs=10, fc="#904EE2")
    p.text(1046, sy - 22, 380, 34, [("merge в master после приёмки;\nне принято → ветка не вливается", "n")], fs=9, fc="#904EE2")
    # hotfix
    hy = 600
    p.free([(1262, my + 20), (1300, hy), (1600, hy)], sw=3, color=RED, arrow=False)
    p.add("ellipse", 1595, hy - 6, 12, 12, [], fill=RED, stroke=RED)
    p.text(1305, hy + 10, 640, 34, [("hotfix (тот же процесс, меньше объём сборки): исправление в master; если master ушёл вперёд — cherry-pick в короткоживущую ветку от тега Прода и новый тег", "b")], fs=9, fc=RED)
    p.text(180, 660, 1950, 20, [("Сервисы живут в отдельных репозиториях: один и тот же ID релиза (Fix Version) ставится тегом в репозиториях всех сервисов релиза. Отдельных release-веток нет — нет и backport между ними.", "b")], fs=10, fc=INDIGO)
    p.text(180, 684, 1950, 20, [("Соответствие этапам схемы 1: 5 — разработка и влитие в master · 9 — демо · 10 — вывод не принятых задач · 11 — фича-фриз и тег · 12–17 — стабилизация, фиксы в master · 31 — деплой в Прод.", "n")], fs=10, fc=DARK)
    rows = [["Тема", "Правило"]] + [[a, b] for a, b in D.BRANCH_RULES]
    table(p, 20, 730, [260, 1660], rows, fs=11)
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
        if steps == [D.ID["psi"]]:
            s0, e0 = sched1[D.ID["psi"]][0], sched1[D.ID["psi"]][1]
            p.add("rect", x0 + s0 * PX, ry + 8, (e0 - s0) * PX, h - 16, [("если нужен · до 5 дн.", "n")], fill="#FFFFFF", stroke=colr[contour], dash=True, sw=1.5, fs=9, fc=DARK)
        else:
            w = max((e0 - s0) * PX, 10)
            is_sprint = steps[0] == D.ID["dev"]
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
    b2 = p.add("round", 400, 84, 320, 120, [("Fix Version (релиз = тег)", "b"), ("состав релиза: только Story и Bug; ID релиза — git-тег в репозитории каждого сервиса", "n")],
               fill="#FFE9D2", stroke=ORANGE_L, fs=11, align="left", valign="top")
    b3 = p.add("round", 780, 84, 340, 120, [("Задача этапа", "b"), ("по одной на каждый этап (1–36): оценка, исполнитель, результат; возврат — новая задача", "n")],
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
def build_html(pages: List[Page], extra=None, trz=None, title: str = "Процесс выпуска релиза ЕАРМ", comments: bool = False, mid=None, editable: bool = False, body_extra: str = "") -> str:
    import html_theme as TH
    import sections as S
    from html import escape as e

    titles = ["1. Процесс", "2. Ветки", "3. Дорожная карта", "4. Jira и метрики", "5. Дорожная карта релизов", "6. Стратегическое планирование", "7. Экономика и ресурсы"]
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
        ("diagrams", "Схемы", "<p class='muted'>Исходник — <code>docs/drawio/10-release-process.drawio</code> (7 страниц); здесь статичные копии с масштабированием. Ведение релизных веток — схема 2.</p>" + "".join(figs)),
        ("steps", "Этапы: ответственные и SLA", S.registry_html()),
        ("roadmap", "Дорожная карта этапов (SLA)", "<p>Этапы, ответственные и SLA (схема 3):</p>" + S.roadmap_html()),
        *(mid or []),
        ("roles", "Роли и зоны ответственности", "<h3>Кто есть кто</h3>" + S.roles_table_html() + "<h3>Матрица «роль × этап»</h3>" + S.roles_matrix_html()),
        ("decisions", "Кто принимает решения", S.decisions_html()),
        ("metrics", "Метрики", S.metrics_html()),
        ("control", "Контроль релиза и риски", S.control_html()),
        ("trz", "Экономика и баланс ресурсов", trz or "<p>См. калькулятор.</p>"),
    ]
    if extra:
        sections = sections + list(extra)
    nav = "".join(f'<a href="#{i}">{e(t)}</a>' for i, t, _ in sections)
    navjs = "document.querySelectorAll('main table').forEach(function(t){var p=t.parentNode;if(!p.matches('.tw,.fx-table,.heat')&&!t.closest('.tw,.fx-table,.heat')){var w=document.createElement('div');w.className='tw';p.insertBefore(w,t);w.appendChild(t)}});(function(){var l=document.querySelectorAll('nav a'),s=[].slice.call(document.querySelectorAll('main>section'));function f(){var y=window.scrollY+120,c=0;s.forEach(function(x,i){if(x.offsetTop<=y)c=i});l.forEach(function(a,i){var on=i===c;if(on&&!a.classList.contains('on')){var nv=a.parentNode.parentNode,x=a.offsetLeft-nv.clientWidth/2+a.offsetWidth/2;nv.scrollLeft=Math.max(0,x)}a.classList.toggle('on',on)})}window.addEventListener('scroll',f);f()})();"

    cm = lambda i: (f'<div class="cm"><label for="cm-{i}">Ваши правки к разделу</label><textarea id="cm-{i}" data-k="{i}" rows="3" placeholder="Что изменить, добавить, убрать…"></textarea></div>' if comments else "")
    body = "".join(f'<section id="{i}"><span class="kicker">Раздел {n}</span><h2>{e(t)}</h2>{c}{cm(i)}</section>' for n, (i, t, c) in enumerate(sections, 1))
    fb = ('<div class="fb"><span>Правок: <b id="fb-n">0</b></span><button id="fb-dl">Правки в .txt</button>'
          '<button id="fb-cp">Копировать правки</button><span class="muted">Правки сохраняются в браузере; перед отправкой нажмите «Скачать» или «Копировать».</span></div>') if comments else ""
    import plan_html as PH
    import edit_layer as EL
    import release_cal as RC
    if editable:
        fb = fb.replace("</div>", EL.FB_EXTRA + "</div>", 1) if fb else fb
    js = TH.JS_FIG + PH.JS_TABS + navjs + (TH.JS_FEEDBACK if comments else "")
    css_extra = (EL.CSS_EDIT + RC.CSS) if editable else ""
    core = ('<script id="rp-embedded" type="application/json">{}</script><script>' + EL.JS_CORE + "</script>") if editable else ""
    tail = ("<script>" + EL.JS_EDIT + "</script>") if editable else ""
    return (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(title)}</title><style>{TH.CSS}{PH.CSS_PLAN}{css_extra}</style></head><body>{core}'
            f'<header class="top"><h1>{e(title)}</h1><div class="muted">Схема, этапы, роли, SLA, метрики, ТРЗ и FTE · сгенерировано <code>scripts/build_release_process.py</code></div></header>'
            f'<nav><div class="in">{nav}</div></nav><main>{body}</main>{fb}{body_extra}<script>{js}</script>{tail}</body></html>')


def main() -> None:
    import plan_pages as PP
    import planning as PL
    rels = PL.releases()
    pages = [page_process(), page_branches(), page_roadmap(), page_jira(), PP.page_release_roadmap(header, rels), PP.page_strategy(header, rels), PP.page_econ(header)]
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
