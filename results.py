import numpy as np
import matplotlib.pyplot as plt


def summarize_results(results, interventions):
    """Summarize results into a table with mean quality and matches with 95% CI, and efficiency"""
    summary = {}

    for intervention in interventions:
        key = intervention if intervention is not None else "baseline"

        qualities = [r[f"{key}_quality"] for r in results]
        match_rates = [r[f"{key}_match_rate"] for r in results]
        efficiencies = [
            r[f"{key}_quality"] / r["assortative_quality"]
            for r in results
        ]

        def compute_stats(values):
            mean = np.mean(values)
            sem = np.std(values, ddof=1) / np.sqrt(len(values))
            ci_low = mean - 1.96 * sem
            ci_high = mean + 1.96 * sem
            return mean, ci_low, ci_high

        q_mean, q_low, q_high = compute_stats(qualities)
        mr_mean, mr_low, mr_high = compute_stats(match_rates)
        e_mean, e_low, e_high = compute_stats(efficiencies)

        summary[key] = {
            "quality_mean": q_mean,
            "quality_ci": (q_low, q_high),
            "match_rate_mean": mr_mean,
            "match_rate_ci": (mr_low, mr_high),
            "efficiency_mean": e_mean,
            "efficiency_ci": (e_low, e_high),
        }

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

        mr_mean = stats["match_rate_mean"]
        mr_low, mr_high = stats["match_rate_ci"]

        e_mean = stats["efficiency_mean"]
        e_low, e_high = stats["efficiency_ci"]

        quality_str = f"{q_mean:.3f} [{q_low:.3f}, {q_high:.3f}]"
        match_rate_str = f"{mr_mean:.3f} [{mr_low:.3f}, {mr_high:.3f}]"
        eff_str = f"{e_mean:.3f} [{e_low:.3f}, {e_high:.3f}]"

        print(f"{key:<15} {quality_str:<25} {match_rate_str:<25} {eff_str:<25}")

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

    y_min_plot = 0
    y_max_plot = max(means) + 0.05
    ticks = np.arange(y_min_plot, y_max_plot + 0.1, 0.1)
    plt.yticks(ticks)
    plt.ylim(y_min_plot, y_max_plot)

    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.show()
