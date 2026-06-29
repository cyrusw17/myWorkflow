<section class="section section-light" id="faq">
    <div class="container narrow reveal">
        <div class="section-header center">
            <p class="eyebrow">FAQ</p>
            <h2 class="section-title">Straight answers</h2>
        </div>
        <div class="faq-list" data-faq>
            <?php foreach (config('faqs') as $i => $faq): ?>
                <div class="faq-item <?= $i === 0 ? 'is-open' : '' ?>">
                    <button type="button" class="faq-trigger" aria-expanded="<?= $i === 0 ? 'true' : 'false' ?>" aria-controls="faq-panel-<?= $i ?>" id="faq-trigger-<?= $i ?>">
                        <span><?= e($faq['q']) ?></span>
                        <span class="faq-icon" aria-hidden="true"></span>
                    </button>
                    <div class="faq-panel" id="faq-panel-<?= $i ?>" role="region" aria-labelledby="faq-trigger-<?= $i ?>">
                        <p><?= e($faq['a']) ?></p>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
    </div>
</section>
