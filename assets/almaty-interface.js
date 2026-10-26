(function(w,d){'use strict';
function ready(){var en=/^\/en\//.test(location.pathname)||d.documentElement.lang==='en';
 if(w.jQuery)jQuery(function(){[['fancybox-close',en?'Close photo':'Закрыть фото'],['fancybox-left',en?'Previous photo':'Предыдущее фото'],['fancybox-right',en?'Next photo':'Следующее фото']].forEach(function(pair){var node=d.getElementById(pair[0]);if(node){node.setAttribute('aria-label',pair[1]);if(pair[0]==='fancybox-close'){node.setAttribute('role','button');node.tabIndex=0;node.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();node.click();}});}}});});
 if(w.jQuery&&jQuery.datepicker){jQuery.datepicker.setDefaults(en?{dayNames:['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],dayNamesMin:['Su','Mo','Tu','We','Th','Fr','Sa'],dayNamesShort:['Sun','Mon','Tue','Wed','Thu','Fri','Sat'],monthNames:['January','February','March','April','May','June','July','August','September','October','November','December'],monthNamesShort:['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],prevText:'Previous',nextText:'Next',closeText:'Close',currentText:'Today',firstDay:1}:{prevText:'Предыдущий',nextText:'Следующий',closeText:'Закрыть',currentText:'Сегодня',firstDay:1});}
 var menu=d.getElementById('left_menu'),middle=d.getElementById('middle');
 if(menu&&middle&&!d.getElementById('mobile-menu-toggle')){var toggle=d.createElement('button');toggle.id='mobile-menu-toggle';toggle.type='button';toggle.style.display='none';toggle.textContent=en?'☰ Menu':'☰ Меню';toggle.setAttribute('aria-controls','left_menu');toggle.setAttribute('aria-expanded','false');menu.classList.add('mobile-menu-closed');toggle.onclick=function(){var closed=menu.classList.toggle('mobile-menu-closed');toggle.setAttribute('aria-expanded',String(!closed));};middle.insertBefore(toggle,middle.firstChild);}
 var slider=d.querySelector('.photo_slider');if(slider&&w.jQuery&&typeof w.showSlide==='function'){var desktopShowSlide=w.showSlide;w.showSlide=function(pos){if(!matchMedia('(max-width:1000px)').matches)return desktopShowSlide(pos);var width=slider.clientWidth;jQuery('.photo_slider ul.slides').animate({marginLeft:-((pos-1)*width)},500,function(){jQuery(this).attr('alt',pos);jQuery('.photo_slider ul.controls li').removeClass('set');jQuery('.photo_slider ul.controls li[alt="'+pos+'"]').addClass('set');});};function size(){var width=matchMedia('(max-width:1000px)').matches?slider.clientWidth:460;var slides=slider.querySelectorAll('ul.slides>li');Array.prototype.forEach.call(slides,function(li){li.style.width=width+'px';});var list=slider.querySelector('ul.slides');if(list){list.style.width=width*slides.length+'px';list.style.marginLeft='0px';list.setAttribute('alt','1');}}size();w.addEventListener('resize',size);}
 Array.prototype.forEach.call(d.querySelectorAll('.main_container p,.main_container li'),function(n){if(!n.textContent.trim()&&!n.querySelector('img,iframe,input,textarea,video'))n.classList.add('mobile-empty-spacer');});
 Array.prototype.forEach.call(d.querySelectorAll('.main_container table'),function(t){if(Array.prototype.some.call(t.rows,function(r){return r.cells.length>=4;}))t.classList.add('wide-data-table');});
 if(w.parent!==w)setTimeout(function(){w.parent.postMessage({previewReady:true,path:location.pathname},location.origin);},250);
}
if(d.readyState==='loading')d.addEventListener('DOMContentLoaded',ready);else ready();
})(window,document);

