# How We Work

> Operating rhythm for this business. Keeps execution consistent while you have a day job.

---

## Weekly rhythm

You have limited time. Protect it with a fixed cadence instead of working randomly.

| Day | Focus | Time block |
|-----|--------|------------|
| **Mon** | Outreach — send messages, follow up | 1–2 hrs |
| **Tue** | Build — website or client work | 1–2 hrs |
| **Wed** | Outreach — calls, visits, DMs | 1–2 hrs |
| **Thu** | Build — website or client work | 1–2 hrs |
| **Fri** | Admin + review — metrics, plan next week | 30–60 min |
| **Sat** (optional) | Catch-up build or outreach burst | 2–3 hrs |
| **Sun** | Off — or 30 min planning only | — |

Adjust to your real schedule. The point is **outreach and build alternate**, not random task switching.

---

## Decision rules (daily)

Before starting any task, run the MOS decision framework:

1. Does this increase recurring revenue?
2. Is this aligned with current phase in `priorities.md`?
3. Is this execution or procrastination?
4. Is there a simpler solution?
5. Highest ROI for today's limited time?
6. What evidence supports this?

If it fails #2 or #3, stop and do the current phase item instead.

---

## How we use this folder

```
Business/
├── knowledge-base/                  # AI source of truth — start here
│   ├── master-prompt.md             # Copy-paste onboarding for any AI
│   └── 01–05 *.md                   # Mission, offer, priorities, tech, changelog
├── .cursor/rules/
│   ├── core-context.mdc             # AI Master OS — always on
│   └── knowledge-base.mdc           # Instructs AI to read KB first
├── business-profile.md              # Who we are, niche, offer, name
├── priorities.md                    # Phased roadmap + checkboxes
├── first-steps.md                   # Launch todo + Founding Partner offer
├── mvp-website/                     # Founding client one-page landing (deploy public/)
├── operations.md                    # This file — rhythm and process
├── website/                         # Full Laravel agency site (not live yet)
├── outreach/                        # Templates, prospect lists (Phase 3)
├── clients/                         # One folder per client (Phase 4+)
└── sops/                            # Repeatable processes (Phase 5+)
```

Create subfolders when you reach that phase. Don't build empty structure upfront.

---

## Project intake (future clients)

When a prospect says yes, capture:

1. Business name, owner name, phone
2. What they do and who their customers are
3. Current website (if any) and what's wrong with it
4. Goal: more calls, bookings, etc.
5. Budget comfort (setup + monthly)
6. Timeline

Store in `clients/[business-name]/intake.md`.

---

## Sales conversation flow

1. **Discover**: What's broken? What does a good month look like?
2. **Diagnose**: Show their site (or lack of one) vs what good looks like
3. **Offer**: Setup + monthly plan — sell the outcome, not the tech
4. **Close**: Clear next step — deposit, kickoff call, start date
5. **Follow up**: If no answer in 3 days, one more touch. Then move on.

---

## Anti-patterns (watch for these)

| Trap | Redirect to |
|------|----------------|
| Researching business names for 2 weeks | Pick from shortlist in 48 hours |
| Rebuilding site for the 4th time | Ship MVP, iterate after outreach feedback |
| Learning new framework | Use current stack |
| "I'll outreach when the site is perfect" | Start conversations in Week 1–2 |
| New side project idea | Back to `priorities.md` current phase |

---

## Weekly review (Fridays, 15 min)

Answer these in a note or chat:

1. What phase am I in? Did I advance it?
2. How many outreach conversations this week?
3. What's blocking the next checkbox in `priorities.md`?
4. One thing to do Monday that moves revenue closest.

---

## How AI should help in this workspace

- **Read `knowledge-base/` first** (see `.cursor/rules/knowledge-base.mdc`)
- Reference `core-context.mdc`, `business-profile.md`, `priorities.md`, and `operations.md`
- Always state which phase a task belongs to
- Push back on work outside current phase
- Update KB + changelog when locked decisions change
- Suggest MOS/KB updates when patterns repeat (per Continuous Improvement Protocol)
- End coaching responses with **one concrete action for today**
