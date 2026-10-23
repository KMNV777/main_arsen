#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Страницы draw.io: дорожная карта релизов, стратегическое планирование, экономика и баланс ресурсов."""

from __future__ import annotations

from datetime import date, timedelta

import planning as P
import process_data as D
import trz_model as T
from drawio_kit import Page, table

INDIGO, LIME, SKY, ORANGE, ORANGE_L, DARK, GRAY = "#140093", "#CFF85E", "#AAC3E3", "#FF7500", "#FDAB64", "#1B1B3A", "#8A8A8A"
PH_COL = {1: "#8A9BB5", 2: "#140093", 3: "#4BADE8", 4: "#904EE2", 5: "#FBAE40", 6: "#63BA3C"}


def kpi(p: Page, x: float, y: float, w: float, big: str, title: str, sub: str, color: str = INDIGO) -> None:
    p.add("round", x, y, w, 84, [], fill="#FFFFFF", stroke="#D5DDEE")
    p.text(x + 12, y + 6, w - 24, 34, [(big, "b")], fs=24, fc=color)
    p.text(x + 12, y + 40, w - 24, 20, [(title, "b")], fs=11, fc=DARK)
    p.text(x + 12, y + 58, w - 24, 22, [(sub, "n")], fs=9, fc="#5E5E5E")


def page_release_roadmap(header, rels) -> Page:
    t0, t1 = date(2026, 10, 1), date(2027, 12, 15)
    PXD = 3.7
    lw, x0 = 270, 20
    X = lambda d: x0 + lw + (d - t0).days * PXD
    W = int(x0 + lw + (t1 - t0).days * PXD + 30)
    rowh = 34
    H = 190 + (len(rels) + 4) * rowh + 80
    p = Page("5. Дорожная карта релизов", W, H)
    header(p, "дорожная карта релизов: скользящий год, фазы каждого релиза")
    y = 56
    p.add("rect", x0, y, lw, 44, [("РЕЛИЗ · СТАТУС", "b")], fill=INDIGO, stroke="#FFFFFF", fs=10, fc="#FFFFFF", align="left")
    d = date(2026, 10, 1)
    while d < t1:
        nm = date(d.year + (d.month == 12), d.month % 12 + 1, 1)
        p.add("rect", X(d), y, (nm - d).days * PXD, 44, [(f"{P.MONTHS_FULL[d.month - 1][:3]} {str(d.year)[2:]}", "b")], fill=INDIGO if d.month % 2 else "#2A1FA8",
              stroke="#FFFFFF", fs=10, fc="#FFFFFF")
        d = nm
    ry = y + 44
    last = None
    for r in rels:
        if r["q"] != last:
            last = r["q"]
            p.add("rect", x0, ry, W - 2 * x0, 24, [(f"{r['q'].upper()} · 3 РЕЛИЗА", "b")], fill="#EEEDF8", stroke="#E4E8F2", fs=9, fc=INDIGO, align="left")
            ry += 24
        p.add("rect", x0, ry, lw, rowh, [], fill="#FFFFFF", stroke="#E4E8F2")
        chip = {"ВЫПОЛНЕНО": ("#E3FCEF", "#006644"), "В РАБОТЕ": ("#DEEBFF", "#0052CC"), "ПЛАН": ("#DFE1E6", "#42526E")}[r["status"]]
        p.add("rect", x0 + 6, ry + 9, 70, 16, [(r["status"], "b")], fill=chip[0], stroke=None, fs=8, fc=chip[1])
        p.text(x0 + 82, ry + 1, lw - 86, 16, [(r["name"], "b")], fs=11, fc=INDIGO)
        p.text(x0 + 82, ry + 17, lw - 86, 15, [(f"спринт {P.fmt(r['sprint'][0])} – {P.fmt(r['sprint'][1])}" + (" · ПСИ ИБ" if r["psi"] else ""), "n")], fs=8, fc="#5E5E5E")
        p.add("rect", x0 + lw, ry, W - 2 * x0 - lw, rowh, [], fill="#FFFFFF", stroke="#EEF1F6", sw=0.5)
        for ph, (a, b) in r["phases"].items():
            w = (b + timedelta(days=1) - a).days * PXD
            nd = r["pdays"][ph]
            lab = f"{D.PHASES[ph].split(' (')[0]} · {nd} дн." if w > 105 else (f"{nd}" if w > 11 else "")
            p.add("rect", X(a), ry + 8, w, 18, [(lab, "b")] if lab else [], fill=PH_COL[ph], stroke="#FFFFFF", fs=8, fc="#FFFFFF")
        p.text(X(r["close"] + timedelta(days=1)) + 6, ry + 8, 80, 18, [(f"{len(r['cols']) - 1} дн.", "b")], fs=9, fc=INDIGO, valign="middle")
        ry += rowh
    p.free([(X(P.TODAY), y + 44), (X(P.TODAY), ry)], color="#E5493A", sw=2, arrow=False)
    p.text(X(P.TODAY) + 4, ry + 2, 200, 16, [("сегодня (21 окт 2026)", "b")], fs=9, fc="#E5493A")
    lx = x0
    for ph in D.PHASES:
        p.add("rect", lx, ry + 28, 12, 12, [], fill=PH_COL[ph], stroke=None)
        p.text(lx + 16, ry + 25, 190, 18, [(D.PHASES[ph], "n")], fs=9, fc=DARK)
        lx += 210
    p.text(x0, ry + 50, W - 2 * x0, 40, [
        ("Каденс: квартал = 6 спринтов по 2 недели, релизов 3 (релизные спринты 2, 4, 6); одновременно в работе до %d релизов. Даты считаются из SLA этапов и ориентировочного производственного календаря." % P.max_parallel(rels), "n"),
        ("Числа в блоках — рабочие дни фазы, справа — длительность всего цикла. Детализация до этапа и дня — в общем HTML (раздел «Дорожная карта релизов»).", "n")], fs=10, fc=DARK)
    return p


