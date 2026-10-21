#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Готовые тексты для Confluence (HTML) по итоговой редакции процесса выпуска релиза ЕАРМ.

Данные — scripts/process_data.py, блоки — scripts/sections.py (те же, что в общем отчёте).
Результат — docs/confluence/confluence-pages.html: блоки ".page", каждый копируется кнопкой.
"""

from __future__ import annotations

from html import escape as e
from pathlib import Path

import process_data as D
import sections as S
import trz_model as T

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "confluence" / "confluence-pages.html"

POLICY_OLD = [
    "К релизным тикетам прикрепляются только Истории и Баги.",
    "В релизный тикет не попадают сущности «Задачи на QA» и отдельные задачи на BE и FE.",
    "В начале каждого спринта создаётся релизная ветка <b>от master</b>, в которую включаются задачи, которые команда планирует закрыть за спринт.",
    "Релизы КФА и ИНФРА идут под общим названием ЕАРМ.",
    "Задачи без тест-кейсов не попадают в релиз.",
    "Каждый мейнтейнер сервиса устраняет уязвимости по ходу спринта (SAST, SCA, Luntry, секреты). Подробнее: «Регламенты по устранению уязвимостей».",
    "Тест-планы на регресс UAT собираются в ТестОпс НЕДРА.",
    "Тест-планы для регресса PProd собираются в ТестОпс ГПН-ЦР для передачи команде сервиса.",
    "Каждая команда предоставляет скрипты миграции при передаче релиза.",
    "К каждой Story прикрепляется кодовый инкремент.",
    "Перед каждым релизом создаётся страница, куда мейнтейнеры сервисов вносят информацию по своим сервисам («ЕАРМ 2-х недельные релизы»).",
    "Под каждый релиз заводится страница с результатами сканирований по уязвимостям («Результаты сканирования»).",
]
DIRECTIONS = [["ЕАРМ1", "Алина Ганеева", "Карина Нежинская"], ["ЕАРМ2", "Шестаков Александр", "Алексей Ковальчук"], ["ЕАРМ3", "Овсепян Эрик", "не указан"],
              ["ЕАРМ4", "Артем Киян", "Алексей Нестеров"], ["ЕАРМ5", "Артем Занчаров", "не указан"], ["ЕАРМ6", "Михаил Гудилов", "Алексей Нестеров"]]


def page_etalon() -> str:
    return "".join([
        "<h1>Эталонный процесс выпуска релиза ЕАРМ (итоговая редакция)</h1>", S.overview_html(),
        "<h2>1. Участники и роли</h2>", S.roles_text_html(),
        "<h2>2. Этапы процесса</h2><p>Этапы пронумерованы от 1; параллельные этапы помечены. Схема последовательности — страница 1 файла 10-release-process.drawio.</p>", S.registry_html(),
        "<h2>3. Тексты этапов, SLA и критический путь</h2>", S.sla_html(),
        "<h2>4. Релиз-борд</h2><p>Цепочка автоматизирована и находится в зоне ответственности релиз-инженера НЕДРА: аудит → выкатка на UAT → функциональное тестирование → "
        "ПСИ ИБ (если не нужен — пропускается сразу, если нужен — загружается документ) → согласование трансфера на ПРОД (этапы 15–19).</p>",
        "<h2>5. Ведение веток</h2>", S.branches_html(),
        "<h2>6. Дорожная карта: ответственные и SLA</h2>", S.roadmap_html(),
        "<h2>7. Решения по шагам</h2>", S.decisions_html(),
        "<h2>8. Учёт в Jira</h2>", S.jira_html(),
        "<h2>9. Метрики</h2>", S.metrics_html(),
        "<h2>10. Hotfix</h2><p>Критические дефекты, найденные после регресса на PreProd, исправляются hotfix по тому же процессу; на самом PreProd допустимы только правки уровня helm.</p>"])


def page_policy() -> str:
    new = "".join(f"<li>{x}</li>" for x in D.RULES)
    return "".join([
        "<h1>Релизная политика ЕАРМ (итоговая редакция)</h1>",
        "<h2>Общие правила</h2><p>Правила 1–12 сохранены; правила 13–%d добавлены.</p>" % (12 + len(D.RULES)),
        S.ol(POLICY_OLD), f'<ol start="13">{new}</ol>',
        "<h2>Графическое представление</h2><p>Заменить рисунок схемой «Процесс выпуска релиза ЕАРМ» (10-release-process.drawio, страница 1) и схемой веток (страница 2).</p>",
        "<h2>Зоны ответственности по этапам</h2>", S.registry_html(),
        "<h3>ВНП и РП по направлениям</h3>", S.tbl(["Направление", "ВНП", "РП"], DIRECTIONS),
        "<p>ИБ ГПН — Томшинский Антон (аудит, ПСИ ИБ, согласование трансфера).</p>",
        "<h2>Ведение веток</h2>", S.branches_html(),
        "<h2>Hotfix</h2><p>Тот же процесс; ветка hotfix/* от ветки Прода.</p>"])


MILESTONES = [("Релизный тикет", 2), ("Релизная ветка", 3), ("Фича-фриз", 7), ("Регресс UAT", 8), ("Скан уязвимостей", 9), ("Код-фриз", 13), ("Smoke UAT", 14),
              ("Аудит", 15), ("Согласование трансфера", 19), ("Регресс PreProd", 23), ("Деплой Прод", 27)]
DK_ROWS = ["ДАРС 14.2", "ИНФРА 06", "EARM26.2.1", "EARM26.2.2", "EARM26.3.1", "EARM26.3.2", "EARM26.4.1", "EARM26.4.2", "EARM26.4.3", "EARM26.4.4", "СППР Релиз 1", "СППР Релиз 2"]


def page_dk() -> str:
    head = "<tr><th rowspan=\"2\">Релиз</th>" + "".join(f'<th colspan="2">{e(m)}<br>{e(D.role_name(D.SN[n][3]))}</th>' for m, n in MILESTONES) + "</tr>"
    head += "<tr>" + "<th>ПЛАН</th><th>ФАКТ</th>" * len(MILESTONES) + "</tr>"
    body = "".join("<tr><td><b>" + e(r) + "</b></td>" + "<td></td><td></td>" * len(MILESTONES) + "</tr>" for r in DK_ROWS)
    detail = S.tbl(["Релиз", "Сервис", "Этап", "Ответственный", "SLA", "Начало ПЛАН", "Начало ФАКТ", "Конец ПЛАН", "Конец ФАКТ", "Результат ✓ / ↩ / ✗", "Комментарий"],
                   [["⟨релиз⟩", "⟨сервис⟩", f"{n}. {D.STEP_NAME[n]}", D.role_name(D.SN[n][3]), D.sla_text(n), "", "", "", "", "", ""] for n in (3, 4, 9, 12, 13, 20, 27)])
    return "".join([
        "<h1>ДК выпуска релизов (версия 2)</h1>",
        "<p><b>Определение готовности задачи.</b> Задача реализована, протестирована на UAT, продемонстрирована QA и принята ВНП направления; для релиза нужны fixVersion, оценка, тест-кейсы, кодовый инкремент и скрипты миграции.</p>",
        "<h2>Что изменилось</h2>", S.ul(["Фича-фриз заменяет Scope freeze; добавлены столбцы релизной ветки, Smoke UAT, аудита и согласования трансфера.",
                                       "Сохранены ответственные прежней таблицы; столбцы правее «Регресс» в исходном PDF не читались — сверить при вставке.",
                                       "Вторая таблица — детализация «релиз × сервис × этап» с результатом."]),
        f'<h2>Таблица 1. Календарь релизов (ПЛАН / ФАКТ)</h2><table class="confluenceTable"><tbody>{head}{body}</tbody></table>',
        "<h2>Таблица 2. Детализация по сервисам</h2>", detail])


PREFLIGHT = [
    (9, "CI, сканеры SAST / SCA / Luntry / секреты", "Релиз-инженер НЕДРА, мейнтейнеры"),
    (8, "UAT-стенды, БД UAT, ТестОпс НЕДРА — по всем ДО релиза", "Lead QA и QA команд"),
    (11, "ТестОпс ГПН-ЦР", "Release owner, QA"),
    (15, "Релиз-борд, портал ББ", "Релиз-инженер НЕДРА; ИБ ГПН"),
    (19, "Система согласования трансфера образов", "ИБ ГПН; Release owner"),
    (20, "Jenkins / OKD PreProd", "DevOps, релиз-инженер НЕДРА"),
    (21, "БД PreProd / Prod", "Администратор БД"),
    (22, "Kafka PreProd / Prod", "Администратор брокеров"),
    (23, "PreProd-стенды, БД PreProd", "Release owner, сервис ГПН-ЦР"),
    (27, "Jenkins / OKD Prod", "Приходько Вадим, Акманов Арсен"),
    (28, "Мониторинг / логи (Grafana, N1, Elastic)", "Сервис ГПН-ЦР"),
]


def page_access() -> str:
    roles = [["Релиз-инженер НЕДРА (новая)", "ALM, Jenkins, Nexus, Релиз-борд, сканеры", "Dev, UAT, PreProd (чтение), Релиз-борд — полный"],
             ["Администратор БД (новая)", "PostgreSQL, ClickHouse, CloudBeaver", "Администрирование PreProd, Prod"],
             ["Администратор брокеров (новая)", "Kafka", "Администрирование PreProd, Prod"]]
    return "".join([
        "<h1>Доступы для релизов — правки</h1>",
        "<p>Матрицы по людям остаются без изменений. Release owner сверяет состав команды с матрицей за 3 рабочих дня до старта этапа.</p>",
        "<h2>1. Роли: добавить</h2>", S.tbl(["Роль", "Основные системы", "Уровень доступа"], roles),
        "<h2>2. Проверка доступов до старта этапа</h2>", S.tbl(["Этап", "Система", "Кому"], [[f"{n}. {D.STEP_NAME[n]}", a, b] for n, a, b in PREFLIGHT]),
        "<h2>3. Выявлено в текущих матрицах</h2>", S.ul([
            "Релиз-инженера НЕДРА Юрченко Дмитрия нет в матрицах доступов.",
            "У Грей Алексея проектные доступы к сегментам и БД UAT / PreProd / Prod — «−».",
            "Часть QA имеет доступ к UAT только по Оренбургу — ограничено покрытие регресса.",
            "В таблице ролей нет администраторов БД и брокеров."])])


def page_trz() -> str:
    base = T.compute()
    tot = T.totals(base)
    rows = [[T.ROLE_NAME[r], f"{base[r]['fte']:.2f}", "по ставке роли"] for r in T.ROLE_ORDER]
    rows.append(["<td><b>Итого</b></td>", f"<td><b>{tot['fte']:.2f}</b></td>", "<td></td>"])
    return "".join(["<h1>Приложение: калькулятор ТРЗ</h1>",
                    f"<p>Расчёт при N = {T.PARAMS['N'][0]} сервисах (допущение). FTE = ТРЗ за год / (часы × 0,8). Стоимость = ТРЗ × ставка роли; ставки в текст не включаются — вводятся в калькуляторе (общий отчёт) или Excel.</p>",
                    S.tbl(["Роль", "FTE", "Стоимость"], rows)])


def page_changes() -> str:
    return "<h1>Реестр правок и снятых расхождений</h1>" + S.resolved_html() + "<h2>Нужно подтвердить</h2>" + S.confirm_html()


def page_strategy() -> str:
    import planning as PL
    rels = PL.releases()
    rules = [x for x in ("Календарь релизов утверждается на скользящий год и пересматривается раз в квартал вместе с Релизным Epic.",
                         "Старт релиза допускается, только если у РИ, ИБ и QA в окне этапов запас по загрузке; иначе релиз сдвигается на спринт.",
                         "ПСИ ИБ закладывается в окно до старта релиза; релиз с ПСИ не стартует параллельно другому релизу с ПСИ.",
                         "Окна без релизных работ: новогодние и длительные майские праздники.",
                         "Сдвиг релиза — решение Release owner по согласованию с ВНП; причина фиксируется в календаре.")]
    return "".join(["<h1>Стратегическое планирование релизов</h1>",
                    f"<p>Каденс: квартал = 6 спринтов, релизов 3 (релизные спринты 2, 4, 6). Цикл релиза {D.total_days(False):g}–{D.total_days(True):g} рабочих дней; одновременно в работе до {PL.max_parallel(rels)} релизов. Даты ориентировочные (производственный календарь уточнить).</p>",
                    "<h2>Календарь релизов на скользящий год</h2>",
                    S.tbl(["Релиз", "Старт (тикет)", "Спринт", "Фича-фриз", "Код-фриз", "Аудит кода", "Трансфер согласован", "PreProd", "Деплой Прод", "Закрытие", "ПСИ ИБ"], PL.calendar_rows(rels)),
                    "<h2>Календарь по всем этапам цикла (дни)</h2><p>Даты «с – по»; колонка «Дн.» — длительность этапа в рабочих днях.</p>",
                    S.tbl(["№", "Этап", "Дн.", "Ответственный"] + [r["name"] for r in rels], PL.stage_matrix(rels)),
                    "<h2>Правила</h2>", S.ol(rules)])


def page_econ() -> str:
    base = T.compute()
    tot = T.totals(base)
    rows = []
    for r in T.ROLE_ORDER:
        b = base[r]["delta"]
        rows.append([T.ROLE_NAME[r], f"{base[r]['fte']:.2f}", f"{T.CURRENT_FTE:.1f}", f"{b:+.2f}", "избыток" if b > 0.2 * T.CURRENT_FTE else ("нехватка" if b < -0.2 * T.CURRENT_FTE else "норма")])
    rows.append(["<td><b>Итого</b></td>", f"<td><b>{tot['fte']:.2f}</b></td>", f"<td><b>{tot['current']:.1f}</b></td>", f"<td><b>{tot['current'] - tot['fte']:+.2f}</b></td>", "<td></td>"])
    return "".join(["<h1>Экономика и баланс ресурсов</h1>",
                    f"<p>Потребность роли: FTE = ТРЗ за год / (рабочие часы × 80 %). Сейчас каждая роль списывается как 1 FTE. Расчёт при N = {T.PARAMS['N'][0]} сервисах, {T.PARAMS['R'][0]} релизах в год (допущения); стоимость = FTE × часы года × ставка роли — ставки в текст не входят.</p>",
                    S.tbl(["Роль", "Нужно по ТРЗ, FTE", "Списано, FTE", "Баланс, FTE", "Вывод"], rows)])


def page_files() -> str:
    import base64

    def link(path: Path, label: str, mime: str, fname: str) -> str:
        b64 = base64.b64encode(path.read_bytes()).decode()
        return f'<li><a download="{fname}" href="data:{mime};base64,{b64}">{label}</a> <span class="muted">({path.stat().st_size // 1024} КБ)</span></li>'
    items = [link(ROOT / "docs/drawio/10-release-process.drawio", "Схема процесса (draw.io, 7 страниц) — редактируемый источник", "application/xml", "10-release-process.drawio"),
             link(ROOT / "docs/release-trz-fte.xlsx", "Модель ТРЗ и FTE по ролям (Excel, живые формулы)", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "release-trz-fte.xlsx")]
    return "<h1>Файлы для скачивания</h1><ul>" + "".join(items) + "</ul><p>Схема в draw.io: File → Open from → Device. Экспорт PNG/SVG страниц вставляется картинкой в Confluence.</p>"


PAGES = [
    ("etalon", "1. Эталонный процесс выпуска релиза", page_etalon),
    ("policy", "2. Релизная политика ЕАРМ", page_policy),
    ("strategy", "3. Стратегическое планирование релизов", page_strategy),
    ("dk", "4. ДК выпуска релизов (v2)", page_dk),
    ("access", "5. Доступы для релизов — правки", page_access),
    ("trz", "6. Приложение: калькулятор ТРЗ", page_trz),
    ("econ", "7. Экономика и баланс ресурсов", page_econ),
    ("changes", "8. Реестр правок", page_changes),
    ("files", "9. Файлы", page_files),
]

CSS = """
body{font:14px/1.5 Inter,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;color:#1B1B3A;max-width:1280px;margin:0 auto;padding:16px;background:#F4F6FB}
.bar{position:sticky;top:0;background:#140093;color:#fff;border-bottom:5px solid #CFF85E;padding:10px 14px;margin-bottom:12px;z-index:5}
.bar a{color:#CFF85E;margin-right:10px}.bar span{color:#AAC3E3}
.page{background:#fff;border:1px solid #D5DDEE;border-top:3px solid #140093;border-radius:3px;padding:8px 24px 24px;margin:16px 0}
.tools{margin:10px 0}button{background:#140093;color:#CFF85E;border:0;border-radius:3px;padding:6px 12px;cursor:pointer;font-weight:600}
button:hover{background:#FF7500;color:#fff}
table{border-collapse:collapse;margin:8px 0 16px}th,td{border:1px solid #C9D2E6;padding:4px 8px;vertical-align:top;text-align:left}
th{background:#140093;color:#fff}code{background:#F4F6FB;padding:0 3px}h1{font-size:26px;color:#140093}h2{font-size:20px;margin-top:26px;color:#140093;border-left:12px solid #CFF85E;padding-left:8px}h3{font-size:16px;color:#140093}
"""
JS = """
function cp(id,btn){var el=document.getElementById(id+'-body');var r=document.createRange();r.selectNodeContents(el);
var s=window.getSelection();s.removeAllRanges();s.addRange(r);var ok=false;try{ok=document.execCommand('copy')}catch(e){}
s.removeAllRanges();btn.textContent=ok?'Скопировано ✓':'Выделите и скопируйте вручную (Ctrl+C)';
if(!ok){s.addRange(r)}setTimeout(function(){btn.textContent='Копировать блок'},2500)}
"""


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    nav = "".join(f'<a href="#{i}">{e(t)}</a>' for i, t, _ in PAGES)
    blocks = ""
    for i, t, fn in PAGES:
        blocks += (f'<div class="page" id="{i}"><div class="tools"><b>{e(t)}</b> &nbsp; '
                   f'<button onclick="cp(\'{i}\',this)">Копировать блок</button></div><div id="{i}-body">{fn()}</div></div>')
    html = (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Confluence: процесс выпуска релиза ЕАРМ</title><style>{CSS}</style></head><body>'
            f'<div class="bar"><b>Пакет текстов для Confluence</b> · {nav}<br><span style="color:#5e6c84">Как вставить: нажмите «Копировать блок» '
            f'(или выделите блок мышью) → в Confluence откройте страницу в режиме редактирования → Ctrl+V. Таблицы, заголовки и списки сохраняются. '
            f'Схему вставьте картинкой (экспорт из draw.io).</span></div>{blocks}<script>{JS}</script></body></html>')
    OUT.write_text(html, encoding="utf-8")
    print("OK:", OUT, f"{len(html) // 1024} KB")


if __name__ == "__main__":
    main()
