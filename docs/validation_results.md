# Phase 0 — validation results

This file aggregates the outputs of the four Phase 0 evaluations. It is the
single document that decides whether Phase 1 starts.

**Status:** Phase 0 in progress.

## 0.1 — mem0 OSS evaluation

See `evals/mem0_eval/results.md`.

**Decision:** _pending_

## 0.2 — clarifying-question eval (50-prompt)

See `evals/clarifying_questions/results.md`.

**Primary model decision:** _pending_

## 0.3 — Wizard-of-Oz user tests

See `evals/woz_protocol.md` for the script.

**Posture validated?** _pending_

### Per-participant notes

| # | Date | Background | Posture-felt | Wished-it-answered | Pay $15/mo | Quote |
|---|------|------------|---------------|--------------------|------------|-------|
| 1 | — | — | — | — | — | — |
| 2 | — | — | — | — | — | — |
| 3 | — | — | — | — | — | — |
| 4 | — | — | — | — | — | — |
| 5 | — | — | — | — | — | — |

### Aggregate

- Posture-felt = yes: __ / 5
- Wished-it-answered = no: __ / 5
- Pay = yes-or-probably: __ / 5

### Decision

(per the protocol's decision-criteria table)

## 0.4 — TTS quality test

See `evals/tts_quality/notes.md`.

**Primary TTS decision:** _pending_

## Phase 1 gate

Phase 1 implementation begins only when:

- [ ] 0.1 has a decision recorded (mem0 adopted or rejected with reasoning)
- [ ] 0.2 has a primary model picked
- [ ] 0.4 has a primary TTS picked
- [ ] 0.3 either green-lit the posture OR the protocol script was revised
  and a second 5-person round was run
