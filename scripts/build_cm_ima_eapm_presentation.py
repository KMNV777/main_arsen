#!/usr/bin/env python3
"""Генерация презентации: варианты интеграции ЦМ ИМА в ЕАРМ (деловой стиль)."""

from __future__ import annotations

import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from presentation_theme import (  # noqa: E402
    ACCENT,
    BG_LIGHT,
    COL_V1,
    COL_V2,
    COL_V3,
    CONTENT_TOP,
    FONT,
    GREEN,
    NAVY,
    ORANGE,
    RED,
    SLIDE_H,
    SLIDE_W,
    TABLE_ALT,
    TEXT_DARK,
    TEXT_MUTED,
    WHITE,
    apply_frame,
    set_font,
    style_score_cell,
    style_table_cell,
    style_table_header,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "presentations"
ASSETS = OUT_DIR / "assets"

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

RATING_CRITERIA = [
    "Скорость внедрения",
    "Экономичность (ТРЗ)",
    "Консолидация ИТ",
    "Целевая архитектура",
    "Управление рисками",
    "Гибкость экспертов",
    "Простота сопровождения",
    "Интеграция данных",
]
RATING_V1 = [2, 3, 5, 5, 2, 5, 4, 4]
RATING_V2 = [2, 2, 5, 4, 2, 3, 3, 5]
RATING_V3 = [5, 5, 2, 3, 4, 4, 2, 4]
RATING_WEIGHTS = [1.2, 1.5, 1.0, 1.2, 1.3, 0.8, 1.0, 1.0]


class SlideBuilder:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = SLIDE_W
        self.prs.slide_height = SLIDE_H
        self._page = 0

    def _next(self) -> int:
        self._page += 1
        return self._page

    def title(self, title: str, subtitle: str = ""):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        apply_frame(slide, dark=True)
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.7), Inches(1.4))
        p = tb.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = title
        set_font(r, 34, True, WHITE)
        if subtitle:
            sb = slide.shapes.add_textbox(Inches(0.8), Inches(3.5), Inches(11.7), Inches(0.9))
            sp = sb.text_frame.paragraphs[0]
            sp.alignment = PP_ALIGN.CENTER
            sr = sp.add_run()
            sr.text = subtitle
            set_font(sr, 18, color=RGBColor(0xCC, 0xDD, 0xEE))
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.5), Inches(3.2), Inches(4.3), Inches(0.03))
        line.fill.solid()
        line.fill.fore_color.rgb = ACCENT
        line.line.fill.background()
        return slide

    def section(self, title: str):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        apply_frame(slide, title, dark=True)
        return slide

    def bullets(self, title: str, items: list[str], sub: dict[int, list[str]] | None = None):
        pg = self._next()
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        apply_frame(slide, title, pg)
        body = slide.shapes.add_textbox(Inches(0.7), CONTENT_TOP, Inches(12), Inches(5.85))
        tf = body.text_frame
        tf.word_wrap = True
        for i, item in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_after = Pt(8)
            r = p.add_run()
            r.text = item
            set_font(r, 15, color=TEXT_DARK)
            p.level = 0
            if sub and i in sub:
                for s in sub[i]:
                    sp = tf.add_paragraph()
                    sp.level = 1
                    sp.space_after = Pt(4)
                    sr = sp.add_run()
                    sr.text = s
                    set_font(sr, 13, color=TEXT_MUTED)
        return slide

    def two_col(self, title: str, left_t: str, left: list[str], right_t: str, right: list[str]):
        pg = self._next()
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        apply_frame(slide, title, pg)
        for col, (ct, items, x, color) in enumerate([
            (left_t, left, 0.55, GREEN),
            (right_t, right, 6.85, RED),
        ]):
            hdr = slide.shapes.add_textbox(Inches(x), Inches(1.05), Inches(5.9), Inches(0.45))
            hr = hdr.text_frame.paragraphs[0].add_run()
            hr.text = ct
            set_font(hr, 16, True, color)
            box = slide.shapes.add_textbox(Inches(x), Inches(1.55), Inches(5.9), Inches(5.2))
            tf = box.text_frame
            tf.word_wrap = True
            for i, item in enumerate(items):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.space_after = Pt(6)
                r = p.add_run()
                r.text = f"• {item}"
                set_font(r, 13, color=TEXT_DARK)
        return slide

    def image(self, title: str, path: Path, caption: str = ""):
        pg = self._next()
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        apply_frame(slide, title, pg)
        if path.exists():
            try:
                from PIL import Image
                with Image.open(path) as im:
                    px_w, px_h = im.size
            except Exception:
                px_w, px_h = 16, 9
            max_w = Inches(12.4)
            max_h = Inches(5.65)
            ratio = px_w / px_h
            if max_w / max_h > ratio:
                pic_h = max_h
                pic_w = int(max_h * ratio)
            else:
                pic_w = max_w
                pic_h = int(max_w / ratio)
            left = int((SLIDE_W - pic_w) / 2)
            slide.shapes.add_picture(str(path), left, Inches(1.0), width=pic_w, height=pic_h)
        if caption:
            cap = slide.shapes.add_textbox(Inches(0.55), Inches(6.78), Inches(12.2), Inches(0.35))
            cr = cap.text_frame.paragraphs[0].add_run()
            cr.text = caption
            set_font(cr, 9, color=TEXT_MUTED)
        return slide

    def table_backlog(self, title: str, rows: list[tuple], total: tuple[str, str]):
        pg = self._next()
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        apply_frame(slide, title, pg)
        tbl = slide.shapes.add_table(len(rows) + 2, 5, Inches(0.35), Inches(1.0), Inches(12.6), Inches(5.75)).table
        headers = ["№", "Feature / Задача", "Подзадача", "ТРЗ без риска", "ТРЗ с риском"]
        widths = [Inches(0.4), Inches(2.1), Inches(5.6), Inches(1.5), Inches(1.5)]
        for i, w in enumerate(widths):
            tbl.columns[i].width = w
        for c, h in enumerate(headers):
            style_table_header(tbl.cell(0, c), h)
        for ri, row in enumerate(rows, 1):
            for ci, val in enumerate(row):
                style_table_cell(tbl.cell(ri, ci), val, alt=(ri % 2 == 0))
        tr = len(rows) + 1
        tbl.cell(tr, 0).merge(tbl.cell(tr, 2))
        style_table_cell(tbl.cell(tr, 0), "ИТОГО", bold=True)
        style_table_cell(tbl.cell(tr, 3), total[0], bold=True)
        style_table_cell(tbl.cell(tr, 4), total[1], bold=True)
        return slide

    def comparison(self):
        pg = self._next()
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        apply_frame(slide, "Сводное сравнение вариантов", pg)
        headers = ["Критерий", "Вариант 1", "Вариант 2 (ЕАРМ-1)", "Вариант 3 (ЕАРМ-2)"]
        data = [
            ("Суть", "Полный перенос функционала", "«Приземление» стека ЦМ ИМА БРД", "ЦМ ИМА — отдельная система"),
            ("ТРЗ (без риска)", "Не оценивался", "281,7 ч/д", "126,6 ч/д"),
            ("ТРЗ (с риском)", "Не оценивался", "221,5 ч/д*", "135,5 ч/д"),
            ("Инфраструктура", "Единая платформа ЕАРМ", "Миграция CH, PG, Airflow, NiFi…", "Минимальные изменения"),
            ("Оркестрация", "Airflow в ЕАРМ", "Airflow в ЕАРМ", "Airflow в ЦМ ИМА"),
            ("Песочница моделей", "Да (MVP)", "Ограниченно", "В ЦМ ИМА"),
            ("Сложность", "Максимальная", "Высокая", "Умеренная"),
            ("Ключевые риски", "Длительная миграция", "Перенос данных, уязвимости", "API-контракты, МСЭ"),
        ]
        tbl = slide.shapes.add_table(len(data) + 1, 4, Inches(0.35), Inches(1.0), Inches(12.6), Inches(5.5)).table
        for c, h in enumerate(headers):
            style_table_header(tbl.cell(0, c), h)
        for ri, row in enumerate(data, 1):
            for ci, val in enumerate(row):
                style_table_cell(tbl.cell(ri, ci), val, bold=(ci == 0), alt=(ri % 2 == 0))
        note = slide.shapes.add_textbox(Inches(0.55), Inches(6.65), Inches(12), Inches(0.3))
        nr = note.text_frame.paragraphs[0].add_run()
        nr.text = "* Проверить методику расчёта рисков в исходном Excel (ЕАРМ-1)."
        set_font(nr, 8, color=TEXT_MUTED)
        return slide

    def _fill_variant_column(self, tf, data: dict, source: str, accent: RGBColor):
        """Заполнить текстовый фрейм колонки сводки по варианту."""
        sections = [
            ("ТРЗ", data["trz"], NAVY),
            ("Особенности", data["feat"], accent),
            ("Плюсы", data["pros"], GREEN),
            ("Минусы", data["cons"], RED),
        ]
        first = True
        for label, items, color in sections:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.space_before = Pt(5)
            r = p.add_run()
            r.text = label
            set_font(r, 9, True, color)
            if isinstance(items, str):
                ip = tf.add_paragraph()
                ir = ip.add_run()
                ir.text = items
                set_font(ir, 8, color=TEXT_DARK)
            else:
                for item in items:
                    bp = tf.add_paragraph()
                    bp.space_before = Pt(1)
                    br = bp.add_run()
                    br.text = f"• {item}"
                    set_font(br, 8, color=TEXT_DARK)
        sp = tf.add_paragraph()
        sp.space_before = Pt(6)
        sr = sp.add_run()
        sr.text = f"Источник: {source}"
        set_font(sr, 7, color=TEXT_MUTED)

    def variants_summary(self):
        """Сводный слайд: особенности, ТРЗ, плюсы и минусы по всем трём вариантам."""
        pg = self._next()
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        apply_frame(slide, "Сводка по вариантам: особенности, ТРЗ, плюсы и минусы", pg)

        variants = [
            ("Вариант 1\nЦелевой перенос", COL_V1, "1-file.feUnSR", {
                "trz": "Не оценивался",
                "feat": [
                    "Оркестрация в Airflow ЕАРМ",
                    "Песочница MVP для моделей",
                    "Перенос компонентов из ЦМ ИМА БРД",
                    "Единая точка входа для ДО",
                ],
                "pros": [
                    "Единая целевая платформа",
                    "Централизация ТМ и расчётов",
                    "Соответствие целевому ландшафту",
                ],
                "cons": [
                    "Максимальный объём изменений",
                    "ТРЗ требует отдельной оценки",
                    "Длительный переходный период",
                ],
            }),
            ("Вариант 2\nВстраивание (ЕАРМ-1)", COL_V2, "2_file.OVCeIx", {
                "trz": f"{TOTAL_EAPM1[0]} ч/д (без риска)\n{TOTAL_EAPM1[1]} ч/д (с риском)",
                "feat": [
                    "Перенос стека CH, PG, Airflow, NiFi…",
                    "Миграция дампов и CI/CD",
                    "Переработка DAG (API, атомарность)",
                    "Устранение уязвимостей (~134 ч/д)",
                ],
                "pros": [
                    "Полная консолидация в ЕАРМ",
                    "Контроль ТМ через NiFi (АДКУ)",
                    "Grafana в frontend ЕАРМ",
                ],
                "cons": [
                    "Максимальные ТРЗ (~282 ч/д)",
                    "Риски при переносе prod-данных",
                    "Высокие затраты на миграцию",
                ],
            }),
            ("Вариант 3\nИнтеграция (ЕАРМ-2)", COL_V3, "3_file.ekYFFz", {
                "trz": f"{TOTAL_EAPM2[0]} ч/д (без риска)\n{TOTAL_EAPM2[1]} ч/д (с риском)",
                "feat": [
                    "Вызов расчётов через API AirFlow",
                    "ТМ: АДКУ → NiFi ЕАРМ → ClickHouse",
                    "Без переноса стека и дампов",
                    "ЦМ ИМА — отдельная система",
                ],
                "pros": [
                    "Минимальные ТРЗ (−55% vs В2)",
                    "Быстрый выход на интеграцию",
                    "Сохранение экспертизы ЦМ ИМА",
                ],
                "cons": [
                    "Два контура эксплуатации",
                    "Зависимость от API-контрактов",
                    "Риск МСЭ OKD→DH",
                ],
            }),
        ]

        col_w = Inches(4.05)
        gap = Inches(0.12)
        top = Inches(1.02)
        col_h = Inches(5.75)

        for i, (title, color, source, data) in enumerate(variants):
            x = Inches(0.38) + i * (col_w + gap)

            hdr = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, top, col_w, Inches(0.55))
            hdr.fill.solid()
            hdr.fill.fore_color.rgb = color
            hdr.line.fill.background()
            ht = slide.shapes.add_textbox(x, top + Inches(0.06), col_w, Inches(0.45))
            hp = ht.text_frame.paragraphs[0]
            hp.alignment = PP_ALIGN.CENTER
            hr = hp.add_run()
            hr.text = title
            set_font(hr, 10, True, WHITE)

            body = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, top + Inches(0.55),
                                          col_w, col_h - Inches(0.55))
            body.fill.solid()
            body.fill.fore_color.rgb = WHITE
            body.line.color.rgb = color

            tx = slide.shapes.add_textbox(x + Inches(0.12), top + Inches(0.62),
                                          col_w - Inches(0.24), col_h - Inches(0.7))
            self._fill_variant_column(tx.text_frame, data, source, color)

        foot = slide.shapes.add_textbox(Inches(0.4), Inches(6.82), Inches(12.5), Inches(0.25))
        fr = foot.text_frame.paragraphs[0].add_run()
        fr.text = "ТРЗ вариантов 2 и 3 — из бэклогов Excel (листы «Бэклог ЦМ ИМА в ЕАРМ-1» и «ЕАРМ-2»)"
        set_font(fr, 8, color=TEXT_MUTED)
        return slide

    def rating_analytics(self):
        """Нативная матрица рейтинга + итоговые баллы + методика."""
        pg = self._next()
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        apply_frame(slide, "Сводная аналитика: рейтинг вариантов", pg)

        matrix = list(zip(RATING_CRITERIA, RATING_V1, RATING_V2, RATING_V3))
        n = len(matrix) + 1

        tbl = slide.shapes.add_table(n, 4, Inches(0.4), Inches(1.05), Inches(7.6), Inches(4.35)).table
        tbl.columns[0].width = Inches(3.4)
        tbl.columns[1].width = Inches(1.4)
        tbl.columns[2].width = Inches(1.4)
        tbl.columns[3].width = Inches(1.4)

        for c, h in enumerate(["Критерий", "В1 — перенос", "В2 — ЕАРМ-1", "В3 — ЕАРМ-2"]):
            style_table_header(tbl.cell(0, c), h)

        for ri, (crit, s1, s2, s3) in enumerate(matrix, 1):
            style_table_cell(tbl.cell(ri, 0), crit, alt=(ri % 2 == 0))
            style_score_cell(tbl.cell(ri, 1), s1)
            style_score_cell(tbl.cell(ri, 2), s2)
            style_score_cell(tbl.cell(ri, 3), s3)

        scale = slide.shapes.add_textbox(Inches(0.45), Inches(5.48), Inches(7.5), Inches(0.28))
        sr = scale.text_frame.paragraphs[0].add_run()
        sr.text = "Шкала: 1 — низко  ·  5 — высоко  |  Тёмнее ячейка = выше балл"
        set_font(sr, 8, color=TEXT_MUTED)

        hdr = slide.shapes.add_textbox(Inches(8.3), Inches(1.05), Inches(4.6), Inches(0.35))
        hr = hdr.text_frame.paragraphs[0].add_run()
        hr.text = "Итоговый взвешенный рейтинг"
        set_font(hr, 13, True, NAVY)

        wsum = sum(RATING_WEIGHTS)
        overall = [
            ("В1 — целевой перенос", sum(a * b for a, b in zip(RATING_V1, RATING_WEIGHTS)) / wsum, COL_V1),
            ("В2 — встраивание", sum(a * b for a, b in zip(RATING_V2, RATING_WEIGHTS)) / wsum, COL_V2),
            ("В3 — интеграция", sum(a * b for a, b in zip(RATING_V3, RATING_WEIGHTS)) / wsum, COL_V3),
        ]
        bar_left = Inches(9.5)
        bar_max_w = Inches(3.2)
        for i, (name, score, color) in enumerate(overall):
            y = Inches(1.55 + i * 0.72)
            lb = slide.shapes.add_textbox(Inches(8.3), y, Inches(1.1), Inches(0.35))
            lr = lb.text_frame.paragraphs[0].add_run()
            lr.text = name
            set_font(lr, 9, color=TEXT_DARK)
            bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bar_left, y + Inches(0.05),
                                        bar_max_w, Inches(0.22))
            bg.fill.solid()
            bg.fill.fore_color.rgb = TABLE_ALT
            bg.line.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
            fg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bar_left, y + Inches(0.05),
                                        int(bar_max_w * score / 5), Inches(0.22))
            fg.fill.solid()
            fg.fill.fore_color.rgb = color
            fg.line.fill.background()
            val = slide.shapes.add_textbox(bar_left + bar_max_w + Inches(0.1), y, Inches(0.9), Inches(0.35))
            vr = val.text_frame.paragraphs[0].add_run()
            vr.text = f"{score:.1f}/5"
            set_font(vr, 10, True, color)

        sc_box = slide.shapes.add_textbox(Inches(8.3), Inches(3.85), Inches(4.6), Inches(1.5))
        stf = sc_box.text_frame
        stf.word_wrap = True
        p0 = stf.paragraphs[0]
        r0 = p0.add_run()
        r0.text = "Рекомендуемые сценарии"
        set_font(r0, 11, True, NAVY)
        for line in [
            "Краткосрочный старт → Вариант 3",
            "Полная консолидация → Вариант 2",
            "Стратегическая цель → Вариант 1",
        ]:
            p = stf.add_paragraph()
            p.space_before = Pt(4)
            r = p.add_run()
            r.text = f"• {line}"
            set_font(r, 9, color=TEXT_DARK)

        meth_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(5.85),
                                         Inches(12.5), Inches(1.05))
        meth_bg.fill.solid()
        meth_bg.fill.fore_color.rgb = TABLE_ALT
        meth_bg.line.color.rgb = NAVY

        meth = slide.shapes.add_textbox(Inches(0.55), Inches(5.92), Inches(12.2), Inches(0.92))
        mtf = meth.text_frame
        mtf.word_wrap = True
        lines = [
            "Источник оценок:  ",
            "Экономичность (ТРЗ) — бэклоги Excel: ЕАРМ-1 = 281,7 ч/д (2_file.OVCeIx), ЕАРМ-2 = 126,6 ч/д (3_file.ekYFFz); В1 — ТРЗ не оценивался, балл 3 (оценочно).  ",
            "Остальные критерии — экспертная оценка схем 1-file.feUnSR / 2_file.OVCeIx / 3_file.ekYFFz (шкала 1–5).  ",
            "Итог = взвешенное среднее (экономичность ×1,5; риски ×1,3; скорость ×1,2; архитектура ×1,2).",
        ]
        for i, line in enumerate(lines):
            p = mtf.paragraphs[0] if i == 0 else mtf.add_paragraph()
            r = p.add_run()
            r.text = line
            set_font(r, 8 if i > 0 else 9, bold=(i == 0), color=NAVY if i == 0 else TEXT_DARK)
        return slide

    def save(self) -> Path:
        path = OUT_DIR / "CM_IMA_EAPM_variants_comparison.pptx"
        self.prs.save(path)
        return path


