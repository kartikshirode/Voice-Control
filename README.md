# Voice-First Developer Brainstorming Partner

> **The AI that thinks with you, out loud.**

A voice-driven Socratic brainstorming partner for developers. Not autocomplete, not chat — a thinking partner that pushes back on weak ideas, remembers your projects across sessions, and runs locally when proprietary work demands it.

**Status:** Pre-implementation. Phase 0 (validation) in progress. See [docs/positioning.md](docs/positioning.md) and the [plan](.) for context.

---

## What this is, in five lines

Unlike Wispr Flow (4× faster typing) or Claude Code `/voice` (input-only), this agent **talks back**, **remembers your projects across sessions**, ships **three named brainstorming postures** (Rubber Duck, Devil's Advocate, Architect), and runs **locally with a Privacy Mode** for proprietary code. Distributed primarily as an **MCP server** for Claude Code / Cursor / Codex — not as another standalone app.

## Why this exists (and why now)

Voice input was commoditized in late 2025 / early 2026 — Wispr Flow at ~$700M valuation, Cursor 2.0 voice (Oct 2025), Claude Code `/voice` (Mar 2026), Codex CLI voice (~Feb 2026). STT is no longer a product.

The defensible cell that's still empty: **voice output + cross-session project memory + Socratic posture + targeted at developers + with a privacy fallback for proprietary code**. No product currently lives there. Window before Anthropic ships full two-way voice + project memory natively in Claude Code: 6–12 months.

## How it differs

- **vs. Wispr Flow**: "Wispr makes you type 4× faster. We help you _think_ better."
- **vs. Claude Code `/voice`**: "Claude Code's voice helps you give it instructions. Ours helps you figure out what the instructions should be."
- **vs. ChatGPT Voice**: "ChatGPT Voice runs an older model that forgets your project at the end of the call."

## Architecture (one paragraph)

The Python core (`core/`) holds all logic: STT (faster-whisper), LLM router (Gemini primary, Qwen 3 4B local fallback, with circuit breaker / budget tracking / context-window-aware switching), TTS (Kokoro-82M), memory (mem0 OSS for per-project semantic memory + a hand-editable central profile split into cloud-safe `MEMORY.md` and local-only `MEMORY_PRIVATE.md`), three brainstorming modes, session-end Granola-style note generation, and a privacy gate that intercepts sensitive utterances before any API call.

Two clients consume the core: an **MCP server** (`mcp_server/`) — the canonical distribution surface, exposing `brainstorm_turn`, `recall_project_memory`, `start/end_brainstorm_session`, `set_mode`, etc. to Claude Code / Cursor / Codex hosts — and a **Gradio demo client** (`ui/`) for the full voice-in / voice-out experience that MCP can't carry end-to-end.

Full plan: see the design doc.

## Status / phases

- [ ] **Phase 0 — Validation** (in progress)
  - [ ] 0.1 mem0 OSS evaluation
  - [ ] 0.2 50-prompt clarifying-question eval (Gemini 2.5 Flash vs Flash Thinking)
  - [ ] 0.3 5-user Wizard-of-Oz on Rubber Duck mode
  - [ ] 0.4 TTS quality test (Piper vs Kokoro-82M)
- [ ] Phase 1 — MCP server v0
- [ ] Phase 2 — Gradio demo client v0
- [ ] Phase 3 — Mobile capture (gated on Phase 0.3 signal)
- [ ] Phase 4 — Distribution & polish

## Setup (placeholder — see Phase 1)

```bash
# Once Phase 0 is green:
uv sync
cp .env.example .env  # fill in GEMINI_API_KEY
ollama pull qwen3:4b
```

## License

TBD.
