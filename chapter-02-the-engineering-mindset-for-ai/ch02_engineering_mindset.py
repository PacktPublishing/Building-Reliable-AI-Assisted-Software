#!/usr/bin/env python3
"""Chapter 2 standalone: from artisanal habit to engineering shell.

Author: Imran Ahmad
Companion code for *Building Reliable AI-Assisted Software Systems* (Packt).
All characters, companies, incidents, and data are fictional.

Runs fully offline against the seeded support layer (Simulation Mode is the
canonical path; nothing here calls a provider). Every printed number
reproduces identically on every run.
"""
from __future__ import annotations

from support_shell import (
    CANON_CH2,
    EMAIL_RE,
    INJECTION_PATTERNS,
    INVOICE_RE,
    TICKETS,
    complete,
    promises_refund_over,
    redact,
)


def main() -> None:
    # --- 1. Five runs of one prompt disagree on substance -------------------
    prompt = "Can I get a refund on the annual license we bought?"
    replies = [complete(prompt, run=r) for r in range(CANON_CH2["RUNS"])]
    for i, r in enumerate(replies, 1):
        print(f"[run {i}] {r}")
    promising = [r for r in replies
                 if promises_refund_over(r, CANON_CH2["APPROVAL_CEILING_USD"])]
    assert len(promising) >= 1, "the scripted drift must include the bad promise"
    print(f"[1] {CANON_CH2['RUNS']} runs, {len(promising)} reply promising a refund "
          f"above the ${CANON_CH2['APPROVAL_CEILING_USD']} ceiling: "
          "same prompt, different substance\n")

    # --- 2. The guard catches the promise the vibe check missed -------------
    bad = promising[0]
    assert promises_refund_over(bad, CANON_CH2["APPROVAL_CEILING_USD"]) is True
    print(f"[2] output guard on run 1: BLOCKED ({bad!r} promises "
          f"${CANON_CH2['ANNUAL_PRICE_USD']:,} above the "
          f"${CANON_CH2['APPROVAL_CEILING_USD']} ceiling)\n")

    # --- 3. The injection ticket never reaches the model --------------------
    attack = TICKETS["injection"]
    hit = next(p for p in INJECTION_PATTERNS if p in attack.lower())
    print(f"[3] input guard on the injection ticket: BLOCKED "
          f"(matched pattern {hit!r})\n")

    # --- 4. Redaction guards the inbound side -------------------------------
    sample = "Reach me at jan@example.studio about INV-20411, please."
    print(f"[4] redaction: {redact(sample, [EMAIL_RE, INVOICE_RE])!r}\n")

    # --- 5. Honest arithmetic for unbounded automation ----------------------
    bill = (CANON_CH2["ROLLOUT_ATTEMPTS"] * CANON_CH2["NODE_RATE_USD_PER_HR"]
            * CANON_CH2["WEEKEND_HOURS"])
    assert bill == CANON_CH2["WEEKEND_BILL_USD"] == 23_400
    print(f"[5] {CANON_CH2['ROLLOUT_ATTEMPTS']} retries x "
          f"${CANON_CH2['NODE_RATE_USD_PER_HR']}/hr x "
          f"{CANON_CH2['WEEKEND_HOURS']}h = ${bill:,}: "
          "unbounded automation, priced\n")

    print(f"the shell holds: promise blocked, injection blocked, PII redacted, "
          f"eval threshold {CANON_CH2['EVAL_THRESHOLD']} on record")


if __name__ == "__main__":
    main()
