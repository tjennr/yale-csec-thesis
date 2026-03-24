import numpy as np
from collections import deque


def match(workers, firms, max_rounds=10):

    workers_apply(workers, firms)

    # Firms rank workers by perceived quality
    for firm in range(firms["m"]):
        applicants = firms["applicants"][firm]
        if len(applicants) > 0:
            sorted_indices = np.argsort(-workers["quality"][applicants])
            firms["ranked_applicants"][firm] = deque([applicants[k] for k in sorted_indices])

    for _ in range(max_rounds):
        # Stop if all firms are filled or no applicants left
        if all(filled is not None or len(rank) == 0 for filled, rank in zip(firms["filled"], firms["ranked_applicants"])):
            break

        firms_offer(workers, firms)
        workers_accept(workers, firms)
        

def workers_apply(workers, firms):
    """Workers rank and apply to firms"""

    n_workers = workers["n"]
    m_firms = firms["m"]

    # Workers have an application capacity K ~ F
    # TODO: should it be a normal dist? depends on how much congestion we want?
    K = np.random.randint(1, m_firms + 1, n_workers)

    # Rank firms by salary with stochasity
    noise = np.random.normal(0, 0.5, (n_workers, m_firms))
    perceived_firm_value = firms["salary"] + noise
    firms_ranked = np.argsort(-perceived_firm_value, axis=1)

    # TODO: wtp > cost of applying

    # Apply to top K firms
    for worker in range(n_workers):
        top_K = firms_ranked[worker, :K[worker]]
        for firm in top_K:
            firms["applicants"][firm].append(worker)


def firms_offer(workers, firms):
    """Firms give an offer to their perceived highest-quality applicant"""

    for firm in range(firms["m"]):

        # Firm already has position filled or has no applicants
        if firms["filled"][firm] is not None or not firms["ranked_applicants"][firm]:
            continue

        # Firm gives offer to perceived highest-quality applicant
        best_applicant = firms["ranked_applicants"][firm].popleft()
        workers["offers"][best_applicant].append(firm)


def workers_accept(workers, firms):
    """Workers accept their highest salary offer"""

    # Each worker chooses the best offer
    for worker in range(workers["n"]):

        if workers["accepted"][worker] is not None or not workers["offers"][worker]:
            continue

        # Pick firm with highest salary and update attributes
        best_firm = max(workers["offers"][worker], key=lambda j: firms["salary"][j])
        
        workers["accepted"][worker] = best_firm
        firms["filled"][best_firm] = worker

        # Remove accepted worker from other firms' applicant pools
        # TODO: optimize for runtime?
        for firm in range(firms["m"]):
            if firm != best_firm:
                if worker in firms["ranked_applicants"][firm]:
                    firms["ranked_applicants"][firm].remove(worker)
