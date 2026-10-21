#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Три раздела отчёта в стиле «Менеджмент команд»: дорожная карта релизов (Jira Timeline), стратегическое планирование, экономика."""

from __future__ import annotations

import json
from datetime import date, timedelta
from html import escape as e

import planning as P
import process_data as D
import sections as S
import trz_model as T

PH_COL = {1: "#8A9BB5", 2: "#140093", 3: "#4BADE8", 4: "#904EE2", 5: "#FBAE40", 6: "#63BA3C"}
CONTOUR_COL = {"НЕДРА": "#140093", "ИБ ГПН-ЦР": "#F26B43", "ГПН-ЦР": "#00A3BF"}

CSS_PLAN = r"""
.tabs{display:flex;gap:4px;background:#F4F5F7;border-radius:9px;padding:4px;margin:6px 0 14px;flex-wrap:wrap}
.tabs button{flex:1 1 0;border:0;background:none;border-radius:7px;padding:8px 12px;font:inherit;font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#8A8A8A;cursor:pointer}
.tabs button:hover{color:#140093}.tabs button.on{background:#140093;color:#fff}
.pane{display:none}.pane.on{display:block}
.tl{background:#fff;border:1px solid var(--line);border-radius:6px;box-shadow:var(--sh-1);overflow-x:auto}
.tl-in{min-width:1100px}
.tl-row{display:grid;grid-template-columns:270px 1fr;border-bottom:1px dashed #E8ECF2}
.tl-row.h{background:#fff;border-bottom:1px solid var(--line)}
.tl-l{padding:6px 12px;font-size:12px;display:flex;align-items:center;gap:8px;border-right:1px solid var(--line);min-height:30px}
.tl-l b{font-size:13px}.tl-l .sub{color:var(--ink-3);font-size:11px}
.tl-g{background:#F5F6F8;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#6B778C;font-weight:700}
.tl-r{position:relative;min-height:30px}
.tl-r .ml{position:absolute;top:0;bottom:0;width:1px;background:#EDF0F5}
.tl-r .mt{position:absolute;top:6px;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:#6B778C;font-weight:700;padding-left:6px}
.tl-r .qt{position:absolute;top:0;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#140093;font-weight:700;padding-left:6px}
.tl-r .today{position:absolute;top:0;bottom:0;width:2px;background:#E5493A;z-index:3}
.seg{position:absolute;top:6px;height:18px;color:#fff;font-size:10px;font-weight:700;line-height:18px;padding:0 5px;white-space:nowrap;overflow:hidden;border-right:1px solid rgba(255,255,255,.5)}
.chip{display:inline-block;font-size:9px;font-weight:700;letter-spacing:.08em;padding:2px 7px;border-radius:3px;white-space:nowrap}
.chip.work{background:#DEEBFF;color:#0052CC}.chip.plan{background:#DFE1E6;color:#42526E}.chip.done{background:#E3FCEF;color:#006644}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--ink-2);margin:6px 0 12px}
.legend i{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
.rsel{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0 12px}
.rsel button{border:1px solid var(--line);background:#fff;color:#140093;border-radius:6px;padding:5px 10px;font:inherit;font-size:12px;font-weight:700;cursor:pointer}
.rsel button.on{background:#140093;color:#fff;border-color:#140093}
.gt{overflow:auto;background:#fff;border:1px solid var(--line);border-radius:6px;box-shadow:var(--sh-1);max-height:80vh}
.gt table{border-collapse:separate;border-spacing:0;font-size:12px;width:auto}
.gt th,.gt td{padding:0;border:0;border-bottom:1px solid #F0F2F6}
.gt thead th{position:sticky;top:0;z-index:2;background:#fff;color:#6B778C;font-size:9px;letter-spacing:.04em;text-transform:none;text-align:center;border-bottom:1px solid var(--line);height:34px;min-width:17px;max-width:17px}
.gt thead th.wk{border-left:1px solid var(--line)}
.gt td.c{min-width:17px;max-width:17px;height:26px;position:relative}
.gt td.c.wk{border-left:1px solid #EEF1F6}
.gt td.c.hit{padding:0}.gt td.c.hit div{height:16px;margin:5px 0}
.gt td.n{position:sticky;left:0;background:#fff;z-index:1;min-width:300px;max-width:300px;padding:4px 10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-right:1px solid var(--line)}
.gt thead th.n{left:0;z-index:3;text-align:left;font-size:10px;letter-spacing:.1em;text-transform:uppercase;padding-left:10px}
.gt td.who{min-width:150px;max-width:150px;padding:4px 8px;font-size:11px;color:#42526E;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-right:1px solid var(--line)}
.gt tr.ph td.n,.gt tr.ph td.who{background:#EEEDF8;color:#140093;font-weight:700;font-size:10px;letter-spacing:.1em;text-transform:uppercase}
.gt tr.ph td.c{background:#EEEDF8}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:10px 0 16px}
.kpi{background:#fff;border:1px solid var(--line);border-radius:6px;padding:14px 16px;box-shadow:var(--sh-1)}
.kpi b{display:block;font-size:30px;color:#140093;line-height:1.05;letter-spacing:-.02em}
.kpi span{display:block;font-size:13px;font-weight:700;margin:4px 0 2px}.kpi small{color:var(--ink-2);font-size:12px}
.kpi.ok b{color:#006644}.kpi.bad b{color:#E5493A}.kpi.warn b{color:#D97706}
.heat{overflow:auto;background:#fff;border:1px solid var(--line);border-radius:6px;box-shadow:var(--sh-1);padding:10px 12px}
.heat table{border-collapse:separate;border-spacing:2px;width:auto;font-size:11px}
.heat th,.heat td{border:0;padding:0;background:none;color:inherit;text-transform:none;letter-spacing:0;position:static}
.heat td.r{padding:0 10px 0 0;white-space:nowrap;min-width:150px;color:#42526E}
.heat td.h{width:15px;height:20px;border-radius:2px;background:#EEF1F6}
.heat th{font-size:9px;color:#6B778C;font-weight:700;text-align:left;white-space:nowrap;padding-bottom:3px}
.h0{background:#EEF1F6!important}.h1{background:#D7F3B0!important}.h2{background:#8ED15A!important}.h3{background:#FBAE40!important}.h4{background:#F26B43!important}
.econ-g{display:grid;grid-template-columns:1fr;gap:14px}.econ-g>.card{max-width:780px}
@media(max-width:1000px){.econ-g{grid-template-columns:1fr}}
.verdict{border-left:4px solid #140093;background:#EEEDF8;border-radius:0 6px 6px 0;padding:12px 16px;margin:10px 0;font-size:14px}
.st{display:inline-block;padding:1px 8px;border-radius:9px;font-size:11px;font-weight:700}
.st.sur{background:#E3FCEF;color:#006644}.st.def{background:#FDE4DC;color:#B3260E}.st.okk{background:#DEEBFF;color:#0052CC}
.calc-p.rates{grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
svg.chart text{font-family:Arial,sans-serif}
"""