def page_strategy(header, rels) -> Page:
    W = 2200
    wl = P.weekly_load(rels)
    wk0 = P.monday(min(r["day0"] for r in rels))
    wk1 = P.monday(max(r["close"] for r in rels))
    weeks = []
    d = wk0
    while d <= wk1:
        weeks.append(d)
        d += timedelta(days=7)
    p = Page("6. Стратегическое планирование", W, 2400)
    header(p, "стратегическое планирование релизов: календарь, окна параллельности, нагрузка ролей")
    par = P.max_parallel(rels)
    kw = 300
    kpi(p, 20, 56, kw, str(len(rels)), "релизов на скользящий год", "3 в квартал · релизные спринты 2, 4, 6")
    kpi(p, 20 + (kw + 20), 56, kw, str(par), "релиза в работе одновременно", f"цикл ≈ {D.total_days(False) / 5:.1f} нед. при релизе раз в 4 недели")
    kpi(p, 20 + 2 * (kw + 20), 56, kw, f"{D.total_days(False):g}–{D.total_days(True):g}", "рабочих дней цикла", "без ПСИ ИБ — с ПСИ ИБ")
    kpi(p, 20 + 3 * (kw + 20), 56, kw, str(sum(r["psi"] for r in rels)), "релизов с ПСИ ИБ", "закладывается в каждый второй (допущение)")
    p.text(20, 156, 600, 22, [("Календарь релизов на скользящий год", "b")], fs=14, fc=INDIGO)
    rows = [["Релиз", "Старт (тикет)", "Спринт", "Фича-фриз", "Код-фриз", "Аудит кода", "Трансфер согласован", "PreProd", "Деплой Прод", "Закрытие", "ПСИ ИБ"]] + P.calendar_rows(rels)
    y = table(p, 20, 184, [130, 120, 170, 120, 120, 170, 160, 120, 130, 120, 90], rows, fs=10, min_h=22)
    y += 24
    p.text(20, y, 900, 22, [("Календарь по всем этапам цикла: даты и длительность, раб. дн.", "b")], fs=14, fc=INDIGO)
    mrows = [["№", "Этап", "Дн.", "Ответственный"] + [r["name"] for r in rels]] + P.stage_matrix(rels)
    y = table(p, 20, y + 28, [34, 250, 50, 120] + [105] * len(rels), mrows, fs=8, min_h=18, fills={(i, 0): "#EEEDF8" for i in range(1, len(mrows))})
    y += 24
    p.text(20, y, 900, 22, [("Загрузка ролей по неделям: ТРЗ в часах в ячейке, цвет — доля от 1 FTE (32 ч в неделю)", "b")], fs=14, fc=INDIGO)
    y += 30
    cap = 40 * T.PARAMS["LOAD"][0]
    order = ["РИ", "ИБ", "QA", "RO", "DEV", "ВНП", "DEVOPS", "SVC", "АБД", "АБР"]
    cw, ch, lw = 26, 22, 230
    for i, w in enumerate(weeks):
        if w.day <= 7:
            p.text(20 + lw + i * cw, y, 60, 14, [(P.MONTHS[w.month - 1], "b")], fs=8, fc="#6B778C")
    y += 16
    for role in order:
        p.text(20, y, lw - 6, ch, [(D.ROLES[role][0].split(" (")[0], "n")], fs=9, fc=DARK, valign="middle")
        for i, w in enumerate(weeks):
            u = wl[role].get(w, 0) / cap
            col = "#EEF1F6" if u < .05 else "#D7F3B0" if u < .5 else "#8ED15A" if u < 1 else "#FBAE40" if u < 1.5 else "#F26B43"
            hh = wl[role].get(w, 0)
            p.add("rect", 20 + lw + i * cw, y, cw - 2, ch - 2, [(f"{hh:.0f}", "n")] if hh >= 0.5 else [], fill=col, stroke=None, fs=6, fc=DARK)
        p.text(20 + lw + len(weeks) * cw + 6, y, 230, ch, [(f"ТРЗ {sum(wl[role].values()):.0f} ч · пик {max(wl[role].values()):.0f} ч/нед", "b")], fs=8, fc=INDIGO, valign="middle")
        y += ch
    y += 12
    lx = 20 + lw
    for col, t in (("#EEF1F6", "< 5 %"), ("#D7F3B0", "до 50 %"), ("#8ED15A", "50–100 %"), ("#FBAE40", "100–150 %"), ("#F26B43", "> 150 %")):
        p.add("rect", lx, y + 2, 12, 12, [], fill=col, stroke=None)
        p.text(lx + 16, y, 100, 16, [(t, "n")], fs=9, fc=DARK)
        lx += 120
    y += 36
    p.text(20, y, 900, 22, [("Правила стратегического планирования", "b")], fs=14, fc=INDIGO)
    rules = ["Календарь релизов утверждается на скользящий год и пересматривается раз в квартал вместе с Релизным Epic.",
             "Старт релиза допускается, только если у РИ, ИБ и QA в окне этапов запас по загрузке; иначе релиз сдвигается на спринт.",
             "Число сервисов N планируется от ёмкости: часы по ролям при N не превышают 100 % FTE роли в пиковую неделю.",
             "ПСИ ИБ закладывается в окно до старта релиза; релиз с ПСИ не стартует параллельно другому релизу с ПСИ.",
             "Окна без релизных работ: новогодние и длительные майские праздники.",
             "Сдвиг релиза — решение Release owner по согласованию с ВНП; причина фиксируется в календаре.",
             "Hotfix вне календаря: тот же процесс, учитывается в нагрузке как резерв."]
    p.text(20, y + 28, W - 40, 20 * len(rules) + 10, [(f"{i}. {t}", "n") for i, t in enumerate(rules, 1)], fs=11, fc=DARK)
    p.height = int(y + 28 + 20 * len(rules) + 50)
    return p


