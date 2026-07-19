"""
Arithmetic locks and behavior gates for the Chapter 2 notebook.

Companion repository for "Building Reliable AI-Assisted Software Systems"
Chapter 2: The Engineering Mindset for AI
Author: Imran Ahmad
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from support_shell import (  # noqa: E402
    CANON_CH2,
    CORPUS,
    ESCALATE_TO_HUMAN,
    EMAIL_RE,
    INVOICE_RE,
    MINI_GOLDEN,
    MockLLM,
    ContextAssembler,
    InputGuard,
    IntentRouter,
    OutputGuard,
    SemanticJudge,
    TICKETS,
    ToyRetriever,
    redact,
)


def test_weekend_bill_arithmetic() -> None:
    # 13 stranded nodes x $30/hr x a 60-hour weekend.
    assert (CANON_CH2["ROLLOUT_ATTEMPTS"]
            * CANON_CH2["NODE_RATE_USD_PER_HR"]
            * CANON_CH2["WEEKEND_HOURS"]
            == CANON_CH2["WEEKEND_BILL_USD"] == 23_400)


def test_listing_2_1_runs_disagree_on_substance() -> None:
    runs = [MockLLM() for _ in range(1)][0]
    prompt = "You are a helpful assistant. Can I get a refund on my license?"
    answers = [runs.complete(prompt) for _ in range(CANON_CH2["RUNS"])]
    assert len(set(answers)) == CANON_CH2["RUNS"]
    assert any(f"${CANON_CH2['ANNUAL_PRICE_USD']:,}" in a for a in answers)
    assert any("store credit" in a for a in answers)
    assert any(a.endswith("?") for a in answers)
    # and the drift itself reproduces across notebook runs
    again = [MockLLM().complete(prompt) if i == 0 else None for i in range(1)][0]
    assert again == answers[0]


def test_input_guard_blocks_the_injection() -> None:
    guard = InputGuard()
    assert guard.is_safe(TICKETS["howto"])
    assert not guard.is_safe(TICKETS["injection"])


def test_output_guard_escalates_the_unauthorized_promise() -> None:
    guard = OutputGuard()
    promise = "Yes - a full $4,200 refund is on its way."
    annual = CORPUS["refunds-annual-licenses"]
    assert guard.enforce(promise, annual) == ESCALATE_TO_HUMAN
    safe = "Open the Render Queue panel, select the job, choose Cancel."
    assert guard.enforce(safe, annual) == safe


def test_redaction_strips_pii_patterns() -> None:
    leaky = "Confirming: your email is mara.j@example.com, invoice INV-88214."
    clean = redact(leaky, patterns=[EMAIL_RE, INVOICE_RE])
    assert "example.com" not in clean and "INV-88214" not in clean
    assert clean.count("[REDACTED]") == 2


def test_toy_retriever_reproduces_the_wrong_doc_failure() -> None:
    refunds_only = {k: v for k, v in CORPUS.items() if k.startswith("refunds")}
    retriever = ToyRetriever(refunds_only)
    assert retriever.search(TICKETS["refund"], k=1) == ["refunds-monthly-trial"]
    retriever.pin_document("refunds-annual-licenses")
    assert retriever.search(TICKETS["refund"], k=1) == ["refunds-annual-licenses"]


def test_the_shell_contains_what_the_vibe_path_ships() -> None:
    input_guard, output_guard = InputGuard(), OutputGuard()
    context = ContextAssembler(ToyRetriever(
        {k: v for k, v in CORPUS.items() if k.startswith("refunds")}))
    router = IntentRouter()

    # the injection dies at the gate
    assert not input_guard.is_safe(TICKETS["injection"])

    # the refund ticket: wrong doc retrieved, wrong draft, contained on exit
    served = context.assemble(TICKETS["refund"],
                              max_tokens=CANON_CH2["CONTEXT_BUDGET_TOKENS"])
    draft = router.dispatch(TICKETS["refund"], served)
    assert f"${CANON_CH2['ANNUAL_PRICE_USD']:,}" in draft
    assert output_guard.enforce(draft, served) == ESCALATE_TO_HUMAN


def test_semantic_judge_grades_the_mini_golden_set() -> None:
    judge = SemanticJudge()
    assert judge.matches("escalate", ESCALATE_TO_HUMAN)
    assert judge.matches(
        "answer_howto",
        "Open the Render Queue panel, select the job, choose Cancel, then Requeue.")
    assert len(MINI_GOLDEN) == 4
