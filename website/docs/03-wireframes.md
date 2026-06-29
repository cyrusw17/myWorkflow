# Phase 3 — Wireframes

> **Project:** Groundwork Web (groundwork-web.com)  
> **Status:** Complete  
> **Date:** 2026-06-25  
> **Inputs:** `01-research-and-patterns.md`, `02-website-strategy.md`  
> **Next phase:** `04-design-system.md`

---

## How to read this document

- **ASCII wireframes** = layout structure, not final visual design
- **`[ ]`** = interactive element
- **Conversion / Psychology** = why the section exists
- **Breakpoints:** Mobile `< 768px` · Tablet `768–1023px` · Desktop `≥ 1024px`
- **All "Book a Call" CTAs** → `/contact#form` until `CALENDLY_URL` is set

---

## Global components

### G1 — Site header

**Conversion job:** Persistent navigation + always-visible CTA  
**Psychology:** Reduces "how do I reach them?" friction

#### Desktop (≥ 1024px)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ [Logo Groundwork Web]     Services   Work   About   Contact    [Book a Call] │
└────────────────────────────────────────────────────────────────────────────┘
```

| Element | Behavior |
|---------|----------|
| Logo | Links to `/` |
| Nav links | Standard hover underline or color shift |
| `[Book a Call]` | Copper filled button → `/contact#form` |
| Scroll | After 80px scroll: solid `bg-primary` background, subtle bottom border, slight shadow |

#### Mobile (< 768px)

```
┌──────────────────────────────────────┐
│ [Logo]              [Book a Call] [☰]│
└──────────────────────────────────────┘
```

| Element | Behavior |
|---------|----------|
| `[Book a Call]` | Always visible — never buried in menu |
| `[☰]` | Opens full-screen or slide-down overlay: Services · Work · About · Contact |
| Menu open | Body scroll locked; focus trap for a11y |

**Primary action:** Book a Call  
**Secondary action:** Nav to Work (proof seekers)

---

### G2 — Site footer

**Conversion job:** Catch bottom-scroll skeptics; reinforce nationwide service  
**Psychology:** Legitimacy — real email, real structure

```
┌────────────────────────────────────────────────────────────────────────────┐
│  [Logo]                                                                    │
│  Builds and runs websites for local service businesses.                    │
│                                                                            │
│  Services · Work · About · Contact          hello@groundwork-web.com       │
│  Privacy · Terms                            Serving businesses across        │
│                                             the United States              │
│                                                                            │
│  © 2026 Groundwork Web                                                     │
└────────────────────────────────────────────────────────────────────────────┘
```

| Breakpoint | Layout |
|------------|--------|
| Desktop | 3 columns |
| Mobile | Stacked: logo+tagline → links → email+service area |

---

### G3 — CTA button (primary)

```
┌─────────────────────────┐
│  Book a Free Discovery  │  ← copper bg, white text, 100px pill or 8px radius (pick in Phase 4)
│         Call            │
└─────────────────────────┘
   30 min · No obligation   ← microcopy, text-muted, 14px
```

**States:** default · hover (darken) · focus (ring) · active · disabled · loading

---

### G4 — Section container

| Token | Desktop | Mobile |
|-------|---------|--------|
| Max content width | `1200px` centered | `100% - 32px` padding |
| Section vertical padding | `96px` top/bottom | `64px` top/bottom |
| Section label (optional) | Small caps eyebrow above H2 | Same |

---

## Page: Home (`/`)

**Page job:** Convert in one scroll or send to Work  
**H1:** None in hero (display headline only) — page has one logical H1 in hero for SEO: visually display text, semantically `<h1>`

---

### H1 — Hero (`#hero`)

**Conversion job:** Answer what/who/why/trust/action in 5 seconds  
**Psychology:** Busy owner decides stay or bounce immediately  
**Objection removed:** "Is this for me?" + "Can I trust them?"

#### Desktop wireframe

