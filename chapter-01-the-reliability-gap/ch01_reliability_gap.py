#!/usr/bin/env python3
"""Chapter 1 standalone: the Reliability Gap, demonstrated end to end.

Author: Imran Ahmad
Companion code for *Building Reliable AI-Assisted Software Systems* (Packt).
All characters, companies, incidents, and data are fictional.

Runs fully offline against the seeded simulation layer (Simulation Mode is
the canonical path; nothing here calls a provider). Every printed number
reproduces identically on every run.
"""
from __future__ import annotations

from model_sim import CANON_CH1, mock_complete, run_agent, run_traffic


def main() -> None:
    # --- 1. Five identical calls, more than one answer ----------------------
    prompt = "In one short sentence, what is the refund window?"
    answers = [mock_complete(prompt, run) for run in range(CANON_CH1["CALLS"])]
    for i, a in enumerate(answers, 1):
        print(f"[call {i}] {a}")
    distinct = len(set(answers))
    assert 1 < distinct <= CANON_CH1["CALLS"]
    print(f"[1] {CANON_CH1['CALLS']} identical calls, {distinct} distinct answers: "
          "assert actual == expected has no single 'actual' to pin\n")

    # --- 2. Reliability compounds down a chain ------------------------------
    step, steps = CANON_CH1["STEP_RELIABILITY"], CANON_CH1["CHAIN_STEPS"]
    chained = round(step ** steps, 4)
    assert chained == CANON_CH1["CHAINED"]
    print(f"[2] {step:.0%} per step across {steps} steps = {chained:.0%} "
          "end-to-end: reliability multiplies down a chain, it does not average\n")

    # --- 3. The 80/20 Demo Trap ---------------------------------------------
    demo_passes, _ = run_traffic("demo", CANON_CH1["DEMO_QUESTIONS"])
    prod_passes, slices = run_traffic("production", CANON_CH1["PROD_TICKETS"])
    print(f"[3] demo: {demo_passes}/{CANON_CH1['DEMO_QUESTIONS']} flawless; "
          f"production: {prod_passes}/{CANON_CH1['PROD_TICKETS']} "
          f"({prod_passes * 100 / CANON_CH1['PROD_TICKETS']:.1f}%)")
    for name, (ok, total) in slices.items():
        print(f"      {name:<24} {ok}/{total}")
    print()

    # --- 4. A model in a loop drifts ----------------------------------------
    runs = CANON_CH1["AGENT_RUNS"]
    trajectories = {tuple(run_agent(r)) for r in range(runs)}
    print(f"[4] same task, {runs} agent runs, {len(trajectories)} distinct "
          "action sequences: the loop compounds the fan-out")

    print(f"\nthe gap: demo {demo_passes}/{CANON_CH1['DEMO_QUESTIONS']}, "
          f"production {prod_passes}/{CANON_CH1['PROD_TICKETS']}")


if __name__ == "__main__":
    main()
