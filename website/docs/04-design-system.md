# Phase 4 — Design System

> **Status:** Complete · **Implements in:** `app/resources/css/app.css`, `tailwind.config.js`, Blade components

## Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `bg-primary` | `#FAFAF8` | Page background |
| `bg-elevated` | `#FFFFFF` | Cards |
| `bg-dark` | `#171717` | CTA bands, footer |
| `text-primary` | `#171717` | Headings, body |
| `text-muted` | `#6B6B6B` | Secondary copy |
| `border` | `#E8E6E1` | Dividers |
| `accent` | `#B87333` | Primary CTA, links |
| `accent-hover` | `#9A6129` | CTA hover |
| `accent-subtle` | `#F5EDE6` | Badges, highlights |
| `success` | `#166534` | Form success |
| `error` | `#B91C1C` | Form errors |

**Rule:** One copper focal point per viewport.

## Typography — Geist (Inter fallback)

| Token | Size | Weight | LH |
|-------|------|--------|-----|
| `display` | 3.5–4.5rem | 600 | 1.1 |
| `h1` | 2.5–3rem | 600 | 1.15 |
| `h2` | 1.75–2rem | 600 | 1.2 |
| `h3` | 1.25–1.5rem | 500 | 1.3 |
| `body` | 1.0625rem | 400 | 1.6 |
| `small` | 0.875rem | 400 | 1.5 |

Letter-spacing: `-0.02em` on display and h1.

## Spacing (4px base)

`4, 8, 12, 16, 24, 32, 48, 64, 96, 128` — section padding `96px` desktop / `64px` mobile.

## Radius

| Token | Value | Use |
|-------|-------|-----|
| `sm` | 6px | Inputs |
| `md` | 8px | Cards |
| `lg` | 12px | Large cards |
| `full` | 9999px | Primary CTA pill |

## Components

### Button primary
Copper bg, white text, `full` radius, px-8 py-3. States: hover darken, focus ring 2px offset, disabled 50% opacity, loading spinner.

### Button secondary
Transparent, copper border, copper text.

### Card
`bg-elevated`, `border`, `md` radius, p-6.

### Input
`border`, `sm` radius, h-12, focus ring accent.

### Section eyebrow
`small`, uppercase, tracking-wider, `text-muted`.

### CTA band (dark)
`bg-dark`, white text, centered, py-20.

### Concept badge
`accent-subtle` bg, accent text, text-xs uppercase.

## Animation

| Token | Value |
|-------|-------|
| `duration-fast` | 150ms |
| `duration` | 300ms |
| `duration-slow` | 500ms |
| `ease` | cubic-bezier(0.22, 1, 0.36, 1) |

Scroll reveal: `translateY(24px)` → `0`, opacity 0 → 1. GSAP ScrollTrigger. Lenis smooth scroll. `@media (prefers-reduced-motion: reduce)` → disable all.

## Icons

Lucide via inline SVG in Blade. Size 20–24px. Use only when aiding scan (industry cards, process steps).

## Imagery

No stock team photos. Placeholder frame: 240×240, border, muted icon. Project screenshots in browser chrome mockups.

## Dark mode

**v1:** Light mode only. Dark used for CTA bands/footer, not full dark theme.
