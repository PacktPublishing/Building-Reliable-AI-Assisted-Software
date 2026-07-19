# Chapter 3: Defining Correctness and Golden Datasets

Companion repository for **_Building Reliable AI-Assisted Software Systems_** (Packt Publishing) · **Author: Imran Ahmad**

> **Simulation Mode: works with zero keys, zero setup.** The notebook runs
> top-to-bottom fully offline: no `.env`, no accounts, no network. Every
> response comes from the committed snapshot of `support-assistant-v0.9`
> (the build that shipped the refund incident), so two consecutive runs are
> byte-identical. The first code cell prints a green `SIMULATION MODE`
> banner to confirm it.

## What this chapter's repo demonstrates

- **Watch `assert ==` die.** A unit test rejects a perfect answer, and the
  same question turns out to have opposite correct answers depending on the
  context served with it.
- **Read a correctness profile.** One password-reset answer scores high on
  six dimensions and collapses on the seventh, and the blended average hides
  exactly the axis with a cost attached.
- **Write the rubric as code.** Six criteria with calibration pairs; the
  deterministic half runs as plain string checks, including the check that
  would have caught the incident. The judge tier exists only as a stub that
  raises `NotImplementedError("Chapter 4 builds the judge.")`.
- **Build the golden dataset.** 240 raw, unlabeled tickets curated into 150
  typed `GoldenExample` records across six intent categories, with the
  eleven money-back phrasings, refusal cases, and the incident preserved as
  `golden_0047`.
- **Version it as code.** A hash manifest with a tamper alarm, a mechanical
  held-out split, and a staleness demo that flags every case a policy
  change touches.
- **Meet the honest number.** The committed hand-grading sheet counts to
  108 of 150, and the per-category slices tell the sharper story.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter lab
```

Open `chapter_03_golden_datasets.ipynb` and **Run All**. No `.env` is
needed. Optional sanity checks from the shell: `python support_mock.py`
prints a green self-test pass, and `pytest tests/` runs the arithmetic
locks that keep every number in the chapter honest.

## Repository map

| Path | What it is |
| --- | --- |
| `chapter_03_golden_datasets.ipynb` | The chapter, executable: objectives, five acts, case file, summary, exercises |
| `support_mock.py` | Canon numbers, the C1-C6 rubric, the 150-case plan, and the frozen assistant |
| `make_dataset.py` | The deterministic generator that authored `data/` (re-running it reproduces every file byte-for-byte) |
| `data/policies/` | The four policy documents the cases cite |
| `data/tickets_raw.jsonl` | 240 raw, unlabeled tickets (Exercise 2 curates from these) |
| `data/golden_v1.0.jsonl` + `data/golden_MANIFEST.json` | The golden dataset and its tamper-evident seal |
| `data/assistant_snapshot_v0.9.jsonl` | The frozen assistant's answers, one per case |
| `data/grades_v1.0.csv` + `data/calibration_pass.csv` | The completed grade sheet and the double-graded calibration overlap |
| `tests/test_canon.py` | Arithmetic locks: category sums, failure-script totals, manifest hash, snapshot regeneration |
| `resilience.py` | Color logging, `@graceful_fallback`, and mode detection (same API as Chapter 2) |

## Live Mode (optional)

Copy `.env.template` to `.env` and add an `OPENAI_API_KEY` to point the same
harness at a real model through `LiveAssistantAdapter` (default model
`gpt-4o-mini`, override with `SUPPORT_LIVE_MODEL`). Every live call is
wrapped in `@graceful_fallback`, so a failure drops back to the mock and the
notebook keeps running. None of the chapter's numbers depend on Live Mode.

## A note on eval tooling

The chapter is deliberately tool-agnostic: JSONL, git, and Pydantic are the
whole stack, because datasets and rubrics outlive platforms. When you want a
managed harness around the same ideas, the usual suspects are promptfoo,
DeepEval, Ragas, and LangSmith datasets; every concept in this chapter maps
onto all four.

## License

MIT (see `LICENSE`).
