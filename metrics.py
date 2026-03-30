import numpy as np


def match_quality(workers, firms):
    """Returns total match quality"""

    total_match_quality = 0
    n = 0

    for worker in range(workers["n"]):
        firm = workers["accepted"][worker]
        if firm is not None:
            total_match_quality += workers["quality"][worker] * firms["salary"][firm]
            n += 1

    return total_match_quality, n


def assortative_match_quality(workers, firms):
    """Returns total match quality for an assortative matching"""

    # Rank firms by salary, applicants by quality
    ranked_workers = np.argsort(-workers["quality"])
    ranked_firms = np.argsort(-firms["salary"])
    n = min(len(workers["quality"]), len(firms["salary"]))

    # Multiply in order
    return np.sum(workers["quality"][ranked_workers[:n]] * firms["salary"][ranked_firms[:n]])