JS_TABS = r"""
document.querySelectorAll('.tabs').forEach(function(t){var g=t.dataset.g;t.querySelectorAll('button').forEach(function(b){b.onclick=function(){
 t.querySelectorAll('button').forEach(function(x){x.classList.toggle('on',x===b)});
 document.querySelectorAll('.pane[data-g="'+g+'"]').forEach(function(p){p.classList.toggle('on',p.dataset.p===b.dataset.p)})}})});
"""


def _d(s: str) -> date:
    return date.fromisoformat(s)


# ---------------------------------------------------------------------------
# 1. Дорожная карта релизов
# ---------------------------------------------------------------------------
def roadmap_html(rels) -> str:
    t0, t1 = date(2026, 10, 1), date(2027, 11, 15)
    span = (t1 - t0).days
    pct = lambda d: (d - t0).days / span * 100

    months = []
    y, m = t0.year, t0.month
    while date(y, m, 1) < t1:
        months.append(date(y, m, 1))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    head = "".join(f'<div class="ml" style="left:{pct(d):.3f}%"></div><div class="mt" style="left:{pct(d):.3f}%">{P.MONTHS[d.month - 1]}{" " + str(d.year)[2:] if d.month == 1 or d == months[0] else ""}</div>' for d in months)
    qline = ""
    for qname, code, n0 in P.QUARTERS:
        qs = P.sprint_start(n0)
        qline += f'<div class="qt" style="left:{pct(qs):.3f}%;top:20px">{qname}</div>'
    today = f'<div class="today" style="left:{pct(P.TODAY):.3f}%"></div>'
    rows = [f'<div class="tl-row h"><div class="tl-l"><span class="kicker" style="margin:0">Релиз · статус</span></div><div class="tl-r" style="min-height:46px">{head}{qline}{today}</div></div>']
    last_q = None
    grid = "".join(f'<div class="ml" style="left:{pct(d):.3f}%"></div>' for d in months)
    for r in rels:
        if r["q"] != last_q:
            last_q = r["q"]
            rows.append(f'<div class="tl-row tl-g"><div class="tl-l" style="min-height:24px">{e(r["q"])} · 3 релиза</div><div class="tl-r" style="min-height:24px"></div></div>')
        segs = ""
        for p, (a, b) in r["phases"].items():
            w = pct(b + timedelta(days=1)) - pct(a)
            label = D.PHASES[p].split(" (")[0] if w > 7.5 else ""
            segs += f'<div class="seg" title="{e(D.PHASES[p])}: {P.fmt(a)} – {P.fmt(b)}" style="left:{pct(a):.3f}%;width:{w:.3f}%;background:{PH_COL[p]}">{e(label)}</div>'
        cls = {"ВЫПОЛНЕНО": "done", "В РАБОТЕ": "work", "ПЛАН": "plan"}[r["status"]]
        rows.append(f'<div class="tl-row"><div class="tl-l"><span class="chip {cls}">{r["status"]}</span><div><b>{r["name"]}</b><div class="sub">спринт {P.fmt(r["sprint"][0])} – {P.fmt(r["sprint"][1])}{" · ПСИ ИБ" if r["psi"] else ""}</div></div></div>'
                    f'<div class="tl-r">{grid}{segs}{today}</div></div>')
    year = '<div class="tl"><div class="tl-in">' + "".join(rows) + "</div></div>"
    legend = '<div class="legend">' + "".join(f'<span><i style="background:{PH_COL[p]}"></i>{e(D.PHASES[p])}</span>' for p in D.PHASES) + '<span><i style="background:#E5493A"></i>сегодня (21 окт 2026)</span></div>'

    # детализация релиза до этапа и рабочего дня
    data = []
    for r in rels:
        data.append({"name": r["name"], "psi": r["psi"], "cols": r["cols"],
                     "steps": [{"n": x["n"], "c0": x["c0"], "c1": x["c1"], "zero": x["b"] <= x["a"]} for x in r["steps"]]})
    meta = {str(n): {"t": D.STEP_NAME[n], "w": D.role_short(D.SN[n][3]), "ph": D.SN[n][1], "col": CONTOUR_COL[D.ROLES[D.SN[n][3]][1]] if D.SN[n][3] in D.ROLES else "#8A9BB5"} for n in D.SN}
    phases = {str(k): v for k, v in D.PHASES.items()}
    js = r"""
(function(){var R=__R__,M=__M__,PH=__PH__,MO=__MO__;var box=document.getElementById('gt'),sel=document.getElementById('rsel');
function f(s){var d=new Date(s);return d.getUTCDate()+' '+MO[d.getUTCMonth()]}
function draw(i){var r=R[i];sel.querySelectorAll('button').forEach(function(b,j){b.classList.toggle('on',j===i)});
 var h='<table><thead><tr><th class="n">Этап</th><th class="n" style="left:300px;min-width:150px">Ответственный</th>';
 r.cols.forEach(function(c,k){var d=new Date(c),wk=(d.getUTCDay()===1||k===0);h+='<th class="'+(wk?'wk':'')+'" title="'+f(c)+'">'+(wk?d.getUTCDate()+'<br>'+MO[d.getUTCMonth()]:'')+'</th>'});
 h+='</tr></thead><tbody>';var last=0;
 r.steps.forEach(function(s){var m=M[s.n];if(s.n===18&&!r.psi){}
  if(m.ph!==last){last=m.ph;h+='<tr class="ph"><td class="n" colspan="2">'+PH[m.ph]+'</td><td class="c" colspan="'+r.cols.length+'"></td></tr>'}
  h+='<tr><td class="n"><b>'+s.n+'.</b> '+m.t+(s.n===18&&!r.psi?' <span class="muted">(не нужен — пропуск)</span>':'')+'</td><td class="who">'+m.w+'</td>';
  r.cols.forEach(function(c,k){var d=new Date(c),wk=(d.getUTCDay()===1||k===0);var hit=k>=s.c0&&k<=s.c1&&!(s.n===18&&!r.psi);
   h+='<td class="c'+(wk?' wk':'')+(hit?' hit':'')+'">'+(hit?'<div style="background:'+m.col+';'+(k===s.c0?'border-radius:3px 0 0 3px;':'')+(k===s.c1?'border-radius:0 3px 3px 0;':'')+'" title="'+s.n+'. '+m.t+' · '+f(r.cols[s.c0])+(s.c1>s.c0?' – '+f(r.cols[s.c1]):'')+'"></div>':'')+'</td>'});
  h+='</tr>'});
 box.innerHTML=h+'</tbody></table>'}
R.forEach(function(r,i){var b=document.createElement('button');b.textContent=r.name+(r.psi?' · ПСИ':'');b.onclick=function(){draw(i)};sel.appendChild(b)});draw(0);
})();
"""
    js = (js.replace("__R__", json.dumps(data, ensure_ascii=False)).replace("__M__", json.dumps(meta, ensure_ascii=False))
          .replace("__PH__", json.dumps(phases, ensure_ascii=False)).replace("__MO__", json.dumps(P.MONTHS, ensure_ascii=False)))
    legend2 = '<div class="legend">' + "".join(f'<span><i style="background:{c}"></i>{n}</span>' for n, c in (("НЕДРА", CONTOUR_COL["НЕДРА"]), ("ИБ ГПН-ЦР", CONTOUR_COL["ИБ ГПН-ЦР"]), ("ГПН-ЦР", CONTOUR_COL["ГПН-ЦР"]))) + "<span>цвет — контур ответственного за этап</span></div>"
    return ("<p>Верхний уровень — релизы скользящего года: на каждом релизе видно, какую фазу он проходит и где пересекается с соседними. "
            "Нижний уровень раскладывает выбранный релиз до этапа, ответственной роли и рабочего дня. Даты считаются из SLA этапов и производственного календаря (ориентировочного).</p>"
            '<div class="tabs" data-g="rm"><button class="on" data-p="y">Скользящий год</button><button data-p="d">Релиз до этапа и дня</button></div>'
            f'<div class="pane on" data-g="rm" data-p="y">{legend}{year}</div>'
            f'<div class="pane" data-g="rm" data-p="d">{legend2}<div class="rsel" id="rsel"></div><div class="gt" id="gt"></div></div>'
            f"<script>{js}</script>")


