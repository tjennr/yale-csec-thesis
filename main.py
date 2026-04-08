import time
import numpy as np
from agents import generate_workers, generate_firms, reset_agent_matchings
from matching import match
from interventions import set_intervention, set_custom_intervention
from metrics import match_quality, assortative_match_quality, segment_market
from results_wholemarket import summarize_results, print_results_table
from results_segmentedmarket import summarize_segments, print_segment_summary
from data_visualization import plot_whole, plot_segmented
from increasing_param_sim import compute_plot_increasing_params


N_WORKERS = 200
M_FIRMS = 50
ROUNDS = 10

INTERVENTIONS = [
    None,
    "cap",
    "fee",
    "cover_letter",
    "assessment",
    "pref_signal",
]


def run_simulation(interventions, param=None, value=None):
    """Run one full simulation across specified interventions"""

    firms = generate_firms(M_FIRMS)
    workers = generate_workers(N_WORKERS, firms)

    results = {}

    for intervention in interventions:
        metrics = run_market(
            workers,
            firms,
            intervention,
            param_value=value if intervention == param else None
        )

        key = intervention if intervention is not None else "baseline"

        results[f"{key}_application_count"] = metrics["application_count"]
        results[f"{key}_quality"] = metrics["quality"]
        results[f"{key}_match_count"] = metrics["match_count"]
        results[f"{key}_segments"] = metrics["segments"]

        reset_agent_matchings(workers, firms)

    results["assortative_quality"] = assortative_match_quality(workers, firms)

    return results


def run_market(workers, firms, intervention=None, param_value=None):
    """Run matching for ONE intervention and return metrics"""

    # Apply intervention
    if param_value is not None:
        set_custom_intervention(firms, intervention, param_value)
    else:
        set_intervention(firms, intervention)

    # Run matching
    match(workers, firms, intervention)

    # Collect metrics
    quality, match_count = match_quality(workers, firms)
    segments = segment_market(workers, firms)

    return {
        "application_count": sum(len(apps) for apps in firms["applicants"]),
        "quality": quality,
        "match_count": match_count,
        "segments": segments
    }


if __name__ == "__main__":

    start = time.time()
    results = []

    # Run simulations
    for _ in range(ROUNDS):
        res = run_simulation(INTERVENTIONS)
        results.append(res)

    # Results
    summary = summarize_results(results)
    segment_summary = summarize_segments(results)

    end = time.time()

    # Print metrics
    print(f"\nTime: {end - start:.2f}s")
    print_results_table(summary)
    # print_segment_summary(segment_summary)

    plot_whole(summary, INTERVENTIONS)
    plot_segmented(segment_summary, INTERVENTIONS)

    compute_plot_increasing_params()
