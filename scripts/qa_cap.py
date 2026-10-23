# -*- coding: utf-8 -*-
"""Динамический расчёт ёмкости QA по спринтам («снежный ком» после релизного спринта)."""

JS = r"""
(function(){
var P={qa:1,days:10,regress:3,smoke:2,retest:1,k:2,qdpt:1.25,tasks:8,auto:0,risk:100},lab={qa:'QA в команде, чел.',days:'Рабочих дней в спринте',regress:'Регресс UAT, дн.',smoke:'Smoke UAT, дн.',retest:'Перепроверка исправлений, дн.',k:'Релизный каждый N-й спринт',qdpt:'QA-дней на задачу',tasks:'Задач в спринте (план без резерва)',auto:'Автоматизация регресса, %',risk:'Доля регресса, выполняемая по риску, %'};
function nf(x,d){return x.toLocaleString('ru-RU',{minimumFractionDigits:d||0,maximumFractionDigits:d||0})}
function calc(){var S=12,rows=[],backlog=0,sumRes=0,cap=P.qa*P.days;
 for(var s=1;s<=S;s++){var res=(s>1&&(s-1)%P.k===0)?(P.regress*(1-P.auto/100)*(P.risk/100)+P.smoke+P.retest):0;res=Math.min(res,cap);sumRes+=res;
  var net=cap-res,demand=P.tasks*P.qdpt,tested=Math.min(P.tasks,net/P.qdpt),miss=Math.max(0,P.tasks-tested);backlog+=miss;
  rows.push({s:s,cap:cap,res:res,net:net,demand:demand,tested:tested,miss:miss,backlog:backlog,rel:(s%P.k===0)})}
 var avgNet=(cap*S-sumRes)/S,smooth=Math.floor(avgNet/P.qdpt);rows.forEach(function(r){r.plan=Math.floor(r.net/P.qdpt)});
 return {rows:rows,avgNet:avgNet,smooth:smooth,sumRes:sumRes,cap:cap}}
function chart(c){var W=760,H=300,L=44,B=40,n=c.rows.length,bw=(W-L-20)/n,mx=Math.max(c.cap,c.rows[n-1].backlog*P.qdpt,P.tasks*P.qdpt)*1.15||1,Y=function(v){return H-B-v/mx*(H-B-18)};
 var st=Math.max(1,Math.ceil(mx/5)),s='<svg class="chart" viewBox="0 0 '+W+' '+H+'" width="100%" role="img" aria-label="Ёмкость QA по спринтам">';
 for(var g=0;g<=mx;g+=st){s+='<line x1="'+L+'" x2="'+(W-10)+'" y1="'+Y(g)+'" y2="'+Y(g)+'" stroke="#EEF1F6"/><text x="'+(L-6)+'" y="'+(Y(g)+3)+'" font-size="10" text-anchor="end" fill="#6B778C">'+g+'</text>'}
 c.rows.forEach(function(r,i){var x=L+i*bw+4,w=bw-8;
  s+='<rect x="'+x+'" y="'+Y(r.cap)+'" width="'+w+'" height="'+(Y(0)-Y(r.cap))+'" fill="#EEF1F6" stroke="#C7D4DE"/>';
  s+='<rect x="'+x+'" y="'+Y(r.res)+'" width="'+w+'" height="'+(Y(0)-Y(r.res))+'" fill="#F26B43"/>';
  var ld=Math.min(r.demand,r.net);s+='<rect x="'+(x+w*0.25)+'" y="'+Y(r.res+ld)+'" width="'+(w*0.5)+'" height="'+(Y(r.res)-Y(r.res+ld))+'" fill="#140093" opacity=".85"/>';
  s+='<text x="'+(x+w/2)+'" y="'+(H-24)+'" font-size="10" text-anchor="middle" fill="#333" font-weight="'+(r.rel?'700':'400')+'">С'+r.s+(r.rel?' ⚑':'')+'</text>'});
 var d='';c.rows.forEach(function(r,i){var x=L+i*bw+bw/2;d+=(i?'L':'M')+x+' '+Y(r.backlog*P.qdpt)});
 s+='<path d="'+d+'" fill="none" stroke="#E5493A" stroke-width="2.5"/><text x="'+(W-12)+'" y="14" font-size="10" fill="#E5493A" text-anchor="end" font-weight="700">красная линия — непротестированный остаток нарастающим итогом, QA-дней</text>';
 return s+'<text x="'+L+'" y="'+(H-6)+'" font-size="10" fill="#6B778C">серый — ёмкость QA, оранжевый — резерв на регресс и Smoke, синий — задачи спринта; ⚑ — релизный спринт</text></svg>'}
function render(){var c=calc(),last=c.rows[c.rows.length-1],first=c.rows.filter(function(r){return r.res>0})[0];
 var kp='<div class="kpis"><div class="kpi"><b>'+nf(first?first.res:0,1)+'</b><span>QA-дней резерв в спринте после релизного</span><small>регресс'+((P.auto||P.risk<100)?' с автотестами и выбором по риску':'')+' + Smoke + перепроверка</small></div>'
  +'<div class="kpi '+(last.backlog>0?'bad':'ok')+'"><b>'+nf(last.backlog,1)+'</b><span>задач не протестировано за 12 спринтов</span><small>если планировать на полный состав QA (снежный ком)</small></div>'
  +'<div class="kpi ok"><b>'+c.smooth+'</b><span>задач в спринте при планировании от нетто-ёмкости</span><small>средняя ёмкость '+nf(c.avgNet,1)+' QA-дн. за вычетом резерва</small></div>'
  +'<div class="kpi"><b>'+nf(c.sumRes/(c.cap*c.rows.length)*100,0)+'%</b><span>ёмкости QA уходит на регресс и Smoke</span><small>в среднем по спринтам</small></div></div>';
 var tr=c.rows.map(function(r){return '<tr><td>С'+r.s+(r.rel?' · релизный':'')+'</td><td>'+nf(r.cap,1)+'</td><td>'+nf(r.res,1)+'</td><td>'+nf(r.net,1)+'</td><td>'+nf(Math.min(P.tasks,r.net/P.qdpt),1)+' / '+P.tasks+'</td><td>'+nf(r.backlog,1)+'</td><td><b>'+r.plan+'</b></td></tr>'}).join('');
 document.getElementById('qa-out').innerHTML=kp+'<div class="verdict"><b>Вывод.</b> Если в спринте после релизного планировать на полный состав QA, непротестированный остаток растёт каждый релиз (красная линия). '
  +'Планируйте ёмкость QA за вычетом резерва: стабильный план — '+c.smooth+' задач в спринт при '+P.tasks+' без резерва. Рычаги: автоматизация регресса, ещё один QA, тестирование внутри спринта (на фризе остаётся только регресс).</div>'
  +'<div class="card" style="max-width:820px">'+chart(c)+'</div><div class="tw"><table><thead><tr><th>Спринт</th><th>Ёмкость QA, дн.</th><th>Резерв, дн.</th><th>Нетто, дн.</th><th>Протестировано / план</th><th>Остаток, задач</th><th>План при резерве, задач</th></tr></thead><tbody>'+tr+'</tbody></table></div>'}
var pf=Object.keys(lab).map(function(k){return '<label>'+lab[k]+'<input type="number" step="any" data-k="'+k+'" value="'+P[k]+'"></label>'}).join('');
document.getElementById('qa').innerHTML='<div class="ctl-panel"><b>Параметры</b><div class="calc-p">'+pf+'</div></div><div id="qa-out"></div>';
document.querySelectorAll('#qa input').forEach(function(i){i.oninput=function(){P[i.dataset.k]=parseFloat(i.value)||0;render()}});render();
})();
"""


def qa_html() -> str:
    return ("<p>Регресс релиза N приходится на спринт N+1: QA в нём занят не 10 дней, а меньше. Если план спринта не учитывает резерв, часть задач не успевает протестироваться и остаток нарастает «снежным комом». "
            "Здесь ёмкость QA считается за вычетом резерва на регресс, Smoke и перепроверку; все поля редактируются. Значения по умолчанию — пример из замечания: 1 QA, 10 дней, регресс 3 дня.</p>"
            '<div id="qa"></div><script>' + JS + "</script>")
