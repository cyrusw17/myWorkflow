<?php $offer = config('offer'); $hero = config('hero'); ?>
<section class="hero" id="hero">
    <div class="container hero-inner reveal">
        <p class="hero-eyebrow">For local service business owners</p>
        <h1 class="hero-title"><?= e($hero['headline']) ?></h1>
        <p class="hero-lead"><?= e($hero['subhead']) ?></p>

        <div class="hero-program">
            <span class="pulse-dot" aria-hidden="true"></span>
            <div>
                <strong><?= e($offer['name']) ?></strong>
                <span>Only <?= (int) $offer['spots_remaining'] ?> of <?= (int) $offer['spots_total'] ?> spots left</span>
            </div>
        </div>

        <?php $size = 'lg'; $showAlt = true; require dirname(__DIR__) . '/partials/text-cta.php'; ?>

        <p class="hero-note">No meetings required to start · Reply on your schedule · 2–4 week launch</p>
    </div>
</section>
