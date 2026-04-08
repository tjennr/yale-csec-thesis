import numpy as np
from main import simulate_market, N_WORKERS, M_FIRMS
from results_wholemarket import summarize_results
from data_visualization import plot_param_effect


def compute_plot_increasing_params():

    fee_values = np.linspace(0, 1.0, 21) # 0 to 1.0 in 0.05 increments
    fee_results = simulate_increasing_param("fee", fee_values)

    cap_values = np.arange(10, 110, 10)
    cap_results = simulate_increasing_param("cap", cap_values)

    x, y = extract_metric_over_param(fee_results, "fee", "efficiency")
    plot_param_effect(
        x, y,
        xlabel="Application Fee",
        ylabel="Efficiency",
        title="Efficiency vs Fee",
        filename="graphs/increasing_param/efficiency_vs_fee.png"
    )

    x, y = extract_metric_over_param(fee_results, "fee", "match_rate")
    plot_param_effect(
        x, y,
        xlabel="Application Fee",
        ylabel="Match Rate",
        title="Match Rate vs Fee",
        filename="graphs/increasing_param/match_rate_vs_fee.png"
    )

    x, y = extract_metric_over_param(cap_results, "cap", "efficiency")
    plot_param_effect(
        x, y,
        xlabel="Application Cap",
        ylabel="Efficiency",
        title="Efficiency vs Cap",
        filename="graphs/increasing_param/efficiency_vs_cap.png"
    )

    x, y = extract_metric_over_param(cap_results, "cap", "match_rate")
    plot_param_effect(
        x, y,
        xlabel="Application Cap",
        ylabel="Match Rate",
        title="Match Rate vs Cap",
        filename="graphs/increasing_param/match_rate_vs_cap.png"
    )


def simulate_increasing_param(param, values, rounds):
    """
    Run market simulations across a set of increasing values for a param
    param: fee, cap
    """

    all_results = {}

    for val in values:
        results = []

        # Runs ROUNDS of simulations for val
        for _ in range(rounds):
            res = simulate_market(
                interventions=[None, param],
                param=param,
                value=val
            )
            results.append(res)

        summary = summarize_results(results, [None, param], N_WORKERS, M_FIRMS)
        all_results[val] = summary

    return all_results


def extract_metric_over_param(all_results, intervention, metric):
    x, y = [], []

    for val in sorted(all_results.keys()):
        summary = all_results[val]
        x.append(val)
        y.append(summary[intervention][f"{metric}_mean"])

    return np.array(x), np.array(y)
