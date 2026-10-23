#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Раздел «Фактический календарь релизов»: план по этапам + поля для фактических дат, отклонения, статусы, график план/факт."""

from __future__ import annotations

import json

import planning as P
import process_data as D

CSS_FACT = r"""
.fx-top{display:flex;gap:14px;flex-wrap:wrap;align-items:flex-end;margin:6px 0 12px}
.fx-top label{font-size:12px;color:var(--ink-2);display:flex;flex-direction:column;gap:3px}
.fx-top input[type=date],.fx-top input[type=text]{font:inherit;border:1px solid #FBAE40;background:#FFE9CC;border-radius:3px;padding:4px 6px}
.fx-top button,.fx-btn{border:1px solid var(--line);background:#fff;color:#140093;border-radius:6px;padding:6px 12px;font:inherit;font-size:12px;font-weight:700;cursor:pointer}
.fx-top button:hover,.fx-btn:hover{background:var(--lime)}
.fx-table{overflow:auto;max-height:80vh;background:#fff;border:1px solid var(--line);border-radius:6px;box-shadow:var(--sh-1)}
.fx-table table{border-collapse:separate;border-spacing:0;font-size:12px;width:100%}
.fx-table th{position:sticky;top:0;z-index:2;background:#140093;color:#fff;font-size:10px;letter-spacing:.05em;text-transform:uppercase;padding:7px 8px;white-space:nowrap}
.fx-table td{padding:3px 8px;border-bottom:1px solid #F0F2F6;white-space:nowrap}
.fx-table tr.ph td{background:#EEEDF8;color:#140093;font-weight:700;font-size:10px;letter-spacing:.08em;text-transform:uppercase}
.fx-table td.pl{background:#F7F8FB;color:#42526E}
.fx-table input[type=date]{font:inherit;font-size:11px;border:1px solid #FBAE40;background:#FFE9CC;border-radius:3px;padding:2px 3px;width:128px}
.fx-table input.nt{font:inherit;font-size:11px;border:1px solid #FBAE40;background:#FFE9CC;border-radius:3px;padding:2px 5px;width:220px}
.fx-table td.dv{text-align:center;font-weight:700}.dv.late{color:#B3260E}.dv.early{color:#006644}
.st2{display:inline-block;padding:1px 8px;border-radius:9px;font-size:11px;font-weight:700}
.st2.nd{background:#DFE1E6;color:#42526E}.st2.wk{background:#DEEBFF;color:#0052CC}.st2.dn{background:#E3FCEF;color:#006644}.st2.ov{background:#FDE4DC;color:#B3260E}.st2.sk{background:#F4F5F7;color:#8A8A8A}
.fx-ov tr.sel td{background:#EEEDF8}.fx-ov tbody tr{cursor:pointer}.fx-ov tbody tr:hover td{background:#F4F1FF}
"""

