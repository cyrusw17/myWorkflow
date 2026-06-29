<header class="site-header" id="top">
    <div class="container header-inner">
        <a href="#top" class="logo"><?= e(config('name')) ?></a>
        <div class="header-right">
            <span class="header-spots" aria-label="<?= (int) config('offer.spots_remaining') ?> of <?= (int) config('offer.spots_total') ?> launch partner spots">
                <span class="pulse-dot" aria-hidden="true"></span>
                <?= (int) config('offer.spots_remaining') ?>/<?= (int) config('offer.spots_total') ?> left
            </span>
            <a href="<?= e(sms_href()) ?>" class="btn btn-primary btn-sm header-cta">
                <?= has_phone() ? 'Text ' . e(config('sms_keyword')) : 'Apply Now' ?>
            </a>
        </div>
    </div>
</header>

<?php $offer = config('offer'); ?>
<div class="sticky-bar" id="sticky-bar">
    <div class="sticky-bar__info">
        <p class="sticky-bar__title">
            <span class="sticky-bar__emoji" aria-hidden="true">🚀</span>
            <?= e($offer['name']) ?>
        </p>
        <p class="sticky-bar__meta">
            <span class="sticky-bar__spots">Only <?= (int) $offer['spots_remaining'] ?> of <?= (int) $offer['spots_total'] ?> spots left</span>
            <span class="sticky-bar__dot" aria-hidden="true">•</span>
            $0 setup · $<?= $offer['monthly'] ?>/mo
        </p>
    </div>
    <a href="<?= e(sms_href()) ?>" class="btn btn-primary btn-text-cta sticky-bar__cta">
        <?php if (has_phone()): ?>
            <span class="btn-text-cta__icon" aria-hidden="true">📲</span>Text "<?= e(config('sms_keyword')) ?>"
        <?php else: ?>
            Apply Now
        <?php endif; ?>
    </a>
</div>
