# Phase 0.2 — clarifying-question eval results

**Status:** not yet run.

## How to run

```bash
# from repo root
python evals/clarifying_questions/runner.py --models gemini-flash gemini-flash-thinking
```

Output lands in `evals/clarifying_questions/runs/<model>-<timestamp>.jsonl`.
Open the file, hand-rate each row in the `score` field (1 / 0.5 / 0 per the
rubric in `runner.py`), then fill in the table below.

## Sample size

The committed `prompts.jsonl` has 15 prompts as a starting set. Expand to 50
before running for real — current set is enough to debug the runner but too
small to make a model decision.

## Results

| Model | Prompts rated | Mean score | Wins (score 1) | Mixed (0.5) | Fails (0) | Median latency |
|-------|----------------|------------|----------------|-------------|-----------|----------------|
| gemini-flash | — | — | — | — | — | — |
| gemini-flash-thinking | — | — | — | — | — | — |
| (claude-haiku-4.5) | — | — | — | — | — | — |

## Failure-mode notes

For each model, after rating, list the top 3 failure modes seen. Examples
to watch for:

- Sycophantic opener ("Great question — ...")
- Answers immediately instead of probing
- Asks two questions instead of one
- Hedges ("It depends on a few things...")
- Lists multiple options instead of asking

## Decision

Highest mean-score model becomes primary brainstorming model in
`core/llm/router.py`. If the gap is < 0.1 between models, prefer the
faster one (latency matters for the conversational loop).

If no model reaches mean ≥ 0.7, the system prompt is the bottleneck —
revise it before re-running.
