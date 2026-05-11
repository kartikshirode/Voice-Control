"""Phase 0.2 — clarifying-question eval runner.

Runs each prompt in `prompts.jsonl` through one or more candidate models and
writes responses to `runs/<model>-<timestamp>.jsonl` for human rating.

Rubric (applied by hand to each response):
    1   = clean clarifying question, no answer attempt, no sycophancy
    0.5 = mixed (some probing, some answering)
    0   = answers, summarizes, or sycophants ("great question, ...")

Usage:
    python evals/clarifying_questions/runner.py --models gemini-flash gemini-flash-thinking
    python evals/clarifying_questions/runner.py --models gemini-flash --delay-seconds 8

Requires GEMINI_API_KEY in the environment.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

EVAL_DIR = Path(__file__).parent
PROMPTS_PATH = EVAL_DIR / "prompts.jsonl"
RUNS_DIR = EVAL_DIR / "runs"

# The system prompt under test. This is the core wedge — if the model can't
# follow this, the posture is bottlenecked by model capability, not by
# product design.
SYSTEM_PROMPT = """You are a Socratic brainstorming partner for a developer.

You ask clarifying questions. You do not answer the developer's question.
You do not propose solutions. You probe.

REQUIRED:
- Reply with exactly ONE clarifying question.
- The question targets the unstated assumption, the missing constraint, or
  the unmeasured fact behind the developer's request.

FORBIDDEN:
- Do not answer.
- Do not propose a solution.
- Do not summarize.
- Do not say "great question" or any sycophantic opener.
- Do not hedge ("it depends...", "well, generally...").
- Do not list multiple questions.

Output format: just the question, one sentence."""

MODEL_MAP = {
    "gemini-flash": "gemini-2.5-flash",
    "gemini-flash-thinking": "gemini-2.5-flash-thinking-exp",
}


class BlockingProviderError(RuntimeError):
    """Provider error that makes the rest of the eval run unusable."""


def load_prompts() -> list[dict]:
    with PROMPTS_PATH.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def is_blocking_provider_error(exc: Exception) -> bool:
    message = str(exc)
    return (
        "quota_limit_value: 0" in message
        or ("quota_limit_value" in message and 'value: "0"' in message)
        or "API key not valid" in message
        or "PERMISSION_DENIED" in message
        or "SERVICE_DISABLED" in message
    )


def run_model(model_name: str, prompts: list[dict], delay_seconds: float) -> list[dict]:
    api_model = MODEL_MAP[model_name]
    model = genai.GenerativeModel(api_model, system_instruction=SYSTEM_PROMPT)
    results = []
    for p in prompts:
        try:
            t0 = time.monotonic()
            resp = model.generate_content(p["prompt"])
            latency_ms = int((time.monotonic() - t0) * 1000)
            text = resp.text.strip() if resp.text else ""
        except Exception as e:  # noqa: BLE001 — we want every prompt logged
            if is_blocking_provider_error(e):
                raise BlockingProviderError(
                    f"{model_name} cannot run with the current provider setup: "
                    f"{type(e).__name__}: {e}"
                ) from e
            text = f"[ERROR] {type(e).__name__}: {e}"
            latency_ms = -1
        results.append(
            {
                "prompt_id": p["id"],
                "category": p["category"],
                "prompt": p["prompt"],
                "ideal_axis": p["ideal_question_axis"],
                "model": model_name,
                "response": text,
                "latency_ms": latency_ms,
                "score": None,  # filled in by hand-rating pass
                "notes": "",
            }
        )
        print(f"  [{model_name}] {p['id']}: {text[:80]}...")
        if delay_seconds > 0 and p != prompts[-1]:
            time.sleep(delay_seconds)
    return results


def write_run(model_name: str, results: list[dict]) -> Path:
    RUNS_DIR.mkdir(exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    out_path = RUNS_DIR / f"{model_name}-{timestamp}.jsonl"
    with out_path.open("w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    return out_path


def main() -> None:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit("GEMINI_API_KEY is not set. Copy .env.example to .env and fill it in.")
    genai.configure(api_key=api_key)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--models",
        nargs="+",
        default=["gemini-flash", "gemini-flash-thinking"],
        choices=list(MODEL_MAP.keys()),
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=4.0,
        help="Delay between prompts for free-tier/API quota friendliness.",
    )
    args = parser.parse_args()

    prompts = load_prompts()
    print(f"Loaded {len(prompts)} prompts.")

    for model in args.models:
        print(f"\n=== Running {model} ===")
        try:
            results = run_model(model, prompts, delay_seconds=args.delay_seconds)
        except BlockingProviderError as e:
            print(f"[BLOCKED] {e}")
            print("Fix the provider quota/API key issue, then rerun this eval.")
            continue
        if not any(r["latency_ms"] >= 0 for r in results):
            print("No successful responses; skipping run file.")
            continue
        out = write_run(model, results)
        print(f"Wrote {len(results)} responses to {out}")
        print("Next: open the .jsonl, fill in `score` (1 / 0.5 / 0) for each row,")
        print("      then summarize in evals/clarifying_questions/results.md.")


if __name__ == "__main__":
    main()
