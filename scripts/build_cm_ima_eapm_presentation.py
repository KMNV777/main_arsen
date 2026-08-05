#!/usr/bin/env python3
"""Генерация презентации: варианты интеграции ЦМ ИМА в ЕАРМ."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "presentations"
ASSETS = OUT_DIR / "assets"

# Бэклог ЕАРМ-1 (встраивание / file 2_file.OVCeIx)
BACKLOG_EAPM1 = [
    ("1", "Изменение Dag-ов AirFlow", "Запуск через API AirFlow", "8,10", "8,50"),
    ("2", "Изменение Dag-ов AirFlow", "Атомарность — получение всех данных без ручного csv/json", "4,20", "6,50"),
    ("3", "Изменение в АКТС", "Добавление техстека ЦМ ИМА в ЕАРМ", "1,10", "1,10"),
    ("4", "Изменение в АКТС", "Анализ интеграций ЦМ ИМА / пересечение с ЕАРМ", "15,20", "16,00"),
    ("5", "Изменение в АКТС", "Добавление новых интеграций в ЕАРМ", "3,20", "3,20"),
    ("6", "Изменение в АКТС", "Увеличение / добавление ресурсов", "5,10", "5,40"),
    ("7", "Инфраструктура", "Заказ ресурсов", "2,10", "2,10"),
    ("8", "Инфраструктура", "Открытие МСЭ", "5,10", "5,90"),
    ("9", "Инфраструктура", "Перенос данных/дампов из ЦМ ИМА в ЕАРМ", "8,10", "8,50"),
    ("10", "Инфраструктура", "Изменение CI/CD", "17,20", "18,10"),
    ("11", "Инфраструктура", "Реконфигурация стендов", "14,00", "14,80"),
    ("12", "Документирование", "Изменение ЕДТ", "13,00", "13,70"),
    ("13", "Документирование", "Изменение ТП", "37,00", "39,00"),
    ("14", "Документирование", "Изменение ПМТ", "29,00", "30,60"),
    ("15", "Документирование", "Инструкции пользователя/администратора", "31,00", "32,70"),
    ("16", "Устранение уязвимостей", "Анализ зависимостей, аудиты, резолюции", "17,20", "21,90"),
    ("17", "Устранение уязвимостей", "Новые требования / замена запрещённых компонент", "37,00", "57,40"),
    ("18", "Устранение уязвимостей", "Изменения под КТ-233 (ЕДТ)", "41,00", "56,80"),
]
TOTAL_EAPM1 = ("281,70", "221,50")

# Бэклог ЕАРМ-2 (интеграция без приземления / file 3_file.ekYFFz)
BACKLOG_EAPM2 = [
    ("1", "Вызов расчётов через API AirFlow", "Анализ endpoint-ов и согласование контрактов", "1,10", "1,30"),
    ("2", "Вызов расчётов через API AirFlow", "Формирование наборов данных по контрактам", "4,20", "5,80"),
    ("4", "Изменение в АКТС", "Анализ интеграций; переход на валидированную ТМ от ЕАРМ", "15,20", "16,00"),
    ("5", "Изменение в АКТС", "Добавление новых интеграций (зависит от контрактов)", "3,20", "3,20"),
    ("6", "Изменение в АКТС", "Ресурсы на наборы данных и хранение результатов", "3,20", "3,20"),
    ("7", "Инфраструктура", "Заказ ресурсов", "2,10", "2,10"),
    ("8", "Инфраструктура", "Открытие МСЭ (риск OKD→DH)", "5,10", "5,90"),
    ("10", "Инфраструктура", "Изменение CI/CD, конфигурации и секреты", "4,20", "4,20"),
    ("12", "Документирование", "Изменение ЕДТ", "13,00", "13,70"),
    ("13", "Документирование", "Изменение ТП", "37,00", "39,00"),
    ("14", "Документирование", "Изменение ПМТ", "22,00", "23,20"),
    ("15", "Документирование", "Инструкции пользователя/администратора", "17,00", "17,90"),
]
TOTAL_EAPM2 = ("126,60", "135,50")

COLOR_TITLE = RGBColor(0x00, 0x33, 0x66)
COLOR_ACCENT = RGBColor(0x00, 0x70, 0xC0)
COLOR_GREEN = RGBColor(0x1B, 0x7A, 0x3A)
COLOR_RED = RGBColor(0xC0, 0x00, 0x00)
COLOR_GRAY = RGBColor(0x55, 0x55, 0x55)


def set_run_font(run, size: int = 18, bold: bool = False, color: RGBColor | None = None):
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = color
    run.font.name = "Calibri"


def add_title_slide(prs: Presentation, title: str, subtitle: str = ""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    box = slide.shapes.add_textbox(Inches(0.6), Inches(2.2), Inches(12), Inches(1.5))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = title
    set_run_font(r, 36, True, COLOR_TITLE)
    if subtitle:
        box2 = slide.shapes.add_textbox(Inches(0.6), Inches(3.6), Inches(12), Inches(1))
        tf2 = box2.text_frame
        p2 = tf2.paragraphs[0]
        p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run()
        r2.text = subtitle
        set_run_font(r2, 20, False, COLOR_GRAY)
    return slide


def add_section_slide(prs: Presentation, title: str):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    box = slide.shapes.add_textbox(Inches(0.6), Inches(3), Inches(12), Inches(1.2))
    p = box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = title
    set_run_font(r, 32, True, COLOR_ACCENT)
    return slide


def add_bullet_slide(prs: Presentation, title: str, bullets: list[str], sub_bullets: dict[int, list[str]] | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(12.3), Inches(0.8))
    tr = title_box.text_frame.paragraphs[0].add_run()
    tr.text = title
    set_run_font(tr, 26, True, COLOR_TITLE)

    body = slide.shapes.add_textbox(Inches(0.7), Inches(1.2), Inches(12), Inches(5.8))
    tf = body.text_frame
    tf.word_wrap = True
    for i, item in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = 0
        p.space_after = Pt(6)
        r = p.add_run()
        r.text = f"• {item}"
        set_run_font(r, 16)
        if sub_bullets and i in sub_bullets:
            for sub in sub_bullets[i]:
                sp = tf.add_paragraph()
                sp.level = 1
                sp.space_after = Pt(3)
                sr = sp.add_run()
                sr.text = f"– {sub}"
                set_run_font(sr, 14, color=COLOR_GRAY)
    return slide


def add_two_column_slide(prs: Presentation, title: str, left_title: str, left_items: list[str],
                         right_title: str, right_items: list[str]):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(12.3), Inches(0.8))
    tr = title_box.text_frame.paragraphs[0].add_run()
    tr.text = title
    set_run_font(tr, 24, True, COLOR_TITLE)

    for col, (ctitle, items, x) in enumerate([
        (left_title, left_items, 0.5),
        (right_title, right_items, 6.8),
    ]):
        hdr = slide.shapes.add_textbox(Inches(x), Inches(1.1), Inches(6), Inches(0.5))
        hr = hdr.text_frame.paragraphs[0].add_run()
        hr.text = ctitle
        color = COLOR_GREEN if col == 0 else COLOR_RED
        set_run_font(hr, 18, True, color)

        body = slide.shapes.add_textbox(Inches(x), Inches(1.6), Inches(6), Inches(5.2))
        tf = body.text_frame
        tf.word_wrap = True
        for i, item in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            r = p.add_run()
            r.text = f"• {item}"
            set_run_font(r, 14)
    return slide


def add_image_slide(prs: Presentation, title: str, image_path: Path, caption: str = ""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.25), Inches(12.3), Inches(0.7))
    tr = title_box.text_frame.paragraphs[0].add_run()
    tr.text = title
    set_run_font(tr, 22, True, COLOR_TITLE)

    if image_path.exists():
        slide.shapes.add_picture(str(image_path), Inches(0.4), Inches(1.0), width=Inches(12.5))

    if caption:
        cap = slide.shapes.add_textbox(Inches(0.5), Inches(6.85), Inches(12), Inches(0.5))
        cr = cap.text_frame.paragraphs[0].add_run()
        cr.text = caption
        set_run_font(cr, 11, color=COLOR_GRAY)
    return slide


def add_backlog_table_slide(prs: Presentation, title: str, rows: list[tuple], total: tuple[str, str]):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    title_box = slide.shapes.add_textbox(Inches(0.4), Inches(0.2), Inches(12.5), Inches(0.6))
    tr = title_box.text_frame.paragraphs[0].add_run()
    tr.text = title
    set_run_font(tr, 20, True, COLOR_TITLE)

    n_rows = len(rows) + 2
    table_shape = slide.shapes.add_table(n_rows, 5, Inches(0.3), Inches(0.85), Inches(12.7), Inches(6.0))
    table = table_shape.table
    headers = ["№", "Feature / Задача", "Подзадача", "ТРЗ без риска", "ТРЗ с риском"]
    widths = [Inches(0.4), Inches(2.2), Inches(5.5), Inches(1.5), Inches(1.5)]
    for i, w in enumerate(widths):
        table.columns[i].width = w

    for c, h in enumerate(headers):
        cell = table.cell(0, c)
        cell.text = h
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                set_run_font(r, 9, True, COLOR_TITLE)

    for r_idx, row in enumerate(rows, start=1):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            for p in cell.text_frame.paragraphs:
                for run in p.runs:
                    set_run_font(run, 8)

    total_row = len(rows) + 1
    table.cell(total_row, 0).merge(table.cell(total_row, 2))
    table.cell(total_row, 0).text = "ИТОГО"
    table.cell(total_row, 3).text = total[0]
    table.cell(total_row, 4).text = total[1]
    for c in range(5):
        for p in table.cell(total_row, c).text_frame.paragraphs:
            for run in p.runs:
                set_run_font(run, 9, True, COLOR_ACCENT)
    return slide


def add_comparison_slide(prs: Presentation):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    title_box = slide.shapes.add_textbox(Inches(0.4), Inches(0.2), Inches(12.5), Inches(0.6))
    tr = title_box.text_frame.paragraphs[0].add_run()
    tr.text = "Сводное сравнение вариантов"
    set_run_font(tr, 24, True, COLOR_TITLE)

    headers = ["Критерий", "Вариант 1\n(целевой перенос)", "Вариант 2\n(встраивание, ЕАРМ-1)", "Вариант 3\n(интеграция, ЕАРМ-2)"]
    data = [
        ("Суть", "Полный перенос функционала ЦМ ИМА в ЕАРМ", "«Приземление» стека ЦМ ИМА БРД в ЕАРМ", "ЦМ ИМА — отдельная ИТ-система"),
        ("ТРЗ (без риска)", "Не оценивался", "281,7 ч/д", "126,6 ч/д"),
        ("ТРЗ (с риском)", "Не оценивался", "221,5 ч/д*", "135,5 ч/д"),
        ("Инфраструктура", "Единая платформа ЕАРМ", "Миграция CH, PG, Airflow, NiFi, Kafka, S3", "Минимальные изменения в ЕАРМ"),
        ("Оркестрация", "Airflow в ЕАРМ", "Airflow в ЕАРМ", "Airflow в ЦМ ИМА, вызов из ЕАРМ"),
        ("Песочница моделей", "Да (MVP ЦМ ИМА)", "Ограниченно", "Сохраняется в ЦМ ИМА"),
        ("Срок / сложность", "Максимальный", "Высокий", "Умеренный"),
        ("Риски", "Длительная миграция", "Перенос данных, уязвимости, CI/CD", "Контракты API, МСЭ OKD→DH"),
    ]

    table_shape = slide.shapes.add_table(len(data) + 1, 4, Inches(0.25), Inches(0.9), Inches(12.8), Inches(5.8))
    table = table_shape.table
    col_widths = [Inches(2.0), Inches(3.5), Inches(3.5), Inches(3.5)]
    for i, w in enumerate(col_widths):
        table.columns[i].width = w

    for c, h in enumerate(headers):
        cell = table.cell(0, c)
        cell.text = h
        for p in cell.text_frame.paragraphs:
            p.alignment = PP_ALIGN.CENTER
            for r in p.runs:
                set_run_font(r, 9, True, COLOR_TITLE)

    for r_idx, row in enumerate(data, start=1):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            for p in cell.text_frame.paragraphs:
                for run in p.runs:
                    set_run_font(run, 8, bold=(c_idx == 0))

    note = slide.shapes.add_textbox(Inches(0.4), Inches(6.75), Inches(12), Inches(0.4))
    nr = note.text_frame.paragraphs[0].add_run()
    nr.text = "* В бэклоге ЕАРМ-1 итог «с риском» ниже «без риска» — проверить методику расчёта рисков в исходном Excel."
    set_run_font(nr, 8, color=COLOR_GRAY)
    return slide


def build_presentation() -> Path:
    ASSETS.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    add_title_slide(
        prs,
        "Варианты интеграции ЦМ ИМА и ЕАРМ",
        "Сравнительный анализ архитектуры, плюсов/минусов и трудозатрат (ТРЗ)",
    )

    add_bullet_slide(
        prs,
        "Цель и контекст",
        [
            "Обеспечить расчёты моделей ИМА в целевом ландшафте ЕАРМ с учётом данных ТМ, Дата-платформы и DUO Tech ИМА.",
            "Рассмотрены три архитектурных варианта с разной глубиной «приземления» компонентов ЦМ ИМА.",
            "Для вариантов 2 и 3 приведены оценки ТРЗ из бэклогов Excel (листы «Бэклог ЦМ ИМА в ЕАРМ-1» и «ЕАРМ-2»).",
            "Вариант 1 представлен как целевая концепция без количественной оценки ТРЗ.",
        ],
    )

    add_bullet_slide(
        prs,
        "Обзор трёх вариантов",
        [
            "Вариант 1 — перенос функционала ЦМ ИМА в ЕАРМ (целевое решение + песочница для гипотез).",
            "Вариант 2 — встраивание стека ЦМ ИМА БРД в ЕАРМ (перенос компонент, ЕАРМ-1).",
            "Вариант 3 — интеграция с ЦМ ИМА как с отдельной ИТ-системой без приземления (ЕАРМ-2).",
        ],
        sub_bullets={
            0: ["Зелёные потоки — целевое решение; оранжевые — разработка моделей/гипотез"],
            1: ["Синие стрелки — перенос ClickHouse, Postgres, Airflow, NiFi, Kafka, Grafana, S3"],
            2: ["ЕАРМ вызывает расчёты через API AirFlow ЦМ ИМА; ТМ — через ЕАРМ ClickHouse"],
        },
    )

    # --- Вариант 1 ---
    add_section_slide(prs, "Вариант 1. Перенос функционала ЦМ ИМА в ЕАРМ")

    add_image_slide(
        prs,
        "Архитектура: целевой перенос функционала",
        ASSETS / "variant1_transfer.png",
        "Источник: 1-file.feUnSR  |  ТРЗ: не оценивался",
    )

    add_bullet_slide(
        prs,
        "Вариант 1 — ключевые особенности",
        [
            "Оркестрация расчётов централизована в Airflow (N1) ЕАРМ.",
            "Получение валидированной ТМ для расчёта из ClickHouse ЕАРМ; данные с Дата-платформы.",
            "Результаты расчёта сохраняются в Postgres Pro и ClickHouse ЕАРМ; отчётность в ГПН КЦ / ГПН-Заполярье.",
            "MVP-ёмкости ЦМ ИМА используются как песочница для разработки и тестирования моделей (оранжевый контур).",
            "Перенос компонентов из ЦМ ИМА БРД (синий контур) в инфраструктуру ЕАРМ.",
        ],
    )

    add_two_column_slide(
        prs,
        "Вариант 1 — плюсы и минусы",
        "Плюсы",
        [
            "Единая целевая платформа и единая точка входа для пользователей ДО.",
            "Централизованное управление данными ТМ, расчётами и результатами.",
            "Сохранение возможности экспериментов в песочнице без влияния на прод.",
            "Соответствие целевому ИТ-ландшафту ЕАРМ в долгосрочной перспективе.",
        ],
        "Минусы",
        [
            "Наибольший объём организационных и технических изменений.",
            "ТРЗ не оценён — требуется отдельная проработка.",
            "Длительный переходный период с параллельной эксплуатацией контуров.",
            "Высокая зависимость от готовности всех компонентов ЕАРМ (NiFi, Kafka, S3).",
        ],
    )

    # --- Вариант 2 ---
    add_section_slide(prs, "Вариант 2. Встраивание ЦМ ИМА в ЕАРМ (ЕАРМ-1)")

    add_image_slide(
        prs,
        "Архитектура: встраивание стека ЦМ ИМА БРД",
        ASSETS / "variant2_embedding.png",
        "Источник: 2_file.OVCeIx  |  Бэклог: «Бэклог ЦМ ИМА в ЕАРМ-1»",
    )

    add_bullet_slide(
        prs,
        "Вариант 2 — ключевые особенности и ТРЗ",
        [
            f"Итого ТРЗ: {TOTAL_EAPM1[0]} ч/д (без риска) / {TOTAL_EAPM1[1]} ч/д (с риском).",
            "Физический перенос стека: ClickHouse, Postgres Pro, Airflow, NiFi, Kafka, Grafana, S3 → ЕАРМ.",
            "Переработка DAG-ов Airflow: запуск через API, атомарность данных.",
            "Миграция дампов, реконфигурация стендов, изменение CI/CD.",
            "Обязательный блок: устранение уязвимостей и приведение к КТ-233 (~134 ч/д).",
            "Обновление АКТС, ЕДТ, ТП, ПМТ и пользовательской документации.",
        ],
    )

    add_two_column_slide(
        prs,
        "Вариант 2 — плюсы и минусы",
        "Плюсы",
        [
            "Полная консолидация инфраструктуры в ЕАРМ — один контур эксплуатации.",
            "Прямой контроль над данными ТМ через NiFi ЕАРМ (АДКУ → Kafka).",
            "Grafana и визуализация встраиваются в frontend ЕАРМ.",
            "Целевые потоки (зелёные) реализуются внутри единого контура.",
        ],
        "Минусы",
        [
            "Максимальные ТРЗ среди оценённых вариантов (~282 ч/д).",
            "Высокие затраты на миграцию данных и реконфигурацию CI/CD.",
            "Блок уязвимостей может существенно увеличить срок (до +57 ч/д по отдельным задачам).",
            "Риски простоя при переносе production-данных и DAG-ов.",
        ],
    )

    add_backlog_table_slide(
        prs,
        "Бэклог ЕАРМ-1 — детализация ТРЗ (лист «Бэклог ЦМ ИМА в ЕАРМ-1»)",
        BACKLOG_EAPM1,
        TOTAL_EAPM1,
    )

    # --- Вариант 3 ---
    add_section_slide(prs, "Вариант 3. Интеграция без приземления (ЕАРМ-2)")

    add_image_slide(
        prs,
        "Архитектура: ЦМ ИМА как отдельная ИТ-система",
        ASSETS / "variant3_integration.png",
        "Источник: 3_file.ekYFFz  |  Бэклог: «Бэклог ЦМ ИМА в ЕАРМ-2»",
    )

    add_bullet_slide(
        prs,
        "Вариант 3 — ключевые особенности и ТРЗ",
        [
            f"Итого ТРЗ: {TOTAL_EAPM2[0]} ч/д (без риска) / {TOTAL_EAPM2[1]} ч/д (с риском).",
            "ЕАРМ backend вызывает расчёты в Airflow ЦМ ИМА через API.",
            "ЕАРМ NiFi получает сырую ТМ из АДКУ (Kafka); ЦМ ИМА читает валидированную ТМ из ClickHouse ЕАРМ.",
            "Результаты расчёта возвращаются из ЦМ ИМА в Airflow / ClickHouse ЕАРМ.",
            "Нет переноса стека и дампов — существенно меньше инфраструктурных работ.",
            "Допущение: DAG-и ЦМ ИМА атомарны и догружают данные вне контракта самостоятельно.",
        ],
    )

    add_two_column_slide(
        prs,
        "Вариант 3 — плюсы и минусы",
        "Плюсы",
        [
            "Минимальные ТРЗ: ~127 ч/д против ~282 ч/д у варианта 2 (−55%).",
            "Быстрее выход на целевые интеграционные потоки (зелёные стрелки).",
            "Сохранение экспертизы и стека ЦМ ИМА без полной миграции.",
            "Меньше работ по CI/CD, стендам и переносу данных.",
        ],
        "Минусы",
        [
            "Два контура эксплуатации: ЕАРМ + ЦМ ИМА БРД.",
            "Зависимость от стабильности API-контрактов AirFlow.",
            "Риск временного МСЭ OKD→DH до перевода ЕАРМ в DH.",
            "Сложнее единое управление версиями моделей и мониторинг.",
        ],
    )

    add_backlog_table_slide(
        prs,
        "Бэклог ЕАРМ-2 — детализация ТРЗ (лист «Бэклог ЦМ ИМА в ЕАРМ-2»)",
        BACKLOG_EAPM2,
        TOTAL_EAPM2,
    )

    add_comparison_slide(prs)

    add_bullet_slide(
        prs,
        "Выводы и рекомендации",
        [
            "Вариант 1 задаёт стратегическое направление, но требует отдельной оценки ТРЗ перед принятием решения.",
            "Вариант 2 (ЕАРМ-1) — полная консолидация, но с максимальными трудозатратами и рисками миграции.",
            "Вариант 3 (ЕАРМ-2) — оптимален как поэтапный шаг: быстрее, дешевле, с сохранением ЦМ ИМА.",
            "Возможна стратегия: Вариант 3 → накопление опыта интеграции → Вариант 1/2 при готовности ЕАРМ.",
            "Критично согласовать контракты API AirFlow и источник валидированной ТМ до старта работ.",
        ],
    )

    add_title_slide(prs, "Спасибо за внимание", "Вопросы и обсуждение")

    out_path = OUT_DIR / "CM_IMA_EAPM_variants_comparison.pptx"
    prs.save(out_path)
    return out_path


if __name__ == "__main__":
    path = build_presentation()
    print(f"Presentation saved: {path}")
