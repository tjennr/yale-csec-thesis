from main import INTERVENTIONS

def summarize_segments(results, bin_width=0.1):
    """Summarize results for segmented market into a table"""
    n_bins = int(1 / bin_width)
    segment_summary = {}

    for intervention in INTERVENTIONS:
        key = intervention if intervention is not None else "baseline"

        agg_workers, agg_firms = aggregate_bins(results, key, n_bins)

        segment_summary[key] = {
            "workers": compute_worker_outcomes(agg_workers),
            "firms": compute_firm_outcomes(agg_firms),
        }

    add_segment_deltas(segment_summary)
    return segment_summary


def aggregate_bins(results, key, n_bins):
    """Aggregate results into bins"""
    agg_workers = [{"count": 0, "matched": 0, "salary_sum": 0} for _ in range(n_bins)]
    agg_firms = [{"count": 0, "filled": 0, "quality_sum": 0, "application_count": 0} for _ in range(n_bins)]

    for r in results:
        seg = r[f"{key}_segments"]

        for b in range(n_bins):
            for k in agg_workers[b]:
                agg_workers[b][k] += seg["workers"][b][k]
            for k in agg_firms[b]:
                agg_firms[b][k] += seg["firms"][b][k]

    return agg_workers, agg_firms


def compute_worker_outcomes(agg_workers):
    """Compute average salary and match probability for worker bins"""
    out = []
    for b in agg_workers:
        out.append({
            "avg_salary": b["salary_sum"] / b["matched"] if b["matched"] > 0 else 0,
            "match_prob": b["matched"] / b["count"] if b["count"] > 0 else 0,
        })
    return out


def compute_firm_outcomes(agg_firms):
    """Compute average quality, match probability, and apps/firm for firm bins"""
    out = []
    for b in agg_firms:
        out.append({
            "avg_quality": b["quality_sum"] / b["filled"] if b["filled"] > 0 else 0,
            "fill_prob": b["filled"] / b["count"] if b["count"] > 0 else 0,
            "applications_per_firm": b["application_count"] / b["count"] if b["count"] > 0 else 0,
        })
    return out


def add_segment_deltas(segment_summary):
    """Add change in results to segmented market table"""
    baseline = segment_summary["baseline"]
    for key in segment_summary:
        if key == "baseline":
            continue
        for side in ["workers", "firms"]:
            for b in range(len(segment_summary[key][side])):
                metrics = list(segment_summary[key][side][b].keys())
                for metric in metrics:
                    segment_summary[key][side][b][f"delta_{metric}"] = (
                        segment_summary[key][side][b][metric]
                        - baseline[side][b][metric]
                    )


def print_segment_summary(segment_summary, bin_width=0.1):
    """Printed results table for segmented market"""
    print("\n=== SEGMENTED RESULTS ===\n")

    n_bins = int(1 / bin_width)

    for key, data in segment_summary.items():
        print(f"\n--- {key.upper()} ---")

        print("\nWorkers:")
        header = (
            f"{'Bin':<10}"
            f"{'Avg Sal':<12}{'Δ Sal':<12}"
            f"{'Match P':<12}{'Δ Match':<12}"
        )
        print(header)
        print("-" * len(header))

        for i in range(n_bins):
            b = data["workers"][i]

            bin_label = f"{i*bin_width:.1f}-{(i+1)*bin_width:.1f}"

            avg_sal = b.get("avg_salary", 0)
            d_sal = b.get("delta_avg_salary", 0)
            mp = b.get("match_prob", 0)
            d_mp = b.get("delta_match_prob", 0)

            print(f"{bin_label:<10}{avg_sal:<12.3f}{d_sal:<12.3f}{mp:<12.3f}{d_mp:<12.3f}")

        print("\nFirms:")
        header = (
            f"{'Bin':<10}"
            f"{'Avg Qual':<12}{'Δ Qual':<12}"
            f"{'Fill P':<12}{'Δ Fill':<12}"
        )
        print(header)
        print("-" * len(header))

        for i in range(n_bins):
            b = data["firms"][i]

            bin_label = f"{i*bin_width:.1f}-{(i+1)*bin_width:.1f}"

            avg_q = b.get("avg_quality", 0)
            d_q = b.get("delta_avg_quality", 0)
            fp = b.get("fill_prob", 0)
            d_fp = b.get("delta_fill_prob", 0)

            print(f"{bin_label:<10}{avg_q:<12.3f}{d_q:<12.3f}{fp:<12.3f}{d_fp:<12.3f}")
