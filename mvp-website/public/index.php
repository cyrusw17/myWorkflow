<?php

declare(strict_types=1);

require dirname(__DIR__) . '/lib/bootstrap.php';
require dirname(__DIR__) . '/lib/LeadStore.php';

session_start();

$offer = config('offer');
$spots = (int) $offer['spots_remaining'];

$meta = [
    'title' => config('name') . ' — Launch Partner Program (' . $spots . '/3 Spots Left)',
    'description' => $spots . ' of 3 Launch Partner spots for local service businesses. $0 setup, $199/mo — custom website, hosting, and maintenance. Text LAUNCH to apply.',
];

$formSuccess = false;
$formErrors = [];
$formOld = [];
$csrfToken = $_SESSION['_csrf'] ??= bin2hex(random_bytes(32));

if (($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'POST') {
    $formOld = [
        'name' => trim($_POST['name'] ?? ''),
        'phone' => trim($_POST['phone'] ?? ''),
        'business_name' => trim($_POST['business_name'] ?? ''),
        'location' => '',
        'industry' => trim($_POST['industry'] ?? ''),
        'email' => '',
        'contact_method' => 'text',
        'contact_time' => 'anytime',
        'message' => '',
    ];

    $allowedIndustries = config('qualify_industries');

    if (! hash_equals($csrfToken, $_POST['_token'] ?? '')) {
        $formErrors['_form'] = 'Session expired. Please try again.';
    } else {
        if ($formOld['name'] === '') {
            $formErrors['name'] = 'Name is required.';
        }
        if ($formOld['phone'] === '') {
            $formErrors['phone'] = 'Phone is required.';
        }
        if ($formOld['business_name'] === '') {
            $formErrors['business_name'] = 'Business name is required.';
        }
        if ($formOld['industry'] === '' || ! in_array($formOld['industry'], $allowedIndustries, true)) {
            $formErrors['industry'] = 'Please select an industry.';
        }
        if (trim($_POST['website'] ?? '') !== '') {
            $formErrors['_form'] = 'Unable to submit. Please try again.';
        }

        if (empty($formErrors)) {
            try {
                $store = new LeadStore(dirname(__DIR__) . '/storage/leads.sqlite');
                $store->save($formOld + ['source' => 'launch-partner-qualify']);

                $logLine = sprintf(
                    "[%s] QUALIFY | %s | %s | %s | %s\n",
                    gmdate('c'),
                    $formOld['name'],
                    $formOld['phone'],
                    $formOld['business_name'],
                    $formOld['industry']
                );
                file_put_contents(dirname(__DIR__) . '/storage/leads.log', $logLine, FILE_APPEND | LOCK_EX);

                $mailTo = getenv('MAIL_TO') ?: config('email');
                $subject = 'Launch Partner qualify: ' . $formOld['business_name'];
                $body = implode("\n", [
                    'Launch Partner qualification form',
                    '',
                    'Name: ' . $formOld['name'],
                    'Phone: ' . $formOld['phone'],
                    'Business: ' . $formOld['business_name'],
                    'Industry: ' . $formOld['industry'],
                    '',
                    'Preferred path: Text ' . config('sms_keyword') . ' to ' . config('phone_display'),
                ]);
                @mail($mailTo, $subject, $body, 'From: ' . config('email'));

                $formSuccess = true;
                $formOld = [];
                $_SESSION['_csrf'] = bin2hex(random_bytes(32));
                $csrfToken = $_SESSION['_csrf'];
            } catch (Throwable $e) {
                $formErrors['_form'] = 'Something went wrong. Text ' . config('sms_keyword') . ' to ' . config('phone_display');
            }
        }
    }
}

require dirname(__DIR__) . '/includes/head.php';
require dirname(__DIR__) . '/includes/header.php';

$sections = [
    'hero',
    'offer',
    'why',
    'included',
    'how-it-works',
    'why-custom',
    'trust',
    'faq',
    'final-cta',
];

echo '<main>';
foreach ($sections as $section) {
    require dirname(__DIR__) . "/includes/sections/{$section}.php";
}
echo '</main>';

require dirname(__DIR__) . '/includes/footer.php';
