# Phase 7 — SEO & Conversion

> **Status:** Complete

## Per-page SEO

| Page | Title | Meta description (≤160) |
|------|-------|---------------------------|
| Home | Groundwork Web \| Websites for Local Service Businesses | Custom websites for shops and trades — built for more calls, hosted and maintained for you. Book a free discovery call. |
| Services | Services & Pricing \| Groundwork Web | Website build, hosting, and maintenance for local businesses. Starting at $2,500 + $199/mo. Get a custom quote. |
| Work | Our Work \| Groundwork Web | Websites built for local service businesses — designed to drive phone calls and trust. |
| Case study | Westside Auto Care \| Groundwork Web | Concept project: auto repair website built for mobile, speed, and local lead generation. |
| About | About \| Groundwork Web | Groundwork Web helps local shop and trade owners get more leads without website headaches. |
| Contact | Contact \| Groundwork Web | Get in touch or request a free discovery call. We serve local businesses across the United States. |

## Keywords

| Page | Primary | Secondary |
|------|---------|-----------|
| Home | local service business website design | custom website for small business |
| Services | website hosting maintenance small business | web design pricing |
| Work | auto shop website example | portfolio local business |
| Contact | web design consultation | contact web designer |

## Schema (JSON-LD)

**Home:** `Organization` + `WebSite` + `FAQPage`  
**Contact:** `ContactPage`  
**Organization fields:** name, url, email, `areaServed: United States`

## Open Graph

- Image: 1200×630 `public/images/og-default.jpg` (create at launch)
- `og:type` website
- Per-page `og:title`, `og:description`

## Sitemap & robots

`GET /sitemap.xml` — static or generated route listing all public URLs.  
`robots.txt`: Allow all, Sitemap URL.

## CRO tracking events

| Event | Trigger |
|-------|---------|
| `cta_click` | Any primary CTA |
| `form_submit` | Contact form success |
| `form_error` | Validation fail |

Analytics: Plausible or GA4 — defer script until cookie consent if required.

## Core Web Vitals targets

LCP < 2.0s · INP < 200ms · CLS < 0.1 · Mobile Lighthouse ≥ 90

## Trust at launch

Honest proof bar · concept badge on spec work · no fake reviews · founder placeholder OK
