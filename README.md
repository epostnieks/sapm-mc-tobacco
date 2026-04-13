# SAPM Monte Carlo — Tobacco / Addiction Ratchet Theorem

**Public replication repository for the quantitative results in:**

> Postnieks, E. (2026). *The Addiction Ratchet: Why the Tobacco Industry Cannot
> Be Reformed Without Replacing It.* SAPM Working Paper No. 37. SSRN.

This repository contains everything a researcher needs to independently
reproduce, audit, and extend the Monte Carlo simulation underlying the paper's
core quantitative claims. The paper itself is available on SSRN.

---

## Results (N = 100,000 draws, seed = 42)

| Statistic | Value |
|-----------|-------|
| **β_W median** | **6.50** |
| β_W mean | 6.71 |
| β_W std | 1.57 |
| **90% CI** | **[4.5, 9.6]** |
| 99% CI | [4.0, 11.3] |
| P(β_W < 1) | 0.0000% |
| P(β_W < floor=3.6) | 0.282% |
| **ΔW median** | **$6,276B/yr** |
| Π (revenue) | $965B/yr |
| Π^SA median | −$5,311B/yr |

β_W = 6.50 means the tobacco industry destroys **$6.50 in system welfare for
every $1.00 it captures in revenue** — after accounting for uncertainty across
all six welfare channels and 100,000 Monte Carlo draws.

---

## What Is β_W?

The System Welfare Accounting and Proof Model (SAPM) measures the ratio:

```
β_W = ΔW / Π
```

where:
- **ΔW** = total annualized welfare destruction ($B/yr), summed across all channels
- **Π** = annual industry revenue ($B/yr) — *not profit*

A β_W > 1 means the industry destroys more welfare than it generates in private
revenue. A β_W > 3 triggers the "Strong Intractability" classification. Tobacco
at β_W = 6.5 is classified as a **Class 1 Impossibility**: the constraint is
biochemical (nicotine addiction + combustion chemistry), not institutional.

---

## Quick Start

```bash
# Clone
git clone https://github.com/epostnieks/sapm-mc-tobacco.git
cd sapm-mc-tobacco

# Install dependencies (standard scientific Python)
pip install numpy scipy

# Run simulation
python mc_simulation.py

# Verify output
python -c "
import json
r = json.load(open('mc_results.json'))
print(f'β_W median: {r[\"beta_w\"][\"median\"]}')  # should be 6.5
print(f'ΔW: \${r[\"welfare_cost\"][\"total_median_B\"]:,.0f}B')  # should be $6,276B
print(f'CI: {r[\"beta_w\"][\"ci_90\"]}')  # should be [4.5, 9.6]
"
```

---

## Repository Contents

| File | Description |
|------|-------------|
| `mc_simulation.py` | Self-contained Monte Carlo simulation (all logic inline) |
| `mc_results.json` | Pre-run results (100K draws, seed=42) — bit-identical to paper |
| `mc_histogram.json` | Binned β_W distribution (80 bins) for companion chart |
| `assumptions.md` | Every parameter: value, justification, source |
| `data_sources.md` | Full citation list for all empirical inputs |
| `README.md` | This file |

---

## Six Welfare Channels

| Channel | Median ($B/yr) | 90% CI | Distribution |
|---------|---------------|--------|--------------|
| C1 — VSL mortality (8M deaths/yr) | $4,892B | [$3,068B, $7,786B] | Lognormal |
| C2 — Direct healthcare costs | $422B | [$378B, $466B] | Normal |
| C3 — Lost productivity | $446B | [$396B, $496B] | Normal |
| C4 — Secondhand smoke | $315B | [$261B, $380B] | Lognormal |
| C5 — Environmental | $40B | [$25B, $65B] | Lognormal |
| C6 — Governance capture | $150B | [$90B, $250B] | Lognormal |
| **Total ΔW** | **$6,276B** | **[$4,373B, $9,251B]** | Correlated (ρ=0.3) |

**C1 dominance note**: The VSL mortality channel accounts for ~78% of total
welfare cost. This reflects the 8 million annual deaths — not a modelling
choice. See `assumptions.md §C1` for full VSL methodology and `data_sources.md`
for WHO mortality citations.

