@extends('layouts.app')

@section('content')
<section class="page-hero">
    <div class="container reveal">
        @if ($project->is_concept)<span class="badge">Concept project</span>@endif
        <h1 class="display" style="font-size:clamp(2.25rem,4.5vw,3.25rem);margin-top:0.75rem;">{{ $project->title }}</h1>
        <p class="lead">{{ $project->industry }} · {{ $project->tagline }}</p>
    </div>
</section>

<section class="section-tight section-dark">
    <div class="container reveal">
        <div class="mockup-frame" style="max-width:900px;margin-inline:auto;transform:none;">
            <div class="mockup-chrome">
                <i></i><i></i><i></i>
                <span>{{ $project->slug }}.com</span>
            </div>
            <img src="{{ asset('images/work/westside-hero.svg') }}" alt="{{ $project->title }} website screenshot" class="case-study-hero-img" style="border:none;border-radius:0;box-shadow:none;">
        </div>
    </div>
</section>

<section class="section section-light">
    <div class="container">
        <div class="grid-3 reveal" style="margin-bottom:3rem;">
            <div class="card"><p class="eyebrow">Industry</p><p style="margin:0;font-weight:600;">{{ $project->industry }}</p></div>
            <div class="card"><p class="eyebrow">Focus</p><p style="margin:0;font-weight:600;">Lead generation</p></div>
            <div class="card"><p class="eyebrow">Built for</p><p style="margin:0;font-weight:600;">Mobile + local SEO</p></div>
        </div>

        <div class="reveal card" style="max-width:720px;padding:2.5rem;">
            <h2 class="h2">The challenge</h2>
            <p class="text-muted">{{ $project->challenge }}</p>

            <h2 class="h2">Our approach</h2>
            <p class="text-muted">{{ $project->approach }}</p>

            <h2 class="h2">Project goals</h2>
            <ul class="text-muted">
                @foreach (explode("\n", $project->goals) as $goal)
                    @if (trim($goal))<li>{{ trim($goal) }}</li>@endif
                @endforeach
            </ul>
            <p class="micro">* Concept project — goals reflect design intent, not live client metrics.</p>
        </div>
    </div>
</section>

@include('components.cta-band', ['title' => 'Want results like this for your business?'])
@endsection
