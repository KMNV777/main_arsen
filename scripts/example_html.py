#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Пример: анализ сроков EARM 26.2.1 / 26.2.2 (по календарю релизов ДК) и диаграмма Ганта «план по SLA / факт»."""

from __future__ import annotations

from datetime import date, timedelta
from html import escape as e

import planning as P
import process_data as D
import sections as S

START = date(2026, 8, 3)                 # дата начала (ветка develop/26.2)
TODAY = date(2026, 10, 22)
Dt = lambda d, m: date(2026, m, d)


def wdb(a: date, b: date) -> int:
    """Рабочих дней от a до b (b позже a — положительно)."""
    sg, n = 1, 0
    if b < a:
        a, b, sg = b, a, -1
    while a < b:
        a += timedelta(days=1)
        if P.is_wd(a):
            n += 1
    return n * sg


def dur(a: date, b: date) -> int:
    """Длительность периода в рабочих днях, включая первый и последний день."""
    return wdb(a, b) + 1


def dd(a: date, b: date) -> str:
    return f"{P.fmt(a)}" if a == b else f"{P.fmt(a)} – {P.fmt(b)}"


def model():
    """План по SLA от старта 03.08 (ПСИ нужен): {шаг: (с, по)}."""
    day0 = P.add_wd(START, -P.PREP)                 # 03.08 — старт спринта (разработка в master)
    sch = D.schedule(True)
    cols = [P.add_wd(day0, c) for c in range(60)]
    out = {}
    for n, (a, b) in sch.items():
        c0, c1 = (int(a), int(b) - 1) if b > a else (max(int(a) - 1, 0),) * 2
        out[n] = (cols[c0], cols[max(c0, c1)])
    return out


def span(m, *keys):
    ns = [D.ID[k] for k in keys]
    return min(m[n][0] for n in ns), max(m[n][1] for n in ns)


def build():
    m = model()
    plan_prod = m[D.ID["prod"]][0]
    S0, S1 = D.schedule(False), D.schedule(True)
    I = D.ID
    sla_total = (S0[I["prod"]][0] - S0[I["dev"]][0], S1[I["prod"]][0] - S1[I["dev"]][0])
    tail_a = int(S0[I["prod"]][0] - S0[I["audit"]][1])
    opt = P.add_wd(Dt(15, 10), tail_a)              # от согласования аудита 15.10 + хвост цикла по SLA
    tail_f = int(S0[I["prod"]][0] - S0[I["fix"]][1])
    cons = P.add_wd(Dt(22, 10), tail_f)             # от конца устранения багов 22.10 + весь хвост цикла по SLA
    # строки: (название, план (с,по) | None, факт-полосы [(с, по, подпись)], маркеры [(дата, тип, подпись)])
    rows = [
        ("Релизный тикет, состав", span(m, "prior", "plan", "ticket", "confirm"), [], [(Dt(13, 8), "warn", "финализация тикета (причина сдвига 2)")]),
        ("Ветка develop/26.2 и спринт", span(m, "dev", "scan", "test", "notes", "demo"), [(Dt(3, 8), Dt(11, 8), "ветка → фича-фриз")], []),
        ("Фича-фриз", span(m, "freeze"), [], [(Dt(11, 8), "ok", "фича-фриз 11.08")]),
        ("Регресс UAT", span(m, "regress"), [(Dt(12, 8), Dt(24, 8), "итерация 1"), (Dt(5, 10), Dt(12, 10), "итерация 2")], []),
        ("Устранение багов UAT", span(m, "fix"), [(Dt(24, 8), Dt(22, 10), "закончили по 2 итерациям")], []),
        ("Уязвимости (в модели — в спринте)", span(m, "scan"), [(Dt(11, 8), Dt(15, 10), "«2 месяца на уязвимости»")], []),
        ("Техсессия и очное демо", None, [(Dt(9, 9), Dt(2, 10), "вне процесса")], []),
        ("Ожидание ИБ", None, [], [(Dt(21, 9), "warn", "нет брони ИБ 21.09")]),
        ("Аудит кода · SAST", span(m, "audit"), [(Dt(8, 9), Dt(15, 10), "")], [(Dt(8, 9), "sent", "ушли 08.09"), (Dt(15, 9), "no", "не согласовали 15.09"), (Dt(15, 10), "ok", "согласовали 15.10")]),
        ("Аудит кода · SCA", None, [(Dt(7, 9), Dt(2, 10), "")], [(Dt(7, 9), "sent", "ушли 07.09"), (Dt(9, 9), "ok", "согласовали 09.09"), (Dt(2, 10), "ok", "согласовали повторно 02.10")]),
        ("Аудит кода · Luntry", None, [(Dt(8, 9), Dt(6, 10), "")], [(Dt(8, 9), "sent", "ушли 08.09"), (Dt(9, 9), "ok", "согласовали 09.09"), (Dt(6, 10), "ok", "согласовали повторно 06.10")]),
        ("Аудит кода · Секреты", None, [(Dt(7, 9), Dt(8, 10), "")], [(Dt(7, 9), "sent", "ушли 07.09"), (Dt(9, 9), "no", "не согласовали 09.09"), (Dt(8, 10), "ok", "согласовали 08.10")]),
        ("ПСИ ИБ", span(m, "psi"), [], [(Dt(3, 9), "ok", "ПСИ пройдено 03.09")]),
        ("Согласование трансфера", span(m, "transfer"), [], []),
        ("PreProd: выкатка и регресс", span(m, "preprod", "pregress", "preport"), [], []),
        ("Деплой в Прод", (plan_prod, plan_prod), [], [(Dt(25, 8), "plan", "план в таблице 25.08"), (Dt(9, 9), "old", "прогноз 09.09"), (Dt(12, 10), "old", "прогноз 12.10"), (Dt(14, 10), "old", "прогноз 14.10"),
                                                        (Dt(26, 10), "fc", "текущий прогноз 26.10"), (opt, "sc", f"по SLA от аудита 15.10: {P.fmt(opt)}"), (cons, "sc", f"по SLA от конца багфикса 22.10: {P.fmt(cons)}")]),
    ]
    return m, rows, plan_prod, sla_total, opt, cons, tail_a


