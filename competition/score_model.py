"""ADTC 2026 score model — Sprint Delta-0.

Predicts S_total from measured inputs, exactly where the formula is
published and with EXPLICIT parameterized assumptions where it is not.

Sources (verified 2026-07-03 against the live rules, not memory):
  - Devpost leaderboard scoring table (adtc-2026.devpost.com)
  - adtc-profiler source (github.com/Africa-Deep-Tech-Foundation/adtc-profiler)
  - adtc-2026-submission-template README

Exact (published formulas):
  S_eff     = 100 * (7GB - peak_ram_gb) / 7GB          [floor 0]
  P_thermal = 10 if temp > 85C or throttled else 0

Parameterized (NOT knowable in advance — do not pretend otherwise):
  S_perf = 100 * tps / tps_max  [capped 100]
    tps_max = "maximum observed across all teams". Unknown until close.
    Published anchor: TPS_REFERENCE = 15.0 (provisional). Sensitivity
    analysis across plausible tps_max values is mandatory in any report
    using this model.
  S_acc: judge panel + hidden per-domain validation subset. A local
    lm_eval proxy score (0-100) stands in; its mapping to the real
    S_acc is an assumption and must be labeled as such.
  African Use Case bonus: 0-10, judge-awarded.

    python3 -m competition.score_model          # self-test
"""

from __future__ import annotations

RAM_BUDGET_GB = 7.0
TPS_REFERENCE = 15.0  # provisional, published on Devpost


def s_eff(peak_ram_gb: float) -> float:
    """Exact published formula. Lower RAM -> higher score."""
    return max(0.0, 100.0 * (RAM_BUDGET_GB - peak_ram_gb) / RAM_BUDGET_GB)


def s_perf(tps: float, tps_max: float = TPS_REFERENCE) -> float:
    """Published shape; tps_max is an ASSUMPTION (max observed across teams)."""
    if tps_max <= 0:
        raise ValueError("tps_max must be positive")
    return min(100.0, 100.0 * tps / tps_max)


def p_thermal(max_temp_c: float | None, throttled: bool) -> float:
    """Exact published penalty. Cloud audit VMs often expose no sensor:
    temp None and not throttled -> no penalty."""
    if throttled:
        return 10.0
    if max_temp_c is not None and max_temp_c > 85.0:
        return 10.0
    return 0.0


def s_total(*, s_acc: float, tps: float, peak_ram_gb: float,
            max_temp_c: float | None = None, throttled: bool = False,
            african_bonus: float = 0.0, tps_max: float = TPS_REFERENCE) -> dict:
    """Full predicted score with per-component breakdown.

    s_acc (0-100) and african_bonus (0-10) are judge/hidden-benchmark
    driven — pass an estimate and LABEL it as an estimate downstream.
    """
    if not 0 <= s_acc <= 100:
        raise ValueError("s_acc must be 0-100")
    if not 0 <= african_bonus <= 10:
        raise ValueError("african_bonus must be 0-10")
    eff = s_eff(peak_ram_gb)
    perf = s_perf(tps, tps_max)
    therm = p_thermal(max_temp_c, throttled)
    total = 0.50 * s_acc + 0.30 * perf + 0.20 * eff - therm + african_bonus
    return {"s_acc": round(s_acc, 2), "s_perf": round(perf, 2),
            "s_eff": round(eff, 2), "p_thermal": therm,
            "african_bonus": african_bonus,
            "assumed_tps_max": tps_max,
            "s_total": round(total, 2)}


def from_profiler_report(report: dict, *, s_acc_estimate: float,
                         african_bonus: float = 0.0,
                         tps_max: float = TPS_REFERENCE) -> dict:
    """Score a real adtc-profiler submission.json / audit.json."""
    tps = report["throughput"]["tokens_per_second_generation"]
    peak_mb = report["memory"]["peak_rss_mb"]
    thermal = report.get("cpu_thermal", {}) or {}
    return s_total(s_acc=s_acc_estimate, tps=tps, peak_ram_gb=peak_mb / 1024.0,
                   max_temp_c=thermal.get("max_temp_c"),
                   throttled=bool(thermal.get("throttled", False)),
                   african_bonus=african_bonus, tps_max=tps_max)


def sensitivity(*, s_acc: float, tps: float, peak_ram_gb: float,
                african_bonus: float = 0.0,
                tps_max_scenarios: tuple = (15.0, 25.0, 50.0, 100.0)) -> list[dict]:
    """S_total across tps_max scenarios — mandatory companion to any point
    estimate, because tps_max is set by the fastest OTHER team."""
    return [s_total(s_acc=s_acc, tps=tps, peak_ram_gb=peak_ram_gb,
                    african_bonus=african_bonus, tps_max=m)
            for m in tps_max_scenarios]


def _selftest() -> None:
    # Exact formulas, hand-computed anchors.
    assert abs(s_eff(7.0) - 0.0) < 1e-9
    assert abs(s_eff(3.5) - 50.0) < 1e-9
    assert abs(s_eff(1.4) - 80.0) < 1e-9
    assert s_eff(8.0) == 0.0                       # floor, never negative
    assert abs(s_perf(15.0, 15.0) - 100.0) < 1e-9
    assert abs(s_perf(7.5, 15.0) - 50.0) < 1e-9
    assert s_perf(30.0, 15.0) == 100.0             # cap
    assert p_thermal(90.0, False) == 10.0
    assert p_thermal(80.0, False) == 0.0
    assert p_thermal(None, True) == 10.0
    assert p_thermal(None, False) == 0.0
    r = s_total(s_acc=80, tps=12, peak_ram_gb=1.4, african_bonus=10)
    # 0.5*80 + 0.3*(100*12/15) + 0.2*80 - 0 + 10 = 40 + 24 + 16 + 10 = 90
    assert abs(r["s_total"] - 90.0) < 1e-9, r
    rows = sensitivity(s_acc=80, tps=12, peak_ram_gb=1.4, african_bonus=10)
    assert rows[0]["s_total"] > rows[-1]["s_total"]  # higher tps_max hurts
    print("score_model selftest: all checks passed")
    print("example:", r)
    print("sensitivity (tps=12):", [(x["assumed_tps_max"], x["s_total"]) for x in rows])


if __name__ == "__main__":
    _selftest()
