<section class="section section-light" id="included">
    <div class="container reveal">
        <div class="section-header center">
            <p class="eyebrow">What's included</p>
            <h2 class="section-title">One plan. Everything handled.</h2>
            <p class="section-lead center">No surprise invoices for hosting, security, or maintenance.</p>
        </div>
        <div class="included-bento">
            <?php foreach (config('included.featured') as $item): ?>
                <div class="included-feature">
                    <div class="included-icon" data-icon="<?= e($item['icon']) ?>"></div>
                    <h3><?= e($item['title']) ?></h3>
                    <p><?= e($item['body']) ?></p>
                </div>
            <?php endforeach; ?>
        </div>
        <div class="included-also">
            <p class="included-also-label">Also included</p>
            <ul>
                <?php foreach (config('included.also') as $item): ?>
                    <li><span class="check-icon" aria-hidden="true"></span><?= e($item) ?></li>
                <?php endforeach; ?>
            </ul>
        </div>
    </div>
</section>
