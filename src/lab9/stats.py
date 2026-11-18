"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    if len(human) != len(judge) or not human or any(x not in ("PASS", "FAIL") for x in [*human, *judge]):
        raise ValueError("expected equally sized, nonempty PASS/FAIL labels")
    return {"tp": sum(h == POS and j == POS for h, j in zip(human, judge)),
            "fp": sum(h != POS and j == POS for h, j in zip(human, judge)),
            "fn": sum(h == POS and j != POS for h, j in zip(human, judge)),
            "tn": sum(h != POS and j != POS for h, j in zip(human, judge))}


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    c = confusion(human, judge)
    return (c["tp"] / (c["tp"] + c["fp"]) if c["tp"] + c["fp"] else 0.0,
            c["tp"] / (c["tp"] + c["fn"]) if c["tp"] + c["fn"] else 0.0)


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """kappa = (p_o - p_e) / (1 - p_e). Raise ValueError when undefined (p_e == 1):
    a constant judge has no signal and must FAIL calibration, not pass on a technicality."""
    c = confusion(human, judge)
    n = len(human)
    observed = (c["tp"] + c["tn"]) / n
    expected = ((c["tp"] + c["fn"]) * (c["tp"] + c["fp"]) +
                (c["tn"] + c["fp"]) * (c["tn"] + c["fn"])) / n**2
    if expected == 1:
        raise ValueError("kappa undefined")
    return (observed - expected) / (1 - expected)


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct an observed failure rate for judge error; clip to [0, 1]."""
    denominator = sensitivity + specificity - 1
    if denominator <= 0:
        raise ValueError("judge must be better than chance")
    return max(0.0, min(1.0, (observed_rate + specificity - 1) / denominator))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    import numpy as np
    from scipy.stats import bootstrap
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.size == 0 or a.shape != b.shape:
        raise ValueError("paired samples must be equally sized and nonempty")
    d = float(np.mean(a - b))
    if np.array_equal(a, b):
        return 0.0, 0.0, 0.0
    result = bootstrap((a, b), lambda x, y, axis: np.mean(x - y, axis=axis), paired=True,
                       method="percentile", n_resamples=n_resamples, confidence_level=confidence,
                       rng=np.random.default_rng(rng))
    return d, float(result.confidence_interval.low), float(result.confidence_interval.high)


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    from math import comb
    if any(not isinstance(x, int) or isinstance(x, bool) for x in (n, c, k)) or n < 1 or c < 0 or c > n or k < 1 or k > n:
        raise ValueError("invalid n, c, k")
    return 1 - (comb(n - c, k) if n - c >= k else 0) / comb(n, k)


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    from math import comb
    if any(not isinstance(x, int) or isinstance(x, bool) for x in (n, c, k)) or n < 1 or c < 0 or c > n or k < 1 or k > n:
        raise ValueError("invalid n, c, k")
    return (comb(c, k) if c >= k else 0) / comb(n, k)
