# Phase 0.1 — mem0 OSS evaluation

**Status:** not yet run.

## Goal

Decide whether mem0 OSS is the memory layer for this product, or whether to
roll our own consolidation/scoring on top of ChromaDB behind a `MemoryStore`
interface.

## Why this question is open

The research called out mem0's strong VC traction (5× quarterly API call
growth, AWS exclusive memory provider) but flagged the LongMemEval ceiling
of 49% (arXiv 2603.04814) — significantly below dedicated systems like
OMEGA (95.4%) and Mastra (94.87%). VC marketing ≠ technical proof. We
back-test against our own data, not their benchmark.

## Procedure

1. Install mem0 (`pip install mem0ai`) and a baseline ChromaDB-only setup.
2. **Synthetic test data** (since we don't have real brainstorm transcripts
   yet): generate 30 hand-curated memories across 3 fictional projects using
   a Gemini Flash call with the consolidation prompt template. Save to
   `evals/mem0_eval/data/synthetic_memories.jsonl`.
3. **Hand-curated query set:** 10 queries per project (30 total) where the
   ideal top-K result is known. Save to
   `evals/mem0_eval/data/queries.jsonl`.
4. Insert all 30 memories into mem0 (one config) and into a baseline Chroma
   collection (other config). Use the same embedding model
   (`bge-small-en-v1.5`) for both.
5. Run all 30 queries against each. Record top-5 returned IDs.
6. Score: count queries where the expected ID is in the top-K returned.

## Decision criteria

| Outcome | Action |
|---------|--------|
| mem0 recall@5 ≥ baseline AND mem0 saves ≥ 1 week of work (consolidation, conflict, decay handled) | Adopt mem0 as default `MemoryStore`. |
| mem0 recall@5 < baseline by ≥ 10pp | Reject mem0. Roll own behind `MemoryStore` interface. |
| Recall comparable, mem0 setup cost > 1 week | Roll own; reconsider mem0 in Phase 2 if maintenance burden grows. |

In every outcome, the `MemoryStore` interface is the same. The decision is
which implementation lives behind it.

## Results

(to be filled after running)

| Config | Recall@5 (% queries with expected ID in top-5) | Median query latency | Setup time (clock hours) |
|--------|-----------------------------------------------|----------------------|--------------------------|
| baseline (Chroma + bge-small) | — | — | — |
| mem0 (defaults, Chroma backend) | — | — | — |

## Notes during evaluation

(open notes during the half-day)

## Decision

(filled in after running)
