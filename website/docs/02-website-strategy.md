# Phase 2 — Website Strategy

> **Project:** Groundwork Web (groundwork-web.com)  
> **Status:** Complete  
> **Date:** 2026-06-25  
> **Inputs:** `01-research-and-patterns.md`, `business-profile.md`, Master OS v1.0  
> **Next phase:** `03-wireframes.md`

---

## Executive summary

Groundwork Web's site is a **sales asset**, not a portfolio experiment. Every page exists to move a local service business owner toward **one action: book a discovery call**.

**Strategic locks for v1:**

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Page scope | Home, Services, Work, About, Contact, 404 | Enough proof + depth; no blog until v2 |
| Primary CTA | Book a discovery call → `/contact` | Form-first at launch; Calendly placeholder until link is ready |
| Pricing on site | **Ranges on Services** + "custom quote on call" | Filters budget mismatch; avoids sticker shock without context |
| Launch proof | 1 spec case study — automotive shop | Aligns with niche; site quality is proof #1 |
| Geography | **United States (nationwide)** | Serve local businesses anywhere in the US |
| Founder photo | **Placeholder** at launch | Neutral blank frame on About; swap when ready |
| Calendly | **Empty / placeholder** at launch | `CALENDLY_URL` blank; CTAs go to Contact + form |
| Visual identity | Warm minimal + copper accent | Premium without Silicon Valley cold |
| Typography | **Geist** (sans) + system fallback | Matches Vercel-adjacent craft; excellent legibility |

---

## Target audience

### Primary customer (who we optimize the site for)

**The busy local service business owner** — runs the shop floor, not a laptop. Makes decisions fast if trust is established.

| Attribute | Detail |
|-----------|--------|
| **Industries (priority)** | Auto repair, detailing, performance shops, mechanics → then HVAC, roofing, electrical, landscaping, pressure washing |
| **Business size** | 1–20 employees, owner-operated or small team |
| **Revenue** | Roughly $300k–$3M/year — can afford $3k+ setup + monthly plan |
| **Tech literacy** | Low to medium — uses phone, Google, maybe Facebook; does not want to "manage a website" |
| **Decision style** | Practical, skeptical of hype, respects craft and reliability |
| **Primary device** | Mobile — checks things between jobs |

### Secondary visitor (not primary, but supported)

- Referral from another owner ("my buddy said call these guys")
- Spouse/office manager researching on owner's behalf
- Future: other agencies/partners (defer messaging for v2)

### Who we are NOT targeting on this site

- E-commerce brands
- SaaS startups
- National franchises with internal marketing teams
- Budget shoppers wanting a $500 Wix site

---

## Customer pain points

| Pain | What they say | What they mean |
|------|---------------|----------------|
| **Invisible online** | "People can't find us on Google" | Competitors get the calls |
| **Embarrassing site** | "My nephew built it years ago" | Hurts credibility with new customers |
| **No time** | "I don't have time for this stuff" | Won't learn DIY tools or fix plugins |
| **Burned before** | "We paid someone and nothing happened" | Needs proof and accountability |
| **Wrong solution** | "We have Facebook — isn't that enough?" | Doesn't understand owned presence |
| **Fear of cost** | "How much is this gonna run me?" | Needs ROI framing, not feature lists |
| **Fear of lock-in** | "What if I want to leave?" | Needs clarity on ownership and terms |

### Emotional state on arrival

Skeptical, busy, comparison-shopping (often 2–4 tabs open), allergic to marketing fluff.

---

## Desired emotions (after 30 seconds on site)

| Emotion | How we create it |
|---------|------------------|
| **Clarity** | Plain headline — they know it's for businesses like theirs |
| **Relief** | "They handle everything after launch" |
| **Trust** | Premium design, real process, honest spec work |
| **Confidence** | Structured offer, clear steps, no hype |
| **Urgency (light)** | Cost of waiting — competitors take calls |

**Not:** excitement about "digital transformation," awe at animations, or confusion about what we sell.

---

## Conversion goals

### Primary goal

**Discovery call request** via Contact page — **form submission** at launch (Calendly embed reserved but empty until link is added).

### Secondary goal (when Calendly is live)

**Calendly booking** — set `CALENDLY_URL` in `.env`. Until then, all "Book a Call" buttons link to `/contact`.

### Also track

- Browse Work → deepen trust → return to contact
- Email `hello@groundwork-web.com` directly

