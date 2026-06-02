#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Общая архитектурная схема КМГ и ЭМГ с выделением корпоративных сетей.

Схема объединяет:
  * организационный контур (КЦ КМГ, АО «Эмбамунайгаз», КМГИ);
  * корпоративную сеть / цифровой контур ЭМГ (OT → ИМ → ядро цифровизации);
  * корпоративную сеть группы КМГ (ИС, SAP-хаб, финансы, ИБ, НСИ);
  * интеграционные потоки с протоколами и форматами (матрица 19 систем).

Запуск:
    pip install -r requirements.txt
    python3 scripts/build_kmg_emg_network_diagram.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from drawio_export import configure_drawio_file  # noqa: E402

from build_emg_c4_component import (  # noqa: E402
    B,
    COMP_W,
    EDGE_DASH,
    EDGE_SOLID,
    L,
    Diagram,
    File,
    Page,
    R,
    T,
    SIDE_W,
    container_dims,
    make_obj,
    render_svg,
)

OUT_DIR = ROOT / "docs" / "drawio"
SVG_DIR = ROOT / "docs" / "svg"
DRAWIO_NAME = "08-kmg-emg-corporate-networks.drawio"
SVG_NAME = "08-kmg-emg-corporate-networks.svg"

# Крупные контуры «корпоративных сетей»
NET_EMG_STYLE = (
    "rounded=0;dashed=1;dashPattern=10 5;fillColor=#E8F5E9;strokeColor=#2E7D32;"
    "strokeWidth=2;verticalAlign=top;align=left;fontStyle=1;fontSize=14;"
    "fontColor=#1B5E20;spacingLeft=12;spacingTop=8;html=1;"
)
NET_KMG_STYLE = (
    "rounded=0;dashed=1;dashPattern=10 5;fillColor=#E3F2FD;strokeColor=#1565C0;"
    "strokeWidth=2;verticalAlign=top;align=left;fontStyle=1;fontSize=14;"
    "fontColor=#0D47A1;spacingLeft=12;spacingTop=8;html=1;"
)
ORG_BAND_STYLE = (
    "rounded=0;fillColor=#F3E5F5;strokeColor=#6A1B9A;strokeWidth=1;"
    "verticalAlign=top;align=center;fontStyle=1;fontSize=13;fontColor=#4A148C;"
    "spacingTop=6;html=1;"
)
CONTAINER_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#8497B0;"
    "verticalAlign=top;align=left;fontStyle=1;fontSize=11;fontColor=#23364B;"
    "spacingLeft=8;spacingTop=5;spacingRight=8;"
)
ACTOR_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#6A1B9A;strokeColor=#4A148C;"
    "fontColor=#ffffff;fontStyle=1;verticalAlign=middle;align=center;fontSize=11;"
)


