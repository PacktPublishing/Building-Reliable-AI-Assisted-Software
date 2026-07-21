# Chapter 1: The Reliability Gap

Companion repository for **_Building Reliable AI-Assisted Software Systems_** (Packt Publishing) · **Author: Imran Ahmad**

> **Simulation Mode: works with zero keys, zero setup.** The notebook runs
> top-to-bottom fully offline against a seeded mock model, so two
> consecutive runs are byte-identical. The first code cell prints a green
> `SIMULATION MODE` banner to confirm it. With an `OPENAI_API_KEY` in
> `.env`, Listing 1.1 calls a real model instead, exactly as printed.

## What this chapter's repo demonstrates

- **Listing 1.1, the chapter's one program.** Five identical calls, and
  rarely one identical answer: the mechanical difference that breaks
  exact-match testing.
- **The compounding gap.** The five-step chain at ninety percent per step,
  and the reliability curve that argues the book's thesis in one chart.
- **The 80/20 Demo Trap, simulated.** The same prototype scoring a
  flawless demo and roughly four-in-five on production traffic, because
  the demo samples only the friendliest slice.
- **A model in a loop.** Ten runs of the same task, a spread of distinct
  action trajectories: output variance becoming behavior variance.
- **The poet and the accountant.** Each observation mapped to the ring of
  the deterministic shell that answers it.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter lab
```

Open `chapter_01_the_reliability_gap.ipynb` and **Run All**. Optional
sanity checks: `python model_sim.py` prints a self-test line, and
`pytest tests/` locks the chapter's arithmetic.

## Repository map

| Path | What it is |
| --- | --- |
| `chapter_01_the_reliability_gap.ipynb` | The chapter, executable: objectives, five acts, summary, exercises |
| `model_sim.py` | The seeded mock model, the demo-vs-production traffic simulator, and the toy agent loop |
| `tests/test_canon.py` | Arithmetic locks: the compounding math, the fan-out, determinism |
| `resilience.py` | Color logging and mode detection (same API across all chapter bundles) |

## License

MIT (see `LICENSE`).

## Standalone notebook editions

Beyond the main chapter notebook, the bundle ships a standalone script and four provider editions of the same walkthrough:

- `ch01_reliability_gap.py` — the whole chapter in one linear script (no key, no network)
- `ch01_reliability_gap_claude.ipynb` · `_openai.ipynb` · `_gemini.ipynb` · `_deepseek_ollama.ipynb` — identical canonical content plus one optional live probe per provider (`requirements-providers.txt`)

Every edition runs fully offline by default and reproduces the chapter's canonical numbers. Live probes are side paths and never feed the canonical numbers.
