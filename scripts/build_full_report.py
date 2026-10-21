#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Единый самодостаточный HTML: процесс + схемы + ТРЗ/FTE (интерактивный калькулятор) + ревью
+ готовые тексты для Confluence (с кнопками копирования) + файлы для скачивания (draw.io, Excel).

В каждом разделе есть поле «Ваши правки»; кнопки внизу скачивают/копируют все правки одним текстом.
Запуск:  python3 scripts/build_full_report.py   (после build_release_process.py и build_trz.py)
"""

import base64
import json
from pathlib import Path

import build_confluence as C
import build_release_process as B
import trz_model as T

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "release-process-full.html"


def calc_html() -> str:
    name = {s[0]: s[3] for s in B.STEPS}
    data = {
        "params": {k: v[0] for k, v in T.PARAMS.items()},
        "notes": {k: v[1] for k, v in T.PARAMS.items()},
        "hours": [[sid, name[sid], role, f, s, code] for sid, role, f, s, code in T.HOURS],
        "roles": [[r, T.ROLE_NAME[r]] for r in T.ROLE_ORDER],
        "current": T.CURRENT_FTE,
    }
    js = r"""
(function(){
 var D=__DATA__, P=Object.assign({},D.params), H=D.hours.map(function(x){return x.slice()}), RATE={};
 var el=document.getElementById('calc');
 var labels={N:'Число сервисов N',R:'Релизов в год',HF:'Hotfix в год',HF_F:'Доля фикс. части для hotfix',P_PSI:'Доля релизов с ПСИ',P_PTZ:'Доля релизов с ПТЗ',H_DAY:'Часов в день',D_YEAR:'Рабочих дней в году',LOAD:'Плановая загрузка'};
 function k(c){return c==='psi'?P.P_PSI:(c==='ptz'?P.P_PTZ:1)}
 function calc(){
  var out={};D.roles.forEach(function(r){out[r[0]]={F:0,S:0}});
  H.forEach(function(h){var kk=k(h[5]);out[h[2]].F+=h[3]*kk;out[h[2]].S+=h[4]*kk});
  var avail=P.H_DAY*P.D_YEAR*P.LOAD,full=P.H_DAY*P.D_YEAR,tot={rel:0,yr:0,fte:0,cost:0,cur:0,has:false};
  var rows=D.roles.map(function(r){var o=out[r[0]];var rel=o.F+o.S*P.N,hf=o.F*P.HF_F+o.S,yr=rel*P.R+hf*P.HF,fte=yr/avail;
   var rate=parseFloat(RATE[r[0]]),cost=isNaN(rate)?null:yr*rate,curc=isNaN(rate)?null:D.current*full*rate;
   tot.rel+=rel;tot.yr+=yr;tot.fte+=fte;tot.cur+=D.current;if(cost!==null){tot.has=true;tot.cost+=cost}
   return '<tr><td>'+r[1]+'</td><td>'+rel.toFixed(0)+'</td><td>'+yr.toFixed(0)+'</td><td><b>'+fte.toFixed(2)+'</b></td><td>'+D.current.toFixed(0)+'</td><td>'+(D.current-fte>=0?'+':'')+(D.current-fte).toFixed(2)+'</td>'
   +'<td><input class="rate" data-r="'+r[0]+'" value="'+(RATE[r[0]]||'')+'" placeholder="₽/ч" size="6"></td><td>'+(cost===null?'':Math.round(cost).toLocaleString('ru-RU'))+'</td><td>'+(curc===null?'':Math.round(curc).toLocaleString('ru-RU'))+'</td></tr>'});
  rows.push('<tr class="tot"><td><b>Итого</b></td><td><b>'+tot.rel.toFixed(0)+'</b></td><td><b>'+tot.yr.toFixed(0)+'</b></td><td><b>'+tot.fte.toFixed(2)+'</b></td><td><b>'+tot.cur.toFixed(0)+'</b></td><td><b>'+(tot.cur-tot.fte>=0?'+':'')+(tot.cur-tot.fte).toFixed(2)+'</b></td><td></td><td>'+(tot.has?Math.round(tot.cost).toLocaleString('ru-RU'):'')+'</td><td></td></tr>');
  document.getElementById('calc-out').innerHTML='<div class="tw"><table><thead><tr><th>Роль</th><th>ТРЗ на релиз, ч</th><th>ТРЗ в год, ч</th><th>FTE по ТРЗ</th><th>Сейчас, FTE</th><th>Разница</th><th>Ставка, ₽/ч</th><th>Стоимость ТРЗ в год, ₽</th><th>Стоимость текущего списания, ₽</th></tr></thead><tbody>'+rows.join('')+'</tbody></table></div>';
  document.querySelectorAll('#calc-out .rate').forEach(function(i){i.onchange=function(){RATE[i.dataset.r]=i.value;calc()}});
 }
 var pf=Object.keys(P).map(function(key){return '<label>'+labels[key]+'<input type="number" step="any" data-k="'+key+'" value="'+P[key]+'" title="'+D.notes[key].replace(/"/g,'')+'"></label>'}).join('');
 var hr=H.map(function(h,i){return '<tr><td>'+h[0]+'</td><td>'+h[1]+'</td><td>'+h[2]+'</td><td><input type="number" step="any" data-i="'+i+'" data-c="3" value="'+h[3]+'"></td><td><input type="number" step="any" data-i="'+i+'" data-c="4" value="'+h[4]+'"></td><td>'+h[5]+'</td></tr>'}).join('');
 el.innerHTML='<div class="calc-p">'+pf+'</div><div id="calc-out"></div><details><summary>Часы по шагам (F — на релиз, S — на сервис): редактируются</summary><div class="tw"><table><thead><tr><th>Шаг</th><th>Название</th><th>Роль</th><th>F, ч</th><th>S, ч</th><th>Условие</th></tr></thead><tbody>'+hr+'</tbody></table></div></details><p><button id="calc-reset">Сбросить к значениям по умолчанию</button></p>';
 el.querySelectorAll('.calc-p input').forEach(function(i){i.oninput=function(){P[i.dataset.k]=parseFloat(i.value)||0;calc()}});
 el.querySelectorAll('details input').forEach(function(i){i.oninput=function(){H[+i.dataset.i][+i.dataset.c]=parseFloat(i.value)||0;calc()}});
 document.getElementById('calc-reset').onclick=function(){location.reload()};
 calc();
})();
"""
    return ('<h2 style="margin-top:24px">Интерактивный расчёт</h2><p class="muted">Меняйте параметры и часы — таблица пересчитывается сразу (расчёт в браузере, без сохранения). '
            'Ставки вводятся по ролям и нигде не сохраняются.</p><div id="calc"></div><script>' + js.replace("__DATA__", json.dumps(data, ensure_ascii=False)) + "</script>")


def downloads_html() -> str:
    def link(path: Path, label: str, mime: str, fname: str) -> str:
        b64 = base64.b64encode(path.read_bytes()).decode()
        kb = path.stat().st_size // 1024
        return f'<li><a download="{fname}" href="data:{mime};base64,{b64}">{label}</a> <span class="muted">({kb} КБ)</span></li>'
    items = [
        link(ROOT / "docs/drawio/10-release-process.drawio", "Схема процесса (draw.io, 5 страниц) — редактируемый источник", "application/xml", "10-release-process.drawio"),
        link(ROOT / "docs/release-trz-fte.xlsx", "Модель ТРЗ и FTE по ролям (Excel, живые формулы)", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "release-trz-fte.xlsx"),
    ]
    return ("<p>Файлы встроены в эту страницу — скачиваются без интернета.</p><ul>" + "".join(items) + "</ul>"
            "<p class='muted'>Схема в draw.io: File → Open from → Device. Excel: жёлтые/оранжевые ячейки — входные данные.</p>")


COPY_JS = r"""
function cpBlock(id,btn){var el=document.getElementById(id+'-body');var r=document.createRange();r.selectNodeContents(el);
var s=window.getSelection();s.removeAllRanges();s.addRange(r);var ok=false;try{ok=document.execCommand('copy')}catch(e){}
btn.textContent=ok?'Скопировано ✓ — вставьте в Confluence (Ctrl+V)':'Выделено — нажмите Ctrl+C';
setTimeout(function(){s.removeAllRanges();btn.textContent='Копировать блок для Confluence'},3000)}
"""
EXTRA_CSS = """
.calc-p{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:8px;margin:8px 0}
.calc-p label{font-size:12px;color:var(--mut);display:flex;flex-direction:column;gap:2px}
#calc input,.tools+div input{font:inherit}
#calc input[type=number],#calc input.rate{background:#FFE4CC;color:#1B1B3A;border:1px solid var(--orgd);border-radius:3px;padding:3px 6px;width:100%}
#calc input.rate{width:80px}
@media (prefers-color-scheme:dark){#calc input[type=number],#calc input.rate{background:#5C3A18;color:#fff}}
tr.tot td{background:var(--lo)}
details{margin:10px 0}summary{cursor:pointer;color:var(--ind);font-weight:600}
.tools{margin:6px 0 10px}.tools button{background:var(--ind);color:var(--lime);border:0;border-radius:3px;padding:6px 12px;cursor:pointer;font-weight:600}
.tools button:hover{background:var(--orgd);color:#fff}
"""


def main() -> None:
    pages = [B.page_process(), B.page_branches(), B.page_matrix(), B.page_jira(), B.page_review()]
    extra = []
    for i, t, fn in C.PAGES:
        if i in ("trz", "review"):
            continue
        extra.append((f"cf-{i}", f"Confluence · {t}",
                      f'<div class="tools"><button onclick="cpBlock(\'cf-{i}\',this)">Копировать блок для Confluence</button></div>'
                      f'<div id="cf-{i}-body">{fn()}</div>'))
    extra.append(("files", "Файлы для скачивания", downloads_html()))
    intro = ("<p class='muted'>Всё в одном файле: описание процесса, схемы, ТРЗ и FTE (с калькулятором), ревью, готовые тексты для Confluence "
             "(у каждого блока кнопка копирования) и файлы для скачивания. В конце каждого раздела — поле «Ваши правки».</p>")
    html = B.build_html(pages, extra=extra, trz=C.page_trz() + calc_html(),
                        title="Процесс выпуска релиза ЕАРМ — материалы для ревью", comments=True)
    html = html.replace("<main>", "<main>" + intro, 1)
    html = html.replace("</style>", EXTRA_CSS + "</style>", 1)
    html = html.replace("</body>", f"<script>{COPY_JS}</script></body>", 1)
    OUT.write_text(html, encoding="utf-8")
    print("OK:", OUT, f"{len(html) // 1024} KB")


if __name__ == "__main__":
    main()