def col_texts(name, plan, bars, marks):
    """Тексты колонок «план» и «факт» для строки диаграммы."""
    pt = [f"{dd(*plan)} · {dur(*plan)} дн."] if plan else ["—"]
    if name == "Деплой в Прод":
        pt = [f"{P.fmt(plan[0])} (по SLA)", "в таблице: 25 авг"]
        return pt, ["прогноз 26 окт", f"{wdb(START, Dt(26, 10))} раб. дн. от старта"]
    if bars:
        if len(bars) > 1:
            ft = [f"{dd(a, b)} · {dur(a, b)} дн." for a, b, _ in bars]
        else:
            a, b, _ = bars[0]
            ft = [f"{dd(a, b)} · {dur(a, b)} дн."]
        return pt, ft
    pts = [mk for mk in marks if mk[1] in ("ok", "warn")]
    return pt, [f"{P.fmt(mk[0])} · {mk[2].split(' (')[0]}"[:34] for mk in pts][:2] or ["—"]


def svg(rows, m) -> str:
    d0, d1 = date(2026, 7, 30), date(2026, 11, 26)
    L, W, rh = 600, 1450, 38
    days = (d1 - d0).days
    k = (W - L - 20) / days
    X = lambda d: L + (d - d0).days * k
    H = 44 + len(rows) * rh + 40
    out = [f'<svg class="chart" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Диаграмма Ганта EARM 26.2">']
    out.append('<text x="206" y="32" font-size="10" font-weight="700" fill="#140093" letter-spacing=".06em">ПЛАН ПО SLA</text><text x="388" y="32" font-size="10" font-weight="700" fill="#140093" letter-spacing=".06em">ФАКТ</text>')
    d = date(2026, 8, 1)
    while d < d1:
        nm = date(d.year + (d.month == 12), d.month % 12 + 1, 1)
        out.append(f'<line x1="{X(d):.1f}" x2="{X(d):.1f}" y1="14" y2="{H - 30}" stroke="#DDE3EE"/><text x="{X(d) + 4:.1f}" y="12" font-size="11" font-weight="700" fill="#140093">{P.MONTHS_FULL[d.month - 1]}</text>')
        d = nm
    w = d0 + timedelta(days=(7 - d0.weekday()) % 7)
    while w < d1:
        out.append(f'<line x1="{X(w):.1f}" x2="{X(w):.1f}" y1="20" y2="{H - 30}" stroke="#F0F2F6"/><text x="{X(w) + 1:.1f}" y="30" font-size="8" fill="#8A9BB5">{w.day}</text>')
        w += timedelta(days=7)
    for i, (name, plan, bars, marks) in enumerate(rows):
        y = 44 + i * rh
        if i % 2 == 0:
            out.append(f'<rect x="0" y="{y}" width="{W}" height="{rh}" fill="#F8F9FC"/>')
        out.append(f'<text x="198" y="{y + 22}" font-size="12" text-anchor="end" fill="#1B1B3A" font-weight="700">{e(name)}</text>')
        pt, ft = col_texts(name, plan, bars, marks)
        for j, t in enumerate(pt):
            out.append(f'<text x="206" y="{y + 16 + j * 13}" font-size="10.5" fill="#42526E">{e(t)}</text>')
        for j, t in enumerate(ft):
            out.append(f'<text x="388" y="{y + 16 + j * 13}" font-size="10.5" fill="#140093" font-weight="700">{e(t)}</text>')
        if plan:
            a, b = plan
            out.append(f'<rect x="{X(a):.1f}" y="{y + 6}" width="{max((b - a).days * k + k, 4):.1f}" height="8" rx="1" fill="#C7D4DE"><title>план по SLA {P.fmt(a)} – {P.fmt(b)} · {dur(a, b)} раб. дн.</title></rect>')
        for a, b, lab in bars:
            out.append(f'<rect x="{X(a):.1f}" y="{y + 20}" width="{max((b - a).days * k + k, 4):.1f}" height="12" rx="2" fill="#140093" opacity=".88"><title>факт {P.fmt(a)} – {P.fmt(b)} · {wdb(a, b)} раб. дн.</title></rect>')
            lab2 = (lab + " · " if lab else "") + f"{dur(a, b)} дн."
            bw = max((b - a).days * k + k, 4)
            if bw < len(lab2) * 5.6 + 30 or marks:
                out.append(f'<text x="{X(a) + bw + 12:.1f}" y="{y + 30}" font-size="10" font-weight="700" fill="#140093">{e(lab2)}</text>')
            else:
                out.append(f'<text x="{X(a) + 16:.1f}" y="{y + 30}" font-size="10" font-weight="700" fill="#fff">{e(lab2)}</text>')
        for dt, kind, lab in marks:
            x, cy = X(dt) + k / 2, y + 26
            tip = f"<title>{e(lab)}</title>"
            if kind == "ok":
                out.append(f'<circle cx="{x:.1f}" cy="{cy}" r="6" fill="#63BA3C" stroke="#fff" stroke-width="1.5">{tip}</circle>')
            elif kind == "sent":
                out.append(f'<circle cx="{x:.1f}" cy="{cy}" r="5" fill="#4BADE8" stroke="#fff" stroke-width="1.5">{tip}</circle>')
            elif kind == "no":
                out.append(f'<g>{tip}<circle cx="{x:.1f}" cy="{cy}" r="6" fill="#E5493A" stroke="#fff" stroke-width="1.5"/><path d="M{x - 3:.1f} {cy - 3} l6 6 M{x + 3:.1f} {cy - 3} l-6 6" stroke="#fff" stroke-width="1.6"/></g>')
            elif kind == "warn":
                out.append(f'<path d="M{x:.1f} {cy - 7} l7 7 l-7 7 l-7 -7 z" fill="#FBAE40" stroke="#fff" stroke-width="1.2">{tip}</path>')
            elif kind == "plan":
                out.append(f'<path d="M{x:.1f} {cy - 7} l7 7 l-7 7 l-7 -7 z" fill="#fff" stroke="#140093" stroke-width="2">{tip}</path>')
            elif kind == "old":
                out.append(f'<g>{tip}<path d="M{x:.1f} {cy - 6} l6 6 l-6 6 l-6 -6 z" fill="#C7D4DE"/><line x1="{x - 7:.1f}" x2="{x + 7:.1f}" y1="{cy}" y2="{cy}" stroke="#E5493A" stroke-width="1.6"/></g>')
            elif kind == "fc":
                out.append(f'<path d="M{x:.1f} {cy - 8} l8 8 l-8 8 l-8 -8 z" fill="#F26B43" stroke="#fff" stroke-width="1.5">{tip}</path>')
            if kind in ("plan", "fc", "sc", "old") and dt != Dt(14, 10):
                out.append(f'<text x="{x:.1f}" y="{y + 9}" font-size="9" font-weight="700" text-anchor="middle" fill="{"#F26B43" if kind == "fc" else "#904EE2" if kind == "sc" else "#140093" if kind == "plan" else "#8A9BB5"}">{P.fmt(dt)}</text>')
            if kind == "sc":
                out.append(f'<path d="M{x:.1f} {cy - 7} l7 7 l-7 7 l-7 -7 z" fill="#904EE2" stroke="#fff" stroke-width="1.2">{tip}</path>')
    tx = X(TODAY) + k / 2
    out.append(f'<line x1="{tx:.1f}" x2="{tx:.1f}" y1="14" y2="{H - 30}" stroke="#E5493A" stroke-width="2"/><text x="{tx + 4:.1f}" y="{H - 34}" font-size="10" font-weight="700" fill="#E5493A">сегодня 22 окт</text>')
    lg = [("#C7D4DE", "план по SLA от 03.08", "r"), ("#140093", "факт (полоса)", "r"), ("#4BADE8", "отправили на аудит", "c"), ("#63BA3C", "согласовали / пройдено", "c"),
          ("#E5493A", "не согласовали", "c"), ("#FBAE40", "причина сдвига", "d"), ("#F26B43", "текущий прогноз Прод", "d"), ("#904EE2", "прогноз по SLA", "d")]
    lx = 206
    for col, t, sh in lg:
        out.append(f'<rect x="{lx}" y="{H - 22}" width="11" height="11" fill="{col}" rx="{5 if sh == "c" else 1}"/><text x="{lx + 16}" y="{H - 13}" font-size="10" fill="#333">{t}</text>')
        lx += 152
    return "".join(out) + "</svg>"


