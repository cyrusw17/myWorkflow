<footer class="site-footer">
    <div class="container footer-inner">
        <div>
            <p class="logo footer-logo"><?= e(config('name')) ?></p>
            <p class="footer-tagline"><?= e(config('tagline')) ?></p>
        </div>
        <div class="footer-meta">
            <a href="mailto:<?= e(config('email')) ?>"><?= e(config('email')) ?></a>
            <p>Serving local businesses across the United States</p>
        </div>
    </div>
    <div class="container footer-bottom">
        <p>&copy; <?= date('Y') ?> <?= e(config('name')) ?>. All rights reserved.</p>
    </div>
</footer>

<script src="https://cdn.jsdelivr.net/npm/lenis@1.1.18/dist/lenis.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js" defer></script>
<script src="/js/app.js?v=2" defer></script>
</body>
</html>
