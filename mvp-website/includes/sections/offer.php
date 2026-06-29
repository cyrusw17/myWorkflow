<?php $offer = config('offer'); ?>
<section class="section section-offer" id="offer">
    <div class="container">
        <div class="offer-funnel reveal">
            <p class="offer-funnel__label">Normal pricing</p>
            <p class="offer-funnel__was">$<?= number_format($offer['setup_normal']) ?>+ setup</p>
            <p class="offer-funnel__plus">+ $<?= $offer['monthly'] ?>/month</p>

            <div class="offer-funnel__arrow" aria-hidden="true">↓</div>

            <p class="offer-funnel__today">Today — Launch Partner pricing</p>
            <p class="offer-funnel__hero-price">$0 <span>setup</span></p>
            <p class="offer-funnel__monthly">$<?= $offer['monthly'] ?>/month</p>

            <div class="offer-funnel__arrow" aria-hidden="true">↓</div>

            <p class="offer-funnel__urgency">
                Only <strong><?= (int) $offer['spots_remaining'] ?></strong> Launch Partner spots remaining
            </p>
        </div>

        <div class="offer-details reveal">
            <div class="offer-col">
                <h3>Includes</h3>
                <ul>
                    <li>Custom 5-page website</li>
                    <li>Mobile-first, lead-generation focused</li>
                    <li>Hosting, maintenance & updates</li>
                    <li>Unlimited technical support</li>
                    <li>Launch in ~<?= e($offer['build_weeks']) ?> weeks</li>
                </ul>
            </div>
            <div class="offer-col">
                <h3>Requirements</h3>
                <ul>
                    <li><?= (int) $offer['term_months'] ?>-month partnership</li>
                    <li>Testimonial at launch</li>
                    <li>Case study permission</li>
                </ul>
            </div>
        </div>

        <p class="offer-after reveal">
            After the final <?= (int) $offer['spots_remaining'] ?> spots are filled, pricing becomes
            <strong>$<?= number_format($offer['setup_normal']) ?> setup + $<?= $offer['monthly'] ?>/month</strong> immediately.
        </p>

        <div class="section-cta-center reveal">
            <?php $size = 'lg'; $showAlt = true; require dirname(__DIR__) . '/partials/text-cta.php'; ?>
        </div>
    </div>
</section>
