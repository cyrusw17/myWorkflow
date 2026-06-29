# Phase 1 — Research & Patterns

> **Project:** Groundwork Web (groundwork-web.com)  
> **Status:** Complete  
> **Date:** 2026-06-25  
> **Next phase:** `02-website-strategy.md`

---

## Executive summary

Research across award-winning agency sites, premium SaaS (Stripe, Linear, Vercel), Framer-era landing pages, and local-service CRO literature reveals a **tension we must resolve intentionally**:

| Source | What they optimize for | Core lesson |
|--------|------------------------|-------------|
| Awwwards / CSS Design Awards | Craft, novelty, immersion | Narrative scroll, typography as hero, motion with purpose |
| Stripe / Linear / Vercel | Trust, clarity, product credibility | Restraint, contrast, spacing discipline, complete interaction states |
| Local service CRO | Phone calls and form fills | Speed, clarity, proof near CTAs, one primary action |

**Groundwork Web must do both:** look like a $3k–$10k+ agency to a shop owner *and* convert that shop owner into a booked discovery call.

**Critical decision from this research:** We will **not** pursue immersive 3D / WebGL scrollytelling for v1. It dominates 2026 award culture but conflicts with our conversion goals, performance budget, Laravel stack, and audience (non-technical local owners on mobile). We extract the *principles* (narrative pacing, scroll intentionality, typography confidence) without the *execution* (Three.js, pinned cinematic scenes).

---

## Reference sites studied

### Tier A — Premium SaaS (design discipline)

