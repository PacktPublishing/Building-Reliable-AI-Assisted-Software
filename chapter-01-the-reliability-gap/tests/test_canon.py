"""
Arithmetic locks for the Chapter 1 notebook's quantitative claims.

Companion repository for "Building Reliable AI-Assisted Software Systems"
Chapter 1: The Reliability Gap
Author: Imran Ahmad
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from model_sim import (  # noqa: E402
    CANON_CH1,
    mock_complete,
    run_agent,
    run_traffic,
)


def test_the_compounding_arithmetic() -> None:
    # The chapter's five-step chain at 90 percent per step.
    chained = CANON_CH1["STEP_RELIABILITY"] ** CANON_CH1["CHAIN_STEPS"]
    assert round(chained, 4) == CANON_CH1["CHAINED"] == 0.5905


def test_five_identical_calls_fan_out() -> None:
    prompt = "In one short sentence, what is the refund window?"
    answers = [mock_complete(prompt, r) for r in range(CANON_CH1["CALLS"])]
    unique = set(answers)
    assert 1 < len(unique) <= CANON_CH1["CALLS"]
    # and the fan-out itself is reproducible
    again = [mock_complete(prompt, r) for r in range(CANON_CH1["CALLS"])]
    assert answers == again


def test_demo_beats_production_by_construction() -> None:
    demo_pass, _ = run_traffic("demo", CANON_CH1["DEMO_QUESTIONS"])
    prod_pass, prod_slices = run_traffic("production", CANON_CH1["PROD_TICKETS"])
    demo_rate = demo_pass / CANON_CH1["DEMO_QUESTIONS"]
    prod_rate = prod_pass / CANON_CH1["PROD_TICKETS"]
    assert demo_rate > 0.85 > prod_rate > 0.60
    assert set(prod_slices) != {"clean, common questions"}


def test_traffic_simulation_is_deterministic() -> None:
    assert run_traffic("production", 500) == run_traffic("production", 500)


def test_agent_trajectories_diverge_but_reproduce() -> None:
    seqs = [tuple(run_agent(r)) for r in range(CANON_CH1["AGENT_RUNS"])]
    assert len(set(seqs)) >= 2                      # the loop compounds variance
    assert seqs == [tuple(run_agent(r)) for r in range(CANON_CH1["AGENT_RUNS"])]
