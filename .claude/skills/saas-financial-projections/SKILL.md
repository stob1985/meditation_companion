---
name: saas-financial-projections
description: Build SaaS financial projections, revenue models, unit economics analyses, and exit valuations. Use this skill when the user asks for financial projections, revenue forecasting, MRR/ARR modeling, SaaS metrics (LTV, CAC, churn, NRR, Rule of 40), scenario planning, exit valuation, or investor-ready financial models.
---

# SaaS Financial Projections

Act as a senior SaaS CFO. Build financial models that are honest, benchmark-grounded, and formatted for investor conversations as well as internal planning. Always show your formulas and assumptions explicitly so the user can challenge them.

Before modeling, gather the inputs you need. Minimum viable inputs: current MRR (or ARR), monthly growth rate, monthly churn rate, ARPU. Better models also use: CAC, gross margin, expansion revenue, monthly burn, headcount costs. Ask only for what is missing; never invent the user's numbers.

## Step 1: Current state baseline

Calculate and present the core metric set from the user's inputs:

| Metric | Formula |
|---|---|
| ARR | MRR × 12 |
| Annual growth rate | (1 + monthly growth)^12 − 1 |
| ARPU | MRR / active customers |
| LTV | ARPU × gross margin % / monthly churn rate |
| LTV:CAC | LTV / CAC (healthy: ≥3:1) |
| CAC payback (months) | CAC / (ARPU × gross margin %) (healthy: ≤12) |
| Gross revenue retention | 1 − gross churn (annualized) |
| Net revenue retention (NRR) | (starting MRR + expansion − contraction − churn) / starting MRR |
| Burn multiple | net burn / net new ARR (great: <1, good: 1–1.5, bad: >2) |
| Magic number | net new ARR in quarter / S&M spend in prior quarter (good: >0.75) |
| Rule of 40 | YoY growth % + FCF (or EBITDA) margin % (good: ≥40) |

Flag any metric that is outside healthy range and say why it matters.

## Step 2: Revenue projection

Default: bottom-up monthly model over 36–60 months.

```
MRR(t+1) = MRR(t) + new MRR(t) + expansion MRR(t) − churned MRR(t)
```

- New MRR: new customers × ARPU. Model new customer acquisition from the user's actual channel data if available; otherwise apply the stated growth rate with a decay factor (growth rates compress as base grows — do not compound a flat 8%/mo for 5 years without flagging it as aggressive).
- Expansion MRR: expansion rate × base MRR (typical: 0.5–2%/mo for products with upgrade paths).
- Churned MRR: churn rate × base MRR.

If the user has cohort data, prefer a cohort-based projection: each monthly cohort retains independently using the observed retention curve, which is more accurate than blended churn.

Present the projection as a year-by-year summary table (MRR, ARR, customers, growth %) with the monthly model available on request or as a CSV.

## Step 3: Three-scenario framework

Always produce three scenarios:

| Scenario | Growth multiplier | Churn multiplier |
|---|---|---|
| Conservative | 0.7× | 1.3× |
| Base | 1.0× | 1.0× |
| Optimistic | 1.4× | 0.7× |

Show ending ARR for each scenario at years 1, 3, and 5, and state the implied assumptions in plain language (e.g., "Optimistic assumes churn improves from 3% to 2.1%/mo — typically requires moving upmarket or major retention work").

## Step 4: Exit valuation

Use three methods and present a range, not a single number:

1. **Revenue multiple**: ARR × multiple (see benchmarks below).
2. **EBITDA multiple**: relevant only if profitable; typical private SaaS 10–15× EBITDA.
3. **DCF**: project free cash flows 5 years + terminal value, discount at 25–40% for private SaaS (higher discount for earlier stage).

### 2025–2026 revenue multiple benchmarks

| Category | Multiple range |
|---|---|
| Public SaaS median | 6–7× revenue |
| Private bootstrapped | 4–5× ARR (4.8× median) |
| Private VC-backed | 5–6× ARR (5.3× median) |
| High growth (>40% YoY) | 7–10× ARR |
| NRR >120% | 11–12× ARR |
| Small/declining (<$1M ARR or <10% growth) | 2–4× ARR |

Adjust the multiple up or down based on: growth rate, NRR, gross margin (target ≥75%), Rule of 40 score, revenue concentration, and founder dependence. State each adjustment explicitly.

## Output format

Structure the final deliverable as:

1. **Executive summary** — current state in 3 bullets, headline projection, valuation range.
2. **Baseline metrics table** with health flags.
3. **Projection table** (3 scenarios × years 1/3/5).
4. **Valuation analysis** with the three methods and the reasoning for the chosen multiple.
5. **Key risks and sensitivities** — which assumption moves the model most (usually churn).

Offer to export the monthly model as CSV or build it into a spreadsheet if the user wants to iterate on assumptions.
