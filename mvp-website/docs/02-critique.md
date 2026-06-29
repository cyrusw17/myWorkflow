# Creative Director Critique — Founding Client Landing

> Self-review after v1 build. Weaknesses identified and addressed in v2.

---

## 10 weakest parts (v1)

### 1. No visual proof of craft
**Why weak:** A web agency landing with zero website imagery asks prospects to trust blind. The hero was a pricing card — indistinguishable from a SaaS billing widget.

**Fix:** Browser mockup with concept preview + price chip beneath. Shows *what you build*, not just what you charge.

### 2. No human trust anchor
**Why weak:** Anonymous agency = skepticism. Local shop owners hire people, not logos.

**Fix:** Founder card with avatar, name, and one-paragraph bio in the proof section.

### 3. Mobile CTA hidden in header
**Why weak:** Hiding `.header-cta` on mobile removed the primary conversion action from the most common viewport.

**Fix:** Compact header CTA kept on mobile + sticky bottom bar after scroll.

### 4. "What's included" was a flat checklist
**Why weak:** Eleven identical pills communicate quantity, not value. No hierarchy. Felt like a terms list, not a premium offer.

**Fix:** Three featured bento cards with icons + descriptions. Secondary items grouped under "Also included."

### 5. Redundant offer repetition
**Why weak:** Hero card, offer section, and final CTA all repeated the same pricing grid. Cognitive fatigue before the form.

**Fix:** Hero owns visual + price chip. Offer section keeps deep comparison. Trimmed how-it-works from 6 → 4 steps. Removed optional message field from form.

### 6. Lucide icons via late-loaded JS
**Why weak:** Checkmarks and icons invisible until JS runs — layout shift and cheap first paint.

**Fix:** CSS check icons and inline SVG data-URIs for featured cards. Removed Lucide dependency.

### 7. Missing OG / social image
**Why weak:** Ad and link shares would show blank previews — unprofessional for a creative business.

**Fix:** `public/images/og-image.svg` + meta tags in head.

### 8. Industry pill clutter
**Why weak:** Eleven tags looked like SEO stuffing, not design. Added noise below an already-long proof section.

**Fix:** Single readable line: "We work with: Automotive · HVAC · …"

### 9. Form friction too high
**Why weak:** Six fields including optional textarea for a "book a call" action. Every field loses ~5–10% of submissions.

**Fix:** Two-column rows on desktop, removed message field, added trust microcopy, honeypot spam field.

### 10. Weak accessibility on FAQ + navigation
**Why weak:** `display: none` panels, no skip link, no FAQ schema — hurts SEO and excludes keyboard users.

**Fix:** Skip link, `aria-controls`/`aria-expanded`, animated `max-height` panels, FAQ JSON-LD schema.

---

## Remaining limitations (honest)

- Founder photo still placeholder (initials avatar) — add real headshot before ads
- `mail()` may not work on all hosts — configure SMTP for production
- Concept preview labeled but still not a live client — acceptable for founding program
- Tailwind not in build pipeline — custom CSS chosen for no-Node deploy; migrate later

---

## v2 changelog

- Hero mockup + stats strip
- Founder trust card
- Mobile sticky CTA
- Included bento layout
- 4-step timeline
- OG image + FAQ schema
- Form simplification + honeypot
- CSS icons, no Lucide FOUC
- Section padding tightened
