import time
import numpy as np
from collections import deque
from agents import generate_workers, generate_firms
from matching import match
from metrics import match_quality, assortative_match_quality
from results_table import summarize_results, print_results_table


N_WORKERS = 500
M_FIRMS = 500
ROUNDS = 50

INTERVENTIONS = [
    None,
    "cap",
    "fee",
    "cover_letter",
    "assessment"
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
        firms["coa_time"] = np.full(M_FIRMS, 0)

    # Match -> compute results -> clean matchings
    results = {}
    for intervention in INTERVENTIONS:
        match(workers, firms, intervention)
        quality, matches = match_quality(workers, firms)
        key = intervention if intervention is not None else "baseline"
        results[f"{key}_quality"] = quality
        results[f"{key}_matches"] = matches
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

    end = time.time()

    # Print metrics
    print(f"\nTime: {end - start:.2f}s")
    print_results_table(summary)
