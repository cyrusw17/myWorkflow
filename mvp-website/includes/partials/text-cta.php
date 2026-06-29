<?php
/** @var string $size lg|sm */
/** @var bool $showAlt */
$size = $size ?? 'lg';
$showAlt = $showAlt ?? false;
$smsHref = sms_href();
?>
<div class="text-cta-group text-cta-group--<?= e($size) ?>">
    <a href="<?= e($smsHref) ?>" class="btn btn-primary btn-<?= e($size) ?> btn-text-cta">
        <?php if (has_phone()): ?><span class="btn-text-cta__icon" aria-hidden="true">📲</span><?php endif; ?>
        <?= e(text_cta_label()) ?>
    </a>
    <?php if ($showAlt): ?>
        <a href="#qualify" class="btn btn-secondary btn-<?= e($size) ?>">See If Your Business Qualifies</a>
    <?php endif; ?>
</div>
