import numpy as np
from main import N_WORKERS, M_FIRMS


def match_quality(workers, firms):
    """Returns total match quality"""

    total_match_quality = 0
    match_count = 0

    for worker in range(N_WORKERS):
        firm = workers["accepted"][worker]
        if firm is not None:
            total_match_quality += workers["quality"][worker] * firms["salary"][firm]
            match_count += 1

    return total_match_quality, match_count


def assortative_match_quality(workers, firms):
    """Returns total match quality for an assortative matching"""

    # Rank firms by salary, applicants by quality
    ranked_workers = np.argsort(-workers["quality"])
    ranked_firms = np.argsort(-firms["salary"])
    n = min(len(workers["quality"]), len(firms["salary"]))

    # Multiply in order
    return np.sum(workers["quality"][ranked_workers[:n]] * firms["salary"][ranked_firms[:n]])


def segment_market(workers, firms):
    """Return stats for segments of the market"""

    bin_width = 0.1
    n_bins = int(1 / bin_width)

    # Initialize storage
    worker_bins = [
        {"count": 0, "matched": 0, "salary_sum": 0}
        for _ in range(n_bins)
    ]

    firm_bins = [
        {"count": 0, "filled": 0, "quality_sum": 0, "application_count": 0}
        for _ in range(n_bins)
    ]

    for w in range(N_WORKERS):
        q = workers["quality"][w]
        b = min(int(q / bin_width), n_bins - 1)

        worker_bins[b]["count"] += 1

        firm = workers["accepted"][w]
        if firm is not None:
            worker_bins[b]["matched"] += 1
            worker_bins[b]["salary_sum"] += firms["salary"][firm]

    for f in range(M_FIRMS):
        s = firms["salary"][f]
        b = min(int(s / bin_width), n_bins - 1)

        firm_bins[b]["count"] += 1

        firm_bins[b]["application_count"] += len(firms["applicants"][f])

        worker = firms["filled"][f]
        if worker is not None:
            firm_bins[b]["filled"] += 1
            firm_bins[b]["quality_sum"] += workers["quality"][worker]

    return {
        "workers": worker_bins,
        "firms": firm_bins,
    }
