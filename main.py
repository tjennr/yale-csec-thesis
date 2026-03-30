import time
import numpy as np
from collections import deque
from agents import generate_workers, generate_firms
from matching import match
from metrics import match_quality, assortative_match_quality


N_WORKERS = 500
M_FIRMS = 500
ROUNDS = 50


def run_simulation():
    """Runs one simulation round and returns metrics"""

    # Generate agents
    firms = generate_firms(M_FIRMS)
    workers = generate_workers(N_WORKERS, firms)

    def clean():
        """Reset agent match attributes inbetween interventions"""
        workers["offers"] = [[] for _ in range(N_WORKERS)]
        workers["accepted"] = [None for _ in range(N_WORKERS)]

        firms["applicants"] = [[] for _ in range(M_FIRMS)]
        firms["ranked_applicants"] = [deque() for _ in range(M_FIRMS)]
        firms["filled"] = [None for _ in range(M_FIRMS)]
        firms["coa_money"] = np.full(M_FIRMS, 0)

    # Match -> compute metrics -> clean matchings
    match(workers, firms)
    baseline_quality, n = match_quality(workers, firms)
    clean()

    match(workers, firms, intervention="cap")
    cap_quality, m = match_quality(workers, firms)
    clean()

    match(workers, firms, intervention="fee")
    fee_quality, q = match_quality(workers, firms)
    clean()

    assortative_quality = assortative_match_quality(workers, firms)

    return {
        "baseline_matches": n,
        "baseline_quality": baseline_quality,
        "cap_matches": m,
        "cap_quality": cap_quality,
        "fee_matches": q,
        "fee_quality": fee_quality,
        "assortative_quality": assortative_quality,
    }


if __name__ == "__main__":

    start = time.time()
    results = []

    # Run simulations
    for _ in range(ROUNDS):
        sim_results = run_simulation()
        results.append(sim_results)

    # Average results
    avg_results = {
        key: np.mean([r[key] for r in results])
        for key in results[0]
    }

    # Compute efficiency
    baseline_efficiency = avg_results["baseline_quality"] / avg_results["assortative_quality"]
    cap_efficiency = avg_results["cap_quality"] / avg_results["assortative_quality"]
    fee_efficiency = avg_results["fee_quality"] / avg_results["assortative_quality"]
    avg_results["baseline_efficiency"] = baseline_efficiency
    avg_results["cap_efficiency"] = cap_efficiency
    avg_results["fee_efficiency"] = fee_efficiency

    end = time.time()

    # Print metrics
    print(f"\n=== Simulation Metrics ({ROUNDS} rounds with {N_WORKERS} workers, {M_FIRMS} firms) ===")
    print(f"Time: {end - start:.2f}s\n")
    for key, value in avg_results.items():
        print(f"{key}: {value:.2f}")
    print()
