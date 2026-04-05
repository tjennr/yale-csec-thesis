import time
import numpy as np
from collections import deque
from agents import generate_workers, generate_firms
from matching import match
from metrics import match_quality, assortative_match_quality, segment_market
from results import summarize_results, print_results_table, plot_bar
from segmented_market_results import summarize_segments, print_segment_summary


N_WORKERS = 200
M_FIRMS = 200
ROUNDS = 50

INTERVENTIONS = [
    None,
    "cap",
    "fee",
    "cover_letter",
    "assessment",
    "pref_signal",
]


def run_simulation():
    """Runs one simulation round and returns metrics"""

    # Generate agents
    firms = generate_firms(M_FIRMS)
    workers = generate_workers(N_WORKERS, firms)

    def reset_state():
        """Reset agent match state inbetween interventions"""
        workers["offers"] = [[] for _ in range(N_WORKERS)]
        workers["accepted"] = [None for _ in range(N_WORKERS)]

        firms["applicants"] = [[] for _ in range(M_FIRMS)]
        firms["ranked_applicants"] = [deque() for _ in range(M_FIRMS)]
        firms["filled"] = [None for _ in range(M_FIRMS)]
        firms["coa_money"] = np.full(M_FIRMS, 0)
        firms["coa_effort"] = np.full(M_FIRMS, 0)

    # Match -> compute results -> clean matchings
    results = {}
    for intervention in INTERVENTIONS:
        match(workers, firms, intervention)
        quality, match_rate = match_quality(workers, firms)
        segments = segment_market(workers, firms)
        key = intervention if intervention is not None else "baseline"
        results[f"{key}_quality"] = quality
        results[f"{key}_match_rate"] = match_rate
        results[f"{key}_segments"] = segments
        reset_state()
        
    results["assortative_quality"] = assortative_match_quality(workers, firms)

    return results


if __name__ == "__main__":

    start = time.time()
    results = []

    # Run simulations
    for _ in range(ROUNDS):
        result = run_simulation()
        results.append(result)

    # Results
    summary = summarize_results(results, INTERVENTIONS)
    segment_summary = summarize_segments(results, INTERVENTIONS)

    end = time.time()

    # Print metrics
    print(f"\nTime: {end - start:.2f}s")
    print_results_table(summary)
    # print_segment_summary(segment_summary)

    # Graphs
    plot_bar(
        summary, INTERVENTIONS,
        metric="efficiency",
        ylabel="Match Efficiency",
        title="Match Efficiency by Intervention (95% CI)",
        filename="efficiency_bar_chart.png"
    )

    plot_bar(
        summary, INTERVENTIONS,
        metric="match_rate",
        ylabel="Match Rate",
        title="Match Rate by Intervention (95% CI)",
        filename="match_rate_bar_chart.png"
    )