```
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│   More calls.                                                              │
│   Zero website headaches.                    ┌──────────────────────────┐  │
│                                            │  [browser mockup or       │  │
│   Groundwork Web builds custom websites    │   abstract device frame   │  │
│   for local shops and trades — then        │   showing sample shop     │  │
│   handles hosting, updates, and            │   site preview]          │  │
│   maintenance so you never think           │                          │  │
│   about it again.                          └──────────────────────────┘  │
│                                                                            │
│   [ Book a Free Discovery Call ]                                           │
│   30 minutes · No obligation · We'll tell you honestly if we're not a fit   │
│                                                                            │
│   ─────────────────────────────────────────────────────────────────────    │
│   Custom-coded    ·    Mobile-first    ·    Hosting & maintenance included │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

#### Mobile wireframe

```
┌──────────────────────────────┐
│ More calls.                  │
│ Zero website headaches.      │
│                              │
│ [subhead — full width]       │
│                              │
│ [ Book a Free Discovery Call]│  ← full width button
│ [microcopy]                  │
│                              │
│ ┌──────────────────────────┐ │
│ │  [mockup — shorter]      │ │
│ └──────────────────────────┘ │
│                              │
│ Custom-coded · Mobile-first  │
│ · Hosting included           │
└──────────────────────────────┘
```

| Action | Target |
|--------|--------|
| **Primary** | Book CTA → `/contact#form` |
| **Secondary** | Text link "See our work" → `/work` |

**Animation:** Headline + subhead fade-up on load (stagger 100ms). Mockup fade-up delayed. Respect `prefers-reduced-motion`.

---

### H2 — Who we help (`#who-we-help`)

**Conversion job:** Self-selection — visitor sees their industry  
**Psychology:** "These guys get shops like mine"  
**Objection removed:** "They only do fancy corporate stuff"

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        WHO WE WORK WITH                                    │
│                   Built for businesses like yours                          │
│                                                                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  [icon]     │ │  [icon]     │ │  [icon]     │ │  [icon]     │          │
│  │  Auto shops │ │  Contractors│ │  HVAC &     │ │  Local pros │          │
│  │  & mechanics│ │  & roofers  │ │  trades     │ │  & services │          │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘          │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

| Breakpoint | Layout |
|------------|--------|
| Desktop | 4 cards in row |
| Tablet | 2×2 grid |
| Mobile | 2×2 grid or horizontal scroll snap (prefer 2×2) |

**Cards:** White `bg-elevated`, border, no click required — informational only  
**Animation:** Scroll reveal stagger per card

---

### H3 — Problem (`#problem`)

**Conversion job:** Agitate pain — create motivation to act  
**Psychology:** Empathy before pitch  
**Objection removed:** "They don't understand my situation"

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     SOUND FAMILIAR?                                        │
│              Most shop owners we talk to say the same things               │
│                                                                            │
│  ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐   │
│  │ 01                 │ │ 02                 │ │ 03                 │   │
│  │ Customers can't    │ │ Your site looks    │ │ You don't have     │   │
│  │ find you online    │ │ outdated or broken │ │ time to deal with  │   │
│  │ — competitors get  │ │ on mobile — and    │ │ website stuff      │   │
│  │ the calls          │ │ it costs you trust │ │                    │   │
│  └────────────────────┘ └────────────────────┘ └────────────────────┘   │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

| Action | Target |
|--------|--------|
| **Primary** | None — emotional setup |
| **Secondary** | Scroll continues to solution |

**Mobile:** 3 cards stacked vertically

---

### H4 — Growth system (`#system`)

**Conversion job:** Educate on offer — not "a website," a system  
**Psychology:** Reframe purchase as partnership + recurring value  
**Objection removed:** "What am I actually paying for?"

```
┌────────────────────────────────────────────────────────────────────────────┐
│                   THE GROUNDWORK GROWTH SYSTEM                             │
│         We don't just build a site — we run your web presence              │
│                                                                            │
│  ┌──────────────────────────────┐  ┌──────────────────────────────┐       │
│  │ BUILD                        │  │ RUN                          │       │
│  │ Custom-coded website built   │  │ Hosting, SSL, backups,       │       │
│  │ for calls — mobile, fast     │  │ uptime monitoring            │       │
│  └──────────────────────────────┘  └──────────────────────────────┘       │
│  ┌──────────────────────────────┐  ┌──────────────────────────────┐       │
│  │ MAINTAIN                     │  │ GROW                         │       │
│  │ Updates, fixes, security     │  │ SEO foundations, Google      │       │
│  │ — you never touch it         │  │ Business Profile guidance    │       │
│  └──────────────────────────────┘  └──────────────────────────────┘       │
│                                                                            │
│              [ View full services → ]                                      │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

| Breakpoint | Bento layout |
|------------|--------------|
| Desktop | 2×2 bento grid, equal height |
| Mobile | 4 cards stacked |

**Primary action:** "View full services" → `/services`  
**Secondary:** Implicit scroll to work preview

---

### H5 — Work preview (`#work-preview`)

