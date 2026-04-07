import numpy as np
import matplotlib.pyplot as plt


def plot_bar_wholemarket(summary, interventions, metric, ylabel, title, filename):
    """
    Plot bar chart that compares each intervention on whole market level
    metric: applications_per_firm, match_rate, efficiency
    """
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


def plot_line_segment(segment_summary, interventions, side, metric, ylabel, title, filename, bin_width=0.1):
    """
    Plot line chart that compares each intervention on a segmented market level
    metric: applications_per_firm
    """
    n_bins = len(segment_summary["baseline"][side])
    x = np.array([i * bin_width + bin_width / 2 for i in range(n_bins)])

    plt.figure(figsize=(6, 5))

    for intervention in interventions:
        key = intervention if intervention is not None else "baseline"

        y = [segment_summary[key][side][i][metric] for i in range(n_bins)]

        if key == "baseline":
            plt.plot(x, y, marker='o', color='red', label=key.capitalize())
        else:
            plt.plot(x, y, marker='o', label=key.capitalize())

    plt.title(title)
    plt.xlabel("Worker Quality" if side == "workers" else "Firm Salary")
    plt.ylabel(ylabel)

    plt.xlim(0, 1)
    plt.xticks(np.arange(0, 1.01, 0.1))
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend()

    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.show()


def plot_line_segment_panel(segment_summary, interventions, metrics, ylabels, titles, filename, bin_width=0.1):
    """
    Plot line chart that compares each intervention on a segmented market level
    metrics: [("workers", "match_prob"), ("firms", "fill_prob")]
    """
    n_bins = len(segment_summary["baseline"][metrics[0][0]])
    x = np.array([i * bin_width + bin_width / 2 for i in range(n_bins)])

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True)

    for ax, (side, metric), ylabel, title in zip(axes, metrics, ylabels, titles):
        
        for intervention in interventions:
            key = intervention if intervention is not None else "baseline"

            y = [segment_summary[key][side][i][metric] for i in range(n_bins)]

            if key == "baseline":
                ax.plot(x, y, marker='o', color='red', label=key.capitalize())
            else:
                ax.plot(x, y, marker='o', label=key.capitalize())

        ax.set_title(title)
        ax.set_xlabel("Worker Quality" if side == "workers" else "Firm Salary")
        ax.set_ylabel(ylabel)
        ax.set_xlim(0, 1)
        ax.set_xticks(np.arange(0, 1.01, 0.1))
        ax.grid(True, linestyle='--', alpha=0.3)

    # Shared legend
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=len(interventions))

    plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.savefig(filename, dpi=300)
    plt.show()
