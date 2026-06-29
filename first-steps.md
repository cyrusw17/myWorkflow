# First Steps — Launch & Founding Partner Offer

> **Goal:** Go live, capture leads, close the first 3 founding clients.  
> **Phase:** 2 → 3 transition (`priorities.md`)  
> **Last updated:** 2026-06-25

Work top to bottom. Don't run ads until **Phase 1** is done.

---

## The offer (lock this in)

**Name:** Founding Partner Program  
**Spots:** 3 total — then standard pricing returns

| What they get | What you get |
|---------------|--------------|
| Custom 5-page website — **$0 setup** (normally $2,500+) | Real portfolio + case study |
| Hosting, maintenance, updates — **$199/mo** | Recurring revenue from month 1 |
| Mobile-first, built for phone calls | Testimonial within 30 days of launch |
| | Permission to feature their business publicly |

**Non-negotiable terms:**
- [ ] **12-month minimum** at $199/mo
- [ ] **Fixed scope:** 5 pages, 1 design round, 2 revision rounds, launch
- [ ] **Testimonial + case study** required (in writing before kickoff)
- [ ] **Stagger starts** — don't sign client #3 until client #1 is near launch
- [ ] After 3 spots: **$2,500 setup + $199/mo** (standard pricing)

**One-liner for outreach:**
> I'm taking 3 founding partners for local shops — full custom site, no setup fee, $199/mo for hosting and maintenance with a 12-month partnership. I need a testimonial and case study in exchange. [X] spots left.

---

## Phase 1 — Go live (do this first)

### Domain & email
- [ ] Register **groundwork-web.com**
- [ ] Set up **hello@groundwork-web.com** (Google Workspace, Zoho, or host email)
- [ ] Point DNS to hosting provider

### Publish the site
- [ ] Deploy **`mvp-website/public/`** — see `mvp-website/README.md`
- [ ] `APP_URL=https://groundwork-web.com`
- [ ] `APP_DEBUG=false`
- [ ] SSL / HTTPS working
- [ ] Smoke test all pages: Home, Services, Work, About, Contact

### Forms & lead flow
- [ ] Configure SMTP in production `.env`
- [ ] Set `MAIL_LEAD_TO=hello@groundwork-web.com`
- [ ] Submit test lead → confirm **database row** + **email in inbox**
- [ ] Confirm you get notifications on your phone (forwarding or mobile email)
- [ ] Set up Calendly (or keep form-only until ready) — update `CALENDLY_URL` in `.env`

### Trust basics (before sending strangers to the site)
- [ ] Replace founder photo placeholder on About (or use a clean headshot — doesn't need to be pro)
- [ ] Proofread copy on Home + Contact
- [ ] Westside case study clearly labeled **Concept project**

**Exit criteria:** You can paste `https://groundwork-web.com` in a text without apologizing. Form works. Email works.

---

## Phase 2 — Founding Partner landing page

- [ ] Create dedicated page: `/founding-partners` (or `/offer`)
- [ ] Page includes:
  - [ ] Headline: Founding Partner Program — 3 spots
  - [ ] What's included (site + $199/mo plan)
  - [ ] What's required (12-month term, testimonial, case study)
  - [ ] Fixed scope summary (5 pages, revision limits)
  - [ ] Spots remaining counter (manual update: "2 of 3 left")
  - [ ] CTA → Contact form with `?offer=founding-partner` or hidden field
- [ ] Add link in site footer or nav (optional: small banner on Home)
- [ ] Test form submission tags offer correctly in lead email/DB

**Exit criteria:** One URL you can send in DMs and ads that explains the full offer.

---

## Phase 3 — Outreach (start before ads)

Do this in parallel with Phase 2 if the main site is live. **Conversations beat ads for client #1.**

### Week 1 targets
- [ ] **10 outreach touches** (shops, warm network, Google Maps prospects)
- [ ] **5 follow-ups** on any prior conversations
- [ ] Use founding partner offer in every pitch

### Assets to prepare
- [ ] Short outreach script (DM / text / email) — see below
- [ ] One-pager or tablet-ready link: `groundwork-web.com` + `/founding-partners`
- [ ] Prospect list in `outreach/prospects.md` (create when ready)

### Outreach script (starter)
```
Hey [Name] — I'm Cyrus with Groundwork Web. I build websites for local shops 
and handle all the hosting/maintenance so owners don't have to think about it.

I'm opening 3 founding partner spots — full custom site, no setup fee, 
$199/mo with a 12-month partnership. I need a testimonial and case study 
in exchange. [X] spots left.

Worth a 15-min call this week? [link to /founding-partners or /contact]
```

**Exit criteria:** At least 3 discovery calls booked from outreach (not ads).

---

## Phase 4 — Ad creatives (small test only)

**Prerequisite:** Phase 1 complete. Phase 2 landing page live. You can take calls this week.

### Strategy
- [ ] **Budget:** $50–150 total test (not more until you get a lead or learn why not)
- [ ] **Audience:** Local service businesses — start with **auto shops OR trades**, one metro area
- [ ] **Goal:** Learn (cost per lead, which headline works) — not "3 clients in 7 days"
- [ ] **Landing page:** `/founding-partners` — not the homepage

### Creatives checklist
- [ ] **3 headline variants** (test one at a time or A/B if platform allows)
  - "Local shop owners — 3 founding partner spots"
  - "Custom website. $0 setup. $199/mo. 3 spots left."
  - "Stop losing calls to a bad website — founding partner offer"
- [ ] **2 image sizes** (if Meta): 1080×1080 feed + 1080×1920 story
- [ ] **Primary text** — short, matches landing page offer exactly
- [ ] **CTA button:** Learn More → founding partners page
- [ ] UTM tags on ad links (`?utm_source=meta&utm_campaign=founding-partners`)

### Before you hit publish on ads
- [ ] Phone/email ready for replies within 24 hours
- [ ] Calendar open for discovery calls
- [ ] Simple tracker: spend, clicks, leads, calls booked

**Exit criteria:** One ad set live, $50 spent, results logged. Pause and iterate — don't scale a loser.

---

## Phase 5 — Close founding clients

When someone responds (from outreach or ads):

- [ ] Discovery call (30 min) — diagnose, don't oversell
- [ ] Send simple agreement: scope, $199/mo, 12-month minimum, testimonial clause
- [ ] Collect deposit or first month before kickoff (recommended: **first month upfront**)
- [ ] Create `clients/[business-name]/intake.md`
- [ ] Update spots remaining on landing page
- [ ] Deliver → launch → collect testimonial → publish case study

**Exit criteria:** 1 paying founding client live. Then push for #2 and #3.

---

## What NOT to do

- Run ads before the site and form work on production
- Offer "free" without 12-month minimum or scope limits
- Sign all 3 clients in the same week while working full-time
- Spend $500 on ads before 10 organic outreach attempts
- Keep redesigning the site instead of deploying

---

## Revenue snapshot (realistic)

| Milestone | MRR |
|-----------|-----|
| 1 founding client | $199/mo |
| 3 founding clients | $597/mo |
| After program: 1 standard client ($2,500 setup + $199/mo) | $199/mo + setup cash |

Proof of work in month 1 matters more than maxing MRR.

---

## Related docs

| Doc | Use for |
|-----|---------|
| `priorities.md` | Big-picture phases |
| `business-profile.md` | Positioning, niche, pitch |
| `operations.md` | Weekly rhythm, sales flow |
| `website/docs/09-launch-checklist.md` | Technical deploy checklist |

---

## Current focus (today)

**Single action:** Register **groundwork-web.com** and deploy the site with a working contact form.
