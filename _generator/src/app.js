/* الفن والسياسة — behaviour. No network calls except the YouTube iframe on demand. */
(function(){
'use strict';
var P='anpo:';
var S={get:function(k,d){try{var v=localStorage.getItem(P+k);return v===null?d:JSON.parse(v)}catch(e){return d}},
 set:function(k,v){try{localStorage.setItem(P+k,JSON.stringify(v));return true}catch(e){return false}}};
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
var root=document.documentElement,body=document.body;
var views=$$('.view'),byId={};views.forEach(function(v){byId[v.id.slice(2)]=v});
var cur=null;

/* ---------- router ---------- */
function route(){
  var h=(location.hash||'').replace(/^#\/?/,'');
  if(!byId[h])h='cover';
  views.forEach(function(v){var on=v.id==='v-'+h;v.hidden=!on;v.classList.toggle('current',on)});
  cur=byId[h];document.title=(h==='cover'?'':cur.dataset.title+' — ')+'الفن والسياسة';
  closeToc();closePop();window.scrollTo(0,0);
  var f=$('h1',cur);if(f){f.setAttribute('tabindex','-1');try{f.focus({preventScroll:true})}catch(e){}}
  S.set('last',h);scrollProg();
}
window.addEventListener('hashchange',route);

/* ---------- toc ---------- */
function openToc(){$('#toc').hidden=false;$('#scrim').hidden=false;$('[data-toc=toggle]').setAttribute('aria-expanded','true')}
function closeToc(){$('#toc').hidden=true;$('#scrim').hidden=true;$('[data-toc=toggle]').setAttribute('aria-expanded','false')}

/* ---------- font size / reading mode ---------- */
var scale=S.get('scale',1);function setScale(s){scale=Math.max(.85,Math.min(1.6,s));root.style.setProperty('--scale',scale);S.set('scale',scale)}
setScale(scale);
function setRM(on){body.classList.toggle('readmode',on);$$('[data-readmode]').forEach(function(b){b.setAttribute('aria-pressed',on)});S.set('rm',on)}
setRM(S.get('rm',false));

/* ---------- popover for glosses ---------- */
var pop=$('#pop');
function closePop(){pop.hidden=true}
function openPop(el){
  pop.innerHTML='';var a=document.createElement('span');a.className='pen';a.textContent=el.dataset.en;
  var b=document.createElement('small');b.textContent=el.dataset.ar+(el.dataset.ctx?' — '+el.dataset.ctx:'');
  pop.appendChild(a);pop.appendChild(b);pop.hidden=false;
  var r=el.getBoundingClientRect(),w=pop.offsetWidth,x=r.left+scrollX+r.width/2-w/2;
  x=Math.max(8,Math.min(x,document.documentElement.clientWidth-w-8));
  pop.style.left=x+'px';pop.style.top=(r.bottom+scrollY+8)+'px';
}

/* ---------- video ---------- */
function loadVideo(box,start){
  var id=box.dataset.yt,fr=$('.vframe',box);
  var src='https://www.youtube-nocookie.com/embed/'+id+'?rel=0&autoplay=1'+(start?'&start='+start:'');
  fr.innerHTML='';var f=document.createElement('iframe');f.src=src;f.title='مشغّل الفيديو';f.allow='accelerometer; autoplay; encrypted-media; picture-in-picture; fullscreen';
  f.referrerPolicy='strict-origin-when-cross-origin';f.allowFullscreen=true;fr.appendChild(f);box.classList.add('on');
}

/* ---------- state restore ---------- */
function restore(){
  $$('[data-ans]').forEach(function(t){var v=S.get('ans:'+t.dataset.ans,'');if(v)t.value=v});
  $$('[data-done]').forEach(function(c){c.checked=!!S.get('done:'+c.dataset.done,false)});
  $$('[data-chk]').forEach(function(c){c.checked=!!S.get('chk:'+c.dataset.chk,false)});
  $$('[data-cds]').forEach(function(c){c.value=S.get('cds:'+c.dataset.cds,'')});
  $$('.vcard').forEach(function(c){if(S.get('lrn:'+c.dataset.key,false)){c.classList.add('learned');$('.vc-learn',c).setAttribute('aria-pressed','true')}});
  $$('[data-glt]').forEach(function(c){c.checked=S.get('glt',true)});body.classList.toggle('no-gl',!S.get('glt',true));
  progress();
}
function progress(){
  var tot=0,done=0;
  $$('[data-done]').forEach(function(c){tot++;var on=c.checked;if(on)done++;
    $$('[data-dn="'+c.dataset.done+'"]').forEach(function(d){d.classList.toggle('on',on)})});
  var units={};$$('[data-done]').forEach(function(c){var u=c.dataset.done.split('-')[0];(units[u]=units[u]||[0,0]);units[u][1]++;if(c.checked)units[u][0]++});
  Object.keys(units).forEach(function(u){var p=units[u];var i=$('[data-uprog='+u+']'),t=$('[data-uprogt='+u+']');
    if(i)i.style.width=(100*p[0]/p[1])+'%';if(t)t.textContent=p[0]+' من '+p[1]+' مواد مكتملة'});
  $$('[data-bprog]').forEach(function(i){i.style.width=(tot?100*done/tot:0)+'%'});
  $$('[data-bprogt]').forEach(function(t){t.textContent=done+' من '+tot+' مادة مكتملة في الكتاب'});
}

/* ---------- reading progress ---------- */
function scrollProg(){
  var y=scrollY,h=document.documentElement.scrollHeight-innerHeight;
  if(cur&&cur.classList.contains('item')){var a=$('.rtext',cur);if(a){var r=a.getBoundingClientRect(),top=r.top+scrollY,len=r.height;var p=Math.max(0,Math.min(1,(y+innerHeight*.4-top)/len));$('.rprog i',cur).style.width=(100*p)+'%'}}
  $('#totop').hidden=y<600;
  if(cur){var ps=$$('.para',cur);if(ps.length){var on=null;ps.forEach(function(p){if(p.getBoundingClientRect().top<innerHeight*.35)on=p.dataset.p});
    $$('.pn',cur).forEach(function(b){b.classList.toggle('on',b.dataset.scroll.slice(-3).replace(/\D/g,'')===on||b.textContent===on)})}}
}
window.addEventListener('scroll',scrollProg,{passive:true});

/* ---------- download answers ---------- */
function download(iid){
  var v=byId[iid],out=[$('h1',v).textContent,'',''];
  $$('.qlist>li',v).forEach(function(li,i){var q=$('.qt',li),t=$('textarea',li);out.push((i+1)+') '+q.textContent,'',(t.value||'(لا إجابة)'),'','---','')});
  var b=new Blob([out.join('\n')],{type:'text/plain;charset=utf-8'}),a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='answers-'+iid+'.txt';
  document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},500);
}

/* ---------- events ---------- */
document.addEventListener('click',function(e){
  var t=e.target;
  var g=t.closest('mark.gl');if(g&&!body.classList.contains('no-gl')){e.stopPropagation();openPop(g);return}
  if(!t.closest('#pop'))closePop();
  var b;
  if((b=t.closest('[data-toc]'))){b.dataset.toc==='toggle'?($('#toc').hidden?openToc():closeToc()):closeToc();return}
  if(t.id==='scrim'){closeToc();return}
  if((b=t.closest('[data-fs]'))){var d=+b.dataset.fs;setScale(d===0?1:scale+d*.08);return}
  if((b=t.closest('[data-readmode]'))){setRM(!body.classList.contains('readmode'));return}
  if(t.closest('[data-print]')){window.print();return}
  if(t.id==='totop'||t.closest('#totop')){window.scrollTo(0,0);return}
  if((b=t.closest('[data-scroll]'))){e.preventDefault();var el=$(b.dataset.scroll);if(el){el.scrollIntoView({block:'center'});el.classList.remove('flash');void el.offsetWidth;el.classList.add('flash')}return}
  if((b=t.closest('.vplay'))){loadVideo(b.closest('.video'),0);return}
  if((b=t.closest('[data-seek]'))){var v=b.closest('.view'),box=$('.video',v);if(box){box.scrollIntoView({block:'center'});loadVideo(box,+b.dataset.seek)}return}
  if((b=t.closest('.vc-flip'))){var c=b.closest('.vcard'),o=c.classList.toggle('open');b.setAttribute('aria-expanded',o);return}
  if((b=t.closest('.vc-learn'))){var c2=b.closest('.vcard'),on=!c2.classList.contains('learned');c2.classList.toggle('learned',on);b.setAttribute('aria-pressed',on);S.set('lrn:'+c2.dataset.key,on);return}
  if((b=t.closest('[data-flipall]'))){var open=b.dataset.flipall==='open';$$('.vcard',b.closest('.vsec')).forEach(function(c){c.classList.toggle('open',open);$('.vc-flip',c).setAttribute('aria-expanded',open)});return}
  if((b=t.closest('[data-download]'))){download(b.dataset.download);return}
  if((b=t.closest('.opt'))){var li=b.closest('.cloze'),ans=+li.dataset.ans,k=+b.dataset.o,fb=$('.fb',li);
    $$('.opt',li).forEach(function(o){o.classList.remove('right','wrong')});b.classList.add(k===ans?'right':'wrong');
    fb.hidden=false;fb.textContent=(k===ans?'✓ صحيح. ':'✗ ليس هذا هو الأنسب. ')+fb.dataset.why;
    var bl=$('.blank',li);if(k===ans)bl.textContent=b.textContent;return}
});
document.addEventListener('keydown',function(e){
  if(e.key==='Escape'){closePop();closeToc()}
  if((e.key==='Enter'||e.key===' ')&&e.target.matches&&e.target.matches('mark.gl')){e.preventDefault();body.classList.contains('no-gl')||openPop(e.target)}
});
document.addEventListener('input',function(e){
  var t=e.target;
  if(t.matches('[data-ans]')){S.set('ans:'+t.dataset.ans,t.value);var s=$('.saved',t.closest('.view'));if(s){s.textContent='تم الحفظ في هذا المتصفح';clearTimeout(s._t);s._t=setTimeout(function(){s.textContent=''},1500)}}
  if(t.id==='vq'){var q=t.value.trim().toLowerCase(),nq=q.replace(/[ً-ٰٟـ]/g,'').replace(/[إأآ]/g,'ا').replace(/ى/g,'ي'),n=0;
    $$('.vi').forEach(function(d){var m=0;$$('tr',d).forEach(function(r){var hit=!q||r.dataset.s.indexOf(nq)>-1||r.dataset.s.indexOf(q)>-1;r.hidden=!hit;if(hit&&q)m++});d.hidden=!!q&&!m;if(q&&m)d.open=true;if(!q)d.open=false;n+=q?m:0});
    $('.count').textContent=q?n+' نتيجة':''}
});
document.addEventListener('change',function(e){
  var t=e.target;
  if(t.matches('[data-done]')){S.set('done:'+t.dataset.done,t.checked);progress()}
  if(t.matches('[data-chk]'))S.set('chk:'+t.dataset.chk,t.checked);
  if(t.matches('[data-cds]'))S.set('cds:'+t.dataset.cds,t.value);
  if(t.matches('[data-glt]')){S.set('glt',t.checked);body.classList.toggle('no-gl',!t.checked);$$('[data-glt]').forEach(function(c){c.checked=t.checked})}
});
if(!location.hash){var l=S.get('last','cover');/* always open on the cover on first load */}
restore();route();
})();
