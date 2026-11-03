/* Design polish: drop empty CMS paragraphs (only spaces/&nbsp;) that left big gaps. */
document.addEventListener('DOMContentLoaded',function(){
 document.querySelectorAll('.main_container p').forEach(function(p){
  if(!p.textContent.replace(/[\s ]+/g,'')&&!p.querySelector('img,iframe,video,input,a,br+br'))p.remove();
 });
});