**Conversion job:** Visual proof of quality  
**Psychology:** "I can see what I'd get"  
**Objection removed:** "Can they actually build anything good?"

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         SELECTED WORK                                      │
│                  See what we build for local businesses                    │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │ [Concept]                                                          │   │
│  │ ┌──────────────────────────────────────────────────────────────┐  │   │
│  │ │                                                              │  │   │
│  │ │            [large project screenshot / mockup]               │  │   │
│  │ │                                                              │  │   │
│  │ └──────────────────────────────────────────────────────────────┘  │   │
│  │  Westside Auto Care · Auto repair                                 │   │
│  │  Designed to increase calls and local search visibility           │   │
│  │  [ View project → ]                                               │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

| Element | Notes |
|---------|-------|
| `[Concept]` badge | Small pill — honest spec label |
| Card | Featured — only 1 at launch; room for 2-col when more projects exist |

**Primary action:** View project → `/work/westside-auto-care`  
**Secondary:** —

---

### H6 — Process (`#process`)

**Conversion job:** Reduce fear of unknown  
**Psychology:** Predictability = trust  
**Objection removed:** "What happens if I say yes?"

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        HOW IT WORKS                                        │
│                   Simple process. No surprises.                            │
│                                                                            │
│    ①────────────②────────────③────────────④                              │
│   Discovery      Build         Launch        We run it                     │
│   30-min call    Custom site   Go live       Hosting, updates,             │
│   Learn your     built for     on your       maintenance —                 │
│   business       your goals    domain        month after month             │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

| Breakpoint | Layout |
|------------|--------|
| Desktop | 4 steps horizontal with connecting line |
| Mobile | 4 steps vertical timeline |

**No CTA in section** — flows to differentiation

---

### H7 — Why custom (`#why-custom`)

**Conversion job:** Differentiate from Wix/nephew  
**Psychology:** Justify premium price  
**Objection removed:** "Why not cheaper options?"

```
┌────────────────────────────────────────────────────────────────────────────┐
│              WHY NOT WIX — OR YOUR NEPHEW?                                 │
│                                                                            │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐       │
│  │ Templates & DIY             │  │ Groundwork Web              │       │
│  │ ─────────────────────       │  │ ─────────────────────       │       │
│  │ · You maintain it           │  │ · We build AND run it       │       │
│  │ · Looks like everyone else  │  │ · Custom-coded for speed    │       │
│  │ · Plugin problems           │  │ · Built for phone calls     │       │
│  │ · Your time = zero saved    │  │ · Your time = zero needed   │       │
│  └─────────────────────────────┘  └─────────────────────────────┘       │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

| Breakpoint | Layout |
|------------|--------|
| Desktop | Side-by-side comparison |
| Mobile | Stacked — Groundwork card second (recency bias) |

---

### H8 — FAQ (`#faq`)

**Conversion job:** Kill remaining objections  
**Psychology:** Safe to proceed  
**Objection removed:** Price, time, DIY, ownership

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     FREQUENTLY ASKED QUESTIONS                             │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │ [+] How much does a website cost?                                  │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │ [−] How long does it take to build?                                │   │
│  │     Typical builds take 2–4 weeks depending on scope...          │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │ [+] What's included in the monthly plan?                           │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │ [+] I already have a website — can you help?                       │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │ [+] Why not just use Wix or Squarespace?                           │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │ [+] What happens on the discovery call?                            │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

**Interaction:** Alpine.js accordion — one open at a time; `aria-expanded` on buttons  
**Max width:** `720px` centered for readability  
**Schema:** `FAQPage` JSON-LD

---

### H9 — Final CTA (`#cta-final`)

**Conversion job:** Convert long-scroll visitors  
**Psychology:** Last chance + urgency without fake scarcity  
**Objection removed:** "I'll think about it" → gentle nudge

```
┌────────────────────────────────────────────────────────────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │  ← bg-dark #171717
│ ░                                                                      ░ │
│ ░        Ready for more calls — without the tech headaches?            ░ │
│ ░                                                                      ░ │
│ ░        [ Book a Free Discovery Call ]                              ░ │
│ ░        30 minutes · No obligation                                    ░ │
│ ░                                                                      ░ │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
└────────────────────────────────────────────────────────────────────────────┘
```

**Mobile:** Full-width button, white text on dark band  
**Primary action:** Book CTA → `/contact#form`

---

### H10 — Footer

Uses global **G2**.

---

## Page: Services (`/services`)

**Page job:** Explain system + pricing ranges → book call  
**H1:** A growth system — not just a website.

---

