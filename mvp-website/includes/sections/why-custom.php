<section class="section section-dark" id="why-custom">
    <div class="container reveal">
        <div class="section-header center">
            <p class="eyebrow eyebrow-light">Custom vs. templates</p>
            <h2 class="section-title light">Your business deserves better than a generic template.</h2>
            <p class="section-lead light center">Cheap website builders work for hobby projects. Growing local businesses need something built around how they actually get customers.</p>
        </div>
        <div class="benefits-grid">
            <?php foreach (config('custom_benefits') as $benefit): ?>
                <article class="benefit-card">
                    <h3><?= e($benefit['title']) ?></h3>
                    <p><?= e($benefit['body']) ?></p>
                </article>
            <?php endforeach; ?>
        </div>
    </div>
</section>
