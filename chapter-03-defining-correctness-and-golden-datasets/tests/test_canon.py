"""
Arithmetic locks and integrity gates for the Chapter 3 data artifacts.

Companion repository for "Building Reliable AI-Assisted Software Systems"
Chapter 3: Defining Correctness and Golden Datasets
Author: Imran Ahmad

Every number the chapter prints is asserted here against the committed
files, so a drive-by edit to any artifact turns the suite red.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BUNDLE))

from support_mock import (  # noqa: E402
    CANON,
    CASE_PLAN,
    CATEGORIES,
    CRITERIA,
    FAILURE_SCRIPT,
    MONEY_BACK_PHRASINGS,
    MockSupportAssistant,
    POLICY_ANNUAL,
    GoldenExample,
)

DATA = BUNDLE / "data"


def _golden_lines() -> list[dict]:
    return [json.loads(line)
            for line in (DATA / "golden_v1.0.jsonl").read_text().splitlines()
            if line.strip()]


def _grades() -> list[dict[str, str]]:
    with open(DATA / "grades_v1.0.csv", newline="") as fh:
        return list(csv.DictReader(fh))


def test_category_counts_and_totals() -> None:
    cases = _golden_lines()
    assert len(cases) == CANON["GOLDEN_CASES"] == 150
    by_cat = Counter(c["tags"][0] for c in cases)
    for cat, spec in CATEGORIES.items():
        assert by_cat[cat] == spec["cases"], cat
    assert sum(spec["cases"] for spec in CATEGORIES.values()) == 150
    assert sum(spec["pass"] for spec in CATEGORIES.values()) == CANON["PASS_COUNT"] == 108


def test_every_record_validates_against_the_schema() -> None:
    for raw in _golden_lines():
        case = GoldenExample.model_validate(raw)
        assert case.rationale
        assert case.tags[0] in CATEGORIES


def test_grades_match_the_failure_script() -> None:
    grades = _grades()
    assert len(grades) == 150
    passes = [g for g in grades if g["verdict"] == "pass"]
    fails = [g for g in grades if g["verdict"] == "fail"]
    assert len(passes) == CANON["PASS_COUNT"] == 108
    assert len(fails) == CANON["FAIL_COUNT"] == 42
    # per-category passes
    per_cat = Counter(g["category"] for g in passes)
    for cat, spec in CATEGORIES.items():
        assert per_cat[cat] == spec["pass"], cat
    # per-(category, criterion) failure totals equal the failure script
    expected: Counter[tuple[str, str]] = Counter()
    for _mode, (criterion, counts) in FAILURE_SCRIPT.items():
        for cat, k in counts.items():
            expected[(cat, criterion)] += k
    actual = Counter((g["category"], g["failed_criterion"]) for g in fails)
    assert actual == expected
    # every fail names exactly one criterion; every pass names none
    assert all(g["failed_criterion"] in CRITERIA for g in fails)
    assert all(g["failed_criterion"] == "" for g in passes)
    # every note is grader-voiced and short
    assert all(0 < len(g["note"]) <= 120 for g in grades)


def test_grader_split_is_by_id_parity() -> None:
    grades = _grades()
    for g in grades:
        n = int(g["case_id"][-4:])
        assert g["grader"] == ("lead" if n % 2 else "ops")
    split = Counter(g["grader"] for g in grades)
    assert split["lead"] == split["ops"] == 75


def test_held_out_rule_yields_exactly_thirty() -> None:
    held = [c["id"] for c in _golden_lines() if int(c["id"][-4:]) % 5 == 0]
    assert len(held) == CANON["HELD_OUT"] == 30
    assert 150 - len(held) == CANON["DEV_CASES"] == 120


def test_calibration_pass_has_three_c5_disputes() -> None:
    with open(DATA / "calibration_pass.csv", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == CANON["DOUBLE_GRADED"] == 10
    disputes = [r for r in rows if r["lead_verdict"] != r["ops_verdict"]]
    assert len(disputes) == CANON["DISAGREEMENTS_BEFORE"] == 3
    assert all(r["disputed_criterion"] == "C5" for r in disputes)
    assert all(r["disputed_criterion"] == "" for r in rows if r not in disputes)
    grades = {g["case_id"]: g["verdict"] for g in _grades()}
    assert all(r["resolved_verdict"] == grades[r["case_id"]] for r in rows)


def test_manifest_sha_matches_the_committed_file() -> None:
    manifest = json.loads((DATA / "golden_MANIFEST.json").read_text())
    digest = hashlib.sha256((DATA / "golden_v1.0.jsonl").read_bytes()).hexdigest()
    assert manifest["sha256"] == digest
    assert manifest["case_count"] == 150
    assert manifest["version"] == CANON["DATASET_VERSION"]
    assert manifest["model_under_test"] == CANON["MODEL_UNDER_TEST"]


def test_snapshot_matches_regeneration_byte_for_byte() -> None:
    committed = (DATA / "assistant_snapshot_v0.9.jsonl").read_text().splitlines()
    regenerated = [json.dumps(r, ensure_ascii=False)
                   for r in MockSupportAssistant().regenerate_snapshot()]
    assert committed == regenerated


def test_anchor_verdicts() -> None:
    grades = {g["case_id"]: g for g in _grades()}
    assert grades["golden_0047"]["verdict"] == "fail"
    assert grades["golden_0047"]["failed_criterion"] == "C1"
    assert grades["golden_0093"]["verdict"] == "fail"
    assert grades["golden_0093"]["failed_criterion"] == "C4"
    assert grades["golden_0104"]["verdict"] == "fail"
    assert grades["golden_0104"]["failed_criterion"] == "C6"
    for cid in ("golden_0001", "golden_0002", "golden_0011", "golden_0050"):
        assert grades[cid]["verdict"] == "pass", cid
    anchors = ["golden_0002", "golden_0011", "golden_0047",
               "golden_0050", "golden_0093", "golden_0104"]
    verdicts = Counter(grades[a]["verdict"] for a in anchors)
    assert verdicts["pass"] == verdicts["fail"] == 3


def test_the_eleven_phrasings_are_present_verbatim() -> None:
    cases = {c["id"]: c for c in _golden_lines()}
    assert len(MONEY_BACK_PHRASINGS) == CANON["PHRASING_COUNT"] == 11
    for cid, phrasing in MONEY_BACK_PHRASINGS.items():
        assert cases[cid]["input"] == phrasing
        assert cases[cid]["tags"][0] == "refund_policy"
    tickets = (DATA / "tickets_raw.jsonl").read_text()
    for phrasing in MONEY_BACK_PHRASINGS.values():
        assert phrasing in tickets


def test_ticket_corpus_shape() -> None:
    lines = [json.loads(line)
             for line in (DATA / "tickets_raw.jsonl").read_text().splitlines()
             if line.strip()]
    assert len(lines) == CANON["RAW_TICKETS"] == 240
    ids = [t["ticket_id"] for t in lines]
    assert ids == [f"T-{n}" for n in range(1001, 1241)]
    assert all(t["body"].strip() for t in lines)
    assert all(t["channel"] in {"email", "chat", "phone_transcript"} for t in lines)
    # no intent labels: curation is the reader's exercise
    assert all("category" not in t and "intent" not in t for t in lines)


def test_c3_passes_and_fails_its_own_calibration_pair() -> None:
    c3 = CRITERIA["C3"]
    assert c3.check is not None
    assert c3.check(c3.pass_example, POLICY_ANNUAL) is True
    assert c3.check(c3.fail_example, POLICY_ANNUAL) is False


def test_stale_monthly_guarantee_cases_number_four() -> None:
    tagged = [c["id"] for c in _golden_lines() if "monthly_guarantee" in c["tags"]]
    assert len(tagged) == CANON["STALE_CASES"] == 4
    assert "golden_0050" in tagged


def test_case_plan_is_stable() -> None:
    # The plan is the single source of truth; two imports must agree.
    from importlib import reload
    import support_mock as sm
    before = dict(sm.CASE_PLAN)
    reload(sm)
    assert before == sm.CASE_PLAN