### S1 — Hero

```
┌────────────────────────────────────────────────────────────────────────────┐
│  A growth system — not just a website.                                     │
│  Setup, hosting, maintenance, and SEO foundations — one partner,           │
│  one monthly plan.                                                         │
│                                                                            │
│  [ Book a Call to Get Your Quote ]                                         │
└────────────────────────────────────────────────────────────────────────────┘
```

**Mobile:** Left-aligned text, full-width CTA

---

### S2 — System deep-dive

```
┌────────────────────────────────────────────────────────────────────────────┐
│  WHAT'S INCLUDED                                                           │
│                                                                            │
│  [ BUILD card — expanded ]                                                 │
│    · Custom design & development                                           │
│    · Mobile-first, fast loading                                            │
│    · Contact / lead capture flows                                          │
│    · Launch on your domain                                                 │
│                                                                            │
│  [ RUN card — expanded ]                                                   │
│  [ MAINTAIN card — expanded ]                                              │
│  [ GROW card — expanded ]                                                  │
│                                                                            │
│  [ AUTOMATE — coming soon teaser card, muted ]                             │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

| Breakpoint | Layout |
|------------|--------|
| Desktop | Alternating image/text or stacked expandable cards |
| Mobile | Accordion per layer (optional) or stacked cards |

---

### S3 — Pricing table

**Conversion job:** Qualify budget; reduce "how much?" anxiety  
**Psychology:** Transparency builds trust with skeptical owners

```
┌────────────────────────────────────────────────────────────────────────────┐
│  PRICING                                                                   │
│  Starting points — final quote depends on your scope                       │
│                                                                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │ BUILD           │  │ GROWTH PLAN     │  │ FULL SYSTEM     │            │
│  │ from $2,500     │  │ from $199/mo    │  │ from $2,500     │            │
│  │ one-time        │  │ recurring       │  │ + $199/mo       │            │
│  │                 │  │                 │  │ ★ Most clients  │            │
│  │ [bullets]       │  │ [bullets]       │  │ [bullets]       │            │
│  │                 │  │                 │  │                 │            │
│  │ [Get a quote]   │  │ [Get a quote]   │  │ [Get a quote]   │            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
│                                                                            │
│  Final pricing depends on pages, integrations, and content needs.          │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

| Mobile | Cards stacked; "Full System" card first or highlighted |
|--------|--------------------------------------------------------|

**All quote buttons** → `/contact#form`

---

### S4 — Comparison table

```
┌────────────────────────────────────────────────────────────────────────────┐
│  GROUNDWORK WEB  vs  DIY / TEMPLATES                                       │
│                                                                            │
│                    │ Wix / DIY    │ Groundwork Web                        │
│  ──────────────────┼──────────────┼─────────────────                      │
│  Custom design     │      ✗       │      ✓                                │
│  You maintain it   │      ✓       │      ✗                                │
│  Built for calls   │      ~       │      ✓                                │
│  Hosting included  │      ~       │      ✓                                │
│  Ongoing support   │      ✗       │      ✓                                │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

**Mobile:** Horizontal scroll table or card flip per row

---

### S5 — Services FAQ

5–6 pricing-focused questions (subset of home FAQ + ROI question)

---

### S6 — CTA band

Same pattern as **H9** — dark band, book call

---

## Page: Work (`/work`)

**Page job:** Portfolio proof  
**H1:** Built for businesses that run on phone calls.

---

### W1 — Hero

Compact — half height of home hero

---

### W2 — Project grid

```
┌────────────────────────────────────────────────────────────────────────────┐
│  [ All ]  [ Automotive ]  [ Trades ]  [ Other ]    ← filters (1 project   │
│                                                       at launch = hide or   │
│  ┌────────────────────────────┐              show All only)               │
│  │ [screenshot]               │                                            │
│  │ Concept · Auto repair      │                                            │
│  │ Westside Auto Care         │                                            │
│  │ Built to drive more calls  │                                            │
│  │ [ View project → ]         │                                            │
│  └────────────────────────────┘                                            │
│                                                                            │
│  ┌ - - - - - - - - - - - - - ┐  ← placeholder dashed card (optional)     │
│  │ Your project could be next │                                            │
│  │ [ Book a call ]            │                                            │
│  └ - - - - - - - - - - - - - ┘                                            │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

**At launch:** Hide filters if only 1 project — show single featured card + "Your project could be next" CTA card

---

## Page: Work detail (`/work/westside-auto-care`)

**Page job:** Deep proof for sales conversations  
**H1:** Westside Auto Care

