<?php
$offer = config('offer');
$success = $formSuccess ?? false;
$errors = $formErrors ?? [];
$old = $formOld ?? [];
?>
<section class="section section-cta" id="text">
    <div class="container narrow reveal">
        <p class="eyebrow eyebrow-light">Ready?</p>
        <h2 class="section-title light center">Only <?= (int) $offer['spots_remaining'] ?> Launch Partner spots left.</h2>
        <p class="section-lead light center">
            Text us to start — on your time, no pressure. If we're not the right fit, we'll tell you honestly.
        </p>

        <div class="section-cta-center">
            <?php $size = 'lg'; $showAlt = true; require dirname(__DIR__) . '/partials/text-cta.php'; ?>
        </div>
    </div>
</section>

<section class="section section-muted" id="qualify">
    <div class="container narrow">
        <div class="qualify-panel reveal" id="form">
            <h3>See if your business qualifies</h3>
            <p class="qualify-sub">
                <?php if (has_phone()): ?>
                    Prefer not to text yet? Leave your info — we'll reach out within 24 hours. For the fastest response, text <strong><?= e(config('sms_keyword')) ?></strong> to <?= e(config('phone_display')) ?>.
                <?php else: ?>
                    Leave your info and we'll reach out within 24 hours to see if you're a fit for one of the remaining spots.
                <?php endif; ?>
            </p>

            <?php if ($success): ?>
                <div class="alert success" role="status">
                    <strong>Received.</strong>
                    <p>We'll be in touch within 24 hours<?php if (has_phone()): ?> — for the fastest reply, text <?= e(config('sms_keyword')) ?> to <?= e(config('phone_display')) ?><?php endif; ?>.</p>
                </div>
            <?php else: ?>

            <?php if (! empty($errors['_form'])): ?>
                <div class="alert error" role="alert"><?= e($errors['_form']) ?></div>
            <?php endif; ?>

            <form method="post" action="#qualify" novalidate>
                <input type="hidden" name="_token" value="<?= e($csrfToken ?? '') ?>">
                <input type="text" name="website" value="" tabindex="-1" autocomplete="off" class="hp-field" aria-hidden="true">
                <div class="field">
                    <label for="name">Your name *</label>
                    <input type="text" id="name" name="name" value="<?= e($old['name'] ?? '') ?>" required autocomplete="name">
                    <?php if (! empty($errors['name'])): ?><span class="field-error"><?= e($errors['name']) ?></span><?php endif; ?>
                </div>
                <div class="field">
                    <label for="business_name">Business name *</label>
                    <input type="text" id="business_name" name="business_name" value="<?= e($old['business_name'] ?? '') ?>" required>
                    <?php if (! empty($errors['business_name'])): ?><span class="field-error"><?= e($errors['business_name']) ?></span><?php endif; ?>
                </div>
                <div class="field-row">
                    <div class="field">
                        <label for="phone">Mobile number *</label>
                        <input type="tel" id="phone" name="phone" value="<?= e($old['phone'] ?? '') ?>" required autocomplete="tel" inputmode="tel">
                        <?php if (! empty($errors['phone'])): ?><span class="field-error"><?= e($errors['phone']) ?></span><?php endif; ?>
                    </div>
                    <div class="field">
                        <label for="industry">Industry *</label>
                        <select id="industry" name="industry" required>
                            <option value="">Select…</option>
                            <?php foreach (config('qualify_industries') as $ind): ?>
                                <option value="<?= e($ind) ?>" <?= ($old['industry'] ?? '') === $ind ? 'selected' : '' ?>><?= e($ind) ?></option>
                            <?php endforeach; ?>
                        </select>
                        <?php if (! empty($errors['industry'])): ?><span class="field-error"><?= e($errors['industry']) ?></span><?php endif; ?>
                    </div>
                </div>
                <button type="submit" class="btn btn-secondary btn-block btn-lg">Check My Eligibility</button>
                <p class="form-trust">No spam. No pressure. One reply within 24 hours.</p>
            </form>
            <?php endif; ?>
        </div>
    </div>
</section>