### Success metrics (first 90 days post-launch)

| Metric | Target |
|--------|--------|
| Discovery calls booked / month | 4+ (outreach-driven) |
| Form submissions / month | 2+ |
| Bounce rate on Home | < 60% |
| Mobile Lighthouse Performance | ≥ 90 |
| Avg time on Work page | > 45 sec |

### Conversion event tracking (implement at build)

- `cta_click` — location (hero, sticky, footer, etc.)
- `form_submitted`
- `calendly_scheduled` (when Calendly is connected)
- `phone_click` (if number added later)

---

## Brand personality

| Trait | Expression on site |
|-------|-------------------|
| **Confident** | Short sentences. No hedging. No "we try to..." |
| **Minimal** | Few sections, lots of air, one idea per block |
| **Premium** | Typography, spacing, motion quality — not clip art |
| **No-nonsense** | Shop-owner language, not agency jargon |
| **Grounded** | Earth tones, foundation metaphors, reliability |
| **Partner-minded** | "We run it for you" — long-term, not one-off |

### Voice guidelines

| Do | Don't |
|----|-------|
| "More calls from local customers" | "Omnichannel digital solutions" |
| "We build it and keep it running" | "Full-stack synergistic ecosystems" |
| "Custom-coded — fast and professional" | "Leveraging cutting-edge frameworks" |
| "30-minute call, no pressure" | "Schedule your transformational strategy session" |

### Brand metaphor system

**Groundwork** = foundation, site prep, first step before building.

Use sparingly in copy: *lay the groundwork, built on solid ground, we handle the foundation* — max 1–2 per page.

---

## Messaging strategy

### Hierarchy (what visitors learn, in order)

1. **Who it's for** — local service businesses (shops, trades)
2. **Outcome** — more leads, more calls, professional presence
3. **What we do** — build + host + maintain (growth system)
4. **Why us** — custom-coded, premium quality, you never touch tech
5. **Proof** — our site + spec case study + process
6. **Action** — book a call

### Core message pillars

| Pillar | Message |
|--------|---------|
| **Outcome** | Your phone should ring more. That's the job. |
| **System** | Website is step one — hosting and maintenance keep it working. |
| **Partnership** | We're not a one-and-done freelancer. |
| **Craft** | Custom-coded beats templates for speed, trust, and SEO. |
| **Simplicity** | You run your business. We run your web presence. |

---

## Approved copy — v1

### Tagline (meta, footer, outreach)

> Builds and runs websites for local service businesses — more leads, zero tech hassle.

### Homepage hero

**Headline (primary):**  
**More calls. Zero website headaches.**

**Subhead:**  
Groundwork Web builds custom websites for local shops and trades — then handles hosting, updates, and maintenance so you never think about it again.

**Primary CTA:** Book a Free Discovery Call  
**Microcopy under CTA:** 30 minutes · No obligation · We'll tell you honestly if we're not a fit

**Hero proof bar (honest at launch):**

| Element | Copy |
|---------|------|
| Signal 1 | Custom-coded |
| Signal 2 | Mobile-first |
| Signal 3 | Hosting & maintenance included |

*Replace with client logos / review count when available.*

### Homepage hero — alternates (A/B later)

| Variant | Headline |
|---------|----------|
| A (outcome) | **More calls. Zero website headaches.** ← **default** |
| B (identity) | **Websites that work as hard as you do.** |
| C (partnership) | **Your web presence. Built and run for you.** |

### Services page hero

**Headline:** A growth system — not just a website.  
**Subhead:** Setup, hosting, maintenance, and SEO foundations — one partner, one monthly plan.

### Work page hero

**Headline:** Built for businesses that run on phone calls.  
**Subhead:** See how we design for local service companies — fast, clear, and built to convert.

### About page hero

**Headline:** We get local businesses.  
**Subhead:** Groundwork Web exists so shop and trade owners can stop worrying about their website and focus on the work.

### Contact page hero

**Headline:** Let's see if we're a fit.  
**Subhead:** Book a 30-minute call or send a message. We'll learn about your business and tell you straight what we'd recommend.

### CTA copy system

| Context | Button text |
|---------|-------------|
| Header (sticky) | Book a Call |
| Hero | Book a Free Discovery Call |
| Mid-page | Book a Call |
| After FAQ | Book Your Discovery Call |
| Work card | View Project → |
| Final band | Book a Free Discovery Call |

**Secondary links (text only):** See our work · How it works · View services

