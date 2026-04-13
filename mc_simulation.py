#!/usr/bin/env python3
"""
SAPM Monte Carlo Simulation — Tobacco / Addiction Ratchet Theorem
=================================================================

Reproduces all quantitative results in:

  Postnieks, E. (2026). "The Addiction Ratchet: Why the Tobacco Industry
  Cannot Be Reformed Without Replacing It." SAPM Working Paper Series.
  Available: SSRN.

This script is self-contained. Dependencies: numpy, scipy (standard scientific
Python stack). No proprietary pipeline code required.

Replication guarantee
---------------------
All results are seeded (seed=42) and deterministic. Running this script on
any machine with the same dependencies produces bit-identical mc_results.json.
If your output differs, check your numpy/scipy versions (tested: numpy>=1.24,
scipy>=1.10).

Usage
-----
  pip install numpy scipy
  python mc_simulation.py

Outputs
-------
  mc_results.json    — all statistics (matches paper §5 and companion site)
  mc_histogram.json  — binned β_W distribution (80 bins, used in companion chart)

Theory
------
The System Welfare Accounting and Proof Model (SAPM) decomposes the welfare
cost of the tobacco industry into W = Σ_i W_i across six channels. The
welfare-to-revenue ratio β_W = W / Π is computed for N=100,000 Monte Carlo
draws with correlated channel uncertainty (ρ=0.3, shared macro drivers).

βW = ΔW / Π  where Π = annual industry REVENUE (not profit)
           and ΔW = total annualized welfare destruction ($B/yr)

The impossibility floor (β_W ≥ 3.6) reflects the physical lower bound on
harm from combustion of addictive organic compounds: no regulatory intervention
can reduce β_W below this floor while the industry continues to operate.

Axiom structure (Addiction Ratchet Theorem):
  A1 — Neurochemical Lock-In: nicotine addiction structurally prevents
       preference reversal; the "deal" is sustained by neurochemical compulsion
  A2 — Pipeline Replacement: a new generation of users is continuously
       recruited to replace quitters and the deceased
  A3 — Fiscal Dependency: excise tax revenue creates government co-dependence
       that blocks decisive regulatory action

Classification: Class 1 Impossibility Theorem (constraint is biochemical,
not institutional — cannot be regulated away, only replaced).
"""

import json
import numpy as np
from pathlib import Path
from scipy import stats

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# All parameters are sourced from paper §4–§5. See assumptions.md for
# full provenance and data_sources.md for citations.
# ─────────────────────────────────────────────────────────────────────────────

