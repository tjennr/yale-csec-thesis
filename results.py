import numpy as np
import matplotlib.pyplot as plt


def summarize_results(results, interventions, possible_matches):
    """Summarize results into a table with mean quality and matches with 95% CI, and efficiency"""
    summary = {}

    for intervention in interventions:
        key = intervention if intervention is not None else "baseline"
        
        qualities = [r[f"{key}_quality"] for r in results]
        efficiencies = [
            r[f"{key}_quality"] / r["assortative_quality"]
            for r in results
        ]

        match_counts = [r[f"{key}_match_count"] for r in results]
        match_rates = [m / possible_matches for m in match_counts]

        application_count = [r[f"{key}_application_count"] for r in results]
        congestion = [
            app_count / match_count if match_count > 0 else np.nan
            for app_count, match_count in zip(application_count, match_counts)
        ]

        def compute_stats(values):
            mean = np.mean(values)
            sem = np.std(values, ddof=1) / np.sqrt(len(values))
            ci_low = mean - 1.96 * sem
            ci_high = mean + 1.96 * sem
            return mean, ci_low, ci_high

        q_mean, q_low, q_high = compute_stats(qualities)
        m_mean, m_low, m_high = compute_stats(match_rates)
        e_mean, e_low, e_high = compute_stats(efficiencies)
        c_mean, c_low, c_high = compute_stats(congestion)

        summary[key] = {
            "quality_mean": q_mean,
            "quality_ci": (q_low, q_high),

            "match_rate_mean": m_mean,
            "match_rate_ci": (m_low, m_high),

            "efficiency_mean": e_mean,
            "efficiency_ci": (e_low, e_high),
            
            "congestion_mean": c_mean,
            "congestion_ci": (c_low, c_high),
        }

    baseline_congestion = summary["baseline"]["congestion_mean"]
    for key in summary:
        if key == "baseline":
            summary[key]["congestion_reduction"] = 0
        else:
            congestion_mean = summary[key]["congestion_mean"]
            summary[key]["congestion_reduction"] = (baseline_congestion - congestion_mean) / baseline_congestion

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

    header = f"{'Intervention':<15} {'Quality':<25} {'Match Rate':<25} {'Efficiency':<25}"
    print(header)
    print("-" * len(header))

    for key, stats in summary.items():
        if key == "assortative":
            continue

        q_mean = stats["quality_mean"]
        q_low, q_high = stats["quality_ci"]

        m_mean = stats["match_rate_mean"]
        m_low, m_high = stats["match_rate_ci"]

        e_mean = stats["efficiency_mean"]
        e_low, e_high = stats["efficiency_ci"]

        c_mean = stats["congestion_mean"]
        c_low, c_high = stats["congestion_ci"]
        c_red = stats["congestion_reduction"]

        quality_str = f"{q_mean:.3f} [{q_low:.3f}, {q_high:.3f}]"
        match_rate_str = f"{m_mean:.3f} [{m_low:.3f}, {m_high:.3f}]"
        eff_str = f"{e_mean:.3f} [{e_low:.3f}, {e_high:.3f}]"
        # cong_str = f"{c_mean:.2f} [{c_low:.2f}, {c_high:.2f}]"
        cong_change_str = f"{c_red:.2%}"

        print(f"{key:<15} {quality_str:<25} {match_rate_str:<25} {eff_str:<25} {cong_change_str:<15}")

    # Assortative benchmark
    a = summary["assortative"]
    a_mean = a["quality_mean"]
    a_low, a_high = a["quality_ci"]

    print("\nAssortative benchmark:")
    print(f"Quality: {a_mean:.3f} [{a_low:.3f}, {a_high:.3f}]\n")


def plot_bar(summary, interventions, metric, ylabel, title, filename):

    labels = []
    means = []
    errors = []
    colors = []

    for intervention in interventions:
        key = intervention if intervention is not None else "baseline"

        stats = summary[key]
        mean = stats[f"{metric}_mean"]
        ci_low, ci_high = stats[f"{metric}_ci"]

        labels.append(key)
        means.append(mean)
        errors.append([mean - ci_low, ci_high - mean])

        if key == "baseline":
            colors.append("red")
        else:
            colors.append("steelblue")

    errors = np.array(errors).T
    x = np.arange(len(labels))

    plt.figure()
    plt.bar(x, means, yerr=errors, capsize=5, color=colors)

    plt.xticks(x, labels)
    plt.xlabel("Intervention")
    plt.ylabel(ylabel)
    plt.title(title)

    y_min_plot = min(0, min(means) - 0.1 * abs(min(means)))
    y_max_plot = max(means) + 0.1 * abs(max(means))
    plt.ylim(y_min_plot, y_max_plot)

    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.show()
