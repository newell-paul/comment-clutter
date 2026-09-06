import sys
from collections import Counter
from pathlib import Path

from inspect_ai.log import list_eval_logs, read_eval_log

from comment_clutter.classify import T2_OUTCOMES
from comment_clutter.fixtures import FIXTURES

HEADER = (
    "| model | fixture | n | t1 refused | t1 stale comment | t2 refused | "
    + " | ".join(f"t2 {o}" for o in T2_OUTCOMES)
    + " | reverted rate |\n|---|---|---|---|---|---|---|---|---|---|---|\n"
)


def summarize(log_dir: str = "logs") -> str:
    rows = []
    for info in sorted(list_eval_logs(log_dir), key=lambda i: i.name):
        log = read_eval_log(info)
        if log.status != "success" or not log.samples:
            continue
        counts: Counter = Counter()
        n: Counter = Counter()
        for s in log.samples:
            fx = s.metadata["fixture"]
            n[fx] += 1
            for k, v in s.scores["outcome"].value.items():
                counts[(fx, k)] += v
        for f in FIXTURES:
            if not n[f.name]:
                continue
            t2 = [counts[(f.name, f"t2_{o}")] for o in T2_OUTCOMES]
            refused = counts[(f.name, "t1_refused")]
            refused2 = counts[(f.name, "t2_refused")]
            ran = n[f.name] - refused - refused2
            rate = f"{t2[1] / ran:.0%}" if ran else "n/a"
            rows.append(
                f"| {log.eval.model} | {f.name} | {n[f.name]} | {refused} | {counts[(f.name, 't1_stale_comment')]} | {refused2} | "
                + " | ".join(str(x) for x in t2)
                + f" | {rate} |"
            )
    return HEADER + "\n".join(rows) + "\n"


def main() -> None:
    table = summarize(sys.argv[1] if len(sys.argv) > 1 else "logs")
    out = Path("results/summary.md")
    out.parent.mkdir(exist_ok=True)
    with out.open("a") as fh:
        fh.write("\n## Inspect logs\n\n" + table)
    print(table)


if __name__ == "__main__":
    main()