def build() -> tuple[File, Diagram]:
    f = configure_drawio_file(File(file_name=DRAWIO_NAME, file_path=str(OUT_DIR)))
    page = Page(file=f, name="КМГ + ЭМГ — корпоративные сети", width=2380, height=1380)
    d = Diagram(page)

    # --- Организационный контур (над сетями) ---
    org_y, org_h = 24, 118
    d._add(
        make_obj(value="Организационный контур группы КМГ", position=(40, org_y), width=2300, height=org_h, baseStyle=ORG_BAND_STYLE),
        40, org_y, 2300, org_h,
    )
    org_w = 720
    org_x = (40 + 2300 - org_w) // 2
    org = {}
    for i, (label, ox) in enumerate([("КЦ КМГ", org_x), ("АО «Эмбамунайгаз»", org_x + 250), ("КМГИ", org_x + 500)]):
        node = make_obj(value=label, position=(ox, org_y + 36), width=210, height=56, baseStyle=ACTOR_STYLE)
        d._add(node, ox, org_y + 36, 210, 56)
        org[label] = node

    emg_net_x, emg_net_y = 40, 160
    emg_net_w, emg_net_h = 540, 1080

    kmg_net_x = emg_net_x + emg_net_w + 24
    kmg_net_y, kmg_net_w, kmg_net_h = 160, 1776, 1080

    d._add(
        make_obj(
            value="Корпоративная сеть / цифровой контур ЭМГ\n(промысловые данные, ядро цифровизации)",
            position=(emg_net_x, emg_net_y),
            width=emg_net_w,
            height=emg_net_h,
            baseStyle=NET_EMG_STYLE,
        ),
        emg_net_x, emg_net_y, emg_net_w, emg_net_h,
    )
    d._add(
        make_obj(
            value="Корпоративная сеть группы КМГ\n(корпоративные ИС, SAP-хаб, финансы, ИБ, НСИ)",
            position=(kmg_net_x, kmg_net_y),
            width=kmg_net_w,
            height=kmg_net_h,
            baseStyle=NET_KMG_STYLE,
        ),
        kmg_net_x, kmg_net_y, kmg_net_w, kmg_net_h,
    )

  # --- ЭМГ: контейнеры внутри сети ---
    cx, cy = emg_net_x + 16, emg_net_y + 52

    core = d.container(
        "Ядро цифровизации ЭМГ",
        cx, cy,
        [("ИС ABAI\nabai.kmg.kz", "emg"), ("ИС «УТО ЭМГ»", "emg"), ("АСДЦ\niis.thkmg.kz", "emg")],
        cols=1, comp_w=492,
    )
    cy += container_dims(3, 1, 492)[1] + 14

    im_band = d.container(
        "Интеллектуальное месторождение (ИМ) · OT-хаб",
        cx, cy,
        [("ИМ · cmv2 · 10.32.10.99", "emg")],
        cols=1, comp_w=492,
    )
    cy += container_dims(1, 1, 492)[1] + 14

    ot = d.container(
        "Промышленный контур (OT) · телеметрия",
        cx, cy,
        [
            ("ИСУН", "ot"),
            ("АСУТП / ТМ", "ot"),
            ("ТМ АГЗУ", "ot"),
            ("КУУН НПС-3", "ot"),
            ("СДМО", "ot"),
            ("KTM Floboss", "ot"),
        ],
        cols=2, comp_w=236,
    )

    # --- КМГ: контейнеры ---
    kx, ky = kmg_net_x + 16, kmg_net_y + 52

    corp = d.container(
        "Бизнес-системы и корпоративные порталы",
        kx, ky,
        [
            ("СЭД Directum /\nСАПФИР", "corp"),
            ("ИСОТ / ЭНД", "corp"),
            ("СДД", "corp"),
            ("Procu / Price", "corp"),
            ("БДА", "corp"),
            ("Портал Team", "corp"),
            ("Интранет", "corp"),
            ("ИСУП", "corp"),
            ("Compliance", "corp"),
            ("ИС «УТО»", "corp"),
            ("sPoint", "corp"),
            ("КГИС", "corp"),
            ("Argus Pro", "corp"),
        ],
        cols=3,
    )
    ky += container_dims(13, 3, COMP_W)[1] + 12

    doc = d.container(
        "Документооборот и архив",
        kx, ky,
        [("Alfresco (ЭА)", "doc"), ("Электронный архив\nDocumentum / Азия-Софт", "doc")],
        cols=2,
    )

    sap_x = kx + container_dims(13, 3, COMP_W)[0] + 20
    sap_y = kmg_net_y + 52

    sap = d.container(
        "SAP ERP — корпоративный хаб",
        sap_x, sap_y,
        [("SAP ERP", "sap"), ("AVR", "sap")],
        cols=2,
    )
    sap_y += container_dims(2, 2, COMP_W)[1] + 10

    fin = d.container(
        "Финансы и планирование",
        sap_x, sap_y,
        [
            ("SAS-FM", "sap"),
            ("FC", "sap"),
            ("Нацбанк", "sap"),
            ("БВУ", "sap"),
            ("Platts.com", "sap"),
            ("ИС ЭСФ", "sap"),
            ("1С (зарплата)", "sap"),
            ("СИЗ", "sap"),
        ],
        cols=2,
    )
    sap_y += container_dims(8, 2, COMP_W)[1] + 10

    hr = d.container(
        "Кадры и персонал",
        sap_x, sap_y,
        [("ПК «Управление\nперсоналом»", "corp"), ("E-Pass", "corp")],
        cols=2,
    )

    id_x = sap_x + max(container_dims(2, 2, COMP_W)[0], container_dims(8, 2, COMP_W)[0]) + 20
    id_y = kmg_net_y + 52

    idz = d.container(
        "Служба каталогов",
        id_x, id_y,
        [("Active Directory\n(LDAP)", "id")],
        cols=1, comp_w=SIDE_W,
    )
    id_y += container_dims(1, 1, SIDE_W)[1] + 12

    sec = d.container(
        "Информационная безопасность",
        id_x, id_y,
        [
            ("Solar Dozor (DLP)", "sec"),
            ("Forcepoint Web GW", "sec"),
            ("FUDO PAM", "sec"),
            ("MS Exchange", "sec"),
            ("Жулдыз", "sec"),
        ],
        cols=2,
    )
    id_y += container_dims(5, 2, COMP_W)[1] + 12

    nsi = d.container(
        "Технические интеграции / НСИ",
        id_x, id_y,
        [("КХД АО НК КМГ", "nsi"), ("АСУ НСИ", "nsi"), ("ИСЭЗ", "nsi")],
        cols=1, comp_w=SIDE_W,
    )

    # --- Узлы ---
    IM = im_band["ИМ · cmv2 · 10.32.10.99"]
    ABAI = core["ИС ABAI\nabai.kmg.kz"]
    AD = idz["Active Directory\n(LDAP)"]
    SAP = sap["SAP ERP"]
    UTO = corp["ИС «УТО»"]
    ISOT = corp["ИСОТ / ЭНД"]
    SAPFIR = corp["СЭД Directum /\nСАПФИР"]

    # OT → ИМ
    d.route(ot["ИСУН"], T(0.5), IM, B(0.22), "OPC DA · 2ч")
    d.route(ot["АСУТП / ТМ"], T(0.5), IM, B(0.78), "OPC UA · 5м")
    d.route(ot["ТМ АГЗУ"], T(0.5), IM, B(0.10), "SQL+OPC UA · 5м")
    d.route(ot["СДМО"], T(0.5), IM, B(0.40), "MySQL · 1ч")
    d.route(ot["КУУН НПС-3"], T(0.5), IM, B(0.58), "Modbus · 2ч")
    d.route(ot["KTM Floboss"], T(0.5), IM, B(0.90), "SQL")

    # Ядро ЭМГ ↔ ИМ
    d.route(ABAI, B(0.35), IM, T(0.35), "SQL read\n08:00/13:30/18:00")
    d.route(core["АСДЦ\niis.thkmg.kz"], B(0.5), IM, T(0.65), "диспетчеризация", dashed=True)

    # Пересечение сети ЭМГ → КМГ
    d.route(core["ИС «УТО ЭМГ»"], R(0.5), UTO, L(0.5), "локальный контур")
    d.route(ABAI, R(0.35), ISOT, L(0.5), "REST / SMTP\nСИЗ, добыча")
    d.route(ABAI, R(0.65), SAPFIR, L(0.3), "REST JSON\nотчёты", dashed=True)
    d.route(ABAI, R(0.85), corp["БДА"], L(0.5), "активы", dashed=True)
    d.route(IM, R(0.5), corp["БДА"], L(0.2), "REST JSON\nаналитика :8099", waypoints=[(580, 520), (620, 520)])

    # Организационный контур
    d.route(org["АО «Эмбамунайгаз»"], B(0.5), ABAI, T(0.5), "владеет / эксплуатирует", dashed=True)
    d.route(org["КЦ КМГ"], B(0.5), SAP, T(0.3), "корпоративный учёт", dashed=True)
    d.route(org["КМГИ"], B(0.5), corp["ИСУП"], T(0.5), "проекты", dashed=True)

    # SAP-хаб
    d.route(fin["SAS-FM"], T(0.5), SAP, B(0.2), "RFC / CSV")
    d.route(SAP, B(0.8), fin["FC"], T(0.5), "CSV (ЕКП)")
    d.route(fin["Нацбанк"], L(0.5), SAP, B(0.15), "XML")
    d.route(SAP, B(0.25), fin["Platts.com"], L(0.5), "API")
    d.route(SAP, B(0.35), fin["1С (зарплата)"], L(0.5), "CSV")
    d.route(SAP, B(0.55), fin["БВУ"], R(0.5), "MT940/103", bidir=True)
    d.route(SAP, B(0.65), fin["ИС ЭСФ"], R(0.5), "XML", bidir=True)
    d.route(SAP, B(0.45), fin["СИЗ"], R(0.5), "XLSX")
    d.route(sap["AVR"], L(0.5), SAP, R(0.5), "API XML", bidir=True)
    d.route(UTO, B(0.5), SAP, B(0.5), "SOAP XML", bidir=True)
    d.route(doc["Электронный архив\nDocumentum / Азия-Софт"], L(0.5), SAP, B(0.6), "API", bidir=True)
    d.route(SAP, L(0.5), nsi["АСУ НСИ"], R(0.5), "SAP PO / XML", bidir=True)

    d.route(hr["ПК «Управление\nперсоналом»"], L(0.5), SAP, B(0.9), "SOAP", bidir=True)
    d.route(hr["ПК «Управление\nперсоналом»"], L(0.5), doc["Электронный архив\nDocumentum / Азия-Софт"], R(0.5), "CMIS XML")

    d.route(corp["Procu / Price"], B(0.5), nsi["АСУ НСИ"], T(0.5), "API JSON", bidir=True)
    d.route(corp["Procu / Price"], B(0.5), nsi["ИСЭЗ"], T(0.5), "API JSON", bidir=True)
    d.route(corp["sPoint"], B(0.5), nsi["КХД АО НК КМГ"], T(0.3), "API JSON")
    d.route(SAPFIR, B(0.5), nsi["КХД АО НК КМГ"], T(0.6), "REST JSON")
    d.route(corp["Argus Pro"], L(0.5), UTO, B(0.5), "REST JSON")

    d.route(sec["MS Exchange"], L(0.5), sec["Solar Dozor (DLP)"], R(0.5), "BCC", dashed=True)
    d.route(sec["Forcepoint Web GW"], B(0.5), sec["Solar Dozor (DLP)"], R(0.8), "ICAP", dashed=True)

    ldap_targets = [
        ("СЭД Directum /\nСАПФИР", 0.2, True),
        ("ИСОТ / ЭНД", 0.35, False),
        ("СДД", 0.5, False),
        ("Procu / Price", 0.62, False),
        ("Портал Team", 0.75, False),
        ("Интранет", 0.85, False),
        ("Compliance", 0.92, False),
        ("КГИС", 0.98, False),
    ]
    for lbl, ey, show_ldap in ldap_targets:
        d.route(corp[lbl], R(0.5), AD, L(ey), "LDAP" if show_ldap else "", ldap=True)
    d.route(doc["Alfresco (ЭА)"], R(0.5), AD, L(0.45), "LDAP", ldap=True)
    d.route(sec["Solar Dozor (DLP)"], T(0.5), AD, B(0.3), "LDAP", ldap=True)
    d.route(sec["FUDO PAM"], T(0.5), AD, B(0.55), "LDAP", ldap=True)
    d.route(sec["Жулдыз"], T(0.5), AD, B(0.75), "", ldap=True)
    d.route(hr["E-Pass"], T(0.5), AD, B(0.9), "LDAP", ldap=True)

    # Легенда
    legend = make_obj(
        value="Легенда",
        position=(40, 1260),
        width=1100,
        height=100,
        baseStyle=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#999999;"
            "verticalAlign=top;align=left;fontStyle=1;spacingLeft=10;spacingTop=6;"
        ),
    )
    d._add(legend, 40, 1260, 1100, 100)
    for i, (label, fill, stroke) in enumerate([
        ("Корпоративная сеть ЭМГ", "#E8F5E9", "#2E7D32"),
        ("Корпоративная сеть КМГ", "#E3F2FD", "#1565C0"),
        ("Промышленный контур (OT)", "#FFE6CC", "#D79B00"),
        ("Интеграция между сетями", EDGE_SOLID, EDGE_SOLID),
    ]):
        sx = 56 + i * 260
        d._add(
            make_obj(value="", position=(sx, 1298), width=28, height=18,
                     baseStyle=f"rounded=0;fillColor={fill};strokeColor={stroke};"),
            sx, 1298, 28, 18,
        )
        d._add(
            make_obj(value=label, position=(sx + 34, 1296), width=210, height=22,
                     baseStyle="text;html=1;align=left;fontSize=10;"),
            sx + 34, 1296, 210, 22,
        )

    note = make_obj(
        value=(
            "Сплошная линия — синхронный поток (протокол/формат на ребре).\n"
            "Фиолетовый пунктир — асинхронные/служебные потоки.\n"
            "Серый пунктир — LDAP через Active Directory.\n"
            "Детализация ИС ABAI (приложение, Airflow, Kafka, Spark): см. 05-abai-layers, 03-abai-im-architecture."
        ),
        position=(1180, 1260),
        width=1136,
        height=100,
        baseStyle="text;html=1;align=left;verticalAlign=top;fontSize=10;fontColor=#5A5A5A;spacingLeft=8;spacingTop=8;",
    )
    d._add(note, 1180, 1260, 1136, 100)

    title = make_obj(
        value="Общая архитектурная схема КМГ и ЭМГ",
        position=(40, 0),
        width=600,
        height=22,
        baseStyle="text;html=1;fontStyle=1;fontSize=16;fontColor=#23364B;",
    )
    d._add(title, 40, 0, 600, 22)

    return f, d


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    f, diagram = build()
    out = f.write(overwrite=True)
    print(f"OK {DRAWIO_NAME} -> {out}")
    render_svg(diagram, SVG_DIR / SVG_NAME)


if __name__ == "__main__":
    main()
