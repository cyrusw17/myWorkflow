# Groundwork Web — Knowledge Base

> **Version:** 1.0  
> **Last updated:** 2026-06-28  
> **Owner:** Cyrus  
> **Purpose:** Single source of truth for AI assistants working in this workspace.

---

## How to use this knowledge base

**AI assistants (Cursor and others):** Before answering business, strategy, outreach, or technical questions in this workspace, read the relevant files below. Treat this knowledge base as **higher priority than general assumptions** unless Cyrus gives new instructions in the current chat.

**Cyrus:** Update these files when strategy, offer, deploy setup, or priorities change. Bump the version in this README.

---

## File index

| File | Read when… |
|------|------------|
| [`master-prompt.md`](master-prompt.md) | Starting a new AI chat; onboarding any assistant to Cyrus + Groundwork Web |
| [`01-founder-and-mission.md`](01-founder-and-mission.md) | Coaching, decisions, values, long-term vision, communication style |
| [`02-offer-sales-and-positioning.md`](02-offer-sales-and-positioning.md) | Offer terms, pricing, pitch, niche, sales flow, outreach |
| [`03-priorities-and-operations.md`](03-priorities-and-operations.md) | What phase we're in, weekly rhythm, what NOT to do |
| [`04-technical-mvp-and-deploy.md`](04-technical-mvp-and-deploy.md) | MVP site, Git, cPanel, DNS, forms, production troubleshooting |
| [`05-decisions-and-changelog.md`](05-decisions-and-changelog.md) | Locked decisions, naming, history, what changed and why |

---

## Quick facts (always true unless updated)

| Item | Value |
|------|--------|
| **Business name** | Groundwork Web |
| **Domain** | https://groundwork-web.com |
| **Email** | hello@groundwork-web.com |
| **Founder** | Cyrus — Workflow Manager at Discount Tire |
| **Live site** | `mvp-website/` → deployed to cPanel `public_html` |
| **Workspace repo** | https://github.com/cyrusw17/myWorkflow.git |
| **Production deploy repo** | https://github.com/cyrusw17/offer1.git |
| **Current offer** | Founding Client Program — **2 of 3 spots open**, $0 setup, $199/mo, 12-month min |
| **Primary CTA** | Application form (not Calendly / book-a-call) |
| **North star** | First 3 founding clients → path to $10k/mo before leaving day job |
| **Full agency site** | `website/app/` (Laravel) — **not** what's live in production |

---

## Related workspace docs (also authoritative)

| Path | Role |
|------|------|
| `business-profile.md` | Brand, niche, positioning |
| `priorities.md` | Phased roadmap + checkboxes |
| `first-steps.md` | Launch playbook + offer checklist |
| `operations.md` | Weekly rhythm, sales flow |
| `.cursor/rules/core-context.mdc` | Always-on AI operating rules |
| `mvp-website/config/site.php` | Live landing page copy + offer numbers |

When KB and another doc conflict, prefer **`mvp-website/config/site.php`** for live offer copy and **`05-decisions-and-changelog.md`** for locked decisions.

---

## Continuous improvement

When a pattern repeats or a major decision is made, update the relevant KB file and add a line to `05-decisions-and-changelog.md`. Propose updates to `master-prompt.md` and `core-context.mdc` when strategy shifts materially.
