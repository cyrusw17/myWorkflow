<?php $why = config('why_exists'); ?>
<section class="section section-light" id="why">
    <div class="container narrow reveal">
        <p class="eyebrow">Why this exists</p>
        <h2 class="section-title">A partnership, not a discount.</h2>
        <p class="section-lead"><?= e($why['lead']) ?></p>
        <p class="section-lead">In return, we ask for:</p>
        <ul class="check-list">
            <?php foreach ($why['exchange'] as $item): ?>
                <li><span class="check-icon" aria-hidden="true"></span><?= e($item) ?></li>
            <?php endforeach; ?>
        </ul>
        <p class="section-note">Transparency builds trust. We're not trying to look cheap — we're looking for the right three partners.</p>
    </div>
</section>
