# cPanel deployment — public_html

Production deploy target for **groundwork-web.com**:

```
/home/grouevbi/public_html/     ← live site (document root)
/home/grouevbi/repositories/offer1/   ← git clone (do not edit here for quick fixes)
```

See **`docs/deploy-groundwork-web.com.md`** for the full workflow.

## .cpanel.yml summary

On **Deploy HEAD Commit**, copies repo files to `public_html` and app dirs to `$HOME`.

Do not edit `public_html` by hand for permanent changes — edit locally, push to GitHub, redeploy.
