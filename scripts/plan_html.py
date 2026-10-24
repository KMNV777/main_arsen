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

PH_STEPS = {p: f"{min(ns)}–{max(ns)}" for p, ns in P.PHASE_STEPS.items()}
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
.seg.tot{border:0;overflow:visible}.seg{position:absolute;top:6px;height:18px;color:#fff;font-size:10px;font-weight:700;line-height:18px;padding:0 5px;white-space:nowrap;overflow:hidden;border-right:1px solid rgba(255,255,255,.5)}
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

.heat th{font-size:9px;color:#6B778C;font-weight:700;text-align:left;white-space:nowrap;padding-bottom:3px}
.h0{background:#EEF1F6!important}.h1{background:#D7F3B0!important}.h2{background:#8ED15A!important}.h3{background:#FBAE40!important}.h4{background:#F26B43!important}
.econ-g{display:grid;grid-template-columns:1fr;gap:14px}.econ-g>.card{max-width:780px}
@media(max-width:1000px){.econ-g{grid-template-columns:1fr}}
.rmx{border-collapse:separate;border-spacing:0;font-size:11px;width:auto}
.rmx th,.rmx td{padding:3px 5px;border-bottom:1px solid #F0F2F6;border-right:1px solid #F0F2F6;text-align:center;white-space:nowrap;background:#fff}
.rmx thead th{position:sticky;top:0;background:#140093;color:#fff;font-size:10px;text-transform:none;letter-spacing:0;z-index:2}
.rmx thead tr:nth-child(2) th{top:26px;background:#2A1FA8}
.rmx td.rl,.rmx th.rl{text-align:left;position:sticky;left:0;z-index:3;min-width:230px;background:#fff}.rmx thead th.rl{background:#140093}
.rmx td.mO{background:#140093;color:#fff;font-weight:700}.rmx td.mI{background:#D7E3F6;color:#140093;font-weight:700}
.stl{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:2px 16px;font-size:12px;color:#42526E;margin-top:10px}.stl b{color:#140093}
.mx{overflow:auto;max-height:78vh;background:#fff;border:1px solid var(--line);border-radius:6px;box-shadow:var(--sh-1)}
.smx{border-collapse:separate;border-spacing:0;font-size:11px;width:auto}
.smx th,.smx td{padding:4px 8px;border-bottom:1px solid #F0F2F6;border-right:1px solid #F0F2F6;white-space:nowrap;background:#fff;text-align:left}
.smx thead th{position:sticky;top:0;z-index:2;background:#140093;color:#fff;font-size:10px;text-transform:none;letter-spacing:0}
.smx td.d{text-align:center;color:#140093}.smx td.np{color:#B3260E;font-style:italic}
.smx tr.ph td{background:#EEEDF8;color:#140093;font-weight:700;font-size:10px;letter-spacing:.08em;text-transform:uppercase}
.smx tr.tot td{background:#EAFAB8}
.ctl{display:flex;gap:18px;flex-wrap:wrap;margin:6px 0 10px;font-size:13px}.ctl input,.ctl select{font:inherit;border:1px solid #FBAE40;background:#FFE9CC;border-radius:3px;padding:3px 6px;width:90px}.ctl select{width:auto}
.heat td.h{width:26px;min-width:26px;height:22px;text-align:center;font-size:9px;font-weight:700;color:#1B1B3A;border-radius:2px}.heat td.h span{pointer-events:none}
.heat td.sum,.heat th.sum{padding:0 8px;white-space:nowrap;text-align:right;background:none}.heat td.sum input{width:60px;font:inherit;font-size:11px;border:1px solid #FBAE40;background:#FFE9CC;border-radius:3px}
.heat td.r{padding:0 10px 0 0}
.verdict{border-left:4px solid #140093;background:#EEEDF8;border-radius:0 6px 6px 0;padding:12px 16px;margin:10px 0;font-size:14px}
.st{display:inline-block;padding:1px 8px;border-radius:9px;font-size:11px;font-weight:700}
.st.sur{background:#E3FCEF;color:#006644}.st.def{background:#FDE4DC;color:#B3260E}.st.okk{background:#DEEBFF;color:#0052CC}
.ctl-panel{background:#fff;border:1px solid var(--line);border-radius:6px;padding:12px 16px;margin:8px 0 14px;box-shadow:var(--sh-1)}.tw input.tx,.tw select{font:inherit;font-size:12px;border:1px solid #FBAE40;background:#FFE9CC;border-radius:3px;padding:2px 4px}.tw input[type=number]{width:70px;font:inherit;border:1px solid #FBAE40;background:#FFE9CC;border-radius:3px;padding:2px 4px}.tw input.al,.tw input.rate{width:80px;font:inherit;border:1px solid #FBAE40;background:#FFE9CC;border-radius:3px;padding:3px 5px}.del{border:0;background:none;color:#B3260E;cursor:pointer;font-size:14px}
.calc-p.rates{grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
svg.chart text{font-family:Arial,sans-serif}
"""

import fact_html as _F
from qa_cap import qa_html
CSS_PLAN += _F.CSS_FACT

JS_TABS = r"""
document.querySelectorAll('.tabs:not(.own)').forEach(function(t){var g=t.dataset.g;t.querySelectorAll('button').forEach(function(b){b.onclick=function(){
 t.querySelectorAll('button').forEach(function(x){x.classList.toggle('on',x===b)});
 document.querySelectorAll('.pane[data-g="'+g+'"]').forEach(function(p){p.classList.toggle('on',p.dataset.p===b.dataset.p)})}})});
"""


def _d(s: str) -> date:
    return date.fromisoformat(s)


# ---------------------------------------------------------------------------
# 1. Дорожная карта релизов
# ---------------------------------------------------------------------------
def roadmap_html(rels) -> str:
    t0, t1 = date(2026, 10, 1), date(2027, 12, 15)
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
            nd = r["pdays"][p]
            label = f'{D.PHASES[p].split(" (")[0]} · {nd} дн.' if w > 9 else (f"{nd}" if w > 1.3 else "")
            segs += f'<div class="seg" title="{e(D.PHASES[p])}: {P.fmt(a)} – {P.fmt(b)} · {nd} раб. дн. · этапы {PH_STEPS[p]}" style="left:{pct(a):.3f}%;width:{w:.3f}%;background:{PH_COL[p]}">{e(label)}</div>'
        cls = {"ВЫПОЛНЕНО": "done", "В РАБОТЕ": "work", "ПЛАН": "plan"}[r["status"]]
        rows.append(f'<div class="tl-row"><div class="tl-l"><span class="chip {cls}">{r["status"]}</span><div><b>{r["name"]}</b><div class="sub">спринт {P.fmt(r["sprint"][0])} – {P.fmt(r["sprint"][1])}{" · ПСИ ИБ" if r["psi"] else ""}</div><div class="sub" title="дни фаз: подготовка · спринт · стабилизация · релиз-борд · PreProd · прод">дни: {" · ".join(str(r["pdays"][p]) for p in D.PHASES)}</div></div></div>'
                    f'<div class="tl-r">{grid}{segs}<div class="seg tot" style="left:{pct(r["close"] + timedelta(days=1)) + .4:.3f}%;color:#140093;background:none;font-size:11px">{len(r["cols"]) - 1} дн.</div>{today}</div></div>')
    year = '<div class="tl"><div class="tl-in">' + "".join(rows) + "</div></div>"
    legend = '<div class="legend">' + "".join(f'<span><i style="background:{PH_COL[p]}"></i>{e(D.PHASES[p])}</span>' for p in D.PHASES) + '<span><i style="background:#E5493A"></i>сегодня (21 окт 2026)</span><span>число в блоке — рабочие дни фазы, справа — весь цикл</span></div>'

    # детализация релиза до этапа и рабочего дня
    data = []
    for r in rels:
        data.append({"name": r["name"], "psi": r["psi"], "cols": r["cols"],
                     "steps": [{"n": x["n"], "c0": x["c0"], "c1": x["c1"], "zero": x["b"] <= x["a"], "dd": P.days_txt(x["n"])} for x in r["steps"]]})
    meta = {str(n): {"t": D.STEP_NAME[n], "w": D.role_short(D.SN[n][3]), "ph": D.SN[n][1], "col": CONTOUR_COL[D.ROLES[D.SN[n][3]][1]] if D.SN[n][3] in D.ROLES else "#8A9BB5"} for n in D.SN}
    phases = {str(k): v for k, v in D.PHASES.items()}
    js = r"""
(function(){var R=__R__,M=__M__,PH=__PH__,MO=__MO__;var box=document.getElementById('gt'),sel=document.getElementById('rsel');
function f(s){var d=new Date(s);return d.getUTCDate()+' '+MO[d.getUTCMonth()]}
function draw(i){var r=R[i];sel.querySelectorAll('button').forEach(function(b,j){b.classList.toggle('on',j===i)});
 var h='<table><thead><tr><th class="n">Этап</th><th class="n" style="left:300px;min-width:150px">Ответственный</th><th class="n" style="min-width:44px;text-align:center">Дн.</th>';
 r.cols.forEach(function(c,k){var d=new Date(c),wk=(d.getUTCDay()===1||k===0);h+='<th class="'+(wk?'wk':'')+'" title="'+f(c)+'">'+(wk?d.getUTCDate()+'<br>'+MO[d.getUTCMonth()]:'')+'</th>'});
 h+='</tr></thead><tbody>';var last=0;
 r.steps.forEach(function(s){var m=M[s.n];if(s.n===18&&!r.psi){}
  if(m.ph!==last){last=m.ph;h+='<tr class="ph"><td class="n" colspan="2">'+PH[m.ph]+'</td><td class="c" colspan="'+r.cols.length+'"></td></tr>'}
  h+='<tr><td class="n"><b>'+s.n+'.</b> '+m.t+(s.n===18&&!r.psi?' <span class="muted">(не нужен — пропуск)</span>':'')+'</td><td class="who">'+m.w+'</td><td style="text-align:center;font-weight:700;color:#140093">'+(s.n===18&&!r.psi?'0':s.dd)+'</td>';
  r.cols.forEach(function(c,k){var d=new Date(c),wk=(d.getUTCDay()===1||k===0);var hit=k>=s.c0&&k<=s.c1&&!(s.n===18&&!r.psi);
   var lab=(k===s.c0)?('<span style="position:absolute;left:3px;top:0;line-height:16px;font-size:9px;font-weight:700;white-space:nowrap;z-index:1;'+(s.c1-s.c0>=2?'color:#fff':'color:#140093;left:'+(s.c1-s.c0+1)*17+'px')+'">'+s.dd+' дн.</span>'):'';
   h+='<td class="c'+(wk?' wk':'')+(hit?' hit':'')+'">'+(hit?'<div style="position:relative;background:'+m.col+';'+(k===s.c0?'border-radius:3px 0 0 3px;':'')+(k===s.c1?'border-radius:0 3px 3px 0;':'')+'" title="'+s.n+'. '+m.t+' · '+f(r.cols[s.c0])+(s.c1>s.c0?' – '+f(r.cols[s.c1]):'')+'">'+lab+'</div>':'')+'</td>'});
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
                  '<div class="card"><b>Каденс</b>' + S.ul(["Квартал = 6 спринтов по 2 недели + буфер; релизов 3.", "Релизный спринт — 2-й, 4-й и 6-й: в его последний день на master ставится тег релиза.",
                                                          "Перед спринтом 4 рабочих дня планирования: приоритеты (ВНП), оценка (РП с командой), релизный тикет (Release owner), подтверждение состава (ВНП).", "Не успели или не приняли на демо — в следующий релиз, объём не растягивается."]) + "</div>"
                  '<div class="card"><b>Окно параллельности</b>' + S.ul([f"В работе одновременно до {par} релизов — потолок для релиз-инженера и ИБ.", "Окна ИБ (аудит, ПСИ, трансфер) разных релизов не пересекаются; окно планируется заранее и сообщается ГПН (подтверждение не гарантировано).", "Старт нового релиза не ждёт аудита предыдущего — ограничением служат окна ИБ и потолок параллельных релизов (проверка — ниже).", "Сдвиг окна ИБ сдвигает следующий релиз на спринт."]) + "</div>"
                  '<div class="card"><b>Что фиксируется на год</b>' + S.ul(["Даты релизных спринтов, фича-фриза и деплоя в Прод.", "Квартальный Релизный Epic: обязательный объём и бизнес-требования.", "Окна ИБ: аудит и ПСИ, согласование трансфера (сообщаются ГПН).",
                                                                          "Окна простоя и праздников: релизные работы в них не планируются."]) + "</div></div>")
    chk = [("Окна ИБ (аудит → трансфер) разных релизов не пересекаются", f"{P.ib_overlaps(rels)} пересечений", P.ib_overlaps(rels) == 0),
           ("В работе одновременно не более 4 релизов", f"максимум {par}", par <= 4),
           ("Спринты релизов не пересекаются", f"{P.sprint_overlaps(rels)} пересечений", P.sprint_overlaps(rels) == 0)]
    check = S.tbl(["Правило календаря", "Результат проверки по календарю", "Итог"], [[a, b, "✓ выполняется" if ok else "✗ нарушено"] for a, b, ok in chk])
    cal = S.tbl(["Релиз", "Старт (тикет)", "Спринт", "Фича-фриз", "Код-фриз", "Аудит кода", "Трансфер согласован", "PreProd", "Деплой Прод", "Закрытие", "ПСИ ИБ"], P.calendar_rows(rels))

    # матрица этапов × релизов
    rel_names = [r["name"] for r in rels]
    mh_ = "<tr><th>№</th><th>Этап</th><th>Дн.</th><th>Ответственный</th>" + "".join(f"<th>{n}{'<br><span class=muted>ПСИ</span>' if r['psi'] else ''}</th>" for n, r in zip(rel_names, rels)) + "</tr>"
    mb_ = ""
    last_ph = 0
    for row in P.stage_matrix(rels):
        n = int(row[0])
        if D.SN[n][1] != last_ph:
            last_ph = D.SN[n][1]
            mb_ += f'<tr class="ph"><td colspan="{4 + len(rels)}"><span style="color:{PH_COL[last_ph]}">■</span> {e(D.PHASES[last_ph])}</td></tr>'
        mb_ += "<tr>" + f"<td><b>{row[0]}</b></td><td>{e(row[1])}</td><td class='d'><b>{row[2]}</b></td><td>{e(row[3])}</td>" + "".join(f"<td{' class=np' if c == 'не нужен' else ''}>{e(c)}</td>" for c in row[4:]) + "</tr>"
    tot_ = "<tr class='tot'><td></td><td><b>Весь цикл, рабочих дней</b></td><td></td><td></td>" + "".join(f"<td><b>{len(r['cols']) - 1}</b></td>" for r in rels) + "</tr>"
    stage_cal = ('<p>Все этапы цикла по каждому релизу: даты «с – по» и длительность этапа в рабочих днях (колонка «Дн.»). ПСИ ИБ есть не в каждом релизе.</p>'
                 f'<div class="mx"><table class="smx"><thead>{mh_}</thead><tbody>{mb_}{tot_}</tbody></table></div>')

    # нагрузка по неделям — динамическая, с ТРЗ в часах
    wf, ws = P.weekly_split(rels)
    wk0 = P.monday(min(r["day0"] for r in rels))
    wk1 = P.monday(max(r["close"] for r in rels))
    weeks = []
    d = wk0
    while d <= wk1:
        weeks.append(d)
        d += timedelta(days=7)
    order = ["РИ", "ИБ", "QA", "RO", "DEV", "ВНП", "DEVOPS", "SVC", "АБД", "АБР", "РП", "ARCH", "REL", "ТПИ", "PMM", "СМ", "АП"]
    hd = {"weeks": [[w.isoformat(), P.fmt(w), P.MONTHS[w.month - 1] if w.day <= 7 else ""] for w in weeks],
          "roles": [[r, D.ROLES[r][0].split(" (")[0].split(" /")[0]] for r in order],
          "F": {r: [round(wf[r].get(w, 0.0), 3) for w in weeks] for r in order},
          "S": {r: [round(ws[r].get(w, 0.0), 3) for w in weeks] for r in order},
          "N": T.PARAMS["N"][0], "load": T.PARAMS["LOAD"][0]}
    hjs = r"""
(function(){var H=__H__,N=H.N,FTE={},el=document.getElementById('heat');H.roles.forEach(function(r){FTE[r[0]]=1});
var hs=(window.RP&&RP.get('heat'))||null;if(hs){if(hs.N!=null)N=hs.N;Object.assign(FTE,hs.FTE||{});document.getElementById('hn').value=N;if(hs.mode)document.getElementById('hmode').value=hs.mode}
function hsv(){if(window.RP)RP.set('heat',{N:N,FTE:FTE,mode:document.getElementById('hmode').value})}
function cap(){return 40*H.load}
function cls(u){return u<.05?'h0':u<.5?'h1':u<1?'h2':u<1.5?'h3':'h4'}
function draw(){var show=document.getElementById('hmode').value,t='<table><tr><th></th>';
 H.weeks.forEach(function(w){t+='<th title="неделя с '+w[1]+'">'+w[2]+'</th>'});t+='<th class="sum">ТРЗ, ч</th><th class="sum">пик, ч/нед</th><th class="sum">FTE пула</th></tr>';var over=[];
 H.roles.forEach(function(r){var tot=0,pk=0,row='';H.weeks.forEach(function(w,i){var h=H.F[r[0]][i]+H.S[r[0]][i]*N;tot+=h;pk=Math.max(pk,h);var u=h/(cap()*FTE[r[0]]);
   row+='<td class="h '+cls(u)+'" title="'+r[1]+', неделя с '+w[1]+': '+Math.round(h)+' ч, '+Math.round(u*100)+'% ёмкости"><span>'+(h>=0.5?(show==='h'?Math.round(h):Math.round(u*100)):'')+'</span></td>'});
  var peak=pk/cap();if(pk/(cap()*FTE[r[0]])>1)over.push(r[1]+' — пик '+Math.round(pk/(cap()*FTE[r[0]])*100)+'% при '+FTE[r[0]]+' FTE');
  t+='<tr><td class="r">'+r[1]+'</td>'+row+'<td class="sum"><b>'+Math.round(tot)+'</b></td><td class="sum">'+Math.round(pk)+'</td><td class="sum"><input class="hf" data-r="'+r[0]+'" type="number" step="0.1" min="0.1" value="'+FTE[r[0]]+'"></td></tr>'});
 el.innerHTML='<div class="heat"><table>'+t+'</table></div><div class="verdict"><b>Вывод по пикам.</b> '+(over.length?'Выше ёмкости: '+over.join('; ')+'. Увеличьте FTE роли, уменьшите N или сдвиньте релизы.':'При текущих N и FTE пиков выше ёмкости нет.')+'</div>';
 el.querySelectorAll('input.hf').forEach(function(i){i.onchange=function(){FTE[i.dataset.r]=parseFloat(i.value)||1;hsv();draw()}})}
document.getElementById('hn').oninput=function(){N=parseFloat(this.value)||0;hsv();draw()};document.getElementById('hmode').onchange=function(){hsv();draw()};draw()})();
"""
    hjs = hjs.replace("__H__", json.dumps(hd, ensure_ascii=False))
    legend = ('<div class="legend"><span><i style="background:#EEF1F6"></i>&lt; 5 %</span><span><i style="background:#D7F3B0"></i>до 50 %</span><span><i style="background:#8ED15A"></i>50–100 %</span>'
              '<span><i style="background:#FBAE40"></i>100–150 %</span><span><i style="background:#F26B43"></i>&gt; 150 %</span><span>цвет — загрузка недели от ёмкости роли (FTE × 40 ч × 80 %); в ячейке — ТРЗ недели</span></div>')
    heat = ('<p>ТРЗ ролей по неделям года: часы этапов из модели ТРЗ <code>(F + S × N)</code> распределены по рабочим дням этапов каждого релиза. '
            "Меняйте число сервисов N и FTE роли — карта пересчитывается. Мейнтейнеры и QA — пулы: для них задавайте численность пула.</p>"
            '<div class="ctl"><label>Число сервисов в релизе, N <input id="hn" type="number" min="0" step="1" value="' + str(T.PARAMS["N"][0]) + '"></label>'
            '<label>В ячейке <select id="hmode"><option value="h">ТРЗ, часы</option><option value="p">% ёмкости</option></select></label></div>'
            + legend + '<div id="heat"></div><script>' + hjs + "</script>")

    rules = S.ol([
        "Календарь релизов утверждается на скользящий год и пересматривается раз в квартал вместе с Релизным Epic.",
        "Старт релиза допускается, только если у РИ, ИБ и QA в окне этапов запас по загрузке (по тепловой карте); иначе релиз сдвигается на спринт.",
        "Ёмкость QA в спринте после релизного планируется за вычетом резерва на регресс, Smoke и перепроверку исправлений.",
        "Объём релиза (число сервисов N) планируется от ёмкости: нужные часы по ролям при N не должны превышать 100 % FTE роли в пиковую неделю.",
        "Окна ИБ (аудит, ПСИ, трансфер) разных релизов не пересекаются; ПСИ ИБ закладывается в окно (5 рабочих дней), релиз с ПСИ не стартует параллельно другому релизу с ПСИ.",
        "В работе одновременно не более 4 релизов (цикл ~11–12 недель при релизе раз в 4 недели); при превышении следующий релиз сдвигается на спринт.",
        "Окна без релизных работ: новогодние праздники, длительные майские праздники; релизные спринты в них не назначаются.",
        "Сдвиг релиза — решение Release owner по согласованию с ВНП; причина фиксируется в календаре и попадает в метрику «Выполнение релизов по плану».",
        "Hotfix не входит в календарь: идёт тем же процессом (этапы короче из-за малого объёма сборки, раздел «Контроль релиза и риски») и учитывается в нагрузке как резерв (по модели ТРЗ — HF в год).",
        "Просрочка этапа эскалируется внутри НЕДРА (>1, >3, >5 рабочих дней); у ГПН обязательств по срокам нет, их сроки — наблюдаемые. Сдвиг Прода более 5 дней пересматривает календарь следующих релизов.",
    ])
    return ("<p>Стратегическое планирование задаёт годовой календарь релизов, окна параллельных релизов и проверку ёмкости ролей до старта каждого релиза. "
            "Исходные данные — SLA этапов, зоны ответственности и часы модели ТРЗ.</p>" + kpis + principles +
            "<h3>Проверка календаря по правилам</h3>" + check + "<h3>Ключевые даты релизов</h3>" + cal + "<h3>Календарь по всем этапам цикла (дни)</h3>" + stage_cal +
            "<h3>Загрузка ролей по неделям</h3>" + heat +
            "<h3>Ёмкость QA и «снежный ком»</h3>" + qa_html() + "<h3>Правила стратегического планирования</h3>" + rules)


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
var D=__DATA__,P=Object.assign({TOL:20},D.params),H=D.hours.map(function(x){return x.slice()}),RATE={},ALLOC={};
D.roles.forEach(function(r){ALLOC[r[0]]=D.cur});
var ES=window.RP&&RP.get('econ');if(ES){Object.assign(P,ES.P||{});RATE=ES.RATE||{};Object.assign(ALLOC,ES.ALLOC||{});if(ES.H&&ES.H.length===H.length)H=ES.H}
function sv(){if(window.RP)RP.set('econ',{P:P,RATE:RATE,ALLOC:ALLOC,H:H})}
var lab={N:'Число сервисов в релизе (N)',R:'Релизов в год',HF:'Hotfix в год',HF_F:'Доля фикс. части для hotfix',P_PSI:'Доля релизов с ПСИ ИБ',H_DAY:'Часов в день',D_YEAR:'Рабочих дней в году',LOAD:'Плановая загрузка',TOL:'Допуск «нормы», ±%'};
function rn(c){var r=D.roles.filter(function(x){return x[0]===c})[0];return r?r[1]:c}
function sh(c){return rn(c).split(' (')[0].split(' /')[0]}
function k(c){return c==='psi'?P.P_PSI:1}
function fs(){var o={};D.roles.forEach(function(r){o[r[0]]={F:0,S:0}});H.forEach(function(h){if(!o[h[2]])return;var kk=k(h[5]);o[h[2]].F+=h[3]*kk;o[h[2]].S+=h[4]*kk});return o}
function yr(o,N,R,HF){return (o.F+o.S*N)*R+(o.F*P.HF_F+o.S)*HF}
function avail(){return P.H_DAY*P.D_YEAR*P.LOAD}
function nf(x,d){return x.toLocaleString('ru-RU',{minimumFractionDigits:d||0,maximumFractionDigits:d||0})}
function calc(){var o=fs(),A=avail(),full=P.H_DAY*P.D_YEAR,rows=[],T={req:0,alloc:0,sur:0,def:0,cost:0,costReq:0,has:false,hours:0,costSur:0,costDef:0},tol=P.TOL/100;
 D.roles.forEach(function(r){var c=o[r[0]],hrs=yr(c,P.N,P.R,P.HF),req=hrs/A,al=ALLOC[r[0]],bal=al-req,rate=parseFloat(RATE[r[0]]);
  var st=Math.abs(bal)<=tol*al?'ok':(bal>0?'sur':'def'),has=!isNaN(rate);
  var cAl=has?al*full*rate:null,cReq=has?req*full*rate:null,cB=has?bal*full*rate:null;
  T.req+=req;T.alloc+=al;T.hours+=hrs;if(bal>0)T.sur+=bal;else T.def+=-bal;if(has){T.has=true;T.cost+=cAl;T.costReq+=cReq;if(cB>0)T.costSur+=cB;else T.costDef+=-cB}
  rows.push({c:r[0],n:r[1],req:req,al:al,bal:bal,st:st,cAl:cAl,cReq:cReq,cB:cB,hrs:hrs})});
 return {rows:rows,T:T,full:full,A:A,o:o}}
var stT={ok:['okk','норма'],sur:['sur','резерв ёмкости'],def:['def','нехватка']};
function bars(items,fmt,colr,W){W=W||640;var rowH=24,pad=190,h=items.length*rowH+20,mx=0;items.forEach(function(r){mx=Math.max(mx,r.v)});mx=mx||1;var sc=(W-pad-80)/mx;
 var s='<svg class="chart" viewBox="0 0 '+W+' '+h+'" width="100%">';
 items.forEach(function(r,i){var y=8+i*rowH;s+='<text x="'+(pad-8)+'" y="'+(y+14)+'" font-size="11" text-anchor="end" fill="#333">'+r.l.slice(0,30)+'</text><rect x="'+pad+'" y="'+(y+2)+'" width="'+Math.max(r.v*sc,1)+'" height="16" rx="2" fill="'+(colr?colr(r):'#140093')+'"/><text x="'+(pad+r.v*sc+5)+'" y="'+(y+14)+'" font-size="10" font-weight="700" fill="#333">'+fmt(r.v)+'</text>'});
 return s+'</svg>'}
function chart(rows){var W=640,rowH=26,pad=170,h=rows.length*rowH+40,mx=0;rows.forEach(function(r){mx=Math.max(mx,Math.abs(r.bal))});mx=Math.max(mx,0.5);var sc=(W-pad-110)/(2*mx),mid=pad+50+mx*sc;
 var s='<svg class="chart" viewBox="0 0 '+W+' '+h+'" width="100%" role="img" aria-label="Баланс FTE по ролям"><line x1="'+mid+'" x2="'+mid+'" y1="16" y2="'+(h-14)+'" stroke="#C7D4DE"/>';
 s+='<text x="'+(mid+4)+'" y="11" font-size="10" fill="#006644" font-weight="700">резерв ёмкости</text><text x="'+(mid-4)+'" y="11" font-size="10" fill="#B3260E" font-weight="700" text-anchor="end">нехватка</text>';
 rows.forEach(function(r,i){var y=22+i*rowH,w=Math.abs(r.bal)*sc,col=r.st==='ok'?'#4BADE8':(r.bal>0?'#63BA3C':'#F26B43');
  s+='<text x="'+(pad-8)+'" y="'+(y+14)+'" font-size="11" text-anchor="end" fill="#333">'+sh(r.c).slice(0,26)+'</text><rect x="'+(r.bal>=0?mid:mid-w)+'" y="'+(y+2)+'" width="'+w+'" height="16" rx="2" fill="'+col+'"/>';
  s+='<text x="'+(r.bal>=0?mid+w+5:mid-w-5)+'" y="'+(y+14)+'" font-size="10" font-weight="700" fill="#333" text-anchor="'+(r.bal>=0?'start':'end')+'">'+(r.bal>0?'+':'')+nf(r.bal,2)+'</text>'});
 return s+'</svg>'}
function sens(o){var W=640,Hh=260,L=46,B=30,Ns=[],i;for(i=1;i<=30;i++)Ns.push(i);var Rs=[[8,'8 в год'],[12,'12 в год (3 в квартал)'],[16,'16 в год'],[26,'26 в год (каждый спринт)'],[P.R,'ваш: '+P.R]],cols=['#8A9BB5','#140093','#904EE2','#F26B43','#006644'];
 function tot(N,R){var t=0;D.roles.forEach(function(r){t+=yr(o[r[0]],N,R,P.HF)/avail()});return t}
 var mx=0;Rs.forEach(function(r){mx=Math.max(mx,tot(30,r[0]))});mx=Math.ceil(mx/5)*5||5;
 var X=function(n){return L+(n-1)/29*(W-L-14)},Y=function(v){return Hh-B-v/mx*(Hh-B-12)};
 var s='<svg class="chart" viewBox="0 0 '+W+' '+Hh+'" width="100%" role="img" aria-label="Потребность в FTE от числа сервисов">';
 for(i=0;i<=mx;i+=5){s+='<line x1="'+L+'" x2="'+(W-14)+'" y1="'+Y(i)+'" y2="'+Y(i)+'" stroke="#EEF1F6"/><text x="'+(L-6)+'" y="'+(Y(i)+3)+'" font-size="10" text-anchor="end" fill="#6B778C">'+i+'</text>'}
 for(i=5;i<=30;i+=5){s+='<text x="'+X(i)+'" y="'+(Hh-12)+'" font-size="10" text-anchor="middle" fill="#6B778C">'+i+'</text>'}
 s+='<text x="'+(W/2)+'" y="'+(Hh-1)+'" font-size="10" text-anchor="middle" fill="#6B778C">число сервисов в релизе, N</text>';
 var al=0;D.roles.forEach(function(r){al+=ALLOC[r[0]]});var cur=Y(al);if(al<=mx)s+='<line x1="'+L+'" x2="'+(W-14)+'" y1="'+cur+'" y2="'+cur+'" stroke="#E5493A" stroke-dasharray="5 4"/><text x="'+(W-16)+'" y="'+(cur-4)+'" font-size="10" fill="#E5493A" text-anchor="end">сейчас списано '+nf(al,1)+' FTE</text>';
 s+='<line x1="'+X(Math.min(P.N,30))+'" x2="'+X(Math.min(P.N,30))+'" y1="12" y2="'+(Hh-B)+'" stroke="#AAC3E3" stroke-dasharray="3 3"/><text x="'+(X(Math.min(P.N,30))+4)+'" y="22" font-size="10" fill="#6B778C">ваш N = '+P.N+'</text>';
 Rs.forEach(function(r,j){var d='';Ns.forEach(function(n,q){d+=(q?'L':'M')+X(n)+' '+Y(tot(n,r[0]))});s+='<path d="'+d+'" fill="none" stroke="'+cols[j]+'" stroke-width="'+(j===4?3:2)+'"/><text x="'+(X(30)-4)+'" y="'+(Y(tot(30,r[0]))-5)+'" font-size="10" fill="'+cols[j]+'" text-anchor="end" font-weight="700">'+r[1]+'</text>'});
 return s+'</svg>'}
function stepsDash(){var m={};H.forEach(function(h){var key=h[0]+'. '+h[1];m[key]=(m[key]||0)+(h[3]+h[4]*P.N)*k(h[5])});var it=Object.keys(m).map(function(x){return {l:x,v:m[x]}}).sort(function(a,b){return b.v-a.v}).slice(0,18);
 var tot=0;Object.keys(m).forEach(function(x){tot+=m[x]});return '<p class="muted">18 самых трудоёмких этапов: ТРЗ на один релиз, ч (всего по всем ролям '+nf(tot)+' ч). Меняйте часы F и S в таблице этапов — график обновится.</p>'+bars(it,function(v){return nf(v,1)+' ч'},function(r){return '#4BADE8'},760)}
function costDash(c){if(!c.T.has)return '<div class="verdict">Введите ставки ролей (колонка «Ставка» в таблице или кнопка «Единая ставка») — график затрат появится здесь.</div>';
 var it=c.rows.filter(function(r){return r.cAl!==null}).map(function(r){return {l:sh(r.c),v:r.cAl,v2:r.cReq}});var mx=0;it.forEach(function(r){mx=Math.max(mx,r.v,r.v2)});mx=mx||1;var W=760,pad=190,sc=(W-pad-110)/mx,h=it.length*34+40;
 var s='<svg class="chart" viewBox="0 0 '+W+' '+h+'" width="100%"><text x="'+pad+'" y="12" font-size="10" fill="#8A9BB5" font-weight="700">■ списание сейчас, ₽/год</text><text x="'+(pad+190)+'" y="12" font-size="10" fill="#140093" font-weight="700">■ по ТРЗ, ₽/год</text>';
 it.forEach(function(r,i){var y=22+i*34;s+='<text x="'+(pad-8)+'" y="'+(y+20)+'" font-size="11" text-anchor="end" fill="#333">'+r.l.slice(0,30)+'</text><rect x="'+pad+'" y="'+y+'" width="'+Math.max(r.v*sc,1)+'" height="13" fill="#8A9BB5"/><text x="'+(pad+r.v*sc+5)+'" y="'+(y+11)+'" font-size="9" fill="#333">'+nf(r.v)+'</text><rect x="'+pad+'" y="'+(y+15)+'" width="'+Math.max(r.v2*sc,1)+'" height="13" fill="#140093"/><text x="'+(pad+r.v2*sc+5)+'" y="'+(y+26)+'" font-size="9" fill="#333">'+nf(r.v2)+'</text>'});
 return '<div class="kpis"><div class="kpi"><b>'+nf(c.T.cost/1e6,1)+'</b><span>млн ₽/год — текущее списание</span></div><div class="kpi"><b>'+nf(c.T.costReq/1e6,1)+'</b><span>млн ₽/год — по ТРЗ</span></div><div class="kpi ok"><b>+'+nf(c.T.costSur/1e6,1)+'</b><span>млн ₽/год — стоимость избытка</span></div><div class="kpi bad"><b>−'+nf(c.T.costDef/1e6,1)+'</b><span>млн ₽/год — стоимость нехватки</span></div></div>'+s+'</svg>'}
function render(){var c=calc(),T=c.T,deficit=c.rows.filter(function(r){return r.st==='def'}),sur=c.rows.filter(function(r){return r.st==='sur'});
 var kp='<div class="kpis"><div class="kpi"><b>'+nf(T.alloc,1)+'</b><span>FTE списывается сейчас</span><small>по полям «Списано» ниже</small></div>'
 +'<div class="kpi"><b>'+nf(T.req,1)+'</b><span>FTE занято релизным циклом</span><small>'+nf(T.hours)+' ч в год при N = '+P.N+', '+P.R+' релизах</small></div>'
 +'<div class="kpi ok"><b>+'+nf(T.sur,1)+'</b><span>FTE свободной ёмкости</span><small>'+sur.length+' ролей: списано больше, чем занято релизом</small></div>'
 +'<div class="kpi '+(T.def>0.05?'bad':'ok')+'"><b>'+(T.def>0.05?'−':'')+nf(T.def,1)+'</b><span>FTE нехватка</span><small>'+deficit.length+' ролей: релизный цикл занимает больше списанного</small></div>'
 +'<div class="kpi"><b>'+nf(T.hours/P.R,0)+'</b><span>часов на один релиз</span><small>'+nf(T.hours/(P.R*Math.max(P.N,1)),1)+' ч на сервис в релизе</small></div></div>';
 var verdict='<div class="verdict"><b>Вывод.</b> Списывается '+nf(T.alloc,1)+' FTE, релизный цикл занимает '+nf(T.req,1)+' FTE: свободная ёмкость '+nf(T.sur,1)+' FTE. <b>Это не штатная потребность</b>: роли заняты и вне релизов (ИБ, DevOps, администраторы и др.), решение о составе — после замера фактической и полной загрузки.'
 +(deficit.length?' Нехватка у ролей: '+deficit.map(function(r){return sh(r.c)+' (−'+nf(-r.bal,2)+')'}).join('; ')+' — ТРЗ превышает списание: усилить роль или сократить объём (N, число релизов).':' Нехватки нет.')
 +(sur.length?' У '+sur.length+' ролей есть ёмкость под другие задачи (суммарно '+nf(T.sur,1)+' FTE); можно перенаправить, если подтвердится полной загрузкой.':'')+(T.has?' Стоимость свободной ёмкости — '+nf(T.costSur)+' ₽ в год, стоимость нехватки — '+nf(T.costDef)+' ₽ в год.':' Введите ставки ролей, чтобы увидеть стоимость.')+'</div>';
 var tr=c.rows.map(function(r){return '<tr><td>'+r.n+'</td><td><b>'+nf(r.req,2)+'</b></td><td><input class="al" type="number" step="0.1" min="0" data-r="'+r.c+'" value="'+r.al+'"></td><td><b>'+(r.bal>0?'+':'')+nf(r.bal,2)+'</b></td><td><span class="st '+stT[r.st][0]+'">'+stT[r.st][1]+'</span></td>'
  +'<td><input class="rate" type="number" step="any" min="0" data-r="'+r.c+'" placeholder="₽/ч" value="'+(RATE[r.c]||'')+'"></td><td>'+(r.cAl===null?'—':nf(r.cAl))+'</td><td>'+(r.cReq===null?'—':nf(r.cReq))+'</td><td>'+(r.cB===null?'—':(r.cB>0?'+':'')+nf(r.cB))+'</td></tr>'}).join('')
  +'<tr class="tot"><td><b>Итого</b></td><td><b>'+nf(T.req,2)+'</b></td><td><b>'+nf(T.alloc,1)+'</b></td><td><b>'+(T.alloc-T.req>0?'+':'')+nf(T.alloc-T.req,2)+'</b></td><td></td><td></td><td>'+(T.has?nf(T.cost):'—')+'</td><td>'+(T.has?nf(T.costReq):'—')+'</td><td>'+(T.has?nf(T.cost-T.costReq):'—')+'</td></tr>';
 var tbl='<div class="tw"><table><thead><tr><th>Роль</th><th>Занято релизом, FTE</th><th>Списано, FTE</th><th>Баланс, FTE</th><th>Вывод</th><th>Ставка, ₽/ч</th><th>Стоимость списания, ₽/год</th><th>Стоимость по ТРЗ, ₽/год</th><th>Баланс, ₽/год</th></tr></thead><tbody>'+tr+'</tbody></table></div>'
  +'<p class="muted">Поля «Списано» и «Ставка» редактируются. Стоимость = FTE × рабочие часы года × ставка роли. «Норма» — отклонение в пределах допуска.</p>';
 var be='<div class="tw"><table><thead><tr><th>Роль</th><th>Часов на релиз, ч</th><th>Из них на каждый сервис, ч</th><th>Баланс при N</th></tr></thead><tbody>'+c.rows.map(function(r){var o=c.o[r.c],S=o.S*P.R+o.S*P.HF,Fx=o.F*P.R+o.F*P.HF_F*P.HF,al=ALLOC[r.c];var n=S>0?(al*c.A-Fx)/S:null;
  return '<tr><td>'+r.n+'</td><td>'+nf(o.F+o.S*P.N,1)+'</td><td>'+nf(o.S,1)+'</td><td>'+(n===null?'не зависит от N':(n<=0?'нехватка при любом N':'до '+nf(n,0)+' сервисов хватает'))+'</td></tr>'}).join('')+'</tbody></table></div>';
 var un='<div class="kpis"><div class="kpi"><b>'+nf(T.hours/P.R,0)+'</b><span>часов на один релиз</span><small>все роли, N = '+P.N+'</small></div><div class="kpi"><b>'+nf(T.hours/(P.R*Math.max(P.N,1)),1)+'</b><span>часов на сервис в релизе</span><small>ТРЗ цикла на одну единицу выпуска</small></div>'
  +'<div class="kpi"><b>'+(T.has?nf(T.costReq/P.R):'—')+'</b><span>₽ на один релиз</span><small>по потребности, со ставками</small></div><div class="kpi"><b>'+(T.has?nf(T.costReq/(P.R*Math.max(P.N,1))):'—')+'</b><span>₽ на сервис в релизе</span><small>цена выпуска одного сервиса</small></div></div>';
 document.getElementById('econ-out').innerHTML=kp+verdict
  +'<div class="tabs own" data-g="ec"><button class="on" data-p="b">Баланс по ролям</button><button data-p="t">ТРЗ по этапам</button><button data-p="c">Затраты</button><button data-p="s">Чувствительность</button><button data-p="u">Цена релиза</button></div>'
  +'<div class="pane on" data-g="ec" data-p="b"><div class="econ-g"><div class="card">'+chart(c.rows)+'</div><div>'+tbl+'</div></div></div>'
  +'<div class="pane" data-g="ec" data-p="t"><div class="card">'+stepsDash()+'</div></div>'
  +'<div class="pane" data-g="ec" data-p="c">'+costDash(c)+'</div>'
  +'<div class="pane" data-g="ec" data-p="s"><div class="econ-g"><div class="card">'+sens(c.o)+'</div><div>'+be+'</div></div></div>'
  +'<div class="pane" data-g="ec" data-p="u">'+un+'</div>';
 restoreTab();bindTabs();
 document.querySelectorAll('#econ-out input.al').forEach(function(i){i.onchange=function(){ALLOC[i.dataset.r]=parseFloat(i.value)||0;sv();render()}});
 document.querySelectorAll('#econ-out input.rate').forEach(function(i){i.onchange=function(){RATE[i.dataset.r]=i.value;sv();render()}})}
var curTab='b';
function restoreTab(){document.querySelectorAll('#econ-out .tabs button').forEach(function(b){b.classList.toggle('on',b.dataset.p===curTab)});document.querySelectorAll('#econ-out .pane').forEach(function(p){p.classList.toggle('on',p.dataset.p===curTab)})}
function bindTabs(){document.querySelectorAll('#econ-out .tabs button').forEach(function(b){b.onclick=function(){curTab=b.dataset.p;restoreTab()}})}
function roleOpts(sel){return D.roles.map(function(r){return '<option value="'+r[0]+'"'+(r[0]===sel?' selected':'')+'>'+sh(r[0])+'</option>'}).join('')}
function hoursTable(){return H.map(function(h,i){return '<tr><td><input class="tx" data-i="'+i+'" data-c="0" value="'+h[0]+'" size="3"></td><td><input class="tx" data-i="'+i+'" data-c="1" value="'+String(h[1]).replace(/"/g,'&quot;')+'" size="34"></td><td><select data-i="'+i+'" data-c="2">'+roleOpts(h[2])+'</select></td><td><input type="number" step="any" data-i="'+i+'" data-c="3" value="'+h[3]+'"></td><td><input type="number" step="any" data-i="'+i+'" data-c="4" value="'+h[4]+'"></td><td><select data-i="'+i+'" data-c="5"><option value="1"'+(h[5]==='1'?' selected':'')+'>всегда</option><option value="psi"'+(h[5]==='psi'?' selected':'')+'>если ПСИ ИБ</option></select></td><td><button type="button" class="del" data-i="'+i+'">✕</button></td></tr>'}).join('')}
function bindHours(){var b=document.getElementById('hrs');b.innerHTML=hoursTable();
 b.querySelectorAll('input,select').forEach(function(i){i.oninput=i.onchange=function(){var c=+i.dataset.c,v=i.value;H[+i.dataset.i][c]=(c===3||c===4)?(parseFloat(v)||0):(c===0?(parseInt(v)||v):v);sv();render()}});
 b.querySelectorAll('.del').forEach(function(x){x.onclick=function(){H.splice(+x.dataset.i,1);bindHours();render()}})}
var pf=Object.keys(lab).map(function(key){return '<label>'+lab[key]+'<input type="number" step="any" data-k="'+key+'" value="'+P[key]+'" title="'+(D.notes[key]||'').replace(/"/g,'')+'"></label>'}).join('');
var el=document.getElementById('calc');
el.innerHTML='<div class="ctl-panel"><b>Параметры расчёта</b><div class="calc-p">'+pf+'</div><p class="muted">Единая ставка для всех ролей: <input id="rate-all" type="number" step="any" min="0" placeholder="₽/ч" style="width:90px"> <button id="rate-fill" type="button">Применить ко всем</button> <button id="calc-reset" type="button">Сбросить всё</button></p></div><div id="econ-out"></div>'
 +'<details><summary>Часы по этапам (F — на релиз, S — на сервис): таблица редактируется, строки можно добавлять и удалять</summary><div class="tw"><table><thead><tr><th>№</th><th>Название этапа</th><th>Роль</th><th>F, ч</th><th>S, ч</th><th>Условие</th><th></th></tr></thead><tbody id="hrs"></tbody></table></div><p><button id="add-row" type="button">+ Добавить строку</button></p></details>';
el.querySelectorAll('.calc-p input[data-k]').forEach(function(i){i.oninput=function(){P[i.dataset.k]=parseFloat(i.value)||0;sv();render()}});
document.getElementById('rate-fill').onclick=function(){var v=document.getElementById('rate-all').value;D.roles.forEach(function(r){RATE[r[0]]=v});sv();render()};
document.getElementById('add-row').onclick=function(){H.push([0,'Новый этап','РИ',1,0,'1']);bindHours();render()};
document.getElementById('calc-reset').onclick=function(){if(window.RP)RP.set('econ',null);location.reload()};
bindHours();render();
})();
"""
    js = js.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    intro = ("<p>Показывает, какую часть ёмкости каждой роли занимает релизный цикл по ТРЗ, и сопоставляет её с тем, сколько роль списывается на проект сейчас (1 FTE). Это <b>не штатная потребность роли</b>: ИБ, DevOps, администраторы заняты и вне релизов, поэтому вывод о составе возможен только после замера полной загрузки. "
             "Занятость релизом: <code>FTE = ТРЗ за год / (рабочие часы × 80 %)</code>; ТРЗ этапа <code>(F + S × N) × k</code>. "
             "<b>Все поля редактируются:</b> параметры, списание и ставки по ролям, часы по этапам (строки можно добавлять и удалять); показатели, графики и вывод пересчитываются сразу.</p>"
             '<p class="muted">Часы по этапам — стартовые допущения: после 1–2 релизов их заменяют фактом списаний по задачам этапов в Jira. Введённые значения сохраняются в этом браузере и в файле при «Сохранить HTML».</p>')
    return intro + '<div id="calc"></div><script>' + js + "</script>"
