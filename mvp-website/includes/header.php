<header class="site-header" id="top">
    <div class="container header-inner">
        <a href="#top" class="logo"><?= e(config('name')) ?></a>
        <div class="header-right">
            <span class="header-spots" aria-label="<?= (int) config('offer.spots_remaining') ?> of <?= (int) config('offer.spots_total') ?> founding spots open">
                <span class="pulse-dot" aria-hidden="true"></span>
                <?= (int) config('offer.spots_remaining') ?>/<?= (int) config('offer.spots_total') ?> spots open
            </span>
            <a href="#apply" class="btn btn-primary btn-sm header-cta">Apply Now</a>
        </div>
    </div>
</header>

<div class="mobile-cta" aria-hidden="true">
    <a href="#apply" class="btn btn-primary btn-block">Apply for a Spot</a>
</div>
