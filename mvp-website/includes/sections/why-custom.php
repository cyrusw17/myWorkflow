<section class="section section-dark" id="custom">
    <div class="container reveal">
        <div class="section-header center">
            <p class="eyebrow eyebrow-light">Why custom</p>
            <h2 class="section-title light">Your business deserves better than a template</h2>
            <p class="section-lead light center">Page builders work for hobby projects. Local businesses that run on phone calls need something faster, sharper, and built for them.</p>
        </div>
        <div class="benefits-grid">
            <?php foreach (config('custom_benefits') as $benefit): ?>
                <div class="benefit-card">
                    <h3><?= e($benefit['title']) ?></h3>
                    <p><?= e($benefit['body']) ?></p>
                </div>
            <?php endforeach; ?>
        </div>
    </div>
</section>
