#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Excel-модель ТРЗ и FTE по ролям релизного цикла (docs/release-trz-fte.xlsx).

Все расчёты — живыми формулами: меняйте жёлтые ячейки (параметры, часы F и S по шагам, ставки), остальное пересчитается.
Данные берутся из scripts/trz_model.py (стартовые допущения, заменить фактом из Jira).
"""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName

import process_data as D
import trz_model as T

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "release-trz-fte.xlsx"

THIN = Side(style="thin", color="BBBBBB")
BOR = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HFILL = PatternFill("solid", fgColor="140093")
HFONT = Font(bold=True, color="FFFFFF")
INP = PatternFill("solid", fgColor="FFE4CC")
SUB = PatternFill("solid", fgColor="E4E1F7")
TOT = PatternFill("solid", fgColor="EAFAB8")


def hdr(ws, row, titles, widths=None):
    for i, t in enumerate(titles, 1):
        c = ws.cell(row=row, column=i, value=t)
        c.fill, c.font, c.border = HFILL, HFONT, BOR
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 34
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w


def box(ws, r1, r2, c2, wrap=True):
    for r in range(r1, r2 + 1):
        for c in range(1, c2 + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = BOR
            cell.alignment = Alignment(vertical="top", wrap_text=wrap)


def main() -> None:
    wb = Workbook()

    # ---- Параметры ---------------------------------------------------------
    ws = wb.active
    ws.title = "Параметры"
    hdr(ws, 1, ["Параметр", "Значение", "Комментарий"], [38, 14, 90])
    names = {"N": "N_SVC", "R": "REL_YEAR", "HF": "HF_YEAR", "HF_F": "HF_F", "P_PSI": "P_PSI", 
             "H_DAY": "H_DAY", "D_YEAR": "D_YEAR", "LOAD": "LOAD"}
    labels = {"N": "Число сервисов в релизе (N)", "R": "Плановых релизов в год", "HF": "Hotfix в год",
              "HF_F": "Доля фиксированной части для hotfix", "P_PSI": "Доля релизов с ПСИ", 
              "H_DAY": "Рабочих часов в день", "D_YEAR": "Рабочих дней в году", "LOAD": "Плановая загрузка роли"}
    r = 2
    for k, (v, note) in T.PARAMS.items():
        ws.cell(r, 1, labels[k])
        c = ws.cell(r, 2, v)
        c.fill = INP
        ws.cell(r, 3, note)
        wb.defined_names[names[k]] = DefinedName(names[k], attr_text=f"'Параметры'!$B${r}")
        r += 1
    ws.cell(r, 1, "Часов на 1 FTE в год с учётом загрузки")
    ws.cell(r, 2, "=H_DAY*D_YEAR*LOAD").fill = TOT
    ws.cell(r, 3, "Знаменатель FTE = рабочие часы года × плановая загрузка (80 % по «Менеджменту команд»)")
    wb.defined_names["H_FTE"] = DefinedName("H_FTE", attr_text=f"'Параметры'!$B${r}")
    ws.cell(r + 1, 1, "Часов в году на 1 FTE (полная занятость)")
    ws.cell(r + 1, 2, "=H_DAY*D_YEAR").fill = TOT
    ws.cell(r + 1, 3, "Используется для стоимости текущего списания «1 FTE на проект»")
    wb.defined_names["H_FULL"] = DefinedName("H_FULL", attr_text=f"'Параметры'!$B${r + 1}")
    box(ws, 2, r + 1, 3)
    ws.cell(r + 3, 1, "Жёлтые ячейки — входные данные. Часы по шагам — стартовые экспертные допущения: заменить фактом списаний по задачам шагов в Jira.").font = Font(italic=True)

    # ---- ТРЗ по шагам --------------------------------------------------------
    st = wb.create_sheet("ТРЗ по шагам")
    hdr(st, 1, ["ID шага", "Шаг", "Роль (код)", "Роль", "F: часов на релиз (фикс.)", "S: часов на 1 сервис", "Условие (1 / psi)",
                "k (вероятность)", "Часов на релиз", "Часов на hotfix", "Часов в год"],
        [9, 46, 10, 34, 14, 14, 12, 11, 12, 12, 12])
    name = D.STEP_NAME
    row = 2
    for sid, role, f, s, code in T.HOURS:
        st.cell(row, 1, sid)
        st.cell(row, 2, name[sid])
        st.cell(row, 3, role)
        st.cell(row, 4, T.ROLE_NAME[role])
        for col, val in ((5, f), (6, s), (7, code)):
            st.cell(row, col, val).fill = INP
        st.cell(row, 8, f'=IF(G{row}="psi",P_PSI,1)')
        st.cell(row, 9, f"=(E{row}+F{row}*N_SVC)*H{row}")
        st.cell(row, 10, f"=(E{row}*HF_F+F{row})*H{row}")
        st.cell(row, 11, f"=I{row}*REL_YEAR+J{row}*HF_YEAR")
        row += 1
    last = row - 1
    st.cell(row, 2, "Итого").font = Font(bold=True)
    for col in (9, 10, 11):
        L = get_column_letter(col)
        c = st.cell(row, col, f"=SUM({L}2:{L}{last})")
        c.fill, c.font = TOT, Font(bold=True)
    box(st, 2, row, 11)
    st.freeze_panes = "A2"
    for col in (8, 9, 10, 11):
        for rr in range(2, row + 1):
            st.cell(rr, col).number_format = "0.0" if col != 8 else "0.00"

    # ---- FTE по ролям ----------------------------------------------------------
    fr = wb.create_sheet("FTE по ролям")
    hdr(fr, 1, ["Роль (код)", "Роль", "Часов на релиз", "Часов в год", "FTE по ТРЗ", "Сейчас на проекте, FTE", "Разница (сейчас − по ТРЗ)",
                "Ставка, ₽/ч", "Стоимость ТРЗ в год, ₽", "Стоимость текущего списания в год, ₽", "Разница, ₽ в год"],
        [10, 38, 13, 13, 12, 14, 16, 12, 18, 20, 16])
    n = len(T.ROLE_ORDER)
    for i, role in enumerate(T.ROLE_ORDER, 2):
        fr.cell(i, 1, role)
        fr.cell(i, 2, T.ROLE_NAME[role])
        fr.cell(i, 3, f"=SUMIFS('ТРЗ по шагам'!$I$2:$I${last},'ТРЗ по шагам'!$C$2:$C${last},A{i})")
        fr.cell(i, 4, f"=SUMIFS('ТРЗ по шагам'!$K$2:$K${last},'ТРЗ по шагам'!$C$2:$C${last},A{i})")
        fr.cell(i, 5, f"=D{i}/H_FTE")
        fr.cell(i, 6, T.CURRENT_FTE).fill = INP
        fr.cell(i, 7, f"=F{i}-E{i}")
        fr.cell(i, 8).fill = INP
        fr.cell(i, 9, f'=IF(H{i}="","",D{i}*H{i})')
        fr.cell(i, 10, f'=IF(H{i}="","",F{i}*H_FULL*H{i})')
        fr.cell(i, 11, f'=IF(H{i}="","",J{i}-I{i})')
    t = n + 2
    fr.cell(t, 2, "Итого").font = Font(bold=True)
    for col in (3, 4, 5, 6, 7, 9, 10, 11):
        L = get_column_letter(col)
        c = fr.cell(t, col, f"=SUM({L}2:{L}{t - 1})")
        c.fill, c.font = TOT, Font(bold=True)
    box(fr, 2, t, 11)
    for rr in range(2, t + 1):
        for col in (3, 4):
            fr.cell(rr, col).number_format = "0"
        for col in (5, 6, 7):
            fr.cell(rr, col).number_format = "0.00"
        for col in (9, 10, 11):
            fr.cell(rr, col).number_format = "#,##0"
    fr.cell(t + 2, 1, "Ставка (₽/ч) — вводится по каждой роли; без неё стоимость не считается. Разница > 0 означает, что на проект списывается больше, чем нужно по ТРЗ.").font = Font(italic=True)
    fr.freeze_panes = "C2"

    # ---- Сценарии по числу сервисов ------------------------------------------------
    sc = wb.create_sheet("Сценарии N")
    ns = [5, 10, 15, 20, 25]
    hdr(sc, 1, ["Роль (код)", "Роль"] + [f"N = {x}" for x in ns], [10, 38] + [12] * len(ns))
    sc.cell(2, 1, "Число сервисов →").font = Font(italic=True)
    for j, x in enumerate(ns, 3):
        sc.cell(2, j, x).fill = INP
    rng = lambda col: f"'ТРЗ по шагам'!${col}$2:${col}${last}"
    for i, role in enumerate(T.ROLE_ORDER, 3):
        sc.cell(i, 1, role)
        sc.cell(i, 2, T.ROLE_NAME[role])
        sumF = f"SUMPRODUCT(({rng('C')}=$A{i})*{rng('E')}*{rng('H')})"
        sumS = f"SUMPRODUCT(({rng('C')}=$A{i})*{rng('F')}*{rng('H')})"
        for j in range(3, 3 + len(ns)):
            L = get_column_letter(j)
            sc.cell(i, j, f"=(({sumF}+{sumS}*{L}$2)*REL_YEAR+({sumF}*HF_F+{sumS})*HF_YEAR)/H_FTE").number_format = "0.00"
    tt = len(T.ROLE_ORDER) + 3
    sc.cell(tt, 2, "Итого FTE по ТРЗ").font = Font(bold=True)
    sc.cell(tt + 1, 2, "Сейчас (1 FTE × число ролей)").font = Font(bold=True)
    for j in range(3, 3 + len(ns)):
        L = get_column_letter(j)
        c = sc.cell(tt, j, f"=SUM({L}3:{L}{tt - 1})")
        c.fill, c.number_format = TOT, "0.00"
        c2 = sc.cell(tt + 1, j, f"={len(T.ROLE_ORDER)}*{T.CURRENT_FTE}")
        c2.fill, c2.number_format = TOT, "0.00"
    box(sc, 3, tt + 1, 2 + len(ns))

    # ---- Методика -----------------------------------------------------------------------
    me = wb.create_sheet("Методика")
    me.column_dimensions["A"].width = 130
    lines = [
        "Методика расчёта ТРЗ и FTE по ролям релизного цикла",
        "",
        "1. Единица учёта — шаг релизного цикла (см. реестр шагов процесса). Каждый шаг — задача Jira с оценкой и списанием времени; сумма ТРЗ задач шагов по роли = ТРЗ роли в релизе.",
        "2. Часы на шаг: H = (F + S × N) × k, где F — фиксированная часть на релиз, S — часть на каждый сервис, N — число сервисов, k — вероятность шага (ПСИ ИБ — не в каждом релизе).",
        "3. Hotfix идёт тем же процессом: H_hotfix = (F × доля_фикс + S × 1) × k; в год — HF_YEAR штук.",
        "4. FTE роли = ТРЗ роли за год / (рабочие часы года × плановая загрузка). Плановая загрузка 80 % — норма из «Менеджмента команд».",
        "5. Сейчас каждая роль списывается на проект на 1 FTE. Разница «сейчас − по ТРЗ» показывает, сколько ёмкости роли можно вернуть в продукт (или, если < 0, где ТРЗ не покрыто списанием).",
        "6. Экономика: стоимость ТРЗ = часы × ставка роли; стоимость текущего списания = 1 FTE × часы года × ставка. Ставки вводятся пользователем.",
        "7. Часы F и S — стартовые экспертные допущения. После 1–2 релизов заменить фактом: ТРЗ шага = Σ списаний по задачам шага (Jira), F и S получить регрессией по числу сервисов.",
        "8. Источник факта: задачи шагов Релизного Epic (оценка и списание времени). До внедрения списания (этап 3 дорожной карты менеджмента) — оценка задач шагов.",
    ]
    for i, l in enumerate(lines, 1):
        c = me.cell(i, 1, l)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        if i == 1:
            c.font = Font(bold=True, size=13)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    _recalc(OUT)
    print("OK:", OUT)


def _recalc(path: Path) -> None:
    """Пересчитать через LibreOffice, чтобы в файле лежали значения формул (если soffice доступен)."""
    import shutil
    import subprocess
    import tempfile
    if not shutil.which("soffice"):
        return
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run(["soffice", "--headless", "--convert-to", "xlsx", "--outdir", tmp, str(path)],
                           capture_output=True, timeout=180)
        res = Path(tmp) / path.name
        if r.returncode == 0 and res.exists():
            shutil.copyfile(res, path)


if __name__ == "__main__":
    main()
