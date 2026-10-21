# -*- coding: utf-8 -*-
"""Тема HTML в палитре Nedra (индиго #140093, лайм #CFF85E, голубой #AAC3E3, бирюзовый #89C9C7, оранжевый #FF7500 / #FDAB64)."""

CSS = r"""
:root{--bg:#F4F6FB;--fg:#1B1B3A;--mut:#5A5A7A;--card:#FFFFFF;--line:#D5DDEE;--ind:#140093;--lime:#CFF85E;--sky:#AAC3E3;--teal:#89C9C7;--org:#FDAB64;--orgd:#FF7500;--acc:#140093;
--hi:#FADBD8;--mid:#FFE4CC;--lo:#EAFAB8;--new:#FFE4CC;--th:#140093;--thfg:#FFFFFF;--ph:#E4E1F7;--head:#140093;--note:#FFF4E8}
@media (prefers-color-scheme:dark){:root{--bg:#0C0A3A;--fg:#E9ECFA;--mut:#A9B4D6;--card:#15125C;--line:#2B2A78;--ind:#CFF85E;--acc:#CFF85E;
--hi:#5A2A33;--mid:#5C3A18;--lo:#2E4A12;--new:#5C3A18;--th:#2B2A78;--ph:#2B2A78;--head:#0A0870;--note:#3A2A1C}}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 Inter,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
header.top{background:var(--head);color:#fff;padding:26px max(16px,calc((100vw - 1240px)/2 + 16px)) 20px;border-bottom:6px solid var(--lime)}
header.top h1{color:#fff}header.top .muted{color:var(--sky)}header.top code{background:rgba(255,255,255,.12);border-color:transparent;color:var(--lime)}
h1{font-size:26px;margin:0 0 6px}h2{font-size:21px;margin:0 0 12px;color:var(--ind)}h3{font-size:16px;margin:18px 0 8px;color:var(--ind)}
h2::before{content:"";display:inline-block;width:12px;height:22px;background:var(--lime);border-left:4px solid var(--head);margin-right:10px;vertical-align:-4px}
.muted{color:var(--mut);font-size:13px}
nav{position:sticky;top:0;z-index:5;background:var(--card);border-bottom:2px solid var(--ind);overflow-x:auto;white-space:nowrap}
nav .in{max-width:1240px;margin:0 auto;padding:0 12px}
nav a{display:inline-block;padding:10px 10px;color:var(--ind);text-decoration:none;font-size:13px;font-weight:500}
nav a:hover{background:var(--lime);color:#140093}
main{max-width:1240px;margin:0 auto;padding:0 16px 60px}
section{background:var(--card);border:1px solid var(--line);border-top:3px solid var(--ind);border-radius:4px;padding:18px 18px 8px;margin:18px 0}
.tw{overflow-x:auto;margin:8px 0 14px}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{background:var(--th);color:var(--thfg);position:sticky;top:0}
td.phase{background:var(--ph);color:var(--ind);font-weight:600;border-left:4px solid var(--orgd)}
.b{display:inline-block;padding:1px 7px;border-radius:9px;font-size:11px;white-space:nowrap}
.b.hi{background:var(--hi)}.b.mid{background:var(--mid)}.b.lo{background:var(--lo)}.b.new{background:var(--new);color:#B85500}.b.sch{background:var(--line)}
figure{margin:10px 0 20px}
.zoom{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:6px}
.zoom button{border:1px solid var(--ind);background:var(--card);color:var(--ind);border-radius:3px;padding:3px 9px;cursor:pointer}
.zoom button:hover{background:var(--lime);color:#140093}
.canvas{overflow:auto;border:1px solid var(--line);border-radius:4px;background:#fff;max-height:78vh}
.canvas svg{display:block}
ul,ol{padding-left:22px}li{margin:3px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.card{border:1px solid var(--line);border-left:4px solid var(--ind);border-radius:4px;padding:10px 12px;background:var(--bg)}
code{background:var(--bg);border:1px solid var(--line);border-radius:4px;padding:0 4px;font-size:12px}
@media (max-width:600px){h1{font-size:21px}}
.cm{margin:14px 0 14px;padding:10px;border:1px dashed var(--orgd);border-radius:4px;background:var(--note)}
.cm label{display:block;font-size:12px;color:var(--mut);margin-bottom:4px}
.cm textarea{width:100%;font:inherit;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px}
.fb{position:sticky;bottom:0;background:var(--head);color:#fff;border-top:4px solid var(--lime);padding:8px 16px;display:flex;gap:8px;flex-wrap:wrap;align-items:center;z-index:6}
.fb .muted{color:var(--sky)}
.fb button{border:0;background:var(--lime);color:#140093;font-weight:600;border-radius:3px;padding:6px 12px;cursor:pointer}
.fb button:hover{background:var(--orgd);color:#fff}
.confluenceTable{margin:8px 0 16px}
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
  function get(k){try{return localStorage.getItem('rp-'+k)||''}catch(e){return ''}}
  function put(k,v){try{localStorage.setItem('rp-'+k,v)}catch(e){}}
  tas.forEach(function(t){t.value=get(t.dataset.k);t.addEventListener('input',function(){put(t.dataset.k,t.value);upd()})});
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
