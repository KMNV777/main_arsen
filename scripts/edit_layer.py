# -*- coding: utf-8 -*-
"""Слой редактирования и сохранения для общего HTML.

* RP — общее хранилище состояния (localStorage + встроенный в файл JSON); побеждает более новое.
* Правки текста: все абзацы, пункты, ячейки таблиц и заголовки разделов редактируются на месте (contenteditable).
* Сохранение: кнопка «Сохранить HTML» скачивает копию страницы со всеми правками и состоянием калькуляторов/календарей;
  её можно открыть и продолжать вести. Плюс экспорт/импорт данных JSON.
"""

CSS_EDIT = r"""
body.editing [contenteditable=true]{cursor:text;transition:background .15s}
body.editing [contenteditable=true]:hover{outline:1px dashed #FBAE40;outline-offset:2px}
body.editing [contenteditable=true]:focus{outline:2px solid #FBAE40;outline-offset:2px;background:#FFF6E8}
.fb .stat{font-size:12px;color:#C9C4F2;margin-left:auto}
.fb .tgl{display:inline-flex;align-items:center;gap:6px;color:#fff;font-size:13px}
.fb .tgl input{accent-color:#CFF85E}
.fb button.sec{background:transparent;color:#fff;border:1px solid #AAC3E3}
.fb button.sec:hover{background:#FF7500;border-color:#FF7500}
"""

# Ядро состояния — выполняется в самом начале body, до всех компонентов
JS_CORE = r"""
window.RP=(function(){
 var KEY='rp-state-v2',st={_ts:0},tm=null,statEl=null;
 function readLS(){try{return JSON.parse(localStorage.getItem(KEY)||'null')||{}}catch(e){return {}}}
 function readEmb(){try{var n=document.getElementById('rp-embedded');return n&&n.textContent.trim()?JSON.parse(n.textContent):{}}catch(e){return {}}}
 var ls=readLS(),em=readEmb();st=((em._ts||0)>(ls._ts||0))?em:ls;st.edits=st.edits||{};
 if(!st.fact){try{var old=JSON.parse(localStorage.getItem('rp-fact-v1')||'null');if(old)st.fact=old}catch(e){}}
 function stamp(){var d=new Date();return ('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2)+':'+('0'+d.getSeconds()).slice(-2)}
 function flush(){try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}statEl=statEl||document.getElementById('rp-status');if(statEl)statEl.textContent='автосохранено '+stamp()}
 window.addEventListener('pagehide',function(){if(tm){clearTimeout(tm);flush()}});
 return {
  state:st,
  get:function(k){return st[k]},
  set:function(k,v){if(v===null||v===undefined)delete st[k];else st[k]=v;st._ts=Date.now();clearTimeout(tm);tm=setTimeout(flush,250)},
  edit:function(id,html){st.edits[id]=html;st._ts=Date.now();clearTimeout(tm);tm=setTimeout(flush,250)},
  touch:function(){st._ts=Date.now();clearTimeout(tm);tm=setTimeout(flush,250)},
  replace:function(obj){for(var k in st)delete st[k];for(var k2 in obj)st[k2]=obj[k2];st.edits=st.edits||{};st._ts=Date.now();flush()},
  reset:function(){try{localStorage.removeItem(KEY)}catch(e){}},
  export:function(){return JSON.stringify(st,null,1)}
 };
})();
"""