---

## Offer structure (what we sell on the site)

### The Groundwork Growth System

| Layer | Name | What they get | Model |
|-------|------|---------------|-------|
| 1 | **Build** | Custom-coded website built for leads — mobile, fast, clear CTAs | One-time setup fee |
| 2 | **Run** | Hosting, SSL, uptime monitoring, backups | Monthly |
| 3 | **Maintain** | Content updates, fixes, security patches | Monthly |
| 4 | **Grow** *(foundation in v1, expanded v2)* | Basic local SEO, Google Business Profile guidance | Monthly |
| 5 | **Automate** *(v2 upsell)* | AI chat, review requests, lead routing | Add-on |

**Site messaging:** Lead with layers 1–3. Mention 4 as included foundation. Tease 5 as "coming as you grow."

### Pricing strategy (v1 launch)

**Decision:** Show **starting ranges** on Services page. Exact quote on discovery call.

| Package | Starting at | Includes |
|---------|-------------|----------|
| **Build** | $2,500 | Custom 5-page site, mobile-first, contact/booking flow, launch support |
| **Growth Plan** | $199/mo | Hosting, maintenance, minor updates, uptime monitoring |
| **Build + Growth** | $2,500 + $199/mo | Full system — most clients |

**Footnote on site:** Final pricing depends on scope — number of pages, integrations, and content needs. We'll quote on your discovery call.

**Why ranges, not hidden:** Shop owners fear unknown costs. Ranges qualify leads and position premium. Hiding price attracts wrong-fit prospects who ghost when they hear $3k.

**Why not exact price list:** Pre-launch — validate in first 3 sales calls. Update ranges after.

---

## Geographic focus

### Status: ✅ Locked — **United States (nationwide)**

Groundwork Web serves **local service businesses across the United States**. We are not limited to one metro — clients can be anywhere in the US.

### Approved copy

| Location | Copy |
|----------|------|
| Footer | Serving local service businesses **across the United States** |
| About | We work with shop and trade owners nationwide — automotive, contractors, HVAC, and more. |
| Contact | "Where is your business located?" (city/state field on form) |
| Homepage | "Local service businesses" — no single-city limitation |

### SEO & schema

- `LocalBusiness` / `Organization` schema: `areaServed` → `{ "@type": "Country", "name": "United States" }`
- Keyword focus: **national** industry terms (e.g. "web design for auto shops") — not city-specific at launch
- City landing pages: v2 if needed for SEO expansion

### Outreach note

Nationwide **service** does not require nationwide **outreach** on day one. In-person visits can still focus on your local area per `operations.md` — the site simply does not turn away out-of-market leads.

---

## Site architecture

### v1 sitemap

```
groundwork-web.com/
├── /                 Home — primary conversion
├── /services         Offer depth + pricing ranges
├── /work             Portfolio + case studies
├── /work/[slug]      Case study detail (1 spec at launch)
├── /about            Founder story + credibility
├── /contact          Contact form (primary) + Calendly placeholder
└── /404              Branded error + CTA
```

**Excluded from v1:** Blog, client portal, admin (v2 platform).

### URL conventions

- Lowercase, hyphenated slugs: `/work/westside-auto-care`
- Trailing slashes: consistent (pick one at build — recommend no trailing slash)
- Canonical URLs on all pages

---

## Navigation structure

### Desktop header

```
[Groundwork Web]    Services    Work    About    Contact    [Book a Call]
```

### Mobile header

```
[Logo]                    [Book a Call]  [☰]
```

Menu: Services · Work · About · Contact

### Footer columns

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Logo + tagline | Services · Work · About · Contact | hello@groundwork-web.com |
| | Privacy · Terms (minimal) | Serving businesses across the United States |

---

## Information hierarchy — first 5 seconds (Home)

Visitor must absorb, in order:

1. **Groundwork Web** — name / logo
2. **More calls. Zero website headaches.** — outcome
3. **Local shops and trades** — this is for me (or not)
4. **Book a Free Discovery Call** — what to do
5. **Custom-coded · Mobile-first · Hosting included** — trust strip

If any of these fail, we lose the comparison-shopping owner.

---

## Homepage — section order (locked)