---

### WD1 — Case study hero

```
┌────────────────────────────────────────────────────────────────────────────┐
│  [Concept project]                                                         │
│  Westside Auto Care                                                        │
│  Auto repair · Demonstration project                                       │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                     [full-width hero screenshot]                     │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

---

### WD2 — Overview stats row

```
┌────────────────────────────────────────────────────────────────────────────┐
│   Industry        │   Focus              │   Built for                       │
│   Auto repair     │   Lead generation    │   Mobile + local SEO              │
└────────────────────────────────────────────────────────────────────────────┘
```

*No fake "% increase" metrics*

---

### WD3 — Challenge

2–3 paragraphs: outdated site, mobile failures, losing calls to competitors

---

### WD4 — Approach

What we prioritized: speed, click-to-call, service clarity, trust signals

---

### WD5 — Solution gallery

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ [homepage shot]  │  │ [mobile shot]    │  │ [services shot]  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

**Mobile:** Stacked images, swipe optional

---

### WD6 — Results (honest)

```
┌────────────────────────────────────────────────────────────────────────────┐
│  PROJECT GOALS                                                             │
│  · Increase phone calls from local search                                  │
│  · Professional presence that builds trust before the customer walks in    │
│  · Fast mobile experience for on-the-go searchers                          │
│                                                                            │
│  * Concept project — goals reflect design intent, not live client metrics. │
└────────────────────────────────────────────────────────────────────────────┘
```

---

### WD7 — CTA

```
┌────────────────────────────────────────────────────────────────────────────┐
│  Want results like this for your business?                                 │
│  [ Book a Free Discovery Call ]                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Page: About (`/about`)

**Page job:** Humanize Cyrus; build trust  
**H1:** We get local businesses.

---

### A1 — Hero

Compact hero with headline + subhead from strategy

---

### A2 — Founder story

```
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│  ┌─────────────────┐     Meet Cyrus                                        │
│  │                 │     ───────────                                        │
│  │   [ placeholder │     I started Groundwork Web because local shop       │
│  │     frame —     │     owners deserve better than broken templates       │
│  │     gray box,   │     and disappearing freelancers.                     │
│  │     no photo ]  │                                                       │
│  │                 │     [2–3 short paragraphs: service industry            │
│  │    Founder      │      understanding, custom-coded craft, long-term     │
│  └─────────────────┘      partner mindset — not day-job focused]          │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

| Breakpoint | Layout |
|------------|--------|
| Desktop | Photo left, text right (60/40) |
| Mobile | Placeholder frame top, text below |

**Placeholder spec:** `240×240px` min, `border` + `bg-elevated`, subtle user icon centered, optional "Founder" caption — **no stock image**

---

### A3 — Values (3 columns)

| Value | Copy direction |
|-------|----------------|
| **Reliability** | We show up. Your site stays up. |
| **Honesty** | We'll tell you if we're not the right fit. |
| **Craft** | Custom code, not cookie-cutter templates. |

---

### A4 — Differentiators

Short list: partner not freelancer · nationwide service · built for calls · we run it monthly

---

### A5 — CTA band

Dark band — Book a call

---

## Page: Contact (`/contact`)

**Page job:** Capture leads  
**H1:** Let's see if we're a fit.

**URL anchor:** `#form` for all site CTAs

---

### C1 — Hero

Compact — headline + subhead + expectations line

---

### C2 — Two-column layout (desktop)

```
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐ │
│  │  SEND A MESSAGE                 │  │  SCHEDULING                     │ │
│  │  ─────────────────              │  │  ──────────                     │ │
│  │  We'll respond within 24 hours. │  │  ┌───────────────────────────┐ │ │
│  │                                 │  │  │                           │ │ │
│  │  Name *        [____________]   │  │  │  Online scheduling        │ │ │
│  │  Phone *       [____________]   │  │  │  coming soon.             │ │ │
│  │  Business *    [____________]   │  │  │                           │ │ │
│  │  City, State * [____________]   │  │  │  Use the form and we'll   │ │ │
│  │  Industry *    [▼ dropdown ]   │  │  │  follow up to book a call.│ │ │
│  │  Message       [____________]   │  │  │                           │ │ │
│  │                [____________]   │  │  └───────────────────────────┘ │ │
│  │                                 │  │                                 │ │
│  │  [ Send message ]               │  │  Or email us:                   │ │
│  │                                 │  │  hello@groundwork-web.com       │ │
│  └─────────────────────────────────┘  └─────────────────────────────────┘ │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

#### When `CALENDLY_URL` is set

Right column becomes Calendly inline embed; left column unchanged.

#### Mobile

Form full width first; scheduling block below; email as `mailto:` link

---

### C3 — Form fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Name | text | yes | |
| Phone | tel | yes | `inputmode="tel"` |
| Business name | text | yes | |
| City, State | text | yes | Supports nationwide |
| Industry | select | yes | Auto · HVAC · Roofing · Electrical · Landscaping · Other |
| Message | textarea | no | 4 rows max |

**Submit states:** loading spinner on button · success message inline · validation errors per field

**Success message:** "Thanks — we'll be in touch within 24 hours to schedule your call."

---

### C4 — Form interaction flow

```
[Submit] → validate client-side → POST /contact → success UI
                              └→ error toast if failed
