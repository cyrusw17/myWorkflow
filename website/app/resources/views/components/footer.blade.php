<footer class="site-footer">
    <div class="container">
        <div class="footer-grid">
            <div>
                <div class="logo" style="color:#fff;margin-bottom:0.75rem;">Groundwork <span>Web</span></div>
                <p style="margin:0;max-width:280px;">{{ config('site.tagline') }}</p>
            </div>
            <div>
                <p style="margin:0 0 0.75rem;font-weight:500;color:#fff;">Pages</p>
                <p style="margin:0;display:flex;flex-direction:column;gap:0.5rem;">
                    <a href="{{ route('services') }}">Services</a>
                    <a href="{{ route('work') }}">Work</a>
                    <a href="{{ route('about') }}">About</a>
                    <a href="{{ route('contact') }}">Contact</a>
                </p>
            </div>
            <div>
                <p style="margin:0 0 0.75rem;font-weight:500;color:#fff;">Contact</p>
                <p style="margin:0;">
                    <a href="mailto:{{ config('site.email') }}">{{ config('site.email') }}</a><br>
                    <span style="margin-top:0.5rem;display:block;">{{ config('site.service_area') }}</span>
                </p>
            </div>
        </div>
        <div class="footer-bottom">
            &copy; {{ date('Y') }} Groundwork Web
        </div>
    </div>
</footer>
