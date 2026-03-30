import numpy as np
from collections import deque


def generate_workers(n_workers, firms):
    """Return attributes for n workers"""

    # Workers have a baseline WTP ~ F
    base_time = np.clip(np.random.normal(0.5, 0.15, n_workers), 0, 1)
    base_effort = np.clip(np.random.normal(0.5, 0.15, n_workers), 0, 1)
    base_money = np.clip(np.random.normal(0.5, 0.15, n_workers), 0, 1)

    # How much a firm's salary effects a worker's wtp
    firm_effect = 0.3 * (firms["salary"] - np.mean(firms["salary"]))
    # Stochasticity to represent other factors on WTP for a firm, eg, career alignment
    epsilon = np.random.normal(0, 0.05, (n_workers, firms["m"]))

    # WTP = baseline WTP + effect from firm salary + effect from other factors
    wtp_time = np.clip(base_time[:, None] + firm_effect[None, :] + epsilon, 0, 1)
    wtp_effort = np.clip(base_effort[:, None] + firm_effect[None, :] + epsilon, 0, 1)
    wtp_money = np.clip(base_money[:, None] + firm_effect[None, :] + epsilon, 0, 1)



    app_capacity = np.random.normal(loc=firms["m"]/2, scale=firms["m"]/4, size=n_workers)
    app_capacity = np.clip(app_capacity, 1, firms["m"]).astype(int)



    workers = {
        "n": n_workers,
        "quality": np.clip(np.random.normal(0.5, 0.15, n_workers), 0, 1),
        "wtp_time": wtp_time,
        "wtp_effort": wtp_effort,
        "wtp_money": wtp_money,
        "app_capacity": app_capacity,
        "offers": [[] for _ in range(n_workers)],
        "accepted": [None for _ in range(n_workers)]
    }
    return workers


def generate_firms(m_firms):
    """Return attributes for m firms"""

    firms = {
        "m": m_firms,
        "salary": np.clip(np.random.normal(0.5, 0.15, m_firms), 0, 1),
        "coa_time": np.full(m_firms, 0),
        "coa_effort": np.full(m_firms, 0),
        "coa_money": np.full(m_firms, 0),
        "cap": np.full(m_firms, 20),
        "applicants": [[] for _ in range(m_firms)],
        "ranked_applicants": [deque() for _ in range(m_firms)],
        "filled": [None for _ in range(m_firms)]
    }
    return firms