# ---------------------------------------------------------------------------
# 2. Стратегическое планирование релизов
# ---------------------------------------------------------------------------
def strategy_html(rels) -> str:
    par = P.max_parallel(rels)
    ph = lambda a, b: f"{(b - a).days // 7}"
    span_w = round(D.total_days(False) / 5, 1)
    kpis = ('<div class="kpis">'
            f'<div class="kpi"><b>{len(rels)}</b><span>релизов на скользящий год</span><small>3 в квартал · релизные спринты 2, 4, 6</small></div>'
            f'<div class="kpi"><b>{par}</b><span>релиза в полёте одновременно</span><small>цикл ≈ {span_w} нед. при релизе раз в 4 недели</small></div>'
            f'<div class="kpi"><b>{D.total_days(False):g}–{D.total_days(True):g}</b><span>рабочих дней цикла</span><small>без ПСИ ИБ — с ПСИ ИБ</small></div>'
            f'<div class="kpi"><b>{sum(r["psi"] for r in rels)}</b><span>релизов с ПСИ ИБ</span><small>закладывается в каждый второй (допущение)</small></div></div>')
    principles = ('<div class="grid">'
                  '<div class="card"><b>Каденс</b>' + S.ul(["Квартал = 6 спринтов по 2 недели + буфер; релизов 3.", "Релизный спринт — 2-й, 4-й и 6-й: в его первый день собирается релизная ветка.",
                                                          "Первый спринт пары (1, 3, 5) — подготовка: подтверждение состава (ВНП) и релизный тикет (Release owner).", "Не успели — в следующий релиз, объём не растягивается."]) + "</div>"
                  '<div class="card"><b>Окно параллельности</b>' + S.ul([f"В стабилизации и релиз-борде одновременно до {par} релизов — это потолок для РИ и ИБ.", "Новый релиз не стартует, пока предыдущий не прошёл аудит кода: ИБ не получает два аудита сразу.",
                                                                       "Следующий релиз можно начинать на этапе выкатки в Прод предыдущего."]) + "</div>"
                  '<div class="card"><b>Что фиксируется на год</b>' + S.ul(["Даты релизных спринтов, фича-фриза и деплоя в Прод.", "Квартальный Релизный Epic: обязательный объём и бизнес-требования.", "Окна ИБ: аудит и ПСИ, согласование трансфера.",
                                                                          "Окна простоя и праздников: релизные работы в них не планируются."]) + "</div></div>")
    cal = S.tbl(["Релиз", "Старт (тикет)", "Спринт", "Фича-фриз", "Код-фриз", "Аудит кода", "Трансфер согласован", "PreProd", "Деплой Прод", "Закрытие", "ПСИ ИБ"], P.calendar_rows(rels))

    # нагрузка по неделям
    wl = P.weekly_load(rels)
    wk0 = P.monday(min(r["day0"] for r in rels))
    wk1 = P.monday(max(r["close"] for r in rels))
    weeks = []
    d = wk0
    while d <= wk1:
        weeks.append(d)
        d += timedelta(days=7)
    cap = 40 * T.PARAMS["LOAD"][0]
    order = ["РИ", "ИБ", "QA", "RO", "DEV", "ВНП", "DEVOPS", "SVC", "АБД", "АБР"]
    mh = "<tr><th></th>" + "".join(f'<th title="неделя с {P.fmt(w)}">{P.MONTHS[w.month - 1][:3] if w.day <= 7 else ""}</th>' for w in weeks) + "</tr>"
    body = ""
    for role in order:
        cells = ""
        for w in weeks:
            u = wl[role].get(w, 0) / cap
            c = "h0" if u < 0.05 else "h1" if u < 0.5 else "h2" if u < 1.0 else "h3" if u < 1.5 else "h4"
            cells += f'<td class="h {c}" title="{D.ROLES[role][0]}, неделя с {P.fmt(w)}: {wl[role].get(w, 0):.0f} ч, {u * 100:.0f}% от 1 FTE"></td>'
        body += f'<tr><td class="r">{e(D.ROLES[role][0].split(" (")[0])}</td>{cells}</tr>'
    legend = ('<div class="legend"><span><i class="h0" style="background:#EEF1F6"></i>&lt; 5 %</span><span><i style="background:#D7F3B0"></i>до 50 %</span><span><i style="background:#8ED15A"></i>50–100 %</span>'
              '<span><i style="background:#FBAE40"></i>100–150 %</span><span><i style="background:#F26B43"></i>&gt; 150 %</span><span>загрузка недели от 1 FTE (32 ч = 40 ч × 80 %)</span></div>')
    peaks = {r: max(wl[r].values()) / cap for r in order}
    over = [f"{D.ROLES[r][0].split(' (')[0]} — до {peaks[r] * 100:.0f} %" for r in order if peaks[r] > 1.0]
    heat = (f'<p>Нагрузка ролей по неделям года при N = {T.PARAMS["N"][0]} сервисах (часы этапов из модели ТРЗ, равномерно по рабочим дням этапа). '
            "Так видно, где пересечение релизов даёт пик и какая роль его не выдерживает.</p>" + legend +
            f'<div class="heat"><table>{mh}{body}</table></div>'
            + f'<div class="verdict"><b>Вывод по пикам.</b> Выше 100 % от 1 FTE: {e("; ".join(over)) if over else "нет"}. Мейнтейнеры и QA — пулы нескольких человек: пик показывает, сколько FTE пула нужно в эту неделю. Роли с пиками выше нормы — кандидаты на усиление или на смещение дат релизов (см. «Экономика и баланс ресурсов»).</div>')
    rules = S.ol([
        "Календарь релизов утверждается на скользящий год и пересматривается раз в квартал вместе с Релизным Epic.",
        "Старт релиза допускается, только если у РИ, ИБ и QA в окне этапов запас по загрузке (по тепловой карте); иначе релиз сдвигается на спринт.",
        "Объём релиза (число сервисов N) планируется от ёмкости: нужные часы по ролям при N не должны превышать 100 % FTE роли в пиковую неделю.",
        "ПСИ ИБ закладывается в окно до старта релиза (5 рабочих дней); релиз с ПСИ не стартует параллельно другому релизу с ПСИ.",
        "Окна без релизных работ: новогодние праздники, длительные майские праздники; релизные спринты в них не назначаются.",
        "Сдвиг релиза — решение Release owner по согласованию с ВНП; причина фиксируется в календаре и попадает в метрику «Выполнение релизов по плану».",
        "Hotfix не входит в календарь: идёт по тому же процессу вне плана и учитывается в нагрузке как резерв (по модели ТРЗ — HF в год).",
    ])
    return ("<p>Стратегическое планирование задаёт годовой календарь релизов, окна параллельных релизов и проверку ёмкости ролей до старта каждого релиза. "
            "Исходные данные — SLA этапов, зоны ответственности и часы модели ТРЗ.</p>" + kpis + principles +
            "<h3>Календарь релизов на скользящий год</h3>" + cal +
            "<h3>Загрузка ролей по неделям</h3>" + heat +
            "<h3>Правила стратегического планирования</h3>" + rules)


