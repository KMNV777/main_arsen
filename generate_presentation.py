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
                "•  Острова Мурано и Бурано",
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
     "plan": "11:00 — собор Сан-Марко (бронь skip-the-line) · 12:30 — Дворец дожей и Мост вздохов · обед · сиеста · 17:00 — гондола (30 мин) по тихим каналам · ужин в Дорсодуро"},
    {"day": "Пт, 19 июня", "date": "День 3 · острова + переезд",
     "plan": "10:30 — вапоретто на Мурано (стекло) и Бурано (цветные домики) · обед на Бурано · возвращение к 16:00 · 17:25 — Frecciarossa Venezia → Roma Termini (~3 ч 45 мин) · ночёвка у FCO"},
    {"day": "Сб, 20 июня", "date": "День 4 · вылет",
     "plan": "Лёгкий завтрак · трансфер в FCO к 9:30 · регистрация · вылет в 11:55 → Санкт-Петербург 21:00"},
]

VENICE_ATTRACTIONS = [
    {"name": "Собор Сан-Марко (skip-the-line)",
     "price": "€ 6", "note": "+ € 7 Pala d’Oro, + € 7 музей"},
    {"name": "Дворец дожей + Мост вздохов",
     "price": "€ 30", "note": "комбо с Museo Correr"},
    {"name": "Кампанила Сан-Марко (лифт)",
     "price": "€ 12", "note": "виды на лагуну"},
    {"name": "Гондола 30 мин (днём)",
     "price": "€ 90 / лодка", "note": "до 5 чел., после 19:00 — € 110"},
    {"name": "Вапоретто 72 часа (ACTV)",
     "price": "€ 45 / чел", "note": "выгоднее единичных билетов €9,50"},
    {"name": "Мурано + Бурано (вход бесплатный)",
     "price": "вход 0", "note": "только проезд вапоретто"},
    {"name": "Базилика Санта-Мария делла Салюте",
     "price": "€ 8", "note": "ризница; сама церковь — бесплатно"},
]

VENICE_TIPS = [
    "Подъём 9:00–9:30 — на Сан-Марко идём после сиесты толп",
    "Сиеста 14:00–16:30: венецианская жара + влажность",
    "Гондолу заказываем у проверенного gondoliere, фикс. цена",
    "20 июня — единственный ранний подъём (~7:30) ради вылета",
]

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
        ("Дворец дожей + Сан-Марко skip",                "€ 72"),
        ("Гондола 30 мин",                               "€ 90"),
        ("Вапоретто 72h × 2",                            "€ 90"),
    ]
    y = Inches(2.05)
    row_h = Inches(0.32)
    for name, price in rows:
        is_header = price == ""
        if is_header:
            add_rect(slide, Inches(0.7), y, Inches(7.3), row_h, COLOR_LIGHT_GREEN)
            add_text(slide, Inches(0.85), y, Inches(7.0), row_h,
                     name, size=12, bold=True, color=COLOR_GREEN,
                     anchor=MSO_ANCHOR.MIDDLE)
        else:
            add_text(slide, Inches(0.85), y, Inches(5.8), row_h,
                     name, size=11, color=COLOR_DARK, anchor=MSO_ANCHOR.MIDDLE)
            add_text(slide, Inches(6.7), y, Inches(1.3), row_h,
                     price, size=11, bold=True, color=COLOR_DARK,
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
             "≈ € 870",
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
#                          СБОРКА                                #
# ============================================================ #
TOTAL = 7

# 1. Титульный
slide = prs.slides.add_slide(BLANK)
make_title_slide(slide)

# 2. Авиабилеты
slide = prs.slides.add_slide(BLANK)
make_flights_slide(slide, 2, TOTAL)

# 3. Маршрут — обзор
slide = prs.slides.add_slide(BLANK)
make_route_overview_slide(slide, 3, TOTAL)

# 4. Рим
slide = prs.slides.add_slide(BLANK)
make_city_slide(
    slide, page=4, total=TOTAL,
    header_title="Рим · 8 — 13 июня",
    city_title="Roma",
    city_subtitle="Вечный город · 5 ночей · базируемся в Монти / Прати",
    accent=COLOR_RED, light_accent=COLOR_LIGHT_RED,
    days=ROME_DAYS, attractions=ROME_ATTRACTIONS, tips=ROME_TIPS,
)

# 5. Флоренция
slide = prs.slides.add_slide(BLANK)
make_city_slide(
    slide, page=5, total=TOTAL,
    header_title="Флоренция · 13 — 17 июня",
    city_title="Firenze",
    city_subtitle="Колыбель Ренессанса · 4 ночи · отель в центре, в шаге от Дуомо",
    accent=COLOR_GREEN, light_accent=COLOR_LIGHT_GREEN,
    days=FLORENCE_DAYS, attractions=FLORENCE_ATTRACTIONS, tips=FLORENCE_TIPS,
)

# 6. Венеция
slide = prs.slides.add_slide(BLANK)
make_city_slide(
    slide, page=6, total=TOTAL,
    header_title="Венеция · 17 — 19 июня",
    city_title="Venezia",
    city_subtitle="Город на воде · 2 ночи · сестьере Сан-Марко или Дорсодуро",
    accent=COLOR_GOLD, light_accent=COLOR_LIGHT_GOLD,
    days=VENICE_DAYS, attractions=VENICE_ATTRACTIONS, tips=VENICE_TIPS,
)

# 7. Бюджет
slide = prs.slides.add_slide(BLANK)
make_budget_slide(slide, 7, TOTAL)

OUT = "Италия_2026_План_путешествия.pptx"
prs.save(OUT)
print(f"OK · сохранено в {OUT}")