| # | Section ID | Content | Conversion job | Psychology |
|---|------------|---------|----------------|------------|
| 1 | `hero` | Headline, subhead, CTA, proof bar | **Primary conversion** | "What is this? Can I trust it? What do I do?" |
| 2 | `who-we-help` | Industry chips/cards: auto, trades, local pros | **Self-selection** | "These guys work with people like me" |
| 3 | `problem` | 3 pain points: invisible, embarrassing site, no time | **Agitation** | "They understand my situation" |
| 4 | `system` | Growth system bento: Build, Run, Maintain, Grow | **Education** | "This is more than a website — good" |
| 5 | `work-preview` | 1 featured spec case study card | **Proof** | "I can see the quality" |
| 6 | `process` | 4 steps: Call → Build → Launch → We run it | **Fear reduction** | "I know what happens next" |
| 7 | `why-custom` | Brief: custom vs template/Wix | **Differentiation** | "Worth paying more than nephew/Wix" |
| 8 | `faq` | 6 questions | **Objection handling** | "My concerns are answered" |
| 9 | `cta-final` | Repeat headline + CTA + microcopy | **Last chance convert** | Catches long scrollers |
| 10 | `footer` | Nav, email, service area | **Catch skeptics** | Final trust + navigation |

**Removed from early draft:** Separate "testimonials" section at launch — no fake quotes. FAQ + work preview handle proof until real clients exist.

---

## Page-by-page strategy

### Home (`/`)

**Job:** Convert cold and warm traffic in one scroll or send to Work for proof.  
**Primary CTA:** Book discovery call  
**SEO title:** Groundwork Web \| Websites for Local Service Businesses  
**Meta description:** Custom websites for shops and trades — built for more calls, hosted and maintained for you. Book a free discovery call.

---

### Services (`/services`)

**Job:** Explain the growth system, show pricing ranges, convert researchers.  
**Sections:** Hero → system deep-dive (4 cards) → what's included lists → pricing table → comparison (us vs DIY/Wix) → FAQ (pricing-focused) → CTA  
**Primary CTA:** Book a call to get your quote

---

### Work (`/work`)

**Job:** Prove craft; reduce "can they actually build?" doubt.  
**Launch content:** 1 spec project minimum  
**Layout:** Grid of project cards → filter by industry (auto first)  
**Each card:** Thumbnail, industry tag, one outcome line, link to case study

---

### Work detail (`/work/westside-auto-care`)

**Job:** Deep proof for serious prospects; sales collateral for outreach.  
**Spec case study — locked for launch:**

| Field | Value |
|-------|-------|
| **Fictional business** | Westside Auto Care |
| **Industry** | Auto repair |
| **Problem** | Outdated site, no mobile, competitors ranking higher |
| **Solution** | Custom site, click-to-call, service pages, speed optimization |
| **Outcome (honest spec)** | "Designed to increase calls and local search visibility" — no fake metrics |
| **Label** | Concept project / demonstration work (small badge if needed for integrity) |

**Case study sections:** Challenge → Approach → Solution highlights → Results (projected goals, not fake numbers) → CTA

---

### About (`/about`)

**Job:** Humanize; build trust with skeptical owners.  
**Sections:** Hero → Cyrus story (Discount Tire background = understands service businesses, without over-emphasizing day job) → values (reliability, no BS) → how we're different from freelancers → CTA  
**Tone:** Direct, personal, not corporate "our team of experts"

**Founder photo (v1):** Neutral **placeholder** — empty frame or subtle avatar silhouette. No stock photo. Label optional: omit or small "Founder" caption only. Replace with real photo when ready.

---

### Contact (`/contact`)

**Job:** Capture leads with minimal friction.

**Layout at launch:**

| Block | Priority | Notes |
|-------|----------|-------|
| **Contact form** | Primary | Name, phone, business name, city/state, industry, message (optional) |
| **Calendly** | Placeholder | Reserved section — empty embed or "Online scheduling coming soon" with form below |
| **Email** | Secondary | hello@groundwork-web.com |

**CTA behavior until Calendly is live:** All site "Book a Call" buttons → `/contact` (anchor to form).

**Calendly config (when ready):** Set `CALENDLY_URL` in `.env` — e.g. `https://calendly.com/your-handle/discovery-call`. Empty string = hide embed, show form only.

**Expectations copy:** "We'll respond within 24 hours. Tell us about your business and we'll follow up to schedule a call — no pressure."

---

### 404

**Job:** Recover lost visitors.  
**Copy:** "This page doesn't exist." + link Home + Book a Call

---

## Launch proof strategy

