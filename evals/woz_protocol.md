# Phase 0.3 — Wizard-of-Oz protocol

## Goal

Validate the **Socratic posture hypothesis** before writing more code.

The hypothesis: developers, given a thinking partner that asks more than it
answers, will report feeling "thought with" — and a meaningful fraction
will say they would pay for it. If the posture itself doesn't land, the
entire wedge is weak and the build needs to pivot before we sink weeks
into it.

## What you (the experimenter) will do

You will play the role of the AI in **Rubber Duck mode** in a chat
window. The participant will not know you are human until the debrief.
You follow the system prompt below, in spirit. Don't be a robot — be
a focused, terse, Socratic listener.

## Recruiting

Recruit 5 developers who match the anchor persona:

- ICs (not managers / not students)
- Mid-level or above (≥ 3 years professional experience)
- Currently working on a real codebase (not a personal project)
- Mix of backend / frontend / fullstack — diversity is good

Tell them: "I'm researching how developers think through problems out loud.
I have a chat-based prototype. I'd like 15 minutes — 10 minutes of using it
and 5 minutes of feedback."

Do **not** tell them:

- That you are the AI.
- That this is for a product you are building.

Both will bias responses.

## Setup

- A blank chat window (any tool — Slack DM with yourself, a terminal, a
  Google Doc, doesn't matter — you just need synchronous text exchange).
- Their problem: ask them to bring a real bug, design question, or
  decision they're currently stuck on. Not hypothetical.

## Session script (10 minutes)

**Opening (you, written):**

> "Hi. I'm a brainstorming assistant. I'll ask questions to help you think
> through your problem out loud. I won't usually answer — I'll keep
> probing until you've worked it out yourself. Tell me what you're stuck
> on."

**Your behavior during the session:**

- **Ask, don't answer.** If they ask "what should I do?" — turn it back:
  "what's the actual constraint you're optimizing for?"
- **Reflect what they said back, sharper.** "So you're saying X because
  Y — but did you check Z?"
- **Probe for the unspoken assumption.** "What would have to be true for
  this to *not* be the right move?"
- **Refuse to summarize unless they ask.** Closing summaries kill the
  thinking flow.
- **One question per message.** Two-question messages overwhelm.
- **Don't be cute.** No "great question," no "interesting." Be direct.
- **End the session at 10 minutes** even if they want to continue —
  consistency matters across participants.

**Closing (you, written):**

> "We're at 10 minutes. Where do you feel like you landed?"

Let them answer. Then transition to debrief.

## Debrief (5 minutes, voice or chat)

Reveal: "I should mention — I was the human, not the AI. I'm validating
whether this style of thinking partner would be useful as a real product."

Then ask, in this exact order:

1. **Did you feel thought-with?** (open-ended)
2. **Did the questions move you forward, or feel like obstacles?**
3. **Was there a moment where you wished it had just answered?**
4. **If this existed as a real tool — voice in, voice out, remembered
   your projects between sessions — would you pay $15/mo for it?**
   (yes / no / probably-not-but-keep-talking)
5. **What would you call it?** (just to harvest naming ideas)

Record exact quotes for the four-pillar questions in
`docs/validation_results.md`.

## Scoring

For each participant, record:

- **Posture-felt** (yes / mixed / no) — answers to Q1+Q2
- **Wished-it-answered** (yes / no) — answer to Q3
- **Pay $15/mo** (yes / probably / no)

## Decision criteria

| Outcome | Action |
|---------|--------|
| ≥ 3/5 say posture-felt = yes AND ≥ 3/5 say pay = yes-or-probably | Wedge is real. Build proceeds. |
| ≥ 3/5 say posture-felt = yes BUT ≥ 4/5 say pay = no | Posture works but bundle isn't worth $15/mo. Revisit pricing or distribution. |
| < 3/5 say posture-felt = yes | Posture itself is weak. Stop building Phase 1. Re-examine: is it the questions? the cadence? the absence of voice? Run another 5-person round with a tweaked script. |

## What we're NOT testing in this round

- Voice quality (Phase 0.4)
- Memory (impossible to test in 10 minutes)
- The other two modes — Devil's Advocate and Architect (test those after
  Rubber Duck validates)
- Any actual product (this is purely the posture hypothesis)