def page_econ(header) -> Page:
    W = 1700
    base = T.compute()
    tot = T.totals(base)
    n = len(T.ROLE_ORDER)
    over = sum(max(base[r]["delta"], 0) for r in T.ROLE_ORDER)
    under = sum(max(-base[r]["delta"], 0) for r in T.ROLE_ORDER)
    p = Page("7. Экономика и ресурсы", W, 1400)
    header(p, "экономическая эффективность: избыток и нехватка ресурсов по ролям")
    kw = 380
    kpi(p, 20, 56, kw, f"{tot['current']:.1f}", "FTE списывается сейчас", f"1 FTE на каждую из {n} ролей")
    kpi(p, 20 + kw + 20, 56, kw, f"{tot['fte']:.1f}", "FTE занято релизным циклом", f"N = {T.PARAMS['N'][0]} сервисов, {T.PARAMS['R'][0]} релизов в год (допущения)")
    kpi(p, 20 + 2 * (kw + 20), 56, kw, f"+{over:.1f}", "FTE свободной ёмкости", "не штатная потребность — роли заняты и вне релизов", "#006644")
    kpi(p, 20 + 3 * (kw + 20), 56, kw, f"−{under:.1f}", "FTE нехватка", "роли, где ТРЗ не покрыто списанием", "#E5493A")
    defs = [T.ROLE_NAME[r].split(" /")[0] for r in T.ROLE_ORDER if base[r]["delta"] < -0.2]
    p.add("rect", 20, 156, W - 40, 44, [(f"Вывод. Списывается {tot['current']:.1f} FTE при потребности {tot['fte']:.1f}: свободная ёмкость {over:.1f} FTE. "
                                          f"Нехватка у ролей: {'; '.join(defs) or 'нет'} — усилить или сократить объём (N, число релизов).", "n")],
          fill="#EEEDF8", stroke=INDIGO, fs=11, fc=DARK, align="left")
    p.text(20, 214, 700, 22, [("Баланс по ролям: списано − нужно по ТРЗ, FTE", "b")], fs=14, fc=INDIGO)
    mid, sc = 20 + 300 + 230, 190.0
    p.free([(mid, 244), (mid, 244 + n * 26 + 8)], color="#C7D4DE", sw=1, arrow=False)
    p.text(mid + 6, 238, 260, 14, [("избыток (списано больше, чем нужно)", "b")], fs=8, fc="#006644")
    p.text(mid - 266, 238, 260, 14, [("нехватка", "b")], fs=8, fc="#B3260E", align="right")
    y = 258
    for r in T.ROLE_ORDER:
        b = base[r]["delta"]
        w = abs(b) * sc
        col = "#4BADE8" if abs(b) <= 0.2 else ("#63BA3C" if b > 0 else "#F26B43")
        p.text(20, y, 300, 22, [(T.ROLE_NAME[r].split(" (")[0].split(" /")[0], "n")], fs=10, fc=DARK, align="right", valign="middle")
        p.add("rect", mid if b >= 0 else mid - w, y + 2, w, 18, [], fill=col, stroke=None)
        p.text(mid + w + 6 if b >= 0 else mid - w - 56, y, 50, 22, [(f"{b:+.2f}", "b")], fs=10, fc=DARK, align="left" if b >= 0 else "right", valign="middle")
        y += 26
    y += 24
    rows = [["Роль", "Занято релизом, FTE", "Списано, FTE", "Баланс, FTE", "Вывод"]]
    fills = {}
    for i, r in enumerate(T.ROLE_ORDER, 1):
        b = base[r]["delta"]
        st = "норма" if abs(b) <= 0.2 else ("резерв ёмкости" if b > 0 else "нехватка")
        rows.append([T.ROLE_NAME[r], f"{base[r]['fte']:.2f}", f"{T.CURRENT_FTE:.1f}", f"{b:+.2f}", st])
        fills[(i, 4)] = {"норма": "#DEEBFF", "резерв ёмкости": "#E3FCEF", "нехватка": "#FDE4DC"}[st]
    rows.append(["Итого", f"{tot['fte']:.2f}", f"{tot['current']:.1f}", f"{tot['current'] - tot['fte']:+.2f}", ""])
    y = table(p, 20, y, [420, 200, 180, 180, 160], rows, fs=10, min_h=22, fills=fills)
    p.text(20, y + 14, W - 40, 100, [
        ("Занятость релизом: FTE = ТРЗ за год / (рабочие часы × 80 %); ТРЗ этапа = (F + S × N) × k. Стоимость = FTE × рабочие часы года × ставка роли — ставки в схему не вносятся, вводятся в калькуляторе общего HTML.", "n"),
        ("«Норма» — отклонение не более ±20 % от списания. Часы по этапам и N — стартовые допущения, заменить фактом списаний по задачам этапов в Jira. Мейнтейнеры и QA — пулы людей: «нехватка 1 FTE» = пул больше одного человека.", "n")],
        fs=10, fc=DARK)
    p.height = int(y + 120)
    return p
