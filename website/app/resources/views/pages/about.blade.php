@extends('layouts.app')

@section('content')
<section class="page-hero">
    <div class="container reveal">
        <p class="eyebrow">About</p>
        <h1 class="display" style="font-size:clamp(2.25rem,4.5vw,3.25rem);">We get local businesses.</h1>
        <p class="lead">Groundwork Web exists so shop and trade owners can stop worrying about their website and focus on the work.</p>
    </div>
</section>

<section class="section section-light">
    <div class="container founder-grid reveal">
        <div class="founder-photo" aria-label="Founder photo placeholder">
            Photo coming soon
        </div>
        <div>
            <h2 class="h2">Meet Cyrus</h2>
            <p>I started Groundwork Web because local shop owners deserve better than broken templates and disappearing freelancers.</p>
            <p>Your business runs on phone calls, trust, and reputation — your website should work the same way. I build custom-coded sites that load fast, look professional on mobile, and actually make it easy for customers to contact you.</p>
            <p>Then I handle hosting and maintenance every month so you never think about plugins, downtime, or updates. You run your business. We run your web presence.</p>
            <p class="text-muted">We serve local service businesses across the United States — automotive shops, contractors, HVAC, and more.</p>
        </div>
    </div>
</section>

<section class="section section-dark">
    <div class="container reveal">
        <div class="section-header center">
            <p class="eyebrow" style="justify-content:center;">Values</p>
            <h2 class="h2">What we stand for</h2>
        </div>
        <div class="grid-3">
            <div class="card text-center">
                <div class="card-icon" style="margin-inline:auto;">
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                </div>
                <h3 class="h3">Reliability</h3>
                <p class="text-muted" style="margin:0;">We show up. Your site stays up.</p>
            </div>
            <div class="card text-center">
                <div class="card-icon" style="margin-inline:auto;">
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>
                </div>
                <h3 class="h3">Honesty</h3>
                <p class="text-muted" style="margin:0;">We'll tell you if we're not the right fit.</p>
            </div>
            <div class="card text-center">
                <div class="card-icon" style="margin-inline:auto;">
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3-1.9 5.8H4l4.9 3.6-1.9 5.8L12 14.6l5 3.8-1.9-5.8L20 8.8h-6.1z"/></svg>
                </div>
                <h3 class="h3">Craft</h3>
                <p class="text-muted" style="margin:0;">Custom code, not cookie-cutter templates.</p>
            </div>
        </div>
    </div>
</section>

<section class="section section-light">
    <div class="container reveal">
        <div class="card" style="max-width:720px;margin-inline:auto;padding:2.5rem;">
            <p class="eyebrow">How we work</p>
            <h2 class="h2">Partner, not freelancer</h2>
            <ul class="text-muted" style="line-height:1.8;">
                <li>Long-term monthly partnership — not a one-and-done project</li>
                <li>Built for local businesses nationwide</li>
                <li>Designed to drive phone calls and leads</li>
                <li>We handle the tech — you handle the shop</li>
            </ul>
        </div>
    </div>
</section>

@include('components.cta-band')
@endsection
