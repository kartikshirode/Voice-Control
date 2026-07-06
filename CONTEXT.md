# Voice-Controlled Local AI Agent — Project Context

> Hand this file to a new chat to continue the design conversation without re-explaining everything.

---

## What this project is

A voice-first AI **brainstorming partner** for developers — pitched as "Jarvis for developers" but better described as **"the AI that thinks with you, out loud."** Originally a Mem0 internship assignment (local voice agent: transcribe → classify intent → execute tools), reframed as a real product.

**Key differentiators (the wedge):**
- Voice-first conversational loop (push-to-talk + TTS reply) for thinking out loud
- Persistent cross-session memory: split central profile + per-project semantic memory
- Socratic posture — pushes back, asks "why," proposes alternatives, doesn't just execute
- Privacy as a contract — explicit local-only mode for proprietary work
- Frontier-quality reasoning via Gemini, with graceful local fallback

The PDF's required intents (create file, write code, summarize, general chat) are preserved as **support tools the brainstorming agent uses**, not the primary surface.

## Hardware target

- RTX 4060 laptop, **8 GB VRAM**
- Windows 11
- CUDA-only execution

## Locked model stack

| Layer | Model | VRAM | Notes |
|---|---|---|---|
| STT | `faster-whisper` `small.en` | ~1.0 GB | Escalate to `medium` if WER bad |
| LLM primary | Gemini 2.5 Flash (API, free tier) | 0 (cloud) | Function calling, ~1M context, 500 RPD free |
| LLM fallback | Qwen 2.5 7B Instruct (Ollama Q4_K_M) | ~5.0 GB | Loaded on demand; preloaded on privacy toggle |
| TTS | Piper (medium voice) | ~0.1 GB | **⚠️ Research recommends switching to Kokoro-82M (MIT, 36× real-time, near-ElevenLabs quality)** |
| Embeddings | `bge-small-en-v1.5` | ~0.2 GB | Always loaded |
| Vector DB | ChromaDB (embedded) | 0 | Disk-backed |

LLM router fallback chain: Gemini Flash → Groq Llama 70B (speed) → NVIDIA NIM (frontier experiments) → local Qwen (offline / privacy / API failure / budget exhaustion).

## Architectural commitments (locked)

1. **Python core is a library, not a Gradio app.** UI handlers are 3-line wrappers. CI-enforced via AST check on `ui/gradio_app.py` — only allowed imports: `gradio`, `httpx`, `pydantic`, `json`, `base64`, `asyncio`, `websockets`, `core.types`. Any other `core.*` import fails CI.
2. **Transport: WebSocket** at `/ws/turn`, not request/response. Generators don't survive HTTP boundaries.
3. **Frontend phasing:** Gradio v0 (validate the loop) → Tauri v1 (real desktop shell with global hotkey, system tray). **Research recommends pivoting:** ship as CLI + MCP server first to ride Claude-Code/Cursor distribution, defer Tauri until 100 users.
4. **Sandbox:** all file writes restricted to `output/` via `SafePath`.
5. **Tauri packaging plan:** spawns Python server as supervised child process, uses `python-build-standalone`, `uv sync` at first launch.

## Privacy & memory contract (the most important design)

**Two-file central profile (provenance-safe):**
- `memory/MEMORY.md` — cloud-safe, hard cap 4 KB, loaded into every Gemini call
- `memory/MEMORY_PRIVATE.md` — local-only, hard cap 4 KB, loaded ONLY when active backend is Qwen

**`remember_fact(fact, scope)` rules:**
- `scope=central` → MEMORY.md, **forbidden in privacy mode**
- `scope=central_private` → MEMORY_PRIVATE.md, allowed in any mode (with voice confirm in privacy)
- `scope=project` → current project's Chroma collection

**PrivacyGate:** embedding-based zero-shot match (NOT regex) on transcription's first sentence vs. canonical privacy phrases ("go private," "stay local," "this is sensitive," etc.). Threshold 0.7, calibrated against held-out set. Toggles privacy BEFORE any API call.

**Privacy mode ON:**
- All LLM traffic to Qwen (no exception, including consolidation)
- Consolidation disabled
- No WAL written; session is in-memory only (crash = total loss, by design)
- UI shows non-dismissable "🔒 Private session" banner
- ON→OFF requires voice confirmation (the confirmation utterance itself rides through Qwen)

