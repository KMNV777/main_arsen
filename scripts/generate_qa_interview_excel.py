#!/usr/bin/env python3
"""Generate QA interview evaluation workbook."""

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

THIN = Side(style="thin", color="CCCCCC")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
SUBHEADER_FILL = PatternFill("solid", fgColor="D9E2F3")
SECTION_FILL = PatternFill("solid", fgColor="E2EFDA")
WARN_FILL = PatternFill("solid", fgColor="FFF2CC")


def style_header_row(ws, row, cols, height=22):
    for c in range(1, cols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER
    ws.row_dimensions[row].height = height


def style_data_area(ws, start_row, end_row, cols):
    for r in range(start_row, end_row + 1):
        for c in range(1, cols + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=True)


def set_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def build_instructions(ws):
    ws.title = "Инструкция"
    set_widths(ws, [18, 90])
    rows = [
        ("Параметр", "Значение"),
        ("Должность", "QA Engineer | Web, Mobile, API (Middle / Senior / Lead)"),
        ("Длительность", "~90 минут"),
        ("Максимум баллов", "100 (+ практика граничных — опционально 10)"),
        ("Strong hire (Lead)", "85–100 + пороги Lead"),
        ("Hire (Senior)", "70–84"),
        ("Hire с оговорками", "55–69"),
        ("No hire", "< 55"),
        ("", ""),
        ("Шкала за вопрос (макс. 3)", "0 — нет ответа; 1 — с подсказками; 2 — верно с пробелами; 3 — полный + пример"),
        ("Подсказки", "После 2-й подсказки максимум 1 балл на вопрос"),
        ("Штрафы", "До −10 (лист «Штрафы»)"),
        ("Lead-пороги", "API ≥10/14; Процессы ≥9/12; Кейс ≥18/24"),
        ("", ""),
        ("Порядок проведения", "1) Знакомство 2) Теория 3) Web/API 4) Mobile 5) Кейс 6) Граничные (опц.) 7) Вопросы кандидату"),
        ("Файлы", "Листы: Вопросы, Кейсы, Граничные, Штрафы, Сводка, Карточка кандидата"),
    ]
    for i, (a, b) in enumerate(rows, 1):
        ws.cell(i, 1, a)
        ws.cell(i, 2, b)
    style_header_row(ws, 1, 2)
    ws["A1"].font = HEADER_FONT
    ws["B1"].font = HEADER_FONT


def build_questions(ws):
    ws.title = "Вопросы"
    headers = [
        "ID",
        "Блок",
        "Вопрос",
        "Макс.",
        "Балл",
        "3 балла (эталон)",
        "2 балла",
        "1 балл",
        "0 баллов",
        "Подсказки",
        "Комментарий",
    ]
    for c, h in enumerate(headers, 1):
        ws.cell(1, c, h)
    style_header_row(ws, 1, len(headers))

    questions = [
        ("1.1", "1. Теория", "Smoke / sanity / регресс / re-test — отличия и когда применять", 3,
         "Чёткие определения + пример из релиза/e-com",
         "Верно, без примера", "Путает 2 вида", "Не различает"),
        ("1.2", "1. Теория", "Техники тест-дизайна + пример для REST endpoint", 3,
         "≥3 техники + конкретные данные (limit, auth, пагинация)",
         "2 техники", "Только границы", "Не называет"),
        ("1.3", "1. Теория", "Как тестируете требования до разработки?", 3,
         "AC, негатив, NFR, аналитика, Figma, вопросы на груминге",
         "Читает ТЗ", "Общие слова", "Не делает review"),
        ("2.1", "2. Web", "DevTools при баге на UI — что смотрите?", 2,
         "Network + Console + сравнение со Swagger",
         "Только Network", "—", "Не знает"),
        ("2.2", "2. Web", "Кэш / устаревшие данные на UI", 2,
         "Headers, hard refresh, API/SQL сверка",
         "Только Ctrl+F5", "—", "—"),
        ("3.1", "3. Mobile", "Чем mobile отличается от web?", 3,
         "lifecycle, push, offline, OS, store, deep links",
         "3–4 пункта", "2 пункта", "Общие слова"),
        ("3.2", "3. Mobile", "Charles / Proxyman — зачем и как?", 3,
         "перехват, mock, pinning, retry, WebSocket",
         "Смотрю запросы", "Не пользовался", "—"),
        ("3.3", "3. Mobile", "Регресс перед релизом мобильного приложения", 4,
         "матрица устройств, build, go/no-go, метрики",
         "Чек-лист без критериев", "Нет процесса", "—"),
        ("4.1", "4. API", "REST: что проверяете помимо 200?", 4,
         "≥5 кодов + валидация + пагинация + auth",
         "3–4 кода", "Только 404", "—"),
        ("4.2", "4. API", "Тестирование через Kafka", 5,
         "event→эффект; дубликаты; DLQ; trace-id",
         "Отправка в топик", "Не знает Kafka", "—"),
        ("4.3", "4. API", "Локализация бага: фронт / API / сервис", 5,
         "Postman изоляция + логи + SQL + порядок шагов",
         "2 из 3", "Угадывает", "—"),
        ("5.1", "5. SQL", "Зачем QA SQL в микросервисах?", 2,
         "side-effects, данные, расследование, read-only prod",
         "Частично", "—", "Не нужен SQL"),
        ("5.2", "5. SQL", "Запрос: active подписки с expires_at < NOW()", 6,
         "Корректный SELECT WHERE; JOIN; осторожность на проде",
         "Идея верная, синтаксис", "Неверная логика", "—"),
        ("6.1", "6. Логи/NFR", "Поиск причины 500 в OpenSearch/Kibana", 4,
         "trace_id, сервис, ERROR, артефакты для dev",
         "время + уровень", "смотрю логи", "—"),
        ("6.2", "6. Логи/NFR", "NFR на highload e-com", 4,
         "таймауты, идемпотентность оплаты, rate limit, алерты",
         "нагрузочное тестирование", "—", "—"),
        ("7.1", "7. Процессы", "QA с нуля / QA Notes / тест-прогоны", 4,
         "процесс, TMS, DoD, метрики, пример внедрения",
         "без метрик", "общие слова", "—"),
        ("7.2", "7. Процессы", "Приоритизация багов перед релизом", 3,
         "severity×priority×blast radius×обходной путь",
         "только severity", "—", "—"),
        ("7.3", "7. Lead", "Как проводите собеседования (только Lead)", 3,
         "структура, компетенции, антибиас, фидбек",
         "без критериев", "—", "N/A Middle/Senior"),
        ("7.4", "7. Процессы", "Kanban vs Scrum", 2,
         "когда что + фокус на прозрачность, не название",
         "одно предпочтение", "—", "—"),
        ("8.1", "8. Python", "Где используете Python в QA?", 4,
         "API checks, данные, логи; ROI автоматизации",
         "писал немного", "—", "нет опыта"),
    ]

    row = 2
    for q in questions:
        qid, block, question, mx, s3, s2, s1, s0 = q
        ws.cell(row, 1, qid)
        ws.cell(row, 2, block)
        ws.cell(row, 3, question)
        ws.cell(row, 4, mx)
        ws.cell(row, 5, "")  # score - filled by interviewer
        ws.cell(row, 6, s3)
        ws.cell(row, 7, s2)
        ws.cell(row, 8, s1)
        ws.cell(row, 9, s0)
        ws.cell(row, 10, "")
        ws.cell(row, 11, "")
        row += 1

    last = row - 1
    style_data_area(ws, 2, last, len(headers))

    # Data validation for score column
    dv = DataValidation(
        type="whole",
        operator="between",
        formula1=0,
        formula2=10,
        allow_blank=True,
    )
    dv.error = "Введите целое число 0–10 (не больше «Макс.»)"
    ws.add_data_validation(dv)
    dv.add(f"E2:E{last}")

    set_widths(ws, [6, 14, 42, 6, 6, 28, 18, 14, 12, 10, 22])

    # Block subtotals reference for summary
    ws.cell(last + 2, 1, "ИТОГО вопросы")
    ws.cell(last + 2, 4, f"=SUM(D2:D{last})")
    ws.cell(last + 2, 5, f"=SUM(E2:E{last})")
    for c in range(1, 6):
        ws.cell(last + 2, c).font = Font(bold=True)


def build_cases(ws):
    ws.title = "Кейсы"
    headers = [
        "Кейс",
        "Критерий",
        "Макс.",
        "Балл",
        "6 баллов",
        "3 балла",
        "0 баллов",
        "Комментарий",
    ]
    for c, h in enumerate(headers, 1):
        ws.cell(1, c, h)
    style_header_row(ws, 1, len(headers))

    cases_a = [
        ("A. E-com подписка", "A1. План расследования", 6),
        ("A. E-com подписка", "A2. Инструменты (API/SQL/Kafka/логи)", 6),
        ("A. E-com подписка", "A3. Гипотезы (≥3)", 6),
        ("A. E-com подписка", "A4. Баг-репорт и риски релиза", 6),
    ]
    cases_b = [
        ("B. Mobile сообщение", "B1. Стратегия (не гадать)", 6),
        ("B. Mobile сообщение", "B2. Матрица тестов", 6),
        ("B. Mobile сообщение", "B3. Sync / push", 6),
        ("B. Mobile сообщение", "B4. Регресс после фикса", 6),
    ]

    rubric_6 = {
        "A1": "repro → id → время → окружение → артефакты",
        "A2": "API + SQL + Kafka + OpenSearch + Network",
        "A3": "race, mapper, cron, TZ, идемпотентность",
        "A4": "Critical/High, блокер hotfix, риск «деньги без услуги»",
        "B1": "проверка message_id в API для B",
        "B2": "другой клиент, аккаунт, сеть, версия, Web",
        "B3": "sync cursor, websocket, push token, ordering",
        "B4": "≥5 сценариев: фон, offline, файлы, порядок, badge",
    }
    rubric_3 = "Неполный план / 2–3 проверки / 1 гипотеза / баг без severity"
    rubric_0 = "Только UI / переустановка / неверная локализация"

    row = 2
    ws.cell(row, 1, "Выберите ОДИН кейс: A или B")
    ws.cell(row, 1).fill = WARN_FILL
    row += 1

    for case_name, crit, mx in cases_a + cases_b:
        key = crit.split(".")[0]
        ws.cell(row, 1, case_name)
        ws.cell(row, 2, crit)
        ws.cell(row, 3, mx)
        ws.cell(row, 4, "")
        ws.cell(row, 5, rubric_6.get(key, "Полный эталонный ответ"))
        ws.cell(row, 6, rubric_3)
        ws.cell(row, 7, rubric_0)
        ws.cell(row, 8, "")
        row += 1

    last = row - 1
    style_data_area(ws, 2, last, len(headers))
    dv = DataValidation(type="whole", operator="between", formula1=0, formula2=6, allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"D3:D{last}")

    case_total_row = row + 1
    ws.cell(case_total_row, 1, "ИТОГО кейс (оцените 4 строки выбранного кейса A или B)")
    ws.cell(case_total_row, 3, 24)
    # Сумма 4 критериев выбранного кейса (интервьюер заполняет только один блок)
    ws.cell(case_total_row, 4, "=MAX(SUM(D3:D6),SUM(D7:D10))")
    set_widths(ws, [22, 28, 6, 6, 36, 28, 22, 24])
    return case_total_row


def build_boundary(ws):
    ws.title = "Граничные"
    headers = [
        "ID",
        "Зона",
        "Граничная проверка",
        "Макс.",
        "Балл",
        "Эталон (ожидание)",
        "Комментарий",
    ]
    for c, h in enumerate(headers, 1):
        ws.cell(1, c, h)
    style_header_row(ws, 1, len(headers))

    items = [
        ("G-01", "URL/локаль", "/ru vs /ru/, несуществующая локаль /xx", 1, "Редирект или 404 по ТЗ, без циклов"),
        ("G-02", "URL/локаль", "Конфликт URL /en и localStorage f2f_language=ru", 1, "Приоритет зафиксирован, нет смешения языков"),
        ("G-03", "Cookie", "Первый визит / accept / инкогнито", 1, "Баннер и скрытие после accept"),
        ("G-04", "Hero", "iOS video playsinline, Slow 3G, autoplay off", 1, "CTA доступен, layout не ломается"),
        ("G-05", "Ивенты", "Слайдер: 1 карточка, быстрые клики стрелок", 1, "Стрелки disabled, нет гонки"),
        ("G-06", "FAQ", "«Открыть все» → вопрос про античит", 2, "Пустой ответ = баг Major"),
        ("G-07", "Footer", "PDF RU/EN по data-lang, пробелы в имени файла", 1, "200, верные документы на локали"),
        ("G-08", "SEO", "og:url, og:image SVG, шаринг в Telegram", 1, "Кандидат называет риски превью"),
        ("G-09", "Ссылки", "app.f2f.vin недоступен, target=_blank + noopener", 1, "Лендинг не падает, безопасность"),
        ("G-10", "a11y", "Tab-навигация, FAQ без мыши", 1, "Фокус и раскрытие FAQ"),
    ]

    row = 2
    for item in items:
        for c, val in enumerate(item, 1):
            ws.cell(row, c, val)
        ws.cell(row, 6, "")
        row += 1

    last = row - 1
    style_data_area(ws, 2, last, len(headers))
    dv = DataValidation(type="whole", operator="between", formula1=0, formula2=2, allow_blank=True)
    ws.add_data_validation(dv)
    ws.add_data_validation(
        DataValidation(type="whole", operator="between", formula1=0, formula2=1, allow_blank=True)
    )
    ws.data_validations.dataValidation[-1].add(f"E2:E{last}")

    boundary_total_row = last + 2
    ws.cell(boundary_total_row, 1, "ИТОГО граничные (опционально)")
    ws.cell(boundary_total_row, 3, f"=SUM(C2:C{last})")
    ws.cell(boundary_total_row, 4, f"=SUM(E2:E{last})")
    set_widths(ws, [8, 12, 48, 6, 6, 40, 22])
    return boundary_total_row


def build_penalties(ws):
    ws.title = "Штрафы"
    headers = ["ID", "Условие", "Штраф", "Применён (да/нет)", "Балл"]
    for c, h in enumerate(headers, 1):
        ws.cell(1, c, h)
    style_header_row(ws, 1, len(headers))

    penalties = [
        ("P-01", "Путает регресс и re-test после пояснения", -3),
        ("P-02", "Не объясняет 401 / 403 / 404", -3),
        ("P-03", "Отрицает SQL на микросервисах без аргументов", -2),
        ("P-04", "Blame-only (только вина разработчиков)", -2),
        ("P-05", "5+ лет опыта, нет ни одного примера из практики", -2),
    ]
    row = 2
    for p in penalties:
        ws.cell(row, 1, p[0])
        ws.cell(row, 2, p[1])
        ws.cell(row, 3, p[2])
        ws.cell(row, 4, "")
        ws.cell(row, 5, f'=IF(D{row}="да",C{row},0)')
        row += 1
    last = row - 1
    style_data_area(ws, 2, last, len(headers))
    dv = DataValidation(type="list", formula1='"да,нет"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"D2:D{last}")
    penalty_total_row = last + 2
    ws.cell(penalty_total_row, 2, "СУММА штрафов (не ниже -10)")
    ws.cell(penalty_total_row, 5, f"=MAX(-10,SUM(E2:E{last}))")
    set_widths(ws, [8, 52, 8, 14, 10])
    return penalty_total_row


def build_summary(ws, case_total_row, boundary_total_row, penalty_total_row):
    ws.title = "Сводка"
    set_widths(ws, [28, 18, 40])

    blocks = [
        ("Блок", "Макс.", "Формула / источник"),
        ("1. Теория", 12, "=SUMIF(Вопросы!B:B,\"1. Теория\",Вопросы!E:E)"),
        ("2. Web", 8, "=SUMIF(Вопросы!B:B,\"2. Web\",Вопросы!E:E)"),
        ("3. Mobile", 10, "=SUMIF(Вопросы!B:B,\"3. Mobile\",Вопросы!E:E)"),
        ("4. API", 14, "=SUMIF(Вопросы!B:B,\"4. API\",Вопросы!E:E)"),
        ("5. SQL", 8, "=SUMIF(Вопросы!B:B,\"5. SQL\",Вопросы!E:E)"),
        ("6. Логи/NFR", 8, "=SUMIF(Вопросы!B:B,\"6. Логи/NFR\",Вопросы!E:E)"),
        (
            "7. Процессы+Lead",
            12,
            '=SUMIF(Вопросы!B:B,"7. Процессы",Вопросы!E:E)+SUMIF(Вопросы!B:B,"7. Lead",Вопросы!E:E)',
        ),
        ("8. Python", 4, '=SUMIF(Вопросы!B:B,"8. Python",Вопросы!E:E)'),
        ("9. Практический кейс", 24, f"=Кейсы!D{case_total_row}"),
        ("10. Граничные (опц.)", 11, f"=Граничные!D{boundary_total_row}"),
        ("Штрафы", -10, f"=Штрафы!E{penalty_total_row}"),
    ]

    for i, row in enumerate(blocks, 1):
        ws.cell(i, 1, row[0])
        if i == 1:
            style_header_row(ws, 1, 3, 20)
        else:
            ws.cell(i, 2, row[1])
            ws.cell(i, 3, row[2])

    total_row = len(blocks) + 3  # строка «ИТОГО» после 10 блоков + штрафы
    ws.cell(total_row, 1, "ИТОГО (основная шкала 100)")
    ws.cell(total_row, 2, 100)
    # Блоки 1–8 (C2–C9) + кейс (C10) + штрафы (C12); граничные (C11) — отдельная шкала
    ws.cell(total_row, 3, "=SUM(C2:C10)+C12")
    ws.cell(total_row, 1).font = Font(bold=True, size=12)
    ws.cell(total_row, 3).font = Font(bold=True, size=12)

    decision_row = total_row + 2
    ws.cell(decision_row, 1, "Решение")
    ws.cell(
        decision_row,
        3,
        f'=IF(C{total_row}>=85,"Strong hire (Lead)",IF(C{total_row}>=70,"Hire (Senior)",IF(C{total_row}>=55,"Hire с оговорками","No hire")))',
    )

    api_row = decision_row + 1
    ws.cell(api_row, 1, "Lead: API ≥10/14")
    ws.cell(api_row, 3, '=IF(SUMIF(Вопросы!B:B,"4. API",Вопросы!E:E)>=10,"OK","FAIL")')

    proc_row = api_row + 1
    ws.cell(proc_row, 1, "Lead: Процессы ≥9/12")
    ws.cell(proc_row, 3, "=C8")  # балл блока 7 из сводки
    ws.cell(
        proc_row,
        3,
        '=IF((SUMIF(Вопросы!B:B,"7. Процессы",Вопросы!E:E)+SUMIF(Вопросы!B:B,"7. Lead",Вопросы!E:E))>=9,"OK","FAIL")',
    )

    case_check_row = proc_row + 1
    ws.cell(case_check_row, 1, "Lead: Кейс ≥18/24")
    ws.cell(case_check_row, 3, f'=IF(Кейсы!D{case_total_row}>=18,"OK","FAIL")')

    lead_row = case_check_row + 1
    ws.cell(lead_row, 1, "Lead итог")
    ws.cell(
        lead_row,
        3,
        f'=IF(AND(C{api_row}="OK",C{proc_row}="OK",C{case_check_row}="OK"),"Strong hire возможен","Макс. Senior")',
    )

    bound_score_row = lead_row + 2
    ws.cell(bound_score_row, 1, "Граничные: отдельная оценка /10")
    ws.cell(
        bound_score_row,
        3,
        f"=IF(Граничные!C{boundary_total_row}=0,0,Граничные!D{boundary_total_row}/Граничные!C{boundary_total_row}*10)",
    )

    bound_verdict_row = bound_score_row + 1
    ws.cell(bound_verdict_row, 1, "Граничные: вердикт")
    ws.cell(
        bound_verdict_row,
        3,
        f'=IF(C{bound_score_row}>=8,"Strong",IF(C{bound_score_row}>=5,"OK","Weak"))',
    )

    return {
        "total_row": total_row,
        "decision_row": decision_row,
        "lead_row": lead_row,
        "bound_score_row": bound_score_row,
    }


def build_candidate_card(ws, summary_rows):
    total_row = summary_rows["total_row"]
    decision_row = summary_rows["decision_row"]
    lead_row = summary_rows["lead_row"]
    bound_score_row = summary_rows["bound_score_row"]
    ws.title = "Карточка кандидата"
    set_widths(ws, [22, 50, 22, 50])
    fields = [
        ("Поле", "Значение", "Поле", "Значение"),
        ("ФИО кандидата", "", "Дата", ""),
        ("Позиция", "Senior / Lead / Middle", "Интервьюер", ""),
        ("Опыт (лет)", "", "Проект/контекст", "F2F / общий QA"),
        ("Кейс на интервью", "A — E-com / B — Mobile", "Граничные", "Да / Нет"),
        ("", "", "", ""),
        ("Итоговый балл (/100)", f"=Сводка!C{total_row}", "Решение", f"=Сводка!C{decision_row}"),
        ("Lead-пороги", f"=Сводка!C{lead_row}", "Граничные /10", f"=Сводка!C{bound_score_row}"),
        ("", "", "", ""),
        ("Сильные стороны", "", "", ""),
        ("", "", "", ""),
        ("Зоны роста", "", "", ""),
        ("", "", "", ""),
        ("Рекомендация", "", "", ""),
    ]
    for i, row in enumerate(fields, 1):
        for j, val in enumerate(row, 1):
            ws.cell(i, j, val)
    style_header_row(ws, 1, 4, 18)
    ws.merge_cells("B9:D9")
    ws.merge_cells("B11:D11")
    ws.merge_cells("B13:D13")
    ws.merge_cells("B15:D15")


def main():
    wb = Workbook()
    ws0 = wb.active
    build_instructions(ws0)
    build_questions(wb.create_sheet())
    case_total_row = build_cases(wb.create_sheet())
    boundary_total_row = build_boundary(wb.create_sheet())
    penalty_total_row = build_penalties(wb.create_sheet())
    summary_rows = build_summary(
        wb.create_sheet(), case_total_row, boundary_total_row, penalty_total_row
    )
    build_candidate_card(wb.create_sheet(), summary_rows)

    out = "/workspace/docs/QA_Interview_Evaluation.xlsx"
    import os
    os.makedirs(os.path.dirname(out), exist_ok=True)
    wb.save(out)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
