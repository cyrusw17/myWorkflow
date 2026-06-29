<section class="section section-light" id="proof">
    <div class="container reveal">
        <div class="proof-layout">
            <div class="founder-card">
                <div class="founder-avatar" aria-hidden="true"><?= strtoupper(substr(config('founder'), 0, 1)) ?></div>
                <div>
                    <p class="founder-label">Who you're talking to</p>
                    <h3 class="founder-name"><?= e(config('founder')) ?>, founder</h3>
                    <p class="founder-bio">
                        I build custom websites for local shops and trades, then handle hosting and maintenance
                        every month. No templates. No disappearing acts. One partner for your web presence.
                    </p>
                </div>
            </div>
            <div class="proof-copy">
                <p class="eyebrow">Why we're doing this</p>
                <h2 class="section-title">Three spots. On purpose.</h2>
                <p class="section-lead">
                    We don't have a wall of client logos yet — and we won't fake one. This founding program
                    is how we partner with three local businesses and earn the portfolio to prove it.
                </p>
                <ul class="proof-list">
                    <li><span class="check-icon" aria-hidden="true"></span> Exclusive — not a public discount</li>
                    <li><span class="check-icon" aria-hidden="true"></span> Fair trade: waived setup for testimonial + case study</li>
                    <li><span class="check-icon" aria-hidden="true"></span> Built for shops that run on phone calls</li>
                </ul>
                <p class="industry-line">
                    <strong>We work with:</strong> <?= e(implode(' · ', config('industries'))) ?>
                </p>
            </div>
        </div>
    </div>
</section>
