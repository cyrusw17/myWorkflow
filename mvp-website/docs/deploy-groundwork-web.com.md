# Deploy groundwork-web.com

**Live web root:** `/home/grouevbi/public_html/`  
**Git source:** `/home/grouevbi/repositories/offer1/`  
**Domain:** https://groundwork-web.com

---

## How deployment works

```
GitHub (offer1)  →  cPanel pull  →  repositories/offer1/
                                 →  .cpanel.yml copies to public_html/
```

Every **Deploy HEAD Commit** syncs:

| To | Files |
|----|--------|
| `~/public_html/` | `index.php`, `.htaccess`, `css/`, `js/`, `images/`, `robots.txt` |
| `~/config/` | Offer copy, spots remaining, FAQs |
| `~/lib/` | PHP bootstrap + lead storage |
| `~/includes/` | Landing page sections |
| `~/storage/` | SQLite leads (writable) |
| `~/.env` | Created once from `.env.example` if missing |

Also removes `public_html/parking-page.shtml` on each deploy.

---

## Deploy now

**cPanel → Git Version Control → offer1**

1. **Update from Remote** (branch `main`)
2. **Deploy HEAD Commit**

---

## First-time server setup

Edit `~/.env` (home folder, show hidden files):

```env
SITE_URL=https://groundwork-web.com
SITE_EMAIL=hello@groundwork-web.com
MAIL_TO=hello@groundwork-web.com
CALENDLY_URL=
```

**SSL/TLS Status → Run AutoSSL** for `groundwork-web.com`

---

## Ship a change

```bash
cd /Users/cyrus/Desktop/Business/mvp-website
git add .
git commit -m "Your change"
git push origin main
```

Then cPanel: **Update from Remote → Deploy HEAD Commit**

---

## Verify

- [ ] https://groundwork-web.com shows the founding partner page
- [ ] Contact form saves to `~/storage/leads.sqlite`
- [ ] No parking page

---

## Change deploy path

Default is `$HOME/public_html/`. For a subfolder, edit `DEPLOYPATH` in `.cpanel.yml`:

```yaml
- export DEPLOYPATH=$HOME/public_html/subfolder/
```
