# Groundwork Web — Website Project Outline

> Master index for all website planning and build documents.  
> **Rule:** Complete phases in order. No code until Phase 3 wireframes are approved.  
> **Brief:** See `BUILD-PROMPT.md` for full creative and engineering standards.

---

## Brand lock

| Field | Value |
|-------|--------|
| **Company name** | Groundwork Web |
| **Domain** | groundwork-web.com |
| **Spoken name** | "Groundwork Web" (no hyphen) |
| **Tagline** | Builds and runs websites for local service businesses — more leads, zero tech hassle |
| **Positioning** | Technology growth partner, not a freelancer selling pages |
| **Primary CTA** | Book a discovery call |
| **Quality bar** | Premium agency — credible at $3k–$10k+ project fees |

---

## Workflow phases

```
Phase 1  Research & patterns     → docs/01-research-and-patterns.md
Phase 2  Website strategy        → docs/02-website-strategy.md
Phase 3  Wireframes              → docs/03-wireframes.md
Phase 4  Design system           → docs/04-design-system.md
Phase 5  Technical architecture  → docs/05-technical-architecture.md
Phase 6  Database schema         → docs/06-database-schema.md
Phase 7  SEO & conversion        → docs/07-seo-and-conversion.md
Phase 8  Implementation roadmap  → docs/08-implementation-roadmap.md
Phase 9  Development             → Laravel app in website/app/ (after docs approved)
Phase 10 Launch checklists       → docs/09-launch-checklist.md
```

**Gate:** Each phase must be reviewed before the next begins.

---

## Strategic decision (read before building)

Your brief targets an Awwwards-grade, full Laravel platform. That is the **correct long-term architecture** for Groundwork Web.

For **launch**, split into two slices so outreach is not blocked for months:

| Slice | Scope | Purpose |
|-------|--------|---------|
| **Launch (v1)** | Marketing site: Home, Services, Work, About, Contact + lead capture | Credibility for sales — ship in weeks |
| **Platform (v2)** | Admin, CRM, blog CMS, client portal, full DB | Recurring ops after first clients |

Document both in `08-implementation-roadmap.md`. Build v1 to v2-ready standards (clean Laravel structure, migrations stubbed) — do not over-build admin before first lead.

---

## Document index

### Phase 1 — Research & patterns

**File:** `docs/01-research-and-patterns.md`  
**Status:** ✅ Complete

| Section | Purpose |
|---------|---------|
| Reference sites studied | Awwwards, Stripe, Linear, premium agencies — what we learned |
| Layout patterns | Hero, social proof, service grids, CTA rhythm — and WHY they work |
| Typography trends | Scale, pairing, readability on mobile |
| Animation principles | GSAP/Lenis usage — guide attention, never distract |
| Color psychology | Trust, authority, trades-friendly premium (not startup neon) |
| Conversion patterns | CTA placement, objection handling, trust sequencing |
| Navigation patterns | Minimal nav, sticky CTA, mobile behavior |
| Anti-patterns to avoid | Generic agency clichés, fake social proof, stock overload |
| Extracted principles | Our rules — not copies of reference sites |

---

### Phase 2 — Website strategy

**File:** `docs/02-website-strategy.md`  
**Status:** ✅ Complete

| Section | Purpose |
|---------|---------|
| Target audience | Local service owners — automotive, trades, pros |
| Customer pain points | No site, bad site, no time, no ROI visibility |
| Desired emotions | Confidence, relief, trust, "these guys get it" |
| Conversion goal | Primary: booked discovery call. Secondary: contact form |
| Brand personality | Confident, minimal, premium, no-nonsense |
| Messaging hierarchy | Outcomes first (leads), deliverables second (site/hosting) |
| Site architecture | Pages, URLs, nav structure |
| Information hierarchy | What users see in first 5 seconds |
| Page list & purpose | Every page — why it exists |
| Section order (Home) | Hero → proof → services → process → CTA (rationale per section) |
| Content strategy | Tone, vocabulary shop owners understand |
| SEO strategy | Local + service keywords, schema plan |
| Accessibility strategy | WCAG AA targets |
| Performance strategy | Core Web Vitals budgets, asset policy |
| Objection handling map | Price, time, "I have a nephew who..." |

