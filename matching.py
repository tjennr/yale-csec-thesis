import numpy as np
from collections import deque
from interventions import apply_cap, run_assessments, apply_preference_signal


def match(workers, firms, intervention=None, max_rounds=10):
    """Runs matching process: workers apply, firms screen and offer, workers accept"""

    workers_apply(workers, firms, intervention)
    firms_screen_workers(workers, firms, intervention)
    for _ in range(max_rounds):
        if all(filled is not None or len(rank) == 0 for filled, rank in zip(firms["filled"], firms["ranked_applicants"])):
            break
        firms_offer(workers, firms)
        workers_accept(workers, firms)


def workers_apply(workers, firms, intervention):
    """Workers rank and apply to firms"""

    n_workers = workers["n"]
    m_firms = firms["m"]

    # Rank firms by salary with stochasity 
    # (to mimic workers only seeing a subset of job listings on market and non-salary factors for favoring a firm)
    noise = np.random.normal(0, 0.3, (n_workers, m_firms))
    perceived_firm_value = firms["salary"] + noise
    firms_ranked = np.argsort(-perceived_firm_value, axis=1)

    # Apply to top firms subject to application capacity and WTP >= firms' COA
    for worker in range(n_workers):

        capacity = workers["app_capacity"][worker]
        applied = 0
        rank_idx = 0
        signals_sent = 0

        while applied < capacity and rank_idx < m_firms:
            firm = firms_ranked[worker][rank_idx]
            
            if workers["wtp_effort"][worker][firm] >= firms["coa_effort"][firm] \
                and workers["wtp_money"][worker][firm] >= firms["coa_money"][firm]:
                
                firms["applicants"][firm].append(worker)
                applied += 1

                if intervention == "pref_signal" and signals_sent < 3:
                    firms["pref_signal"][worker][firm] = True
                    signals_sent += 1

            rank_idx += 1


def firms_screen_workers(workers, firms, intervention):
    """Firms rank workers by perceived quality"""

    for firm in range(firms["m"]):
        if len(firms["applicants"][firm]) > 0:

            if intervention == "cap":
                apply_cap(firms, firm)

            if intervention == "assessment":
                run_assessments(workers, firms, firm)
            
            # Firms noisily evaluate worker quality
            applicants = firms["applicants"][firm]
            noise = np.random.normal(0, 0.005, len(applicants))
            perceived_quality = workers["quality"][applicants] + noise

            if intervention == "pref_signal":
                apply_preference_signal(firms, firm, applicants, perceived_quality)

            # Firms rank workers based on perceived quality
            sorted_indices = np.argsort(-perceived_quality)
            firms["ranked_applicants"][firm] = deque([applicants[k] for k in sorted_indices])


def firms_offer(workers, firms):
    """Firms give an offer to their perceived highest-quality applicant"""

    for firm in range(firms["m"]):
        if firms["filled"][firm] is not None or not firms["ranked_applicants"][firm]:
            continue

        # Firm gives offer to perceived highest-quality applicant
        best_applicant = firms["ranked_applicants"][firm].popleft()
        workers["offers"][best_applicant].append(firm)


def workers_accept(workers, firms):
    """Workers accept their highest salary offer"""

    for worker in range(workers["n"]):
        if workers["accepted"][worker] is not None or not workers["offers"][worker]:
            continue

        # Workers accept offer from firm with highest salary
        best_firm = max(workers["offers"][worker], key=lambda j: firms["salary"][j])
        workers["accepted"][worker] = best_firm
        firms["filled"][best_firm] = worker

        # Remove accepted worker from other firms' applicant pools -> exit market
        for firm in range(firms["m"]):
            if firm != best_firm:
                if worker in firms["ranked_applicants"][firm]:
                    firms["ranked_applicants"][firm].remove(worker)
