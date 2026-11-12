<?php
// Enquiry handler for the static almaty-travel.kz site.
// Secret keys live only on the server in lead-config.php (never in git):
//   <?php return array('recaptcha_secret' => '...', 'to' => 'info@almaty-travel.kz');
$lang = (isset($_POST['lang']) && $_POST['lang'] === 'en') ? 'en' : 'ru';
$back = '/' . $lang . '/order/';
function go($url) { header('Location: ' . $url, true, 303); exit; }

if ($_SERVER['REQUEST_METHOD'] !== 'POST' || empty($_POST['do']) || $_POST['do'] !== 'send') go($back);
if (!empty($_POST['website'])) go($back . '?sent=1'); // honeypot: pretend success for bots

$cfg = @include(__DIR__ . '/lead-config.php');
if (!is_array($cfg) || empty($cfg['recaptcha_secret'])) go($back . '?error=config');

$field = function ($k, $max = 1000) {
    $v = isset($_POST[$k]) ? trim((string)$_POST[$k]) : '';
    return mb_substr($v, 0, $max, 'UTF-8');
};
$data = array(
    'fio' => $field('fio'), 'phone' => $field('phone'), 'email' => $field('email'),
    'count' => $field('count', 50), 'tourname' => $field('tourname'), 'date' => $field('date', 50),
    'comments' => $field('comments', 10000),
);
foreach (array('fio', 'phone', 'email', 'count', 'tourname', 'date') as $k) {
    if ($data[$k] === '') go($back . '?error=fields');
}
if (!filter_var($data['email'], FILTER_VALIDATE_EMAIL)) go($back . '?error=fields');

$token = isset($_POST['g-recaptcha-response']) ? (string)$_POST['g-recaptcha-response'] : '';
if ($token === '') go($back . '?error=captcha');
$query = http_build_query(array('secret' => $cfg['recaptcha_secret'], 'response' => $token, 'remoteip' => $_SERVER['REMOTE_ADDR']));
$ctx = stream_context_create(array('http' => array('method' => 'POST', 'timeout' => 10,
    'header' => "Content-Type: application/x-www-form-urlencoded\r\n", 'content' => $query)));
$verify = @file_get_contents('https://www.google.com/recaptcha/api/siteverify', false, $ctx);
$result = json_decode((string)$verify, true);
if (empty($result['success'])) go($back . '?error=captcha');

$h = function ($s) { return nl2br(htmlspecialchars($s, ENT_QUOTES, 'UTF-8')); };
$host = 'almaty-travel.kz';
$to = !empty($cfg['to']) ? $cfg['to'] : 'info@almaty-travel.kz';
$subject = 'Онлайн заявка с сайта ' . $host;
$body = '<html><body>Отправлено: ' . date('d.m.Y') . ' в ' . date('H:i') . ' с IP ' . $h($_SERVER['REMOTE_ADDR'])
    . ' (' . ($lang === 'en' ? 'английская' : 'русская') . ' версия)<br><br>'
    . '<b>Ф.И.О.:</b><br>' . $h($data['fio']) . '<br><br>'
    . '<b>Телефон:</b><br>' . $h($data['phone']) . '<br><br>'
    . '<b>E-mail:</b><br>' . $h($data['email']) . '<br><br>'
    . '<b>Количество человек:</b><br>' . $h($data['count']) . '<br><br>'
    . '<b>Тур:</b><br>' . $h($data['tourname']) . '<br><br>'
    . '<b>Дата:</b><br>' . $h($data['date']) . '<br><br>'
    . '<b>Комментарии:</b><br>' . $h($data['comments']) . '</body></html>';
$headers = 'MIME-Version: 1.0' . "\r\n"
    . 'Content-Type: text/html; charset=UTF-8' . "\r\n"
    . 'From: =?UTF-8?B?' . base64_encode('Сайт almaty-travel.kz') . '?= <admin@' . $host . '>' . "\r\n"
    . 'Reply-To: ' . $data['email'] . "\r\n";
$ok = @mail($to, '=?UTF-8?B?' . base64_encode($subject) . '?=', $body, $headers);
if (!empty($cfg['copy_to'])) @mail($cfg['copy_to'], '=?UTF-8?B?' . base64_encode($subject) . '?=', $body, $headers);
go($back . ($ok ? '?sent=1' : '?error=mail'));
