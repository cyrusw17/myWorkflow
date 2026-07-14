# AI Agent — Agentic Trading Research & Execution

**Owner intent:** Build an AI agent that can eventually trade via Robinhood (agentic trading), starting with **strategy selection** — not live capital.

## Phase 0 (current): Strategy bake-off vs SPY

Before any brokerage wiring, the agent must scientifically compare:

| # | Strategy | Style | Horizon |
|---|----------|-------|---------|
| **1** | Residual Momentum | Classic quant / factor | Multi-day to weeks |
| **2** | Liquidity Sweep Continuation (LSC) | SMC / ICT day-trade | Intraday (1H/4H → 5m) |

Both strategies are benchmarked against **SPY** (buy-and-hold and risk-adjusted SPY proxies). Winner → Phase 1 paper trading → Phase 2 Robinhood execution with hard risk caps.

## Use the master prompt

Open a new Cursor / Claude / Codex chat and paste:

→ [`prompts/MASTER_PROMPT_quant_agent.md`](prompts/MASTER_PROMPT_quant_agent.md)

That single prompt is the operating system for the agent: research protocol, strategy specs, metrics, kill criteria, and Robinhood-ready architecture later.

## Repo layout

```
ai-agent/
├── README.md
├── prompts/
│   └── MASTER_PROMPT_quant_agent.md   ← paste this into a new AI session
├── strategies/
│   ├── 01-residual-momentum.md
│   └── 02-liquidity-sweep-continuation.md
└── docs/
    └── research-protocol.md
```

## Target GitHub home

Intended home: **`github.com/cyrus2005/ai-agent`**

This copy currently lives under the Groundwork workflow repo until you create/push the standalone repo.

## Non-negotiables

1. **No live trading** until backtests + paper trade clear kill criteria.
2. **SPY is the null hypothesis** — if a strategy does not beat SPY on risk-adjusted terms, it dies.
3. **Operational definitions > vibes** — BOS, IFVG, SMT, liquidity sweeps must be coded as measurable rules.
4. **Risk first** — max daily loss, position size, and kill-switch before any order path exists.

## Status

- [x] Master quant prompt
- [x] Strategy 1 + Strategy 2 written specs
- [x] Research protocol (metrics, walk-forward, kill rules)
- [ ] Backtest scaffolding (code)
- [ ] Paper trade loop
- [ ] Robinhood execution adapter (last)
