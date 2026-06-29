@extends('layouts.app')

@section('content')
<section class="page-hero">
    <div class="container reveal">
        <p class="eyebrow">Services</p>
        <h1 class="display" style="font-size:clamp(2.25rem,4.5vw,3.25rem);">A growth system — not just a website.</h1>
        <p class="lead">Setup, hosting, maintenance, and SEO foundations — one partner, one monthly plan.</p>
        <a href="{{ route('contact') }}#form" class="btn btn-primary">Book a Call to Get Your Quote</a>
    </div>
</section>

<section class="section section-light">
    <div class="container reveal">
        <div class="section-header">
            <p class="eyebrow">What's included</p>
            <h2 class="h2">Four layers. One partner.</h2>
        </div>
        <div class="bento">
            @foreach (config('site.system_layers') as $i => $layer)
                <div class="card {{ $i === 0 ? 'bento-featured' : '' }}">
                    <span class="badge">{{ str_pad($i + 1, 2, '0', STR_PAD_LEFT) }}</span>
                    <h3 class="h3" style="margin-top:0.75rem;">{{ $layer['title'] }}</h3>
                    <p class="text-muted" style="margin:0;">{{ $layer['body'] }}</p>
                    @if ($layer['key'] === 'build')
                        <ul style="margin:1.25rem 0 0;padding:0;list-style:none;">
                            <li class="text-muted" style="padding:0.35rem 0;font-size:0.9rem;">✓ Custom design &amp; development</li>
                            <li class="text-muted" style="padding:0.35rem 0;font-size:0.9rem;">✓ Mobile-first, fast loading</li>
                            <li class="text-muted" style="padding:0.35rem 0;font-size:0.9rem;">✓ Contact / lead capture flows</li>
                            <li class="text-muted" style="padding:0.35rem 0;font-size:0.9rem;">✓ Launch on your domain</li>
                        </ul>
                    @endif
                </div>
            @endforeach
            <div class="card" style="opacity:0.85;border-style:dashed;">
                <span class="badge">Coming soon</span>
                <h3 class="h3" style="margin-top:0.75rem;">Automate</h3>
                <p class="text-muted" style="margin:0;">AI chat, review requests, lead routing — add-ons as you grow.</p>
            </div>
        </div>
    </div>
</section>

<section class="section section-dark">
    <div class="container reveal">
        <div class="section-header center">
            <p class="eyebrow" style="justify-content:center;">Pricing</p>
            <h2 class="h2">Clear starting points</h2>
            <p class="lead" style="margin-inline:auto;">Final quote depends on scope — we'll walk through it on your discovery call.</p>
        </div>
        <div class="pricing-grid">
            <div class="card pricing-card">
                <h3 class="h3">Build</h3>
                <p class="price">from ${{ number_format(config('site.pricing.build')) }}</p>
                <p class="price-note">one-time</p>
                <ul>
                    <li>Custom 5-page site</li>
                    <li>Mobile-first design</li>
                    <li>Lead capture flow</li>
                    <li>Launch support</li>
                </ul>
                <a href="{{ route('contact') }}#form" class="btn btn-secondary-dark btn-block">Get a quote</a>
            </div>
            <div class="card pricing-card">
                <h3 class="h3">Growth Plan</h3>
                <p class="price">from ${{ config('site.pricing.growth_monthly') }}/mo</p>
                <p class="price-note">recurring</p>
                <ul>
                    <li>Hosting &amp; SSL</li>
                    <li>Maintenance &amp; updates</li>
                    <li>Uptime monitoring</li>
                    <li>Minor content changes</li>
                </ul>
                <a href="{{ route('contact') }}#form" class="btn btn-secondary-dark btn-block">Get a quote</a>
            </div>
            <div class="card pricing-card featured">
                <span class="badge">Most clients</span>
                <h3 class="h3" style="margin-top:0.75rem;">Full System</h3>
                <p class="price">from ${{ number_format(config('site.pricing.build')) }}</p>
                <p class="price-note">+ ${{ config('site.pricing.growth_monthly') }}/mo</p>
                <ul>
                    <li>Everything in Build</li>
                    <li>Everything in Growth Plan</li>
                    <li>SEO foundations</li>
                    <li>One partner, one bill</li>
                </ul>
                <a href="{{ route('contact') }}#form" class="btn btn-primary btn-block">Get a quote</a>
            </div>
        </div>
    </div>
</section>

<section class="section section-light">
    <div class="container reveal">
        <div class="section-header center">
            <h2 class="h2">Groundwork Web vs DIY</h2>
        </div>
        <table class="compare-table">
            <thead>
                <tr><th></th><th>Wix / DIY</th><th>Groundwork Web</th></tr>
            </thead>
            <tbody>
                <tr><td>Custom design</td><td>✗</td><td>✓</td></tr>
                <tr><td>You maintain it</td><td>✓</td><td>✗</td></tr>
                <tr><td>Built for phone calls</td><td>~</td><td>✓</td></tr>
                <tr><td>Hosting included</td><td>~</td><td>✓</td></tr>
                <tr><td>Ongoing support</td><td>✗</td><td>✓</td></tr>
            </tbody>
        </table>
    </div>
</section>

@include('components.cta-band')
@endsection