---

### Phase 3 — Wireframes

**File:** `docs/03-wireframes.md`  
**Status:** ✅ Complete

Low-fidelity wireframes for **every page, every section, every interaction**.

| Page | Sections to wireframe |
|------|----------------------|
| **Home** | Hero, trust bar, who we help, services overview, process, work preview, FAQ, final CTA |
| **Services** | Growth system breakdown (site, hosting, SEO, AI, maintenance) |
| **Work** | Portfolio / case study grid (spec projects OK at launch) |
| **About** | Story, why Groundwork Web, credibility |
| **Contact** | Form, Calendly embed, phone, expectations |
| **404** | Branded dead-end with CTA |

Per section document:

- Conversion purpose
- User psychology (what objection it removes)
- Primary and secondary actions
- Mobile vs desktop notes

---

### Phase 4 — Design system

**File:** `docs/04-design-system.md`  
**Status:** Not started

| Deliverable | Contents |
|-------------|----------|
| Color palette | Primary, neutral, accent, semantic (success/error) — hex + usage rules |
| Typography guide | Font families, scale (type ramp), weights, line heights |
| Spacing system | Base unit, section padding, component gaps |
| Component library | Buttons, cards, inputs, nav, footer, CTA blocks — states included |
| Animation system | Duration, easing, scroll behavior, reduced-motion fallbacks |
| Imagery direction | No stock clichés; photography/illustration rules |
| Iconography | Lucide set, sizing, when NOT to use icons |
| Dark/light mode | Decision + implementation rules (if applicable) |

---

### Phase 5 — Technical architecture

**File:** `docs/05-technical-architecture.md`  
**Status:** Not started

| Section | Contents |
|---------|----------|
| Stack summary | Laravel 11, PHP 8.3+, MySQL, Vite, Tailwind, Alpine, GSAP, Lenis |
| Folder structure | `app/`, `resources/`, `routes/`, `database/`, component organization |
| Laravel architecture | Controllers, services, form requests, policies |
| Frontend architecture | Blade components, JS modules, asset pipeline |
| API design | Contact/lead endpoints, validation, rate limits |
| Auth plan | Admin-only (v2) — scaffold early, implement later |
| Security | CSRF, CSP, sanitization, env secrets, session config |
| Caching & queues | What gets cached, mail queue for contact form |
| Third-party integrations | Calendly, analytics, email (PHPMailer/Laravel Mail) |
| Deployment target | Server requirements, env vars, SSL |

**Planned code root:** `website/app/` (Laravel project lives here when development starts)

---

### Phase 6 — Database schema

**File:** `docs/06-database-schema.md`  
**Status:** Not started

Normalized MySQL schema with migrations plan.

| Table | Purpose |
|-------|---------|
| `leads` | Contact form submissions, source, status |
| `clients` | Signed customers |
| `projects` | Active builds, URLs, status |
| `testimonials` | Quotes linked to clients/projects |
| `portfolio_items` | Work showcase entries |
| `blog_posts` | v2 content marketing |
| `users` | Admin authentication |

Include: ER diagram (mermaid), foreign keys, indexes, seed strategy for portfolio spec work.

---

### Phase 7 — SEO & conversion

**File:** `docs/07-seo-and-conversion.md`  
**Status:** Not started

| Section | Contents |
|---------|----------|
| Keyword map | Per-page primary + secondary keywords |
| Meta templates | Title/description formulas |
| Schema markup | LocalBusiness, Organization, Service, FAQ |
| Open Graph & Twitter | Image specs, per-page OG |
| Sitemap & robots | URL list, crawl rules |
| CRO plan | CTA copy, placement, A/B ideas post-launch |
| Trust elements | What proof we show at launch (no fake testimonials) |
| Analytics events | Form submit, CTA click, scroll depth |
| Core Web Vitals targets | LCP, INP, CLS budgets |

---

### Phase 8 — Implementation roadmap

**File:** `docs/08-implementation-roadmap.md`  
**Status:** Not started

