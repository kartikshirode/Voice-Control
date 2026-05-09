"""WebSocket protocol models shared between the core, the FastAPI server, and clients.

This is the *only* module that clients (`ui/gradio_app.py`, `mcp_server/server.py`)
are permitted to import from `core.*`. It defines the contract surface; everything
else in core is implementation. The CI test in `tests/ci/test_handler_imports.py`
enforces this rule.
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums and shared primitives
# ---------------------------------------------------------------------------


class Mode(str, Enum):
    """Brainstorming postures. New modes are added by dropping a file into
    `core/prompts/modes/` and a class into `core/modes/`."""

    RUBBER_DUCK = "rubber_duck"
    DEVILS_ADVOCATE = "devils_advocate"
    ARCHITECT = "architect"


class ModelState(str, Enum):
    """Active LLM backend, surfaced to the UI as a colored badge."""

    GEMINI = "gemini"
    QWEN_OFFLINE = "qwen-offline"
    QWEN_PRIVACY = "qwen-privacy"
    QWEN_FALLBACK = "qwen-fallback"
    QWEN_BUDGET = "qwen-budget"


class MemoryScope(str, Enum):
    """Where a remembered fact is written.

    `central` is cloud-loadable and forbidden in privacy mode.
    `central_private` is local-only and never reaches a cloud API.
    `project` is per-project semantic memory.
    """

    CENTRAL = "central"
    CENTRAL_PRIVATE = "central_private"
    PROJECT = "project"


# ---------------------------------------------------------------------------
# Client → Server messages
# ---------------------------------------------------------------------------


class TurnStart(BaseModel):
    type: Literal["turn_start"] = "turn_start"
    project: str
    session_id: str
    audio: str  # base64-encoded


class ConfirmationResponse(BaseModel):
    type: Literal["confirmation_response"] = "confirmation_response"
    pending_id: str
    accept: bool


class SetPrivacyMode(BaseModel):
    type: Literal["set_privacy_mode"] = "set_privacy_mode"
    on: bool


class SetProject(BaseModel):
    type: Literal["set_project"] = "set_project"
    name: str


class SetMode(BaseModel):
    type: Literal["set_mode"] = "set_mode"
    mode: Mode


class SessionEnd(BaseModel):
    type: Literal["session_end"] = "session_end"


ClientMessage = Annotated[
    Union[TurnStart, ConfirmationResponse, SetPrivacyMode, SetProject, SetMode, SessionEnd],
    Field(discriminator="type"),
]


# ---------------------------------------------------------------------------
# Server → Client messages
# ---------------------------------------------------------------------------


class Transcription(BaseModel):
    type: Literal["transcription"] = "transcription"
    text: str


class Intent(BaseModel):
    type: Literal["intent"] = "intent"
    labels: list[str]


class LLMToken(BaseModel):
    type: Literal["llm_token"] = "llm_token"
    text: str


class TTSChunk(BaseModel):
    type: Literal["tts_chunk"] = "tts_chunk"
    audio: str  # base64-encoded
    sentence_index: int


class ToolCall(BaseModel):
    type: Literal["tool_call"] = "tool_call"
    name: str
    args: dict[str, object]


class ToolResult(BaseModel):
    type: Literal["tool_result"] = "tool_result"
    name: str
    result: dict[str, object]


class ConfirmationRequired(BaseModel):
    type: Literal["confirmation_required"] = "confirmation_required"
    pending_id: str
    tool: str
    args: dict[str, object]
    preview: str
    expires_at: float  # unix timestamp


class ModelStateEvent(BaseModel):
    type: Literal["model_state"] = "model_state"
    active: ModelState
    reason: str | None = None


class ConsolidationStatus(BaseModel):
    type: Literal["consolidation_status"] = "consolidation_status"
    pending_count: int
    current_state: Literal["idle", "running", "paused_privacy", "error"]


class TurnEnd(BaseModel):
    type: Literal["turn_end"] = "turn_end"
    status: Literal["ok", "interrupted", "error"] = "ok"


class ErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    code: str
    message: str


ServerMessage = Annotated[
    Union[
        Transcription,
        Intent,
        LLMToken,
        TTSChunk,
        ToolCall,
        ToolResult,
        ConfirmationRequired,
        ModelStateEvent,
        ConsolidationStatus,
        TurnEnd,
        ErrorEvent,
    ],
    Field(discriminator="type"),
]


# ---------------------------------------------------------------------------
# MCP tool surface — typed return models for the canonical client
# ---------------------------------------------------------------------------


class MemoryRecord(BaseModel):
    """A single consolidated memory record returned by recall_project_memory."""

    id: str
    project: str
    type: Literal["decision", "open_question", "attempt", "context", "fact"]
    content: str
    created_at: float
    valid_from: float | None = None
    superseded_by: str | None = None
    score: float | None = None  # similarity score on retrieval


class BrainstormSessionStarted(BaseModel):
    session_id: str
    project: str
    mode: Mode


class BrainstormTurnResult(BaseModel):
    session_id: str
    reply_text: str  # the on-screen / text reply (display content if tagged)
    voice_text: str | None = None  # spoken portion only, if tags were used
    intent: list[str]
    model_used: ModelState


class BrainstormSessionEnded(BaseModel):
    session_id: str
    artifact_markdown: str
    artifact_path: str | None = None
    consolidation_queued: bool = False
