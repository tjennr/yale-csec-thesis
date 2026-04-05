def summarize_segments(results, interventions, bin_width=0.1):
    n_bins = int(1 / bin_width)
    segment_summary = {}

    for intervention in interventions:
        key = intervention if intervention is not None else "baseline"

        # Initialize aggregates
        agg_workers = [
            {"count": 0, "matched": 0, "salary_sum": 0}
            for _ in range(n_bins)
        ]
        agg_firms = [
            {"count": 0, "filled": 0, "quality_sum": 0}
            for _ in range(n_bins)
        ]

        # Aggregate across simulations
        for r in results:
            seg = r[f"{key}_segments"]

            for b in range(n_bins):
                for k in agg_workers[b]:
                    agg_workers[b][k] += seg["workers"][b][k]
                for k in agg_firms[b]:
                    agg_firms[b][k] += seg["firms"][b][k]

        # Convert to final metrics
        worker_outcomes = []
        for b in agg_workers:
            avg_salary = (
                b["salary_sum"] / b["matched"] if b["matched"] > 0 else 0
            )
            match_prob = b["matched"] / b["count"] if b["count"] > 0 else 0

            worker_outcomes.append({
                "avg_salary": avg_salary,
                "match_prob": match_prob,
            })

        firm_outcomes = []
        for b in agg_firms:
            avg_quality = (
                b["quality_sum"] / b["filled"] if b["filled"] > 0 else 0
            )
            fill_prob = b["filled"] / b["count"] if b["count"] > 0 else 0

            firm_outcomes.append({
                "avg_quality": avg_quality,
                "fill_prob": fill_prob,
            })

        segment_summary[key] = {
            "workers": worker_outcomes,
            "firms": firm_outcomes,
        }

    add_segment_deltas(segment_summary)

    return segment_summary


def add_segment_deltas(segment_summary):
    baseline = segment_summary["baseline"]
    for key in segment_summary:
        if key == "baseline":
            continue
        for side in ["workers", "firms"]:
            for b in range(len(segment_summary[key][side])):
                metrics = list(segment_summary[key][side][b].keys())  # FIX
                for metric in metrics:
                    segment_summary[key][side][b][f"delta_{metric}"] = (
                        segment_summary[key][side][b][metric]
                        - baseline[side][b][metric]
                    )


def print_segment_summary(segment_summary, bin_width=0.1):
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