```

---

## Page: 404

```
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│                         404                                                │
│                   This page doesn't exist.                                   │
│                                                                            │
│              The link may be broken or the page was moved.                   │
│                                                                            │
│              [ Go to homepage ]    [ Book a call ]                           │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

**Psychology:** Don't dead-end — recover to conversion path  
**Layout:** Centered, minimal, same header/footer as site

---

## Interaction specification (global)

### Sticky header

| Trigger | Change |
|---------|--------|
| `scrollY > 80` | Add solid background, border-bottom, compress optional |
| Always | CTA button remains visible |

### Scroll animations (GSAP ScrollTrigger)

| Element | Animation | Reduced motion |
|---------|-----------|----------------|
| Section headings | fade-up `y: 24 → 0`, opacity 0 → 1 | Instant show |
| Cards | stagger children 80ms | Instant show |
| Hero | on load only | Instant show |

**Duration:** 0.5–0.7s · **Easing:** `power2.out`

### Smooth scroll (Lenis)

- Enable desktop + mobile
- Disable when `prefers-reduced-motion: reduce`
- Anchor links (`#form`) scroll with offset for sticky header (`80px`)

### Focus management

- Skip link → `#main`
- Mobile menu: trap focus, Escape closes
- Accordion: arrow keys navigate

---

## Component inventory (for Phase 4)

Emerging reusable Blade/Vue components:

| Component | Used on |
|-----------|---------|
| `site-header` | All pages |
| `site-footer` | All pages |
| `button-primary` | Global |
| `button-secondary` | Text links |
| `section-wrapper` | All sections |
| `section-eyebrow` | Section labels |
| `proof-bar` | Hero |
| `industry-card` | Home who-we-help |
| `pain-card` | Home problem |
| `bento-card` | Home system, Services |
| `process-step` | Home process |
| `comparison-table` | Home why-custom, Services |
| `project-card` | Work grid, Home preview |
| `concept-badge` | Work, case study |
| `faq-accordion` | Home, Services |
| `cta-band-dark` | Home, Services, About, case study |
| `pricing-card` | Services |
| `contact-form` | Contact |
| `scheduling-placeholder` | Contact |
| `founder-placeholder` | About |
| `case-study-gallery` | Work detail |
| `page-hero` | Inner pages (variants: full, compact) |

---

## Responsive summary

| Page | Mobile priority |
|------|-----------------|
| Home | Hero CTA above mockup; stacked sections |
| Services | Pricing cards stacked; comparison scroll |
| Work | Single column grid |
| Case study | Full-width images |
| About | Placeholder → text stack |
| Contact | Form first |
| 404 | Stacked buttons |

**Touch targets:** minimum `44×44px` on all interactive elements

---

## Wireframe approval checklist

- [x] Global header + footer wireframed
- [x] Home — all 10 sections
- [x] Services — all 6 sections
- [x] Work — grid + placeholder CTA card
- [x] Work detail — case study full flow
- [x] About — founder placeholder + story + values
- [x] Contact — form primary + Calendly placeholder
- [x] 404 — recovery CTAs
- [x] Interactions documented (sticky, scroll, accordion, form)
- [x] Component inventory for Phase 4
- [x] Mobile + desktop notes per major section

---

## Phase 3 → Phase 4 handoff

`04-design-system.md` will tokenize:

- Exact border radius (pill vs 8px)
- Component state styles from **G3**
- Spacing tokens from **G4**
- Color tokens from strategy
- Geist type scale with exact px/rem values

---

**Gate status:** ✅ Ready for Phase 4 — pending your review

Say **"start phase 4"** to build the design system, or **"start building"** if you want to skip to Laravel implementation (not recommended — design system first).
