"""Pydantic models for messages, transport and scenarios."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TransportProtocol(str, Enum):
    UDP = "udp"
    TCP = "tcp"


class AsterixMessage(BaseModel):
    category: int = Field(..., ge=1, le=255, description="ASTERIX category number")
    fields: dict[str, Any] = Field(default_factory=dict, description="Field values keyed by field id")


class EncodeRequest(BaseModel):
    message: AsterixMessage


class EncodeResponse(BaseModel):
    hex: str
    length: int
    category: int


class SendRequest(BaseModel):
    message: AsterixMessage
    host: str = "127.0.0.1"
    port: int = Field(8600, ge=1, le=65535)
    protocol: TransportProtocol = TransportProtocol.UDP


class SendResponse(BaseModel):
    success: bool
    bytes_sent: int
    host: str
    port: int
    protocol: TransportProtocol


class ScenarioStep(BaseModel):
    id: str
    name: str = ""
    message: AsterixMessage
    delay_ms: int = Field(0, ge=0, description="Delay before this step relative to previous")
    repeat: int = Field(1, ge=1, description="Number of times to send this step")


class ScenarioTransport(BaseModel):
    host: str = "127.0.0.1"
    port: int = Field(8600, ge=1, le=65535)
    protocol: TransportProtocol = TransportProtocol.UDP


class Scenario(BaseModel):
    id: str
    name: str
    description: str = ""
    transport: ScenarioTransport = Field(default_factory=ScenarioTransport)
    loop_count: int = Field(1, ge=0, description="0 = infinite loop")
    interval_ms: int = Field(1000, ge=0, description="Delay between full scenario loops")
    steps: list[ScenarioStep] = Field(default_factory=list)


class ScenarioRunRequest(BaseModel):
    scenario: Scenario


class ScenarioStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ERROR = "error"


class ScenarioRunState(BaseModel):
    scenario_id: str
    status: ScenarioStatus
    current_step: int = 0
    current_loop: int = 0
    messages_sent: int = 0
    error: str | None = None


class MessageTemplate(BaseModel):
    id: str
    name: str
    description: str = ""
    message: AsterixMessage