def build_presentation() -> Path:
    ASSETS.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    s = SlideBuilder()

    s.title(
        "Варианты интеграции ЦМ ИМА и ЕАРМ",
        "Сравнительный анализ архитектуры, трудозатрат и рекомендаций",
    )

    s.bullets("Цель и контекст", [
        "Обеспечить расчёты моделей ИМА в целевом ландшафте ЕАРМ.",
        "Рассмотрены три архитектурных варианта с разной глубиной интеграции ЦМ ИМА.",
        "ТРЗ вариантов 2 и 3 — из бэклогов Excel (листы ЕАРМ-1 и ЕАРМ-2).",
        "Вариант 1 — целевая концепция без количественной оценки ТРЗ.",
    ])

    s.bullets("Обзор трёх вариантов", [
        "Вариант 1 — перенос функционала ЦМ ИМА в ЕАРМ (целевое решение + песочница).",
        "Вариант 2 — встраивание стека ЦМ ИМА БРД в ЕАРМ (ЕАРМ-1).",
        "Вариант 3 — интеграция с ЦМ ИМА как с отдельной ИТ-системой (ЕАРМ-2).",
    ], sub={
        0: ["Источник: 1-file.feUnSR"],
        1: ["Источник: 2_file.OVCeIx | ТРЗ: 281,7 ч/д"],
        2: ["Источник: 3_file.ekYFFz | ТРЗ: 126,6 ч/д"],
    })

    s.section("Вариант 1. Перенос функционала ЦМ ИМА в ЕАРМ")
    s.image("Архитектура: целевой перенос функционала", ASSETS / "variant1_transfer.png",
            "Источник: 1-file.feUnSR  |  ТРЗ: не оценивался")
    s.bullets("Вариант 1 — ключевые особенности", [
        "Оркестрация расчётов в Airflow (N1) ЕАРМ.",
        "Валидированная ТМ из ClickHouse; данные с Дата-платформы.",
        "Результаты в Postgres Pro и ClickHouse; отчётность в ГПН КЦ / Заполярье.",
        "MVP ЦМ ИМА — песочница для разработки моделей.",
    ])
    s.two_col("Вариант 1 — плюсы и минусы", "Плюсы", [
        "Единая платформа и точка входа для пользователей ДО.",
        "Централизованное управление ТМ, расчётами и результатами.",
        "Песочница для экспериментов без влияния на прод.",
        "Соответствие целевому ИТ-ландшафту ЕАРМ.",
    ], "Минусы", [
        "Наибольший объём организационных и технических изменений.",
        "ТРЗ не оценён — требуется отдельная проработка.",
        "Длительный переходный период.",
        "Зависимость от готовности NiFi, Kafka, S3.",
    ])

    s.section("Вариант 2. Встраивание ЦМ ИМА в ЕАРМ (ЕАРМ-1)")
    s.image("Архитектура: встраивание стека ЦМ ИМА БРД", ASSETS / "variant2_embedding.png",
            "Источник: 2_file.OVCeIx  |  Бэклог: «Бэклог ЦМ ИМА в ЕАРМ-1»")
    s.bullets("Вариант 2 — особенности и ТРЗ", [
        f"Итого ТРЗ: {TOTAL_EAPM1[0]} ч/д (без риска) / {TOTAL_EAPM1[1]} ч/д (с риском).",
        "Перенос стека: ClickHouse, Postgres, Airflow, NiFi, Kafka, Grafana, S3.",
        "Переработка DAG-ов: API, атомарность данных.",
        "Миграция дампов, CI/CD, устранение уязвимостей (~134 ч/д).",
    ])
    s.two_col("Вариант 2 — плюсы и минусы", "Плюсы", [
        "Полная консолидация — один контур эксплуатации.",
        "Контроль ТМ через NiFi ЕАРМ (АДКУ → Kafka).",
        "Grafana встраивается в frontend ЕАРМ.",
    ], "Минусы", [
        "Максимальные ТРЗ (~282 ч/д).",
        "Высокие затраты на миграцию и CI/CD.",
        "Риски простоя при переносе production-данных.",
    ])
    s.table_backlog("Бэклог ЕАРМ-1 — детализация ТРЗ", BACKLOG_EAPM1, TOTAL_EAPM1)

    s.section("Вариант 3. Интеграция без приземления (ЕАРМ-2)")
    s.image("Архитектура: ЦМ ИМА как отдельная ИТ-система", ASSETS / "variant3_integration.png",
            "Источник: 3_file.ekYFFz  |  Бэклог: «Бэклог ЦМ ИМА в ЕАРМ-2»")
    s.bullets("Вариант 3 — особенности и ТРЗ", [
        f"Итого ТРЗ: {TOTAL_EAPM2[0]} ч/д (без риска) / {TOTAL_EAPM2[1]} ч/д (с риском).",
        "Вызов расчётов в Airflow ЦМ ИМА через API.",
        "NiFi ЕАРМ получает ТМ из АДКУ; ЦМ ИМА читает валидированную ТМ из ClickHouse ЕАРМ.",
        "Нет переноса стека и дампов.",
    ])
    s.two_col("Вариант 3 — плюсы и минусы", "Плюсы", [
        "Минимальные ТРЗ: ~127 ч/д (−55% vs В2).",
        "Быстрый выход на целевые интеграционные потоки.",
        "Сохранение экспертизы и стека ЦМ ИМА.",
    ], "Минусы", [
        "Два контура эксплуатации.",
        "Зависимость от API-контрактов AirFlow.",
        "Риск МСЭ OKD→DH.",
    ])
    s.table_backlog("Бэклог ЕАРМ-2 — детализация ТРЗ", BACKLOG_EAPM2, TOTAL_EAPM2)

    s.variants_summary()
    s.image(
        "Сравнение вариантов: диаграммы",
        ASSETS / "variants_comparison_charts.png",
        "Столбцы — ТРЗ (ч/д) | Кольцевая — итоговый рейтинг | Гистограмма — критерии | Врезка — индексы плюсов/минусов",
    )
    s.comparison()
    s.rating_analytics()
    s.bullets("Выводы и рекомендации", [
        "Вариант 1 — стратегическое направление; требуется оценка ТРЗ.",
        "Вариант 2 — полная консолидация с максимальными трудозатратами.",
        "Вариант 3 — оптимален как поэтапный шаг: быстрее и дешевле.",
        "Рекомендуемая траектория: В3 → накопление опыта → В1/В2.",
        "Критично согласовать API AirFlow и источник валидированной ТМ до старта.",
    ])

    s.title("Спасибо за внимание", "Вопросы и обсуждение")
    return s.save()


if __name__ == "__main__":
    path = build_presentation()
    print(f"Presentation saved: {path}")
