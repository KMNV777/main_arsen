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
    return ("<p>Ведение релизных веток показано отдельной схемой (страница 2): старт спринта → создание релизной ветки → влитие задач → тестирование → фича-фриз в конце спринта. "
            "Что не успели — идёт в следующий релиз (следующий спринт). Допускается вести несколько релизных веток параллельно.</p>"
            + tbl(["Шаг", "Правило"], [[a, b] for a, b in D.BRANCH_RULES]))


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
        "<b>Подзадача сервиса</b> для этапов, которые выполняются по сервису (сбор ветки, влитие, устранение багов и уязвимостей, выкатка): обязательное поле «Сервис».",
        "Workflow задачи: Ожидает → В работе → Готово; старт и финиш — источник времени этапа и ожидания.",
        "Календарь и паспорт релиза в Confluence — витрина для менеджмента; источник метрик — Jira.",
    ])


def overview_html() -> str:
    return ("<p>Итоговая редакция процесса выпуска релиза ЕАРМ: 32 этапа, пронумерованные от 1, с явной последовательностью и параллельностью. "
            "Ветки вынесены на отдельную схему. Релиз-борд описан цепочкой автоматизированных шагов в зоне ответственности релиз-инженера НЕДРА. "
            "Все расхождения между эталоном, Политикой, ДК, доступами и ролевой моделью устранены (см. раздел «Расхождения и как они устранены»).</p>"
            '<div class="grid"><div class="card"><b>Принятые решения</b>'
            + ul(["Ветка — от master на старте спринта; допускается несколько веток параллельно.",
                  "Фича-фриз — в конце спринта; не успели — в следующий релиз (спринт). Scope freeze не используется.",
                  "Демо проводит QA, принимает ВНП.",
                  "Релиз-борд: аудит → выкатка на UAT → функциональное тестирование → ПСИ ИБ → согласование трансфера на ПРОД (ЗО релиз-инженера НЕДРА).",
                  "Go/No-Go нет: релиз идёт в Прод всегда; критические дефекты — в hotfix.",
                  "Smoke PROD, БД и брокеры — параллельно.",
                  "Hotfix — тот же процесс."])
            + '</div><div class="card"><b>Как читать материалы</b>'
            + ul(["Схема 1 — последовательность и параллельность по зонам ответственности.", "Схема 2 — ведение релизных веток.",
                  "Схема 3 — дорожная карта: этапы, ответственные, SLA.", "Схема 4 — Jira и метрики.",
                  "Таблицы и тексты — ниже, готовые описания для Confluence — в конце."])
            + "</div></div>")
