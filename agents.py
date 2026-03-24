import numpy as np
from collections import deque


def generate_workers(n_workers):
    """Return attributes n workers"""
    # TODO: WTP needs to be dynamic across diff firms/salaries

    workers = {
        "n": n_workers,
        "quality": np.random.lognormal(mean=0, sigma=0.5, size=n_workers),
        "wtp_time": np.random.uniform(0, 1, n_workers),
        "wtp_effort": np.random.uniform(0, 1, n_workers),
        "wtp_money": np.random.uniform(0, 1, n_workers),
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
