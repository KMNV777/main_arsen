#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTML-блоки (таблицы и тексты) итоговой редакции процесса — общие для отчёта и пакета для Confluence."""

from __future__ import annotations

from html import escape as e
from typing import List

import process_data as D


def tbl(head: List[str], rows: List[List[str]], widths: List[int] | None = None) -> str:
    h = "".join(f"<th>{e(x)}</th>" for x in head)
    body = ""
    for r in rows:
        body += "<tr>" + "".join(c if c.startswith("<t") else f"<td>{e(c)}</td>" for c in r) + "</tr>"
    return f'<div class="tw"><table class="confluenceTable"><tbody><tr>{h}</tr>{body}</tbody></table></div>'


def ul(items: List[str]) -> str:
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def ol(items: List[str]) -> str:
    return "<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>"


def doers_text(n: int) -> str:
    s = D.SN[n]
    names = [D.role_name(c) for c in s[4]]
    return "; ".join(names)


def registry_html() -> str:
    rows: List[List[str]] = []
    last = 0
    for n, ph, name, a, doers, grp, sla, given, text in D.STEPS:
        if ph != last:
            rows.append([f'<td colspan="5"><b>{e(D.PHASES[ph])}</b></td>'])
            last = ph
        par = " (параллельно)" if grp else ""
        rows.append([f"<td><b>{n}</b></td>", name + par, D.role_name(a), doers_text(n), D.sla_text(n) + ("" if given else " *")])
    return (tbl(["№", "Этап", "Ответственный", "Исполнители", "SLA"], rows)
            + "<p class='muted'>* SLA предложен — в вашем перечне для этого этапа значения нет; подтвердить.</p>")


def steps_text_html() -> str:
    out = []
    last = 0
    for n, ph, name, a, doers, grp, sla, given, text in D.STEPS:
        if ph != last:
            out.append(f"<h3>{e(D.PHASES[ph])}</h3>")
            last = ph
        out.append(f"<p><b>{n}. {e(name)}</b> — SLA: {e(D.sla_text(n))}{'' if given else ' (предложение)'}.<br>"
                   f"Ответственный: {e(D.role_name(a))}. Исполнители: {e(doers_text(n))}.<br>{e(text)}</p>")
    return "".join(out)


def sla_html() -> str:
    return ("<p>Для каждого этапа указан текст: что делается, кто отвечает и кто исполняет; SLA — рабочие дни. Значения из вашего перечня: сбор тикета 1 день, сбор ветки 1 день, спринт 2 недели, "
            "регресс 3 дня, устранение багов и уязвимостей 3 дня, Smoke UAT 2 дня, аудит 5 дней, согласование трансфера 5 дней, регресс на PreProd 3 дня; "
            "остальные значения — предложение (помечены в таблице этапов).</p>"
            + steps_text_html() + "<h3>Критический путь</h3><p>" + e(D.critical_path_text()) + "</p>")


def roles_text_html() -> str:
    out = ["<p>Для каждой роли — кто это, что она делает в релизном цикле и какие полномочия даёт карточка роли. Этапы, за которые роль отвечает, и этапы, где она исполнитель, выведены из таблицы этапов.</p>"]
    for code in D.ROLES:
        name, contour, fio = D.ROLES[code]
        resp = [f"{n}. {D.STEP_NAME[n]}" for n in D.SN if D.SN[n][3] == code]
        doing = [f"{n}. {D.STEP_NAME[n]}" for n in D.SN if code in D.SN[n][4] and D.SN[n][3] != code]
        parts = [f"<h3>{e(name)}{' — ' + e(fio) if fio and fio != '—' else ''}</h3>", f"<p>{e(D.ROLE_AUTH[code])}</p>"]
        parts.append("<p><b>Отвечает за этапы:</b> " + (e("; ".join(resp)) if resp else "—") + "</p>")
        if doing:
            parts.append("<p><b>Исполняет:</b> " + e("; ".join(doing)) + "</p>")
        out.append("".join(parts))
    return "".join(out)


def decisions_html() -> str:
    return tbl(["Шаг", "Ответственный"], [[a, b] for a, b in D.DECISIONS])


def roadmap_html() -> str:
    rows = [[n, r, s, c] for n, steps, r, s, c in D.STAGES]
    return tbl(["Этап", "Ответственный", "SLA", "Контур"], rows)


def branches_html() -> str:
    return ("<p>Предлагается отойти от параллельных release-веток: сервисы живут в отдельных репозиториях, поэтому основа — один master на репозиторий, а релиз обозначается git-тегом с ID релиза "
            "(как в ядре Linux). Для сложных фич — опциональные агрегирующие (супер-фича) ветки. Схема — страница 2.</p>"
            + tbl(["Тема", "Правило"], [[a, b] for a, b in D.BRANCH_RULES])
            + "<p class='muted'>Риск схемы: пока предыдущий релиз стабилизируется, в master уже идёт работа следующего спринта — её нужно вести за feature flag или в супер-фича-ветке. "
              "Если это неприемлемо для сервиса, запасной вариант — короткоживущая ветка от тега релиза на время стабилизации. Подтвердить (см. «Нужно подтвердить»).</p>")


def metrics_html() -> str:
    return tbl(["Метрика", "Влияние", "Формула", "Ответственный"], [list(m) for m in D.METRICS])


def resolved_html() -> str:
    return tbl(["Расхождение", "Как устранено в итоговой схеме", "Документ"], [list(r) for r in D.RESOLVED])


def confirm_html() -> str:
    return ul([e(x) for x in D.CONFIRM])


