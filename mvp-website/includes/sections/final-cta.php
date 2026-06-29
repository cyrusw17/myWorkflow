<?php
$offer = config('offer');
$success = $formSuccess ?? false;
$errors = $formErrors ?? [];
$old = $formOld ?? [];
$contactMethods = config('form_contact_methods');
$contactTimes = config('form_contact_times');
$emailRequired = ($old['contact_method'] ?? '') === 'email';
?>
<section class="section section-cta" id="apply">
    <div class="cta-bg" aria-hidden="true"></div>
    <div class="container cta-grid reveal">
        <div class="cta-copy">
            <p class="eyebrow eyebrow-light">Apply now</p>
            <h2 class="section-title light">
                <?= (int) $offer['spots_remaining'] ?>/<?= (int) $offer['spots_total'] ?> founding spots open
            </h2>
            <p class="section-lead light">
                When they're filled, pricing returns to
                <strong>$<?= number_format($offer['setup_normal']) ?> setup + $<?= $offer['monthly'] ?>/month</strong>.
                Submit the form — we'll reach out the way you prefer and tell you honestly if we're the right fit.
            </p>
            <ul class="cta-checklist">
                <li><span class="check-icon check-icon--light" aria-hidden="true"></span> 2-minute form</li>
                <li><span class="check-icon check-icon--light" aria-hidden="true"></span> You pick how we contact you</li>
                <li><span class="check-icon check-icon--light" aria-hidden="true"></span> No pressure — walk away if it's not right</li>
            </ul>
        </div>

        <div class="form-panel" id="form">
            <h3>Apply for a Founding Client Spot</h3>
            <p class="form-sub">Tell us about your business and when we should reach out.</p>

            <?php if ($success): ?>
                <div class="alert success" role="status">
                    <strong>Application received.</strong>
                    <p>We'll contact you within 24 hours using your preferred method.</p>
                </div>
            <?php else: ?>

            <?php if (! empty($errors['_form'])): ?>
                <div class="alert error" role="alert"><?= e($errors['_form']) ?></div>
            <?php endif; ?>

            <form method="post" action="#form" novalidate id="apply-form">
                <input type="hidden" name="_token" value="<?= e($csrfToken ?? '') ?>">
                <input type="text" name="website" value="" tabindex="-1" autocomplete="off" class="hp-field" aria-hidden="true">
                <div class="field-row">
                    <div class="field">
                        <label for="name">Your name *</label>
                        <input type="text" id="name" name="name" value="<?= e($old['name'] ?? '') ?>" required autocomplete="name">
                        <?php if (! empty($errors['name'])): ?><span class="field-error"><?= e($errors['name']) ?></span><?php endif; ?>
                    </div>
                    <div class="field">
                        <label for="phone">Phone *</label>
                        <input type="tel" id="phone" name="phone" value="<?= e($old['phone'] ?? '') ?>" required autocomplete="tel" inputmode="tel">
                        <?php if (! empty($errors['phone'])): ?><span class="field-error"><?= e($errors['phone']) ?></span><?php endif; ?>
                    </div>
                </div>
                <div class="field">
                    <label for="email">Email<?= $emailRequired ? ' *' : '' ?></label>
                    <input type="email" id="email" name="email" value="<?= e($old['email'] ?? '') ?>" autocomplete="email" inputmode="email"<?= $emailRequired ? ' required' : '' ?>>
                    <?php if (! empty($errors['email'])): ?><span class="field-error"><?= e($errors['email']) ?></span><?php endif; ?>
                </div>
                <div class="field">
                    <label for="business_name">Business name *</label>
                    <input type="text" id="business_name" name="business_name" value="<?= e($old['business_name'] ?? '') ?>" required>
                    <?php if (! empty($errors['business_name'])): ?><span class="field-error"><?= e($errors['business_name']) ?></span><?php endif; ?>
                </div>
                <div class="field-row">
                    <div class="field">
                        <label for="location">City, State *</label>
                        <input type="text" id="location" name="location" value="<?= e($old['location'] ?? '') ?>" required placeholder="Phoenix, AZ">
                        <?php if (! empty($errors['location'])): ?><span class="field-error"><?= e($errors['location']) ?></span><?php endif; ?>
                    </div>
                    <div class="field">
                        <label for="industry">Industry *</label>
                        <select id="industry" name="industry" required>
                            <option value="">Select…</option>
                            <?php foreach (config('form_industries') as $ind): ?>
                                <option value="<?= e($ind) ?>" <?= ($old['industry'] ?? '') === $ind ? 'selected' : '' ?>><?= e($ind) ?></option>
                            <?php endforeach; ?>
                        </select>
                        <?php if (! empty($errors['industry'])): ?><span class="field-error"><?= e($errors['industry']) ?></span><?php endif; ?>
                    </div>
                </div>

                <fieldset class="field fieldset">
                    <legend>How should we contact you? *</legend>
                    <div class="radio-group">
                        <?php foreach ($contactMethods as $value => $label): ?>
                            <label class="radio-option">
                                <input type="radio" name="contact_method" value="<?= e($value) ?>" <?= ($old['contact_method'] ?? '') === $value ? 'checked' : '' ?> required>
                                <span><?= e($label) ?></span>
                            </label>
                        <?php endforeach; ?>
                    </div>
                    <?php if (! empty($errors['contact_method'])): ?><span class="field-error"><?= e($errors['contact_method']) ?></span><?php endif; ?>
                </fieldset>

                <div class="field">
                    <label for="contact_time">Best time to contact you *</label>
                    <select id="contact_time" name="contact_time" required>
                        <option value="">Select…</option>
                        <?php foreach ($contactTimes as $value => $label): ?>
                            <option value="<?= e($value) ?>" <?= ($old['contact_time'] ?? '') === $value ? 'selected' : '' ?>><?= e($label) ?></option>
                        <?php endforeach; ?>
                    </select>
                    <?php if (! empty($errors['contact_time'])): ?><span class="field-error"><?= e($errors['contact_time']) ?></span><?php endif; ?>
                </div>

                <button type="submit" class="btn btn-primary btn-block btn-lg">Submit Application</button>
                <p class="form-trust">No spam. No pressure. One reply within 24 hours.</p>
            </form>
            <?php endif; ?>
        </div>
    </div>
</section>
