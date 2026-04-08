import numpy as np
# from main import N_WORKERS, M_FIRMS


INTERVENTION_STAT = {
    "cap": 50,
    "fee": 0.3,
    "cover_letter_effort": 0.3,
    "assessment_effort": 0.5,       # TODO: should assessment attributes differ across firms?
    "assessment_difficulty": 0.5,
    "pref_signal_value": 0.05
}


def set_intervention(firms, intervention):
    """Update firm attributes according to congestion intervention strategy"""

    if intervention == "cap":
        firms["cap"] = np.full(M_FIRMS, INTERVENTION_STAT["cap"])
    elif intervention == "fee":
        firms["coa_money"] = np.full(M_FIRMS, INTERVENTION_STAT["fee"])
    elif intervention == "cover_letter":
        firms["coa_effort"] = np.full(M_FIRMS, INTERVENTION_STAT["cover_letter_effort"])
    elif intervention == "assessment":
        firms["coa_effort"] = np.full(M_FIRMS, INTERVENTION_STAT["assessment_effort"])
        firms["assessment_difficulty"] = np.full(M_FIRMS, INTERVENTION_STAT["assessment_difficulty"])
    elif intervention == "pref_signal":
        firms["pref_signal"] = np.full((N_WORKERS, M_FIRMS), False)


def set_custom_intervention(firms, intervention, value):

    if intervention == "cap":
        firms["cap"] = np.full(M_FIRMS, value)
    elif intervention == "fee":
        firms["coa_money"] = np.full(M_FIRMS, value)


# CAP
def apply_cap(firms, firm):
    """Caps the number of applicants a firm screens"""
    cap = firms["cap"][firm]
    np.random.shuffle(firms["applicants"][firm]) # Shuffle to replicate workers simultaneously applying rather than sequentially
    firms["applicants"][firm] = firms["applicants"][firm][:cap] # Cut down to only cap num of applications


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

    assessment_effort = firms["coa_effort"][firm]
    assessment_difficulty = firms["assessment_difficulty"][firm]

    wtp_effort = workers["wtp_effort"][worker][firm]
    worker_quality = workers["quality"][worker]

    if wtp_effort < assessment_effort:
        return False

    # Probabilistic pass using logistic function (higher quality > difficulty -> higher prob of pass)
    k = 10
    bias = 0.1
    prob_pass = 1 / (1 + np.exp(-k * (worker_quality - assessment_difficulty + bias)))
    return np.random.rand() < prob_pass


# PREFERENCE SIGNAL
def apply_preference_signal(firms, firm, applicants, perceived_quality):
    """Increase perceived quality of applicants who sent a preference signal"""
    signal_value = INTERVENTION_STAT["pref_signal_value"]
    signaled_applicants = firms["pref_signal"][applicants, firm]
    perceived_quality[signaled_applicants] += signal_value
