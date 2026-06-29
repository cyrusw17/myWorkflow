# Phase 8 — Implementation Roadmap

> **Status:** Complete

## v1 launch scope ✅

- Pages: Home, Services, Work, Work detail, About, Contact, 404
- Contact form → `leads` table + email notification
- Calendly placeholder (env-driven)
- Portfolio seed: Westside Auto Care
- Responsive, accessible, SEO meta + schema
- GSAP scroll reveals + Lenis (reduced-motion safe)

## v2 platform (after first client)

- Admin auth + lead CRM
- Portfolio CMS
- Blog
- Client portal
- Testimonials from real clients

## Build order (completed in Phase 9)

1. Laravel scaffold + migrations
2. Layout + global components
3. Home page (all sections)
4. Services, Work, About, Contact
5. Case study detail
6. Form + mail
7. SEO, sitemap, 404
8. JS polish + performance pass

## Risks

| Risk | Mitigation |
|------|------------|
| Scope creep (3D, blog) | v1 scope locked |
| No PHP locally | README setup instructions |
| Animation bloat | CSS-first, GSAP only on scroll |
| Fake social proof | Concept badges |

## Testing before launch

See `09-launch-checklist.md`

## Deployment steps

1. Server: PHP 8.2, MySQL, Composer, Node (build)
2. `composer install --no-dev`
3. `npm ci && npm run build`
4. `.env` production values
5. `php artisan migrate --force`
6. `php artisan db:seed --force`
7. Point DNS to server, SSL via Let's Encrypt
8. Configure SMTP for lead emails
