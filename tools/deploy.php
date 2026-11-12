<?php
// One-off deploy helper for almaty-travel.kz (removed after use).
if (!isset($_GET['t']) || !hash_equals('__DEPLOY_TOKEN__', (string)$_GET['t'])) { http_response_code(404); exit; }
@set_time_limit(600); @ini_set('memory_limit', '256M');
header('Content-Type: text/plain; charset=utf-8');
$doc = __DIR__; $home = dirname(dirname(__DIR__)); $work = $home . '/_deploy';
$old = $work . '/old'; $src = $work . '/x/almaty-travel-review-live-site';
@mkdir($work, 0755, true); @mkdir($old, 0755, true);
$step = isset($_GET['step']) ? $_GET['step'] : 'info';
function rrm($p) { if (is_dir($p) && !is_link($p)) { foreach (scandir($p) as $f) if ($f !== '.' && $f !== '..') rrm("$p/$f"); return rmdir($p); } return @unlink($p); }
if ($step === 'info') {
    echo "php ", PHP_VERSION, "\nzip ", class_exists('ZipArchive') ? 'yes' : 'no', "\ncurl ", function_exists('curl_init') ? 'yes' : 'no';
    echo "\nmax_exec ", ini_get('max_execution_time'), "\nhome $home\ndoc $doc\n";
    echo "work: "; print_r(is_dir($work) ? scandir($work) : 'none'); exit;
}
if ($step === 'download') {
    $zip = "$work/live.zip"; $fp = fopen($zip, 'w');
    $ch = curl_init('https://codeload.github.com/adirov/almaty-travel-review/zip/refs/heads/live-site');
    curl_setopt_array($ch, array(CURLOPT_FILE => $fp, CURLOPT_FOLLOWLOCATION => true, CURLOPT_TIMEOUT => 550, CURLOPT_USERAGENT => 'deploy'));
    $ok = curl_exec($ch); $code = curl_getinfo($ch, CURLINFO_HTTP_CODE); $err = curl_error($ch); curl_close($ch); fclose($fp);
    echo "ok=", var_export($ok, true), " http=$code err=$err size=", filesize($zip), "\n"; exit;
}
if ($step === 'extract') {
    if (is_dir("$work/x")) rrm("$work/x");
    $z = new ZipArchive(); $r = $z->open("$work/live.zip"); if ($r !== true) { echo "open failed $r\n"; exit; }
    $n = $z->numFiles; $ok = $z->extractTo("$work/x"); $z->close();
    echo "files=$n extracted=", var_export($ok, true), "\n"; if ($ok) { unlink("$work/live.zip"); echo "zip removed\n"; }
    print_r(scandir($src)); exit;
}
if ($step === 'install') {
    // secret for lead.php comes from the old order.php, never from git
    if (!file_exists("$doc/lead-config.php")) {
        $o = file_get_contents("$doc/order.php");
        if (preg_match('/RECAPTCHA_SECRET_KEY\s*=\s*\'([^\']+)\'/', $o, $m)) {
            file_put_contents("$doc/lead-config.php", "<?php\nreturn array('recaptcha_secret' => '" . $m[1] . "', 'to' => 'info@almaty-travel.kz');\n");
            echo "lead-config.php created\n";
        } else echo "SECRET NOT FOUND\n";
    }
    foreach (scandir($src) as $f) {
        if ($f === '.' || $f === '..' || $f === '.htaccess') continue;
        $to = "$doc/$f";
        if (file_exists($to)) {
            if (is_dir($to)) { echo "SKIP existing dir $f\n"; continue; }
            rename($to, "$old/$f"); echo "saved old $f\n";
        }
        echo (rename("$src/$f", $to) ? "installed " : "FAILED ") . "$f\n";
    }
    exit;
}
if ($step === 'htaccess') {
    if (!file_exists("$old/.htaccess")) copy("$doc/.htaccess", "$old/.htaccess");
    echo copy("$src/.htaccess", "$doc/.htaccess") ? "new .htaccess live\n" : "FAILED\n"; exit;
}
if ($step === 'rollback') {
    foreach (array('.htaccess', 'robots.txt', 'sitemap.xml') as $f) if (file_exists("$old/$f")) { copy("$old/$f", "$doc/$f"); echo "restored $f\n"; }
    if (file_exists("$doc/index.html")) { rename("$doc/index.html", "$old/index.html.new"); echo "root index.html moved away\n"; }
    exit;
}
if ($step === 'update') {
    function rcp($a, $b) { if (is_dir($a)) { if (!is_dir($b)) mkdir($b, 0755, true); $n = 0; foreach (scandir($a) as $f) if ($f !== '.' && $f !== '..') $n += rcp("$a/$f", "$b/$f"); return $n; } return copy($a, $b) ? 1 : 0; }
    $n = 0; foreach (scandir($src) as $f) { if ($f === '.' || $f === '..') continue; $n += rcp("$src/$f", "$doc/$f"); }
    echo "copied $n files\n";
    foreach (array('ru/photo/432', 'ru/photo/463', 'summer/ru/photo/432', 'summer/ru/photo/463') as $d) if (is_dir("$doc/$d")) { rrm("$doc/$d"); echo "removed $d\n"; }
    exit;
}
if ($step === 'cleanup') { if (is_dir("$work/x")) rrm("$work/x"); echo "x removed\n"; print_r(scandir($work)); exit; }
if ($step === 'selfdelete') { echo unlink(__FILE__) ? "deleted\n" : "fail\n"; exit; }
echo "unknown step\n";
