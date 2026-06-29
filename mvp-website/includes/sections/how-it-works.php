<section class="section section-light" id="process">
    <div class="container reveal">
        <div class="section-header center">
            <p class="eyebrow">How it works</p>
            <h2 class="section-title">Four steps. No surprises.</h2>
        </div>
        <div class="timeline">
            <?php foreach (config('how_it_works') as $i => $step): ?>
                <article class="timeline-step">
                    <div class="timeline-marker"><?= e($step['step']) ?></div>
                    <div class="timeline-body">
                        <h3><?= e($step['title']) ?></h3>
                        <p><?= e($step['body']) ?></p>
                    </div>
                    <?php if ($i < count(config('how_it_works')) - 1): ?>
                        <div class="timeline-line" aria-hidden="true"></div>
                    <?php endif; ?>
                </article>
            <?php endforeach; ?>
        </div>
    </div>
</section>
