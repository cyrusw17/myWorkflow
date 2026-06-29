<section class="section section-light" id="how-it-works">
    <div class="container reveal">
        <div class="section-header center">
            <p class="eyebrow">How it works</p>
            <h2 class="section-title">Simple from first text to launch.</h2>
        </div>
        <ol class="steps-list">
            <?php foreach (config('how_it_works') as $step): ?>
                <li class="steps-list__item">
                    <span class="steps-list__num"><?= e($step['step']) ?></span>
                    <div>
                        <h3><?= e($step['title']) ?></h3>
                        <p><?= e($step['body']) ?></p>
                    </div>
                </li>
            <?php endforeach; ?>
        </ol>
        <div class="section-cta-center">
            <?php $size = 'lg'; $showAlt = false; require dirname(__DIR__) . '/partials/text-cta.php'; ?>
        </div>
    </div>
</section>
