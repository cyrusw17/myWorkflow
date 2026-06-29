<section class="section section-muted" id="included">
    <div class="container reveal">
        <div class="section-header center">
            <p class="eyebrow">What's included</p>
            <h2 class="section-title">Everything to look professional and win more customers.</h2>
            <p class="section-lead center">One monthly plan. No surprise bills. No tech headaches.</p>
        </div>
        <ul class="included-grid">
            <?php foreach (config('included') as $item): ?>
                <li><span class="check-icon" aria-hidden="true"></span><?= e($item) ?></li>
            <?php endforeach; ?>
        </ul>
    </div>
</section>
