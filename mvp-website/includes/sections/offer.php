<?php $offer = config('offer'); ?>
<section class="section section-dark" id="offer">
    <div class="container reveal">
        <div class="offer-split">
            <div>
                <p class="eyebrow eyebrow-light">The offer</p>
                <h2 class="section-title light"><?= e($offer['name']) ?></h2>
                <p class="section-lead light">
                    Normally <s>$<?= number_format($offer['setup_normal']) ?>+</s> to build your site.
                    Founding clients pay <strong>$<?= $offer['monthly'] ?>/month</strong> — that's it.
                </p>
                <ul class="offer-details">
                    <li><i data-lucide="check-circle"></i> No setup fee for founding clients</li>
                    <li><i data-lucide="check-circle"></i> Custom-built website — not a template</li>
                    <li><i data-lucide="check-circle"></i> Hosting, SSL, and security included</li>
                    <li><i data-lucide="check-circle"></i> Maintenance and updates handled for you</li>
                    <li><i data-lucide="check-circle"></i> Professional support when you need it</li>
                </ul>
            </div>
            <div class="pricing-panel">
                <div class="spots-badge">
                    <span class="spots-num"><?= (int) $offer['spots_remaining'] ?></span>
                    <span class="spots-label">of <?= (int) $offer['spots_total'] ?> founding spots open</span>
                </div>
                <div class="pricing-compare">
                    <div class="pricing-col muted">
                        <p>After program closes</p>
                        <p class="big">$<?= number_format($offer['setup_normal']) ?></p>
                        <p>setup + $<?= $offer['monthly'] ?>/mo</p>
                    </div>
                    <div class="pricing-col active">
                        <p>Founding clients</p>
                        <p class="big">$0</p>
                        <p>setup + $<?= $offer['monthly'] ?>/mo</p>
                    </div>
                </div>
                <p class="pricing-note"><?= $offer['term_months'] ?>-month minimum partnership · testimonial required</p>
                <a href="#apply" class="btn btn-primary btn-block btn-lg">Apply for a Founding Spot</a>
            </div>
        </div>
    </div>
</section>
