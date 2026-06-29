<footer class="site-footer">
    <div class="container footer-inner">
        <div>
            <p class="logo footer-logo"><?= e(config('name')) ?></p>
            <p class="footer-tagline"><?= e(config('tagline')) ?></p>
        </div>
        <div class="footer-meta">
            <?php if (has_phone()): ?>
                <a href="<?= e(sms_href()) ?>">Text <?= e(config('sms_keyword')) ?> to <?= e(config('phone_display')) ?></a>
            <?php else: ?>
                <a href="#qualify">See if your business qualifies</a>
            <?php endif; ?>
            <p>Serving local service businesses across the United States</p>
        </div>
    </div>
    <div class="container footer-bottom">
        <p>&copy; <?= date('Y') ?> <?= e(config('name')) ?>. All rights reserved.</p>
    </div>
</footer>

<script src="/js/app.js?v=5" defer></script>
</body>
</html>
