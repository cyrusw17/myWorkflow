<!DOCTYPE html>
@php
    $hasDarkHero = ! request()->routeIs('errors.*') && ! request()->is('*404*');
@endphp
<html lang="en" class="{{ $hasDarkHero ? 'has-dark-hero' : '' }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ $meta['title'] ?? config('site.name') }}</title>
    <meta name="description" content="{{ $meta['description'] ?? config('site.tagline') }}">
    <link rel="canonical" href="{{ url()->current() }}">
    <meta property="og:title" content="{{ $meta['title'] ?? config('site.name') }}">
    <meta property="og:description" content="{{ $meta['description'] ?? config('site.tagline') }}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{{ url()->current() }}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
    @if (file_exists(public_path('build/manifest.json')))
        @vite(['resources/css/app.css', 'resources/js/app.js'])
    @else
        <link rel="stylesheet" href="{{ asset('css/site.css') }}?v=3">
        <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.3/dist/cdn.min.js"></script>
    @endif
    @stack('head')
</head>
<body>
    <a href="#main" class="skip-link">Skip to main content</a>

    @include('components.header')

    <main id="main">
        @yield('content')
    </main>

    @include('components.footer')

    @unless (file_exists(public_path('build/manifest.json')))
        <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function () {
                var header = document.querySelector('.site-header');
                if (header) {
                    window.addEventListener('scroll', function () {
                        header.classList.toggle('is-scrolled', window.scrollY > 60);
                    }, { passive: true });
                }

                if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches && window.gsap) {
                    document.documentElement.classList.add('js-animations');
                    gsap.registerPlugin(ScrollTrigger);
                    gsap.utils.toArray('.reveal').forEach(function (el) {
                        gsap.fromTo(el,
                            { opacity: 0, y: 24 },
                            {
                                opacity: 1, y: 0, duration: 0.65, ease: 'power2.out',
                                scrollTrigger: { trigger: el, start: 'top 88%' }
                            }
                        );
                    });
                }
            });
        </script>
    @endunless
    @stack('scripts')
</body>
</html>
