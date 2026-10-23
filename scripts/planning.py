#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Календарь релизов (стратегическое планирование) и нагрузка ролей по неделям.

Каденс — как в «Менеджменте команд»: квартал = 6 спринтов по 2 недели, релизов 3 (релизные спринты 2, 4, 6).
Ветка релиза собирается в первый день релизного спринта (этап 3), поэтому этапы 1–2 стартуют за 3 рабочих дня до него.
Длительности этапов — из process_data.schedule(); часы ролей — из trz_model.HOURS.
Производственный календарь ориентировочный (уточнить).
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Dict, List

import process_data as D
import trz_model as T

TODAY = date(2026, 10, 21)
SPRINT0 = date(2026, 10, 5)                      # начало спринта 1 квартала IV 2026
SPRINT_DAYS = 14
QUARTERS = [("IV кв. 2026", "26.4", 0), ("I кв. 2027", "27.1", 7), ("II кв. 2027", "27.2", 13), ("III кв. 2027", "27.3", 19)]  # (подпись, код, индекс первого спринта)
RELEASE_SPRINTS = (2, 4, 6)                      # номера релизных спринтов квартала
PSI_EVERY = 2                                    # ПСИ ИБ закладывается в каждый второй релиз (допущение)
HOLIDAYS = {date(2026, 11, 4), date(2026, 12, 31), date(2027, 2, 23), date(2027, 3, 8), date(2027, 5, 3), date(2027, 5, 10), date(2027, 6, 14)} | \
    {date(2027, 1, d) for d in range(1, 9)}
MONTHS = ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
MONTHS_FULL = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]


def is_wd(d: date) -> bool:
    return d.weekday() < 5 and d not in HOLIDAYS


def add_wd(d: date, n: int) -> date:
    step = 1 if n >= 0 else -1
    while n:
        d += timedelta(days=step)
        if is_wd(d):
            n -= step
    return d


def fmt(d: date) -> str:
    return f"{d.day} {MONTHS[d.month - 1]}"


def sprint_start(idx: int) -> date:
    return SPRINT0 + timedelta(days=SPRINT_DAYS * idx)


PREP = int(D.schedule(False)[D.ID["dev"]][0])          # рабочих дней планирования до старта спринта
SPRINT_WD = 10
PSI = D.ID["psi"]
PHASE_STEPS = {p: [s[0] for s in D.STEPS if s[1] == p] for p in D.PHASES}


def releases() -> List[dict]:
    out: List[dict] = []
    k_all = 0
    for qi, (qname, code, n0) in enumerate(QUARTERS):
        for k, spr in enumerate(RELEASE_SPRINTS, 1):
            k_all += 1
            idx = n0 + spr - 1
            s0 = sprint_start(idx)
            day0 = s0
            while not is_wd(day0):
                day0 += timedelta(days=1)
            day0 = add_wd(day0, -PREP)
            psi = k_all % PSI_EVERY == 0
            sch = D.schedule(psi)
            cols = [add_wd(day0, c) for c in range(int(max(v[1] for v in sch.values())) + 1)]
            steps = []
            for n, (a, b) in sch.items():
                if b > a:
                    c0, c1 = int(a), int(b) - 1
                else:                       # этап без длительности — один день, последний день предыдущего этапа
                    c0 = c1 = max(int(a) - 1, 0)
                c0 = min(c0, len(cols) - 1)
                c1 = min(max(c1, c0), len(cols) - 1)
                steps.append({"n": n, "c0": c0, "c1": c1, "s": cols[c0].isoformat(), "e": cols[c1].isoformat(), "a": a, "b": b})
            phases = {}
            for p, ns in PHASE_STEPS.items():
                st = [x for x in steps if x["n"] in ns and not (x["n"] == PSI and not psi)]
                phases[p] = (date.fromisoformat(min(x["s"] for x in st)), date.fromisoformat(max(x["e"] for x in st)))
            end = max(v[1] for v in phases.values())
            pdays = {}
            for p_, ns_ in PHASE_STEPS.items():
                ss = [sch[n_] for n_ in ns_ if not (n_ == PSI and not psi)]
                pdays[p_] = int(round(max(b_ for a_, b_ in ss) - min(a_ for a_, b_ in ss)))
            out.append({"name": f"EARM{code}.{k}", "q": qname, "k": k, "psi": psi, "sprint": (add_wd(day0, PREP), add_wd(day0, PREP + SPRINT_WD - 1)), "day0": day0,
                        "freeze": add_wd(day0, PREP + SPRINT_WD - 1), "code_freeze": date.fromisoformat(next(x for x in steps if x["n"] == D.ID["fix"])["e"]),
                        "audit": (date.fromisoformat(next(x for x in steps if x["n"] == D.ID["audit"])["s"]), date.fromisoformat(next(x for x in steps if x["n"] == D.ID["audit"])["e"])),
                        "transfer": date.fromisoformat(next(x for x in steps if x["n"] == D.ID["transfer"])["e"]),
                        "preprod": date.fromisoformat(next(x for x in steps if x["n"] == D.ID["preprod"])["s"]),
                        "prod": date.fromisoformat(next(x for x in steps if x["n"] == D.ID["prod"])["s"]),
                        "close": end, "phases": phases, "pdays": pdays, "steps": steps, "cols": [c.isoformat() for c in cols]})
    for r in out:
        r["status"] = "ВЫПОЛНЕНО" if r["close"] < TODAY else ("В РАБОТЕ" if r["day0"] <= TODAY else "ПЛАН")
    return out


def monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def weekly_load(rels: List[dict] | None = None, n_services: int | None = None) -> Dict[str, Dict[date, float]]:
    """Часы по ролям и неделям: часы шага (F + S×N) × k равномерно по рабочим дням шага."""
    rels = rels or releases()
    n = n_services if n_services is not None else T.PARAMS["N"][0]
    out: Dict[str, Dict[date, float]] = defaultdict(lambda: defaultdict(float))
    for r in rels:
        cols = [date.fromisoformat(c) for c in r["cols"]]
        by = {x["n"]: x for x in r["steps"]}
        for sid, role, f, s, code in T.HOURS:
            if code == "psi" and not r["psi"]:
                continue
            x = by[sid]
            hours = f + s * n
            span = cols[x["c0"]: max(x["c0"], x["c1"]) + 1]
            for d in span:
                out[role][monday(d)] += hours / len(span)
    return out


def calendar_rows(rels: List[dict] | None = None) -> List[List[str]]:
    rels = rels or releases()
    return [[r["name"], fmt(r["day0"]), f"{fmt(r['sprint'][0])} – {fmt(r['sprint'][1])}", fmt(r["freeze"]), fmt(r["code_freeze"]),
             f"{fmt(r['audit'][0])} – {fmt(r['audit'][1])}", fmt(r["transfer"]), fmt(r["preprod"]), fmt(r["prod"]), fmt(r["close"]),
             "да" if r["psi"] else "нет"] for r in rels]


def max_parallel(rels: List[dict] | None = None) -> int:
    rels = rels or releases()
    best = 0
    d = min(r["day0"] for r in rels)
    end = max(r["close"] for r in rels)
    while d <= end:
        best = max(best, sum(1 for r in rels if r["day0"] <= d <= r["close"]))
        d += timedelta(days=1)
    return best


if __name__ == "__main__":
    rs = releases()
    for row in calendar_rows(rs):
        print(row)
    print("parallel", max_parallel(rs))
    w = weekly_load(rs)
    for role in ("РИ", "ИБ", "QA", "DEV"):
        print(role, round(max(w[role].values()), 1))


def days_txt(n: int) -> str:
    if n in D.IN_SPRINT:
        return "10"
    if n == PSI:
        return "0 / 5"
    return f"{D.dur(n, False):g}"


def stage_matrix(rels: List[dict] | None = None) -> List[List[str]]:
    """Строки: № | этап | дней | ответственный | по релизам «с – по»."""
    rels = rels or releases()
    rows = []
    for n in D.SN:
        row = [str(n), D.STEP_NAME[n], days_txt(n), D.role_short(D.SN[n][3])]
        for r in rels:
            x = next(x for x in r["steps"] if x["n"] == n)
            if n == PSI and not r["psi"]:
                row.append("не нужен")
                continue
            a, b = date.fromisoformat(x["s"]), date.fromisoformat(x["e"])
            row.append(fmt(a) if a == b else f"{fmt(a)} – {fmt(b)}")
        rows.append(row)
    return rows


def weekly_split(rels: List[dict] | None = None):
    """Недельные часы ролей: постоянная часть F и часть на один сервис S (часы = F + S×N)."""
    rels = rels or releases()
    f = weekly_load(rels, 0)
    fs = weekly_load(rels, 1)
    s = {role: {w: fs[role][w] - f[role].get(w, 0.0) for w in fs[role]} for role in fs}
    return f, s


def ib_overlaps(rels: List[dict] | None = None) -> int:
    """Число пар релизов, у которых окна ИБ (аудит → согласование трансфера) пересекаются."""
    rels = rels or releases()
    n = 0
    for i in range(len(rels)):
        for j in range(i + 1, len(rels)):
            a = (rels[i]["audit"][0], rels[i]["transfer"])
            b = (rels[j]["audit"][0], rels[j]["transfer"])
            if a[0] <= b[1] and b[0] <= a[1]:
                n += 1
    return n


def sprint_overlaps(rels: List[dict] | None = None) -> int:
    rels = rels or releases()
    return sum(1 for i in range(len(rels)) for j in range(i + 1, len(rels))
               if rels[i]["sprint"][0] <= rels[j]["sprint"][1] and rels[j]["sprint"][0] <= rels[i]["sprint"][1])
