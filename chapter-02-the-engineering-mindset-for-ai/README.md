# Chapter 2: The Engineering Mindset for AI

Companion repository for **_Building Reliable AI-Assisted Software Systems_** (Packt Publishing) · **Author: Imran Ahmad**

> **Simulation Mode: works with zero keys, zero setup.** Every model
> response comes from a scripted, seeded mock, so the notebook runs
> top-to-bottom fully offline and two consecutive runs are byte-identical.
> The first code cell prints a green `SIMULATION MODE` banner to confirm it.

## What this chapter's repo demonstrates

All eight printed listings (2.1 through 2.8), runnable:

- **The artisanal failure.** One prompt, no shell, five runs that disagree
  on substance, including an unauthorized $4,200 refund promise, and the
  three-line handler that makes the failure inevitable.
- **The Deterministic Shell.** The same feature rebuilt as five named,
  independently testable layers around one model call, then both handlers
  fed the same hostile ticket and the same refund ticket. Inside the
  shell, retrieval still fails and the model still drafts the wrong
  promise; the customer never sees it.
- **`graceful_fallback`.** The shell at the scale of one risky call.
- **Four pillar miniatures.** An eval gate that blocks the artisanal
  handler and clears the shell; a naive retriever that reproduces the
  wrong-document failure and the seam that fixes it; bounded versus
  unbounded autonomy with the $23,400 weekend computed honestly; and
  deterministic guards on both sides of the model.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter lab
```

Open `chapter_02_the_engineering_mindset.ipynb` and **Run All**. Optional
sanity checks: `python support_shell.py` prints a green self-test pass,
and `pytest tests/` runs the behavior gates (the injection dies at the
gate, the promise escalates, the wrong document is fetched and then
pinned, the weekend arithmetic holds).

## Repository map

| Path | What it is |
| --- | --- |
| `chapter_02_the_engineering_mindset.ipynb` | The chapter, executable: objectives, five acts, summary, exercises |
| `support_shell.py` | The scripted mock model, the ticket cast, the policy corpus, and every layer the listings need |
| `tests/test_canon.py` | Behavior gates and the weekend-bill arithmetic |
| `resilience.py` | Color logging, `@graceful_fallback`, and mode detection (same API across all chapter bundles) |

## License

MIT (see `LICENSE`).
