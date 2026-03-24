import numpy as np
from collections import deque


def generate_workers(n_workers, firms):
    """Return attributes n workers"""

    # How much a firm's salary effects a worker's wtp
    firm_effect = 0.3 * (firms["salary"] - np.mean(firms["salary"]))
    # Stochasticity to represent other factors on WTP for a firm, eg, career alignment
    epsilon = np.random.normal(0, 0.05, (n_workers, firms["m"]))

    # Workers have a baseline WTP ~ F
    base_time = np.clip(np.random.normal(0.5, 0.15, n_workers), 0, 1)
    base_effort = np.clip(np.random.normal(0.5, 0.15, n_workers), 0, 1)
    base_money = np.clip(np.random.normal(0.5, 0.15, n_workers), 0, 1)

    # WTP = baseline WTP + effect from firm salary + effect from other factors
    wtp_time = np.clip(base_time[:, None] + firm_effect[None, :] + epsilon, 0, 1)
    wtp_effort = np.clip(base_effort[:, None] + firm_effect[None, :] + epsilon, 0, 1)
    wtp_money = np.clip(base_money[:, None] + firm_effect[None, :] + epsilon, 0, 1)

    workers = {
        "n": n_workers,
        "quality": np.random.lognormal(mean=0, sigma=0.5, size=n_workers),
        "wtp_time": wtp_time,
        "wtp_effort": wtp_effort,
        "wtp_money": wtp_money,
        "offers": [[] for _ in range(n_workers)],
        "accepted": [None for _ in range(n_workers)]
    }
    return workers


def generate_firms(m_firms):
    """Return attributes for m firms"""

    firms = {
        "m": m_firms,
        "salary": np.random.lognormal(mean=np.log(1), sigma=0.3, size=m_firms),
        "coa_time": np.zeros(m_firms),
        "coa_effort": np.zeros(m_firms),
        "coa_money": np.zeros(m_firms),
        "applicants": [[] for _ in range(m_firms)],
        "ranked_applicants": [deque() for _ in range(m_firms)],
        "filled": [None for _ in range(m_firms)]
    }
    return firms
