from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

Role = Literal["system", "user", "assistant", "tool"]


class ChatCompletionMessageToolCallFunction(BaseModel):
    name: str
    arguments: str


class ChatCompletionMessageToolCall(BaseModel):
    id: str
    type: Literal["function"] = "function"
    function: ChatCompletionMessageToolCallFunction


class ChatCompletionMessage(BaseModel):
    role: Role
    content: Optional[Union[str, List[Dict[str, Any]]]] = None
    tool_calls: Optional[List[ChatCompletionMessageToolCall]] = None
    tool_call_id: Optional[str] = None
    refusal: Optional[str] = None


class Choice(BaseModel):
    index: int
    message: ChatCompletionMessage
    finish_reason: Optional[str] = None
    logprobs: Optional[Any] = None


class CompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletion(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Optional[CompletionUsage] = None
    system_fingerprint: Optional[str] = None


class ChunkDelta(BaseModel):
    role: Optional[Role] = None
    content: Optional[str] = None
    tool_calls: Optional[List[ChatCompletionMessageToolCall]] = None


class ChunkChoice(BaseModel):
    index: int
    delta: ChunkDelta
    finish_reason: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChunkChoice]


class Model(BaseModel):
    id: str
    object: str = "model"
    created: int = 0
    owned_by: Optional[str] = None


class ModelList(BaseModel):
    object: str = "list"
    data: List[Model] = Field(default_factory=list)


class FunctionParameters(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ChatCompletionToolParamOption(BaseModel):
    type: Literal["function"] = "function"
    function: FunctionParameters


ChatCompletionToolParam = ChatCompletionToolParamOption
