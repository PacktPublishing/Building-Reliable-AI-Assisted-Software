"""
Deterministic simulation layer for the Chapter 1 notebook.

Companion repository for "Building Reliable AI-Assisted Software Systems"
Chapter 1: The Reliability Gap
Author: Imran Ahmad

Chapter 1 argues from architecture rather than code, with one deliberate
exception: Listing 1.1, five identical calls that rarely produce one
identical answer. This module lets the notebook demonstrate that behavior,
and the chapter's other quantitative claims, fully offline: a seeded mock
of a chat model that paraphrase-samples like the real thing, a demo-vs-
production traffic simulator for the 80/20 Demo Trap, and a tiny agent
loop whose action sequences drift across runs.

Everything is seeded per item (``random.Random(f"{SEED}:{tag}")``), so two
consecutive runs of the notebook are byte-identical.
"""

from __future__ import annotations

from random import Random

__author__ = "Imran Ahmad"

SEED = 42

CANON_CH1 = {
    "CALLS": 5,
    "STEP_RELIABILITY": 0.90,
    "CHAIN_STEPS": 5,
    "CHAINED": round(0.90 ** 5, 4),          # ~0.59: the compounding gap
    "DEMO_QUESTIONS": 12,
    "PROD_TICKETS": 500,
    "AGENT_RUNS": 10,
    "AGENT_STEPS": 6,
}

# --------------------------------------------------------------------------- #
# The mock model: same prompt in, a sampled paraphrase out.                    #
# --------------------------------------------------------------------------- #

_REFUND_PARAPHRASES = [
    "Refunds are available for 30 days after purchase.",
    "You can get a refund within 30 days.",
    "Our refund window is 30 days from the purchase date.",
    "Purchases can be refunded up to 30 days after you buy.",
    "You have a 30-day window to request a refund.",
]

_GENERIC_PARAPHRASES = [
    "Happy to help with that. Could you share a few more details?",
    "Sure, here is what I found on that topic.",
    "Thanks for asking. The short answer is that it depends on your plan.",
    "Here is a quick summary of how that works.",
]


def mock_complete(prompt: str, run: int) -> str:
    """One sampled answer to one prompt: deterministic per (prompt, run).

    The mock reproduces the property Listing 1.1 demonstrates: identical
    inputs fan out across semantically similar, lexically distinct outputs.
    """
    rng = Random(f"{SEED}:{prompt}:{run}")
    pool = _REFUND_PARAPHRASES if "refund" in prompt.lower() else _GENERIC_PARAPHRASES
    return rng.choice(pool)


def live_complete_or_mock(prompt: str, run: int) -> str:
    """Use a real model when a key is present; fall back to the mock.

    Lazy import so Simulation Mode never needs the ``openai`` package.
    """
    import os

    if not os.getenv("OPENAI_API_KEY"):
        return mock_complete(prompt, run)
    try:
        from openai import OpenAI

        client = OpenAI()
        response = client.responses.create(
            model=os.getenv("SUPPORT_LIVE_MODEL", "gpt-4o-mini"), input=prompt
        )
        return response.output_text.strip()
    except Exception:
        return mock_complete(prompt, run)


# --------------------------------------------------------------------------- #
# The 80/20 Demo Trap, simulated: two input distributions, one system.         #
# --------------------------------------------------------------------------- #

# Success probability of the same prototype per traffic slice. Illustrative
# values: the demo samples only the first slice; production samples them all.
_SLICE_PROFILE: dict[str, tuple[float, float]] = {
    # slice: (share of production traffic, prototype success rate)
    "clean, common questions": (0.55, 0.96),
    "ambiguous phrasing": (0.20, 0.70),
    "multi-part tickets": (0.12, 0.55),
    "edge-case policies": (0.08, 0.42),
    "adversarial or hostile": (0.05, 0.30),
}


def run_traffic(kind: str, n: int) -> tuple[int, dict[str, tuple[int, int]]]:
    """Simulate n requests of 'demo' or 'production' traffic.

    Returns (passes, {slice: (passes, total)}). Deterministic per (kind, n).
    """
    rng = Random(f"{SEED}:traffic:{kind}:{n}")
    slices = list(_SLICE_PROFILE)
    weights = [_SLICE_PROFILE[s][0] for s in slices]
    per_slice: dict[str, list[int]] = {s: [0, 0] for s in slices}
    for _ in range(n):
        s = slices[0] if kind == "demo" else rng.choices(slices, weights)[0]
        ok = rng.random() < _SLICE_PROFILE[s][1]
        per_slice[s][0] += int(ok)
        per_slice[s][1] += 1
    passes = sum(v[0] for v in per_slice.values())
    return passes, {s: (v[0], v[1]) for s, v in per_slice.items() if v[1]}


# --------------------------------------------------------------------------- #
# A model in a loop: the same task, divergent action sequences.                #
# --------------------------------------------------------------------------- #

_ACTIONS = ["search_kb", "read_ticket", "draft_reply", "check_policy",
            "ask_clarifying", "escalate"]


def run_agent(run: int, steps: int = 6) -> list[str]:
    """One agent run: a sampled action sequence for the same fixed task.

    Sampling, context drift, and tool outcomes each add randomness; here one
    seeded choice per step stands in for all three layers.
    """
    rng = Random(f"{SEED}:agent:{run}")
    sequence = ["read_ticket"]
    for _ in range(steps - 1):
        options = [a for a in _ACTIONS if a != sequence[-1]]
        sequence.append(rng.choice(options))
        if sequence[-1] == "escalate":
            break
    return sequence


if __name__ == "__main__":
    answers = {mock_complete("In one short sentence, what is the refund window?", r)
               for r in range(CANON_CH1["CALLS"])}
    assert 1 < len(answers) <= CANON_CH1["CALLS"]
    d1 = run_traffic("demo", CANON_CH1["DEMO_QUESTIONS"])
    d2 = run_traffic("demo", CANON_CH1["DEMO_QUESTIONS"])
    assert d1 == d2, "traffic simulation must be deterministic"
    seqs = {tuple(run_agent(r)) for r in range(CANON_CH1["AGENT_RUNS"])}
    assert len(seqs) > 1
    print(f"model_sim self-test: {len(answers)} distinct answers from "
          f"{CANON_CH1['CALLS']} identical calls, deterministic traffic, "
          f"{len(seqs)} distinct agent trajectories in {CANON_CH1['AGENT_RUNS']} runs.")
