# Groundwork Web — Business Workspace

Cyrus's business operating system for **Groundwork Web** (groundwork-web.com).

## Start here

| Path | Purpose |
|------|---------|
| [`knowledge-base/README.md`](knowledge-base/README.md) | AI knowledge base index + quick facts |
| [`knowledge-base/master-prompt.md`](knowledge-base/master-prompt.md) | Master prompt for any AI assistant |
| [`priorities.md`](priorities.md) | Phased roadmap |
| [`first-steps.md`](first-steps.md) | Launch playbook |
| [`mvp-website/`](mvp-website/) | Live founding client landing page |

## Repos

| Repo | Purpose |
|------|---------|
| **myWorkflow** (this repo) | Full business workspace — docs, KB, MVP site, Laravel app |
| [offer1](https://github.com/cyrusw17/offer1) | cPanel deploy source for production MVP site only |

## Deploy live site

Production deploys from **offer1**, not this repo. After MVP changes:

```bash
cd mvp-website
git push origin main   # if using offer1 remote on mvp-website
```

Or sync mvp-website changes to offer1 separately. See `mvp-website/docs/deploy-groundwork-web.com.md`.