# Слой редактирования — в конце body, после всех компонентов
JS_EDIT = r"""
(function(){
 var DYN='#calc,#qa,#heat,#fx,#gt,#rsel,#relpages,#econ-out,#qa-out,.tabs,.zoom,figure,nav,.fb,.cm,header.top,details>summary,script,style,svg';
 var SEL='h2,h3,p,li,td,th';
 function inDyn(el){return !!el.closest(DYN)||!!el.closest('[data-noedit]')}
 var EL=[],byId={};
 document.querySelectorAll('main>section').forEach(function(sec){
  var cnt={};
  sec.querySelectorAll(SEL).forEach(function(el){
   if(inDyn(el))return; if(el.querySelector('input,select,textarea,button,table'))return;
   var t=el.tagName.toLowerCase();cnt[t]=(cnt[t]||0)+1;var id=sec.id+':'+t+':'+cnt[t];
   el.dataset.eid=id;EL.push(el);byId[id]=el})});
 var ed=RP.state.edits||{};
 Object.keys(ed).forEach(function(id){var el=byId[id];if(el&&el.innerHTML!==ed[id])el.innerHTML=ed[id]});
 function on(flag){document.body.classList.toggle('editing',flag);EL.forEach(function(el){if(flag)el.setAttribute('contenteditable','true');else el.removeAttribute('contenteditable')});
  var c=document.getElementById('rp-edit-on');if(c)c.checked=flag;try{localStorage.setItem('rp-editing',flag?'1':'0')}catch(e){}}
 EL.forEach(function(el){el.addEventListener('input',function(){RP.edit(el.dataset.eid,el.innerHTML)})});
 var flag=true;try{flag=localStorage.getItem('rp-editing')!=='0'}catch(e){}on(flag);
 var tg=document.getElementById('rp-edit-on');if(tg)tg.onchange=function(){on(tg.checked)};

 function dl(text,mime,name){var b=new Blob([text],{type:mime}),a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=name;document.body.appendChild(a);a.click();setTimeout(function(){a.remove();URL.revokeObjectURL(a.href)},500)}
 function stampName(){var d=new Date();function z(n){return ('0'+n).slice(-2)}return d.getFullYear()+z(d.getMonth()+1)+z(d.getDate())+'-'+z(d.getHours())+z(d.getMinutes())}
 function saveHtml(){
  var live=[].slice.call(document.querySelectorAll('input,textarea,select'));
  var clone=document.documentElement.cloneNode(true);
  var cl=[].slice.call(clone.querySelectorAll('input,textarea,select'));
  live.forEach(function(el,i){var c=cl[i];if(!c)return;
   if(el.tagName==='TEXTAREA'){c.textContent=el.value}
   else if(el.tagName==='SELECT'){[].slice.call(c.options).forEach(function(o,k){if(el.options[k]&&el.options[k].selected)o.setAttribute('selected','');else o.removeAttribute('selected')})}
   else if(el.type==='checkbox'||el.type==='radio'){if(el.checked)c.setAttribute('checked','');else c.removeAttribute('checked')}
   else{c.setAttribute('value',el.value)}});
  ['calc','qa','heat','fx','gt','rsel','relpages'].forEach(function(id){var n=clone.querySelector('#'+id);if(n){n.innerHTML='';n.removeAttribute('style')}});
  clone.querySelectorAll('[contenteditable]').forEach(function(n){n.removeAttribute('contenteditable')});
  clone.querySelectorAll('[data-eid]').forEach(function(n){n.removeAttribute('data-eid')});
  var b=clone.querySelector('body');if(b){b.classList.remove('editing');b.classList.remove('relmode')}
  RP.state._ts=Date.now();
  var emb=clone.querySelector('#rp-embedded');if(emb)emb.textContent=JSON.stringify(RP.state).replace(/<\//g,'<\\/');
  var html='<!doctype html>\n'+clone.outerHTML;
  dl(html,'text/html;charset=utf-8','release-process-'+stampName()+'.html');
  var s=document.getElementById('rp-status');if(s)s.textContent='файл сохранён';
 }
 var q=function(id){return document.getElementById(id)};
 if(q('rp-save'))q('rp-save').onclick=saveHtml;
 if(q('rp-exp'))q('rp-exp').onclick=function(){dl(RP.export(),'application/json','данные-релизов-'+stampName()+'.json')};
 if(q('rp-imp'))q('rp-imp').onclick=function(){q('rp-file').click()};
 if(q('rp-file'))q('rp-file').onchange=function(){var f=this.files[0];if(!f)return;var rd=new FileReader();rd.onload=function(){try{var o=JSON.parse(rd.result);if(!o||typeof o!=='object')throw 0;RP.replace(o);location.reload()}catch(e){alert('Не удалось прочитать файл данных')}};rd.readAsText(f)};
 if(q('rp-reset'))q('rp-reset').onclick=function(){if(confirm('Сбросить все правки и данные этого браузера (тексты, калькуляторы, календари)? Сохранённые файлы не затрагиваются.')){RP.reset();try{localStorage.removeItem('rp-fact-v1')}catch(e){}location.reload()}};
})();
"""

FB_EXTRA = ('<span class="sep"></span><label class="tgl"><input type="checkbox" id="rp-edit-on" checked> Режим правки</label>'
            '<button id="rp-save" title="Скачать копию страницы со всеми правками и данными — её можно открыть и продолжать вести">Сохранить HTML</button>'
            '<button id="rp-exp" class="sec" title="Скачать данные (тексты, калькуляторы, календари) в JSON">Экспорт данных</button>'
            '<button id="rp-imp" class="sec">Импорт данных</button><input type="file" id="rp-file" accept=".json" style="display:none">'
            '<button id="rp-reset" class="sec">Сбросить</button><span class="stat" id="rp-status">сохраняется в браузере</span>')
