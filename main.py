import time
import numpy as np
from collections import deque
from agents import generate_workers, generate_firms
from matching import match
from metrics import match_quality, assortative_match_quality, segment_market
from results_wholemarket import summarize_results, print_results_table
from results_segmentedmarket import summarize_segments, print_segment_summary
from data_visualization import plot_bar_wholemarket, plot_line_segment, plot_line_segment_panel

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

        firms["applications_received"] = 0
        firms["applicants"] = [[] for _ in range(M_FIRMS)]
        firms["ranked_applicants"] = [deque() for _ in range(M_FIRMS)]
        firms["filled"] = [None for _ in range(M_FIRMS)]
        firms["coa_money"] = np.full(M_FIRMS, 0)
        firms["coa_effort"] = np.full(M_FIRMS, 0)

    # Match -> compute results -> clean matchings
    results = {}
    for intervention in INTERVENTIONS:
        match(workers, firms, intervention)
        quality, match_count = match_quality(workers, firms)
        segments = segment_market(workers, firms)
        key = intervention if intervention is not None else "baseline"
        results[f"{key}_application_count"] = sum(
            len(applicants) for applicants in firms["applicants"]
        )
        results[f"{key}_quality"] = quality
        results[f"{key}_match_count"] = match_count
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
    summary = summarize_results(results, INTERVENTIONS, N_WORKERS, M_FIRMS)
    segment_summary = summarize_segments(results, INTERVENTIONS)

    end = time.time()

    # Print metrics
    print(f"\nTime: {end - start:.2f}s")
    print_results_table(summary)
    # print_segment_summary(segment_summary)

    # Bar charts: Whole market
    plot_bar_wholemarket(
        summary, INTERVENTIONS,
        metric="applications_per_firm",
        ylabel="Applications per Firm",
        title="Applications per Firm by Intervention (95% CI)",
        filename="graphs/applications_bar_chart.png"
    )
    plot_bar_wholemarket(
        summary, INTERVENTIONS,
        metric="match_rate",
        ylabel="Match Rate",
        title="Match Rate by Intervention (95% CI)",
        filename="graphs/match_rate_bar_chart.png"
    )
    plot_bar_wholemarket(
        summary, INTERVENTIONS,
        metric="efficiency",
        ylabel="Match Efficiency",
        title="Match Efficiency by Intervention (95% CI)",
        filename="graphs/efficiency_bar_chart.png"
    )

    # Line charts: Segmented market
    plot_line_segment(
        segment_summary,
        INTERVENTIONS,
        side="firms",
        metric="applications_per_firm",
        ylabel="Applications per Firm",
        title="Applications per Firm by Salary",
        filename="graphs/segment_congestion.png"
    )
    plot_line_segment_panel(
        segment_summary,
        INTERVENTIONS,
        metrics=[("workers", "match_prob"), ("firms", "fill_prob")],
        ylabels=["Match Probability", "Fill Probability"],
        titles=["Worker Match Probability", "Firm Fill Probability"],
        filename="graphs/segment_match_rates.png"
    )
    plot_line_segment_panel(
        segment_summary,
        INTERVENTIONS,
        metrics=[("workers", "avg_salary"), ("firms", "avg_quality")],
        ylabels=["Average Salary", "Average Worker Quality"],
        titles=["Worker Outcomes", "Firm Outcomes"],
        filename="graphs/segment_outcomes.png"
    )
