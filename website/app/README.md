# Groundwork Web — Laravel Site

Marketing site for **Groundwork Web** (groundwork-web.com).

## Quick start

**Requires:** PHP 8.2+, Composer, Node 18+ (recommended: [Laravel Herd](https://herd.laravel.com/) on macOS)

```bash
cd website/app
cp .env.example .env
composer install
php artisan key:generate
touch database/database.sqlite
php artisan migrate --seed
npm install && npm run build   # optional — falls back to public/css/site.css
php artisan serve
```

Open http://127.0.0.1:8000

## Without Node (fallback)

If you skip `npm run build`, the site uses `public/css/site.css` and Alpine CDN automatically.

## Docs

Planning: `../docs/` (Phases 1–10)  
Developer guide: `../docs/10-developer-guide.md`  
Launch checklist: `../docs/09-launch-checklist.md`

## Pages

- `/` Home
- `/services` Pricing & offer
- `/work` Portfolio
- `/work/westside-auto-care` Case study
- `/about` Founder story
- `/contact` Lead form
- `/sitemap.xml` · `/robots.txt`

## Environment

| Variable | Purpose |
|----------|---------|
| `CALENDLY_URL` | Leave empty for placeholder; set when ready |
| `MAIL_LEAD_TO` | Lead notification email |
| `MAIL_MAILER=log` | Dev default — emails written to log |

## Deploy

See `../docs/08-implementation-roadmap.md` and `../docs/09-launch-checklist.md`.
