@extends('layouts.app')

@section('content')
<div class="container error-page section">
    <p class="eyebrow">404</p>
    <h1 class="h1">This page doesn't exist.</h1>
    <p class="text-muted">The link may be broken or the page was moved.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;justify-content:center;">
        <a href="{{ route('home') }}" class="btn btn-secondary-dark">Go to homepage</a>
        <a href="{{ route('contact') }}#form" class="btn btn-primary">Book a call</a>
    </div>
</div>
@endsection
