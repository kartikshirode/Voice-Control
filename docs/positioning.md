# Positioning

## Tagline (working)

> The AI that thinks with you, out loud.

Alternates that tested similarly in the research:

- "A rubber duck that asks better questions than you do."
- "Stop typing about your code. Talk about it. It will remember."

## Anchor persona

The senior IC who paces while thinking. Already pays $200/mo for Cursor
Ultra and $15/mo for Wispr — willingness to pay for thinking-tools is
established. Brainstorming happens out loud, often away from the keyboard,
and the artifact (the decision, the open question, the next step) needs to
end up somewhere durable.

## What we are not

- **Not a dictation tool.** Wispr Flow, SuperWhisper, Aqua, Willow,
  MacWhisper, Voicy already own that lane. STT quality is not our wedge.
- **Not a code generator.** Claude Code, Cursor, Codex, Aider, Open
  Interpreter cover that. We're upstream of code generation: we help you
  decide what to build before you ask one of them to build it.
- **Not a voice companion.** Pi raised $1.5B and still couldn't make it
  work. Friend.com sold ~3,000 pendants. A polished voice companion
  without a workflow wedge is not a business.

## Anti-positioning (sharper than the pitch itself)

- **vs. Wispr Flow**: "Wispr makes you type 4× faster. We help you
  *think* better."
- **vs. Claude Code `/voice`**: "Claude Code's voice helps you give it
  instructions. Ours helps you figure out what the instructions should
  be."
- **vs. ChatGPT Voice**: "ChatGPT Voice runs an older model that
  forgets your project at the end of the call. We don't."
- **vs. Mem.ai's 'AI Thought Partner'**: "Theirs is text. Ours
  is voice. Code-aware. With modes."

## The four pillars (in priority order)

1. **Socratic posture** — the agent asks more than it answers. Three named
   modes (Rubber Duck / Devil's Advocate / Architect) make this tangible.
2. **Cross-session project memory** — backed by mem0 OSS for semantic
   recall, plus a hand-editable central profile (cloud-safe + local-only
   split). The agent that doesn't remember is just another chatbot.
3. **Workflow wedge** — every brainstorm produces a Granola-style markdown
   note (decisions, open questions, next actions). The brainstorm becomes
   a deliverable.
4. **Privacy as a switchable mode** — for proprietary code. Cloud-fast
   by default; local-private when it matters. Demoted from headline
   because Wispr's $700M valuation came from cloud-first to 270 F500s
   — privacy is a *segment*, not a *category*.

## Distribution

**MCP-first.** Ship as an MCP server installable in Claude Code, Cursor,
Codex. Distribution to ~5M existing users without building reach from
zero. Gradio is the demo surface for the full voice loop that MCP can't
carry end-to-end.

Tauri standalone is killed. It re-enters the conversation only if MCP
distribution fails AND there is evidence of standalone demand.

## Tone & voice (for replies)

- Peer, not assistant. Senior engineer talking to a senior engineer.
- Direct. Confident. Disagrees when it disagrees.
- No sycophancy. No "great question." No closing summaries unless asked.
- No filler. No safety-theater hedging on technical topics.

These tone rules are baked into every mode's system prompt and tested.

## Risks we are watching

- **Anthropic ships full two-way voice + project memory in Claude Code
  natively** (~6–12 month window per the research). Monitor monthly. If it
  ships, our wedge narrows to *better Socratic prompting + better memory
  than theirs.*
- **Mem0's LongMemEval ceiling (49%)** caps recall quality regardless of
  layering. The golden recall test is the early-warning.
- **Local TTS quality below ElevenLabs.** Phase 0.4 quantifies. If Kokoro
  doesn't make the bar in cloud mode, it remains the privacy-mode TTS
  only and cloud mode uses cloud TTS.
- **PTT onboarding friction.** Wispr's user-research insight: many users
  drop off because they don't realize how PTT works across apps.
  First-run flow needs explicit "press Right-Ctrl now" prompting.