| Priority | Asset | Status at launch |
|----------|-------|------------------|
| 1 | Groundwork Web site quality | Build to premium standard |
| 2 | Westside Auto Care spec case study | Build as demo + portfolio piece |
| 3 | Process section | Document 4-step flow |
| 4 | Honest proof bar | Custom-coded, etc. — no fake reviews |
| 5 | Cyrus About story + photo placeholder | Real story; blank photo frame until headshot ready |
| 6 | Client testimonials | Add when first client delivers |
| 7 | Client logos | Add with permission only |

**Integrity rule:** Spec work labeled as concept/demo if any metric could be misread as real client results.

---

## Visual identity — locked for Phase 4

### Color palette

| Token | Hex | Usage |
|-------|-----|-------|
| `bg-primary` | `#FAFAF8` | Page background — warm white |
| `bg-elevated` | `#FFFFFF` | Cards |
| `bg-dark` | `#171717` | CTA bands, footer |
| `text-primary` | `#171717` | Body, headings |
| `text-muted` | `#6B6B6B` | Secondary copy |
| `border` | `#E8E6E1` | Dividers, card borders |
| `accent` | `#B87333` | Copper — primary CTA, links, highlights |
| `accent-hover` | `#9A6129` | Button hover |
| `accent-subtle` | `#F5EDE6` | Accent backgrounds, badges |

**Rule:** Copper accent on **one focal element per viewport** — typically the CTA.

### Typography — Geist

| Role | Size (desktop) | Weight | Notes |
|------|----------------|--------|-------|
| Display | 56–72px | 600 | Hero only |
| H1 | 40–48px | 600 | Page titles |
| H2 | 28–32px | 600 | Section heads |
| H3 | 20–24px | 500 | Card titles |
| Body | 17–18px | 400 | Line-height 1.6 |
| Small | 14–15px | 400 | Captions, legal |

**Letter-spacing:** -0.02em on display and H1.

### Imagery

- **Founder photo:** Placeholder frame on About at launch — no stock "team" photo
- Project screenshots and browser mockups for Work / case studies
- Optional: subtle texture on dark sections (noise, 2–3% opacity)

---

## Content strategy

### Tone checklist (every page)

- [ ] Readable at 8th-grade level
- [ ] Short paragraphs (2–3 sentences max)
- [ ] Active voice
- [ ] No jargon without explanation
- [ ] One idea per section

### Words we use

calls, leads, customers, local, shop, trades, built, run, maintain, hosting, fast, mobile, professional, partner, monthly plan

### Words we avoid

synergy, disrupt, leverage, cutting-edge, solutions provider, digital ecosystem, best-in-class, world-class

---

## SEO strategy

### Keyword themes

| Theme | Example keywords |
|-------|------------------|
| Core | web design for auto shops, mechanic website design, local business website |
| Service | small business web design, custom website local business |
| Intent | website for [hvac contractor / auto repair / roofing] |
| Local (v2 optional) | web design [city] — add city pages if SEO expansion needed |
| Branded | Groundwork Web, groundwork web design |

### On-page plan

| Page | Primary keyword focus |
|------|----------------------|
| Home | local service business website design |
| Services | website hosting maintenance local business |
| Work | web design portfolio local business / auto shop website example |
| About | about Groundwork Web |
| Contact | book web design consultation |

### Technical SEO (at build)

- Unique `<title>` and meta description per page
- One H1 per page
- Semantic HTML (`header`, `main`, `section`, `article`, `footer`)
- `LocalBusiness` + `Organization` JSON-LD on Home
- `WebSite` schema with `potentialAction` for search
- `FAQPage` schema on Home FAQ section
- `sitemap.xml`, `robots.txt`
- Open Graph + Twitter Card images (1200×630)
- Canonical URLs

### Content SEO (v2)

Blog: "Why your auto shop needs a real website" — defer until after first client.

---

## Accessibility strategy

**Target:** WCAG 2.1 AA minimum.

| Requirement | Implementation |
|-------------|----------------|
| Color contrast | 4.5:1 body text; 3:1 large text — verify copper on white |
| Keyboard nav | All interactive elements focusable; visible focus ring |
| Screen readers | Meaningful alt text; `aria-label` on icon-only buttons |
| Motion | `prefers-reduced-motion`: disable Lenis + scroll animations |
| Forms | Labels, error messages, `aria-invalid` |
| Touch targets | 44×44px minimum on mobile |
| Skip link | "Skip to main content" |

---

## Performance strategy

