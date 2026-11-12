/* Design polish: drop empty CMS paragraphs (only spaces/&nbsp;) that left big gaps. */
document.addEventListener('DOMContentLoaded',function(){
 document.querySelectorAll('.main_container p').forEach(function(p){
  if(!p.textContent.replace(/[\s ]+/g,'')&&!p.querySelector('img,iframe,video,input,a,br+br'))p.remove();
 });
 /* EN/summer home: the CMS block starts with an empty <h3> and uses a bold
    <h3> for "Tourism in Almaty". Drop the empty one and give the real one the
    same heading style as the other home sections (as on the RU page). */
 document.querySelectorAll('.owner-home .main_container h3').forEach(function(h){
  if(!h.textContent.replace(/[\s\u00a0]+/g,''))h.remove();else h.classList.add('almaty-demoted-heading');
 });
 /* Home text under "Туризм в Алматы" is one CMS paragraph split by <br>.
    Turn each line break into a real paragraph; the words are unchanged. */
 document.querySelectorAll('.owner-home .almaty-demoted-heading~p').forEach(function(p){
  if(!p.querySelector('br'))return p.classList.add('almaty-home-text');
  var part=document.createElement('p'),parts=[part];
  Array.prototype.slice.call(p.childNodes).forEach(function(node){
   if(node.nodeName==='BR'){part=document.createElement('p');parts.push(part);}else part.appendChild(node);
  });
  parts.forEach(function(q){if(q.textContent.trim()){q.className='almaty-home-text';p.parentNode.insertBefore(q,p);}});
  p.remove();
 });
});
