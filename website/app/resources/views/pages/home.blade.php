@extends('layouts.app')

@push('head')
<script type="application/ld+json">
{!! json_encode([
    '@'.'context' => 'https://schema.org',
    '@'.'type' => 'Organization',
    'name' => config('site.name'),
    'url' => url('/'),
    'email' => config('site.email'),
    'areaServed' => ['@'.'type' => 'Country', 'name' => 'United States'],
], JSON_UNESCAPED_SLASHES) !!}
</script>
<script type="application/ld+json">
{!! json_encode([
    '@'.'context' => 'https://schema.org',
    '@'.'type' => 'FAQPage',
    'mainEntity' => collect(config('site.faqs'))->map(fn ($f) => [
        '@'.'type' => 'Question',
        'name' => $f['q'],
        'acceptedAnswer' => ['@'.'type' => 'Answer', 'text' => $f['a']],
    ])->values(),
], JSON_UNESCAPED_SLASHES) !!}
</script>
@endpush

@section('content')
<section class="hero-premium">
    <div class="hero-bg" aria-hidden="true"></div>
    <div class="container hero-grid">
        <div class="reveal">
            <div class="hero-badge">
                <span class="hero-badge-dot"></span>
                Local service growth partner
            </div>
            <h1 class="display">
                More calls.<br>
                <span class="text-gradient">Zero headaches.</span>
            </h1>
            <p class="lead">We build custom websites for shops and trades — then run hosting, updates, and maintenance so your phone rings and you never touch the tech.</p>
            <div class="btn-group">
                <a href="{{ route('contact') }}#form" class="btn btn-primary">Book a Free Discovery Call</a>
                <a href="{{ route('work') }}" class="btn btn-secondary">See our work</a>
            </div>
            <p class="micro" style="color:rgba(255,255,255,0.4);">30 min · No obligation · Honest fit check</p>
            <div class="proof-pills">
                <span class="proof-pill">Custom-coded</span>
                <span class="proof-pill">Mobile-first</span>
                <span class="proof-pill">Hosting included</span>
            </div>
            <div class="stat-row">
                <div><strong>$2,500+</strong><span>typical build</span></div>
                <div><strong>$199/mo</strong><span>growth plan</span></div>
                <div><strong>2–4 wks</strong><span>to launch</span></div>
            </div>
        </div>
        <div class="hero-visual reveal">
            <div class="hero-visual-glow" aria-hidden="true"></div>
            <div class="mockup-frame">
                <div class="mockup-chrome">
                    <i></i><i></i><i></i>
                    <span>westsideautocare.com</span>
                </div>
                <img src="{{ asset('images/work/westside-hero.svg') }}" alt="Example website built for a local auto shop" width="800" height="500">
            </div>
        </div>
    </div>
</section>

<section class="section section-light" id="who-we-help">
    <div class="container">
        <div class="section-header center reveal">
            <p class="eyebrow" style="justify-content:center;">Who we work with</p>
            <h2 class="h2">Built for businesses that run on phone calls</h2>
            <p class="lead" style="margin-inline:auto;">Auto shops, contractors, trades — if your customers find you online and call, we're built for you.</p>
        </div>
        <div class="grid-4">
            @php
                $icons = [
                    '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
                    '<path d="m2 22 10-10"/><path d="m12 12 10-10"/><path d="m2 2 20 20"/>',
                    '<path d="M12 2v4"/><path d="m6.8 15-3.5 2"/><path d="m20.7 17-3.5-2"/><path d="M6.8 9 3.3 7"/><path d="m20.7 7-3.5 2"/><circle cx="12" cy="13" r="3"/>',
                    '<rect width="16" height="20" x="4" y="2" rx="2"/><path d="M9 22v-4h6v4"/>',
                ];
            @endphp
            @foreach (config('site.industries') as $i => $industry)
                <div class="card reveal">
                    <div class="card-icon">
                        <svg viewBox="0 0 24 24" aria-hidden="true">{!! $icons[$i] ?? $icons[0] !!}</svg>
                    </div>
                    <h3 class="h3">{{ $industry['title'] }}</h3>
                </div>
            @endforeach
        </div>
    </div>
</section>

<section class="section section-dark">
    <div class="container">
        <div class="section-header reveal">
            <p class="eyebrow">Sound familiar?</p>
            <h2 class="h2">The problems costing you calls every week</h2>
        </div>
        <div class="grid-3">
            @foreach (config('site.pain_points') as $i => $pain)
                <div class="card reveal">
                    <p class="process-step-num">{{ str_pad($i + 1, 2, '0', STR_PAD_LEFT) }}</p>
                    <h3 class="h3">{{ $pain['title'] }}</h3>
                    <p class="text-muted" style="margin:0;">{{ $pain['body'] }}</p>
                </div>
            @endforeach
        </div>
    </div>
</section>

