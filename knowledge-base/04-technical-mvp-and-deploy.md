# 04 — Technical: MVP Site & Deploy

> **Version:** 1.0 · **Last updated:** 2026-06-28

---

## What is live vs planned

| Project | Path | Status |
|---------|------|--------|
| **Founding landing page** | `mvp-website/` | **Production target** — deploy this |
| **Full agency site** | `website/app/` (Laravel) | Built locally; **not** deployed to groundwork-web.com |

The MVP is a **single-page PHP** conversion site. One goal: fill 3 founding client spots.

---

## MVP stack

- PHP 8.2+ (8.3 local)
- SQLite lead storage (`storage/leads.sqlite`) — MySQL-ready pattern
- HTML/CSS/JS — GSAP, Lenis, Lucide (CDN)
- Config-driven copy: `config/site.php`
- No framework — evolves to Laravel later

---

## Project structure

```
mvp-website/
├── config/site.php          # Offer, copy, FAQs, form options
├── includes/sections/       # Page sections (hero, offer, form, etc.)
├── lib/bootstrap.php        # Env + helpers
├── lib/LeadStore.php        # SQLite + migrations
├── public/                  # Web root
│   ├── index.php            # Form handler + page render
│   ├── css/app.css
│   └── js/app.js
├── storage/                 # leads.sqlite, leads.log (gitignored)
├── .cpanel.yml              # cPanel deploy tasks
└── .env                     # Local only (gitignored)
```

---

## Local development

**Herd (recommended):**
```bash
cd mvp-website/public
herd link groundwork-web --secure --update-env
```
→ https://groundwork-web.test

**PHP built-in:**
```bash
cd mvp-website/public && php -S 127.0.0.1:8080
```

---

## Git & GitHub

| | |
|---|---|
| **Workspace repo** | https://github.com/cyrusw17/myWorkflow.git — full Business folder |
| **Production deploy repo** | https://github.com/cyrusw17/offer1.git — cPanel pulls this for live site |
| **Branch** | `main` |
| **Local path** | `/Users/cyrus/Desktop/Business/` |

**Ship a change:**
```bash
cd mvp-website
git add .
git commit -m "Description"
git push origin main
```

**Security note:** Cyrus once pasted a GitHub PAT in chat — if not revoked, revoke immediately and use SSH or credential manager.

---

## cPanel production

| | |
|---|---|
| **Host** | Namecheap shared — `server313.web-hosting.com` |
| **Account** | `grouevbi` |
| **Git clone** | `/home/grouevbi/repositories/offer1/` |
| **Live web root** | `/home/grouevbi/public_html/` |
| **Domain** | groundwork-web.com |

### Deploy workflow

1. `git push origin main`
2. cPanel → **Git Version Control** → offer1
3. **Update from Remote**
4. **Deploy HEAD Commit**

### What `.cpanel.yml` deploys

| Destination | Files |
|-------------|-------|
| `~/public_html/` | `index.php`, `.htaccess`, `css/`, `js/`, `images/`, `robots.txt` |
| `~/config/` | Offer copy |
| `~/lib/` | Bootstrap + LeadStore |
| `~/includes/` | Sections |
| `~/storage/` | Writable (775) |
| `~/.env` | Created from `.env.example` if missing |

Also removes `parking-page.shtml` on deploy.

### Production `.env` (`/home/grouevbi/.env`)

```env
SITE_URL=https://groundwork-web.com
SITE_EMAIL=hello@groundwork-web.com
MAIL_TO=hello@groundwork-web.com
```

Run **AutoSSL** in cPanel after DNS works.

---

## DNS (Namecheap)

**Advanced DNS** — keep minimal:

| Type | Host | Value |
|------|------|-------|
| A | `@` | `66.29.141.224` |
| A | `www` | `66.29.141.224` |

**Do NOT use:** Dynamic DNS (wrong for static shared hosting IP), URL redirects that conflict with A records, parking page CNAMEs.

**Propagation issues:** Router/WiFi may cache stale DNS after first setup. Flush Mac DNS: `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`. Test on cellular vs WiFi.

**Verify globally:** https://www.whatsmydns.net/#A/groundwork-web.com

---

## Application form (current)

**Section ID:** `#apply`  
**Fields:** name, phone, email, business_name, location, industry, contact_method (radio), contact_time (select)  
**Storage:** `~/storage/leads.sqlite` + `~/storage/leads.log`  
**Email:** `@mail()` to `MAIL_TO` — configure SMTP if host mail unreliable

**LeadStore columns:** name, phone, email, business_name, location, industry, contact_method, contact_time, message, source, created_at

---

## Known technical fixes applied

1. **Hero invisible on load** — GSAP `.reveal` hid above-fold content until scroll; fixed in `app.js` (animate in-view elements immediately)
2. **`.cpanel.yml` parking page removal** — verify path is `$DEPLOYPATH/parking-page.shtml` (slash)
3. **Primary domain** — document root cannot change on Namecheap shared hosting; `public_html` is correct

---

## Troubleshooting

| Symptom | Likely cause |
|---------|--------------|
| Site can't be reached | Missing/wrong DNS A records |
| Namecheap parking page | DNS wrong or `parking-page.shtml` still in public_html |
| Dark page, header only | Old JS cached — deploy hero animation fix |
| Form submits but no email | `MAIL_TO` wrong or host mail not configured |
| Works on cellular, not WiFi | Local DNS cache |

---

## Checklist before ads

- [ ] HTTPS + padlock working
- [ ] hello@groundwork-web.com working
- [ ] Form test → SQLite row + inbox email
- [ ] Mobile test on real phone
- [ ] `spots_remaining` accurate in `config/site.php`

---

## Updating offer numbers

Edit `mvp-website/config/site.php` → push → cPanel deploy:

```php
'spots_remaining' => 2,  // decrement when a spot closes
```

---

## Related docs

- `mvp-website/README.md`
- `mvp-website/docs/deploy-groundwork-web.com.md`
- `mvp-website/docs/01-research.md`
- `mvp-website/docs/02-critique.md`
