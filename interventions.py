import numpy as np

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

    assessment_difficulty = 0.5 # placeholder!!!
    assessment_time = firms["coa_time"][firm]

    wtp_time = workers["wtp_time"][worker][firm]
    worker_quality = workers["quality"][worker]

    if wtp_time >= assessment_time and worker_quality >= assessment_difficulty:
        return True
    return False
