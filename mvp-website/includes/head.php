<?php
/** @var array<string, mixed> $meta */
$title = $meta['title'] ?? config('name') . ' — Launch Partner Program';
$description = $meta['description'] ?? 'Launch Partner spots for local service businesses. $0 setup, $199/mo. Text LAUNCH to apply.';
$url = rtrim(config('url'), '/');
$ogImage = $url . '/images/og-image.png';
$offer = config('offer');
?>
<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script>document.documentElement.className = document.documentElement.className.replace('no-js', 'js');</script>
    <title><?= e($title) ?></title>
    <meta name="description" content="<?= e($description) ?>">
    <link rel="canonical" href="<?= e($url) ?>">
    <meta name="robots" content="index, follow">
    <meta name="theme-color" content="#fafafa">

    <meta property="og:type" content="website">
    <meta property="og:url" content="<?= e($url) ?>">
    <meta property="og:title" content="<?= e($title) ?>">
    <meta property="og:description" content="<?= e($description) ?>">
    <meta property="og:site_name" content="<?= e(config('name')) ?>">
    <meta property="og:image" content="<?= e($ogImage) ?>">
    <meta property="og:image:type" content="image/png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="Groundwork Web — Launch Partner Program for local service businesses">

    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="<?= e($title) ?>">
    <meta name="twitter:description" content="<?= e($description) ?>">
    <meta name="twitter:image" content="<?= e($ogImage) ?>">
    <meta name="twitter:image:alt" content="Groundwork Web — Launch Partner Program for local service businesses">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="preload" href="/css/app.css?v=5" as="style">
    <link rel="stylesheet" href="/css/app.css?v=5">

    <script type="application/ld+json">
    <?= json_encode([
        '@context' => 'https://schema.org',
        '@type' => 'ProfessionalService',
        'name' => config('name'),
        'url' => $url,
        'email' => config('email'),
        'description' => $description,
        'areaServed' => ['@type' => 'Country', 'name' => 'United States'],
        'offers' => [
            '@type' => 'Offer',
            'name' => config('offer.name'),
            'price' => (string) config('offer.monthly'),
            'priceCurrency' => 'USD',
            'description' => 'Launch Partner Program — custom website with monthly hosting and maintenance.',
        ],
    ], JSON_UNESCAPED_SLASHES) ?>
    </script>
    <script type="application/ld+json">
    <?= json_encode([
        '@context' => 'https://schema.org',
        '@type' => 'FAQPage',
        'mainEntity' => array_map(fn ($f) => [
            '@type' => 'Question',
            'name' => $f['q'],
            'acceptedAnswer' => ['@type' => 'Answer', 'text' => $f['a']],
        ], config('faqs')),
    ], JSON_UNESCAPED_SLASHES) ?>
    </script>
</head>
<body>
<a class="skip-link" href="#text">Skip to text CTA</a>