| Section | Contents |
|---------|----------|
| v1 launch scope | Exact pages and features for first deploy |
| v2 platform scope | Admin, CRM, blog — after first client |
| Sprint breakdown | Week-by-week build order |
| Dependency order | Design system → components → pages → backend |
| Risk register | Scope creep, animation bloat, Laravel over-engineering |
| Testing checklist | Cross-browser, mobile, forms, a11y, performance |
| Deployment checklist | DNS, SSL, email, backups |
| Maintenance documentation | Update workflow, hosting |
| Future improvements | AI chat, client portal, review automation |

---

### Phase 9 — Launch & operations

**File:** `docs/09-launch-checklist.md`  
**Status:** Not started

Pre-launch verification:

- [ ] All pages live on groundwork-web.com
- [ ] SSL active
- [ ] Contact form delivers to hello@groundwork-web.com
- [ ] Calendly/booking flow works
- [ ] SEO meta + schema validated
- [ ] Lighthouse performance ≥ 90
- [ ] WCAG AA spot-check passed
- [ ] Mobile tested on real device
- [ ] Analytics installed
- [ ] 404 and error pages styled

---

### Phase 10 — Developer & admin docs (post-build)

**Files:** `docs/10-developer-guide.md`, `docs/11-admin-guide.md`  
**Status:** Not started — created after v1 code exists

---

## Sitemap (planned)

```
groundwork-web.com/
├── /                    Home — primary conversion page
├── /services            What we build + monthly growth plan
├── /work                Portfolio & case studies
├── /about               Who we are, why trust us
├── /contact             Form + book a call
└── /blog                (v2) SEO content
```

**Admin (v2):** `/admin` — leads, clients, portfolio CMS

---

## Homepage section order (draft — finalize in Phase 2)

| # | Section | Conversion job |
|---|---------|------------------|
| 1 | Hero | Instant clarity: who we help + primary CTA |
| 2 | Trust indicators | Credibility in 3 seconds (stats, logos, or process) |
| 3 | Who we serve | Automotive, trades, local pros — visitor self-selects |
| 4 | The growth system | Site + hosting + SEO + maintenance — not "a website" |
| 5 | Selected work | Proof we deliver premium results |
| 6 | Process | Reduce fear — what working together looks like |
| 7 | FAQ | Kill objections (price, time, DIY alternatives) |
| 8 | Final CTA | Book discovery call — low friction |

---

## Repository structure (target)

```
website/
├── BUILD-PROMPT.md              ← Master brief (done)
├── PROJECT-OUTLINE.md             ← This file (done)
├── docs/
│   ├── 01-research-and-patterns.md
│   ├── 02-website-strategy.md
│   ├── 03-wireframes.md
│   ├── 04-design-system.md
│   ├── 05-technical-architecture.md
│   ├── 06-database-schema.md
│   ├── 07-seo-and-conversion.md
│   ├── 08-implementation-roadmap.md
│   ├── 09-launch-checklist.md
│   ├── 10-developer-guide.md      (after build)
│   └── 11-admin-guide.md          (after build)
└── app/                           ← Laravel project (Phase 9 — not started)
```

---

## Current status

| Phase | Document | Status |
|-------|----------|--------|
| — | BUILD-PROMPT.md | ✅ Done |
| — | PROJECT-OUTLINE.md | ✅ Done |
| 1 | 01-research-and-patterns.md | ✅ Done |
| 2 | 02-website-strategy.md | ✅ Done |
| 3 | 03-wireframes.md | ✅ Done |
| 4 | 04-design-system.md | ✅ Done |
| 5 | 05-technical-architecture.md | ✅ Done |
| 6 | 06-database-schema.md | ✅ Done |
| 7 | 07-seo-and-conversion.md | ✅ Done |
| 8 | 08-implementation-roadmap.md | ✅ Done |
| 9 | 09-launch-checklist.md | ✅ Done |
| 10 | 10-developer-guide.md | ✅ Done |
| — | **Laravel app** (`app/`) | ✅ Built — run `composer install` |

---

## Next action

**Start Phase 1:** Create `docs/01-research-and-patterns.md` — research premium agency and SaaS sites, extract principles (no copying), document patterns with rationale.

Say **"start phase 1"** when ready and we will write the research doc before any code.
