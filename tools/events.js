/* Measurement of contact clicks and enquiry submits for GTM / Yandex Metrika.
   Events carry only the event name, where on the page the link was and the page path:
   no names, phone numbers, e-mails or form fields. */
(function () {
  var dl = window.dataLayer = window.dataLayer || [];
  function place(el) {
    var zones = [['.wa-float', 'floating_button'], ['#header', 'header'], ['#center_footer, #footer', 'footer'],
      ['.school-link', 'school_block'], ['.owner-contact-cta', 'page_cta'], ['.main_container', 'content']];
    for (var i = 0; i < zones.length; i++) { if (el.closest(zones[i][0])) return zones[i][1]; }
    return 'other';
  }
  function send(name, extra) {
    var ev = { event: name, page_path: location.pathname };
    for (var k in extra) ev[k] = extra[k];
    dl.push(ev);
    try { if (window.ym) window.ym(53138671, 'reachGoal', name); } catch (e) {}
  }
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a) return;
    var h = a.getAttribute('href') || '', name = null;
    if (/^(https?:\/\/)?(wa\.me|api\.whatsapp\.com|web\.whatsapp\.com)\//i.test(h) || /^whatsapp:/i.test(h)) name = 'whatsapp_click';
    else if (/^tel:/i.test(h)) name = 'phone_click';
    else if (/^mailto:kztravel@/i.test(h)) name = 'email_click';
    else if (/^https?:\/\/(www\.)?snow-school\.kz/i.test(h)) name = 'partner_school_click';
    if (name) send(name, { link_location: place(a) });
  }, true);
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (f && /lead\.php/.test(f.getAttribute('action') || '')) send('enquiry_submit', {});
  }, true);
})();
