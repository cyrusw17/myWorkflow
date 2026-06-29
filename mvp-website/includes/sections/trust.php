<section class="section section-light" id="trust">
    <div class="container reveal">
        <div class="section-header center">
            <p class="eyebrow">Why owners trust us</p>
            <h2 class="section-title">No gimmicks. No hidden fees. Just honest work.</h2>
            <p class="section-lead center">We keep everything transparent so you know exactly what you're getting before you ever send a text.</p>
        </div>
        <ul class="trust-grid">
            <?php foreach (config('trust') as $item): ?>
                <li class="trust-card">
                    <span class="trust-card__check" aria-hidden="true"></span>
                    <div>
                        <h3><?= e($item['title']) ?></h3>
                        <p><?= e($item['body']) ?></p>
                    </div>
                </li>
            <?php endforeach; ?>
        </ul>
    </div>
</section>
