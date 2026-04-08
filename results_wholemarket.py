import numpy as np


def summarize_results(results, interventions, n_workers, m_firms):
    """Summarize results for match rate, quality, efficiency, apps/firm, and change in apps/firm"""
    summary = {}

    possible_matches = min(n_workers, m_firms)

    # Compute mean and 95% CI values across all simulations
    for intervention in interventions:
        key = intervention if intervention is not None else "baseline"

        # Match rate
        match_counts = [r[f"{key}_match_count"] for r in results]
        match_rates = [m / possible_matches for m in match_counts]
        
        # Quality
        qualities = [r[f"{key}_quality"] for r in results]

        # Efficiency
        efficiencies = [
            r[f"{key}_quality"] / r["assortative_quality"]
            for r in results
        ]

        # Applications per firm
        application_count = [r[f"{key}_application_count"] for r in results]
        apps_per_firm = [app_count / m_firms for app_count in application_count]

        def compute_stats(values):
            mean = np.mean(values)
            sem = np.std(values, ddof=1) / np.sqrt(len(values))
            ci_low = mean - 1.96 * sem
            ci_high = mean + 1.96 * sem
            return mean, ci_low, ci_high

        m_mean, m_low, m_high = compute_stats(match_rates)
        q_mean, q_low, q_high = compute_stats(qualities)
        e_mean, e_low, e_high = compute_stats(efficiencies)
        a_mean, a_low, a_high = compute_stats(apps_per_firm)

        summary[key] = {
            "match_rate_mean": m_mean,
            "match_rate_ci": (m_low, m_high),

            "quality_mean": q_mean,
            "quality_ci": (q_low, q_high),

            "efficiency_mean": e_mean,
            "efficiency_ci": (e_low, e_high),
            
            "applications_per_firm_mean": a_mean,
            "applications_per_firm_ci": (a_low, a_high),
        }

    baseline_apps_per_firm = summary["baseline"]["applications_per_firm_mean"]
    for key in summary:
        if key == "baseline":
            summary[key]["applications_per_firm_change"] = 0
        else:
            summary[key]["applications_per_firm_change"] = (
                summary[key]["applications_per_firm_mean"] - baseline_apps_per_firm
            ) / baseline_apps_per_firm

    # Assortative
    assortative_vals = [r["assortative_quality"] for r in results]
    mean = np.mean(assortative_vals)
    sem = np.std(assortative_vals, ddof=1) / np.sqrt(len(assortative_vals))
    summary["assortative"] = {
        "quality_mean": mean,
        "quality_ci": (mean - 1.96 * sem, mean + 1.96 * sem),
    }

    return summary


def print_results_table(summary):
    """Print results table"""
    print("\n=== Simulation Results (mean with 95% CI) ===\n")

    header = f"{'Intervention':<15} {'Match Rate':<25} {'Quality':<25} {'Efficiency':<25} {'Apps/Firm Δ':<15}"
    print(header)
    print("-" * len(header))

    for key, stats in summary.items():
        if key == "assortative":
            continue

        m_mean = stats["match_rate_mean"]
        m_low, m_high = stats["match_rate_ci"]

        q_mean = stats["quality_mean"]
        q_low, q_high = stats["quality_ci"]

        e_mean = stats["efficiency_mean"]
        e_low, e_high = stats["efficiency_ci"]

        a_mean = stats["applications_per_firm_mean"]
        a_low, a_high = stats["applications_per_firm_ci"]
        a_change = stats["applications_per_firm_change"]

        quality_str = f"{q_mean:.3f} [{q_low:.3f}, {q_high:.3f}]"
        match_rate_str = f"{m_mean:.3f} [{m_low:.3f}, {m_high:.3f}]"
        eff_str = f"{e_mean:.3f} [{e_low:.3f}, {e_high:.3f}]"
        # apps_str = f"{a_mean:.2f} [{a_low:.2f}, {a_high:.2f}]"
        apps_change_str = f"{a_change:.2%}"

        print(f"{key:<15} {match_rate_str:<25} {quality_str:<25} {eff_str:<25} {apps_change_str:<15}")

    # Assortative benchmark
    a = summary["assortative"]
    a_mean = a["quality_mean"]
    a_low, a_high = a["quality_ci"]

    print("\nAssortative benchmark:")
    print(f"Quality: {a_mean:.3f} [{a_low:.3f}, {a_high:.3f}]\n")
