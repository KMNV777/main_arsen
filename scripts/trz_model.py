#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Модель ТРЗ и FTE по ролям релизного цикла ЕАРМ.

Часы на шаг заданы как  H = (F + S × N) × k,  где
  F — фиксированная часть на релиз (не зависит от числа сервисов),
  S — часть на каждый сервис,
  N — число сервисов релиза,
  k — вероятность выполнения шага (1; для ПСИ ИБ — доля релизов, где он нужен).

ВАЖНО: значения F и S — СТАРТОВЫЕ ЭКСПЕРТНЫЕ ДОПУЩЕНИЯ, а не факт. Они нужны, чтобы модель считалась
уже сейчас; после 1–2 релизов по списаниям в задачах шагов (Jira) их заменяют фактом.
Методика расчёта FTE — по «Менеджменту команд»: FTE = ТРЗ роли за период / (рабочие часы периода × плановая загрузка 80 %).
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import process_data as D

# --- параметры (значения по умолчанию) ---------------------------------------
PARAMS = {
    "N": (10, "Число сервисов в релизе (список сервисов пока не задан — подставить)"),
    "R": (12, "Плановых релизов в год (Политика: до 3 в квартал)"),
    "HF": (4, "Hotfix в год (допущение)"),
    "HF_F": (0.5, "Доля фиксированной части шага для hotfix (допущение); сервисная часть — на 1 сервис"),
    "P_PSI": (0.5, "Доля релизов, где нужен ПСИ (допущение)"),
    "H_DAY": (8, "Рабочих часов в день"),
    "D_YEAR": (247, "Рабочих дней в году (уточнить по производственному календарю)"),
    "LOAD": (0.8, "Плановая загрузка роли (Менеджмент команд: 80 %)"),
}

# (этап, роль, F, S, коэффициент: "1" | "psi")  — этап задан ключом из process_data.ID
_H = [
    ("prior", "ВНП", 2, 0.25, "1"),
    ("plan", "РП", 4, 0.5, "1"), ("plan", "DEV", 0, 1, "1"), ("plan", "QA", 0, 0.5, "1"),
    ("ticket", "RO", 6, 0.25, "1"), ("ticket", "РП", 1, 0, "1"),
    ("confirm", "ВНП", 2, 0.5, "1"),
    ("dev", "DEV", 0, 8, "1"),
    ("scan", "DEV", 0, 2, "1"),
    ("test", "QA", 8, 8, "1"), ("test", "DEV", 0, 2, "1"),
    ("notes", "ТПИ", 4, 0, "1"), ("notes", "РП", 1, 0, "1"),
    ("demo", "QA", 2, 0.5, "1"), ("demo", "ВНП", 0, 1.5, "1"),
    ("exclude", "РП", 1, 0, "1"), ("exclude", "DEV", 0, 0.5, "1"),
    ("freeze", "РИ", 2, 0.25, "1"), ("freeze", "DEV", 0, 0.5, "1"),
    ("regress", "QA", 8, 12, "1"),
    ("gate", "РИ", 3, 0.25, "1"),
    ("toml", "RO", 4, 0, "1"), ("toml", "ARCH", 2, 0, "1"),
    ("testplan", "QA", 3, 0.5, "1"), ("testplan", "RO", 3, 0, "1"),
    ("fix", "DEV", 0, 8, "1"), ("fix", "РП", 2, 0, "1"),
    ("smoke", "QA", 4, 2, "1"),
    ("init", "РИ", 2, 0.25, "1"),
    ("audit", "ИБ", 8, 1, "1"),
    ("uatdeploy", "DEVOPS", 1, 0.25, "1"),
    ("functest", "DEVOPS", 1, 0.25, "1"),
    ("psi", "ИБ", 8, 0, "psi"), ("psi", "РИ", 3, 0, "psi"),
    ("transfer", "ИБ", 3, 0.25, "1"),
    ("notify", "РИ", 1, 0, "1"),
    ("preprod", "DEVOPS", 4, 0.5, "1"),
    ("db", "АБД", 2, 0.5, "1"),
    ("brokers", "АБР", 2, 0.5, "1"),
    ("pregress", "SVC", 8, 4, "1"),
    ("preport", "SVC", 3, 0, "1"),
    ("orgnotify", "RO", 2, 0, "1"), ("orgnotify", "PMM", 1, 0, "1"),
    ("prod", "REL", 4, 0.25, "1"), ("prod", "RO", 1, 0, "1"),
    ("smokeprod", "SVC", 4, 0.5, "1"),
    ("dbpost", "АБД", 2, 0.25, "1"),
    ("brpost", "АБР", 2, 0.25, "1"),
    ("comm", "ВНП", 3, 0, "1"), ("comm", "PMM", 1, 0, "1"),
    ("close", "RO", 2, 0, "1"), ("close", "СМ", 2, 0, "1"), ("close", "АП", 2, 0.25, "1"),
]
HOURS: List[Tuple[int, str, float, float, str]] = [(D.ID[k], r, f, s, c) for k, r, f, s, c in _H]

ROLE_ORDER = ["ВНП", "РП", "RO", "РИ", "DEV", "DEVOPS", "QA", "ARCH", "PMM", "ИБ", "REL", "SVC", "АБД", "АБР", "СМ", "АП", "ТПИ"]
ROLE_NAME = {c: D.ROLES[c][0] for c in ROLE_ORDER}
CURRENT_FTE = 1.0  # сейчас каждая роль списывается на проект на 1 FTE


def k_of(code: str, p: Dict[str, float]) -> float:
    return {"1": 1.0, "psi": p["P_PSI"]}[code]


def compute(**over) -> Dict[str, Dict[str, float]]:
    """Часы и FTE по ролям. Возвращает {роль: {...}}."""
    p = {k: v[0] for k, v in PARAMS.items()}
    p.update(over)
    out: Dict[str, Dict[str, float]] = {r: {"F": 0.0, "S": 0.0} for r in ROLE_ORDER}
    for sid, role, f, s, code in HOURS:
        k = k_of(code, p)
        out[role]["F"] += f * k
        out[role]["S"] += s * k
    avail = p["H_DAY"] * p["D_YEAR"] * p["LOAD"]
    for r, d in out.items():
        rel = d["F"] + d["S"] * p["N"]                       # часов на релиз
        hf = d["F"] * p["HF_F"] + d["S"] * 1                 # часов на hotfix
        d["per_release"] = rel
        d["per_year"] = rel * p["R"] + hf * p["HF"]
        d["fte"] = d["per_year"] / avail
        d["delta"] = CURRENT_FTE - d["fte"]
    return out


def totals(res: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    return {"per_release": sum(d["per_release"] for d in res.values()),
            "per_year": sum(d["per_year"] for d in res.values()),
            "fte": sum(d["fte"] for d in res.values()),
            "current": CURRENT_FTE * len(res)}


if __name__ == "__main__":
    for n in (5, 10, 15, 20):
        r = compute(N=n)
        t = totals(r)
        print(n, {k: round(v["fte"], 2) for k, v in r.items()}, round(t["fte"], 2), "of", t["current"])
