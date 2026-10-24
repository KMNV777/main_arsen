# -*- coding: utf-8 -*-
"""Тема HTML в палитре Nedra (индиго #140093, лайм #CFF85E, голубой #AAC3E3, бирюзовый #89C9C7, оранжевый #FF7500 / #FDAB64)."""

CSS = r"""
:root{--blue:#140093;--blue-2:#250DBA;--lime:#CFF85E;--orange:#F26B43;--amber:#FBAE40;--grey-l:#C7D4DE;--ink:#333333;--bg:#F5F6F8;--white:#fff;--ink-2:#5E5E5E;--ink-3:#8A8A8A;--line:#E3E8EE;--blue-wash:#EEEDF8;
--bg2:#F5F6F8;--fg:#333333;--mut:#5E5E5E;--card:#fff;--ind:#140093;--sky:#AAC3E3;--orgd:#F26B43;--org:#FBAE40;--hi:#FADBD8;--mid:#FFE9CC;--lo:#EAFAB8;--new:#FFE9CC;--th:#140093;--thfg:#fff;--ph:#EEEDF8;--note:#FFF6E8;--r:3px;--r2:6px;
--sh-1:0 1px 2px rgba(23,43,77,.08);--sh-2:0 4px 14px rgba(23,43,77,.12)}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:70px;zoom:1.25}@media (max-width:900px){html{zoom:1}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 Arial,"Helvetica Neue",Helvetica,sans-serif;-webkit-font-smoothing:antialiased}
h1,h2,h3,h4{margin:0;font-weight:700;letter-spacing:-.015em;line-height:1.1}p{margin:0 0 10px}
header.top{background:linear-gradient(120deg,#1B08A6,#140093 55%,#10007A);color:#fff;padding:34px 56px;position:relative;overflow:hidden;box-shadow:0 6px 24px rgba(20,0,147,.16)}
header.top:before{content:"";position:absolute;right:-220px;top:50%;transform:translateY(-50%);width:700px;height:700px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.09),rgba(255,255,255,0) 64%)}
header.top h1{font-size:38px;color:#fff;position:relative}header.top .muted{color:#C9C4F2;position:relative;margin-top:10px;font-size:14px}
header.top code{background:rgba(255,255,255,.12);border-color:transparent;color:var(--lime)}
nav{position:sticky;top:0;z-index:20;background:#140093;box-shadow:0 2px 10px rgba(20,0,147,.25);overflow-x:auto;white-space:nowrap}
nav{scrollbar-width:none}nav::-webkit-scrollbar{display:none}nav .in{padding:10px 40px;display:flex;gap:4px;width:max-content}
nav a{display:inline-block;padding:7px 11px;border-radius:7px;color:#CFCBF5;text-decoration:none;font-size:12px;font-weight:700}
nav a:hover{background:rgba(255,255,255,.12);color:#fff}nav a.on{background:var(--lime);color:#140093}
main{max-width:1440px;margin:0 auto;padding:0 56px 70px}
section{padding:44px 0 6px;border-bottom:1px solid var(--line)}
.kicker{display:block;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--blue);font-weight:700;margin-bottom:8px}
h2{font-size:31px;line-height:1.08;margin:0 0 18px;color:var(--ink)}
h3{font-size:18px;margin:22px 0 8px;color:var(--blue)}
.muted{color:var(--ink-2);font-size:13px}
.tw{overflow-x:auto;margin:10px 0 16px;background:#fff;border:1px solid var(--line);border-radius:var(--r2);box-shadow:var(--sh-1)}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{border-bottom:1px solid var(--line);padding:9px 12px;text-align:left;vertical-align:top}
th{background:var(--blue);color:#fff;font-size:11px;letter-spacing:.06em;text-transform:uppercase}
tr:last-child td{border-bottom:0}
td.phase{background:var(--ph);color:var(--blue);font-weight:700;border-left:4px solid var(--orange)}
.b{display:inline-block;padding:1px 7px;border-radius:9px;font-size:11px;white-space:nowrap}
.b.hi{background:var(--hi)}.b.mid{background:var(--mid)}.b.lo{background:var(--lo)}.b.new{background:var(--new);color:#B85500}.b.sch{background:var(--line)}
figure{margin:10px 0 24px}
.zoom{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:8px}
.zoom button{border:1px solid var(--line);background:#fff;color:var(--blue);border-radius:var(--r2);padding:4px 10px;cursor:pointer;font:inherit;font-size:12px;font-weight:700}
.zoom button:hover{background:var(--lime)}
.canvas{overflow:auto;border:1px solid var(--line);border-radius:var(--r2);background:#fff;max-height:78vh;box-shadow:var(--sh-1)}
.canvas svg{display:block}
ul,ol{padding-left:22px}li{margin:4px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(320px,100%),1fr));gap:14px;margin:6px 0 14px}
.card{background:#fff;border:1px solid var(--line);border-top:3px solid var(--blue);border-radius:var(--r2);padding:18px 20px;box-shadow:var(--sh-1)}
.card>b:first-child{display:block;font-size:16px;color:var(--blue);margin-bottom:6px}
code{background:var(--blue-wash);border-radius:3px;padding:1px 5px;font-size:12px}
section>p,section>ul,section>ol{max-width:1100px}
.cm{margin:18px 0 22px;padding:12px 14px;border:1px dashed var(--orange);border-radius:var(--r2);background:var(--note)}
.cm label{display:block;font-size:12px;color:var(--ink-2);margin-bottom:4px}
.cm textarea{width:100%;font:inherit;background:#fff;color:var(--ink);border:1px solid var(--line);border-radius:var(--r);padding:6px}
.fb{position:sticky;bottom:0;background:var(--blue);color:#fff;border-top:4px solid var(--lime);padding:9px 56px;display:flex;gap:10px;flex-wrap:wrap;align-items:center;z-index:20}
.fb .muted{color:#C9C4F2}
.fb button,.tools button{border:0;background:var(--lime);color:#140093;font:inherit;font-weight:700;border-radius:var(--r);padding:6px 12px;cursor:pointer}
.fb button:hover,.tools button:hover{background:var(--orange);color:#fff}
.confluenceTable{margin:0}
.calc-p{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(200px,100%),1fr));gap:10px;margin:10px 0}
.calc-p label{font-size:12px;color:var(--ink-2);display:flex;flex-direction:column;gap:3px}
#calc input[type=number],#calc input.rate{font:inherit;background:var(--mid);color:var(--ink);border:1px solid var(--amber);border-radius:var(--r);padding:4px 7px;width:100%}
tr.tot td{background:var(--lo)}
details{margin:12px 0;background:#fff;border:1px solid var(--line);border-radius:var(--r2);padding:10px 14px}summary{cursor:pointer;color:var(--blue);font-weight:700}
.tools{margin:6px 0 12px}
@media (max-width:700px){main,header.top,.fb{padding-left:16px;padding-right:16px}nav .in{padding:8px 12px}h2{font-size:24px}header.top h1{font-size:26px}}

/* единый шрифт и UX-правки */
:root{--font:Arial,"Helvetica Neue",Helvetica,sans-serif}
html{font-family:var(--font)}body,button,input,select,textarea,table,svg text,svg tspan,code,pre,kbd{font-family:var(--font)!important}
code,pre,kbd{font-size:.92em}
input,select,textarea,button{font-size:inherit;color:inherit}
button{cursor:pointer}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible,summary:focus-visible{outline:2px solid #904EE2;outline-offset:2px}
header.top h1{font-size:clamp(24px,2.6vw,36px);line-height:1.15;max-width:1100px}
main>p:first-child{margin:22px 0 0}
main>section{scroll-margin-top:64px;min-width:0}
main{padding-bottom:40px}
nav{scrollbar-width:thin;scrollbar-color:#4A3BC0 transparent}nav::-webkit-scrollbar{display:block;height:6px}nav::-webkit-scrollbar-thumb{background:#4A3BC0;border-radius:3px}
nav .in{padding:8px 40px 6px}
nav a{padding:6px 10px;font-size:12px}
td,th{vertical-align:top}td,th{overflow-wrap:anywhere}
table td:first-child,table th:first-child{overflow-wrap:normal}
.tw,.fx-table,.heat{max-width:100%;min-width:0;overflow-x:auto;-webkit-overflow-scrolling:touch}
th{white-space:nowrap}th .muted{color:var(--lime)!important;font-size:10px;letter-spacing:.06em}
a.op,.fx-btn,button{white-space:nowrap}
.fb{padding:6px 56px;gap:8px;border-top-width:3px;font-size:12px;box-shadow:0 -4px 14px rgba(20,0,147,.18)}
.fb button{padding:4px 10px;font-size:12px;border-radius:6px}
.fb>.muted{display:none}
.fb .stat{margin-left:auto;white-space:nowrap}
main button:not([class]):not([data-z]){border:1px solid var(--line);background:#fff;color:#140093;border-radius:6px;padding:5px 12px;font-weight:700;font-size:12px}main button:not([class]):hover{background:var(--lime)}
.fb .sep{width:1px;height:18px;background:rgba(255,255,255,.3)}
input.dt{width:112px;text-align:center}input.dt.bad{border-color:#E5493A!important;background:#FDE4DC!important}
input[type=number]{text-align:right}
@media (max-width:900px){main{padding-left:16px;padding-right:16px}.fb{padding:6px 16px}nav .in{padding:8px 12px}}
body.relmode .fb{position:fixed;left:0;right:0;bottom:0}body.relmode .relpage{padding-bottom:64px}
svg.chart{max-width:100%;height:auto}.econ-g>*{min-width:0;max-width:100%;overflow-x:auto}.card{max-width:100%}
@media (max-width:900px){html{zoom:1}header.top{padding:22px 16px}header.top:before{display:none}h2{font-size:24px}h3{font-size:18px}
 .tabs{overflow-x:auto;white-space:nowrap;-webkit-overflow-scrolling:touch}.tabs button{flex:0 0 auto;min-height:40px}
 .fx-top{gap:10px}.fx-top label{flex:1 1 140px}.fx-top input,.fx-top select{width:100%;box-sizing:border-box}
 .rp-head{padding:16px 16px 14px}.rp-head h1{font-size:24px}.rp-body{padding:14px 16px 96px}
 .rp-pills{flex-wrap:nowrap;overflow-x:auto;padding-bottom:4px;-webkit-overflow-scrolling:touch}.rp-pills a{flex:0 0 auto;padding:7px 12px}
 .fx-table{max-height:none}.calc-p{grid-template-columns:repeat(2,minmax(0,1fr))}
 .fb{padding-bottom:calc(6px + env(safe-area-inset-bottom));padding-left:max(16px,env(safe-area-inset-left));padding-right:max(16px,env(safe-area-inset-right))}
 .fb .m2{display:none!important}.fb.open .m2{display:inline-flex!important}.fb.open{max-height:60vh;overflow:auto}.fb .stat{margin-left:0;flex:1 1 100%}
 main{padding-bottom:90px}
}
@media (pointer:coarse){main button,main select,main input:not([type=checkbox]),.relpage button,.relpage select,.relpage input:not([type=checkbox]),.rp-pills a,.relpage a.back,.fb button,.fb .tgl,.zoom button,nav a,summary{min-height:38px;box-sizing:border-box}input[type=checkbox]{width:20px;height:20px}.fx-table td{padding-top:5px;padding-bottom:5px}}
@media (max-width:600px){input,select,textarea{font-size:16px!important}.calc-p{grid-template-columns:1fr}.cards,.grid,.kp{grid-template-columns:1fr!important}main{padding-left:14px;padding-right:14px}nav a{padding:8px 12px}.fx-table input.dt{width:104px}.fx-table input.nt{width:160px}.fx-table input.nm{width:150px}.fx-table input.rl{width:110px}}
@media (max-height:480px) and (orientation:landscape){.fb{position:static}nav{position:static}body.relmode .fb{position:static}}
@media (hover:none){.fb button:hover,.tools button:hover{background:var(--lime);color:#140093}}
.fb .more{display:none}@media (max-width:900px){.fb .more{display:inline-flex}}
@media print{.fb,nav{display:none!important}body{zoom:1}}

"""

