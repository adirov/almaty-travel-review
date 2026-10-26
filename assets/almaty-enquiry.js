(function(w,d){'use strict';function init(){var f=d.getElementById('order_form');if(!f||f.getAttribute('data-enquiry-bound'))return;f.setAttribute('data-enquiry-bound','1');var en=d.documentElement.lang==='en'||/^\/en\//.test(location.pathname);var busy=false;
if(w.jQuery&&jQuery.datepicker){
var calendar={dateFormat:'dd.mm.yy',firstDay:1,changeYear:true,
dayNames:en?['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']:['Воскресенье','Понедельник','Вторник','Среда','Четверг','Пятница','Суббота'],
dayNamesMin:en?['Su','Mo','Tu','We','Th','Fr','Sa']:['Вс','Пн','Вт','Ср','Чт','Пт','Сб'],
dayNamesShort:en?['Sun','Mon','Tue','Wed','Thu','Fri','Sat']:['Вс','Пн','Вт','Ср','Чт','Пт','Сб'],
monthNames:en?['January','February','March','April','May','June','July','August','September','October','November','December']:['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'],
monthNamesShort:en?['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']:['Янв','Фев','Мар','Апр','Май','Июн','Июл','Авг','Сен','Окт','Ноя','Дек'],
prevText:en?'Previous':'Предыдущий',nextText:en?'Next':'Следующий',closeText:en?'Close':'Закрыть',currentText:en?'Today':'Сегодня'};
var field=jQuery('#date');if(field.hasClass('hasDatepicker'))field.datepicker('option',calendar);else field.datepicker(calendar);
}
f.addEventListener('submit',function(e){if(busy){e.preventDefault();return;}var errors=[],focus=null;var keys=['fio','phone','email','count','tourname','date'];keys.forEach(function(key){var field=f.elements[key];if(!field.value.trim()){errors.push((en?'Please enter ':'Укажите ')+(f.querySelector('label[for="'+key+'"]').textContent));if(!focus)focus=field;}});if(f.elements.email.value&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.elements.email.value)){errors.push(en?'Please enter a valid e-mail address.':'Укажите корректный e-mail.');if(!focus)focus=f.elements.email;}if(f.elements.count.value&&!/^[1-9]\d*$/.test(f.elements.count.value)){errors.push(en?'Please enter a valid number of people.':'Укажите корректное количество человек.');if(!focus)focus=f.elements.count;}
if(typeof w.grecaptcha==='undefined'||!w.grecaptcha.getResponse()){errors.push(en?'Please confirm that you are not a robot.':'Подтвердите, что вы не робот.');}
if(errors.length){e.preventDefault();if(focus)focus.focus();w.alert(errors.join('\n'));return;}busy=true;var send=d.getElementById('form_sub_btn');send.disabled=true;send.setAttribute('aria-disabled','true');});
}if(d.readyState==='loading')d.addEventListener('DOMContentLoaded',init);else init();})(window,document);
