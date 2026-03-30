import numpy as np
from collections import deque


def match(workers, firms, intervention=None, max_rounds=10):
    """Runs matching process: workers apply, firms screen and offer, workers accept"""

    set_intervention(firms, intervention)
    workers_apply(workers, firms)
    firms_screen_workers(workers, firms, intervention)
    for _ in range(max_rounds):
        if all(filled is not None or len(rank) == 0 for filled, rank in zip(firms["filled"], firms["ranked_applicants"])):
            break
        firms_offer(workers, firms)
        workers_accept(workers, firms)


def set_intervention(firms, intervention):

    m = firms["m"]

    if intervention == "cap":
        # only look at + rank first C applicants from firms["applicants"][firm] list
        pass
    elif intervention == "fee":
        firms["coa_money"] = np.full(m, 0.5)
    elif intervention == "coverletter":
        # coa time + effort
        # todo before workers apply
        pass
    elif intervention == "assessment":
        # coa time + effort + quality
        # todo before + after workers apply
        pass
    elif intervention == "pref_signal":
        # todo before workers apply
        pass


def workers_apply(workers, firms, intervention):
    """Workers rank and apply to firms"""

    n_workers = workers["n"]
    m_firms = firms["m"]

    # Rank firms by salary with stochasity (to account for non-salary factors for favoring a firm)
    noise = np.random.normal(0, 0.5, (n_workers, m_firms))
    perceived_firm_value = firms["salary"] + noise
    firms_ranked = np.argsort(-perceived_firm_value, axis=1)

    # Apply to top firms subject to application capacity and WTP >= firms' COA
    for worker in range(n_workers):
        capacity = workers["app_capacity"][worker]
        applied = 0
        rank_idx = 0
        while applied < capacity and rank_idx < m_firms:
            firm = firms_ranked[worker][rank_idx]
            if workers["wtp_time"][worker][firm] >= firms["coa_time"][firm] \
                and workers["wtp_effort"][worker][firm] >= firms["coa_effort"][firm] \
                and workers["wtp_money"][worker][firm] >= firms["coa_money"][firm]:
                firms["applicants"][firm].append(worker)
                applied += 1
            rank_idx += 1

    # firms_ranked = np.argsort(-firms["salary"])
    # for j in firms_ranked:
    #     salary = firms["salary"][j]
    #     n_applicants = len(firms["applicants"][j])
    #     print(f"Firm {j}: salary={salary:.2f}, applicants={n_applicants}")


def firms_screen_workers(workers, firms, intervention):
    """Firms rank workers by perceived quality"""

    # TODO: add noise for realistic imperfect evaluation of applications
    for firm in range(firms["m"]):
        applicants = firms["applicants"][firm]
        if len(applicants) > 0:
            if intervention == "cap":
                cap = firms["cap"][firm]
                np.random.shuffle(firms["applicants"][firm]) # I think we need this to replicate workers simultaneously applying rather than sequentially
                firms["applicants"][firm] = firms["applicants"][firm][:cap]
                applicants = firms["applicants"][firm]
            sorted_indices = np.argsort(-workers["quality"][applicants])
            firms["ranked_applicants"][firm] = deque([applicants[k] for k in sorted_indices])


def firms_offer(workers, firms):
    """Firms give an offer to their perceived highest-quality applicant"""

    for firm in range(firms["m"]):
        # Skip if firm already has position filled or has no applicants
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
