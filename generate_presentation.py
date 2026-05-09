"""
Презентация "План путешествия Арсена и Женечки в Италию"
07.06.2026 — 20.06.2026
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from copy import deepcopy
from lxml import etree


# ------------------- Цветовая палитра (итальянский флаг + тёплые тона) ------------------- #
COLOR_GREEN       = RGBColor(0x0B, 0x6E, 0x4F)   # глубокий зелёный
COLOR_RED         = RGBColor(0xC8, 0x3E, 0x36)   # терракотово-красный
COLOR_CREAM       = RGBColor(0xFA, 0xF3, 0xE7)   # кремовый фон
COLOR_GOLD        = RGBColor(0xC9, 0xA2, 0x27)   # золотой акцент
COLOR_DARK        = RGBColor(0x2B, 0x2B, 0x2B)   # основной текст
COLOR_GREY        = RGBColor(0x6B, 0x6B, 0x6B)   # вторичный текст
COLOR_WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
COLOR_LIGHT_GREEN = RGBColor(0xE8, 0xF1, 0xEC)
COLOR_LIGHT_RED   = RGBColor(0xFB, 0xEC, 0xEA)
COLOR_LIGHT_GOLD  = RGBColor(0xFA, 0xF3, 0xDC)


# ------------------- Конфигурация ------------------- #
prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
SLIDE_W = prs.slide_width
SLIDE_H = prs.slide_height
BLANK = prs.slide_layouts[6]


# ------------------- Утилиты ------------------- #
def add_rect(slide, x, y, w, h, fill, line=None, shadow=False):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(0.75)
    if not shadow:
        # Уберём тень
        sp = shape.shadow
        sp.inherit = False
    shape.shadow.inherit = False
    return shape


def add_round_rect(slide, x, y, w, h, fill, line=None, radius=0.08):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shape.adjustments[0] = radius
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(1)
    shape.shadow.inherit = False
    return shape


def add_text(slide, x, y, w, h, text, *, size=18, bold=False, italic=False,
             color=COLOR_DARK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font="Calibri"):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return tb


def add_multi_text(slide, x, y, w, h, lines, *, default_size=14, default_color=COLOR_DARK,
                   align=PP_ALIGN.LEFT, font="Calibri", line_spacing=1.15):
    """lines: список dict с ключами text, size, bold, italic, color, bullet (optional)"""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.alignment = line.get("align", align)
        p.line_spacing = line.get("line_spacing", line_spacing)
        if line.get("space_before"):
            p.space_before = Pt(line["space_before"])
        if line.get("space_after"):
            p.space_after = Pt(line["space_after"])
        run = p.add_run()
        run.text = line["text"]
        run.font.name = line.get("font", font)
        run.font.size = Pt(line.get("size", default_size))
        run.font.bold = line.get("bold", False)
        run.font.italic = line.get("italic", False)
        run.font.color.rgb = line.get("color", default_color)
    return tb


def add_line(slide, x1, y1, x2, y2, color=COLOR_GOLD, width=1.5, dash=False):
    line = slide.shapes.add_connector(1, x1, y1, x2, y2)
    line.line.color.rgb = color
    line.line.width = Pt(width)
    if dash:
        ln = line.line._get_or_add_ln()
        prstDash = etree.SubElement(ln, qn('a:prstDash'))
        prstDash.set('val', 'dash')
    return line


def slide_background(slide, color=COLOR_CREAM):
    bg = add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, color)
    return bg


def add_header_band(slide, title, subtitle=None):
    add_rect(slide, 0, 0, SLIDE_W, Inches(1.1), COLOR_GREEN)
    add_rect(slide, 0, Inches(1.1), SLIDE_W, Inches(0.05), COLOR_GOLD)
    add_text(slide, Inches(0.6), Inches(0.18), Inches(11), Inches(0.6),
             title, size=28, bold=True, color=COLOR_WHITE)
    if subtitle:
        add_text(slide, Inches(0.6), Inches(0.66), Inches(11), Inches(0.4),
                 subtitle, size=14, italic=True, color=COLOR_LIGHT_GOLD)


def add_footer(slide, page_num, total):
    add_rect(slide, 0, SLIDE_H - Inches(0.35), SLIDE_W, Inches(0.35), COLOR_GREEN)
    add_text(slide, Inches(0.5), SLIDE_H - Inches(0.34), Inches(8), Inches(0.32),
             "Италия 2026  ·  Арсен & Женечка  ·  07.06 — 20.06",
             size=10, color=COLOR_LIGHT_GOLD, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, SLIDE_W - Inches(1.5), SLIDE_H - Inches(0.34), Inches(1), Inches(0.32),
             f"{page_num} / {total}",
             size=10, color=COLOR_LIGHT_GOLD,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)


# ============================================================ #
#                       СЛАЙД 1: ТИТУЛЬНЫЙ                      #
# ============================================================ #
def make_title_slide(slide):
    # Фон с градиентом-имитация: три полосы итальянского флага сверху и снизу
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, COLOR_CREAM)

    # Декоративная цветная полоса наверху (флаг)
    band_h = Inches(0.4)
    third = SLIDE_W // 3
    add_rect(slide, 0, 0, third, band_h, COLOR_GREEN)
    add_rect(slide, third, 0, third, band_h, COLOR_WHITE)
    add_rect(slide, 2 * third, 0, SLIDE_W - 2 * third, band_h, COLOR_RED)

    # Полоса внизу
    add_rect(slide, 0, SLIDE_H - band_h, third, band_h, COLOR_GREEN)
    add_rect(slide, third, SLIDE_H - band_h, third, band_h, COLOR_WHITE)
    add_rect(slide, 2 * third, SLIDE_H - band_h, SLIDE_W - 2 * third, band_h, COLOR_RED)

    # Большая центральная карточка
    card_w = Inches(10.5)
    card_h = Inches(4.8)
    card_x = (SLIDE_W - card_w) // 2
    card_y = (SLIDE_H - card_h) // 2
    add_round_rect(slide, card_x, card_y, card_w, card_h, COLOR_WHITE,
                   line=COLOR_GOLD, radius=0.04)

    # Декоративная плашка вверху карточки
    add_rect(slide, card_x + Inches(0.4), card_y + Inches(0.5),
             card_w - Inches(0.8), Inches(0.04), COLOR_GOLD)

    # Маленький шрифт-надстрочник
    add_text(slide, card_x, card_y + Inches(0.65), card_w, Inches(0.4),
             "ИТАЛИЯ  ·  ROMA  ·  FIRENZE  ·  VENEZIA",
             size=16, bold=True, color=COLOR_GOLD, align=PP_ALIGN.CENTER,
             font="Calibri")

    # Главный заголовок
    add_text(slide, card_x, card_y + Inches(1.25), card_w, Inches(1.4),
             "План путешествия",
             size=68, bold=True, color=COLOR_GREEN, align=PP_ALIGN.CENTER,
             font="Georgia")

    # Подзаголовок-курсив
    add_text(slide, card_x, card_y + Inches(2.55), card_w, Inches(0.5),
             "“La dolce vita”",
             size=22, italic=True, color=COLOR_RED, align=PP_ALIGN.CENTER,
             font="Georgia")

    # Разделитель
    add_line(slide, card_x + Inches(4), card_y + Inches(3.25),
             card_x + card_w - Inches(4), card_y + Inches(3.25),
             color=COLOR_GOLD, width=1.5)

    # Имена путешественников
    add_text(slide, card_x, card_y + Inches(3.4), card_w, Inches(0.5),
             "Арсен  &  Женечка",
             size=24, bold=True, color=COLOR_DARK, align=PP_ALIGN.CENTER,
             font="Georgia")

    # Даты
    add_text(slide, card_x, card_y + Inches(4.0), card_w, Inches(0.4),
             "7 июня — 20 июня 2026",
             size=18, color=COLOR_GREY, align=PP_ALIGN.CENTER, italic=True)


# ============================================================ #
#                     СЛАЙД 2: АВИАБИЛЕТЫ                       #
# ============================================================ #
def make_flights_slide(slide, page, total):
    slide_background(slide, COLOR_CREAM)
    add_header_band(slide, "Авиабилеты — FlyOne",
                    "Маршрут Санкт-Петербург ⇄ Рим")

    # Под-заголовок: логотип-плашка
    badge_x, badge_y = Inches(0.6), Inches(1.4)
    add_round_rect(slide, badge_x, badge_y, Inches(2.0), Inches(0.6),
                   COLOR_RED, radius=0.4)
    add_text(slide, badge_x, badge_y, Inches(2.0), Inches(0.6),
             "✈  FlyOne", size=20, bold=True, color=COLOR_WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    add_text(slide, Inches(2.8), Inches(1.45), Inches(8), Inches(0.5),
             "Прямые рейсы  ·  багаж и ручная кладь по тарифу  ·  бронирование заранее",
             size=13, italic=True, color=COLOR_GREY, anchor=MSO_ANCHOR.MIDDLE)

    # ---------- Карточка 1: Туда ---------- #
    c1_x, c1_y = Inches(0.6), Inches(2.25)
    c1_w, c1_h = Inches(6.05), Inches(4.5)
    add_round_rect(slide, c1_x, c1_y, c1_w, c1_h, COLOR_WHITE,
                   line=COLOR_GREEN, radius=0.04)
    # Шапка карточки
    add_rect(slide, c1_x, c1_y, c1_w, Inches(0.7), COLOR_GREEN)

    # Округлим только верх — добавим имитацию через скрытие нижнего края
    add_text(slide, c1_x, c1_y, c1_w, Inches(0.7),
             "ТУДА  ·  Рейс №1", size=18, bold=True, color=COLOR_WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # Город отправления
    add_text(slide, c1_x + Inches(0.3), c1_y + Inches(0.95), Inches(2.6), Inches(0.5),
             "Санкт-Петербург", size=16, bold=True, color=COLOR_DARK)
    add_text(slide, c1_x + Inches(0.3), c1_y + Inches(1.4), Inches(2.6), Inches(0.4),
             "LED  ·  Пулково", size=12, color=COLOR_GREY)

    # Стрелка / самолёт
    add_text(slide, c1_x + Inches(2.95), c1_y + Inches(0.95), Inches(0.6), Inches(0.9),
             "✈", size=34, color=COLOR_GOLD, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)

    # Город прилёта
    add_text(slide, c1_x + Inches(3.6), c1_y + Inches(0.95), Inches(2.3), Inches(0.5),
             "Рим", size=16, bold=True, color=COLOR_DARK, align=PP_ALIGN.RIGHT)
    add_text(slide, c1_x + Inches(3.6), c1_y + Inches(1.4), Inches(2.3), Inches(0.4),
             "FCO  ·  Леонардо да Винчи", size=12, color=COLOR_GREY,
             align=PP_ALIGN.RIGHT)

    # Линия с пунктиром
    add_line(slide, c1_x + Inches(0.3), c1_y + Inches(2.0),
             c1_x + c1_w - Inches(0.3), c1_y + Inches(2.0),
             color=COLOR_GOLD, width=1, dash=True)

    # Время вылета и прилёта
    add_text(slide, c1_x + Inches(0.3), c1_y + Inches(2.15), Inches(2.6), Inches(0.4),
             "ВЫЛЕТ", size=11, bold=True, color=COLOR_GREEN)
    add_text(slide, c1_x + Inches(0.3), c1_y + Inches(2.5), Inches(2.6), Inches(0.7),
             "22:00", size=36, bold=True, color=COLOR_DARK, font="Georgia")
    add_text(slide, c1_x + Inches(0.3), c1_y + Inches(3.25), Inches(2.6), Inches(0.4),
             "вс, 7 июня 2026", size=12, color=COLOR_GREY, italic=True)

    add_text(slide, c1_x + Inches(3.0), c1_y + Inches(2.15), Inches(2.9), Inches(0.4),
             "ПРИЛЁТ", size=11, bold=True, color=COLOR_RED, align=PP_ALIGN.RIGHT)
    add_text(slide, c1_x + Inches(3.0), c1_y + Inches(2.5), Inches(2.9), Inches(0.7),
             "20:10", size=36, bold=True, color=COLOR_DARK, align=PP_ALIGN.RIGHT,
             font="Georgia")
    add_text(slide, c1_x + Inches(3.0), c1_y + Inches(3.25), Inches(2.9), Inches(0.4),
             "пн, 8 июня 2026", size=12, color=COLOR_GREY, italic=True,
             align=PP_ALIGN.RIGHT)

    # Доп. инфо в нижней плашке
    add_rect(slide, c1_x, c1_y + Inches(3.85), c1_w, Inches(0.65), COLOR_LIGHT_GREEN)
    add_text(slide, c1_x + Inches(0.3), c1_y + Inches(3.85), c1_w - Inches(0.6),
             Inches(0.65),
             "В пути  ~ 4 ч 10 мин  (с учётом разницы во времени −1 ч)",
             size=12, italic=True, color=COLOR_GREEN, anchor=MSO_ANCHOR.MIDDLE)

    # ---------- Карточка 2: Обратно ---------- #
    c2_x, c2_y = Inches(6.7), Inches(2.25)
    c2_w, c2_h = Inches(6.05), Inches(4.5)
    add_round_rect(slide, c2_x, c2_y, c2_w, c2_h, COLOR_WHITE,
                   line=COLOR_RED, radius=0.04)
    add_rect(slide, c2_x, c2_y, c2_w, Inches(0.7), COLOR_RED)
    add_text(slide, c2_x, c2_y, c2_w, Inches(0.7),
             "ОБРАТНО  ·  Рейс №2", size=18, bold=True, color=COLOR_WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    add_text(slide, c2_x + Inches(0.3), c2_y + Inches(0.95), Inches(2.6), Inches(0.5),
             "Рим", size=16, bold=True, color=COLOR_DARK)
    add_text(slide, c2_x + Inches(0.3), c2_y + Inches(1.4), Inches(2.6), Inches(0.4),
             "FCO  ·  Фьюмичино", size=12, color=COLOR_GREY)

    add_text(slide, c2_x + Inches(2.95), c2_y + Inches(0.95), Inches(0.6), Inches(0.9),
             "✈", size=34, color=COLOR_GOLD, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)

    add_text(slide, c2_x + Inches(3.6), c2_y + Inches(0.95), Inches(2.3), Inches(0.5),
             "Санкт-Петербург", size=16, bold=True, color=COLOR_DARK,
             align=PP_ALIGN.RIGHT)
    add_text(slide, c2_x + Inches(3.6), c2_y + Inches(1.4), Inches(2.3), Inches(0.4),
             "LED  ·  Пулково", size=12, color=COLOR_GREY, align=PP_ALIGN.RIGHT)

    add_line(slide, c2_x + Inches(0.3), c2_y + Inches(2.0),
             c2_x + c2_w - Inches(0.3), c2_y + Inches(2.0),
             color=COLOR_GOLD, width=1, dash=True)

    add_text(slide, c2_x + Inches(0.3), c2_y + Inches(2.15), Inches(2.6), Inches(0.4),
             "ВЫЛЕТ", size=11, bold=True, color=COLOR_GREEN)
    add_text(slide, c2_x + Inches(0.3), c2_y + Inches(2.5), Inches(2.6), Inches(0.7),
             "11:55", size=36, bold=True, color=COLOR_DARK, font="Georgia")
    add_text(slide, c2_x + Inches(0.3), c2_y + Inches(3.25), Inches(2.6), Inches(0.4),
             "сб, 20 июня 2026", size=12, color=COLOR_GREY, italic=True)

    add_text(slide, c2_x + Inches(3.0), c2_y + Inches(2.15), Inches(2.9), Inches(0.4),
             "ПРИЛЁТ", size=11, bold=True, color=COLOR_RED, align=PP_ALIGN.RIGHT)
    add_text(slide, c2_x + Inches(3.0), c2_y + Inches(2.5), Inches(2.9), Inches(0.7),
             "21:00", size=36, bold=True, color=COLOR_DARK, align=PP_ALIGN.RIGHT,
             font="Georgia")
    add_text(slide, c2_x + Inches(3.0), c2_y + Inches(3.25), Inches(2.9), Inches(0.4),
             "вс, 21 июня 2026", size=12, color=COLOR_GREY, italic=True,
             align=PP_ALIGN.RIGHT)

    add_rect(slide, c2_x, c2_y + Inches(3.85), c2_w, Inches(0.65), COLOR_LIGHT_RED)
    add_text(slide, c2_x + Inches(0.3), c2_y + Inches(3.85), c2_w - Inches(0.6),
             Inches(0.65),
             "В пути  ~ 5 ч 05 мин  (через стыковку  /  с учётом разницы +1 ч)",
             size=12, italic=True, color=COLOR_RED, anchor=MSO_ANCHOR.MIDDLE)

    add_footer(slide, page, total)


# ============================================================ #
#                СЛАЙД 3: ОБЗОР МАРШРУТА                        #
# ============================================================ #
def make_route_overview_slide(slide, page, total):
    slide_background(slide, COLOR_CREAM)
    add_header_band(slide, "Маршрут: Рим → Флоренция → Венеция",
                    "12 дней · 3 города · без ранних подъёмов · с сиестой 14:00–16:30")

    # Линия маршрута с тремя точками
    line_y = Inches(2.4)
    p1_x = Inches(2.0)
    p2_x = Inches(6.665)
    p3_x = Inches(11.333)

    add_line(slide, p1_x, line_y, p3_x, line_y, color=COLOR_GOLD, width=3)

    def add_city_pin(x, name, dates, color, nights):
        # Кружок
        size = Inches(0.6)
        circle = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                        x - size/2, line_y - size/2, size, size)
        circle.fill.solid()
        circle.fill.fore_color.rgb = color
        circle.line.color.rgb = COLOR_WHITE
        circle.line.width = Pt(3)
        circle.shadow.inherit = False

        add_text(slide, x - Inches(1.5), line_y - Inches(1.4), Inches(3.0), Inches(0.6),
                 name, size=24, bold=True, color=color, align=PP_ALIGN.CENTER,
                 font="Georgia")
        add_text(slide, x - Inches(1.5), line_y - Inches(0.9), Inches(3.0), Inches(0.4),
                 dates, size=13, color=COLOR_DARK, align=PP_ALIGN.CENTER, italic=True)
        add_text(slide, x - Inches(1.5), line_y + Inches(0.5), Inches(3.0), Inches(0.4),
                 f"{nights} ночей", size=12, bold=True, color=COLOR_GREY,
                 align=PP_ALIGN.CENTER)

    add_city_pin(p1_x, "Roma",     "8 — 13 июня",  COLOR_RED,   "5")
    add_city_pin(p2_x, "Firenze",  "13 — 17 июня", COLOR_GREEN, "4")
    add_city_pin(p3_x, "Venezia",  "17 — 19 июня", COLOR_GOLD,  "2")

    # Подсказка о возвращении
    add_text(slide, Inches(0.6), Inches(3.45), Inches(12.1), Inches(0.4),
             "→  19 июня вечером возвращаемся в Рим (ночь у аэропорта),  20 июня — вылет в 11:55",
             size=12, italic=True, color=COLOR_GREY, align=PP_ALIGN.CENTER)

    # Три карточки с описанием
    card_y = Inches(4.0)
    card_w = Inches(4.0)
    card_h = Inches(3.0)
    gap = Inches(0.15)
    start_x = (SLIDE_W - card_w * 3 - gap * 2) // 2

    cards = [
        {
            "title": "Roma",
            "subtitle": "Вечный город",
            "color": COLOR_RED,
            "lines": [
                "•  Колизей и Римский форум",
                "•  Ватикан и Сикстинская капелла",
                "•  Пантеон, Треви, Навона",
                "•  Галерея Боргезе",
                "•  Трастевере вечером",
            ],
        },
        {
            "title": "Firenze",
            "subtitle": "Колыбель Ренессанса",
            "color": COLOR_GREEN,
            "lines": [
                "•  Дуомо и купол Брунеллески",
                "•  Галерея Уффици",
                "•  Давид в Академии",
                "•  Сады Боболи и Палаццо Питти",
                "•  Понте-Веккьо на закате",
            ],
        },
        {
            "title": "Venezia",
            "subtitle": "Город на воде",
            "color": COLOR_GOLD,
            "lines": [
                "•  Площадь и собор Сан-Марко",
                "•  Дворец дожей и Мост вздохов",
                "•  Прогулка на гондоле",
                "•  Биеннале Arte 2026",
                "•  Каналы Каннареджо",
            ],
        },
    ]

    for i, c in enumerate(cards):
        x = start_x + i * (card_w + gap)
        add_round_rect(slide, x, card_y, card_w, card_h, COLOR_WHITE,
                       line=c["color"], radius=0.05)
        add_rect(slide, x, card_y, card_w, Inches(0.55), c["color"])
        add_text(slide, x, card_y, card_w, Inches(0.55),
                 c["title"], size=18, bold=True, color=COLOR_WHITE,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, font="Georgia")
        add_text(slide, x, card_y + Inches(0.6), card_w, Inches(0.35),
                 c["subtitle"], size=11, italic=True, color=COLOR_GREY,
                 align=PP_ALIGN.CENTER)
        # Список
        lines_data = [{"text": ln, "size": 12, "color": COLOR_DARK,
                       "space_after": 4} for ln in c["lines"]]
        add_multi_text(slide, x + Inches(0.3), card_y + Inches(1.05),
                       card_w - Inches(0.6), card_h - Inches(1.2),
                       lines_data, default_size=12)

    add_footer(slide, page, total)


# ============================================================ #
#               СЛАЙД ГОРОДА (универсальный шаблон)             #
# ============================================================ #
def make_city_slide(slide, *, page, total, city_title, city_subtitle, accent,
                    light_accent, days, attractions, tips, header_title):
    """
    days        : список dict {day, date, plan} — план посещения
    attractions : список dict {name, price, note}
    tips        : список строк (горизонтальный баннер сверху)
    """
    slide_background(slide, COLOR_CREAM)
    add_header_band(slide, header_title, city_subtitle)

    # ---------- Горизонтальный баннер: Режим дня (tips) ---------- #
    banner_x = Inches(0.6)
    banner_y = Inches(1.3)
    banner_w = SLIDE_W - Inches(1.2)
    banner_h = Inches(0.55)
    add_round_rect(slide, banner_x, banner_y, banner_w, banner_h,
                   COLOR_LIGHT_GOLD, line=COLOR_GOLD, radius=0.3)
    add_text(slide, banner_x + Inches(0.25), banner_y, Inches(2.0), banner_h,
             "☀  Режим дня",
             size=13, bold=True, color=COLOR_GOLD,
             anchor=MSO_ANCHOR.MIDDLE)
    tip_text = "  ·  ".join(tips)
    add_text(slide, banner_x + Inches(2.1), banner_y, banner_w - Inches(2.3),
             banner_h,
             tip_text, size=10, color=COLOR_DARK, anchor=MSO_ANCHOR.MIDDLE)

    # ---------- Левая колонка: ПЛАН ПО ДНЯМ ---------- #
    left_x = Inches(0.6)
    left_y = Inches(2.0)
    left_w = Inches(7.2)
    left_h = Inches(5.1)
    add_round_rect(slide, left_x, left_y, left_w, left_h, COLOR_WHITE,
                   line=accent, radius=0.02)
    add_rect(slide, left_x, left_y, left_w, Inches(0.55), accent)
    add_text(slide, left_x, left_y, left_w, Inches(0.55),
             "📅  План по дням", size=16, bold=True, color=COLOR_WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    inner_y = left_y + Inches(0.75)
    row_h = (left_h - Inches(0.85)) / max(len(days), 1)

    for i, d in enumerate(days):
        ry = inner_y + row_h * i
        add_rect(slide, left_x + Inches(0.2), ry + Inches(0.05),
                 Inches(0.08), row_h - Inches(0.15), accent)
        add_text(slide, left_x + Inches(0.4), ry + Inches(0.02),
                 Inches(1.6), Inches(0.35),
                 d["day"], size=12, bold=True, color=accent)
        add_text(slide, left_x + Inches(0.4), ry + Inches(0.32),
                 Inches(1.6), Inches(0.32),
                 d["date"], size=10, color=COLOR_GREY, italic=True)
        add_text(slide, left_x + Inches(2.05), ry + Inches(0.02),
                 left_w - Inches(2.25), row_h - Inches(0.1),
                 d["plan"], size=11, color=COLOR_DARK, anchor=MSO_ANCHOR.TOP)

    # ---------- Правая колонка: достопримечательности на всю высоту ---------- #
    right_x = Inches(7.95)
    right_y = Inches(2.0)
    right_w = Inches(4.8)
    right_h = Inches(5.1)

    add_round_rect(slide, right_x, right_y, right_w, right_h, COLOR_WHITE,
                   line=accent, radius=0.03)
    add_rect(slide, right_x, right_y, right_w, Inches(0.5), accent)
    add_text(slide, right_x, right_y, right_w, Inches(0.5),
             "🎟  Билеты и достопримечательности", size=13, bold=True,
             color=COLOR_WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    inner_ry = right_y + Inches(0.6)
    a_row_h = (right_h - Inches(0.7)) / max(len(attractions), 1)
    for i, a in enumerate(attractions):
        ry = inner_ry + a_row_h * i
        if i % 2 == 0:
            add_rect(slide, right_x + Inches(0.1), ry,
                     right_w - Inches(0.2), a_row_h - Inches(0.04),
                     light_accent)
        # Название
        add_text(slide, right_x + Inches(0.2), ry + Inches(0.04),
                 right_w - Inches(1.55), Inches(0.32),
                 a["name"], size=10, bold=True, color=COLOR_DARK,
                 anchor=MSO_ANCHOR.TOP)
        # Подробности (мелким курсивом снизу)
        add_text(slide, right_x + Inches(0.2), ry + Inches(0.36),
                 right_w - Inches(0.4), a_row_h - Inches(0.42),
                 a.get("note", ""), size=8, italic=True, color=COLOR_GREY,
                 anchor=MSO_ANCHOR.TOP)
        # Цена справа
        add_text(slide, right_x + right_w - Inches(1.45), ry + Inches(0.04),
                 Inches(1.30), Inches(0.32),
                 a["price"], size=11, bold=True, color=accent,
                 align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.TOP)

    add_footer(slide, page, total)


# ----------- Данные по городам ----------- #

ROME_DAYS = [
    {"day": "Пн, 8 июня",  "date": "День 1 · прибытие",
     "plan": "Прилёт в FCO 20:10 → Leonardo Express до Termini → отель → лёгкий ужин в Монти, прогулка к Колизею с подсветкой"},
    {"day": "Вт, 9 июня",  "date": "День 2 · Античный Рим",
     "plan": "Поздний завтрак · 11:00 — Колизей, Палатин, Римский форум (вход по таймслоту) · обед в Монти · 14:30–16:30 сиеста · вечер — Капитолий, виа деи Фори Империали"},
    {"day": "Ср, 10 июня", "date": "День 3 · Ватикан",
     "plan": "Завтрак не спеша · 11:30 — Музеи Ватикана и Сикстинская капелла (бронь онлайн) · 14:00 — собор Св. Петра · сиеста · ужин в Борго"},
    {"day": "Чт, 11 июня", "date": "День 4 · сердце города",
     "plan": "10:30 Пантеон → Пьяцца Навона → Кампо-деи-Фьори · обед · сиеста · 17:00 — фонтан Треви, Испанская лестница · аперитив на Виа Маргутта"},
    {"day": "Пт, 12 июня", "date": "День 5 · Боргезе и Трастевере",
     "plan": "11:00 Галерея Боргезе (бронь обязательна) · прогулка по парку Вилла Боргезе · сиеста · вечер в Трастевере (ужин с видом на Санта-Мария)"},
    {"day": "Сб, 13 июня", "date": "День 6 · переезд",
     "plan": "Поздний завтрак · 11:50 — поезд Frecciarossa Roma → Firenze (~1 ч 30 мин) · заселение · вечерняя прогулка по Олтрарно"},
]

ROME_ATTRACTIONS = [
    {"name": "Колизей + Форум + Палатин (24h combo)",
     "price": "€ 18", "note": "брать онлайн заранее, таймслот"},
    {"name": "Full Experience с ареной и подземельями",
     "price": "€ 24", "note": "по желанию, дополнительно"},
    {"name": "Музеи Ватикана + Сикстинская капелла",
     "price": "€ 25", "note": "цена с букинг-сбором, скользящий вход"},
    {"name": "Собор Св. Петра",
     "price": "бесплатно", "note": "купол ещё € 10 (пешком) / € 15 (лифт)"},
    {"name": "Пантеон",
     "price": "€ 5", "note": "вход с 2023 года платный"},
    {"name": "Галерея Боргезе",
     "price": "€ 15", "note": "только по предв. брони, 2 часа"},
    {"name": "Фонтан Треви, Навона, Испанская лестница",
     "price": "бесплатно", "note": "лучше вечером, без толпы"},
]

ROME_TIPS = [
    "Подъём 8:30–9:30, выход после 10:30 — без спешки",
    "Сиеста 14:00–16:30: отдых в отеле, кафе с кондиционером",
    "Активность смещаем на вечер — после 17:00 город оживает",
    "Ужин по-итальянски: после 20:30, бронь в Трастевере обязательна",
]

FLORENCE_DAYS = [
    {"day": "Сб, 13 июня", "date": "День 1 · приезд",
     "plan": "Прибытие из Рима ~13:30 · обед на Меркато Сант’Амброджо · сиеста · вечер: Понте-Веккьо, Пьяцца-делла-Синьория, ужин с видом"},
    {"day": "Вс, 14 июня", "date": "День 2 · Уффици",
     "plan": "11:00 — Галерея Уффици (бронь, 2,5–3 ч) · обед · сиеста · 17:30 — Палаццо Веккьо, башня Арнольфо · аперитив на крыше"},
    {"day": "Пн, 15 июня", "date": "День 3 · Дуомо",
     "plan": "10:30 Brunelleschi Pass: купол (бронь обязательна, выбираем поздний слот ~12:00), баптистерий, кампанила, музей Опера дель Дуомо · сиеста · вечер на Пьяццале Микеланджело — закат над городом"},
    {"day": "Вт, 16 июня", "date": "День 4 · Академия и Олтрарно",
     "plan": "11:00 Галерея Академии — Давид (бронь) · обед в Сан-Лоренцо · сиеста · 17:00 — Палаццо Питти и сады Боболи · ужин в Олтрарно"},
    {"day": "Ср, 17 июня", "date": "День 5 · переезд",
     "plan": "Завтрак · 11:25 — Frecciarossa Firenze → Venezia S. Lucia (~2 ч 10 мин) · заселение · ужин в Каннареджо"},
]

FLORENCE_ATTRACTIONS = [
    {"name": "Галерея Уффици",
     "price": "€ 25", "note": "пик-сезон, бронь обязательна"},
    {"name": "Brunelleschi Pass (Дуомо комплекс)",
     "price": "€ 30", "note": "купол, баптистерий, кампанила, музей"},
    {"name": "Галерея Академии (Давид)",
     "price": "€ 16", "note": "+ € 4 букинг-сбор"},
    {"name": "Палаццо Веккьо + башня Арнольфо",
     "price": "€ 21,50", "note": "comb. музей и башня"},
    {"name": "Сады Боболи + Палаццо Питти",
     "price": "€ 22", "note": "Uffizi+Pitti+Boboli pass — € 38"},
    {"name": "Пьяццале Микеланджело",
     "price": "бесплатно", "note": "лучшее место для заката"},
    {"name": "Понте-Веккьо",
     "price": "бесплатно", "note": "вечером без толпы туристов"},
]

FLORENCE_TIPS = [
    "Подъём 9:00, завтрак до 10:30 — гостиничный или в баре",
    "Сиеста 14:00–16:30: жара во Флоренции серьёзная",
    "Билеты в Уффици / Академию / на купол брать ОНЛАЙН за 1–2 мес",
    "Закат — обязательный ритуал на Пьяццале Микеланджело",
]

VENICE_DAYS = [
    {"day": "Ср, 17 июня", "date": "День 1 · прибытие",
     "plan": "Прибытие ~13:35 · вапоретто №1 до Сан-Марко (живописный маршрут по Гранд-каналу) · заселение · сиеста · вечер: пл. Сан-Марко, кафе Florian, ужин у канала"},
    {"day": "Чт, 18 июня", "date": "День 2 · сердце Венеции",
     "plan": "11:00 — собор Сан-Марко (skip-the-line) · 12:30 — Дворец дожей и Мост вздохов · 14:00 обед · сиеста · 17:00 — Кампанила Сан-Марко · 18:00 — гондола (30 мин) по тихим каналам · ужин в Дорсодуро"},
    {"day": "Пт, 19 июня", "date": "День 3 · Биеннале + переезд",
     "plan": "10:30 — Биеннале Arte 2026 в Arsenale (длинные галереи Кордерие) · 13:00 обед в кафе биеннале · 14:30 — Giardini, национальные павильоны (90+ стран) · 16:30 — vaporetto до Санта-Лючии · 17:25 — Frecciarossa Venezia → Roma Termini (~3 ч 45 мин) · ночёвка у FCO"},
    {"day": "Сб, 20 июня", "date": "День 4 · вылет",
     "plan": "Лёгкий завтрак · трансфер в FCO к 9:30 · регистрация · вылет в 11:55 → Санкт-Петербург 21:00"},
]

VENICE_ATTRACTIONS = [
    {"name": "Биеннале Arte 2026 (Giardini + Arsenale)",
     "price": "€ 30", "note": "61-я Международная выставка, единый билет на 2 локации"},
    {"name": "Собор Сан-Марко (skip-the-line)",
     "price": "€ 6", "note": "+ € 7 Pala d’Oro, + € 7 музей"},
    {"name": "Дворец дожей + Мост вздохов",
     "price": "€ 30", "note": "комбо с Museo Correr"},
    {"name": "Кампанила Сан-Марко (лифт)",
     "price": "€ 12", "note": "виды на лагуну"},
    {"name": "Гондола 30 мин (днём)",
     "price": "€ 90 / лодка", "note": "до 5 чел., после 19:00 — € 110"},
    {"name": "Вапоретто 72 часа (ACTV)",
     "price": "€ 45 / чел", "note": "выгоднее единичных билетов € 9,50"},
    {"name": "Мурано + Бурано (по желанию)",
     "price": "вход 0", "note": "вход бесплатный, только проезд вапоретто"},
    {"name": "Базилика Санта-Мария делла Салюте",
     "price": "€ 8", "note": "ризница; сама церковь — бесплатно"},
]

VENICE_TIPS = [
    "Подъём 9:00–9:30 — на Сан-Марко идём после открытия толп",
    "Сиеста 14:00–16:30: венецианская жара + влажность",
    "Биеннале вт-вс, 11:00–19:00 (по пт до 20:00) — 19.06 пятница",
    "20 июня — единственный ранний подъём (~7:30) ради вылета",
]

# ============================================================ #
#         СЛАЙД ДОСТОПРИМЕЧАТЕЛЬНОСТИ (детальный)                #
# ============================================================ #
def make_attraction_slide(slide, *, page, total, city, city_color,
                          accent, light_accent,
                          icon, title, subtitle, facts, history, fact):
    """
    icon       : короткий значок-символ (✦, ⌘ и т.п.)
    title      : крупное название достопримечательности
    subtitle   : итальянское имя + период / эпоха
    facts      : список (label, value) — карточка фактов слева
    history    : список абзацев (str) — справа
    fact       : строка-факт внизу
    """
    slide_background(slide, COLOR_CREAM)

    # Header band
    add_rect(slide, 0, 0, SLIDE_W, Inches(1.5), accent)
    add_rect(slide, 0, Inches(1.5), SLIDE_W, Inches(0.05), COLOR_GOLD)

    # Малая надстрочная плашка с городом
    add_text(slide, Inches(0.6), Inches(0.12), Inches(11), Inches(0.32),
             city, size=11, bold=True, color=COLOR_LIGHT_GOLD)

    # Название
    add_text(slide, Inches(0.6), Inches(0.42), Inches(12.2), Inches(0.78),
             f"{icon}  {title}", size=28, bold=True, color=COLOR_WHITE,
             font="Georgia", anchor=MSO_ANCHOR.MIDDLE)
    # Подзаголовок-курсив
    add_text(slide, Inches(0.6), Inches(1.15), Inches(12.2), Inches(0.32),
             subtitle, size=12, italic=True, color=COLOR_LIGHT_GOLD)

    # ---------- Левая карточка: ключевые факты ---------- #
    lx = Inches(0.6)
    ly = Inches(1.75)
    lw = Inches(4.4)
    lh = Inches(4.65)

    add_round_rect(slide, lx, ly, lw, lh, COLOR_WHITE,
                   line=accent, radius=0.03)
    add_rect(slide, lx, ly, lw, Inches(0.5), accent)
    add_text(slide, lx, ly, lw, Inches(0.5),
             "📋  Кратко", size=14, bold=True, color=COLOR_WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # Факты
    fact_y = ly + Inches(0.7)
    fact_h = (lh - Inches(0.85)) / max(len(facts), 1)
    for i, (label, value) in enumerate(facts):
        ry = fact_y + fact_h * i
        # Боковая полоса
        add_rect(slide, lx + Inches(0.25), ry + Inches(0.05),
                 Inches(0.06), fact_h - Inches(0.15), COLOR_GOLD)
        add_text(slide, lx + Inches(0.45), ry + Inches(0.02),
                 lw - Inches(0.6), Inches(0.32),
                 label, size=10, bold=True, color=accent)
        add_text(slide, lx + Inches(0.45), ry + Inches(0.34),
                 lw - Inches(0.6), fact_h - Inches(0.4),
                 value, size=12, color=COLOR_DARK)

    # ---------- Правая карточка: история ---------- #
    rx = Inches(5.15)
    ry_top = Inches(1.75)
    rw = Inches(7.6)
    rh = Inches(4.65)

    add_round_rect(slide, rx, ry_top, rw, rh, COLOR_WHITE,
                   line=accent, radius=0.03)
    add_rect(slide, rx, ry_top, rw, Inches(0.5), accent)
    add_text(slide, rx, ry_top, rw, Inches(0.5),
             "📖  Историческая справка", size=14, bold=True, color=COLOR_WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # Текст истории
    paras = []
    for i, p in enumerate(history):
        paras.append({
            "text": p, "size": 12, "color": COLOR_DARK,
            "space_after": 8 if i < len(history) - 1 else 0,
            "align": PP_ALIGN.JUSTIFY,
        })
    add_multi_text(slide, rx + Inches(0.35), ry_top + Inches(0.65),
                   rw - Inches(0.7), rh - Inches(0.8),
                   paras, line_spacing=1.18)

    # ---------- Нижняя плашка: интересный факт ---------- #
    fy = Inches(6.55)
    fh = Inches(0.6)
    add_round_rect(slide, Inches(0.6), fy, SLIDE_W - Inches(1.2), fh,
                   COLOR_LIGHT_GOLD, line=COLOR_GOLD, radius=0.3)
    add_text(slide, Inches(0.85), fy, Inches(1.7), fh,
             "💡  Любопытно",
             size=12, bold=True, color=COLOR_GOLD, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(2.55), fy, SLIDE_W - Inches(2.85), fh,
             fact, size=11, italic=True, color=COLOR_DARK,
             anchor=MSO_ANCHOR.MIDDLE)

    add_footer(slide, page, total)


# ============================================================ #
#                           СЛАЙД: БЮДЖЕТ                        #
# ============================================================ #
def make_budget_slide(slide, page, total):
    slide_background(slide, COLOR_CREAM)
    add_header_band(slide, "Сводная стоимость билетов",
                    "Ориентировочно на двоих, в евро · бронировать заранее")

    # Левая колонка: Музеи и достопримечательности
    add_round_rect(slide, Inches(0.6), Inches(1.4), Inches(7.5), Inches(5.4),
                   COLOR_WHITE, line=COLOR_GREEN, radius=0.02)
    add_rect(slide, Inches(0.6), Inches(1.4), Inches(7.5), Inches(0.55), COLOR_GREEN)
    add_text(slide, Inches(0.6), Inches(1.4), Inches(7.5), Inches(0.55),
             "🎟  Достопримечательности (на двоих)",
             size=15, bold=True, color=COLOR_WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    rows = [
        ("РИМ",                                          ""),
        ("Колизей + Форум + Палатин (combo)",           "€ 36"),
        ("Музеи Ватикана + Сикстинская капелла",         "€ 50"),
        ("Пантеон",                                      "€ 10"),
        ("Галерея Боргезе",                              "€ 30"),
        ("Купол Св. Петра (по желанию)",                 "€ 20"),
        ("ФЛОРЕНЦИЯ",                                    ""),
        ("Галерея Уффици",                               "€ 50"),
        ("Brunelleschi Pass (Дуомо)",                    "€ 60"),
        ("Галерея Академии — Давид",                     "€ 32"),
        ("Палаццо Питти + Боболи (комбо)",               "€ 44"),
        ("ВЕНЕЦИЯ",                                      ""),
        ("Биеннале Arte 2026 (Giardini + Arsenale)",     "€ 60"),
        ("Дворец дожей + Сан-Марко skip",                "€ 72"),
        ("Кампанила Сан-Марко",                          "€ 24"),
        ("Гондола 30 мин",                               "€ 90"),
        ("Вапоретто 72h × 2",                            "€ 90"),
    ]
    y = Inches(2.0)
    row_h = Inches(0.28)
    for name, price in rows:
        is_header = price == ""
        if is_header:
            add_rect(slide, Inches(0.7), y, Inches(7.3), row_h, COLOR_LIGHT_GREEN)
            add_text(slide, Inches(0.85), y, Inches(7.0), row_h,
                     name, size=11, bold=True, color=COLOR_GREEN,
                     anchor=MSO_ANCHOR.MIDDLE)
        else:
            add_text(slide, Inches(0.85), y, Inches(5.8), row_h,
                     name, size=10, color=COLOR_DARK, anchor=MSO_ANCHOR.MIDDLE)
            add_text(slide, Inches(6.7), y, Inches(1.3), row_h,
                     price, size=10, bold=True, color=COLOR_DARK,
                     align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
        y += row_h

    # Правая колонка: транспорт и итог
    rx = Inches(8.3)
    rw = Inches(4.45)

    # Поезда
    add_round_rect(slide, rx, Inches(1.4), rw, Inches(2.7),
                   COLOR_WHITE, line=COLOR_RED, radius=0.04)
    add_rect(slide, rx, Inches(1.4), rw, Inches(0.5), COLOR_RED)
    add_text(slide, rx, Inches(1.4), rw, Inches(0.5),
             "🚄  Поезда Frecciarossa", size=14, bold=True, color=COLOR_WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    train_rows = [
        ("Roma → Firenze  (13.06, 11:50)",       "от € 60 / 2"),
        ("Firenze → Venezia  (17.06, 11:25)",    "от € 70 / 2"),
        ("Venezia → Roma  (19.06, 17:25)",       "от € 100 / 2"),
        ("Leonardo Express FCO ⇄ Termini ×2",    "€ 56 / 2"),
    ]
    ty = Inches(2.0)
    for name, price in train_rows:
        add_text(slide, rx + Inches(0.2), ty, rw - Inches(1.6), Inches(0.35),
                 name, size=10, color=COLOR_DARK, anchor=MSO_ANCHOR.MIDDLE)
        add_text(slide, rx + rw - Inches(1.5), ty, Inches(1.3), Inches(0.35),
                 price, size=10, bold=True, color=COLOR_RED,
                 align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
        ty += Inches(0.4)
    add_line(slide, rx + Inches(0.2), ty + Inches(0.05),
             rx + rw - Inches(0.2), ty + Inches(0.05),
             color=COLOR_GREY, width=0.75, dash=True)
    add_text(slide, rx + Inches(0.2), ty + Inches(0.1),
             rw - Inches(0.4), Inches(0.4),
             "Итого по транспорту:  ~ € 286 на двоих",
             size=11, bold=True, italic=True, color=COLOR_DARK,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    # 60 + 70 + 100 + 56 = € 286

    # Итог
    add_round_rect(slide, rx, Inches(4.25), rw, Inches(2.55),
                   COLOR_GREEN, line=None, radius=0.04)
    add_text(slide, rx, Inches(4.4), rw, Inches(0.5),
             "ОРИЕНТИР ПО БИЛЕТАМ",
             size=12, bold=True, color=COLOR_LIGHT_GOLD,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, rx, Inches(4.85), rw, Inches(1.0),
             "≈ € 960",
             size=54, bold=True, color=COLOR_WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
             font="Georgia")
    add_text(slide, rx, Inches(5.85), rw, Inches(0.4),
             "достопр. + транспорт на двоих",
             size=11, color=COLOR_LIGHT_GOLD, italic=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, rx + Inches(0.2), Inches(6.25), rw - Inches(0.4), Inches(0.5),
             "* без авиабилетов, отелей и питания",
             size=9, color=COLOR_LIGHT_GOLD, italic=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    add_footer(slide, page, total)


# ============================================================ #
#         ДАННЫЕ ДОСТОПРИМЕЧАТЕЛЬНОСТЕЙ (исторические справки)   #
# ============================================================ #

ROME_DETAILS = [
    {
        "icon": "🏟",
        "title": "Колизей",
        "subtitle": "Colosseo (Amphitheatrum Flavium) · 70–80 гг. н. э.",
        "facts": [
            ("Эпоха", "Древний Рим, династия Флавиев"),
            ("Заказчик", "Веспасиан · открыт Титом в 80 г."),
            ("Размеры", "188 × 156 м, высота 48 м"),
            ("Вместимость", "~50 000 зрителей, 80 входов"),
            ("Материал", "травертин, туф, кирпич, бетон"),
        ],
        "history": [
            "Самый большой амфитеатр античного мира был построен на месте осушённого пруда «Золотого дома» Нерона. Веспасиан, основатель династии Флавиев, начал стройку около 72 года, сын Тит открыл её в 80-м играми, длившимися 100 дней.",
            "Здесь устраивали гладиаторские бои (munera), травли диких зверей (venationes) и даже — в первые годы — навмахии: затоплённую арену превращали в озеро для морских сражений. Под полом находились двухуровневые подземелья (hypogeum) с клетками, лифтами и системой блоков.",
            "После падения Рима Колизей служил каменоломней, крепостью семейства Франджипани и христианской святыней — папа Бенедикт XIV в 1749 году освятил его в память о мучениках. Землетрясения XIV века обрушили южную часть; нынешний разрушенный фасад — результат именно этих сейсмических событий.",
        ],
        "fact": "Название «Колизей» происходит не от размеров здания, а от стоявшей рядом 35-метровой бронзовой статуи Нерона — «колосса», переплавленной в Средние века.",
    },
    {
        "icon": "🏛",
        "title": "Римский форум и Палатинский холм",
        "subtitle": "Forum Romanum, Palatinus · VIII в. до н. э. — V в. н. э.",
        "facts": [
            ("Эпоха", "Царский, республиканский и имперский Рим"),
            ("Функция", "политический, религиозный и торговый центр"),
            ("На Палатине", "согласно легенде, Ромул основал Рим в 753 г. до н. э."),
            ("Знаковое", "арка Тита, храм Сатурна, Дом Весталок, дворцы Августа и Домициана"),
            ("Площадь", "~10 га"),
        ],
        "history": [
            "Форум вырос в долине между Палатинским и Капитолийским холмами и более тысячи лет был сердцем Рима: здесь собирался Сенат в Курии Юлия, ораторы выступали с Ростры, проходили триумфы и похороны императоров.",
            "Палатинский холм — самая аристократическая часть города. От слова «Palatium» произошло само слово «дворец» во многих языках: с Августа здесь жили все императоры. Дом Августа и Дом Ливии хранят великолепные фрески I века до н. э.",
            "После падения империи Форум превратился в коровий выгон Campo Vaccino — в Средние века уровень земли поднялся на 6–8 метров, и колонны заносило мусором. Систематические раскопки начались только в XIX веке и продолжаются по сей день.",
        ],
        "fact": "Арка Тита (81 г.) изображает захват иерусалимского Храма в 70 году — это древнейшее визуальное свидетельство меноры, и до создания Государства Израиль евреи Рима принципиально не проходили под этой аркой.",
    },
    {
        "icon": "⛪",
        "title": "Музеи Ватикана и Сикстинская капелла",
        "subtitle": "Musei Vaticani, Cappella Sistina · 1473–1481, потолок 1508–1512",
        "facts": [
            ("Основание", "Папа Сикст IV (капелла), Юлий II (музеи, 1506)"),
            ("Архитекторы", "Джованнино де Дольчи; росписи — Микеланджело"),
            ("Сикстинская", "потолок 1508–1512, «Страшный суд» 1536–1541"),
            ("Размеры музеев", "~7 км маршрута, ~1500 залов"),
            ("Посещаемость", "~7 млн человек в год — крупнейший музей мира"),
        ],
        "history": [
            "Капелла построена при папе Сиксте IV как домовой храм пап и место конклавов. Микеланджело, считавший себя в первую очередь скульптором, четыре года расписывал потолок лёжа на лесах: 33 × 13 м, более 300 фигур, девять центральных сцен из Книги Бытия — от «Сотворения Адама» до «Опьянения Ноя».",
            "Через четверть века он вернулся, чтобы написать «Страшный суд» на алтарной стене — и это уже был совсем иной Микеланджело: 391 обнажённая фигура, мрачный синий фон ляпис-лазури, апостол Варфоломей со снятой кожей-автопортретом.",
            "Музеи Ватикана объединяют коллекции 26 веков: египетские саркофаги, греческие оригиналы (Лаокоон, Аполлон Бельведерский), Станцы Рафаэля с «Афинской школой», Пинакотека с Караваджо и Леонардо. На конклаве в капелле кардиналы выбирают нового папу — белый дым над Сикстиной означает «Habemus Papam».",
        ],
        "fact": "Реставрация фресок (1980–1994) сняла трёхвековой слой копоти от свечей — открылись насыщенные цвета, которые многие критики поначалу сочли «слишком яркими и неправильными».",
    },
    {
        "icon": "✝",
        "title": "Собор Святого Петра",
        "subtitle": "Basilica di San Pietro · 1506–1626",
        "facts": [
            ("Стиль", "Высокое Возрождение и барокко"),
            ("Архитекторы", "Браманте, Рафаэль, Микеланджело, Бернини, Мадерно"),
            ("Купол", "Микеланджело, ⌀ 42 м, высота 136,6 м"),
            ("Площадь", "колоннада Бернини, 1656–1667, 284 колонны"),
            ("Длина нефа", "211,5 м — крупнейший христианский храм мира"),
        ],
        "history": [
            "На этом месте, по преданию, в 64 году н. э. был распят апостол Пётр — над его могилой император Константин в 320-х построил первую базилику. К XV веку она обветшала, и папа Юлий II решил снести её и возвести новую, заложив краеугольный камень в 1506 году.",
            "Стройка длилась 120 лет и сменила полдюжины архитекторов. Браманте задумал крест с равными плечами, Микеланджело уже в 71 год спроектировал гигантский купол, вдохновлённый Дуомо Брунеллески. Карло Мадерно удлинил неф, превратив план в латинский крест, а Бернини обрамил площадь знаменитой эллиптической колоннадой — «руками Церкви, обнимающими мир».",
            "Внутри — «Пьета» 25-летнего Микеланджело (единственная подписанная им работа), бронзовый балдахин Бернини над могилой Петра (29 м, отлит из бронзы Пантеона), «Кафедра святого Петра» в апсиде. Спуск в Ватиканские гроты ведёт к археологически подтверждённой могиле апостола.",
        ],
        "fact": "Купол собора, на самом деле, не самый высокий в мире, но самый высокий из исторических: по итальянскому правилу с 1626 года ни одно здание Рима не должно быть выше креста Святого Петра — 136,57 м.",
    },
    {
        "icon": "○",
        "title": "Пантеон",
        "subtitle": "Pantheon · 118–128 гг. н. э., император Адриан",
        "facts": [
            ("Эпоха", "Древний Рим, II век"),
            ("Архитектор", "приписывается Аполлодору Дамасскому"),
            ("Купол", "⌀ 43,3 м — рекорд бетона до XIX века"),
            ("Окулюс", "круглое отверстие 8,9 м — единственный источник света"),
            ("С 609 г.", "церковь Санта-Мария-ад-Мартирес"),
        ],
        "history": [
            "Сначала на этом месте был храм, построенный другом Августа — Марком Випсанием Агриппой (отсюда монументальная надпись на фронтоне «M·AGRIPPA·L·F·COS·TERTIUM·FECIT»). После двух пожаров Адриан полностью перестроил здание около 125 года, сохранив имя Агриппы из скромности.",
            "Пантеон — посвящение «всем богам». Его купол отлит из бетона: чем выше, тем легче становится заполнитель (внизу травертин, выше — пемза). Толщина купола уменьшается с 6,4 м у основания до 1,2 м у окулюса. Внутренняя высота равна диаметру — здание вписано в идеальную сферу.",
            "В 609 году Папа Бонифаций IV получил здание от византийского императора и переосвятил как церковь — именно поэтому Пантеон уцелел, тогда как другие античные храмы Рима были разобраны на стройматериалы. В нём похоронен Рафаэль, а также короли Виктор Эммануил II и Умберто I.",
        ],
        "fact": "Когда дождь идёт через окулюс, вода уходит через 22 крошечных отверстия в наклонном мраморном полу — древнеримский водоотвод работает безотказно почти 19 веков.",
    },
    {
        "icon": "🎨",
        "title": "Галерея Боргезе",
        "subtitle": "Galleria Borghese · 1612–1616",
        "facts": [
            ("Заказчик", "кардинал Шипионе Боргезе, племянник папы Павла V"),
            ("Архитектор", "Фламинио Понцио, завершил Джованни Вазанцио"),
            ("Жемчужины", "Бернини: «Аполлон и Дафна», «Похищение Прозерпины», «Давид»"),
            ("Караваджо", "6 шедевров, включая «Юношу с корзиной фруктов»"),
            ("Регламент", "только по бронированию · 2 часа на посещение"),
        ],
        "history": [
            "Шипионе Боргезе — пожалуй, самый страстный коллекционер раннего барокко: племянник папы использовал родственные связи, чтобы конфисковать картины Кавальере д’Арпино, отнять имение Доменикино, выкупить Караваджо у наследников. Он же стал главным покровителем юного Бернини.",
            "Вилла строилась как загородный «казино» — место досуга, искусства и приёмов. Сегодня в 20 залах развёрнут хронологически выстроенный путь от античных мраморов через шедевры Бернини и Караваджо к Тициану («Любовь земная и небесная»), Рафаэлю, Антонелло да Мессине.",
            "«Аполлон и Дафна» Бернини (1622–1625) — одна из самых поэтичных скульптур мира: момент превращения нимфы в лавр, тончайшие листья из мрамора. Бернини было 24 года. «Похищение Прозерпины» он создал ещё раньше, в 23 — пальцы Плутона буквально вдавлены в мраморное бедро Прозерпины.",
        ],
        "fact": "Из-за хрупкости фресок и небольших залов вход строго лимитирован: 360 человек в каждый двухчасовой слот. Билеты раскупают за месяц — поэтому бронировать обязательно заранее.",
    },
    {
        "icon": "⛲",
        "title": "Фонтан Треви",
        "subtitle": "Fontana di Trevi · 1732–1762",
        "facts": [
            ("Архитектор", "Никола Сальви; завершил Джузеппе Паннини"),
            ("Заказчик", "папа Климент XII (конкурс 1730 г.)"),
            ("Размеры", "26,3 м высота, 49,15 м ширина"),
            ("Источник", "акведук Aqua Virgo, 19 г. до н. э., Агриппа"),
            ("Стиль", "позднее римское барокко, рококо"),
        ],
        "history": [
            "Фонтан — финальная точка одного из древнейших римских акведуков, Aqua Virgo, построенного Агриппой в 19 году до н. э. для его терм. По легенде, акведук получил имя в честь девушки, указавшей римским солдатам источник чистой воды в 13 км от города.",
            "В 1730 году папа Климент XII объявил конкурс на оформление выхода акведука. Победил Никола Сальви: он встроил фонтан прямо в фасад палаццо Поли. Центральная фигура — Океан на колеснице-раковине, которую тащат два морских коня (один спокойный, другой буйный — символ настроений моря) с тритонами.",
            "Со времён фильма «Сладкая жизнь» Феллини (1960) с Анитой Экберг, купающейся в фонтане, Треви стал главной кинозвездой Рима. Традиция бросать монетку через левое плечо правой рукой обещает возвращение в Рим — ежегодно из фонтана собирают около 1,5 млн евро, которые передают на помощь нуждающимся.",
        ],
        "fact": "Над водой видны рельефы с легендой о девушке-«Девственнице» (Virgo) и сценой одобрения Агриппой проекта акведука — таким образом классическое барокко рассказывает историю того, что течёт у вас под ногами.",
    },
    {
        "icon": "✦",
        "title": "Пьяцца Навона и Испанская лестница",
        "subtitle": "Piazza Navona (I в.) · Scalinata di Trinità dei Monti (1723–1725)",
        "facts": [
            ("Навона", "форма стадиона Домициана 86 г. н. э., 240 × 65 м"),
            ("Фонтан рек", "Бернини, 1651 — Дунай, Нил, Ганг, Ла-Плата"),
            ("Сант-Аньезе", "церковь Борромини, 1652–1672"),
            ("Лестница", "де Санктис · 135 ступеней"),
            ("Сверху", "церковь Тринита-деи-Монти, 1502"),
        ],
        "history": [
            "Пьяцца Навона повторяет очертания античного стадиона Домициана, где проходили греческие атлетические состязания (отсюда и имя — от греческого «agon»). До XIX века площадь летом затапливали для водных праздников. Сегодня её формируют три фонтана и церковь Сант-Аньезе-ин-Агоне Борромини — главного архитектурного соперника Бернини.",
            "«Фонтан четырёх рек» Бернини в центре площади (1651) — аллегория четырёх частей света: Нил с закрытой головой (его исток тогда не был известен), Ганг с веслом, Дунай с папским гербом и Ла-Плата с горкой монет. Сверху — настоящий древнеегипетский обелиск Домициана.",
            "Испанская лестница (1723–1725) соединяет площадь Испании внизу и церковь Тринита-деи-Монти наверху. Её спроектировал Франческо де Санктис как 135 ступеней с тремя «волнообразными» площадками. У подножия — фонтан Баркачча Пьетро Бернини (отца), стилизованный под полузатонувшую лодку, что напоминает о наводнении Тибра 1598 года.",
        ],
        "fact": "Знаменитый чайный салон Babington’s у подножия лестницы открыли в 1893 году две англичанки — там до сих пор подают тот же английский чай, что заказывали Байрон, Китс и Гёте, жившие тут же поблизости.",
    },
]

FLORENCE_DETAILS = [
    {
        "icon": "✦",
        "title": "Дуомо — Санта-Мария-дель-Фьоре",
        "subtitle": "Cattedrale di Santa Maria del Fiore · 1296–1436",
        "facts": [
            ("Архитекторы", "Арнольфо ди Камбио, купол — Филиппо Брунеллески"),
            ("Купол", "1420–1436 · ⌀ 45,5 м · высота с фонарём 116 м"),
            ("Длина", "153 м — 4-й по величине собор Европы"),
            ("Облицовка", "белый мрамор Каррары, зелёный Прато, розовый Маремма"),
            ("Часы", "механические астрономические Уччелло, 1443"),
        ],
        "history": [
            "Закладка прошла в 1296-м, но к 1418 году собор стоял без купола: никто не знал, как перекрыть пролёт 45 метров без огромных деревянных лесов. Конкурс выиграл ювелир Филиппо Брунеллески, ездивший в Рим изучать Пантеон. Он построил уникальный двухоболочный купол в технике «сельди» — кирпичи укладывались по спирали и держались сами без опор.",
            "Брунеллески изобрёл специальные краны и платформы, организовал кухню прямо на стройке (чтобы рабочие не спускались на обед) и хранил расчёты в тайне. Купол стал символом начала эпохи Возрождения и до сих пор остаётся крупнейшим кирпичным куполом мира.",
            "Внутри — фреска «Страшный суд» Вазари и Цуккари (3600 м²), готическое распятие Лоренцо Монако, бюст Брунеллески у входа. С 463 ступеней между двумя оболочками купола открывается лучший вид на Флоренцию.",
        ],
        "fact": "Когда Микеланджело проектировал купол собора Святого Петра, он сказал: «Сделаю больше, но не красивее, чем у Брунеллески». В Риме его купол шире на 1,5 м, но флорентийский — выше по мастерству.",
    },
    {
        "icon": "⚜",
        "title": "Баптистерий Сан-Джованни и кампанила Джотто",
        "subtitle": "Battistero · XI–XII вв. · Campanile di Giotto · 1334–1359",
        "facts": [
            ("Баптистерий", "освящён в 1059, романский стиль, 8-угольник"),
            ("Райские двери", "Лоренцо Гиберти, 1425–1452, бронза с позолотой"),
            ("Мозаики купола", "XIII в., 1000 м² — «Страшный суд»"),
            ("Кампанила", "Джотто, продолжили Андреа Пизано и Таленти"),
            ("Высота", "84,7 м · 414 ступеней"),
        ],
        "history": [
            "Баптистерий — древнейшее здание Флоренции, средневековые горожане считали его перестроенным римским храмом Марса. Сюда крестили всех младенцев города (включая Данте и Макиавелли). У него три бронзовых дверей: южная Андреа Пизано (1336), северная и восточная — Гиберти.",
            "Восточные двери, обращённые к собору, — 10 рельефов на сюжеты Ветхого Завета. Гиберти работал над ними 27 лет. Микеланджело, по преданию, увидев их, воскликнул: «Эти двери достойны быть райскими» — и название прижилось.",
            "Кампанилу спроектировал в 1334 году Джотто, но успел построить только нижний ярус. После его смерти продолжили Андреа Пизано (рельефы на тему «истории человечества») и Франческо Таленти. Узкие готические окна, цветной мрамор и обзорная площадка наверху делают её одной из самых элегантных колоколен Италии.",
        ],
        "fact": "Подлинники «Райских врат» хранятся в Музее Опера-дель-Дуомо — на здании баптистерия установлена точная копия. Реставрация подлинников заняла 27 лет — столько же, сколько Гиберти их создавал.",
    },
    {
        "icon": "🖼",
        "title": "Галерея Уффици",
        "subtitle": "Galleria degli Uffizi · 1560–1581",
        "facts": [
            ("Заказчик", "Козимо I Медичи, под канцелярии («uffizi»)"),
            ("Архитектор", "Джорджо Вазари; завершил Бернардо Буонталенти"),
            ("Открыта как музей", "1769 — одно из старейших публичных собраний мира"),
            ("Шедевры", "Боттичелли, Леонардо, Микеланджело, Рафаэль, Караваджо, Тициан"),
            ("Залов", "101 · около 2 500 произведений"),
        ],
        "history": [
            "В 1560-х герцог Козимо I Медичи поручил Вазари построить здание для 13 магистратур Флоренции — отсюда и название «офисы». Длинное П-образное здание соединило Палаццо Веккьо с Арно. Уже сын Козимо, Франческо I, превратил верхний этаж в Tribuna — первый кабинет редкостей и шедевров.",
            "В 1737 году Анна Мария Луиза, последняя из Медичи, заключила «Семейный пакт»: всё художественное наследие династии остаётся во Флоренции навечно и не может быть вывезено. Благодаря этому документу сегодня мы видим коллекцию во всей полноте.",
            "Главные сокровища — «Рождение Венеры» и «Весна» Боттичелли, «Благовещение» и «Поклонение волхвов» Леонардо, «Мадонна Дони» Микеланджело (его единственная станковая работа), «Венера Урбинская» Тициана, «Юный Вакх» и «Медуза» Караваджо.",
        ],
        "fact": "По коридорам Уффици можно пройти через Понте-Веккьо до самого Палаццо Питти — это «Коридор Вазари», секретный проход длиной около километра, по которому Медичи передвигались, не выходя на улицу.",
    },
    {
        "icon": "𓀀",
        "title": "Галерея Академии — Давид",
        "subtitle": "Galleria dell’Accademia · «Давид» Микеланджело, 1501–1504",
        "facts": [
            ("Размер «Давида»", "5,17 м (с пьедесталом 5,49)"),
            ("Материал", "единый блок каррарского мрамора"),
            ("Возраст автора", "26–29 лет"),
            ("Изначально", "стоял у Палаццо Веккьо до 1873"),
            ("Также в музее", "«Узники» (Prigioni) и «Святой Матфей» Микеланджело"),
        ],
        "history": [
            "Огромный блок мрамора простоял заброшенным 25 лет: за него брались Агостино ди Дуччо и Антонио Россселино, но оставляли — слишком вытянутый, с трещинами. В 1501 году Микеланджело принял вызов и за два с половиной года высек из него библейского Давида, готовящегося к битве с Голиафом.",
            "Это первая монументальная обнажённая статуя со времён античности. Микеланджело изобразил не победителя с головой Голиафа, как это делали Донателло и Верроккьо, а юношу в момент решимости — с непропорционально большими руками и головой, рассчитанными на взгляд снизу.",
            "До 1873 года скульптура стояла под открытым небом на Пьяцце-делла-Синьория. Чтобы спасти её от непогоды, Давида перенесли в Академию, под специально спроектированный купол с верхним светом. Сегодня к нему ведёт галерея с «Узниками» — будто скульптуры пытаются выйти из мрамора.",
        ],
        "fact": "При перевозке в 1873 году статую везли 4 дня по специально проложенным рельсам через 800 метров улиц Флоренции — одна из самых дорогих логистических операций XIX века.",
    },
    {
        "icon": "🏰",
        "title": "Палаццо Веккьо",
        "subtitle": "Palazzo Vecchio · 1299–1314",
        "facts": [
            ("Архитектор", "Арнольфо ди Камбио"),
            ("Башня", "Torre di Arnolfo, 94 м"),
            ("Зал Пятисот", "53 × 22 м, фрески Вазари"),
            ("Резиденции", "Синьория, Медичи (с 1540), сейчас — мэрия"),
            ("На площади", "копия «Давида», «Похищение сабинянок» Джамболоньи"),
        ],
        "history": [
            "Палаццо Веккьо построен на руинах амфитеатра — отсюда его слегка асимметричный план. С первого дня это была резиденция Синьории — высшего органа Флорентийской республики. Зубчатая башня, поставленная не по центру, символизировала независимость от соседнего собора.",
            "В 1540 году Козимо I Медичи перенёс сюда свой двор и поручил Вазари перестроить интерьеры. Так появился Зал Пятисот, расписанный сценами побед Флоренции, и роскошные апартаменты Элеоноры Толедской. Здесь же — «Гений Победы» Микеланджело и «Юдифь и Олоферн» Донателло.",
            "В Зале Пятисот по легенде существует фреска «Битва при Ангиари» Леонардо да Винчи, скрытая под фреской Вазари — поиски «утерянного Леонардо» с помощью эндоскопов и нейтронных пушек ведутся до сих пор. Башня доступна для подъёма (233 ступени) — оттуда открывается обзор всей Флоренции.",
        ],
        "fact": "Часы на башне идут с 1353 года (механизм с обновлениями) — это одни из старейших публичных часов Италии. И ходят весьма точно.",
    },
    {
        "icon": "🌿",
        "title": "Палаццо Питти и сады Боболи",
        "subtitle": "Palazzo Pitti · 1458 · Giardini di Boboli · с 1549",
        "facts": [
            ("Заказчик дворца", "Лука Питти, банкир-соперник Медичи"),
            ("С 1549", "куплен Элеонорой Толедской, резиденция Медичи"),
            ("Длина фасада", "205 м, сплошной рустик"),
            ("Сады", "Триболо, Аммаанати, Буонталенти — 45 000 м²"),
            ("Сегодня", "5 музеев — Палатинская галерея, апартаменты, костюмы, фарфор, серебро"),
        ],
        "history": [
            "Лука Питти заказал дворец, чтобы превзойти Медичи — фасад нарочито грубый, с гигантскими блоками. Но банк Питти разорился, и в 1549 году вдова Козимо I Элеонора Толедская купила дом за 9 000 флоринов. С тех пор и до объединения Италии (1865) Палаццо Питти было главной резиденцией флорентийских правителей: Медичи, Лотарингских, Савойских.",
            "Сады Боболи — образцовый итальянский сад: чёткая ось «амфитеатр – обелиск – нептунов фонтан – статуя Изобилия», тенистые аллеи, гроты Буонталенти с раковинами и сталактитами, кипарисовая аллея Vottolone. Внутри грота когда-то стояли «Узники» Микеланджело — теперь там копии.",
            "Палатинская галерея сохраняет уникальную «княжескую» развеску XVII века: картины висят рядами от пола до потолка, по принципу красоты, а не школы. Здесь больше всего работ Рафаэля в одной экспозиции в мире — 11 шедевров, включая «Мадонну в кресле» и «Беременную».",
        ],
        "fact": "Из садов Боболи Медичи попадали во дворец и далее по Коридору Вазари через Понте-Веккьо в Уффици и Палаццо Веккьо — целая «секретная» система сообщения над городом.",
    },
    {
        "icon": "🌉",
        "title": "Понте-Веккьо",
        "subtitle": "Ponte Vecchio · 1345",
        "facts": [
            ("Архитектор", "Таддео Гадди (приписывается)"),
            ("Длина / пролёты", "84 м, три арки"),
            ("Лавки", "с 1593 — только золотых дел мастера"),
            ("Коридор Вазари", "1565, 760 м, надстройка над мостом"),
            ("Уцелел", "единственный мост Флоренции, сохранённый в 1944"),
        ],
        "history": [
            "Мост на этом месте был ещё в римские времена — здесь Cassia пересекала Арно. Нынешний построен в 1345 году после катастрофического наводнения. Лавки на нём изначально занимали мясники и кожевники: с моста удобно было сбрасывать отходы в реку.",
            "В 1565 году по случаю свадьбы Франческо I Медичи и Иоанны Австрийской Вазари за пять месяцев надстроил над мостом Коридор — закрытый проход от Палаццо Веккьо через Уффици и Понте-Веккьо до Палаццо Питти. Чтобы герцог не страдал от запаха мясных лавок, Фердинандо I в 1593 году указом изгнал мясников и заменил их на ювелиров.",
            "В августе 1944-го отступающие немцы взорвали все мосты Флоренции, кроме Понте-Веккьо: по легенде, приказ исходил лично от Гитлера, считавшего его слишком красивым. Чтобы заблокировать переправу, немцы разрушили средневековые улицы у обоих концов моста.",
        ],
        "fact": "Бюст Бенвенуто Челлини в центре моста (1900) — дань главному ювелиру Флоренции; туристы вешают тут «замочки любви», от которых каждые несколько лет приходится спасать перила.",
    },
    {
        "icon": "🌅",
        "title": "Пьяццале Микеланджело",
        "subtitle": "Piazzale Michelangelo · 1869",
        "facts": [
            ("Архитектор", "Джузеппе Поджи"),
            ("Повод", "Флоренция — временная столица Италии (1865–1870)"),
            ("Высота", "104 м над уровнем моря"),
            ("В центре", "бронзовая копия «Давида» (1873)"),
            ("Рядом", "Сан-Миниато-аль-Монте — церковь XI века"),
        ],
        "history": [
            "Когда в 1865 году Флоренция стала временной столицей объединённой Италии, архитектор Джузеппе Поджи получил масштабный заказ — спроектировать «бульвары» вокруг города по парижской модели Османа и облагородить южный холм Сан-Миниато. Так появился Пьяццале Микеланджело — обзорная терраса, открытая в 1869 году.",
            "В центре площадки — бронзовая копия Давида, окружённая копиями четырёх аллегорий капеллы Медичи (Утро, День, Вечер, Ночь). Поджи задумывал здесь и музей Микеланджело, но он так и не был построен — нынешнее «Лоджия» внизу превратилась в ресторан.",
            "С Пьяццале — лучший вид Флоренции: купол Брунеллески прямо по центру, башня Палаццо Веккьо и кампанила Джотто слева, изгиб Арно с Понте-Веккьо. Особенно на закате — итальянцы называют этот свет «la luce del Rinascimento».",
        ],
        "fact": "К Пьяццале лучше подниматься пешком по «Розовому саду» (Giardino delle Rose) — бесплатно, тенисто и красиво. Спуск — мимо церкви Сан-Миниато-аль-Монте с её полосатым романским фасадом 1018 года.",
    },
]

VENICE_DETAILS = [
    {
        "icon": "✪",
        "title": "Собор Сан-Марко",
        "subtitle": "Basilica di San Marco · 829–1094 (нынешняя — с 1063)",
        "facts": [
            ("Стиль", "византийский с готическими и ренессансными добавлениями"),
            ("Купола", "5 крупных, по образцу храма Апостолов в Константинополе"),
            ("Мозаики", "8000 м², от XI до XIX вв., золото-смальта"),
            ("Pala d’Oro", "1102–1342: 1927 драгоценных камня, 187 эмалей"),
            ("Бронзовые кони", "греческие оригиналы IV в. до н. э., из Константинополя"),
        ],
        "history": [
            "В 828 году два венецианских купца выкрали из Александрии мощи апостола Марка, спрятав их в свинине, которую мусульмане-стражники не стали проверять. Над святыней дож Юстиниан построил первую базилику; нынешняя — третья по счёту, освящена в 1094-м.",
            "Сан-Марко — главный «военный трофей» Венеции: после захвата Константинополя в 1204 году крестоносцы под командованием венецианского дожа Дандоло вывезли в собор всё ценное, включая знаменитых бронзовых коней (на фасаде сейчас копии, оригиналы — в музее наверху).",
            "Внутри 8000 м² мозаик образуют «золотую коробку» — отсюда прозвище «Chiesa d’Oro». Pala d’Oro за главным алтарём — золотой ретабль, набираемый и дополнявшийся 250 лет: в нём 1927 драгоценных и полудрагоценных камней. До 1807 года Сан-Марко был не главным храмом Венеции, а домовой капеллой дожа: патриарх сидел в Сан-Пьетро-ди-Кастелло.",
        ],
        "fact": "Полы собора — мозаика XII века с геометрическими узорами и животными — со временем «поплыли»: грунт под собором проседает, и пол идёт волнами. При высокой воде acqua alta его иногда заливает.",
    },
    {
        "icon": "♛",
        "title": "Дворец дожей и Мост вздохов",
        "subtitle": "Palazzo Ducale · с IX в., готика 1340–1424 · Ponte dei Sospiri 1602",
        "facts": [
            ("Стиль", "венецианская готика, белый и розовый веронский мрамор"),
            ("Зал Большого совета", "53 × 25 м — крупнейшая зала Европы того времени"),
            ("Тинторетто", "«Рай», 22×7 м — крупнейшая картина маслом в мире"),
            ("Тюрьма", "Piombi (под крышей) и Pozzi (под водой)"),
            ("Мост вздохов", "Антонио Контино, 1602, белый истрийский камень"),
        ],
        "history": [
            "Дворец дожей был резиденцией главы Венецианской республики, парламентом, верховным судом и тюрьмой одновременно. Готическая аркада на первых двух этажах опровергает все законы — массивная стена «парит» над лёгкими колоннами. Капитель за углом, у моря, изображает Адама и Еву — самая старая (XIV в.) и тонкая работа.",
            "Внутри — Зал Большого совета, где собирались до 2000 нобилей. По периметру — 76 портретов дожей: один закрашен чёрным с надписью «Hic est locus Marini Faletro decapitati pro criminibus» — место казнённого за заговор Марино Фальеро (1355). На потолке — гигантский «Рай» Тинторетто и «Триумф Венеции» Веронезе.",
            "Мост вздохов соединяет дворец с тюрьмой Prigioni Nuove: осуждённые шли по нему, бросая последний взгляд на свободу — отсюда название, придуманное Байроном. По этому мосту бежал из Пьомби в 1756 году Джакомо Казанова — единственный за всю историю успешный побег из венецианской тюрьмы.",
        ],
        "fact": "На фасаде со стороны Пьяццетты — две красные колонны. Между ними публично казнили преступников; до сих пор венецианцы из суеверия избегают проходить именно между ними.",
    },
    {
        "icon": "↑",
        "title": "Кампанила Сан-Марко",
        "subtitle": "Campanile di San Marco · X в., воссоздана в 1912",
        "facts": [
            ("Высота", "98,6 м — самое высокое здание Венеции"),
            ("Фундамент", "сваи в иле, без свай-«венецианский лес»"),
            ("Пять колоколов", "у каждого своё имя и функция"),
            ("Лоджетта внизу", "Якопо Сансовино, 1538–1546"),
            ("Лифт", "с 1962 — без подъёма по ступеням"),
        ],
        "history": [
            "Кампанила служила сразу маяком, дозорной вышкой и колокольней. Колокола подавали разные сигналы городу: «marangona» — начало и конец рабочего дня, «trottiera» — сбор сенаторов на заседание, «nona» — полдень, «mezza terza» — открытие судов, «malefico» — казнь.",
            "В 1609 году Галилео Галилей привёл сюда дожа Леонардо Дона и продемонстрировал свой только что усовершенствованный телескоп — Сенат повысил ему жалование и пожизненно закрепил кафедру в Падуе.",
            "14 июля 1902 года, без жертв, кампанила обрушилась — за неделю до этого в стенах появились трещины, и площадь успели огородить. Совет города в тот же день постановил: «com’era, dov’era» — «как была, где была». Восстановление закончили в апреле 1912 года к тысячелетию первой постройки.",
        ],
        "fact": "Перед обрушением 1902 года кампанилу спасал реставратор Пьетро Сальяна — но за 50 минут до катастрофы он спустился на обед. Из-под завалов потом достали единственного «пострадавшего»: смотрительского кота.",
    },
    {
        "icon": "⚓",
        "title": "Гондола",
        "subtitle": "Gondola · традиционная лодка с XI века",
        "facts": [
            ("Размеры", "10,87 м длина, 1,42 м ширина, 700 кг"),
            ("Конструкция", "8 пород дерева, 280 деталей"),
            ("Асимметрия", "левый борт на 24 см длиннее — компенсация одного гребца"),
            ("Ferro", "6 зубцов = 6 районов (sestiere) Венеции"),
            ("Статус", "сегодня лицензий ~425; первая женщина-гондольер — 2010"),
        ],
        "history": [
            "Слово «gondola» впервые упоминается в документе 1094 года. К XVII веку их было около 10 000 — личным транспортом каждой состоятельной семьи. Чтобы прекратить хвастовство роскошью, в 1562 году Сенат предписал красить все гондолы исключительно в чёрный цвет. С тех пор это правило не нарушалось.",
            "Современная гондола формировалась веками: только в XIX веке мастер Доменико Транкуилло Фриулани добавил выраженную асимметрию корпуса — гондольер гребёт только справа стоя, и правильный наклон лодки сам компенсирует прямой ход. Сложная двоемордая форма ferro (носового украшения) объединяет головной убор дожа сверху и шесть гребней — символы шести районов города.",
            "Лицензию гондольера получают по экзамену с 50–100 кандидатами на место: история города, навигация в каналах, английский, иногда японский. Одни и те же семьи занимаются этим веками — отсюда и стоимость прогулки. Стандарт: 30 минут — €90 (днём), €110 (после 19:00) за лодку до 5 человек.",
        ],
        "fact": "Squero di San Trovaso в Дорсодуро — последняя действующая верфь, где гондолы строят традиционным способом. Туда можно прийти посмотреть, как мастер вручную «изгибает» левый борт горящим тростником.",
    },
    {
        "icon": "✶",
        "title": "Мурано — остров стекла",
        "subtitle": "Murano · с XIII в. — мировая столица стеклоделия",
        "facts": [
            ("От Сан-Марко", "вапоретто №4.1 / №4.2, ~25 минут"),
            ("Перенос мастерских", "1291 — указ Сената, ради защиты от пожаров"),
            ("Базилика", "Санти-Мария-э-Донато, XII в., мозаичный пол 1140 г."),
            ("Музей стекла", "Museo del Vetro, € 10, в Палаццо Джустиниан"),
            ("Знаменито", "millefiori, латтимо, авентурин, муранские люстры"),
        ],
        "history": [
            "Венеция была деревянным городом, а печи стеклоделов — постоянной угрозой пожара. В 1291 году Сенат постановил перенести все мастерские на остров Мурано. Стеклодувы получили привилегии аристократии: дочери могли выходить за дворян, а дети мастеров наследовали фамилию.",
            "Но был и обратный эффект — за разглашение секретов мастерства полагалась смерть. Тех, кто всё же бежал во Францию или Богемию, тайно настигали посланцы Совета десяти. Так Венеция почти 400 лет удерживала монополию: цветное стекло, прозрачное cristallo, авантюрин с золотыми искрами, технику millefiori.",
            "Сегодня на острове ~200 мастерских — по-настоящему ручную работу легко отличить от китайских подделок: ищите наклейку «Vetro Artistico Murano» с коллективным товарным знаком и подпись маэстро. Базилика Санти-Мария-э-Донато XII века скрывает один из самых красивых мозаичных полов Италии — ровесника Сан-Марко.",
        ],
        "fact": "Хранители костей дракона: за алтарём базилики Сан-Донато выставлены четыре огромных «драконьих ребра», которые, по преданию, святой Донат привёз из Малой Азии. На самом деле — кости доисторического кита.",
    },
    {
        "icon": "✿",
        "title": "Бурано — остров кружев",
        "subtitle": "Burano · поселение с VI века · кружевная столица",
        "facts": [
            ("Расположение", "лагуна, 7 км от Венеции, 40 минут вапоретто"),
            ("Население", "~2 800 человек"),
            ("Дома", "разноцветные, по строгому реестру цветов"),
            ("Кружево", "punto in aria, с XVI века"),
            ("Достопримечательность", "падающая колокольня Сан-Мартино, XVI в."),
        ],
        "history": [
            "Бурано основали жители материка, бежавшие в лагуну от лангобардских нашествий VI века. Пока Венеция богатела на торговле, на Бурано развились два промысла: рыбная ловля и кружевоплетение «punto in aria» («стежок в воздухе») — без подложки.",
            "В XVI веке буранское кружево стало визитной карточкой европейских аристократок — Екатерина Медичи, Елизавета Английская и Людовик XIV заказывали манжеты только отсюда. К XX веку ремесло почти умерло; в 1981 году муниципалитет открыл Музей кружева, чтобы сохранить технику.",
            "Знаменитые цветные домики — не туристический ход: рыбаки красили дома в яркие тона, чтобы видеть свою улицу в утреннем тумане лагуны. Цвет каждого дома закреплён за хозяином: чтобы перекрасить, нужно подать заявление в коммуну и получить три согласованных варианта.",
        ],
        "fact": "Колокольня Сан-Мартино — местная Пизанская: отклонение около 1,83 м. Её ставили на свайном фундаменте, который начал крениться почти сразу после постройки.",
    },
    {
        "icon": "✟",
        "title": "Санта-Мария делла Салюте",
        "subtitle": "Basilica di Santa Maria della Salute · 1631–1687",
        "facts": [
            ("Архитектор", "Бальдассаре Лонгена (ему было 26 лет)"),
            ("Стиль", "венецианское барокко"),
            ("План", "8-угольник с большим и малым куполами"),
            ("Свайный фундамент", "1 156 627 деревянных свай в иле"),
            ("Картины ризницы", "Тициан, Тинторетто"),
        ],
        "history": [
            "В 1630–1631 годах Венецию опустошила чума: погибло 46 000 человек — почти треть города. Сенат поклялся в обмен на избавление построить Богоматери великолепный храм. 22 октября 1630 года епископ выбрал место — оконечность Дорсодуро напротив Сан-Марко. Конкурс выиграл молодой Лонгена.",
            "Чтобы поставить тяжёлый храм на топкую землю, в дно вбили более миллиона деревянных свай — лиственница из карстовых лесов веками не гниёт под водой. На этом «лесу» лежит каменное основание. Барочная сложность плана — два связанных восьмиугольника — потребовала революционных по тем временам инженерных решений.",
            "Внутри — 12 крупных алтарных полотен, на алтаре — византийская икона «Madonna della Salute» XIII века. В ризнице — поздние работы Тициана («Давид и Голиаф», «Каин и Авель», «Жертвоприношение Авраама») и «Брак в Кане» Тинторетто. Каждое 21 ноября от Сан-Марко до Салюте перекидывают понтонный мост — праздник Madonna della Salute.",
        ],
        "fact": "Огромные «уши» по периметру храма — на самом деле не декорация, а контрфорсы-завитки (volute), которые Лонгена замаскировал в волну барокко. Они держат гигантский купол.",
    },
    {
        "icon": "◈",
        "title": "Венецианская Биеннале — Arte 2026",
        "subtitle": "La Biennale di Venezia · 61-я Международная выставка искусства",
        "facts": [
            ("Год основания", "1895 — старейшая в мире биеннале"),
            ("Локации", "Giardini (с 1895) и Arsenale (с 1980)"),
            ("Часы 2026", "вт–вс 11:00–19:00, пт–сб до 20:00; пн закрыто"),
            ("Билет", "€ 30 — единый, на 2 локации, действует 2 дня"),
            ("Время визита", "5–6 часов на обе площадки"),
        ],
        "history": [
            "Первая Esposizione Internazionale d’Arte открылась 30 апреля 1895 года в честь 25-летия свадьбы короля Умберто I — городские власти искали способ оживить Венецию после её упадка как порта. С тех пор Биеннале проходит каждые два года и стала прообразом всех последующих биеннале мира — от Сан-Паулу до Стамбула.",
            "Главная локация — Giardini della Biennale, заложенные ещё Наполеоном в 1807-м. На 19 акрах работают 29 национальных павильонов, многие — архитектурные памятники сами по себе: австрийский Йозефа Хоффмана, голландский Геррита Ритвельда, скандинавский Сверре Фена, бразильский Энрико Темпеля, российский Алексея Щусева.",
            "Вторая локация — Arsenale, бывшая судостроительная верфь Венецианской республики (с XII в.), некогда — крупнейший промышленный комплекс Европы, где собирали по галере в день. С 1980 года длинные кирпичные галереи Корерие и Гаджандре отданы кураторской выставке и павильонам стран без своего здания. 61-я Arte 2026 продлится с апреля по ноябрь — июнь идеален: уже всё открыто, а толпы пика сентября ещё впереди.",
        ],
        "fact": "Премии «Золотой лев» Биеннале вручают с 1949 года — сейчас существует пять номинаций. У России свой павильон с 1914 года; в разные годы там выступали Кандинский, Малевич, Кабаков, AES+F.",
    },
]


# ============================================================ #
#                          СБОРКА                                #
# ============================================================ #
# Итоговое количество слайдов:
# 1 титул + 1 авиабилеты + 1 обзор маршрута
# + 1 Рим обзор + N_R слайдов о римских достопримечательностях
# + 1 Флоренция обзор + N_F слайдов
# + 1 Венеция обзор + N_V слайдов
# + 1 бюджет
N_R = len(ROME_DETAILS)
N_F = len(FLORENCE_DETAILS)
N_V = len(VENICE_DETAILS)
TOTAL = 3 + (1 + N_R) + (1 + N_F) + (1 + N_V) + 1
page = 1


def add_slide_and_advance():
    global page
    s = prs.slides.add_slide(BLANK)
    p = page
    page += 1
    return s, p


# 1. Титульный
slide, _ = add_slide_and_advance()
make_title_slide(slide)

# 2. Авиабилеты
slide, p = add_slide_and_advance()
make_flights_slide(slide, p, TOTAL)

# 3. Маршрут — обзор
slide, p = add_slide_and_advance()
make_route_overview_slide(slide, p, TOTAL)

# --- Рим: обзорный + детали ---
slide, p = add_slide_and_advance()
make_city_slide(
    slide, page=p, total=TOTAL,
    header_title="Рим · 8 — 13 июня",
    city_title="Roma",
    city_subtitle="Вечный город · 5 ночей · базируемся в Монти / Прати",
    accent=COLOR_RED, light_accent=COLOR_LIGHT_RED,
    days=ROME_DAYS, attractions=ROME_ATTRACTIONS, tips=ROME_TIPS,
)
for i, d in enumerate(ROME_DETAILS, 1):
    slide, p = add_slide_and_advance()
    make_attraction_slide(
        slide, page=p, total=TOTAL,
        city=f"РИМ  ·  Достопримечательность {i} / {N_R}",
        city_color=COLOR_RED,
        accent=COLOR_RED, light_accent=COLOR_LIGHT_RED,
        **d,
    )

# --- Флоренция: обзорный + детали ---
slide, p = add_slide_and_advance()
make_city_slide(
    slide, page=p, total=TOTAL,
    header_title="Флоренция · 13 — 17 июня",
    city_title="Firenze",
    city_subtitle="Колыбель Ренессанса · 4 ночи · отель в центре, в шаге от Дуомо",
    accent=COLOR_GREEN, light_accent=COLOR_LIGHT_GREEN,
    days=FLORENCE_DAYS, attractions=FLORENCE_ATTRACTIONS, tips=FLORENCE_TIPS,
)
for i, d in enumerate(FLORENCE_DETAILS, 1):
    slide, p = add_slide_and_advance()
    make_attraction_slide(
        slide, page=p, total=TOTAL,
        city=f"ФЛОРЕНЦИЯ  ·  Достопримечательность {i} / {N_F}",
        city_color=COLOR_GREEN,
        accent=COLOR_GREEN, light_accent=COLOR_LIGHT_GREEN,
        **d,
    )

# --- Венеция: обзорный + детали ---
slide, p = add_slide_and_advance()
make_city_slide(
    slide, page=p, total=TOTAL,
    header_title="Венеция · 17 — 19 июня",
    city_title="Venezia",
    city_subtitle="Город на воде · 2 ночи · сестьере Сан-Марко или Дорсодуро · Биеннале Arte 2026",
    accent=COLOR_GOLD, light_accent=COLOR_LIGHT_GOLD,
    days=VENICE_DAYS, attractions=VENICE_ATTRACTIONS, tips=VENICE_TIPS,
)
for i, d in enumerate(VENICE_DETAILS, 1):
    slide, p = add_slide_and_advance()
    make_attraction_slide(
        slide, page=p, total=TOTAL,
        city=f"ВЕНЕЦИЯ  ·  Достопримечательность {i} / {N_V}",
        city_color=COLOR_GOLD,
        accent=COLOR_GOLD, light_accent=COLOR_LIGHT_GOLD,
        **d,
    )

# Финальный слайд — бюджет
slide, p = add_slide_and_advance()
make_budget_slide(slide, p, TOTAL)

OUT = "Италия_2026_План_путешествия.pptx"
prs.save(OUT)
print(f"OK · {len(prs.slides)} слайдов · сохранено в {OUT}")