JS = r"""
(function(){
var DATA=__DATA__,ID=DATA.ids,KEY='rp-fact-v1',MO=__MO__,HOL={};DATA.hol.forEach(function(h){HOL[h]=1});
var ST={};try{ST=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){ST={}}
function save(){try{localStorage.setItem(KEY,JSON.stringify(ST))}catch(e){}}
var cur=0,today=new Date().toISOString().slice(0,10);
function D0(s){var p=s.split('-');return new Date(Date.UTC(+p[0],+p[1]-1,+p[2]))}
function iso(d){return d.toISOString().slice(0,10)}
function isWd(d){var w=d.getUTCDay();return w>=1&&w<=5&&!HOL[iso(d)]}
function addWd(s,n){var d=D0(s),st=n>=0?1:-1;while(n){d=new Date(d.getTime()+st*864e5);if(isWd(d))n-=st}return iso(d)}
function wdDiff(a,b){if(!a||!b)return null;var x=D0(a),y=D0(b),sg=1,n=0;if(y<x){var t=x;x=y;y=t;sg=-1}while(x<y){x=new Date(x.getTime()+864e5);if(isWd(x))n++}return n*sg}
function fm(s){if(!s)return '—';var d=D0(s);return d.getUTCDate()+' '+MO[d.getUTCMonth()]+' '+String(d.getUTCFullYear()).slice(2)}
function rst(i){var b=DATA.rels[i],o=ST[b.name]||(ST[b.name]={});if(!o.steps)o.steps={};return o}
function plan(i){var b=DATA.rels[i],o=rst(i),day0=o.start||b.day0,psi=(o.psi===undefined)?b.psi:o.psi,cols=[],c;
 for(c=0;c<=50;c++)cols.push(addWd(day0,c));var out={};
 DATA.steps.forEach(function(s){var a=psi?s.a1:s.a0,b2=psi?s.b1:s.b0,c0,c1;if(b2>a){c0=Math.floor(a);c1=Math.floor(b2)-1}else{c0=c1=Math.max(Math.floor(a)-1,0)}
  out[s.n]={s:cols[c0],e:cols[Math.max(c1,c0)],skip:(s.n===ID.psi&&!psi),days:(s.n===ID.psi&&!psi)?0:s.d}});
 return {day0:day0,psi:psi,p:out}}
function esc(pl){var od=wdDiff(pl.e,today);return od>5?'эскалация: руководство НЕДРА':od>3?'эскалация: ВНП, РП':od>1?'эскалация: Release owner':'просрочен'}
function status(pl,f){if(pl.skip)return ['sk','пропуск'];if(f&&f.fe)return ['dn','готово'];if(f&&f.fs)return [(today>pl.e?'ov':'wk'),(today>pl.e?esc(pl):'в работе')];return [(today>pl.e?'ov':'nd'),(today>pl.e?esc(pl):'не начат')]}
function dev(pl,f){if(pl.skip)return null;if(f&&f.fe)return wdDiff(pl.e,f.fe);if(today>pl.e)return wdDiff(pl.e,today);return null}
function summary(i){var o=rst(i),P0=plan(i),done=0,tot=0,last=null,lastDev=null;
 DATA.steps.forEach(function(s){var pl=P0.p[s.n];if(pl.skip)return;tot++;var f=o.steps[s.n];if(f&&f.fe){done++;last=s.n;lastDev=wdDiff(pl.e,f.fe)}});
 var prodF=(o.steps[ID.prod]||{}).fe,closeF=(o.steps[ID.close]||{}).fe,dv=P0.p[ID.prod]?wdDiff(P0.p[ID.prod].e,prodF):null;
 var st=closeF?'закрыт':(done?'в работе':(today>P0.p[1].e?'не начат (просрочка)':'план'));
 return {P:P0,done:done,tot:tot,lastDev:lastDev,prodPlan:P0.p[ID.prod].e,prodFact:prodF,devProd:dv,closePlan:P0.p[ID.close].e,closeFact:closeF,st:st}}
function devCell(v){if(v===null||v===undefined)return '<td class="dv">—</td>';return '<td class="dv '+(v>0?'late':(v<0?'early':''))+'">'+(v>0?'+':'')+v+'</td>'}
function chart(i){var o=rst(i),P0=plan(i),rows=DATA.steps.filter(function(s){return !P0.p[s.n].skip}),
 mn=P0.p[1].s,mx=P0.p[ID.close].e;rows.forEach(function(s){var f=o.steps[s.n]||{};[f.fs,f.fe].forEach(function(x){if(x){if(x<mn)mn=x;if(x>mx)mx=x}})});if(today>mx&&Object.keys(o.steps).length)mx=today;
 var d0=D0(mn),days=Math.round((D0(mx)-d0)/864e5)+4,W=1000,L=250,rh=17,H=rows.length*rh+44,k=(W-L-20)/days;
 var X=function(s){return L+(Math.round((D0(s)-d0)/864e5))*k},sv='<svg class="chart" viewBox="0 0 '+W+' '+H+'" width="100%" role="img" aria-label="План и факт по этапам">';
 var m=new Date(d0.getTime());m.setUTCDate(1);m=new Date(Date.UTC(m.getUTCFullYear(),m.getUTCMonth()+1,1));
 while(m<=D0(mx)){var x=X(iso(m));sv+='<line x1="'+x+'" x2="'+x+'" y1="16" y2="'+(H-6)+'" stroke="#EEF1F6"/><text x="'+(x+3)+'" y="12" font-size="9" fill="#6B778C">'+MO[m.getUTCMonth()]+'</text>';m=new Date(Date.UTC(m.getUTCFullYear(),m.getUTCMonth()+1,1))}
 rows.forEach(function(s,j){var y=22+j*rh,pl=P0.p[s.n],f=o.steps[s.n]||{};
  sv+='<text x="'+(L-6)+'" y="'+(y+11)+'" font-size="9.5" text-anchor="end" fill="#333">'+s.n+'. '+s.t.slice(0,34)+'</text>';
  sv+='<rect x="'+X(pl.s)+'" y="'+(y+1)+'" width="'+Math.max((D0(pl.e)-D0(pl.s))/864e5*k+k,3)+'" height="6" fill="#C7D4DE" rx="1"><title>план '+fm(pl.s)+' – '+fm(pl.e)+'</title></rect>';
  if(f.fs||f.fe){var a=f.fs||f.fe,b=f.fe||today,late=f.fe?wdDiff(pl.e,f.fe)>0:today>pl.e;
   sv+='<rect x="'+X(a)+'" y="'+(y+8)+'" width="'+Math.max((D0(b)-D0(a))/864e5*k+k,3)+'" height="6" fill="'+(late?'#F26B43':'#140093')+'" rx="1" '+(f.fe?'':'opacity=".55"')+'><title>факт '+fm(a)+' – '+(f.fe?fm(f.fe):'в работе')+'</title></rect>'}});
 var tx=X(today);if(today>=mn&&today<=mx)sv+='<line x1="'+tx+'" x2="'+tx+'" y1="16" y2="'+(H-6)+'" stroke="#E5493A" stroke-width="1.5"/><text x="'+(tx+3)+'" y="'+(H-1)+'" font-size="9" fill="#E5493A">дата отчёта</text>';
 return sv+'</svg><div class="legend"><span><i style="background:#C7D4DE"></i>план</span><span><i style="background:#140093"></i>факт в срок</span><span><i style="background:#F26B43"></i>факт с опозданием</span></div>'}
var box=document.getElementById('fx');
function render(){var s=summary(cur),o=rst(cur),P0=s.P,rel=DATA.rels[cur];
 var ov='<div class="tw fx-ov"><table><thead><tr><th>Релиз</th><th>Старт, план</th><th>Деплой в Прод, план</th><th>Деплой в Прод, факт</th><th>Откл., раб. дн.</th><th>Этапов готово</th><th>Закрытие, план</th><th>Закрытие, факт</th><th>Статус</th></tr></thead><tbody>'
  +DATA.rels.map(function(r,i){var q=summary(i);return '<tr data-i="'+i+'" class="'+(i===cur?'sel':'')+'"><td><b>'+r.name+'</b></td><td>'+fm(q.P.day0)+'</td><td>'+fm(q.prodPlan)+'</td><td>'+fm(q.prodFact)+'</td>'+devCell(q.devProd)+'<td>'+q.done+' / '+q.tot+'</td><td>'+fm(q.closePlan)+'</td><td>'+fm(q.closeFact)+'</td><td>'+q.st+'</td></tr>'}).join('')+'</tbody></table></div>';
 var fin=0,ontime=0;DATA.rels.forEach(function(r,i){var q=summary(i);if(q.prodFact){fin++;if(q.devProd<=0)ontime++}});
 var kp='<div class="kpis"><div class="kpi"><b>'+fin+' / '+DATA.rels.length+'</b><span>релизов выкачено в Прод</span><small>по фактической дате этапа «Деплой в Прод»</small></div>'
  +'<div class="kpi '+(fin&&ontime<fin?'warn':'ok')+'"><b>'+(fin?Math.round(ontime/fin*100)+'%':'—')+'</b><span>в срок</span><small>Прод не позже плана — метрика «Выполнение релизов по плану»</small></div>'
  +'<div class="kpi"><b>'+s.done+' / '+s.tot+'</b><span>этапов готово: '+rel.name+'</span><small>'+s.st+'</small></div>'
  +'<div class="kpi '+(s.lastDev>0?'bad':'ok')+'"><b>'+(s.lastDev===null?'—':(s.lastDev>0?'+':'')+s.lastDev)+'</b><span>откл. последнего этапа, раб. дн.</span><small>+ опоздание, − опережение; прогноз закрытия: '+(s.lastDev===null?fm(s.closePlan):fm(addWd(s.closePlan,s.lastDev)))+'</small></div></div>';
 var rows='',last=0;DATA.steps.forEach(function(st){var pl=P0.p[st.n],f=o.steps[st.n]||{},stt=status(pl,f),dv=dev(pl,f);
  if(st.ph!==last){last=st.ph;rows+='<tr class="ph"><td colspan="11">'+DATA.ph[st.ph]+'</td></tr>'}
  rows+='<tr><td><b>'+st.n+'</b></td><td>'+st.t+(pl.skip?' <span class="muted">(не нужен)</span>':'')+'</td><td>'+st.w+'</td><td style="text-align:center">'+pl.days+'</td><td class="pl">'+fm(pl.s)+'</td><td class="pl">'+fm(pl.e)+'</td>'
   +'<td><input type="date" data-n="'+st.n+'" data-f="fs" value="'+(f.fs||'')+'"'+(pl.skip?' disabled':'')+'></td><td><input type="date" data-n="'+st.n+'" data-f="fe" value="'+(f.fe||'')+'"'+(pl.skip?' disabled':'')+'></td>'
   +devCell(dv)+'<td><span class="st2 '+stt[0]+'">'+stt[1]+'</span></td><td><input class="nt" type="text" data-n="'+st.n+'" data-f="note" placeholder="причина, комментарий" value="'+((f.note||'').replace(/"/g,'&quot;'))+'"></td></tr>'});
 var top='<div class="fx-top"><label>Дата отчёта (для статусов) <input type="date" id="fx-today" value="'+today+'"></label>'
  +'<label>Старт релиза (этап 1), план <input type="date" id="fx-start" value="'+P0.day0+'"></label>'
  +'<label>ПСИ ИБ <select id="fx-psi" style="font:inherit;border:1px solid #FBAE40;background:#FFE9CC;border-radius:3px;padding:4px"><option value="0"'+(P0.psi?'':' selected')+'>не нужен</option><option value="1"'+(P0.psi?' selected':'')+'>нужен</option></select></label>'
  +'<button id="fx-clr">Очистить факт релиза</button><button id="fx-rst">Вернуть план релиза</button>'
  +'<span style="flex:1"></span><button id="fx-csv">Скачать CSV</button><button id="fx-json">Скачать JSON</button><button id="fx-imp">Загрузить JSON</button><input type="file" id="fx-file" accept=".json" style="display:none"><button id="fx-all">Очистить всё</button></div>';
 var sel='<div class="rsel" id="fx-sel">'+DATA.rels.map(function(r,i){return '<button data-i="'+i+'" class="'+(i===cur?'on':'')+'">'+r.name+'</button>'}).join('')+'</div>';
 var sc=box.scrollTop;
 box.innerHTML='<h3 style="margin-top:6px">Сводка по релизам</h3>'+ov+kp+'<h3>Релиз '+rel.name+'</h3>'+sel+top
  +'<div class="tabs own" data-g="fx"><button class="on" data-p="t">Таблица этапов</button><button data-p="c">График план / факт</button></div>'
  +'<div class="pane on" data-g="fx" data-p="t"><div class="fx-table"><table><thead><tr><th>№</th><th>Этап</th><th>Ответственный</th><th>Дн.</th><th>План с</th><th>План по</th><th>Факт с</th><th>Факт по</th><th>Откл., раб. дн.</th><th>Статус</th><th>Комментарий</th></tr></thead><tbody>'+rows+'</tbody></table></div></div>'
  +'<div class="pane" data-g="fx" data-p="c"><div class="card">'+chart(cur)+'</div></div>';
 bind()}
var tab='t';
function bind(){
 box.querySelectorAll('.tabs.own button').forEach(function(b){b.classList.toggle('on',b.dataset.p===tab);b.onclick=function(){tab=b.dataset.p;box.querySelectorAll('.tabs.own button').forEach(function(x){x.classList.toggle('on',x===b)});box.querySelectorAll('.pane[data-g="fx"]').forEach(function(p){p.classList.toggle('on',p.dataset.p===tab)})}});
 box.querySelectorAll('.pane[data-g="fx"]').forEach(function(p){p.classList.toggle('on',p.dataset.p===tab)});
 box.querySelectorAll('#fx-sel button,.fx-ov tbody tr').forEach(function(b){b.onclick=function(){cur=+b.dataset.i;render()}});
 box.querySelectorAll('.fx-table input').forEach(function(i){i.onchange=function(){var o=rst(cur),f=o.steps[i.dataset.n]||(o.steps[i.dataset.n]={});f[i.dataset.f]=i.value;if(!f.fs&&!f.fe&&!f.note)delete o.steps[i.dataset.n];save();render()}});
 document.getElementById('fx-today').onchange=function(){today=this.value||today;render()};
 document.getElementById('fx-start').onchange=function(){if(this.value){rst(cur).start=this.value;save();render()}};
 document.getElementById('fx-psi').onchange=function(){rst(cur).psi=this.value==='1';save();render()};
 document.getElementById('fx-clr').onclick=function(){if(confirm('Очистить фактические даты релиза '+DATA.rels[cur].name+'?')){rst(cur).steps={};save();render()}};
 document.getElementById('fx-rst').onclick=function(){var o=rst(cur);delete o.start;delete o.psi;save();render()};
 document.getElementById('fx-all').onclick=function(){if(confirm('Очистить фактические даты и правки плана по всем релизам?')){ST={};save();render()}};
 document.getElementById('fx-json').onclick=function(){dl(JSON.stringify(ST,null,1),'application/json','факт-релизов.json')};
 document.getElementById('fx-csv').onclick=function(){var L=['Релиз;№;Этап;Ответственный;План с;План по;Факт с;Факт по;Откл. раб. дн.;Статус;Комментарий'];
  DATA.rels.forEach(function(r,i){var o=rst(i),P0=plan(i);DATA.steps.forEach(function(s){var pl=P0.p[s.n],f=o.steps[s.n]||{},d=dev(pl,f),stt=status(pl,f);L.push([r.name,s.n,s.t,s.w,pl.s,pl.e,f.fs||'',f.fe||'',d===null?'':d,stt[1],(f.note||'').replace(/[;\n]/g,' ')].join(';'))})});
  dl('﻿'+L.join('\n'),'text/csv;charset=utf-8','календарь-релизов-план-факт.csv')};
 document.getElementById('fx-imp').onclick=function(){document.getElementById('fx-file').click()};
 document.getElementById('fx-file').onchange=function(){var f=this.files[0];if(!f)return;var rd=new FileReader();rd.onload=function(){try{ST=JSON.parse(rd.result);save();render()}catch(e){alert('Не удалось прочитать файл')}};rd.readAsText(f)}}
function dl(t,m,n){var b=new Blob([t],{type:m}),a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=n;a.click()}
render();
})();
"""


