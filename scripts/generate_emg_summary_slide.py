"""Generate the EMG IT-landscape summary slide (3 colored columns)."""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Cm, Pt


OUT = Path(__file__).resolve().parent.parent / "docs" / "slide-emg-summary.pptx"

SLIDE_W_CM = 33.867
SLIDE_H_CM = 19.05

HEADER_BLUE = RGBColor(0x35, 0x4A, 0xCB)
HEADER_PURPLE = RGBColor(0x1D, 0x1A, 0xA3)
GREEN_BORDER = RGBColor(0x3D, 0xB4, 0x5D)
BLACK = RGBColor(0x10, 0x10, 0x10)
RED = RGBColor(0xC0, 0x39, 0x2B)
TITLE_BG = RGBColor(0xF2, 0xF6, 0xFC)


HEADERS = [
    ("Текущие результаты анализа", HEADER_BLUE),
    ("Выявленная проблематика", HEADER_BLUE),
    ("Текущие рекомендации", HEADER_PURPLE),
]

# (bullet, is_red_emphasis)
COL1 = [
    ("Что сделано: обследован ИТ-ландшафт ЭМГ (НГДУ Жылыоймунайгаз, Кайнармунайгаз), собран реестр 19 ИС с протоколами и направлениями обмена", False),
    ("С кем интервьюировали: С. Нуржанова, СП В. Молдабек, владельцы ABAI / ИМ, КЦ КМГ (SAP, АСУНСИ, КХД, AD), ОЦИБ Qazcloud", False),
    ("Поездки: НГДУ Жылыоймунайгаз и Кайнармунайгаз (АСУТП), КУУН / АГЗУ / реклоузеры КОА, НПС-3, SDMO, офисы КЦ КМГ и ЭМГ", False),
    ("Подтверждена гибридная модель: собственный ЦОД + IaaS Qazcloud (VMware); ядро данных — ИС ABAI с IV кв. 2024 (ТБД выведена в архив, сопровождает КМГ Инжиниринг)", False),
    ("Корпоративный контур: SAP ERP + 1С (учёт), Directum (СЭД), SMAX (ITSM с 2023), ArgusPro (GPS с 2025, заменил CityPoint); ИБ — НПА + ОЦИБ Qazcloud 24×7 SLA", False),
    ("Построены сводные схемы (C4, Mermaid, SVG, draw.io): корпоративный ландшафт, фокус ЭМГ–ABAI, ИМ, SAP-хаб, слои ABAI, общий ИТ-ландшафт", False),
    ("Реестр ИС с владельцами / критичностью / SLA — в стадии подготовки; часть материалов передана только в бумажном виде", False),
]

COL2 = [
    ("Децентрализованная архитектура сбора данных: ESB / API Gateway не внедрена, обмен «точка-точка», реестр потоков и SLA отсутствуют", True),
    ("9+ источников телеметрии (ABAI, Kepware OPC DA, OPC UA, Modbus, SDMO, KTM, WinCC HDA, emg) подключены напрямую к ИМ; параллельно работают 3 контура: ABAI, ИМ/cmv2, АСДЦ", False),
    ("Верхнеуровневая as-is схема расходится с фактом: SMAX внедрён, ТБД в архиве, CityPoint → ArgusPro; дубли (City Point, EAM ×2, KPI ×2, SAP MDM, SCADA ×N, SAP HCM vs 1С 8.2)", False),
    ("Высокая степень ручного ввода и дублирования данных: модель данных не сформирована, MDM / Data Governance / Data Office отсутствуют, единого владельца НСИ нет", True),
    ("Аналитика живёт во встроенных средствах SAP / 1С / ABAI / Directum — «силосы» без единой версии правды; реестры СИЗ, добычи, нарушений идут XLSX по SMTP", False),
    ("Отсутствие единой базы данных по осложнениям: в ABAI в продуктиве только 6 отчётных форм из 58, 52 в доработке; ключевые расчётные модули — вспомогательные", True),
    ("Корпоративное КХД на уровне ЭМГ отсутствует — ожидается «сверху» от КЦ КМГ; ABAI развивает внешний подрядчик (КМГ Инжиниринг), ЭМГ не управляет очередью развития", False),
    ("Расхождения SAP ↔ 1С ↔ ABAI ↔ Directum ↔ SCADA ↔ лаборатория не закрываются регулярно → разные версии правды по добыче, фонду скважин, материалам, кадрам", False),
    ("Риски: интеграционный (рост стоимости и техдолга), облачный (DR/BCP, RPO/RTO, OT/IT сегментация не подтверждены), регуляторный (нет автоэкомониторинга), вендорный/санкционный", False),
]

