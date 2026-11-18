"""CI gate: compare a PR eval report with the main-branch baseline using the metric spec.

    python -m lab9.gate --pr reports/eval_workflow.json --baseline reports/baseline_v1.json

exit 0 = merge, exit 1 = blocked. Safety metrics: max 0, no averaging away.
Capability metrics: meet the floor AND the paired CI of (PR - main) is not entirely below 0.
Thresholds may only get stricter on the same eval-set version (ratchet).
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

from lab8.console import utf8_stdio
from lab9 import stats
from lab9.eval import SPEC, load_spec, per_item


def integrity_check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> list[str]:
    """M7 (Expert): refuse to compare reports that cannot be trusted. Return a list of problems
    (empty = trustworthy). A gate that passes a broken report is worse than no gate.
    Must catch at least:
      - any metric value in pr["metrics"] that is NaN or inf
      - len(pr["rows"]) != manifest items x len(manifest seeds)   (dropped / duplicated rows)
      - the (item_id, seed) set of PR differs from the baseline's (cherry-picked seeds/items)
      - pr["evaluator_failures"] non-empty, or a row whose value for a graded spec metric is
        None (a crashed grader silently scores as "missing" and drops out of the mean)
      - base_spec given and a threshold in spec is LOOSER than in base_spec for the same
        eval-set version (ratchet: max may not rise, min may not fall, a blocking metric may
        not become non-blocking, a metric may not disappear; the same for spec["slices"],
        including dropping no_significant_drop)
      - an item's slice tags in PR rows differ from the baseline's (relabelling an item out of a
        slice hides its regression from the slice gate)"""
    problems = []
    rows, baseline = pr.get("rows", []), base.get("rows", [])
    manifest = pr.get("manifest", {})
    keys = [(r.get("item_id"), r.get("seed")) for r in rows]
    base_keys = [(r.get("item_id"), r.get("seed")) for r in baseline]
    if len(rows) != manifest.get("items", 0) * len(manifest.get("seeds", [])) or len(set(keys)) != len(keys):
        problems.append("row count or duplicate item/seed")
    if Counter(keys) != Counter(base_keys):
        problems.append("item/seed pairs differ from baseline")
    base_slices = {(r.get("item_id"), r.get("seed")): sorted(r.get("slices") or []) for r in baseline}
    if any(sorted(r.get("slices") or []) != base_slices.get((r.get("item_id"), r.get("seed"))) for r in rows):
        problems.append("slice tags differ from baseline")
    if pr.get("evaluator_failures"):
        problems.append("evaluator failures")
    for name, value in pr.get("metrics", {}).items():
        if value is None or not isinstance(value, (int, float)) or not math.isfinite(value):
            problems.append(f"invalid metric {name}")
    from lab9.graders import GRADERS
    for m in spec.get("metrics", []):
        mid = m["id"]
        if mid in GRADERS and any(r.get(mid) is None for r in rows):
            problems.append(f"missing graded value {mid}")
    if base_spec and spec.get("eval_set_version") == base_spec.get("eval_set_version"):
        def ratchet(old, new, label, nested):
            for key in ("min", "max", "max_increase"):
                if key in old and (key not in new or (new[key] < old[key] if key == "min" else new[key] > old[key])):
                    problems.append(f"loosened {label} {key}")
            if old.get("no_significant_drop") and not new.get("no_significant_drop"):
                problems.append(f"loosened {label} no_significant_drop")
        for section, key in (("metrics", lambda x: x["id"]), ("slices", lambda x: (x["name"], x["metric"]))):
            current = {key(x): x for x in spec.get(section, [])}
            for old in base_spec.get(section, []):
                name = key(old)
                new = current.get(name)
                if new is None:
                    problems.append(f"removed {section} {name}")
                    continue
                if old.get("blocking") and not new.get("blocking"):
                    problems.append(f"nonblocking {section} {name}")
                ratchet(old.get("threshold", {}) if section == "metrics" else old,
                        new.get("threshold", {}) if section == "metrics" else new, str(name), section)
    return problems


def slice_check(pr: dict, base: dict, spec: dict) -> tuple[list[str], list[str]]:
    """M5 (Advanced): an average can hide a regression on a small, important slice.
    For each entry of spec["slices"] ({"name", "metric", "min"?, "no_significant_drop"?, "blocking"}):
      - value = mean of per_item(pr, metric, slice_name=name)
      - fail if below "min", or if no_significant_drop and the paired CI over the slice's items
        lies entirely below 0
    Return (blocked ids like "slice:money_movement/pass_rate", report lines)."""
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for rule in spec.get("slices", []):
        name, metric = rule["name"], rule["metric"]
        a, b = per_item(pr, metric, name), per_item(base, metric, name)
        keys = sorted(set(a) & set(b))
        value = sum(a.values()) / len(a) if a else None
        fail = value is None or ("min" in rule and value < rule["min"])
        note = ""
        if rule.get("no_significant_drop") and keys:
            d, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027))
            note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
            fail |= hi < 0
        ident = f"slice:{name}/{metric}"
        if fail and rule.get("blocking"):
            blocked.append(ident)
        lines.append(f"  {ident} {value} {note} {'BLOCK' if fail and rule.get('blocking') else 'warn' if fail else 'ok'}")
    return blocked, lines


def check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> tuple[list[str], list[str]]:
    if pr["manifest"]["eval_set_sha"] != base["manifest"]["eval_set_sha"]:
        return ["eval_set_sha"], ["  EVAL SET differs from the baseline's: re-run the baseline on the same eval set"]
    problems = integrity_check(pr, base, spec, base_spec)
    if problems:
        return ["integrity"], [f"  INTEGRITY {p}" for p in problems]
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for m in spec["metrics"]:
        mid, th, val = m["id"], m.get("threshold", {}), pr["metrics"].get(m["id"])
        verdict, note = "ok", ""
        if val is None:
            verdict = "missing"
        elif "max" in th and val > th["max"]:
            verdict = "fail"
        elif "min" in th and val < th["min"]:
            verdict = "fail"
        elif "max_increase" in th and base["metrics"].get(mid):
            if val > base["metrics"][mid] * (1 + th["max_increase"]):
                verdict = "fail"
        if th.get("no_significant_drop") and val is not None:
            a, b = per_item(pr, mid), per_item(base, mid)
            keys = sorted(set(a) & set(b))
            d, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                                               n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027))
            note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
            if hi < 0:
                verdict = "fail"
        if verdict != "ok" and m.get("blocking"):
            blocked.append(mid)
        label = {"ok": "ok", "missing": "MISSING"}.get(verdict, "BLOCK" if m.get("blocking") else "warn")
        lines.append(f"  {mid:<22} {val!s:<8} {json.dumps(th):<40} {note:<28} {label}")
    if spec.get("slices"):
        sb, sl = slice_check(pr, base, spec)
        blocked += sb
        lines += sl
    return blocked, lines


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9.gate")
    ap.add_argument("--pr", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--spec", default=str(SPEC))
    ap.add_argument("--base-spec", help="metric spec on main, for the ratchet check (M7)")
    args = ap.parse_args(argv)
    pr = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    base_spec = load_spec(Path(args.base_spec)) if args.base_spec else None
    blocked, lines = check(pr, base, load_spec(Path(args.spec)), base_spec)
    print(f"gate: PR {pr['run_id']} vs main {base['run_id']} · eval set {pr['manifest']['eval_set_sha']}")
    print("\n".join(lines))
    if blocked:
        print(f"exit 1 — blocked: {', '.join(blocked)}")
        return 1
    print("exit 0 — merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
