<section class="section section-light" id="faq">
    <div class="container narrow reveal">
        <div class="section-header center">
            <p class="eyebrow">FAQ</p>
            <h2 class="section-title">Questions owners ask before they text.</h2>
        </div>
        <div class="faq-list" data-faq>
            <?php foreach (config('faqs') as $i => $faq): ?>
                <div class="faq-item<?= $i === 0 ? ' is-open' : '' ?>">
                    <button type="button" class="faq-trigger" aria-expanded="<?= $i === 0 ? 'true' : 'false' ?>">
                        <?= e($faq['q']) ?>
                        <span class="faq-icon" aria-hidden="true"></span>
                    </button>
                    <div class="faq-panel">
                        <p><?= e($faq['a']) ?></p>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
    </div>
</section>