COL3 = [
    ("Формирование единой платформы-источника данных: свести 3 контура (ABAI / ИМ / АСДЦ) к одной модели данных по скважинам, режимам и ремонтам с RACI «ЭМГ ↔ КМГ Инжиниринг»", False),
    ("Закрыть 52 отчётные формы ABAI, зафиксировать дорожную карту функциональных модулей (ГТМ, подбор ГНО, заводнение, осложнения) со стадиями идея/ТЭО/ТЗ/пилот/проект", False),
    ("Заменить пакетные CSV/XLSX-выгрузки SAP ↔ 1С / FC / Кадры / СИЗ на API через SAP PO / шину; SMTP-рассылки реестров — на дашборды поверх единого хранилища", False),
    ("Выстраивание целевой архитектуры: корпоративный Data Lake поверх КХД КМГ + ESB / API Gateway / iPaaS (SAP PO, WSO2, Kafka, Camel, DataFlow, 1С:Шина); SLA на потоки, реестр интеграций", False),
    ("Приоритетные потоки автоматизации: (1) учёт добычи (скважина/куст/ДНС/мест.), (2) ГТМ и ТКРС, (3) осложнения и подбор ГНО, (4) ТОиР (единая EAM), (5) НСИ и закупки", False),
    ("Закрыть «красные» гэпы: производственное планирование, ЦУМ, моделирование скважины/пласта/нефтесбора, петрофизика, экомониторинг, DLP, внутренний портал (Directum-интеграция)", False),
    ("Усилить инфраструктуру и ИБ: DR-площадка, RPO/RTO, резервное копирование, сегментация OT/IT, SIEM/IAM/PAM/NGFW/EDR/MFA; зафиксировать Shared Responsibility ЭМГ ↔ Qazcloud ↔ ОЦИБ ↔ КМГИ", False),
    ("Унификация НСИ: мастер-система АСУНСИ + Informatica MDM Product 360 — для ДЗО (ЭМГ, ОМГ, КМГИ); единые справочники скважин (КГИС / ArcGIS), оборудования (EAM), материалов, контрагентов", False),
    ("Закрыть кадровый контур: определить источник истины между SAP HCM и 1С 8.2 «Зарплата»; внедрить архитектурное управление (архкомитет, ADR, стандарты, KPI), матрица as-is → to-be", False),
]


def add_header(slide, left, top, width, height, text, color):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.adjustments[0] = 0.35
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    tf = shape.text_frame
    tf.margin_left = Cm(0.3)
    tf.margin_right = Cm(0.3)
    tf.margin_top = Cm(0.1)
    tf.margin_bottom = Cm(0.1)
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.size = Pt(18)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    run.font.name = "Calibri"


def add_body_box(slide, left, top, width, height, bullets):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.adjustments[0] = 0.06
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    shape.line.color.rgb = GREEN_BORDER
    shape.line.width = Pt(1.75)
    tf = shape.text_frame
    tf.margin_left = Cm(0.45)
    tf.margin_right = Cm(0.45)
    tf.margin_top = Cm(0.35)
    tf.margin_bottom = Cm(0.35)
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP

    for i, (text, emphasis) in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(4)
        p.level = 0
        run = p.add_run()
        run.text = "• " + text
        run.font.size = Pt(10)
        run.font.name = "Calibri"
        run.font.color.rgb = RED if emphasis else BLACK
        run.font.bold = emphasis


def main():
    prs = Presentation()
    prs.slide_width = Cm(SLIDE_W_CM)
    prs.slide_height = Cm(SLIDE_H_CM)
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)

    margin_x = Cm(0.6)
    margin_top = Cm(0.6)
    gap = Cm(0.4)
    col_w = (prs.slide_width - 2 * margin_x - 2 * gap) // 3
    header_h = Cm(1.4)
    body_top = margin_top + header_h + Cm(0.3)
    body_h = prs.slide_height - body_top - Cm(0.6)

    for idx, ((title, color), bullets) in enumerate(zip(HEADERS, [COL1, COL2, COL3])):
        left = margin_x + (col_w + gap) * idx
        add_header(slide, left, margin_top, col_w, header_h, title, color)
        add_body_box(slide, left, body_top, col_w, body_h, bullets)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