---

## Impossibility Floor

The **biochemical impossibility floor** is β_W ≥ 3.6. Even in the minimum-harm
scenario (100% cessation uptake, full pharmacotherapy coverage), 8 years of
lag mortality from established cardiovascular disease and cancer means at minimum
~$3,470B in remaining annual welfare destruction. $3,470B / $965B = 3.59 ≈ 3.6.

In 100,000 draws, only **0.282%** fall below this floor — confirming the
impossibility classification is not a function of parameter choice.

---

## Sensitivity Analysis

The sensitivity matrix shows β_W under VSL multipliers (0.5×–1.5×) and
double-counting adjustments (0–40%):

| VSL mult | No DC adj | DC 20% | DC 40% |
|----------|-----------|--------|--------|
| 0.5× | 3.96 | 3.17 | 2.38 |
| **1.0× (central)** | **6.50** | **5.20** | **3.90** |
| 1.5× | 9.04 | 7.23 | 5.42 |

Even at 0.5× VSL and 40% double-counting adjustment, β_W = 2.38 — above the
industry's own claimed "positive contribution" threshold. The result is
directionally robust across the full sensitivity range.

---

## Replication Notes

**Exact replication**: Running `python mc_simulation.py` produces bit-identical
`mc_results.json` on any system with numpy ≥ 1.24 and scipy ≥ 1.10 (Python 3.9+).
The simulation uses `numpy.random.default_rng(seed=42)` — the modern Generator
API, which is reproducible across platforms (unlike the legacy `np.random.seed`).

**Version tested**:
```
numpy==1.26.4
scipy==1.12.0
Python 3.11.9
```

**If your results differ**: Check numpy/scipy versions. The lognormal quantile
function (`scipy.stats.lognorm.ppf`) has been stable across versions since 1.7,
but precision may vary at the 4th decimal place. The core results (median, 90%
CI to 1 decimal) should match exactly.

---

## The Addiction Ratchet Theorem

The paper proves that three structural axioms make the tobacco game a
Private Side-Taking (PST) game that cannot be converted to a non-PST game
through regulation:

**Axiom 1 — Neurochemical Lock-In**: Nicotine addiction creates a
neurochemical compulsion that structurally prevents preference reversal.
Consumers cannot "opt out" in the standard economic sense: the "deal" is
sustained by neurochemical enforcement, not preference.

**Axiom 2 — Pipeline Replacement**: A new generation of users is continuously
recruited to replace quitters and the deceased. Industry documents reveal
explicit recruitment targets for "replacement smokers" at ages 14–18.

**Axiom 3 — Fiscal Dependency**: Excise tax revenue creates government
co-dependence. In 2023, tobacco taxes generated $300B+ in government revenue
globally — creating a structural incentive for governments to maintain the
industry at a welfare-destroying scale.

**Impossibility conclusion**: All three axioms are structural — the first is
biochemical, the second is demographic, the third is fiscal. No regulatory
intervention can break all three simultaneously while the industry continues
to operate. This is a Class 1 Impossibility Theorem.

*Compare*: Alcohol (Class 2 Intractability — the Nordic retail monopoly model
has demonstrated 40% welfare reduction; βW = 24.96 but it CAN be reduced).
Tobacco's biochemistry creates a harder constraint than alcohol's social
game structure.

---

## Companion Site

Interactive visualization of these results:
https://tobacco-sapm-companion.vercel.app *(deployment pending)*

---

## License

CC BY 4.0. Cite as:

> Postnieks, E. (2026). *SAPM Monte Carlo — Tobacco (Addiction Ratchet
> Theorem)*. GitHub: epostnieks/sapm-mc-tobacco.
> https://github.com/epostnieks/sapm-mc-tobacco

---

## Issues / Challenges

Found a parameter error? A better data source? Open an issue. This repository
is maintained to ensure the simulation remains traceable to the best available
evidence. If WHO updates its mortality estimates or Euromonitor revises industry
revenue, the configuration will be updated with a new version tag and the
paper will note the revision.