## Session lifecycle

- **Start:** app launch (resume prompt if <60 min old session), voice "new session," project switch
- **End:** explicit ("save and exit"), 60-min inactivity, project switch, app close
- **On end (privacy OFF):** consolidation via Gemini Flash → write to project's Chroma collection. If offline, queue WAL to `memory/pending_consolidation/` for later flush by serial background worker.
- **On end (privacy ON):** discard everything. No consolidation. No WAL.

## Memory architecture

- **Tier 1:** Central profile (split as above), 4 KB cap each, LLM-driven compaction to ≤2 KB when exceeded. Cloud file uses Gemini for compaction; private file uses Qwen.
- **Tier 2:** Per-project Chroma collection at `memory/projects/<slug>/chroma/`. Records are **consolidated memories** (decision, open_question, attempt, context, fact), not raw turns. Top-K=5 cosine retrieval, scoped to current project. Cross-project widening is **opt-in only**.
- **Embedding cache:** LRU(100) keyed on normalized query string.
- **Consolidation:** always uses Gemini Flash (memory quality determines future brainstorming quality).

## Voice & UX spec

**System prompt** (`core/prompts/system.txt`, versioned with change log) defines the persona: peer not assistant, push back on weak ideas, propose alternatives, no sycophancy, no closing summaries, no filler. Uses `<voice>...</voice>` and `<display>...</display>` tags so TTS gets prose and UI gets full markdown.

**Streaming TTS:**
- Sentence-level chunking (`. ! ?` + whitespace, or `</voice>` close tag, or 2 newlines)
- Tag-aware streaming state machine (handles tags split across token boundaries)
- Tool-call turns DON'T stream to TTS during agent loop (only stream on terminal text response)
- Fallbacks: missing `<voice>` = treat all as voice; unclosed = auto-close at end; malformed = warn + treat as voice

**Audio preprocessing (pre-STT):** decode 16 kHz mono → webrtcvad silence trim (mode 2, 30ms frames) → reject if <200ms remaining → faster-whisper.

## Robustness layer

- **CircuitBreaker** per backend: closed → open (3 failures in 60s OR single AuthError) → half-open (after 30s, single 1-token probe) → closed/reopen
- **HealthChecker:** Gemini-specific 1-token probe, cached 30s. NOT generic internet ping.
- **BudgetTracker:** `memory/budget.json`, atomic writes, UTC midnight reset. Toast at 80% RPD, auto-fallback to Qwen at 95%.
- **ContextBudget:** recursive chunked summarization for mid-session backend switches (200K Gemini context → 32K Qwen window without exploding).
- **Routing precedence:** `privacy_mode → qwen` > `offline → qwen` > `circuit_open → qwen` > `budget_exceeded → qwen` > else `gemini`.

## HITL confirmation contract

- Server emits `confirmation_required` with `expires_at` (now + 60s)
- 60s timeout → reject, agent loop continues
- WS disconnect mid-confirmation → cancel pending tool calls, roll back agent loop, send `turn_end{status: interrupted}`
- New `turn_start` while pending → reject with `error{code: pending_confirmation}`

## WebSocket protocol

**Client → Server:** `turn_start`, `confirmation_response`, `set_privacy_mode`, `set_project`, `session_end`

**Server → Client:** `transcription`, `intent`, `llm_token`, `tts_chunk`, `tool_call`, `tool_result`, `confirmation_required`, `model_state` (`gemini | qwen-offline | qwen-privacy | qwen-fallback | qwen-budget`), `consolidation_status`, `turn_end`, `error`

## Tools registry

| Tool | Description | Safety |
|---|---|---|
| `create_file(path, content)` | Create new file | SafePath + HITL |
| `write_code(path, language, content)` | Write generated code | SafePath + HITL; refuses overwrite without `force` |
| `summarize(text)` | Summarize text | Pure compute |
| `remember_fact(fact, scope)` | Update memory | scope ∈ {central, central_private, project}; central forbidden in privacy |
| `set_project(name)` | Switch project | Creates if new |
| `set_privacy_mode(on)` | Toggle privacy | OFF requires voice confirmation |
| `delete_project(name)` | Delete project | UI button only, NOT voice-confirmable |
| `list_recent_actions(n)` | Last N tool calls | Read from session log |

