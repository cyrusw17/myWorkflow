@extends('layouts.app')

@section('content')
<section class="page-hero">
    <div class="container reveal">
        <p class="eyebrow">Work</p>
        <h1 class="display" style="font-size:clamp(2.25rem,4.5vw,3.25rem);">Built for businesses that run on phone calls.</h1>
        <p class="lead">See how we design for local service companies — fast, clear, and built to convert.</p>
    </div>
</section>

<section class="section section-light">
    <div class="container">
        <div class="grid-2">
            @forelse ($projects as $project)
                <div class="card project-card reveal">
                    <div class="thumb">
                        <img src="{{ asset('images/work/westside-hero.svg') }}" alt="{{ $project->title }} preview">
                    </div>
                    <div class="body">
                        @if ($project->is_concept)<span class="badge">Concept project</span>@endif
                        <h2 class="h3" style="margin-top:0.75rem;">{{ $project->title }}</h2>
                        <p class="text-muted">{{ $project->industry }} · {{ $project->tagline }}</p>
                        <a href="{{ route('work.show', $project->slug) }}" class="btn btn-secondary-dark btn-sm" style="margin-top:1rem;">View project →</a>
                    </div>
                </div>
            @empty
                <p>No projects yet.</p>
            @endforelse

            <div class="card project-card-dashed reveal">
                <h3 class="h3">Your project could be next</h3>
                <p class="text-muted">Let's build something that brings in more calls.</p>
                <a href="{{ route('contact') }}#form" class="btn btn-primary" style="margin-top:1rem;">Book a call</a>
            </div>
        </div>
    </div>
</section>

@include('components.cta-band')
@endsection
