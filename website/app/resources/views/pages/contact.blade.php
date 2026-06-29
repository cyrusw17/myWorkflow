@extends('layouts.app')

@section('content')
<section class="page-hero">
    <div class="container reveal">
        <p class="eyebrow">Contact</p>
        <h1 class="display" style="font-size:clamp(2.25rem,4.5vw,3.25rem);">Let's see if we're a fit.</h1>
        <p class="lead">Send a message and we'll follow up within 24 hours to schedule a call. No pressure.</p>
    </div>
</section>

<section class="section section-light" id="form">
    <div class="container contact-grid">
        <div class="form-panel reveal">
            <h2 class="h2">Send a message</h2>
            <p class="text-muted">We'll respond within 24 hours.</p>

            @if (session('success'))
                <div class="alert-success" role="status">{{ session('success') }}</div>
            @endif

            <form method="POST" action="{{ route('contact.store') }}" novalidate>
                @csrf
                <div class="form-group">
                    <label class="form-label" for="name">Name *</label>
                    <input class="form-input" type="text" id="name" name="name" value="{{ old('name') }}" required autocomplete="name">
                    @error('name')<p class="form-error">{{ $message }}</p>@enderror
                </div>
                <div class="form-group">
                    <label class="form-label" for="phone">Phone *</label>
                    <input class="form-input" type="tel" id="phone" name="phone" value="{{ old('phone') }}" required autocomplete="tel">
                    @error('phone')<p class="form-error">{{ $message }}</p>@enderror
                </div>
                <div class="form-group">
                    <label class="form-label" for="business_name">Business name *</label>
                    <input class="form-input" type="text" id="business_name" name="business_name" value="{{ old('business_name') }}" required>
                    @error('business_name')<p class="form-error">{{ $message }}</p>@enderror
                </div>
                <div class="form-group">
                    <label class="form-label" for="location">City, State *</label>
                    <input class="form-input" type="text" id="location" name="location" value="{{ old('location') }}" required placeholder="e.g. Phoenix, AZ">
                    @error('location')<p class="form-error">{{ $message }}</p>@enderror
                </div>
                <div class="form-group">
                    <label class="form-label" for="industry">Industry *</label>
                    <select class="form-select" id="industry" name="industry" required>
                        <option value="">Select…</option>
                        @foreach (config('site.form_industries') as $ind)
                            <option value="{{ $ind }}" @selected(old('industry') === $ind)>{{ $ind }}</option>
                        @endforeach
                    </select>
                    @error('industry')<p class="form-error">{{ $message }}</p>@enderror
                </div>
                <div class="form-group">
                    <label class="form-label" for="message">Message (optional)</label>
                    <textarea class="form-textarea" id="message" name="message" rows="4">{{ old('message') }}</textarea>
                    @error('message')<p class="form-error">{{ $message }}</p>@enderror
                </div>
                <button type="submit" class="btn btn-primary">Send message</button>
            </form>
        </div>

        <div class="reveal">
            <h2 class="h2">Scheduling</h2>
            @if (config('site.calendly_url'))
                <div class="calendly-embed">
                    <iframe src="{{ config('site.calendly_url') }}" title="Schedule a call" style="width:100%;min-height:600px;border:0;border-radius:12px;"></iframe>
                </div>
            @else
                <div class="scheduling-placeholder">
                    <p>Online scheduling coming soon</p>
                    <p>Use the form and we'll follow up to book your discovery call.</p>
                </div>
            @endif
            <div class="card" style="margin-top:1.5rem;padding:1.5rem;">
                <p class="eyebrow" style="margin-bottom:0.5rem;">Direct</p>
                <a href="mailto:{{ config('site.email') }}" style="font-weight:600;font-size:1.05rem;">{{ config('site.email') }}</a>
                <p class="text-muted" style="margin:0.75rem 0 0;font-size:0.9rem;">{{ config('site.service_area') }}</p>
            </div>
        </div>
    </div>
</section>
@endsection
