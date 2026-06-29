<?php $offer = config('offer'); ?>
<section class="hero" id="hero">
    <div class="hero-bg" aria-hidden="true"></div>
    <div class="container hero-grid">
        <div class="reveal">
            <div class="hero-badge">
                <span class="pulse-dot" aria-hidden="true"></span>
                <?= (int) $offer['spots_remaining'] ?>/<?= (int) $offer['spots_total'] ?> founding spots open
            </div>
            <p class="hero-eyebrow">For local service business owners</p>
            <h1 class="hero-title">
                More calls.<br>
                <span class="text-gradient">Zero website stress.</span>
            </h1>
            <p class="hero-lead">
                Join the <strong>Founding Client Program</strong> — a custom-built website with
                <strong>no setup fee</strong>. <?= '$' . $offer['monthly'] ?>/month covers hosting,
                maintenance, and support. We handle the tech. You run the business.
            </p>
            <div class="hero-cta">
                <a href="#apply" class="btn btn-primary btn-lg">Apply for a Founding Spot</a>
                <a href="#included" class="btn btn-ghost btn-lg">See What's Included</a>
            </div>
            <p class="hero-note">2-minute form · No obligation · Honest fit check</p>
        </div>
        <div class="hero-visual reveal">
            <div class="hero-visual-glow" aria-hidden="true"></div>
            <div class="mockup-frame">
                <div class="mockup-chrome">
                    <span></span><span></span><span></span>
                    <p>yourbusiness.com</p>
                </div>
                <img src="/images/preview.svg" alt="Example website layout for a local service business" width="800" height="500" loading="eager" fetchpriority="high">
                <span class="mockup-badge">Sample layout</span>
            </div>
            <div class="hero-price-chip">
                <div>
                    <span class="chip-label">Founding rate</span>
                    <span class="chip-price">$<?= $offer['monthly'] ?><small>/mo</small></span>
                </div>
                <div class="chip-divider"></div>
                <div>
                    <span class="chip-label">Setup fee</span>
                    <span class="chip-was">$<?= number_format($offer['setup_normal']) ?>+</span>
                    <span class="chip-now">$0</span>
                </div>
            </div>
        </div>
    </div>
</section>

<section class="stats-strip" aria-label="Program highlights">
    <div class="container stats-grid">
        <div class="stat"><strong>$<?= number_format($offer['setup_normal']) ?>+</strong><span>typical build value</span></div>
        <div class="stat"><strong>$<?= $offer['monthly'] ?>/mo</strong><span>all-inclusive plan</span></div>
        <div class="stat"><strong><?= e($offer['build_weeks']) ?> wks</strong><span>to launch</span></div>
        <div class="stat"><strong><?= (int) $offer['spots_remaining'] ?>/<?= (int) $offer['spots_total'] ?></strong><span>founding spots open</span></div>
    </div>
</section>