### Core Web Vitals budgets

| Metric | Target |
|--------|--------|
| LCP | < 2.0s |
| INP | < 200ms |
| CLS | < 0.1 |
| Lighthouse Performance (mobile) | ≥ 90 |

### Asset policy

| Asset type | Rule |
|------------|------|
| Images | WebP/AVIF, responsive `srcset`, lazy below fold |
| Fonts | Subset Geist, `font-display: swap`, preload critical |
| JS | Defer non-critical; Alpine for small interactions |
| CSS | Tailwind purge; critical above-fold inlined if needed |
| Animation | GPU-friendly transforms only; no layout thrashing |

### Third-party scripts (minimize)

- Calendly embed — **only when `CALENDLY_URL` is set**; otherwise omit script entirely
- Analytics — Plausible or GA4, defer
- No chat widgets at launch

---

## Objection handling map

| Objection | Where addressed | Response summary |
|-----------|-----------------|------------------|
| "Too expensive" | Services pricing, FAQ | Ranges + ROI: one new customer/month often pays for the site |
| "My nephew can do it" | FAQ, Why Custom section | Reliability, professionalism, you need it working not learning |
| "I'll use Wix/Squarespace" | FAQ, Services comparison | Templates vs custom speed, SEO, and you still maintain it |
| "I don't have time" | Hero, Process | That's why we run it — your time is zero after kickoff |
| "How long does it take?" | FAQ, Process | Typical 2–4 weeks for build; depends on scope |
| "What if I already have a site?" | FAQ | We rebuild or improve — audit on discovery call |
| "Do I own the website?" | FAQ | Yes — clarify terms on call; you own your content |
| "What's the monthly fee for?" | Services | Hosting, updates, security — like insurance for your presence |
| "Are you local?" | About, footer | We serve local businesses **nationwide** across the United States |
| "Can I see examples?" | Work | Spec case study + our own site |

### FAQ — approved questions (Home)

1. How much does a website cost?
2. How long does it take to build?
3. What's included in the monthly plan?
4. I already have a website — can you help?
5. Why not just use Wix or Squarespace?
6. What happens on the discovery call?

---

## User journeys (validated against architecture)

### Journey 1 — Cold outreach (primary)

SMS/email with link → Home hero → Book call  
**Success:** Call booked in < 60 seconds on site

### Journey 2 — Skeptical researcher

Google → Home → Work → case study → Services (pricing) → Contact  
**Success:** Call or form after seeing proof + price range

### Journey 3 — Referral

Friend said call → Home → Book call immediately  
**Success:** Sticky CTA visible without scrolling

---

## Phase 2 decisions — launch config

| Item | Status | Notes |
|------|--------|-------|
| Service area | ✅ **United States** | Nationwide; footer + schema locked |
| Founder photo | ✅ **Placeholder** | Blank frame on About; add real photo later |
| Calendly | ✅ **Empty for now** | `CALENDLY_URL=""` — CTAs → `/contact`; add link when ready |
| Pricing validation | Draft ranges | Adjust after first 3 discovery calls |
| Spec case study name | ✅ Westside Auto Care | Locked |

---

## Phase 2 → Phase 3 handoff

Wireframes (`03-wireframes.md`) will detail:

1. Every section listed in homepage order (table above)
2. All 5 pages + case study detail + 404
3. Mobile and desktop layout notes per section
4. Interaction notes (sticky header, scroll reveals, contact form + Calendly placeholder)
5. Component list emerging from wireframes (hero, bento card, process step, FAQ accordion, CTA band)

---

## Phase 2 completion checklist

- [x] Target audience defined
- [x] Pain points and emotions mapped
- [x] Conversion goals and metrics set
- [x] Brand personality and voice documented
- [x] Messaging hierarchy and approved copy
- [x] Offer structure and pricing strategy
- [x] Geographic strategy — United States nationwide
- [x] Site architecture and navigation locked
- [x] Homepage section order locked
- [x] Every page strategy documented
- [x] Launch proof strategy (Westside Auto Care spec)
- [x] Color and typography locked for Phase 4
- [x] SEO strategy outlined
- [x] Accessibility targets set
- [x] Performance budgets set
- [x] Objection handling + FAQ approved
- [x] User journeys validated
- [x] Handoff to Phase 3 defined

**Gate status:** ✅ Ready for Phase 3

**No blockers** — metro, photo placeholder, and Calendly deferral are locked.
