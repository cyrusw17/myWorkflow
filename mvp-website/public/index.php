<?php

declare(strict_types=1);

require dirname(__DIR__) . '/lib/bootstrap.php';
require dirname(__DIR__) . '/lib/LeadStore.php';

session_start();

$meta = [
    'title' => config('name') . ' — Founding Client Program (2/3 Spots Open)',
    'description' => '2 of 3 founding client spots open for local service businesses. Custom website, no setup fee. $199/month with hosting and maintenance included.',
];

$formSuccess = false;
$formErrors = [];
$formOld = [];
$csrfToken = $_SESSION['_csrf'] ??= bin2hex(random_bytes(32));

if (($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'POST') {
    $formOld = [
        'name' => trim($_POST['name'] ?? ''),
        'phone' => trim($_POST['phone'] ?? ''),
        'email' => trim($_POST['email'] ?? ''),
        'business_name' => trim($_POST['business_name'] ?? ''),
        'location' => trim($_POST['location'] ?? ''),
        'industry' => trim($_POST['industry'] ?? ''),
        'contact_method' => trim($_POST['contact_method'] ?? ''),
        'contact_time' => trim($_POST['contact_time'] ?? ''),
        'message' => trim($_POST['message'] ?? ''),
    ];

    $allowedMethods = array_keys(config('form_contact_methods'));
    $allowedTimes = array_keys(config('form_contact_times'));

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
        if ($formOld['location'] === '') {
            $formErrors['location'] = 'Location is required.';
        }
        if ($formOld['industry'] === '') {
            $formErrors['industry'] = 'Please select an industry.';
        }
        if ($formOld['contact_method'] === '' || ! in_array($formOld['contact_method'], $allowedMethods, true)) {
            $formErrors['contact_method'] = 'Please choose how we should contact you.';
        }
        if ($formOld['contact_time'] === '' || ! in_array($formOld['contact_time'], $allowedTimes, true)) {
            $formErrors['contact_time'] = 'Please choose the best time to contact you.';
        }
        if ($formOld['contact_method'] === 'email') {
            if ($formOld['email'] === '') {
                $formErrors['email'] = 'Email is required when email is your preferred contact method.';
            } elseif (! filter_var($formOld['email'], FILTER_VALIDATE_EMAIL)) {
                $formErrors['email'] = 'Please enter a valid email address.';
            }
        } elseif ($formOld['email'] !== '' && ! filter_var($formOld['email'], FILTER_VALIDATE_EMAIL)) {
            $formErrors['email'] = 'Please enter a valid email address.';
        }
        if (trim($_POST['website'] ?? '') !== '') {
            $formErrors['_form'] = 'Unable to submit. Please try again.';
        }

        if (empty($formErrors)) {
            try {
                $store = new LeadStore(dirname(__DIR__) . '/storage/leads.sqlite');
                $store->save($formOld + ['source' => 'founding-landing']);

                $methodLabel = config('form_contact_methods')[$formOld['contact_method']] ?? $formOld['contact_method'];
                $timeLabel = config('form_contact_times')[$formOld['contact_time']] ?? $formOld['contact_time'];

                $logLine = sprintf(
                    "[%s] %s | %s | %s | %s | %s | %s | %s\n",
                    gmdate('c'),
                    $formOld['name'],
                    $formOld['phone'],
                    $formOld['business_name'],
                    $formOld['location'],
                    $formOld['industry'],
                    $methodLabel,
                    $timeLabel
                );
                file_put_contents(dirname(__DIR__) . '/storage/leads.log', $logLine, FILE_APPEND | LOCK_EX);

                $mailTo = getenv('MAIL_TO') ?: config('email');
                $subject = 'Founding client lead: ' . $formOld['business_name'];
                $body = implode("\n", [
                    'New founding client application',
                    '',
                    'Name: ' . $formOld['name'],
                    'Phone: ' . $formOld['phone'],
                    'Email: ' . ($formOld['email'] ?: '(none)'),
                    'Business: ' . $formOld['business_name'],
                    'Location: ' . $formOld['location'],
                    'Industry: ' . $formOld['industry'],
                    'Preferred contact: ' . $methodLabel,
                    'Best time: ' . $timeLabel,
                ]);
                @mail($mailTo, $subject, $body, 'From: ' . config('email'));

                $formSuccess = true;
                $formOld = [];
                $_SESSION['_csrf'] = bin2hex(random_bytes(32));
                $csrfToken = $_SESSION['_csrf'];
            } catch (Throwable $e) {
                $formErrors['_form'] = 'Something went wrong. Email us at ' . config('email');
            }
        }
    }
}

require dirname(__DIR__) . '/includes/head.php';
require dirname(__DIR__) . '/includes/header.php';

$sections = [
    'hero',
    'social-proof',
    'offer',
    'included',
    'why',
    'how-it-works',
    'why-custom',
    'faq',
    'final-cta',
];

echo '<main>';
foreach ($sections as $section) {
    require dirname(__DIR__) . "/includes/sections/{$section}.php";
}
echo '</main>';

require dirname(__DIR__) . '/includes/footer.php';