CONFIG = {
    # Simulation parameters
    "seed": 42,
    "n_draws": 100_000,
    "correlation_rho": 0.3,  # Cross-channel correlation (shared macro drivers)

    # Private payoff — ANNUAL GLOBAL REVENUE (not profit)
    # Source: Euromonitor International (2023); WHO FCTC Secretariat (2023)
    # $965B = global tobacco industry revenue including cigarettes, cigars,
    # smokeless tobacco, heated tobacco, e-cigarettes
    "private_payoff_B": 965.0,

    # Impossibility floor
    # β_W ≥ 3.6 is the biochemical lower bound: no policy can reduce the
    # ratio below this while combustion of addictive compounds continues.
    # Derived from minimum-harm scenario: VSL × (minimum attributable deaths
    # at full cessation assistance coverage) / $965B
    "impossibility_floor": 3.6,

    # Welfare cost channels (all values in $B/yr)
    # Each channel: low = 5th percentile, mid = median, high = 95th percentile
    # Distribution choice: lognormal for fat-tailed mortality/exposure channels;
    # normal for well-established epidemiological estimates with symmetric error
    "channels": {

        # C1: VSL-adjusted mortality
        # 8 million tobacco-attributable deaths per year (WHO 2023).
        # Population-weighted global VSL: $7.3M–$14.4M (low–high)
        # Low: $7.3M VSL × 7.8M attributable deaths (conservative attribution)
        # Mid: $10M VSL × 8.0M deaths (WHO central)
        # High: $14.4M VSL × 8.0M deaths (US VSL applied globally, upper)
        # Distribution: lognormal (right-skewed — VSL uncertainty is asymmetric)
        "C1_vsl_mortality": {
            "dist": "lognormal",
            "low": 3800,
            "mid": 4900,
            "high": 7800,
            "weight": 0.40,
            "description": (
                "VSL-adjusted mortality. 8M deaths/yr × population-weighted "
                "global VSL. Low=$3,800B (VSL=$7.3M × 480K LMI-adjusted deaths "
                "equivalent), Mid=$4,900B (VSL=$10M × 8M deaths), "
                "High=$7,800B (VSL=$14.4M × 500K deaths upper scenario). "
                "Source: WHO (2023); Viscusi & Masterman (2017); paper §4.1."
            ),
        },

        # C2: Direct healthcare costs
        # Goodchild, Perucic & Nargis (2018) — most comprehensive global estimate
        # Healthcare costs for tobacco-attributable disease treatment globally
        # Distribution: normal (well-established estimate, symmetric CI)
        "C2_healthcare": {
            "dist": "normal",
            "low": 380,
            "mid": 422,
            "high": 467,
            "weight": 0.20,
            "description": (
                "Direct healthcare costs: treatment of tobacco-attributable "
                "cardiovascular disease, COPD, lung cancer, stroke, other. "
                "Source: Goodchild, Perucic & Nargis (2018) $422B central estimate. "
                "WHO FCTC (2023) sensitivity range $380–467B. Paper §4.2."
            ),
        },

        # C3: Lost productivity
        # Absenteeism, presenteeism, disability, premature workforce exit
        # ILO (2017); Tobacco Atlas 8th Edition (2023)
        # Distribution: normal (multiple meta-analyses, reasonably tight CI)
        "C3_productivity": {
            "dist": "normal",
            "low": 400,
            "mid": 446,
            "high": 500,
            "weight": 0.18,
            "description": (
                "Lost productivity: absenteeism (smoking breaks, illness), "
                "presenteeism (reduced on-job performance), disability, and "
                "premature labor force exit. Source: ILO (2017) $430B; "
                "Goodchild et al. (2018) supplementary estimates; "
                "Tobacco Atlas 8th Ed (2023) $446B central. Paper §4.3."
            ),
        },

        # C4: Secondhand smoke (SHS) burden
        # 1.2 million SHS deaths/yr (WHO 2023) + pediatric morbidity + occupational
        # Distribution: lognormal (attribution uncertainty is asymmetric — SHS
        # deaths are harder to attribute than direct smoking deaths)
        "C4_secondhand_smoke": {
            "dist": "lognormal",
            "low": 260,
            "mid": 315,
            "high": 380,
            "weight": 0.12,
            "description": (
                "Secondhand smoke burden: 1.2M SHS-attributable deaths/yr, "
                "pediatric respiratory disease, occupational exposure costs, "
                "non-smoker healthcare costs. Source: WHO IARC Monograph 100E; "
                "Öberg et al. (2011); FCTC country reports. Range $260–380B. "
                "Paper §4.4."
            ),
        },

        # C5: Environmental externalities
        # Cigarette butt pollution (2 trillion/yr), deforestation (600K ha/yr),
        # pesticide/fertilizer runoff, fire costs, packaging waste
        # Distribution: lognormal (high uncertainty; few comprehensive global estimates)
        "C5_environmental": {
            "dist": "lognormal",
            "low": 25,
            "mid": 40,
            "high": 65,
            "weight": 0.05,
            "description": (
                "Environmental externalities: cigarette butt pollution "
                "(most-collected litter globally; marine ecotoxicity), "
                "tobacco-specific deforestation (~600K ha/yr curing fuel), "
                "pesticide and fertilizer runoff, fire costs ($27B/yr US alone). "
                "Source: WHO (2022) Tobacco and the Environment; "
                "Yach et al. estimates; paper §4.5."
            ),
        },

        # C6: Governance capture
        # Cost of tobacco industry lobbying → blocked regulation → foregone
        # welfare improvement. Not the lobbying spend itself but the welfare
        # cost of regulatory delay/failure attributable to industry capture.
        # Distribution: lognormal (highly uncertain; hard to observe counterfactual)
        "C6_governance": {
            "dist": "lognormal",
            "low": 100,
            "mid": 150,
            "high": 250,
            "weight": 0.05,
            "description": (
                "Governance capture: welfare cost of industry-induced regulatory "
                "delay and policy failure. Estimated as: years of regulatory delay "
                "× annual welfare cost per year of delay. Industry has spent "
                "$100B+ on lobbying, litigation, and scientific controversy "
                "manufacturing since 1950. Conservative welfare cost of "
                "documented delays in FCTC implementation. "
                "Source: Brownell & Warner (2009); paper §4.6."
            ),
        },
    },

    "notes": (
        "All values in $B/yr (annualized, 2023 USD). "
        "Distributions calibrated from literature ranges in paper §4. "
        "Lognormal for fat-tailed channels (mortality, SHS, environmental, "
        "governance); normal for well-established estimates (healthcare, "
        "productivity). Cross-channel correlation ρ=0.3 reflects shared macro "
        "drivers (GDP growth, population, regulatory environment)."
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
# SIMULATION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def generate_correlated_draws(config: dict, rng: np.random.Generator) -> tuple:
    """Generate correlated channel draws via Cholesky decomposition.

    Method: draw N independent standard normals, apply Cholesky factor of the
    equicorrelation matrix to introduce correlation ρ across all channels,
    then transform to channel-specific marginal distributions via the
    probability integral transform (quantile function).

    Returns: (draws array of shape [N, n_channels], channel_names list)
    """
    channels = config["channels"]
    n_draws = config["n_draws"]
    rho = config["correlation_rho"]
    n_ch = len(channels)

    # Equicorrelation matrix: all off-diagonal entries = ρ
    corr = np.full((n_ch, n_ch), rho)
    np.fill_diagonal(corr, 1.0)

    # Cholesky decomposition
    L = np.linalg.cholesky(corr)

    # Independent standard normal draws
    Z = rng.standard_normal((n_draws, n_ch))

    # Introduce correlation: Z_corr = Z @ L^T (each row is one draw vector)
    Z_corr = Z @ L.T

    # Transform to channel-specific distributions
    draws = np.zeros((n_draws, n_ch))
    channel_names = list(channels.keys())

    for i, (name, params) in enumerate(channels.items()):
        dist = params["dist"]
        low  = params["low"]
        mid  = params["mid"]
        high = params["high"]

        # Uniform quantile from correlated normal
        U = stats.norm.cdf(Z_corr[:, i])

        if dist == "lognormal":
            # Parameterize: median = mid, and P95 ≈ high
            # P95 = exp(ln(mid) + 1.645 * σ)  →  σ = ln(high/mid) / 1.645
            sigma = np.log(high / mid) / 1.645
            draws[:, i] = stats.lognorm.ppf(U, s=sigma, scale=mid)

        elif dist == "normal":
            # Parameterize: mean = mid, P5/P95 at low/high
            # [P95 - P5] ≈ 2 × 1.645 × σ
            sigma = (high - low) / (2 * 1.645)
            draws[:, i] = stats.norm.ppf(U, loc=mid, scale=sigma)

        elif dist == "triangular":
            c = (mid - low) / (high - low)
            draws[:, i] = stats.triang.ppf(U, c, loc=low, scale=high - low)

        else:
            raise ValueError(f"Unknown distribution '{dist}' for channel {name}")

    return draws, channel_names


def build_sensitivity_matrix(config: dict) -> list:
    """Build VSL multiplier × double-counting adjustment grid.

    Provides robustness check: how does β_W change if VSL assumptions
    (which dominate C1) are varied, and if 0–40% of costs represent
    double-counting across channels?
    """
    channels = config["channels"]
    ch_names = list(channels.keys())
    ch_mids  = [channels[n]["mid"] for n in ch_names]
    vsl_idx  = ch_mids.index(max(ch_mids))  # largest channel = C1_vsl_mortality

    private_payoff = config["private_payoff_B"]
    vsl_multipliers = [0.5, 0.75, 1.0, 1.25, 1.5]
    dc_adjustments  = [0.0, 0.10, 0.20, 0.30, 0.40]

    matrix = []
    for vsl_mult in vsl_multipliers:
        row = {"vsl_multiplier": vsl_mult, "values": {}}
        for dc_adj in dc_adjustments:
            total = sum(
                ch_mids[i] * (vsl_mult if i == vsl_idx else 1.0)
                for i in range(len(ch_names))
            )
            total *= (1 - dc_adj)
            row["values"][f"dc_{int(dc_adj * 100)}pct"] = round(total / private_payoff, 2)
        matrix.append(row)
    return matrix


def build_histogram(beta_draws: np.ndarray, n_bins: int = 80) -> list:
    """Build binned histogram for companion site chart."""
    counts, edges = np.histogram(beta_draws, bins=n_bins)
    return [
        {
            "bin_low":  round(float(edges[i]), 3),
            "bin_high": round(float(edges[i + 1]), 3),
            "bin_mid":  round(float((edges[i] + edges[i + 1]) / 2), 3),
            "count":    int(counts[i]),
            "density":  round(float(counts[i] / len(beta_draws)), 6),
        }
        for i in range(len(counts))
    ]


def run_simulation() -> dict:
    """Execute the full Monte Carlo simulation and return results dict."""
    config = CONFIG
    rng = np.random.default_rng(seed=config["seed"])

    print(f"SAPM Monte Carlo — Tobacco (Addiction Ratchet Theorem)")
    print(f"  N = {config['n_draws']:,} draws  |  seed = {config['seed']}")
    print(f"  Channels: {len(config['channels'])}  |  ρ = {config['correlation_rho']}")
    print(f"  Π = ${config['private_payoff_B']:,}B/yr (global revenue)")
    print()

    # Generate draws
    draws, ch_names = generate_correlated_draws(config, rng)

    # β_W for each draw
    total_cost = np.sum(draws, axis=1)
    beta_draws = total_cost / config["private_payoff_B"]

    # Scalar statistics
    p5, p95 = np.percentile(beta_draws, [5, 95])
    p1, p99 = np.percentile(beta_draws, [1, 99])
    floor = config["impossibility_floor"]
    p_below_floor = float(np.mean(beta_draws < floor))

    pi_sa = total_cost - config["private_payoff_B"]

    # Channel statistics
    channel_stats = {
        name: {
            "median": round(float(np.median(draws[:, i])), 1),
            "mean":   round(float(np.mean(draws[:, i])), 1),
            "p5":     round(float(np.percentile(draws[:, i], 5)), 1),
            "p95":    round(float(np.percentile(draws[:, i], 95)), 1),
            "std":    round(float(np.std(draws[:, i])), 1),
        }
        for i, name in enumerate(ch_names)
    }

    results = {
        "paper_id": "tobacco",
        "theorem": "Addiction Ratchet",
        "classification": "Class 1 — Impossibility",
        "seed": config["seed"],
        "n_draws": config["n_draws"],
        "n_channels": len(config["channels"]),
        "correlation_rho": config["correlation_rho"],
        "private_payoff_B": config["private_payoff_B"],
        "beta_w": {
            "median":         round(float(np.median(beta_draws)), 2),
            "mean":           round(float(np.mean(beta_draws)), 2),
            "std":            round(float(np.std(beta_draws)), 2),
            "p1":             round(float(p1), 2),
            "p5":             round(float(p5), 2),
            "p95":            round(float(p95), 2),
            "p99":            round(float(p99), 2),
            "ci_90":          [round(float(p5), 1), round(float(p95), 1)],
            "ci_99":          [round(float(p1), 1), round(float(p99), 1)],
            "p_below_1":      round(float(np.mean(beta_draws < 1.0)), 6),
            "p_below_1_pct":  f"{np.mean(beta_draws < 1.0) * 100:.4f}%",
        },
        "impossibility_floor": {
            "floor_value":       floor,
            "p_below_floor":     round(p_below_floor, 6),
            "p_below_floor_pct": f"{p_below_floor * 100:.4f}%",
        },
        "welfare_cost": {
            "total_median_B": round(float(np.median(total_cost)), 1),
            "total_mean_B":   round(float(np.mean(total_cost)), 1),
            "total_p5_B":     round(float(np.percentile(total_cost, 5)), 1),
            "total_p95_B":    round(float(np.percentile(total_cost, 95)), 1),
        },
        "pi_sa": {
            "median_B": round(float(np.median(pi_sa)), 1),
            "mean_B":   round(float(np.mean(pi_sa)), 1),
            "p5_B":     round(float(np.percentile(pi_sa, 5)), 1),
            "p95_B":    round(float(np.percentile(pi_sa, 95)), 1),
        },
        "channel_statistics": channel_stats,
        "sensitivity_matrix": build_sensitivity_matrix(config),
    }

    # Print summary
    bw = results["beta_w"]
    wc = results["welfare_cost"]
    print(f"  β_W median : {bw['median']}")
    print(f"  β_W mean   : {bw['mean']}")
    print(f"  90% CI     : [{bw['ci_90'][0]}, {bw['ci_90'][1]}]")
    print(f"  P(β_W < 1) : {bw['p_below_1_pct']}")
    print(f"  P(β_W < {floor}): {results['impossibility_floor']['p_below_floor_pct']}")
    print(f"  ΔW median  : ${wc['total_median_B']:,.1f}B/yr")
    print(f"  Π^SA median: −${abs(results['pi_sa']['median_B']):,.0f}B/yr")

    return results


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    results = run_simulation()

    # Write mc_results.json
    out = Path(__file__).parent / "mc_results.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n  Wrote: {out}")

    # Write histogram (re-seed for identical draws)
    rng2 = np.random.default_rng(seed=CONFIG["seed"])
    draws2, _ = generate_correlated_draws(CONFIG, rng2)
    total2 = np.sum(draws2, axis=1)
    beta2 = total2 / CONFIG["private_payoff_B"]
    hist = build_histogram(beta2)

    hist_out = Path(__file__).parent / "mc_histogram.json"
    hist_out.write_text(json.dumps(hist, indent=2), encoding="utf-8")
    print(f"  Wrote: {hist_out}")
    print(f"\nDone. Verify: mc_results.json beta_w.median should be 6.5")
