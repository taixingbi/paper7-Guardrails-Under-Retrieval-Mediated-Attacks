from gurma.eval.bootstrap import bootstrap_ci, fmt_ci


def test_bootstrap_ci_all_zeros():
    ci = bootstrap_ci([False] * 40, n_boot=200, seed=0)
    assert ci["low"] == 0.0
    assert ci["high"] == 0.0
    assert ci["n"] == 40


def test_bootstrap_ci_all_ones():
    ci = bootstrap_ci([True] * 20, n_boot=200, seed=1)
    assert ci["low"] == 1.0
    assert ci["high"] == 1.0


def test_bootstrap_ci_empty():
    ci = bootstrap_ci([], n_boot=100)
    assert ci["low"] is None
    assert ci["high"] is None


def test_fmt_ci():
    assert fmt_ci(0.3, {"low": 0.21, "high": 0.39}) == "0.300 [0.210, 0.390]"
    assert fmt_ci(None, None) == "—"
    assert fmt_ci(0.5, None) == "0.500"