Compound commands ride function calling natively (Gemini and Qwen both support multi-tool turns).

## Test plan (what's specced)

- `test_safe_path.py`, `test_circuit_breaker.py`, `test_budget.py`, `test_context_budget.py` (recursive summarization), `test_health_check.py`, `test_privacy_gate.py` (calibrated set), `test_memory_compaction.py`, `test_consolidation_json.py` + `test_consolidation_quality.py` (real transcript recall), `test_session_lifecycle.py`, `test_hitl_confirm.py`, `test_voice_tag_parser.py`, `test_pending_queue.py`
- Integration: `test_recall_quality.py` (golden retrieval, 30 memories × 10 queries, threshold ≥8/10), `test_agent_e2e.py` (mocked LLM, full turn per intent)
- CI: `tests/ci/test_handler_imports.py` (AST enforces thin-handler rule)
- Pre-commit: ruff + mypy

## Article thesis (pinned)

**"Function calling subsumes intent classification, and privacy is a first-class contract in voice agents."**

Three demonstrations with measurements:
1. Function calling > intent classification (latency, accuracy on held-out, compound commands)
2. Privacy as a contract (PrivacyGate TPR/FNR, assertion that MEMORY_PRIVATE.md never appears in Gemini calls)
3. Memory makes a difference (recall@K, qualitative with/without memory comparison)

Required measurements (→ `docs/benchmark.md`): per-turn latency breakdown (STT, recall, LLM-first-token, complete, tool-exec, TTS-first-chunk), fallback frequency, token cost p50/p95, recall@K, PrivacyGate confusion matrix.

---

## Decisions made along the way

