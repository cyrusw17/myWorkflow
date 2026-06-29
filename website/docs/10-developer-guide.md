# Developer Guide — Groundwork Web

> **App path:** `website/app/`

## Requirements

- PHP 8.2+
- Composer 2
- Node.js 18+ & npm
- SQLite (dev) or MySQL 8+ (production)

Install PHP: [Laravel Herd](https://herd.laravel.com/) (macOS, recommended) or Homebrew `brew install php composer node`.

## First-time setup

```bash
cd website/app
cp .env.example .env
composer install
php artisan key:generate
touch database/database.sqlite
php artisan migrate --seed
npm install
npm run build
php artisan serve
```

Visit http://127.0.0.1:8000

## Development

```bash
npm run dev          # Vite HMR (run alongside artisan serve)
php artisan serve
```

If Vite is not running, the layout falls back to `public/css/site.css` + CDN scripts.

## Environment

| Variable | Purpose |
|----------|---------|
| `MAIL_LEAD_TO` | Lead notification recipient |
| `CALENDLY_URL` | If set, shows Calendly on Contact |
| `DB_*` | Database connection |

## Key commands

```bash
php artisan migrate:fresh --seed   # Reset DB + Westside seed
php artisan route:list
php artisan test                   # When tests added
```

## Adding a portfolio project

1. Insert row in `portfolio_items` or extend seeder
2. Add images to `public/images/work/`
3. Case study uses `work.show` route

## Deployment

See `08-implementation-roadmap.md` and `09-launch-checklist.md`.

## Structure

- `PageController` — static pages
- `ContactController@store` — lead capture
- `resources/views/components/` — Blade UI components
- `resources/views/pages/` — page templates
