#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Календари релизов: сводка в разделе 7 и отдельная редактируемая страница на каждый релиз (#rel=<имя>).

Состояние хранится в RP (edit_layer.py): RP.get('fact')[<релиз>] = {start, psi, fid, svcs, owner, notes,
steps: {n: {fs, fe, note, ps, pe, w}}, extra: [{name, w, ps, pe, fs, fe, note}]}.
Формат совместим с прежним календарём фактов (rp-fact-v1).
"""

from __future__ import annotations

import json

import planning as P
import process_data as D

CSS = r"""
.relpage{display:none;background:var(--bg);min-height:100vh}
body.relmode>header.top,body.relmode>nav,body.relmode>main{display:none}
body.relmode .relpage{display:block}
.rp-head{background:linear-gradient(120deg,#1B08A6,#140093 55%,#10007A);color:#fff;padding:22px 56px 18px;box-shadow:0 6px 24px rgba(20,0,147,.16)}
.rp-head h1{font-size:30px;color:#fff;margin:8px 0 4px}.rp-head .muted{color:#C9C4F2}
.rp-head a.back{color:var(--lime);font-weight:700;text-decoration:none;font-size:14px}
.rp-pills{display:flex;gap:6px;flex-wrap:wrap;margin-top:12px}
.rp-pills a{background:rgba(255,255,255,.12);color:#fff;border-radius:6px;padding:4px 10px;font-size:12px;font-weight:700;text-decoration:none}
.rp-pills a.on{background:var(--lime);color:#140093}
.rp-body{padding:18px 56px 90px;max-width:1700px;margin:0 auto}
@media(max-width:900px){.rp-head,.rp-body{padding-left:16px;padding-right:16px}}
.fx-top{display:flex;gap:14px;flex-wrap:wrap;align-items:flex-end;margin:10px 0 12px}
.fx-top label{font-size:12px;color:var(--ink-2);display:flex;flex-direction:column;gap:3px}
.fx-top input[type=date],.fx-top input[type=text],.fx-top select{font:inherit;border:1px solid #FBAE40;background:#FFE9CC;border-radius:3px;padding:4px 6px}
.fx-top button,.fx-btn{border:1px solid var(--line);background:#fff;color:#140093;border-radius:6px;padding:6px 12px;font:inherit;font-size:12px;font-weight:700;cursor:pointer}
.fx-top button:hover,.fx-btn:hover{background:var(--lime)}
.fx-table{overflow:auto;max-height:78vh;background:#fff;border:1px solid var(--line);border-radius:6px;box-shadow:var(--sh-1)}
.fx-table table{border-collapse:separate;border-spacing:0;font-size:12px;width:100%}
.fx-table th{position:sticky;top:0;z-index:2;background:#140093;color:#fff;font-size:10px;letter-spacing:.05em;text-transform:uppercase;padding:7px 8px;white-space:nowrap}
.fx-table td{padding:3px 8px;border-bottom:1px solid #F0F2F6;white-space:nowrap}
.fx-table tr.ph td{background:#EEEDF8;color:#140093;font-weight:700;font-size:10px;letter-spacing:.08em;text-transform:uppercase}
.fx-table input[type=date]{font:inherit;font-size:11px;border:1px solid #FBAE40;background:#FFE9CC;border-radius:3px;padding:2px 3px;width:128px}
.fx-table input[type=date].ovr{border-color:#904EE2;background:#EEE6FB}
.fx-table input.nt,.fx-table input.nm,.fx-table input.rl{font:inherit;font-size:11px;border:1px solid #FBAE40;background:#FFE9CC;border-radius:3px;padding:2px 5px}
.fx-table input.nt{width:230px}.fx-table input.nm{width:220px}.fx-table input.rl{width:130px}
.fx-table td.dv{text-align:center;font-weight:700}.dv.late{color:#B3260E}.dv.early{color:#006644}
.fx-table .rs{border:0;background:none;color:#904EE2;cursor:pointer;font-size:13px}
.st2{display:inline-block;padding:1px 8px;border-radius:9px;font-size:11px;font-weight:700}
.st2.nd{background:#DFE1E6;color:#42526E}.st2.wk{background:#DEEBFF;color:#0052CC}.st2.dn{background:#E3FCEF;color:#006644}.st2.ov{background:#FDE4DC;color:#B3260E}.st2.sk{background:#F4F5F7;color:#8A8A8A}
.fx-ov tbody tr{cursor:pointer}.fx-ov tbody tr:hover td{background:#F4F1FF}
.fx-ov a.op{color:#140093;font-weight:700;text-decoration:none;border:1px solid #140093;border-radius:6px;padding:3px 10px;font-size:12px}
.fx-ov a.op:hover{background:#CFF85E}
.rp-notes{width:100%;min-height:220px;font:inherit;border:1px solid #FBAE40;background:#FFF6E8;border-radius:6px;padding:10px}
"""

JS = r"""
(function(){
var DATA=__DATA__,ID=DATA.ids,MO=__MO__,HOL={};DATA.hol.forEach(function(h){HOL[h]=1});
var FS=RP.get('fact')||{};function saveF(){RP.set('fact',FS)}
var cur=0,today=RP.get('today')||new Date().toISOString().slice(0,10);
function D0(s){var p=s.split('-');return new Date(Date.UTC(+p[0],+p[1]-1,+p[2]))}
function iso(d){return d.toISOString().slice(0,10)}
function isWd(d){var w=d.getUTCDay();return w>=1&&w<=5&&!HOL[iso(d)]}
function addWd(s,n){var d=D0(s),st=n>=0?1:-1;while(n){d=new Date(d.getTime()+st*864e5);if(isWd(d))n-=st}return iso(d)}
function wdDiff(a,b){if(!a||!b)return null;var x=D0(a),y=D0(b),sg=1,n=0;if(y<x){var t=x;x=y;y=t;sg=-1}while(x<y){x=new Date(x.getTime()+864e5);if(isWd(x))n++}return n*sg}
function fm(s){if(!s)return '—';var d=D0(s);return d.getUTCDate()+' '+MO[d.getUTCMonth()]+' '+String(d.getUTCFullYear()).slice(2)}
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;')}
function rst(i){var b=DATA.rels[i],o=FS[b.name]||(FS[b.name]={});if(!o.steps)o.steps={};if(!o.extra)o.extra=[];return o}
function plan(i){var b=DATA.rels[i],o=rst(i),day0=o.start||b.day0,psi=(o.psi===undefined)?b.psi:o.psi,cols=[],c;
 for(c=0;c<=60;c++)cols.push(addWd(day0,c));var out={};
 DATA.steps.forEach(function(s){var a=psi?s.a1:s.a0,b2=psi?s.b1:s.b0,c0,c1;if(b2>a){c0=Math.floor(a);c1=Math.floor(b2)-1}else{c0=c1=Math.max(Math.floor(a)-1,0)}
  var ov=o.steps[s.n]||{},skip=(s.n===ID.psi&&!psi),ps=ov.ps||cols[c0],pe=ov.pe||cols[Math.max(c1,c0)];
  out[s.n]={s:ps,e:pe,skip:skip,days:skip?0:(ov.ps||ov.pe?wdDiff(ps,pe)+1:s.d),ovr:!!(ov.ps||ov.pe)}});
 return {day0:day0,psi:psi,p:out}}
function esclab(pl){var od=wdDiff(pl.e,today);return od>5?'эскалация: руководство НЕДРА':od>3?'эскалация: ВНП, РП':od>1?'эскалация: Release owner':'просрочен'}
function status(pl,f){if(pl.skip)return ['sk','пропуск'];if(f&&f.fe)return ['dn','готово'];if(f&&f.fs)return [(today>pl.e?'ov':'wk'),(today>pl.e?esclab(pl):'в работе')];return [(today>pl.e?'ov':'nd'),(today>pl.e?esclab(pl):'не начат')]}
function dev(pl,f){if(pl.skip)return null;if(f&&f.fe)return wdDiff(pl.e,f.fe);if(today>pl.e)return wdDiff(pl.e,today);return null}
function summary(i){var o=rst(i),P0=plan(i),done=0,tot=0,lastDev=null;
 DATA.steps.forEach(function(s){var pl=P0.p[s.n];if(pl.skip)return;tot++;var f=o.steps[s.n];if(f&&f.fe){done++;lastDev=wdDiff(pl.e,f.fe)}});
 var prodF=(o.steps[ID.prod]||{}).fe,closeF=(o.steps[ID.close]||{}).fe,dv=wdDiff(P0.p[ID.prod].e,prodF);
 var st=closeF?'закрыт':(done?'в работе':(today>P0.p[1].e?'не начат (просрочка)':'план'));
 return {P:P0,done:done,tot:tot,lastDev:lastDev,prodPlan:P0.p[ID.prod].e,prodFact:prodF,devProd:dv,closePlan:P0.p[ID.close].e,closeFact:closeF,st:st}}
function devCell(v){if(v===null||v===undefined)return '<td class="dv">—</td>';return '<td class="dv '+(v>0?'late':(v<0?'early':''))+'">'+(v>0?'+':'')+v+'</td>'}
function dl(t,m,n){var b=new Blob([t],{type:m}),a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=n;document.body.appendChild(a);a.click();setTimeout(function(){a.remove()},500)}

/* ---------- сводка (раздел 7) ---------- */
function renderOverview(){var box=document.getElementById('fx');if(!box)return;
 var fin=0,ontime=0;DATA.rels.forEach(function(r,i){var q=summary(i);if(q.prodFact){fin++;if(q.devProd<=0)ontime++}});
 var ov='<div class="tw fx-ov"><table><thead><tr><th>Релиз</th><th>Старт, план</th><th>Деплой в Прод, план</th><th>Деплой в Прод, факт</th><th>Откл., раб. дн.</th><th>Этапов готово</th><th>Закрытие, план</th><th>Закрытие, факт</th><th>Статус</th><th></th></tr></thead><tbody>'
  +DATA.rels.map(function(r,i){var q=summary(i);return '<tr data-i="'+i+'"><td><b>'+r.name+'</b></td><td>'+fm(q.P.day0)+'</td><td>'+fm(q.prodPlan)+'</td><td>'+fm(q.prodFact)+'</td>'+devCell(q.devProd)+'<td>'+q.done+' / '+q.tot+'</td><td>'+fm(q.closePlan)+'</td><td>'+fm(q.closeFact)+'</td><td>'+q.st+'</td><td><a class="op" href="#rel='+encodeURIComponent(r.name)+'">Открыть страницу</a></td></tr>'}).join('')+'</tbody></table></div>';
 var kp='<div class="kpis"><div class="kpi"><b>'+fin+' / '+DATA.rels.length+'</b><span>релизов выкачено в Прод</span><small>по фактической дате этапа «Деплой в Прод»</small></div>'
  +'<div class="kpi '+(fin&&ontime<fin?'warn':'ok')+'"><b>'+(fin?Math.round(ontime/fin*100)+'%':'—')+'</b><span>в срок</span><small>Прод не позже плана — метрика «Выполнение релизов по плану»</small></div></div>';
 box.innerHTML='<div class="fx-top"><label>Дата отчёта (для статусов) <input type="date" id="fx-today" value="'+today+'"></label></div>'+kp+ov;
 box.querySelectorAll('.fx-ov tbody tr').forEach(function(tr){tr.onclick=function(ev){if(ev.target.tagName!=='A')location.hash='#rel='+encodeURIComponent(DATA.rels[+tr.dataset.i].name)}});
 document.getElementById('fx-today').onchange=function(){today=this.value||today;RP.set('today',today);renderOverview()}}

/* ---------- страница релиза ---------- */
function chart(i){var o=rst(i),P0=plan(i),rows=DATA.steps.filter(function(s){return !P0.p[s.n].skip}),
 mn=P0.p[1].s,mx=P0.p[ID.close].e;rows.forEach(function(s){var f=o.steps[s.n]||{};[f.fs,f.fe,P0.p[s.n].s,P0.p[s.n].e].forEach(function(x){if(x){if(x<mn)mn=x;if(x>mx)mx=x}})});if(today>mx&&Object.keys(o.steps).length)mx=today;
 var d0=D0(mn),days=Math.round((D0(mx)-d0)/864e5)+4,W=1000,L=250,rh=17,H=rows.length*rh+44,k=(W-L-20)/days;
 var X=function(s){return L+(Math.round((D0(s)-d0)/864e5))*k},sv='<svg class="chart" viewBox="0 0 '+W+' '+H+'" style="width:100%" role="img" aria-label="План и факт по этапам">';
 var m=new Date(Date.UTC(d0.getUTCFullYear(),d0.getUTCMonth()+1,1));
 while(m<=D0(mx)){var x=X(iso(m));sv+='<line x1="'+x+'" x2="'+x+'" y1="16" y2="'+(H-6)+'" stroke="#EEF1F6"/><text x="'+(x+3)+'" y="12" font-size="10" fill="#6B778C">'+MO[m.getUTCMonth()]+'</text>';m=new Date(Date.UTC(m.getUTCFullYear(),m.getUTCMonth()+1,1))}
 rows.forEach(function(s,j){var y=22+j*rh,pl=P0.p[s.n],f=o.steps[s.n]||{};
  sv+='<text x="'+(L-6)+'" y="'+(y+11)+'" font-size="10.5" text-anchor="end" fill="#333">'+s.n+'. '+esc(s.t).slice(0,36)+'</text>';
  sv+='<rect x="'+X(pl.s)+'" y="'+(y+1)+'" width="'+Math.max((D0(pl.e)-D0(pl.s))/864e5*k+k,3)+'" height="6" fill="'+(pl.ovr?'#C9B5F2':'#C7D4DE')+'" rx="1"><title>план '+fm(pl.s)+' – '+fm(pl.e)+'</title></rect>';
  if(f.fs||f.fe){var a=f.fs||f.fe,b=f.fe||today,late=f.fe?wdDiff(pl.e,f.fe)>0:today>pl.e;
   sv+='<rect x="'+X(a)+'" y="'+(y+8)+'" width="'+Math.max((D0(b)-D0(a))/864e5*k+k,3)+'" height="6" fill="'+(late?'#F26B43':'#140093')+'" rx="1" '+(f.fe?'':'opacity=".55"')+'><title>факт '+fm(a)+' – '+(f.fe?fm(f.fe):'в работе')+'</title></rect>'}});
 var tx=X(today);if(today>=mn&&today<=mx)sv+='<line x1="'+tx+'" x2="'+tx+'" y1="16" y2="'+(H-6)+'" stroke="#E5493A" stroke-width="1.5"/><text x="'+(tx+3)+'" y="'+(H-1)+'" font-size="10" fill="#E5493A">дата отчёта</text>';
 return sv+'</svg><div class="legend"><span><i style="background:#C7D4DE"></i>план</span><span><i style="background:#C9B5F2"></i>план изменён вручную</span><span><i style="background:#140093"></i>факт в срок</span><span><i style="background:#F26B43"></i>факт с опозданием</span></div>'}

var tab='t';
function renderPage(){var rp=document.getElementById('relpages');if(!rp)return;var rel=DATA.rels[cur],o=rst(cur),P0=plan(cur),s=summary(cur);
 var pills=DATA.rels.map(function(r,i){return '<a href="#rel='+encodeURIComponent(r.name)+'" class="'+(i===cur?'on':'')+'">'+r.name+'</a>'}).join('');
 var head='<div class="rp-head"><a class="back" href="#fact">← к отчёту, раздел «Фактический календарь»</a><h1>'+rel.name+' · календарь релиза</h1><div class="muted">Плановые даты считаются из SLA и стартовой даты; любое поле можно изменить. Всё сохраняется автоматически; кнопка «Сохранить HTML» внизу делает копию файла со всеми данными.</div><div class="rp-pills">'+pills+'</div></div>';
 var fin=s.prodFact?'выкачен':'';
 var kp='<div class="kpis"><div class="kpi"><b>'+s.done+' / '+s.tot+'</b><span>этапов готово</span><small>'+s.st+'</small></div>'
  +'<div class="kpi"><b>'+fm(s.prodPlan)+'</b><span>деплой в Прод, план</span><small>факт: '+fm(s.prodFact)+'</small></div>'
  +'<div class="kpi '+(s.devProd>0?'bad':'ok')+'"><b>'+(s.devProd===null?'—':(s.devProd>0?'+':'')+s.devProd)+'</b><span>откл. Прода, раб. дн.</span><small>+ опоздание, − опережение</small></div>'
  +'<div class="kpi '+(s.lastDev>0?'bad':'ok')+'"><b>'+(s.lastDev===null?'—':(s.lastDev>0?'+':'')+s.lastDev)+'</b><span>откл. последнего этапа, раб. дн.</span><small>прогноз закрытия: '+(s.lastDev===null?fm(s.closePlan):fm(addWd(s.closePlan,s.lastDev)))+'</small></div></div>';
 var top='<div class="fx-top"><label>ID релиза (Fix Version / тег)<input type="text" id="p-fid" value="'+esc(o.fid||rel.name)+'" size="14"></label>'
  +'<label>Старт релиза (этап 1), план<input type="date" id="p-start" value="'+P0.day0+'"></label>'
  +'<label>ПСИ ИБ<select id="p-psi"><option value="0"'+(P0.psi?'':' selected')+'>не нужен</option><option value="1"'+(P0.psi?' selected':'')+'>нужен</option></select></label>'
  +'<label>Release owner<input type="text" id="p-owner" value="'+esc(o.owner||'Акманов Арсен')+'" size="18"></label>'
  +'<label>Сервисы релиза<input type="text" id="p-svcs" value="'+esc(o.svcs||'')+'" size="34" placeholder="перечень сервисов"></label>'
  +'<label>Дата отчёта<input type="date" id="p-today" value="'+today+'"></label>'
  +'<button id="p-reset">Вернуть расчётный план</button><button id="p-clr">Очистить факт</button><span style="flex:1"></span><button id="p-csv">CSV</button><button id="p-json">JSON релиза</button><button id="p-print">Печать</button></div>';
 var rows='',last=0;DATA.steps.forEach(function(st){var pl=P0.p[st.n],f=o.steps[st.n]||{},stt=status(pl,f),dv=dev(pl,f);
  if(st.ph!==last){last=st.ph;rows+='<tr class="ph"><td colspan="12">'+DATA.ph[st.ph]+'</td></tr>'}
  rows+='<tr><td><b>'+st.n+'</b></td><td>'+esc(st.t)+(pl.skip?' <span class="muted">(не нужен)</span>':'')+'</td><td><input class="rl" data-n="'+st.n+'" data-f="w" value="'+esc(f.w!=null?f.w:st.w)+'"></td><td style="text-align:center">'+pl.days+'</td>'
   +'<td><input type="date" class="'+(pl.ovr?'ovr':'')+'" data-n="'+st.n+'" data-f="ps" value="'+pl.s+'"'+(pl.skip?' disabled':'')+'></td><td><input type="date" class="'+(pl.ovr?'ovr':'')+'" data-n="'+st.n+'" data-f="pe" value="'+pl.e+'"'+(pl.skip?' disabled':'')+'></td>'
   +'<td><input type="date" data-n="'+st.n+'" data-f="fs" value="'+(f.fs||'')+'"'+(pl.skip?' disabled':'')+'></td><td><input type="date" data-n="'+st.n+'" data-f="fe" value="'+(f.fe||'')+'"'+(pl.skip?' disabled':'')+'></td>'
   +devCell(dv)+'<td><span class="st2 '+stt[0]+'">'+stt[1]+'</span></td><td><input class="nt" type="text" data-n="'+st.n+'" data-f="note" placeholder="причина, комментарий" value="'+esc(f.note)+'"></td>'
   +'<td>'+(pl.ovr?'<button class="rs" data-n="'+st.n+'" title="вернуть расчётные даты плана">↺</button>':'')+'</td></tr>'});
 rows+='<tr class="ph"><td colspan="12">Свои этапы и задачи релиза</td></tr>';
 o.extra.forEach(function(x,k){var pl={s:x.ps||'',e:x.pe||''},stt=status({s:pl.s,e:pl.e||'9999-12-31',skip:false},x),dv=x.fe&&pl.e?wdDiff(pl.e,x.fe):null;
  rows+='<tr><td>+</td><td><input class="nm" data-x="'+k+'" data-f="name" value="'+esc(x.name)+'" placeholder="название этапа"></td><td><input class="rl" data-x="'+k+'" data-f="w" value="'+esc(x.w)+'"></td><td style="text-align:center">'+(x.ps&&x.pe?wdDiff(x.ps,x.pe)+1:'—')+'</td>'
   +'<td><input type="date" data-x="'+k+'" data-f="ps" value="'+(x.ps||'')+'"></td><td><input type="date" data-x="'+k+'" data-f="pe" value="'+(x.pe||'')+'"></td><td><input type="date" data-x="'+k+'" data-f="fs" value="'+(x.fs||'')+'"></td><td><input type="date" data-x="'+k+'" data-f="fe" value="'+(x.fe||'')+'"></td>'
   +devCell(dv)+'<td><span class="st2 '+stt[0]+'">'+stt[1]+'</span></td><td><input class="nt" type="text" data-x="'+k+'" data-f="note" value="'+esc(x.note)+'" placeholder="комментарий"></td><td><button class="rs" data-xd="'+k+'" title="удалить строку">✕</button></td></tr>'});
 var table='<div class="fx-table"><table><thead><tr><th>№</th><th>Этап</th><th>Ответственный</th><th>Дн.</th><th>План с</th><th>План по</th><th>Факт с</th><th>Факт по</th><th>Откл., раб. дн.</th><th>Статус</th><th>Комментарий</th><th></th></tr></thead><tbody>'+rows+'</tbody></table></div><p><button class="fx-btn" id="p-add">+ Добавить свой этап</button></p>';
 var notes='<p class="muted">Заметки по релизу: риски, решения, договорённости, состав. Сохраняются автоматически.</p><textarea class="rp-notes" id="p-notes" placeholder="Заметки по релизу…">'+esc(o.notes)+'</textarea>';
 rp.innerHTML=head+'<div class="rp-body">'+kp+top
  +'<div class="tabs own" data-g="rc"><button class="'+(tab==='t'?'on':'')+'" data-p="t">Таблица этапов</button><button class="'+(tab==='c'?'on':'')+'" data-p="c">График план / факт</button><button class="'+(tab==='n'?'on':'')+'" data-p="n">Заметки</button></div>'
  +'<div class="pane '+(tab==='t'?'on':'')+'" data-p="t">'+table+'</div><div class="pane '+(tab==='c'?'on':'')+'" data-p="c"><div class="card">'+chart(cur)+'</div></div><div class="pane '+(tab==='n'?'on':'')+'" data-p="n">'+notes+'</div></div>';
 bindPage()}
function bindPage(){var rp=document.getElementById('relpages'),o=rst(cur);
 rp.querySelectorAll('.tabs.own button').forEach(function(b){b.onclick=function(){tab=b.dataset.p;renderPage()}});
 rp.querySelectorAll('input[data-n]').forEach(function(i){i.onchange=function(){var n=i.dataset.n,f=o.steps[n]||(o.steps[n]={}),k=i.dataset.f,v=i.value;
  if(k==='ps'||k==='pe'){var P0=plan(cur);f[k]=v||undefined;if(!v)delete f[k]}else if(k==='w'){f.w=v}else{f[k]=v}
  if(!f.fs&&!f.fe&&!f.note&&!f.ps&&!f.pe&&(f.w===undefined))delete o.steps[n];saveF();renderPage()}});
 rp.querySelectorAll('input[data-x]').forEach(function(i){i.onchange=function(){o.extra[+i.dataset.x][i.dataset.f]=i.value;saveF();renderPage()}});
 rp.querySelectorAll('button.rs[data-n]').forEach(function(b){b.onclick=function(){var f=o.steps[b.dataset.n];if(f){delete f.ps;delete f.pe}saveF();renderPage()}});
 rp.querySelectorAll('button.rs[data-xd]').forEach(function(b){b.onclick=function(){o.extra.splice(+b.dataset.xd,1);saveF();renderPage()}});
 function $(id){return document.getElementById(id)}
 $('p-fid').onchange=function(){o.fid=this.value;saveF()};$('p-owner').onchange=function(){o.owner=this.value;saveF()};$('p-svcs').onchange=function(){o.svcs=this.value;saveF()};
 $('p-start').onchange=function(){if(this.value){o.start=this.value;saveF();renderPage()}};
 $('p-psi').onchange=function(){o.psi=this.value==='1';saveF();renderPage()};
 $('p-today').onchange=function(){today=this.value||today;RP.set('today',today);renderPage()};
 $('p-add').onclick=function(){o.extra.push({name:'',w:'',ps:'',pe:'',fs:'',fe:'',note:''});saveF();renderPage()};
 $('p-reset').onclick=function(){if(confirm('Вернуть расчётные плановые даты (старт, ПСИ и ручные правки плана)?')){delete o.start;delete o.psi;Object.keys(o.steps).forEach(function(n){delete o.steps[n].ps;delete o.steps[n].pe});saveF();renderPage()}};
 $('p-clr').onclick=function(){if(confirm('Очистить фактические даты и комментарии этапов релиза '+DATA.rels[cur].name+'?')){Object.keys(o.steps).forEach(function(n){var f=o.steps[n];delete f.fs;delete f.fe;delete f.note});saveF();renderPage()}};
 var nt=$('p-notes');if(nt)nt.oninput=function(){o.notes=nt.value;saveF()};
 $('p-print').onclick=function(){window.print()};
 $('p-json').onclick=function(){dl(JSON.stringify(o,null,1),'application/json',DATA.rels[cur].name+'.json')};
 $('p-csv').onclick=function(){var P0=plan(cur),L=['Релиз;№;Этап;Ответственный;План с;План по;Факт с;Факт по;Откл. раб. дн.;Статус;Комментарий'];
  DATA.steps.forEach(function(st){var pl=P0.p[st.n],f=o.steps[st.n]||{},d=dev(pl,f),stt=status(pl,f);L.push([DATA.rels[cur].name,st.n,st.t,(f.w!=null?f.w:st.w),pl.s,pl.e,f.fs||'',f.fe||'',d===null?'':d,stt[1],(f.note||'').replace(/[;\n]/g,' ')].join(';'))});
  o.extra.forEach(function(x){L.push([DATA.rels[cur].name,'+',x.name,x.w,x.ps,x.pe,x.fs,x.fe,'','',(x.note||'').replace(/[;\n]/g,' ')].join(';'))});
  dl('﻿'+L.join('\n'),'text/csv;charset=utf-8',DATA.rels[cur].name+'-календарь.csv')}}

/* ---------- маршрутизация ---------- */
function route(){var m=/^#rel=(.+)$/.exec(decodeURIComponent(location.hash)),rp=document.getElementById('relpages');
 if(m){var i=-1;DATA.rels.forEach(function(r,k){if(r.name===m[1])i=k});if(i>=0){cur=i;document.body.classList.add('relmode');rp.style.display='block';renderPage();window.scrollTo(0,0);return}}
 var was=document.body.classList.contains('relmode');document.body.classList.remove('relmode');if(rp){rp.style.display='';rp.innerHTML=''}renderOverview();
 if(was){var t=document.getElementById('fact');if(t)t.scrollIntoView()}}
window.addEventListener('hashchange',route);route();
})();
"""


def release_cal(rels):
    """Возвращает (HTML раздела со сводкой, HTML страниц релизов для вставки в конец body)."""
    steps = []
    s0, s1 = D.schedule(False), D.schedule(True)
    for n in D.SN:
        steps.append({"n": n, "t": D.STEP_NAME[n], "w": D.role_short(D.SN[n][3]), "ph": D.SN[n][1], "d": P.days_txt(n),
                      "a0": s0[n][0], "b0": s0[n][1], "a1": s1[n][0], "b1": s1[n][1]})
    data = {"steps": steps, "ph": {str(k): v for k, v in D.PHASES.items()}, "ids": D.ID,
            "rels": [{"name": r["name"], "day0": r["day0"].isoformat(), "psi": r["psi"]} for r in rels],
            "hol": sorted(d.isoformat() for d in P.HOLIDAYS)}
    js = JS.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__MO__", json.dumps(P.MONTHS, ensure_ascii=False))
    section = ("<p>Сводка по 12 релизам. Для каждого релиза есть <b>отдельная редактируемая страница</b> (кнопка «Открыть страницу»): плановые даты можно менять, "
               "рядом — фактические даты, комментарии, свои этапы, заметки и график «план / факт». Данные сохраняются автоматически в этом браузере; "
               "кнопка «Сохранить HTML» в нижней панели скачивает копию файла со всеми данными, «Экспорт данных» — JSON.</p>"
               '<div id="fx"></div>')
    body = '<div class="relpage" id="relpages"></div><script>' + js + "</script>"
    return section, body
