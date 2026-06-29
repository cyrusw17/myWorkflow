# 05 — Decisions & Changelog

> **Version:** 1.0 · **Last updated:** 2026-06-28  
> Locked decisions from conversations and build sessions. **Do not contradict without explicit new instruction from Cyrus.**

---

## Locked business decisions

| Decision | Choice | Date |
|----------|--------|------|
| Business name | **Groundwork Web** (was considering Groundwork Digital) | 2026-06-25 |
| Domain | **groundwork-web.com** | 2026-06-25 |
| Niche | Local service businesses — automotive/trades priority | 2026-06-25 |
| Service area | United States (nationwide) | 2026-06-25 |
| Positioning | Growth partner, not page seller | 2026-06-25 |
| Quit job | Not until ~$10k/mo consistent from web business | 2026-06-25 |

---

## Locked offer decisions

| Decision | Choice | Date |
|----------|--------|------|
| Program name (canonical) | **Founding Client Program** | 2026-06-25 |
| Total spots | 3 | 2026-06-25 |
| Spots remaining | **2** | 2026-06-28 |
| Founding setup | $0 (normally $2,500+) | 2026-06-25 |
| Monthly | $199/mo | 2026-06-25 |
| Minimum term | 12 months | 2026-06-25 |
| Client obligation | Testimonial + case study | 2026-06-25 |
| Post-program pricing | $2,500 setup + $199/mo | 2026-06-25 |
| Stagger starts | Don't sign #3 until #1 near launch | 2026-06-25 |

---

## Locked product / CTA decisions

| Decision | Choice | Date |
|----------|--------|------|
| Live site | `mvp-website/` one-page landing — **not** full Laravel site | 2026-06-28 |
| Primary CTA | **Application form** (#apply) | 2026-06-28 |
| Calendly | Removed from primary flow; optional env var unused for now | 2026-06-28 |
| Form fields | + contact_method (phone/text/email) + contact_time | 2026-06-28 |
| Westside Auto Care | Removed from mockup/examples | 2026-06-28 |
| Founder photo | Placeholder for now | 2026-06-25 |

---

## Locked technical decisions

| Decision | Choice | Date |
|----------|--------|------|
| GitHub repo | cyrusw17/offer1 | 2026-06-28 |
| Deploy target | cPanel `~/public_html/` via `.cpanel.yml` | 2026-06-28 |
| Hosting | Namecheap shared — server313, account grouevbi | 2026-06-28 |
| DNS | Namecheap Advanced DNS — A @ and www → 66.29.141.224 | 2026-06-28 |
| Local dev | Laravel Herd → groundwork-web.test | 2026-06-25 |
| Lead storage | SQLite on server (`~/storage/leads.sqlite`) | 2026-06-25 |

---

## Changelog

### 2026-06-28 — myWorkflow repo created
- Entire `Business/` folder pushed to https://github.com/cyrusw17/myWorkflow
- `mvp-website/.git` merged into parent repo (offer1 remains separate cPanel deploy target)
- Root `.gitignore` excludes `.env`, `vendor/`, secrets, runtime storage

### 2026-06-28 — Form-first CTA + knowledge base
- Replaced "book a call" CTAs with application form
- Added contact preference + best time fields
- Updated LeadStore schema (email, contact_method, contact_time)
- Fixed hero GSAP invisible-on-load bug
- Pushed to GitHub (`c3708af`)
- Created `knowledge-base/` and master prompt

### 2026-06-28 — DNS & deploy troubleshooting
- Root cause of site not loading: empty Namecheap Advanced DNS (later fixed with A records)
- WiFi/router DNS cache caused false "site down" after DNS was fixed
- Confirmed site live at 66.29.141.224 with valid SSL
- Dynamic DNS confirmed **not** applicable (static shared hosting IP)

### 2026-06-28 — cPanel deploy to public_html
- Primary domain cannot change document root on Namecheap shared hosting
- `.cpanel.yml` updated to deploy `public/*` → `$HOME/public_html/`
- Git workflow: push → Update from Remote → Deploy HEAD Commit

### 2026-06-28 — MVP critique pass
- Creative director self-critique: 10 weaknesses identified and fixed
- Spots messaging updated to 2/3 open
- Form simplified; mobile CTA added; mockup genericized

### 2026-06-25 — MVP build
- Created `mvp-website/` folder separate from full Laravel `website/app/`
- Founding Client Program landing page built
- Git initialized; connected to offer1 repo

### 2026-06-25 — Business foundation
- Created priorities.md, business-profile.md, operations.md, first-steps.md
- Cursor rule: AI Master Operating System (core-context.mdc)
- Name chosen: Groundwork Web

---

## Open items (not locked — still TODO)

- [ ] hello@groundwork-web.com email fully configured
- [ ] Production form email delivery verified end-to-end
- [ ] Founder photo replaced
- [ ] First outreach batch (10 touches)
- [ ] LLC vs sole prop decision
- [ ] Standard pricing validation after 3 founding clients
- [ ] Revoke/regenerate GitHub PAT if it was exposed in chat

---

## Terminology note

| Term used | Meaning |
|-----------|---------|
| Founding Client Program | Canonical — live on site |
| Founding Partner Program | Older docs (`first-steps.md`) — same offer |
| MVP website | `mvp-website/` landing page |
| Full site | `website/app/` Laravel agency site |

When updating copy, use **Founding Client Program** unless Cyrus says otherwise.
