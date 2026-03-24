import time
import numpy as np
from agents import generate_workers, generate_firms
from matching import match
from metrics import match_quality, assortative_quality


n_workers = 500
m_firms = 500
ROUNDS = 100


def run_simulation():
    """Runs one simulation round and returns metrics"""

    # Generate agents
    firms = generate_firms(m_firms)
    workers = generate_workers(n_workers, firms)

    # Match
    match(workers, firms)

    # Compute metrics
    total_match_quality, n = match_quality(workers, firms)
    assortative_match_quality = assortative_quality(workers, firms)

    return {
        "matches": n,
        "match_quality": total_match_quality,
        "assortative_quality": assortative_match_quality,
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
    match_efficiency = avg_results["match_quality"] / avg_results["assortative_quality"]

    end = time.time()

    # Print metrics
    print(f"\n=== Simulation Metrics ({ROUNDS} rounds with {n_workers} workers, {m_firms} firms) ===")
    print(f"Time: {end - start:.2f}s\n")
    for key, value in avg_results.items():
        print(f"{key}: {value:.2f}")
    print(f"{'Match efficiency'}: {match_efficiency:.2%}\n")