def example_html() -> str:
    m, rows, plan_prod, sla_total, opt, cons, tail_a = build()
    pp = Dt(25, 8)
    prog = Dt(26, 10)
    plan_wd, fact_wd = wdb(START, pp), wdb(START, prog)
    kp = ('<div class="kpis">'
          f'<div class="kpi"><b>{plan_wd}</b><span>раб. дней в плане таблицы</span><small>03.08 → 25.08 (план выхода в Прод)</small></div>'
          f'<div class="kpi"><b>{sla_total[0]:g}–{sla_total[1]:g}</b><span>раб. дней по нашим SLA</span><small>от старта спринта до деплоя в Прод (без ПСИ — с ПСИ)</small></div>'
          f'<div class="kpi bad"><b>{fact_wd}</b><span>раб. дней по текущему прогнозу</span><small>03.08 → 26.10; прогноз сдвигали 4 раза</small></div>'
          f'<div class="kpi bad"><b>+{wdb(pp, prog)}</b><span>раб. дней сдвиг Прода</span><small>план 25.08 → прогноз 26.10</small></div></div>')
    stages = [
        ("Ветка → фича-фриз (спринт)", "10", Dt(3, 8), Dt(11, 8), "спринт сжат: фича-фриз 11.08 вместо конца 2-недельного спринта"),
        ("Регресс UAT, итерация 1", "3", Dt(12, 8), Dt(24, 8), "регресс растянут; найденные дефекты ушли в багфикс"),
        ("Пауза между итерациями регресса", "—", Dt(24, 8), Dt(5, 10), "ожидание исправлений: регресс стоит, пока фича-команды правят баги"),
        ("Регресс UAT, итерация 2", "3", Dt(5, 10), Dt(12, 10), "повторный регресс после исправлений"),
        ("Устранение багов UAT", "3", Dt(24, 8), Dt(22, 10), "закончили по 2 итерациям; критический путь факта"),
        ("Устранение уязвимостей", "3", Dt(11, 8), Dt(15, 10), "«2 месяца на уязвимости» (причина 5); идёт параллельно багам"),
        ("Техсессия и очное демо", "в спринте", Dt(9, 9), Dt(2, 10), "отдельный этап вне процесса (причина 4)"),
        ("Аудит кода: первая отправка → последнее согласование", "5", Dt(7, 9), Dt(15, 10), "SAST и Секреты не согласованы с первого раза; брони ИБ не было 21.09"),
        ("Старт аудита после фича-фриза", "5 (после Smoke UAT)", Dt(11, 8), Dt(7, 9), "ИБ получила код только через 4 недели после фича-фриза — аудит не был забронирован"),
        ("Выход в Прод: план → текущий прогноз", "—", Dt(25, 8), Dt(26, 10), "прогноз сдвигался 09.09 → 12.10 → 14.10 → 26.10"),
    ]
    tr = []
    for name, sla, a, b, note in stages:
        v = dur(a, b) if name not in ('Пауза между итерациями регресса', 'Старт аудита после фича-фриза', 'Выход в Прод: план → текущий прогноз') else wdb(a, b)
        if name == 'Пауза между итерациями регресса':
            v = dur(P.add_wd(a, 1), P.add_wd(b, -1))
        tr.append([name, sla, f"{P.fmt(a)} – {P.fmt(b)}", f"<td><b>{v}</b></td>", note])
    tbl = S.tbl(["Этап", "SLA, раб. дн.", "Факт: период", "Факт, раб. дн.", "Что произошло"], tr)
    shifts = S.ul([
        "03.08 — одна ветка develop/26.2 на старте релиза: два релиза (26.2.1 и 26.2.2) шли одним потоком, спринт сжат до 7 рабочих дней.",
        "13.08 — финализация релизного тикета уже после старта (должна быть до сбора ветки).",
        "11.08 – 15.10 — «2 месяца на уязвимости»: устранение уязвимостей шло весь период вместо 3 дней по SLA.",
        "21.09 — нет брони ИБ: окно на аудит не было заранее заложено в календарь.",
        "09.09 – 02.10 — техсессия и очное демо вне процесса; в новой модели демо проводит QA, принимает ВНП внутри спринта.",
    ])
    wnd = ("<div class='verdict'><b>Реалистичный выход в Прод.</b> Текущий прогноз 26.10 всего на "
           f"{wdb(Dt(15, 10), Dt(26, 10))} рабочих дней позже последнего согласования аудита (15.10), тогда как оставшаяся цепочка по SLA "
           f"(согласование трансфера 5 дн., уведомление ГПН, выкатка и регресс на PreProd, отчёт, организация уведомления, деплой) занимает {tail_a} рабочих дней — это <b>{P.fmt(opt)}</b>. "
           f"Если после завершения багфикса 22.10 понадобятся повторные Smoke UAT и аудит, цикл по SLA даст <b>{P.fmt(cons)}</b>. Прогноз 26.10 при текущем состоянии не достижим.</div>")
    insights = S.ol([
        f"План выхода в Прод 25.08 заложен на {plan_wd} раб. дней; цикл по SLA — {sla_total[0]:g}–{sla_total[1]:g}. Даты релиза надо считать от SLA этапов, а не задавать произвольно.",
        "Потери по этапам: багфикс и уязвимости растянулись на 44–48 раб. дней вместо 3, пауза регресса — 29 дней, аудит — 28 дней вместо 5.",
        "Аудит ИБ стартовал на 4 недели позже фича-фриза: нужна бронь окон ИБ в годовом календаре (раздел «Стратегическое планирование»).",
        "SAST и Секреты не согласованы с первого раза: уязвимости закрываются в спринте (CI на каждый PR), финальный скан по тегу — контроль перед релиз-бордом.",
        "Два релиза одной веткой (26.2.1 + 26.2.2) нарушили правило «один релиз — один тег и один набор дат»: сдвиг одного тянет второй.",
        "ПСИ ИБ пройдено 03.09 — в фактическом порядке раньше аудита, в модели ПСИ идёт после функционального тестирования; порядок стоит подтвердить.",
    ])
    note = ("<p class='muted'>Источник — таблица календаря релизов (ДК). Ячейки с датами объединены на строки EARM 26.2.1 и 26.2.2, поэтому они разобраны как один поток с общими датами. "
            "Не видно на скриншотах: нижняя часть списка причин сдвига, столбцы «Код фриз», PProd и «Риски» пустые. Если у 26.2.2 свои даты — пришлите, разнесу по двум строкам. "
            "План по SLA построен от старта 03.08 с учётом ПСИ ИБ (график — серые полосы).</p>")
    return ("<p>Пример применения модели к реальным релизам: на диаграмме Ганта — план по нашим SLA от 03.08 и факт из календаря релизов по этапам, "
            "вехи аудита, причины сдвига и прогнозы выхода в Прод.</p>" + note + kp + '<div class="card" style="overflow:auto">' + svg(rows, m) + "</div>"
            + "<h3>Сроки по этапам: SLA и факт</h3>" + tbl + "<p class='muted'>Длительность — рабочие дни периода, включая первый и последний день; для паузы — дни простоя между итерациями, для «старта аудита» и «выхода в Прод» — рабочих дней между датами.</p>" + "<h3>Причины сдвига</h3>" + shifts + wnd + "<h3>Выводы</h3>" + insights)
