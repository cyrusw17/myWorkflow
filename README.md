# AI Agent — Agentic Trading Research & Execution

> **Agent build prompt:** When an AI coding agent is pointed at this README, treat § Build Prompt below as the executable brief. Prefer the full spec in [`prompts/MASTER_PROMPT_quant_agent.md`](prompts/MASTER_PROMPT_quant_agent.md). Do Phase 0 first. Ship a **GitHub Pages** backtest viewer.

**Owner intent:** Build an AI agent that can eventually trade via Robinhood (agentic trading), starting with **strategy selection** — not live capital.

## Phase 0 (current): Strategy bake-off vs SPY

| # | Strategy | Style | Horizon |
|---|----------|-------|---------|
| **1** | Residual Momentum | Classic quant / factor | Multi-day to weeks |
| **2** | Liquidity Sweep Continuation (LSC) | SMC / ICT day-trade | Intraday (1H/4H → 5m; daily proxy OK until bars land) |

Both strategies are benchmarked against **SPY**. Winner → paper trading → Robinhood with hard risk caps.

## Build Prompt (execute this)

You are shipping a reproducible research lab + public results page.

1. **Compare** Residual Momentum vs LSC vs SPY using the locked specs in `strategies/` and `docs/research-protocol.md`.
2. **Implement** Python backtests under `src/` with one CLI: `python -m src.run_bakeoff`.
3. **Emit** `site/data/bakeoff.json` (equity curves + metrics + assumptions + decision status).
4. **Publish** a GitHub Pages dashboard from `site/` that visualizes the bake-off (curves, metrics table, costs, stale-data badge). Deploy via GitHub Actions on push to the default branch.
5. **Do not** wire live Robinhood orders in this phase.
6. If market data is unavailable, use cached CSV under `data/cache/` and still ship a working Pages site.

### GitHub Pages requirements

- Static only (HTML/CSS/JS). No server.
- Charts + metrics for Strat A, Strat B, SPY B&H, SPY vol-match.
- Mobile-readable.
- Document the live URL in this README once Pages is on.
- Expected URL pattern: `https://cyrusw17.github.io/myWorkflow/` (updates if the repo is renamed to `ai-agent`).

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.run_bakeoff
# open https://cyrusw17.github.io/myWorkflow/ (or /site/) after Actions deploy
# Labs: /ftmo-lab.html · /funded-lab.html · /rp-dual-lab.html (also under /site/)

```

## Repo layout

```
.
├── README.md                          ← this build prompt
├── prompts/MASTER_PROMPT_quant_agent.md
├── strategies/                        ← locked strategy specs
├── docs/                              ← research protocol + decision memo
├── src/                               ← backtest code
├── site/                              ← GitHub Pages dashboard
│   ├── index.html
│   └── data/bakeoff.json
└── .github/workflows/pages.yml
```

## GitHub

**https://github.com/cyrusw17/myWorkflow** (rename to `ai-agent` when ready)  
**Pages:** https://cyrusw17.github.io/myWorkflow/  
**Resume page:** https://cyrusw17.github.io/myWorkflow/resume/

## Non-negotiables

1. No live trading until backtests + paper clear kill criteria.
2. SPY is the null hypothesis.
3. Operational definitions > vibes.
4. Risk first.
5. Backtests must be viewable on GitHub Pages.

## Status

- [x] Master quant prompt (+ Pages requirement)
- [x] Strategy specs + research protocol
- [x] Backtest scaffolding + Pages dashboard
- [ ] Full walk-forward + filled decision memo
- [ ] Paper trade loop
- [ ] Robinhood execution adapter (last)