| Site | What they do well | Principle to extract (not copy) |
|------|-------------------|--------------------------------|
| **Stripe** | High-contrast layout, confident headline, single accent (purple gradient used sparingly), product UI as proof | One accent color carries the brand; let typography and whitespace do the rest |
| **Linear** | Extreme consistency, dark surfaces, accent used once per viewport, interaction-dense UI | Discipline beats decoration; every interactive element has complete states |
| **Vercel** | Ink-near-black (#171717), Geist typography, full-bleed sections, generous side margins | Monochrome confidence; content held in a narrow column within wide canvas |
| **Notion** | Friendly clarity, scannable benefit blocks, low cognitive load | Plain language + structure beats clever copy |
| **Raycast** | Tight product storytelling, keyboard-native aesthetic | Show the outcome visually when possible — for us, before/after sites |
| **Ramp** | B2B trust + numbers, clean proof sequencing | Metrics and specificity build authority |

**Why this tier works:** These sites communicate *"we are serious infrastructure"* without shouting. Groundwork Web borrows **restraint and hierarchy**, not the cold engineer-only tone — our buyers are shop owners, not developers.

---

### Tier B — Award-winning agencies & studios

| Pattern observed | Why it works | Groundwork Web application |
|------------------|--------------|----------------------------|
| Case study as hero content | Proof of outcomes, not claims | `/work` leads with measurable results (calls, speed, leads) |
| Oversized headline + tight subhead | 3-second comprehension | Hero: who we help + outcome + one CTA |
| Scroll-linked section reveals (2D) | Guides attention through a story | GSAP fade/slide between sections — no 3D |
| Custom cursor / micro-interactions | Signals craft | Subtle hover on cards and CTAs only |
| Showreel or device mockups | Makes abstract work tangible | Browser mockups of shop sites we've built |
| Minimal nav (4–5 links) | Reduces escape paths | Home, Services, Work, About, Contact + sticky CTA |

**Why agency sites win awards:** They demonstrate the *quality they sell*. Our site is the first portfolio piece.

---

### Tier C — High-converting local service sites (what our clients need)

| Pattern | Why it works | Note for Groundwork Web |
|---------|--------------|-------------------------|
| Phone number in header, tap-to-call | Primary conversion for trades | We sell this — demonstrate it on our own site |
| One primary CTA per page | Attention dilution kills conversion | "Book a discovery call" everywhere |
| Real photos, not stock | Instant trust or instant skepticism | Use real project screenshots; no fake team stock |
| Reviews embedded near CTAs | Reduces anxiety at decision moment | At launch: spec work + process proof until real testimonials exist |
| Service area clarity | Local trust signal | State who we serve (regions TBD in Phase 2) |
| Load under 3s on mobile | Google and humans punish slow sites | Non-negotiable performance budget |

**Why this tier matters:** Our *customers* live here. Groundwork Web must feel premium **and** practice what we preach. A cinematic 3D hero that hides the CTA would undermine our positioning.

---

### Tier D — Framer / modern landing templates

| Pattern | Why it works | Application |
|---------|--------------|-------------|
| Smooth scroll (Lenis) | Premium feel without heavy assets | Use with `prefers-reduced-motion` fallback |
| Bento grids for features | Scannable service breakdown | Services section on Home + `/services` |
| Gradient meshes (subtle) | Depth without imagery overload | Background atmosphere only — not Stripe-level flash |
| Social proof marquee | Logos move = momentum | Only when we have real client logos — never fake |
| FAQ accordion | Objection handling without clutter | Pricing fit, timeline, DIY alternatives |

---

## Layout patterns

### 1. Hero — clarity in one viewport

**Pattern:** Headline (outcome) → subhead (who + how) → primary CTA → proof bar (rating, logos, or stat).

**Why it works:** Visitors decide in ~3 seconds whether to stay. The hero answers: *What is this? Is it for me? Can I trust it? What do I do next?*

**Groundwork Web rule:** Hero promises **more leads for local service businesses**, not "custom web design." CTA is **Book a discovery call** — not "Learn more" + "View work" + "Contact" competing equally.

---

### 2. Proof bar immediately below hero

**Pattern:** Thin band with 3–5 trust signals: star rating, client logos, years in business, or one metric.

**Why it works:** Separates winners from unknowns before the visitor reads further. Conformity bias — *others trust them*.

**Groundwork Web rule:** At launch, use **honest proof** — e.g. "Custom-coded · Mobile-first · Hosting included" + spec project metrics. **No fake logos or fabricated review counts.**

---

### 3. Problem → agitation → solution (PAS)

**Pattern:** Name the pain (outdated site, no calls, nephew who disappeared) → cost of inaction → our system as relief.

**Why it works:** Shop owners feel seen. Emotional resonance before feature lists.

**Groundwork Web rule:** Copy in plain language a tire shop owner would use, not agency jargon.

---

### 4. Service pillars (bento or 3-column)

**Pattern:** 3–4 cards: Website, Hosting, Maintenance, SEO/Growth — each with one line of outcome.

**Why it works:** Chunking reduces overwhelm. Mirrors how owners think about "what I get."

**Groundwork Web rule:** Frame as **growth system**, not feature checklist.

---

### 5. Process (3–4 steps)

**Pattern:** Discovery → Build → Launch → Ongoing partnership.

**Why it works:** Reduces fear of the unknown. Implies professionalism and predictability.

**Groundwork Web rule:** Emphasize **they don't touch tech after kickoff** — you run it.

---

### 6. Work preview (case studies)

**Pattern:** 2–3 cards with before/after, industry tag, one outcome metric.

**Why it works:** Visual proof beats adjectives. Visitors imagine their business in the slot.

**Groundwork Web rule:** Spec projects for fictional local shops are OK at launch if labeled honestly or presented as demonstration work.

---

### 7. FAQ (objection handling)

**Pattern:** 5–7 questions: cost, timeline, why not Wix, what if I already have a site, contract length.

**Why it works:** Addresses doubts at the moment of highest intent (before final CTA).

---

### 8. Final CTA band (full-width)

**Pattern:** Repeat headline + single button + risk reducer ("Free 30-min call · No obligation").

**Why it works:** Long-scroll visitors need a second conversion opportunity.

---

### 9. Footer (dense trust)

**Pattern:** Contact, service areas, email, legal, subtle certifications.

**Why it works:** Catchers for skeptics who scroll to the bottom before deciding.

---

## Typography systems

### Trends observed

| Trend | Where seen | Verdict for Groundwork Web |
|-------|------------|----------------------------|
| Single geometric sans (Inter, Geist, custom) | Linear, Vercel, Stripe | **Adopt** — one family, weight/size for hierarchy |
| Oversized display headlines (48–80px desktop) | Agencies, Awwwards | **Adopt** — confident, not shouty |
| Tight letter-spacing on headlines (-0.02 to -0.04em) | Premium SaaS | **Adopt** — signals craft |
| Kinetic / animated type | Award sites | **Selective** — subtle fade-up only, not distracting loops |
| Serif + sans pairing | Editorial brands | **Defer** — adds complexity; revisit if brand needs warmth |
| Body 16–18px, line-height 1.5–1.6 | Universal best practice | **Adopt** — readability on mobile for older owners |

### Groundwork Web direction (draft — finalize in Phase 4)

- **Primary family:** Geist or Inter (Vite/Tailwind ecosystem, excellent legibility)
- **Scale:** 6 sizes max — display, h1, h2, h3, body, small
- **Weight:** 400 body, 500 labels, 600 headings — avoid ultralight (feels fragile for trades audience)
- **Voice in type:** Confident and clean, not playful startup or cold enterprise

**Why one family works:** Consistency reads as professionalism. Shop owners don't notice fonts — they notice *clarity*.

---

## Animation & motion

### What award sites do

- GSAP ScrollTrigger for section choreography
- Lenis for smooth momentum scroll
- Pinned sections with narrative chapters
- 3D camera paths (WebGL) — **reject for v1**

### What converts

- Lightweight hover states on buttons and cards
- Fade-up on scroll (once, staggered children)
- Page transitions under 300ms
- **Respect `prefers-reduced-motion`** — disable Lenis and scroll animations

### Groundwork Web animation rules

| Use | Avoid |
|-----|-------|
| 200–400ms ease-out on hovers | Bounce, elastic, playful springs |
| Subtle opacity + translateY on scroll reveal | Pinned 3D scenes |
| Lenis smooth scroll (desktop) | Auto-playing video heroes |
| Loading skeleton for async content | Parallax on every layer |
| CTA micro-pulse on idle (optional, once) | Cursor followers, particle backgrounds |

**Why:** Motion should **guide attention toward the CTA**, not demonstrate technical skill to other developers.

**Library stack (from brief, justified):** GSAP + Lenis + Alpine for toggles. No Three.js for v1.

---

## Color psychology

### Premium SaaS pattern

Monochrome base (near-black, white, gray scale) + **one accent** used sparingly. High contrast. No muddy mid-tones.

### Local service pattern

Trust colors: navy, forest green, deep orange, warm neutrals. Signals stability and approachability.

### Groundwork Web synthesis

We are **premium agency** selling to **blue-collar buyers**. Palette must feel:

- **Grounded** — name literally suggests foundation, earth, reliability
- **Premium** — not cheap template blues or neon gradients
- **Warm enough** — not sterile Silicon Valley cold

**Draft palette direction (Phase 4 will tokenize):**

| Role | Direction | Why |
|------|-----------|-----|
| Background | Warm off-white (#FAFAF8) or deep charcoal (#1A1A1A) | Light mode primary; dark accents for CTA bands |
| Text | Near-black (#171717) | Vercel-style ink — maximum readability |
| Accent | Copper / burnt amber OR deep forest green | Earth + craft; avoids generic "agency purple" |
| Muted | Warm gray scale | Borders, secondary text |
| Semantic | Success green, error red — standard | Forms and feedback |

**Rule:** Accent appears on **primary CTA, active nav, and one highlight per viewport** — not everywhere.

---

## Conversion strategies

### Funnel for Groundwork Web

```
Awareness (outreach, SEO, referral)
    → Land on Home or Services
    → Understand offer in 5 seconds
    → See proof (work, process)
    → Objections handled (FAQ)
    → Book discovery call (Calendly)
    → Lead in database → sales conversation
```

### CRO principles to implement

| Principle | Implementation |
|-----------|----------------|
| **One primary action** | "Book a discovery call" — secondary links are text, not buttons |
| **CTA repetition** | Hero, mid-page after proof, final band, sticky header |
| **Friction reduction** | Calendly embed — no 12-field form for first contact |
| **Risk reversal** | "No obligation · 30 minutes · We'll tell you honestly if we're not a fit" |
| **Specificity** | "Local shops and trades" not "businesses of all sizes" |
| **Outcome language** | "More calls" not "responsive design" |
| **Proof at decision points** | Testimonial or stat adjacent to every CTA block |
| **Speed** | LCP < 2.5s, minimal JS on first paint |

### Behavioral psychology

| Technique | Ethical use on our site |
|-----------|-------------------------|
| Social proof | Real testimonials only when available |
| Authority | Show craft via site quality + process |
| Scarcity | **Careful** — only honest capacity limits ("Taking 3 new clients this quarter") |
| Loss aversion | "Every month without a real site, competitors get the calls" |
| Commitment ladder | Free call → proposal → deposit — don't ask for payment on first visit |

---

## Navigation patterns

### Recommended structure

```
[Logo]     Services   Work   About   Contact     [Book a Call]
```

**Why minimal nav works:** Every link is an exit from the conversion path. Five items max.

### Sticky header behavior

| Scroll state | Behavior |
|--------------|----------|
| Top | Transparent or light — hero breathes |
| Scrolled | Solid background, subtle shadow, CTA button visible |
| Mobile | Hamburger + **prominent CTA button** (not buried in menu) |

**Why sticky CTA works:** 15–30% conversion lift reported when primary action stays visible (local service CRO research).

### Mobile-specific

- Thumb-zone CTA placement
- Tap targets ≥ 44px
- No hover-dependent interactions
- Phone number visible if we add click-to-call later

---

## Trust-building techniques

| Technique | Priority for launch | Notes |
|-----------|---------------------|-------|
| Site quality as proof | **#1** | The site itself is the portfolio |
| Spec case studies | **#2** | Automotive shop demo site |
| Process transparency | **#3** | 4-step "how we work" |
| Founder story (About) | **#4** | Cyrus — credible, local, understands service businesses |
| Real testimonials | When available | Never fabricate |
| Client logos | When available | Never use logos without permission |
| Guarantees | Optional | e.g. satisfaction on setup milestone |
| Licenses / insurance | N/A at launch | Not applicable to web agency |

**"Trusted by" vs "Our clients":** Research suggests "Trusted by" triggers conformity bias more strongly — use only when true.

---

## CTA placement map (Homepage)

| Location | CTA copy (draft) | Purpose |
|----------|------------------|---------|
| Header (sticky) | Book a Call | Always available |
| Hero | Book a Free Discovery Call | Primary conversion |
| After services | See How It Works → or Book a Call | Post-education |
| After work preview | View Case Study / Book a Call | Proof → action |
| After FAQ | Book a Call | Objections cleared |
| Final band | Ready for more leads? Book a call. | Last chance |
| Contact page | Calendly embed + minimal form fallback | High-intent visitors |

---

## User flow (primary paths)

### Path A — Cold outreach landing (most common early)

```
Text/email with link → Home hero → scan proof → Book call
```

**Requirement:** Hero alone must convert without scrolling.

### Path B — Skeptical researcher

```
Home → Work → case study → Services → About → Contact
```

**Requirement:** Every page ends with CTA. Work page is conversion asset, not gallery only.

### Path C — Referral (warm)

```
Home → Book call (fast path)
```

**Requirement:** CTA above fold, minimal friction.

---

## Anti-patterns to avoid

### Generic agency clichés

| Avoid | Why |
|-------|-----|
| "We craft digital experiences" | Meaningless to shop owners |
| Rocket ship / lightbulb icons | Template energy |
| "Innovative solutions" | Empty |
| Full-screen video background | Slow, cliché, hides message |
| Carousel heroes | Low engagement, hides CTA |
| Chat widget on first second | Annoying before trust exists |

### Trust killers

| Avoid | Why |
|-------|-----|
| Fake testimonials | Destroys credibility if caught — instant deal killer |
| Stock photos of "diverse team" | Shop owners detect fakes |
| Fake client logos | Legal and ethical risk |
| inflated stats | Unverifiable claims backfire |

### Technical anti-patterns

| Avoid | Why |
|-------|-----|
| Three.js hero for v1 | GPU cost, accessibility, maintenance — wrong ROI |
| 2MB+ images | Kills mobile conversion |
| 15 npm animation libraries | Bundle bloat |
| Cookie-cutter Webflow template look | Undermines $3k+ positioning |
| Auto-playing audio/video | Immediate bounce |

### Groundwork Web explicit don'ts (from research + brief)

1. No 3D scroll experiences in v1
2. No fake social proof at launch
3. No more than one primary button style per section
4. No blog before first client (v2)
5. No dark patterns (fake scarcity, hidden pricing tricks)
6. No sacrificing mobile speed for desktop animation

---

## Extracted principles — Groundwork Web design constitution

These rules govern Phases 2–4. They are **our** principles, not copies of any reference site.

### 1. Conversion is the product

The site exists to book discovery calls. Beauty serves conversion, not awards.

### 2. Premium through restraint

Whitespace, contrast, typography, and interaction completeness — not effects.

### 3. One accent, one CTA, one message per section

Discipline creates premium feel. Clutter creates cheap feel.

### 4. Show, don't claim

Case studies, mockups, and this site's own quality are the proof.

### 5. Speak shop owner, not developer

Outcomes and plain language. No jargon without explanation.

### 6. Performance is a feature

Fast sites convert better and demonstrate competence.

### 7. Motion with mercy

Animate to guide; respect reduced motion; never block content.

### 8. Honest at launch

Spec work and process proof until real testimonials exist.

### 9. Mobile is the main device

Design mobile-first — owners check sites on phones between jobs.

### 10. Narrative scroll, not cinematic scroll

Section-by-section story with 2D reveals — not 3D immersion.

---

## What we deliberately reject from Awwwards culture

| Trend | Why we reject for Groundwork Web |
|-------|----------------------------------|
| WebGL / Three.js heroes | Wrong audience, performance cost, maintenance burden |
| Experimental navigation | Shop owners expect standard nav |
| Anti-design / chaotic type | Conflicts with trust for conservative buyers |
| AI-personalized layouts | Over-engineering for v1 |
| Award-chasing over conversion | Business goal is clients, not Site of the Day |

**Note:** We can still hit a **high craft bar** without 3D. Linear and Vercel prove restraint wins.

---

## Research → Phase 2 handoff

Phase 2 (`02-website-strategy.md`) must decide using this research:

1. **Exact homepage section order** with conversion job per section
2. **Messaging** — headline, subhead, CTA copy variants
3. **Launch proof strategy** — what spec case study we build first (automotive shop recommended)
4. **Color and type final choices** — narrow draft palette above
5. **Geographic focus** — service area for local SEO and trust copy
6. **Pricing visibility** — show ranges vs "book a call for quote"
7. **v1 page scope** — confirm Home, Services, Work, About, Contact only

---

## Sources & inspiration categories

- Awwwards / CSS Design Awards — narrative scroll, typography confidence (execution level adjusted)
- Stripe, Linear, Vercel, Notion — restraint, contrast, interaction density
- Framer community templates — section rhythms, bento layouts, smooth scroll
- Local service CRO practitioners — phone visibility, proof placement, speed budgets
- Premium agency case study structures — MRG Growth, Orbit Media social proof patterns
- GSAP / Lenis documentation — performant 2D scroll choreography

**We studied patterns. We do not clone any site.**

---

## Phase 1 completion checklist

- [x] Reference sites studied and categorized
- [x] Layout patterns documented with rationale
- [x] Typography trends and direction drafted
- [x] Animation principles and library scope defined
- [x] Color psychology and draft direction
- [x] Conversion and CTA strategy outlined
- [x] Navigation patterns defined
- [x] Trust-building techniques prioritized
- [x] User flows mapped
- [x] Anti-patterns documented
- [x] Groundwork Web principles extracted
- [x] Awwwards 3D trend explicitly rejected with reasoning
- [x] Handoff to Phase 2 defined

**Gate status:** ✅ Ready for Phase 2 — pending your review