JS_FIG = r"""
document.querySelectorAll('figure').forEach(function(f){
  var svg=f.querySelector('svg'),w=+f.dataset.w,cv=f.querySelector('.canvas');
  function set(z){ if(z==='fit'){z=Math.min(1,(cv.clientWidth-4)/w);} svg.style.width=(w*z)+'px'; svg.style.height='auto'; }
  f.querySelectorAll('button').forEach(function(b){b.onclick=function(){set(b.dataset.z==='fit'?'fit':+b.dataset.z)}});
  set(w>3000?0.4:'fit');
});
"""

JS_FEEDBACK = r"""
(function(){
  var tas=document.querySelectorAll('.cm textarea'); if(!tas.length) return;
  function get(k,d){if(window.RP){var c=RP.get('cm');if(c&&c[k]!==undefined)return c[k];}try{var l=localStorage.getItem('rp-'+k);if(l)return l}catch(e){}return d||''}
  function put(k,v){if(window.RP){var c=RP.get('cm')||{};c[k]=v;RP.set('cm',c)}else{try{localStorage.setItem('rp-'+k,v)}catch(e){}}}
  tas.forEach(function(t){t.value=get(t.dataset.k,t.defaultValue);t.addEventListener('input',function(){put(t.dataset.k,t.value);upd()})});
  function collect(){var out=[];document.querySelectorAll('section').forEach(function(s){var t=s.querySelector('textarea');
    if(t&&t.value.trim())out.push('## '+s.querySelector('h2').textContent+'\n'+t.value.trim())});return out.join('\n\n')}
  function upd(){var n=collect().split('## ').length-1;var c=document.getElementById('fb-n');if(c)c.textContent=n}
  upd();
  document.getElementById('fb-dl').onclick=function(){var b=new Blob([collect()||'(правок нет)'],{type:'text/plain;charset=utf-8'});
    var a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='правки-к-процессу-релиза.txt';a.click()};
  document.getElementById('fb-cp').onclick=function(){var t=collect()||'(правок нет)';var b=this;
    if(navigator.clipboard){navigator.clipboard.writeText(t).then(function(){b.textContent='Скопировано ✓';setTimeout(function(){b.textContent='Копировать правки'},2000)})}};
})();
"""

JS_COPY = r"""
function cpBlock(id,btn){var el=document.getElementById(id+'-body');var r=document.createRange();r.selectNodeContents(el);
var s=window.getSelection();s.removeAllRanges();s.addRange(r);var ok=false;try{ok=document.execCommand('copy')}catch(e){}
btn.textContent=ok?'Скопировано ✓ — вставьте в Confluence (Ctrl+V)':'Выделено — нажмите Ctrl+C';
setTimeout(function(){s.removeAllRanges();btn.textContent='Копировать блок для Confluence'},3000)}
"""