- **API vs local LLM:** hybrid with router, NOT pure local. Reasoning: brainstorming partner is defined by reasoning quality; 7B models feel weak at exactly the moments the product should shine.
- **Free APIs chosen:** Gemini 2.5 Flash (primary, 500 RPD free, 1M context), Groq Llama 70B (speed), NVIDIA NIM (1k credits, frontier experiments), Qwen local (offline/privacy/fallback).
- **UI framework:** Gradio v0 → Tauri v1, NOT Electron, NOT pure web. Push-to-talk requires global hotkey → desktop app. Gradio for v0 because it gets to working voice loop in an afternoon; Python core stays as a library so v0→v1 is a frontend swap.
- **TTS chunking:** sentence-level (closed open item).
- **Qwen warm/cold:** load on demand; preload on privacy-mode toggle (we know it's about to be needed).
- **Whisper size:** start `small.en`, escalate to `medium` only if WER bad in real demo audio.
- **Compaction similarity threshold (0.7):** smoke threshold, calibrated against held-out set during implementation, NOT a guarantee.
- **Privacy gate:** embedding-based zero-shot match, NOT regex (regex rejected as too brittle for a security boundary).

## Critical files to create (priority order)

1. `core/tools/safe_path.py` — safety boundary; tests first
2. `core/types.py` — Pydantic WS-protocol models (the legitimate shared-types boundary)
3. `core/llm/base.py` + error classes (`RateLimitError`, `AuthError`, `NetworkError`, `ServerError`)
4. `core/llm/circuit_breaker.py` + tests
5. `core/llm/budget.py` + `core/llm/context_budget.py` (recursive summarization) + tests
6. `core/llm/health_check.py`, `core/llm/gemini.py`, `core/llm/ollama.py`
7. `core/llm/router.py`
8. `core/privacy.py` (embedding-based PrivacyGate) + tests + calibration set
9. `core/stt.py` (preprocessing + faster-whisper)
10. `core/tts.py` (tag state machine + sentence streaming)
11. `core/memory/{central, project, consolidate, pending_queue, projects}.py` + tests
12. `core/session.py` (lifecycle + WAL + offline-aware resume)
13. `core/tools/registry.py` + tool modules (with HITL contract)
14. `core/prompts/system.txt`, `core/prompts/consolidation.txt`
15. `core/warmup.py`
16. `core/agent.py` — orchestration
17. `server/main.py` — FastAPI + WebSocket + warmup hook + HITL state
18. `ui/gradio_app.py` — thin handlers + WS client
19. `tests/ci/test_handler_imports.py`
20. `docs/intents_matrix.md`, `docs/system_prompt.md`, `docs/privacy_calibration.md`, `README.md`

---

## Market research findings (research run May 2026)

### Direct competitors at the user's slot
**Nobody occupies the exact intersection** of "voice in + voice out + persistent project memory + Socratic posture + local fallback + targeted at devs." But the adjacent cells are saturated:

- **Wispr Flow** — $81M raised, ~$700M valuation, 100k+ DAU, dictation-only (no reply, no memory)
- **SuperWhisper** — $84.99/yr or $249.99 lifetime, on-device, dictation-only
- **Claude Code `/voice`** — shipped March 3, 2026, push-to-talk via spacebar, **input-only** (text reply, no TTS, no cross-session memory). Anthropic likely ships full two-way voice in 6-12 months.
- **Cursor 2.0 voice** (Oct 2025), **Codex CLI voice** (~Feb 2026) — input-only
- **ChatGPT Advanced Voice** — talks back, has coarse memory, but runs older/weaker model (Willison: still reports April 2024 cutoff as of April 2026), not project-segregated
- **Sam (iamsam.ai)** — voice-first thinking partner, "when your mind is loud" — **the closest positioning analog**, but consumer wellness not dev-targeted
- **Pi (Inflection)** — cautionary tale: 1M DAU, $1.525B raised, team absorbed by Microsoft March 2024, product wound down
- **GitHub OSS jarvis/voice-agent repos** — dozens exist (open-jarvis, isair/jarvis, ollama-voice, local-voice-ai, etc.); high builder interest, low productized presence

### Adjacent products informing the plan
- **Mem0** — $24M raised Oct 2025, 41k stars, 5× quarterly API growth, but mediocre LongMemEval (49.0%). **Recommendation: evaluate as memory layer above ChromaDB before rolling custom logic.**
- **Letta** (formerly MemGPT) — $10M seed, "agent edits its own memory" pattern worth borrowing
- **Granola** — $125M Series C at $1.5B, "no bot, capture system audio" UX; killer feature is **shareable structured note artifact**
- **AudioPen** — proves voice-to-rewritten-text demand exists; "rewrite styles" pattern → "modes"
- **SuperWhisper** has "Super Mode" (screen context awareness) — pattern worth stealing

### Demand signals
- **Bullish:** Wispr's funding/growth trajectory, Mem0's API growth, Granola's $1.5B, Karpathy coining "vibe coding" with SuperWhisper as his tool, Deepgram explicitly identifying the "true pair-programming partner / sublime rubber duck" gap
- **Bearish:** Pi shutdown, Friend.com pendant ($400k revenue total, "wearable that bullies you" reviews), Limitless EU shutdown
- **Verdict:** demand is real but fragmented across saturated adjacent categories. The bundle hypothesis (voice + memory + Socratic + local) is unproven and must be earned through sharp positioning + workflow wedge.

### Concrete plan changes recommended by research

**ADD:**
1. MCP server distribution path (ride Claude Code / Cursor / Codex base)
2. Screen/IDE context capture (active window + clipboard hook)
3. Named "modes" framework: Rubber Duck, Devil's Advocate, Architect, Standup Coach (each = system prompt)
4. Session-end shareable brainstorm note artifact (Granola pattern)
5. Memory inspector UI (Letta lesson — users trust visible memory)
6. Mobile capture path (Phase 2 PWA)
7. Mem0 OSS evaluation as memory layer above ChromaDB

**REMOVE / DE-PRIORITIZE:**
1. **"Jarvis for developers" name** — culturally crowded, trademark-shaky, dozens of GitHub collisions. Pick something tied to Socratic positioning.
2. Tauri v1 milestone — replace with CLI + MCP server first
3. Privacy mode as headline — demote to toggle (Wispr/Granola valuations prove cloud is acceptable for most)
4. Full intent-execution suite at v1 — overlaps with Claude Code / Cursor / Open Interpreter; keep one execution primitive
5. **Piper TTS** — below 2025-2026 quality bar; **switch to Kokoro-82M** (MIT, 82M params, 36× real-time, near-ElevenLabs in blind tests, fits 4060)

**RETHINK:**
1. Primary model — try Claude Haiku 4.5 or Gemini 2.5 Flash Thinking for Socratic question generation (asking, not answering)
2. Local fallback — consider Qwen 3 4B (Apr 2025) for headroom
3. Add **temporal awareness** to memory (Zep lesson: facts have validity windows)
4. PTT hotkey — must NOT collide with Claude Code spacebar, Wispr Fn, SuperWhisper ⌥+Space; pick Right-Ctrl or similar
5. Skip Gradio entirely once CLI/MCP exists; signals "internship project"

**VALIDATE BEFORE BUILDING (5 users each, week 1):**
1. The bundle hypothesis (would they pay $15/mo given Claude Code/ChatGPT exist?)
2. The Socratic posture (Wizard-of-Oz: human-as-AI in chat for 10 min)
3. Privacy mode demand (have you avoided ChatGPT/Cursor for confidential code?)
4. TTS quality tolerance (Piper vs Kokoro vs ElevenLabs blind)
5. Walking-and-thinking use case (concrete frequency in last 2 weeks)

### Positioning recommendations
- **Don't say "Jarvis for developers."** Lead with the verb "think," not the noun "voice."
- Suggested taglines: *"The AI that thinks with you, out loud,"* *"A rubber duck that asks better questions than you do,"* *"Stop typing about your code. Talk about it. It will remember."*
- Position vs Wispr: "Wispr makes you type 4× faster. We make you think better."
- Position vs Claude Code voice: "Claude Code's voice helps you give it instructions. Ours helps you figure out what the instructions should be."
- Position vs ChatGPT Voice: "ChatGPT Voice runs a weaker model that forgets your project at the end of the call."

### Risks
- **Anthropic ships two-way voice + memory in Claude Code in 6-12 months** → 3-month defensive window
- Pi precedent — free voice companion is not a business
- Memory benchmarks weaker than marketing suggests (Mem0 49% LongMemEval)
- Local TTS quality below user expectations even with Kokoro

### Open questions research couldn't resolve
1. Voice-curious dev → paying user conversion rate (Wispr doesn't disclose)
2. Share of ChatGPT Voice usage that's actually coding rubber-ducking
3. Whether Claude Code `/voice` extends to two-way audio
4. Real-time TTS latency on 4060 with concurrent Whisper + Qwen
5. Whether developers will pay for "memory" as a feature (no clean precedent)
6. Whether "Socratic" posture survives at scale
7. Whether enterprise privacy buyers accept single-developer product

---

## Improvements that were put on hold (NOT applied yet)

These were flagged in review but the user chose not to apply them:

1. `MEMORY_PRIVATE.md` loads on any Qwen call (not just `qwen-privacy`) — internally consistent but document explicitly
2. WebSocket reconnect / state recovery handshake (`reconnect: {session_id, last_event_seq}` → replay or `turn_end{status: interrupted}`)
3. `core.telemetry` module to actually capture the per-turn timing records the article needs
4. Backup before MEMORY.md compaction (`.bak` files, last 3)
5. `list_projects` tool
6. Pre-canned messages for security-critical acks (privacy on/off, file delete) — don't depend on LLM
7. `consolidation_status` event emission rules (who emits when)
8. AST check that `core/types.py` only contains Pydantic models + literal type aliases
9. `docs/threat_model.md` — privacy contract is "doesn't touch cloud," not "encrypted at rest"
10. Adding explicit `intent_label(turn)` step to make tool-calls-as-intent legible to assignment evaluator

---

## How to continue this conversation

The plan is in shipping shape from a software engineering standpoint. The market research surfaced a separate, larger question: **should the plan be rewritten around the research findings before implementation starts?**

Three reasonable next moves:

1. **Build the plan as-is** (it's specced, the assignment is satisfied) and treat the research as v2 input
2. **Rewrite the plan around the research** — rename, reposition, switch Piper→Kokoro, add MCP server path, add modes framework, add shareable brainstorm note, defer Tauri, demote privacy from headline
3. **Run the 5-user validation tests first** before doing either — answer "do devs want this bundle?" before more code

The user's call. The new chat should ask which path before continuing.
