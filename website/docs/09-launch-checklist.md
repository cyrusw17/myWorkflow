# Phase 9 — Launch Checklist

> **Status:** Ready for use at deploy time

## Domain & hosting

- [ ] `groundwork-web.com` registered
- [ ] DNS A/CNAME pointed to server
- [ ] SSL certificate active (HTTPS)
- [ ] `APP_URL` set to `https://groundwork-web.com`

## Application

- [ ] `composer install --optimize-autoloader --no-dev`
- [ ] `npm run build` (production assets)
- [ ] `php artisan migrate --force`
- [ ] `php artisan db:seed --force`
- [ ] `APP_DEBUG=false`
- [ ] `APP_KEY` generated

## Email & leads

- [ ] SMTP configured in `.env`
- [ ] `MAIL_LEAD_TO=hello@groundwork-web.com`
- [ ] Test form submission → DB row + email received
- [ ] Rate limiting verified on contact POST

## Content

- [ ] All pages load without errors
- [ ] Westside Auto Care case study displays
- [ ] Founder photo placeholder on About
- [ ] Calendly placeholder or live embed if URL set
- [ ] Footer: "Serving businesses across the United States"

## SEO

- [ ] Unique title + meta per page
- [ ] JSON-LD validates (Google Rich Results Test)
- [ ] `/sitemap.xml` accessible
- [ ] `/robots.txt` accessible
- [ ] OG image uploaded

## Performance & a11y

- [ ] Mobile Lighthouse Performance ≥ 90
- [ ] LCP < 2.5s on 4G throttled
- [ ] Keyboard nav works (header, form, FAQ)
- [ ] `prefers-reduced-motion` disables scroll animations
- [ ] Form errors announced / visible

## Cross-browser / device

- [ ] Safari iOS — contact form + CTA
- [ ] Chrome Android — tap targets
- [ ] Desktop Chrome, Safari, Firefox

## Analytics

- [ ] Plausible or GA4 installed
- [ ] CTA click tracking verified

## Post-launch

- [ ] Submit sitemap to Google Search Console
- [ ] Google Business Profile (for Groundwork Web when applicable)
- [ ] Paste URL in outreach messages — ship it