# ---------------------------------------------------------------------------
# 3. Экономика и баланс ресурсов
# ---------------------------------------------------------------------------
def econ_html() -> str:
    names = D.STEP_NAME
    data = {"params": {k: v[0] for k, v in T.PARAMS.items()}, "notes": {k: v[1] for k, v in T.PARAMS.items()},
            "hours": [[sid, names[sid], role, f, s, code] for sid, role, f, s, code in T.HOURS],
            "roles": [[r, T.ROLE_NAME[r]] for r in T.ROLE_ORDER], "cur": T.CURRENT_FTE}
    js = r"""
(function(){
var D=__DATA__,P=Object.assign({},D.params),H=D.hours.map(function(x){return x.slice()}),RATE={},ALLOC={},TOL=0.2;
D.roles.forEach(function(r){ALLOC[r[0]]=D.cur});
var lab={N:'Число сервисов в релизе (N)',R:'Релизов в год',HF:'Hotfix в год',HF_F:'Доля фикс. части для hotfix',P_PSI:'Доля релизов с ПСИ ИБ',H_DAY:'Часов в день',D_YEAR:'Рабочих дней в году',LOAD:'Плановая загрузка'};
function k(c){return c==='psi'?P.P_PSI:1}
function fs(){var o={};D.roles.forEach(function(r){o[r[0]]={F:0,S:0}});H.forEach(function(h){var kk=k(h[5]);o[h[2]].F+=h[3]*kk;o[h[2]].S+=h[4]*kk});return o}
function yr(o,N,R,HF){return (o.F+o.S*N)*R+(o.F*P.HF_F+o.S)*HF}
function avail(){return P.H_DAY*P.D_YEAR*P.LOAD}
function nf(x,d){return x.toLocaleString('ru-RU',{minimumFractionDigits:d||0,maximumFractionDigits:d||0})}
function calc(){var o=fs(),A=avail(),full=P.H_DAY*P.D_YEAR,rows=[],T={req:0,alloc:0,sur:0,def:0,cost:0,costReq:0,has:false,hours:0};
 D.roles.forEach(function(r){var c=o[r[0]],hrs=yr(c,P.N,P.R,P.HF),req=hrs/A,al=ALLOC[r[0]],bal=al-req,rate=parseFloat(RATE[r[0]]);
  var st=Math.abs(bal)<=TOL*al?'ok':(bal>0?'sur':'def'),has=!isNaN(rate);
  var cAl=has?al*full*rate:null,cReq=has?req*full*rate:null,cB=has?bal*full*rate:null;
  T.req+=req;T.alloc+=al;T.hours+=hrs;if(bal>0)T.sur+=bal;else T.def+=-bal;if(has){T.has=true;T.cost+=cAl;T.costReq+=cReq}
  rows.push({c:r[0],n:r[1],req:req,al:al,bal:bal,st:st,cAl:cAl,cReq:cReq,cB:cB,hrs:hrs})});
 return {rows:rows,T:T,full:full,A:A,o:o}}
var stT={ok:['okk','норма'],sur:['sur','избыток'],def:['def','нехватка']};
function chart(rows){var W=640,rowH=26,pad=170,h=rows.length*rowH+40,mx=0;rows.forEach(function(r){mx=Math.max(mx,Math.abs(r.bal))});mx=Math.max(mx,0.5);var sc=(W-pad-110)/(2*mx),mid=pad+50+mx*sc;
 var s='<svg class="chart" viewBox="0 0 '+W+' '+h+'" width="100%" role="img" aria-label="Баланс FTE по ролям"><line x1="'+mid+'" x2="'+mid+'" y1="16" y2="'+(h-14)+'" stroke="#C7D4DE"/>';
 s+='<text x="'+(mid+4)+'" y="11" font-size="10" fill="#006644" font-weight="700">избыток (списано больше, чем нужно)</text><text x="'+(mid-4)+'" y="11" font-size="10" fill="#B3260E" font-weight="700" text-anchor="end">нехватка</text>';
 rows.forEach(function(r,i){var y=22+i*rowH,w=Math.abs(r.bal)*sc,col=r.st==='ok'?'#4BADE8':(r.bal>0?'#63BA3C':'#F26B43');
  s+='<text x="'+(pad-8)+'" y="'+(y+14)+'" font-size="11" text-anchor="end" fill="#333">'+r.n.split(' (')[0].replace(/ \/.*/,'').slice(0,26)+'</text>';
  s+='<rect x="'+(r.bal>=0?mid:mid-w)+'" y="'+(y+2)+'" width="'+w+'" height="16" rx="2" fill="'+col+'"/>';
  s+='<text x="'+(r.bal>=0?mid+w+5:mid-w-5)+'" y="'+(y+14)+'" font-size="10" font-weight="700" fill="#333" text-anchor="'+(r.bal>=0?'start':'end')+'">'+(r.bal>0?'+':'')+nf(r.bal,2)+'</text>'});
 return s+'</svg>'}
function sens(o){var W=640,Hh=260,L=46,B=30,Ns=[],i;for(i=1;i<=30;i++)Ns.push(i);var Rs=[[8,'8 в год'],[12,'12 в год (3 в квартал)'],[16,'16 в год'],[26,'26 в год (каждый спринт)']],cols=['#8A9BB5','#140093','#904EE2','#F26B43'];
 function tot(N,R){var t=0;D.roles.forEach(function(r){t+=yr(o[r[0]],N,R,P.HF)/avail()});return t}
 var mx=0;Rs.forEach(function(r){mx=Math.max(mx,tot(30,r[0]))});mx=Math.ceil(mx/5)*5;
 var X=function(n){return L+(n-1)/29*(W-L-14)},Y=function(v){return Hh-B-v/mx*(Hh-B-12)};
 var s='<svg class="chart" viewBox="0 0 '+W+' '+Hh+'" width="100%" role="img" aria-label="Потребность в FTE от числа сервисов">';
 for(i=0;i<=mx;i+=5){s+='<line x1="'+L+'" x2="'+(W-14)+'" y1="'+Y(i)+'" y2="'+Y(i)+'" stroke="#EEF1F6"/><text x="'+(L-6)+'" y="'+(Y(i)+3)+'" font-size="10" text-anchor="end" fill="#6B778C">'+i+'</text>'}
 for(i=5;i<=30;i+=5){s+='<text x="'+X(i)+'" y="'+(Hh-12)+'" font-size="10" text-anchor="middle" fill="#6B778C">'+i+'</text>'}
 s+='<text x="'+(W/2)+'" y="'+(Hh-1)+'" font-size="10" text-anchor="middle" fill="#6B778C">число сервисов в релизе, N</text>';
 var cur=Y(D.roles.length*D.cur);if(D.roles.length*D.cur<=mx)s+='<line x1="'+L+'" x2="'+(W-14)+'" y1="'+cur+'" y2="'+cur+'" stroke="#E5493A" stroke-dasharray="5 4"/><text x="'+(W-16)+'" y="'+(cur-4)+'" font-size="10" fill="#E5493A" text-anchor="end">сейчас списано '+D.roles.length*D.cur+' FTE</text>';
 Rs.forEach(function(r,j){var d='';Ns.forEach(function(n,q){d+=(q?'L':'M')+X(n)+' '+Y(tot(n,r[0]))});s+='<path d="'+d+'" fill="none" stroke="'+cols[j]+'" stroke-width="2.2"/><text x="'+(X(30)-4)+'" y="'+(Y(tot(30,r[0]))-5)+'" font-size="10" fill="'+cols[j]+'" text-anchor="end" font-weight="700">'+r[1]+'</text>'});
 return s+'</svg>'}
function render(){var c=calc(),T=c.T,deficit=c.rows.filter(function(r){return r.st==='def'}),sur=c.rows.filter(function(r){return r.st==='sur'});
 var kp='<div class="kpis"><div class="kpi"><b>'+nf(T.alloc,1)+'</b><span>FTE списывается сейчас</span><small>1 FTE на каждую из '+D.roles.length+' ролей</small></div>'
 +'<div class="kpi"><b>'+nf(T.req,1)+'</b><span>FTE нужно по ТРЗ</span><small>'+nf(T.hours)+' ч в год при N = '+P.N+', '+P.R+' релизах</small></div>'
 +'<div class="kpi ok"><b>+'+nf(T.sur,1)+'</b><span>FTE избыток</span><small>'+sur.length+' ролей списано больше потребности</small></div>'
 +'<div class="kpi '+(T.def>0.05?'bad':'ok')+'"><b>'+(T.def>0.05?'−':'')+nf(T.def,1)+'</b><span>FTE нехватка</span><small>'+deficit.length+' ролей, где ТРЗ не покрыто списанием</small></div></div>';
 var verdict='<div class="verdict"><b>Вывод.</b> Списывается '+nf(T.alloc,1)+' FTE при потребности '+nf(T.req,1)+' FTE: суммарный избыток '+nf(T.sur,1)+' FTE.'
 +(deficit.length?' При этом нехватка у ролей: '+deficit.map(function(r){return r.n.split(' (')[0].replace(/ \/.*/,'')+' (−'+nf(-r.bal,2)+')'}).join('; ')+' — их ТРЗ превышает списание, нужно усилить или сократить объём (N, число релизов).':' Нехватки нет.')
 +(sur.length?' Избыток у '+sur.length+' ролей: их ёмкость (суммарно '+nf(T.sur,1)+' FTE) можно вернуть в продукт.':'')+(T.has?' Стоимость избытка при введённых ставках — '+nf((c.rows.reduce(function(a,r){return a+(r.cB>0?r.cB:0)},0)))+' ₽ в год.':' Введите ставки, чтобы увидеть стоимость.')+'</div>';
 var tr=c.rows.map(function(r){return '<tr><td>'+r.n+'</td><td><b>'+nf(r.req,2)+'</b></td><td><input class="al" type="number" step="0.1" min="0" data-r="'+r.c+'" value="'+r.al+'"></td><td><b>'+(r.bal>0?'+':'')+nf(r.bal,2)+'</b></td><td><span class="st '+stT[r.st][0]+'">'+stT[r.st][1]+'</span></td>'
  +'<td>'+(r.cAl===null?'—':nf(r.cAl))+'</td><td>'+(r.cReq===null?'—':nf(r.cReq))+'</td><td>'+(r.cB===null?'—':(r.cB>0?'+':'')+nf(r.cB))+'</td></tr>'}).join('')
  +'<tr class="tot"><td><b>Итого</b></td><td><b>'+nf(T.req,2)+'</b></td><td><b>'+nf(T.alloc,1)+'</b></td><td><b>'+(T.alloc-T.req>0?'+':'')+nf(T.alloc-T.req,2)+'</b></td><td></td><td>'+(T.has?nf(T.cost):'—')+'</td><td>'+(T.has?nf(T.costReq):'—')+'</td><td>'+(T.has?nf(T.cost-T.costReq):'—')+'</td></tr>';
 var tbl='<div class="tw"><table><thead><tr><th>Роль</th><th>Нужно по ТРЗ, FTE</th><th>Списано, FTE</th><th>Баланс, FTE</th><th>Вывод</th><th>Стоимость списания, ₽/год</th><th>Стоимость по ТРЗ, ₽/год</th><th>Баланс, ₽/год</th></tr></thead><tbody>'+tr+'</tbody></table></div>'
  +'<p class="muted">Вывод: «норма» — отклонение не более ±'+TOL*100+' % от списания; «избыток» — списано больше потребности; «нехватка» — потребность выше списания. Стоимость = FTE × рабочие часы года × ставка роли.</p>';
 var be='<div class="tw"><table><thead><tr><th>Роль</th><th>Часов на релиз, ч</th><th>Из них на каждый сервис, ч</th><th>Баланс при N =</th></tr></thead><tbody>'+c.rows.map(function(r){var o=c.o[r.c],S=o.S*P.R+o.S*P.HF,Fx=o.F*P.R+o.F*P.HF_F*P.HF,al=ALLOC[r.c];var n=S>0?(al*c.A-Fx)/S:null;
  return '<tr><td>'+r.n+'</td><td>'+nf(o.F+o.S*P.N,1)+'</td><td>'+nf(o.S,1)+'</td><td>'+(n===null?'не зависит от N':(n<=0?'нехватка при любом N':'до '+nf(n,0)+' сервисов хватает'))+'</td></tr>'}).join('')+'</tbody></table></div>'
  +'<p class="muted">«Баланс при N» — до какого числа сервисов в релизе списанной ёмкости роли хватает при текущем числе релизов и hotfix.</p>';
 var un='<div class="kpis"><div class="kpi"><b>'+nf(T.hours/P.R,0)+'</b><span>часов на один релиз</span><small>все роли, при N = '+P.N+'</small></div><div class="kpi"><b>'+nf(T.hours/(P.R*P.N),1)+'</b><span>часов на сервис в релизе</span><small>ТРЗ релизного цикла на одну единицу выпуска</small></div>'
  +'<div class="kpi"><b>'+(T.has?nf(T.costReq/P.R):'—')+'</b><span>₽ на один релиз</span><small>по потребности (ТРЗ), с учётом ставок</small></div><div class="kpi"><b>'+(T.has?nf(T.costReq/(P.R*P.N)):'—')+'</b><span>₽ на сервис в релизе</span><small>цена выпуска одного сервиса</small></div></div>'
  +'<p>Эффект планирования по экономике (как в «Менеджменте команд»): затраты направления = ТРЗ × ставка; решение о нагрузке принимается по тому, где списанная ёмкость расходится с ТРЗ. Показатели выше — основание: сократить списание там, где избыток, и усилить там, где нехватка.</p>';
 document.getElementById('econ-out').innerHTML=kp+verdict
  +'<div class="tabs" data-g="ec"><button class="on" data-p="b">Баланс по ролям</button><button data-p="s">Чувствительность</button><button data-p="u">Цена релиза</button></div>'
  +'<div class="pane on" data-g="ec" data-p="b"><div class="econ-g"><div class="card">'+chart(c.rows)+'</div><div>'+tbl+'</div></div></div>'
  +'<div class="pane" data-g="ec" data-p="s"><div class="econ-g"><div class="card">'+sens(c.o)+'</div><div>'+be+'</div></div></div>'
  +'<div class="pane" data-g="ec" data-p="u">'+un+'</div>';
 bindTabs();document.querySelectorAll('#econ-out input.al').forEach(function(i){i.onchange=function(){ALLOC[i.dataset.r]=parseFloat(i.value)||0;render()}})}
function bindTabs(){document.querySelectorAll('#econ-out .tabs').forEach(function(t){var g=t.dataset.g;t.querySelectorAll('button').forEach(function(b){b.onclick=function(){t.querySelectorAll('button').forEach(function(x){x.classList.toggle('on',x===b)});document.querySelectorAll('#econ-out .pane[data-g="'+g+'"]').forEach(function(p){p.classList.toggle('on',p.dataset.p===b.dataset.p)})}})})}
var pf=Object.keys(P).map(function(key){return '<label>'+lab[key]+'<input type="number" step="any" data-k="'+key+'" value="'+P[key]+'" title="'+D.notes[key].replace(/"/g,'')+'"></label>'}).join('');
var rf=D.roles.map(function(r){return '<label>'+r[1]+'<input class="rate" type="number" step="any" min="0" data-r="'+r[0]+'" placeholder="₽/ч"></label>'}).join('');
var hr=H.map(function(h,i){return '<tr><td>'+h[0]+'</td><td>'+h[1]+'</td><td>'+h[2]+'</td><td><input type="number" step="any" data-i="'+i+'" data-c="3" value="'+h[3]+'"></td><td><input type="number" step="any" data-i="'+i+'" data-c="4" value="'+h[4]+'"></td><td>'+h[5]+'</td></tr>'}).join('');
var el=document.getElementById('calc');
el.innerHTML='<div id="econ-out"></div><details><summary>Параметры: число сервисов, релизы и hotfix в год, загрузка</summary><div class="calc-p">'+pf+'</div></details>'
 +'<details><summary>Ставки по ролям, ₽/ч (нигде не сохраняются)</summary><p class="muted">Единая ставка для всех ролей: <input id="rate-all" type="number" step="any" min="0" placeholder="₽/ч" style="width:90px"> <button id="rate-fill" type="button">Применить ко всем</button></p><div class="calc-p rates">'+rf+'</div></details>'
 +'<details><summary>Часы по этапам (F — на релиз, S — на сервис): допущения, редактируются</summary><div class="tw"><table><thead><tr><th>Этап</th><th>Название</th><th>Роль</th><th>F, ч</th><th>S, ч</th><th>Условие</th></tr></thead><tbody>'+hr+'</tbody></table></div></details>'
 +'<p><button id="calc-reset" type="button">Сбросить к значениям по умолчанию</button></p>';
el.querySelectorAll('.calc-p input[data-k]').forEach(function(i){i.oninput=function(){P[i.dataset.k]=parseFloat(i.value)||0;render()}});
el.querySelectorAll('input.rate').forEach(function(i){i.oninput=function(){RATE[i.dataset.r]=i.value;render()}});
el.querySelectorAll('details input[data-i]').forEach(function(i){i.oninput=function(){H[+i.dataset.i][+i.dataset.c]=parseFloat(i.value)||0;render()}});
document.getElementById('rate-fill').onclick=function(){var v=document.getElementById('rate-all').value;D.roles.forEach(function(r){RATE[r[0]]=v});el.querySelectorAll('input.rate').forEach(function(i){i.value=v});render()};
document.getElementById('calc-reset').onclick=function(){location.reload()};
render();
})();
"""
    js = js.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    intro = ("<p>Чтобы обосновать избыток или нехватку ресурсов, потребность ролей по ТРЗ релизного цикла сопоставляется с тем, сколько роль списывается на проект сейчас (1 FTE). "
             "Потребность: <code>FTE = ТРЗ за год / (рабочие часы × 80 %)</code>; ТРЗ этапа <code>(F + S × N) × k</code>. Всё пересчитывается при изменении параметров, списания по ролям (поле «Списано») и ставок.</p>"
             '<p class="muted">Часы по этапам — стартовые допущения: после 1–2 релизов их заменяют фактом списаний по задачам этапов в Jira. Ставки по ролям в документ не входят — вводятся в браузере.</p>')
    return intro + '<div id="calc"></div><script>' + js + "</script>"
