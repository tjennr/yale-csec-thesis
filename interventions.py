import numpy as np


intervention_stat = {
    "cap": 50,
    "fee": 0.3,
    "cover_letter_time": 0.3,
    "assessment_time": 0.5,
    "pref_signal_value": 0.05
}


def set_intervention(workers, firms, intervention):
    """Update firm attributes according to congestion intervention strategy"""

    n = workers["n"]
    m = firms["m"]

    if intervention == "cap":
        firms["cap"] = np.full(m, intervention_stat["cap"])
    elif intervention == "fee":
        firms["coa_money"] = np.full(m, intervention_stat["fee"])
    elif intervention == "cover_letter":
        firms["coa_time"] = np.full(m, intervention_stat["cover_letter_time"])
    elif intervention == "assessment":
        firms["coa_time"] = np.full(m, intervention_stat["assessment_time"])
        # quality here?
    elif intervention == "pref_signal":
        firms["pref_signal"] = np.full((n, m), False)


# CAP
def apply_cap(firms, firm):
    cap = firms["cap"][firm]
    np.random.shuffle(firms["applicants"][firm]) # Shuffle to replicate workers simultaneously applying rather than sequentially
    firms["applicants"][firm] = firms["applicants"][firm][:cap]


# ASSESSMENT
def run_assessments(workers, firms, firm):
    """Filters applicants list to only keep workers who pass assessment"""

    passed = []
    for worker in firms["applicants"][firm]:
        if pass_assessment(workers, worker, firms, firm):
            passed.append(worker)
    firms["applicants"][firm] = passed


def pass_assessment(workers, worker, firms, firm):
    """Returns True if a worker passes a firm's assessment"""

    assessment_difficulty = 0.5     # placeholder!!! TODO
    assessment_time = firms["coa_time"][firm]

    wtp_time = workers["wtp_time"][worker][firm]
    worker_quality = workers["quality"][worker]

    # TODO: not guaranteed that a high quality worker will pass difficult test -> need some randomness

    if wtp_time >= assessment_time and worker_quality >= assessment_difficulty:
        return True
    return False


# PREFERENCE SIGNAL
def apply_preference_signal(firms, firm, applicants, perceived_quality):
    """Increase perceived quality of applicants who sent a preference signal"""
    signal_value = intervention_stat["pref_signal_value"]
    signaled_applicants = firms["pref_signal"][applicants, firm]
    perceived_quality[signaled_applicants] += signal_value