<section class="section section-light" id="system">
    <div class="container">
        <div class="section-header reveal">
            <p class="eyebrow">The Growth System</p>
            <h2 class="h2">Not a website. A system that runs your web presence.</h2>
            <p class="lead">Setup once. We handle everything after — so leads keep coming while you run the business.</p>
        </div>
        <div class="bento">
            @foreach (config('site.system_layers') as $i => $layer)
                <div class="card reveal {{ $i === 0 ? 'bento-featured' : '' }}">
                    <span class="badge">{{ str_pad($i + 1, 2, '0', STR_PAD_LEFT) }}</span>
                    <h3 class="h3" style="margin-top:1rem;">{{ $layer['title'] }}</h3>
                    <p class="text-muted" style="margin:0;">{{ $layer['body'] }}</p>
                    @if ($i === 0)
                        <ul style="margin:1.25rem 0 0;padding:0;list-style:none;">
                            <li class="text-muted" style="padding:0.35rem 0;font-size:0.9rem;">✓ Custom design &amp; development</li>
                            <li class="text-muted" style="padding:0.35rem 0;font-size:0.9rem;">✓ Mobile-first, built for calls</li>
                            <li class="text-muted" style="padding:0.35rem 0;font-size:0.9rem;">✓ Launch on your domain</li>
                        </ul>
                    @endif
                </div>
            @endforeach
        </div>
        <p style="margin-top:2rem;" class="reveal">
            <a href="{{ route('services') }}" class="btn btn-secondary-dark btn-sm">View pricing &amp; services →</a>
        </p>
    </div>
</section>

@if ($featured)
<section class="section section-dark">
    <div class="container">
        <div class="section-header reveal">
            <p class="eyebrow">Selected work</p>
            <h2 class="h2">Premium sites for real local businesses</h2>
        </div>
        <div class="card project-card reveal" style="max-width:800px;">
            <div class="thumb">
                <img src="{{ asset('images/work/westside-hero.svg') }}" alt="Westside Auto Care website preview">
            </div>
            <div class="body">
                @if ($featured->is_concept)<span class="badge">Concept project</span>@endif
                <h3 class="h3" style="margin-top:0.75rem;color:#fff;">{{ $featured->title }}</h3>
                <p class="text-muted">{{ $featured->industry }} — {{ $featured->tagline }}</p>
                <a href="{{ route('work.show', $featured->slug) }}" class="btn btn-primary btn-sm" style="margin-top:1rem;">View case study →</a>
            </div>
        </div>
    </div>
</section>
@endif

<section class="section section-light">
    <div class="container">
        <div class="section-header center reveal">
            <p class="eyebrow" style="justify-content:center;">How it works</p>
            <h2 class="h2">Four steps. No surprises.</h2>
        </div>
        <div class="process-steps">
            @foreach (config('site.process_steps') as $step)
                <div class="process-card reveal">
                    <p class="process-step-num">{{ $step['step'] }}</p>
                    <h3 class="h3">{{ $step['title'] }}</h3>
                    <p class="text-muted" style="margin:0;font-size:0.9rem;">{{ $step['body'] }}</p>
                </div>
            @endforeach
        </div>
    </div>
</section>

<section class="section section-dark">
    <div class="container">
        <div class="section-header center reveal">
            <h2 class="h2">Why not Wix — or your nephew?</h2>
            <p class="lead" style="margin-inline:auto;">Cheap templates cost you time. We cost less than one lost customer per month.</p>
        </div>
        <div class="compare-grid">
            <div class="card compare-card reveal">
                <h3 class="h3">Templates &amp; DIY</h3>
                <ul>
                    @foreach (config('site.comparison.diy') as $item)<li>{{ $item }}</li>@endforeach
                </ul>
            </div>
            <div class="card compare-card us reveal">
                <h3 class="h3">Groundwork Web</h3>
                <ul>
                    @foreach (config('site.comparison.us') as $item)<li>{{ $item }}</li>@endforeach
                </ul>
            </div>
        </div>
    </div>
</section>

<section class="section section-light" id="faq" x-data="{ open: 0 }">
    <div class="container">
        <div class="section-header center reveal">
            <p class="eyebrow" style="justify-content:center;">FAQ</p>
            <h2 class="h2">Straight answers</h2>
        </div>
        <div class="faq-wrap reveal">
            @foreach (config('site.faqs') as $i => $faq)
                <div class="faq-item">
                    <button type="button" class="faq-question" @click="open = open === {{ $i }} ? -1 : {{ $i }}" :aria-expanded="open === {{ $i }}">
                        {{ $faq['q'] }}
                        <span x-text="open === {{ $i }} ? '−' : '+'"></span>
                    </button>
                    <div class="faq-answer" x-show="open === {{ $i }}" x-cloak style="display:none;">{{ $faq['a'] }}</div>
                </div>
            @endforeach
        </div>
    </div>
</section>

@include('components.cta-band')
@endsection
