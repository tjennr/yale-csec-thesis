import numpy as np


def summarize_results(results, interventions):
    """Summarize results into a table with mean quality and matches with 95% CI, and efficiency"""
    summary = {}

    for intervention in interventions:
        key = intervention if intervention is not None else "baseline"

        qualities = [r[f"{key}_quality"] for r in results]
        matches = [r[f"{key}_matches"] for r in results]

        def compute_stats(values):
            mean = np.mean(values)
            sem = np.std(values, ddof=1) / np.sqrt(len(values))
            ci_low = mean - 1.96 * sem
            ci_high = mean + 1.96 * sem
            return mean, ci_low, ci_high

        q_mean, q_low, q_high = compute_stats(qualities)
        m_mean, m_low, m_high = compute_stats(matches)

        summary[key] = {
            "quality_mean": q_mean,
            "quality_ci": (q_low, q_high),
            "matches_mean": m_mean,
            "matches_ci": (m_low, m_high),
        }

    # Assortative
    assortative_vals = [r["assortative_quality"] for r in results]
    mean = np.mean(assortative_vals)
    sem = np.std(assortative_vals, ddof=1) / np.sqrt(len(assortative_vals))
    summary["assortative"] = {
        "quality_mean": mean,
        "quality_ci": (mean - 1.96 * sem, mean + 1.96 * sem),
    }

    add_efficiency(summary)

    return summary


def add_efficiency(summary):
    """Add match efficiency metrics to results table"""
    assortative_mean = summary["assortative"]["quality_mean"]
    for key in summary:
        if key == "assortative":
            continue
        summary[key]["efficiency"] = summary[key]["quality_mean"] / assortative_mean


def print_results_table(summary):
    """Print results table"""
    print("\n=== Simulation Results (mean with 95% CI) ===\n")

    header = f"{'Intervention':<15} {'Quality':<25} {'Matches':<25} {'Efficiency':<12}"
    print(header)
    print("-" * len(header))

    for key, stats in summary.items():
        if key == "assortative":
            continue

        q_mean = stats["quality_mean"]
        q_low, q_high = stats["quality_ci"]

        m_mean = stats["matches_mean"]
        m_low, m_high = stats["matches_ci"]

        eff = stats["efficiency"]

        quality_str = f"{q_mean:.3f} [{q_low:.3f}, {q_high:.3f}]"
        matches_str = f"{m_mean:.1f} [{m_low:.1f}, {m_high:.1f}]"

        print(f"{key:<15} {quality_str:<25} {matches_str:<25} {eff:.3f}")

    # Assortative benchmark
    a = summary["assortative"]
    a_mean = a["quality_mean"]
    a_low, a_high = a["quality_ci"]

    print("\nAssortative benchmark:")
    print(f"Quality: {a_mean:.3f} [{a_low:.3f}, {a_high:.3f}]\n")
