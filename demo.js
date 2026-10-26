/* Approval snapshot only. No enquiry transport, tracking or entered-data storage. */
(function(w,d){'use strict';
 var config=w.AlmatyDemo,en=config.lang==='en';
 function ready(){
  var form=d.getElementById('order_form');
  if(form){
   form.setAttribute('method','get');form.removeAttribute('onsubmit');
   Array.prototype.forEach.call(form.querySelectorAll('input,textarea'),function(field){field.removeAttribute('name');});
   var status=d.createElement('p');status.id='demo-form-status';status.className='demo-form-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');
   status.textContent=en?'Demo form: entered details are not sent or saved.':'Демонстрационная форма: введённые данные не отправляются и не сохраняются.';
   form.insertBefore(status,form.firstChild);
   function submit(event){
    event.preventDefault();event.stopImmediatePropagation();
    var fields=['fio','phone','email','count','tourname','date'],invalid=null;
    fields.some(function(id){var field=d.getElementById(id);if(field&&!field.value.trim()){invalid=field;return true;}return false;});
    if(!invalid&& !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.getElementById('email').value))invalid=d.getElementById('email');
    if(!invalid&&!/^[1-9]\d*$/.test(d.getElementById('count').value))invalid=d.getElementById('count');
    if(!invalid&&!/^\d{2}\.\d{2}\.\d{4}$/.test(d.getElementById('date').value))invalid=d.getElementById('date');
    var check=d.getElementById('stage-captcha');if(!invalid&&check&&!check.checked)invalid=check;
    status.setAttribute('data-error',String(!!invalid));
    if(invalid){status.textContent=en?'Please complete the required fields and the demo check.':'Заполните обязательные поля и отметьте демопроверку.';invalid.focus();return;}
    status.textContent=en?'Demo check completed. No enquiry was sent or saved.':'Демопроверка пройдена. Заявка не отправлена, данные не сохранены.';
    status.scrollIntoView({block:'nearest',behavior:'smooth'});
   }
   form.addEventListener('submit',submit,true);
   var button=d.getElementById('form_sub_btn');if(button)button.addEventListener('click',submit,true);
   var requested=new URLSearchParams(location.search).get('tour');if(requested&&d.getElementById('tourname'))d.getElementById('tourname').value=requested.slice(0,300);
  }
  if(w.jQuery){var ajax=jQuery.ajax;jQuery.ajax=function(options){if(typeof options==='object'&&/ajax\.php/.test(options.url||'')){if(options.success)options.success({error:true,message:en?'Instagram connection will be completed after approval. Use the profile link.':'Подключение Instagram завершим после согласования. Сейчас доступна ссылка на профиль.',next_cursor:null,posts:[]});return {abort:function(){}};}return ajax.apply(this,arguments);};}
 }
 if(d.readyState==='loading')d.addEventListener('DOMContentLoaded',ready);else ready();
})(window,document);