def fact_html(rels) -> str:
    steps = []
    s0, s1 = D.schedule(False), D.schedule(True)
    for n in D.SN:
        steps.append({"n": n, "t": D.STEP_NAME[n], "w": D.role_short(D.SN[n][3]), "ph": D.SN[n][1], "d": P.days_txt(n),
                      "a0": s0[n][0], "b0": s0[n][1], "a1": s1[n][0], "b1": s1[n][1]})
    data = {"steps": steps, "ph": {str(k): v for k, v in D.PHASES.items()},
            "rels": [{"name": r["name"], "day0": r["day0"].isoformat(), "psi": r["psi"]} for r in rels],
            "ids": D.ID, "hol": sorted(d.isoformat() for d in P.HOLIDAYS)}
    js = JS.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__MO__", json.dumps(P.MONTHS, ensure_ascii=False))
    return ("<p>Фактический календарь: план по каждому этапу считается из SLA и стартовой даты релиза; рядом — поля для <b>фактических дат начала и окончания</b>. "
            "По ним считаются отклонение в рабочих днях, статус этапа, сводка по релизам, прогноз закрытия и график «план / факт». "
            "Можно сдвинуть старт релиза и отметить, нужен ли ПСИ ИБ — план пересчитается.</p>"
            '<p class="muted">Введённые даты сохраняются в этом браузере (localStorage). Чтобы передать коллегам или перенести — «Скачать JSON» / «Загрузить JSON»; для отчёта — «Скачать CSV».</p>'
            '<div id="fx"></div><script>' + js + "</script>")
