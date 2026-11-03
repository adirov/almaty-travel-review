/* The poster remains a usable YouTube link when JavaScript is unavailable. */
document.addEventListener('click',function(event){
 var link=event.target.closest('a.home-video');
 if(!link||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
 event.preventDefault();
 var frame=document.createElement('iframe');
 frame.src='https://www.youtube.com/embed/sRgOxH9iPXY?autoplay=1';
 frame.title=link.getAttribute('aria-label');
 frame.allow='autoplay; encrypted-media; picture-in-picture';
 frame.setAttribute('allowfullscreen','');frame.setAttribute('frameborder','0');
 link.replaceWith(frame);
});
