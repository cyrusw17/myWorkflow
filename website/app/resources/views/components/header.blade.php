<header class="site-header" x-data="{ open: false }">
    <div class="header-inner">
        <a href="{{ route('home') }}" class="logo">Groundwork <span>Web</span></a>

        <nav class="nav-desktop" aria-label="Main">
            <a href="{{ route('services') }}">Services</a>
            <a href="{{ route('work') }}">Work</a>
            <a href="{{ route('about') }}">About</a>
            <a href="{{ route('contact') }}">Contact</a>
        </nav>

        <div class="header-actions">
            <a href="{{ route('contact') }}#form" class="btn btn-primary btn-sm hide-mobile">Book a Call</a>
            <button type="button" class="menu-toggle" aria-label="Open menu" @click="open = !open" :aria-expanded="open">
                <span></span><span></span><span></span>
            </button>
        </div>
    </div>

    <nav class="mobile-nav" :class="{ 'is-open': open }" aria-label="Mobile" @click.outside="open = false">
        <a href="{{ route('services') }}" @click="open = false">Services</a>
        <a href="{{ route('work') }}" @click="open = false">Work</a>
        <a href="{{ route('about') }}" @click="open = false">About</a>
        <a href="{{ route('contact') }}" @click="open = false">Contact</a>
        <a href="{{ route('contact') }}#form" class="btn btn-primary btn-block" @click="open = false">Book a Call</a>
    </nav>
</header>
