# Phase 0.4 — TTS quality test

**Status:** not yet run.

## Goal

Confirm Kokoro-82M is good enough for the conversational loop. Quantify
the gap to better TTS so we know what we're trading off when running
locally.

## Configuration

- **Hardware:** RTX 4060 8 GB, Windows 11.
- **Constraint:** must run alongside faster-whisper (small.en) + sentence-
  transformers + Qwen 3 4B (when local fallback active).

## Test set

A code-review excerpt of ~150 words covering:

- A short prose paragraph (typical brainstorming reply).
- A pair of inline `code references` (single backticks, common in dev chat).
- A short bullet list of 2–3 items (test that the reader handles
  list-marker pronunciation gracefully).
- One acronym (e.g. "API", "TCP") to test pronunciation.
- One technical term that's commonly mispronounced ("pgvector",
  "Postgres", "Redis", "Kubernetes").

Source the excerpt from a real PR comment — synthetic scripts read
unnaturally well and bias the comparison.

Save the script to `evals/tts_quality/script.txt` (one paragraph, plain
text, no markdown).

## Procedure

1. Generate three audio files for the same script:
   - `samples/piper.wav` — Piper, en_US-lessac-medium voice.
   - `samples/kokoro.wav` — Kokoro-82M, default voice.
   - `samples/elevenlabs.wav` — only if ELEVENLABS_API_KEY is set; skip
     otherwise.
2. Listen to each three times. Take notes in the table below.
3. Time the latency to first audio chunk for each (proxy for "how
   conversational does it feel"). For Piper / Kokoro this is the
   important number; ElevenLabs cloud latency varies by region.

## Rubric (per voice)

For each, rate 1–5 on:

- **Naturalness** — does it sound like a person, or a robot?
- **Pacing** — would a listener follow it without rewinding?
- **Pronunciation of code/acronyms** — does it stumble on `pgvector`?
- **First-byte latency** — how long from request to first audio chunk?

## Results

| Voice | Naturalness | Pacing | Pronunciation | First-byte (ms) | Notes |
|-------|--------------|--------|----------------|------------------|-------|
| Piper (lessac-medium) | — | — | — | — | — |
| Kokoro-82M | — | — | — | — | — |
| ElevenLabs (optional) | — | — | — | — | — |

## Decision

| Outcome | Action |
|---------|--------|
| Kokoro ≥ 4 on naturalness AND first-byte < 500ms | Adopt as primary TTS. |
| Kokoro 3–4 on naturalness | Adopt for v0; revisit in Phase 4 polish. |
| Kokoro < 3 on naturalness | Cloud TTS as primary in non-privacy mode; Kokoro becomes the privacy-mode-only TTS. |
| Piper beats Kokoro on the rubric | Keep Piper. (Unlikely per the research; document if so.) |
