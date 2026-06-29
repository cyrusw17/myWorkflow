# Phase 5 — Technical Architecture

> **Status:** Complete · **Code root:** `website/app/`

## Stack

| Layer | Technology |
|-------|------------|
| Runtime | PHP 8.2+ |
| Framework | Laravel 11 |
| Database | SQLite (dev) / MySQL (production) |
| ORM | Eloquent |
| Templates | Blade + components |
| CSS | Tailwind CSS 3 |
| Build | Vite 5 |
| JS | Alpine.js 3, GSAP 3, Lenis 1 |
| Icons | Lucide (inline SVG) |
| Mail | Laravel Mail (SMTP) |

## Directory structure

```
app/
├── app/
│   ├── Http/Controllers/PageController.php
│   ├── Http/Controllers/ContactController.php
│   ├── Http/Requests/ContactRequest.php
│   ├── Models/Lead.php
│   └── Models/PortfolioItem.php
├── config/
├── database/migrations/
├── public/          ← web root
├── resources/
│   ├── css/app.css
│   ├── js/app.js
│   └── views/
│       ├── layouts/app.blade.php
│       ├── components/
│       └── pages/
├── routes/web.php
└── storage/
```

## Request flow

```
GET  /              → PageController@home
GET  /services      → PageController@services
GET  /work          → PageController@work
GET  /work/{slug}   → PageController@workShow
GET  /about         → PageController@about
GET  /contact       → PageController@contact
POST /contact       → ContactController@store (throttled)
```

## Contact / leads

1. `ContactRequest` validates input
2. `Lead` model persisted to DB
3. `Mail::to(config('mail.lead_to'))` queued or sent
4. JSON redirect with flash or Inertia-less redirect back with success

Rate limit: `throttle:5,1` on POST contact.

## Security

- CSRF on all forms (`@csrf`)
- `$fillable` / mass assignment guarded
- `ContactRequest` sanitization
- `APP_KEY` required
- Production: HTTPS, secure cookies, `APP_DEBUG=false`
- CSP header (v1.1): script-src self + cdn fallback if used

## Caching

- `php artisan config:cache` in production
- Route cache in production
- Portfolio items cacheable (v2)

## Environment variables

```env
APP_NAME="Groundwork Web"
APP_URL=https://groundwork-web.com
DB_CONNECTION=sqlite
MAIL_MAILER=smtp
MAIL_LEAD_TO=hello@groundwork-web.com
CALENDLY_URL=
```

## Deployment target

- VPS or Laravel Forge / Ploi
- PHP 8.2+, Composer, Node (build assets once)
- MySQL 8+ production
- Queue worker optional for mail

## v2 additions (not built in v1)

- `auth` middleware + admin routes
- Filament or custom admin for leads CRM
- Blog CMS
