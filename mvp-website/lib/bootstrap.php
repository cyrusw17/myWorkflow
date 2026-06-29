<?php

declare(strict_types=1);

$root = dirname(__DIR__);

if (is_file($root . '/.env')) {
    foreach (file($root . '/.env', FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
        if (str_starts_with(trim($line), '#') || ! str_contains($line, '=')) {
            continue;
        }
        [$key, $value] = explode('=', $line, 2);
        putenv(trim($key) . '=' . trim($value, " \t\"'"));
    }
}

$config = require $root . '/config/site.php';

function config(string $key, mixed $default = null): mixed
{
    global $config;
    $keys = explode('.', $key);
    $value = $config;
    foreach ($keys as $k) {
        if (! is_array($value) || ! array_key_exists($k, $value)) {
            return $default;
        }
        $value = $value[$k];
    }
    return $value;
}

function e(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES, 'UTF-8');
}

function asset(string $path): string
{
    $base = rtrim(config('url', ''), '/');
    return $base . '/' . ltrim($path, '/');
}

function phone_digits(): string
{
    return preg_replace('/\D/', '', (string) config('phone_sms', ''));
}

function has_phone(): bool
{
    return phone_digits() !== '' && trim((string) config('phone_display', '')) !== '';
}

function sms_href(): string
{
    if (! has_phone()) {
        return '#qualify';
    }
    $body = rawurlencode((string) config('sms_keyword', 'LAUNCH'));

    return 'sms:' . phone_digits() . '?&body=' . $body;
}

function text_cta_label(): string
{
    if (! has_phone()) {
        return 'Apply for a Launch Partner Spot';
    }

    return 'Text "' . config('sms_keyword', 'LAUNCH') . '" to ' . config('phone_display', '');
}
