<?php
/** @var array<string, mixed> $meta */
$title = $meta['title'] ?? config('name') . ' — Founding Client Program';
$description = $meta['description'] ?? '2 of 3 founding client spots open for local service businesses. Custom website, no setup fee. $199/month — hosting and maintenance included.';
$url = rtrim(config('url'), '/');
$ogImage = $url . '/images/og-image.svg';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?= e($title) ?></title>
    <meta name="description" content="<?= e($description) ?>">
    <link rel="canonical" href="<?= e($url) ?>">
    <meta name="robots" content="index, follow">
    <meta name="theme-color" content="#0a0a0a">

    <meta property="og:type" content="website">
    <meta property="og:url" content="<?= e($url) ?>">
    <meta property="og:title" content="<?= e($title) ?>">
    <meta property="og:description" content="<?= e($description) ?>">
    <meta property="og:site_name" content="<?= e(config('name')) ?>">
    <meta property="og:image" content="<?= e($ogImage) ?>">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">

    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="<?= e($title) ?>">
    <meta name="twitter:description" content="<?= e($description) ?>">
    <meta name="twitter:image" content="<?= e($ogImage) ?>">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/app.css?v=2">

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
            'description' => 'Founding client program — custom website with monthly hosting and maintenance.',
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
<body class="has-mobile-cta">
<a class="skip-link" href="#apply">Skip to application form</a>