def jira_html() -> str:
    return ul([
        "<b>Релизный Epic</b> на квартал — обязательный объём спринтов (как в эталоне). <b>Fix Version</b> — состав релиза: только Story и Bug.",
        "<b>Задача этапа</b> (Enabler/Task в Релизном Epic с fixVersion) на каждый этап таблицы: оценка, исполнитель, результат; возврат — новая задача того же этапа со ссылкой «Возврат из».",
        "<b>Подзадача сервиса</b> для этапов, которые выполняются по сервису (влитие задач, тег релиза, устранение багов и уязвимостей, выкатка): обязательное поле «Сервис».",
        "Workflow задачи: Ожидает → В работе → Готово; старт и финиш — источник времени этапа и ожидания.",
        "Календарь и паспорт релиза в Confluence — витрина для менеджмента; источник метрик — Jira.",
    ])


def overview_html() -> str:
    return (f"<p>Итоговая редакция процесса выпуска релиза ЕАРМ: {D.N_STEPS} этапов, пронумерованных от 1, с явной последовательностью и параллельностью. "
            "Код и релизы — trunk-схема (master и теги). Ответственные — роли той компании, где идёт процесс; релиз-инженер НЕДРА отвечает за инициацию релиз-борда и уведомления. "
            "Все расхождения между эталоном, Политикой, ДК, доступами и ролевой моделью устранены в итоговой схеме.</p>"
            '<div class="grid"><div class="card"><b>Принятые решения</b>'
            + ul(["Планирование: приоритеты ВНП → оценка РП с командой → релизный тикет → подтверждение состава ВНП.",
                  "Спринт: параллельно разработка, скан и устранение уязвимостей в CI, тестирование, release notes; затем демо (QA проводит, ВНП принимает).",
                  "Не принятые на демо задачи выводятся из релиза до тега; фича-фриз = тег релиза в последний день спринта.",
                  "Релиз-борд по порядку борда: аудит → выкатка на UAT → функциональное тестирование → решение о ПСИ → согласование трансфера.",
                  "Go/No-Go нет: релиз идёт в Прод всегда; критические дефекты — в hotfix.",
                  "Smoke PROD, БД и брокеры — параллельно; на этапе Прода только организация уведомления.",
                  "Ёмкость QA планируется за вычетом резерва на регресс и Smoke предыдущего релиза."])
            + '</div><div class="card"><b>Как читать материалы</b>'
            + ul(["Схема 1 — последовательность и параллельность по зонам ответственности.", "Схема 2 — код и релизы: master, теги, супер-фича-ветки.",
                  "Схема 3 — дорожная карта: этапы, ответственные, SLA.", "Схема 4 — Jira и метрики.", "Схемы 5–7 — дорожная карта релизов, стратегическое планирование, экономика.",
                  "Описательная часть (тексты этапов, код и релизы, Jira, политика, ДК, доступы) — в отдельном HTML для Confluence."])
            + "</div></div>")


def roles_table_html() -> str:
    rows = []
    for code, (name, contour, fio) in D.ROLES.items():
        comp, who, does, notdo = D.ROLE_DESC[code]
        rows.append([f"<td><b>{e(name)}</b></td>", comp, who, does, notdo, fio if fio and fio != "—" else "—"])
    return tbl(["Роль", "Компания", "Кто это", "Что делает в релизном цикле", "Чем не занимается", "Кто сейчас"], rows)


def roles_matrix_html() -> str:
    """Матрица «роль × этап»: О — ответственный, И — исполнитель."""
    phase_cols = {}
    for n in D.SN:
        phase_cols[D.SN[n][1]] = phase_cols.get(D.SN[n][1], 0) + 1
    h1 = "<tr><th rowspan='2' class='rl'>Роль</th><th rowspan='2'>Контур</th>" + "".join(f"<th colspan='{c}' class='ph{p}'>{e(D.PHASES[p])}</th>" for p, c in phase_cols.items()) + "<th rowspan='2'>Отв.</th><th rowspan='2'>Исп.</th></tr>"
    h2 = "<tr>" + "".join(f"<th class='sn' title='{n}. {e(D.STEP_NAME[n])}'>{n}</th>" for n in D.SN) + "</tr>"
    rows = ""
    for code, (name, contour, fio) in D.ROLES.items():
        cells, a, d = "", 0, 0
        for n in D.SN:
            if D.SN[n][3] == code:
                cells += f"<td class='mO' title='{n}. {e(D.STEP_NAME[n])} — ответственный'>О</td>"
                a += 1
            elif code in D.SN[n][4]:
                cells += f"<td class='mI' title='{n}. {e(D.STEP_NAME[n])} — исполнитель'>И</td>"
                d += 1
            else:
                cells += "<td></td>"
        rows += f"<tr><td class='rl' title='{e(fio)}'><b>{e(name)}</b></td><td>{e(contour)}</td>{cells}<td><b>{a}</b></td><td>{d}</td></tr>"
    legend = "<p class='muted'><b>О</b> — ответственный за этап (принимает результат), <b>И</b> — исполнитель. Один этап — один ответственный. Наведите курсор на номер этапа или ячейку — появится название; на роль — ФИО.</p>"
    steps = "<div class='stl'>" + "".join(f"<span><b>{n}</b> {e(D.STEP_NAME[n])}</span>" for n in D.SN) + "</div>"
    return legend + f"<div class='mx'><table class='rmx'><thead>{h1}{h2}</thead><tbody>{rows}</tbody></table></div>" + steps