/* FancyBox 1.3 recenters on resize but does not rescale an already open image. */
(function(w,d){'use strict';
 var pending=0,retry=0;
 function fit(){
  var wrap=d.getElementById('fancybox-wrap'),inner=d.getElementById('fancybox-inner'),img=d.getElementById('fancybox-img');
  if(!wrap||!inner||!img||!img.naturalWidth||!wrap.getClientRects().length||getComputedStyle(wrap).display==='none')return;
  if(w.jQuery&&jQuery(wrap).is(':animated')){clearTimeout(retry);retry=setTimeout(fit,200);return;}
  var style=getComputedStyle(wrap),outerX=parseFloat(style.paddingLeft)+parseFloat(style.paddingRight),outerY=parseFloat(style.paddingTop)+parseFloat(style.paddingBottom);
  var frameX=Math.max(0,wrap.offsetWidth-inner.offsetWidth-outerX),frameY=Math.max(0,wrap.offsetHeight-inner.offsetHeight-outerY);
  var viewportWidth=d.documentElement.clientWidth,viewportHeight=w.innerHeight;
  var scale=Math.min(1,Math.max(1,viewportWidth-outerX-frameX-40)/img.naturalWidth,Math.max(1,viewportHeight-outerY-frameY-40)/img.naturalHeight);
  var width=Math.max(1,Math.floor(img.naturalWidth*scale)),height=Math.max(1,Math.floor(img.naturalHeight*scale));
  inner.style.width=width+'px';inner.style.height=height+'px';
  wrap.style.width=(width+frameX)+'px';wrap.style.height=(height+frameY)+'px';
  if(w.jQuery&&jQuery.fancybox&&typeof jQuery.fancybox.center==='function')jQuery.fancybox.center();
 }
 function resize(){cancelAnimationFrame(pending);pending=requestAnimationFrame(fit);clearTimeout(retry);retry=setTimeout(fit,200);}
 w.addEventListener('resize',resize);
 w.addEventListener('orientationchange',resize);
 if(w.visualViewport)w.visualViewport.addEventListener('resize',resize);
})(window,document);

/* Keep the legacy datepicker in view after opening, changing month or rotation. */
(function(w,d){'use strict';
 var timer=0;
 // Legacy jQuery's animation queue can leave an invisible calendar intercepting
 // clicks in WebKit. Opening and closing this utility does not need animation.
 if(w.jQuery&&jQuery.datepicker)jQuery.datepicker.setDefaults({showAnim:'',duration:0});
 function place(){
  var popup=d.getElementById('ui-datepicker-div');
  if(!popup||getComputedStyle(popup).display==='none')return;
  var r=popup.getBoundingClientRect();if(!r.width||!r.height)return;
  var width=d.documentElement.clientWidth,height=w.innerHeight,pad=12;
  var left=Math.max(pad,Math.min(r.left,width-r.width-pad)),top=Math.max(pad,Math.min(r.top,height-r.height-pad));
  var fixed=getComputedStyle(popup).position==='fixed';
  popup.style.left=(left+(fixed?0:w.pageXOffset))+'px';
  popup.style.top=(top+(fixed?0:w.pageYOffset))+'px';
 }
 function schedule(){w.requestAnimationFrame(place);clearTimeout(timer);timer=setTimeout(place,220);}
 d.addEventListener('focusin',function(e){
  if(e.target.id==='date')schedule();
  else if(!e.target.closest('#ui-datepicker-div')&&w.jQuery&&jQuery.datepicker){
   jQuery('#date').datepicker('hide');jQuery('#ui-datepicker-div').stop(true,true).hide();
  }
 });
 d.addEventListener('click',function(e){if(e.target.id==='date'||e.target.closest('#ui-datepicker-div'))schedule();});
 w.addEventListener('resize',schedule);
 w.addEventListener('orientationchange',schedule);
 if(w.visualViewport)w.visualViewport.addEventListener('resize',schedule);
})(window,document);
