# cPanel deploy stuck — troubleshooting

## Symptom

**Deploy HEAD Commit** shows: *"The deployment that you triggered on … is in progress …"* and never finishes.

---

## Most common causes

### 1. Nested copy bug (fixed in `.cpanel.yml`)

Older deploy scripts used `cp -R config $APPROOT/config`. When `~/config` already exists, each deploy created `~/config/config/...` nested folders. After several deploys this can balloon disk usage and hang the deploy task.

**Fix:** Updated `.cpanel.yml` removes and recopies `config`, `lib`, `includes` cleanly each deploy.

### 2. Dirty git working tree on server

cPanel requires a **clean working tree** before deploy. Untracked or modified files in `~/repositories/offer1/` block deployment.

**Fix (Terminal in cPanel, if available):**
```bash
cd ~/repositories/offer1
git status
git reset --hard HEAD
git clean -fd
```

Do **not** delete `~/storage/` or `~/.env` — those live outside the repo.

### 3. Stuck deploy queue

A previous deploy may have crashed but left the UI in "in progress."

**Check logs (File Manager → Settings → Show Hidden Files):**
```
~/.cpanel/logs/vc_*_git_deploy.log
~/.cpanel/logs/user_task_runner.log
```

Look for the latest `vc_*_git_deploy.log` — the error is usually at the bottom.

### 4. Pull didn't finish before deploy

Always run in order:
1. **Update from Remote**
2. Wait until it completes
3. **Deploy HEAD Commit**

---

## Recovery steps (do in order)

1. **Wait 5 minutes** — sometimes it completes on slow shared hosting.
2. **Refresh** the Git Version Control page.
3. **Terminal** (if your plan has it):
   ```bash
   cd ~/repositories/offer1
   git fetch origin
   git reset --hard origin/main
   git clean -fd
   ```
4. **File Manager** — check for nested junk:
   - `~/config/config/` — if this exists, delete the inner nested folders or the whole `~/config` (deploy will recreate).
   - `~/lib/lib/`, `~/includes/includes/` — same.
5. **Update from Remote** → **Deploy HEAD Commit** again (after pulling latest with fixed `.cpanel.yml`).
6. If still stuck, **contact Namecheap support** and ask them to clear stuck Version Control deployment tasks for account `grouevbi`.

---

## Manual deploy (emergency fallback)

If Git deploy keeps failing, copy files manually via File Manager or FTP:

| From repo | To |
|-----------|-----|
| `public/*` | `~/public_html/` |
| `config/` | `~/config/` |
| `lib/` | `~/lib/` |
| `includes/` | `~/includes/` |

Ensure `~/storage/` is writable (775).

---

## Verify deploy worked

Visit https://groundwork-web.com and View Source. You should see:
- `app.css?v=5` (or newer)
- `sticky-bar`
- `Launch Partner Program`
- `sms:12708019780`

If you still see `app.css?v=2` or `Founding Client Program`, deploy did not apply.
