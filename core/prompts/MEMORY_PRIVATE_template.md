# Central memory (local-only)

This file is **only loaded when the active backend is the local model** (Qwen).
Cloud LLMs never see it.

Use this for proprietary employer context, NDA-bound topics, internal
project names, anything you would not paste into a public LLM.

The agent will only write here when you explicitly ask via `remember_fact`
with `scope=central_private`. In privacy mode, it will also voice-confirm
each write.

Hard cap: 4 KB. When exceeded, the local model rewrites this file to ≤ 2 KB
preserving every distinct fact (compaction never touches a cloud API).

## Identity

<!-- Internal role, employer-specific context. -->

## Tech Stack

<!-- Internal tools, proprietary systems, internal naming conventions. -->

## Preferences

<!-- Anything sensitive about how you work that shouldn't reach a cloud API. -->

## Active Projects

<!-- Internal project names with brief context. -->
