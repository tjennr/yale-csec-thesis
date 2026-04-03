import numpy as np
import matplotlib.pyplot as plt


def summarize_results(results, interventions):
    """Summarize results into a table with mean quality and matches with 95% CI, and efficiency"""
    summary = {}

    for intervention in interventions:
        key = intervention if intervention is not None else "baseline"

        qualities = [r[f"{key}_quality"] for r in results]
        matches = [r[f"{key}_matches"] for r in results]
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
        m_mean, m_low, m_high = compute_stats(matches)
        e_mean, e_low, e_high = compute_stats(efficiencies)

        summary[key] = {
            "quality_mean": q_mean,
            "quality_ci": (q_low, q_high),
            "matches_mean": m_mean,
            "matches_ci": (m_low, m_high),
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

    header = f"{'Intervention':<15} {'Quality':<25} {'Matches':<25} {'Efficiency':<25}"
    print(header)
    print("-" * len(header))

    for key, stats in summary.items():
        if key == "assortative":
            continue

        q_mean = stats["quality_mean"]
        q_low, q_high = stats["quality_ci"]

        m_mean = stats["matches_mean"]
        m_low, m_high = stats["matches_ci"]

        e_mean = stats["efficiency_mean"]
        e_low, e_high = stats["efficiency_ci"]

        quality_str = f"{q_mean:.3f} [{q_low:.3f}, {q_high:.3f}]"
        matches_str = f"{m_mean:.1f} [{m_low:.1f}, {m_high:.1f}]"
        eff_str = f"{e_mean:.3f} [{e_low:.3f}, {e_high:.3f}]"

        print(f"{key:<15} {quality_str:<25} {matches_str:<25} {eff_str:<25}")

    # Assortative benchmark
    a = summary["assortative"]
    a_mean = a["quality_mean"]
    a_low, a_high = a["quality_ci"]

    print("\nAssortative benchmark:")
    print(f"Quality: {a_mean:.3f} [{a_low:.3f}, {a_high:.3f}]\n")


def plot_efficiency_bar(summary, interventions):

    labels = []
    means = []
    errors = []

    for intervention in interventions:
        key = intervention if intervention is not None else "baseline"

        stats = summary[key]
        mean = stats["efficiency_mean"]
        ci_low, ci_high = stats["efficiency_ci"]

        labels.append(key)
        means.append(mean)
        errors.append([mean - ci_low, ci_high - mean])

    errors = np.array(errors).T

    x = np.arange(len(labels))

    plt.figure()
    plt.bar(x, means, yerr=errors, capsize=5)

    plt.xticks(x, labels)
    plt.xlabel("Intervention")
    plt.ylabel("Match Efficiency")
    plt.title("Match Efficiency by Intervention (95% CI)")

    y_min_plot = 0
    y_max_plot = max(means) + 0.05
    ticks = np.arange(y_min_plot, y_max_plot + 0.1, 0.1)
    plt.yticks(ticks)
    plt.ylim(y_min_plot, y_max_plot)

    plt.tight_layout()
    plt.savefig("efficiency_bar_chart.png", dpi=300)
    plt.show()







def summarize_segments(results, interventions, bin_width=0.1):
    n_bins = int(1 / bin_width)
    segment_summary = {}

    for intervention in interventions:
        key = intervention if intervention is not None else "baseline"

        # Initialize aggregates
        agg_workers = [
            {"count": 0, "matched": 0, "salary_sum": 0}
            for _ in range(n_bins)
        ]
        agg_firms = [
            {"count": 0, "filled": 0, "quality_sum": 0}
            for _ in range(n_bins)
        ]

        # Aggregate across simulations
        for r in results:
            seg = r[f"{key}_segments"]

            for b in range(n_bins):
                for k in agg_workers[b]:
                    agg_workers[b][k] += seg["workers"][b][k]
                for k in agg_firms[b]:
                    agg_firms[b][k] += seg["firms"][b][k]

        # Convert to final metrics
        worker_outcomes = []
        for b in agg_workers:
            avg_salary = (
                b["salary_sum"] / b["matched"] if b["matched"] > 0 else 0
            )
            match_prob = b["matched"] / b["count"] if b["count"] > 0 else 0

            worker_outcomes.append({
                "avg_salary": avg_salary,
                "match_prob": match_prob,
            })

        firm_outcomes = []
        for b in agg_firms:
            avg_quality = (
                b["quality_sum"] / b["filled"] if b["filled"] > 0 else 0
            )
            fill_prob = b["filled"] / b["count"] if b["count"] > 0 else 0

            firm_outcomes.append({
                "avg_quality": avg_quality,
                "fill_prob": fill_prob,
            })

        segment_summary[key] = {
            "workers": worker_outcomes,
            "firms": firm_outcomes,
        }

    add_segment_deltas(segment_summary)

    return segment_summary


def add_segment_deltas(segment_summary):
    baseline = segment_summary["baseline"]
    for key in segment_summary:
        if key == "baseline":
            continue
        for side in ["workers", "firms"]:
            for b in range(len(segment_summary[key][side])):
                metrics = list(segment_summary[key][side][b].keys())  # FIX
                for metric in metrics:
                    segment_summary[key][side][b][f"delta_{metric}"] = (
                        segment_summary[key][side][b][metric]
                        - baseline[side][b][metric]
                    )


def print_segment_summary(segment_summary, bin_width=0.1):
    print("\n=== SEGMENTED RESULTS ===\n")

    n_bins = int(1 / bin_width)

    for key, data in segment_summary.items():
        print(f"\n--- {key.upper()} ---")

        print("\nWorkers:")
        header = (
            f"{'Bin':<10}"
            f"{'Avg Sal':<12}{'Δ Sal':<12}"
            f"{'Match P':<12}{'Δ Match':<12}"
        )
        print(header)
        print("-" * len(header))

        for i in range(n_bins):
            b = data["workers"][i]

            bin_label = f"{i*bin_width:.1f}-{(i+1)*bin_width:.1f}"

            avg_sal = b.get("avg_salary", 0)
            d_sal = b.get("delta_avg_salary", 0)
            mp = b.get("match_prob", 0)
            d_mp = b.get("delta_match_prob", 0)

            print(f"{bin_label:<10}{avg_sal:<12.3f}{d_sal:<12.3f}{mp:<12.3f}{d_mp:<12.3f}")

        print("\nFirms:")
        header = (
            f"{'Bin':<10}"
            f"{'Avg Qual':<12}{'Δ Qual':<12}"
            f"{'Fill P':<12}{'Δ Fill':<12}"
        )
        print(header)
        print("-" * len(header))

        for i in range(n_bins):
            b = data["firms"][i]

            bin_label = f"{i*bin_width:.1f}-{(i+1)*bin_width:.1f}"

            avg_q = b.get("avg_quality", 0)
            d_q = b.get("delta_avg_quality", 0)
            fp = b.get("fill_prob", 0)
            d_fp = b.get("delta_fill_prob", 0)

            print(f"{bin_label:<10}{avg_q:<12.3f}{d_q:<12.3f}{fp:<12.3f}{d_fp:<12.3f}")
