#!/usr/bin/env python3
"""Chapter 3 standalone: build, validate, and hand-grade the golden dataset.

Author: Imran Ahmad
Companion code for *Building Reliable AI-Assisted Software Systems* (Packt).
All characters, companies, incidents, and data are fictional.

Runs fully offline against the committed data artifacts (Simulation Mode is
the canonical path; nothing here calls a provider). Every printed number is
canon and reproduces identically on every run.
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

from support_mock import (
    CANON,
    CATEGORIES,
    CRITERIA,
    DATA_DIR,
    SEED,
    GoldenExample,
    MONEY_BACK_PHRASINGS,
)

random.seed(SEED)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    # --- 1. Integrity: the committed dataset matches its manifest -----------
    manifest = json.loads((DATA_DIR / "golden_MANIFEST.json").read_text())
    golden_path = DATA_DIR / "golden_v1.0.jsonl"
    assert sha256(golden_path) == manifest["sha256"], "dataset drifted from manifest"
    print(f"[1] golden v{manifest['version']}: hash verified, "
          f"{manifest['case_count']} cases expected")

    # --- 2. Schema validation + stratified counts ---------------------------
    cases = [GoldenExample.model_validate_json(line)
             for line in golden_path.read_text().splitlines() if line.strip()]
    assert len(cases) == int(CANON["GOLDEN_CASES"])
    counts = Counter(case.tags[0] for case in cases)
    assert dict(counts) == {k: v["cases"] for k, v in CATEGORIES.items()}
    print(f"[2] {len(cases)} records schema-validated; per-category counts match canon")

    # --- 3. The eleven money-back phrasings ---------------------------------
    family = {c.id: c for c in cases if c.id in MONEY_BACK_PHRASINGS}
    assert len(family) == int(CANON["PHRASING_COUNT"])
    print(f"[3] phrasing family present: {len(family)} cases "
          f"({min(family)}..{max(family)}), incident replay = golden_0047")

    # --- 4. One deterministic criterion, exercised on its calibration pair --
    c3 = CRITERIA["C3"]
    assert c3.check is not None
    assert c3.check(c3.pass_example, c3.pass_example) is True
    assert c3.check(c3.fail_example, c3.pass_example) is False
    print("[4] C3 calibration pair behaves: pass example passes, fail example fails")

    # --- 5. The hand-graded verdicts reproduce the honest number ------------
    with (DATA_DIR / "grades_v1.0.csv").open() as fh:
        rows = list(csv.DictReader(fh))
    passes = sum(row["verdict"] == "pass" for row in rows)
    fails = sum(row["verdict"] == "fail" for row in rows)
    rate = passes * 100 // len(rows)
    assert (passes, fails, rate) == (int(CANON["PASS_COUNT"]),
                                     int(CANON["FAIL_COUNT"]),
                                     int(CANON["PASS_RATE_PCT"]))
    print("[5] per-category slice rates:")
    for cat, spec in CATEGORIES.items():
        got = sum(r["verdict"] == "pass" for r in rows if r["category"] == cat)
        print(f"      {cat:<24} {got}/{spec['cases']:<3} = {got * 100 / spec['cases']:.1f}%")

    # --- 6. Held-out split by ID arithmetic ---------------------------------
    held = [c.id for c in cases if int(c.id[-4:]) % 5 == 0]
    print(f"[6] held-out split: {len(cases) - len(held)} dev / {len(held)} held out "
          "(mechanical, so nobody curates an easy holdout)")

    # --- 7. The final printout ----------------------------------------------
    print(f"\nthe count: {passes}/{len(rows)} = {rate}%")


if __name__ == "__main__":
    main()
