# Research — Founding Client Landing Page

> Principles extracted from Stripe, Linear, Apple, Framer, Vercel, and high-converting SaaS/agency landings.  
> **Do not copy layouts.** Use the reasoning.

---

## Hero patterns

| Principle | Why it converts |
|-----------|-----------------|
| One clear audience callout | Shop owners self-select in 2 seconds — reduces unqualified leads |
| Transformation headline (outcome, not service) | "More calls" beats "Web design agency" — speaks to their goal |
| Offer visible above fold | Removes "what does this cost?" friction before scroll |
| Dual CTA (primary + secondary) | Captures ready-to-book and still-browsing visitors |
| Scarcity with honesty | "3 spots" creates urgency without fake countdown timers |

## Trust without fake proof

| Principle | Why it converts |
|-----------|-----------------|
| Explain *why* the offer exists | Transparency beats fabricated testimonials for a launch |
| Name the trade openly | Waiving setup fee for case study feels fair, not cheap |
| Industry pills | Visitor sees their business type — instant relevance |
| Professional visual design | Premium aesthetics signal premium delivery |

## Offer presentation

| Principle | Why it converts |
|-----------|-----------------|
| Anchor pricing ($2,500+ crossed out) | Frames $199/mo as a deal without sounding discount-bin |
| Side-by-side "after program" vs "founding" | Makes the exclusive nature concrete |
| Spots counter | Real scarcity — update manually as spots fill |
| 12-month term stated early | Filters bad-fit leads before the call |

## Section order (conversion flow)

1. **Hero** — who, what, why care, CTA  
2. **Social proof (honest)** — why only 3, why trust us anyway  
3. **Offer** — pricing mechanics  
4. **Included** — reduce "what am I getting?" anxiety  
5. **Why this exists** — the trade, builds trust  
6. **How it works** — removes "what happens next?" fear  
7. **Why custom** — educate, don't attack DIY  
8. **FAQ** — objection handling  
9. **Final CTA + form** — urgency + frictionless booking  

Each section answers: *Why trust? Why now? Why not wait? Why not someone else?*

## Typography & spacing

| Principle | Why it converts |
|-----------|-----------------|
| One type family, 2–3 weights | Cohesive, premium (Stripe/Linear pattern) |
| Large display headline | Authority and confidence |
| Generous whitespace in hero | Focus — one message per viewport |
| Tighter density in feature grids | More proof per scroll without clutter |

## Color psychology

- **Dark hero** — premium, modern, stands apart from generic white agency sites  
- **Warm copper accent** — approachable for blue-collar audience; not cold tech-blue  
- **White form card on dark CTA** — maximum contrast on the conversion action  

## CTA rules

- Primary: "Book Your Free Strategy Call" — low commitment, high value  
- Repeat CTA every ~2 scroll depths  
- Form at bottom for those who read everything  
- No navigation clutter — single page, one goal  

## Performance

- No heavy WebGL or video backgrounds for v1  
- GSAP scroll reveals only — respects `prefers-reduced-motion`  
- System fonts fallback, single font load  
- SQLite leads — fast, migrates to MySQL/Laravel later  

---

## Applied to this build

- One-page PHP architecture → migrates to Laravel Blade components  
- Config-driven copy in `config/site.php`  
- Modular sections in `includes/sections/`  
- Lead capture: SQLite + log + mail() hook for production SMTP  
