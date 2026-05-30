"""Pydantic models for Link 16 messages and transport."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.models.schemas import ConfigurationScope, ScenarioTransport, TransportProtocol


class Link16MessagePayload(BaseModel):
    j_series: str = Field(..., description="J-series label, e.g. J3.2")
    fields: dict[str, Any] = Field(default_factory=dict, description="Field values keyed by field id")


class Link16Configuration(BaseModel):
    """Saved field values for one Link 16 J-message."""

    id: str
    name: str
    description: str = ""
    scope: ConfigurationScope = ConfigurationScope.LOCAL
    message: Link16MessagePayload

    @property
    def config_id(self) -> str:
        from app.core.link16_configuration_storage import make_config_id

        return make_config_id(self.scope, self.message.j_series, self.id)


class Link16ScenarioStep(BaseModel):
    id: str
    name: str = ""
    message: Link16MessagePayload
    delay_ms: int = Field(0, ge=0)
    repeat: int = Field(1, ge=1)


class Link16Scenario(BaseModel):
    id: str
    name: str
    description: str = ""
    transport: ScenarioTransport = Field(
        default_factory=lambda: ScenarioTransport(host="host.docker.internal", port=8700)
    )
    loop_count: int = Field(1, ge=0)
    interval_ms: int = Field(1000, ge=0)
    steps: list[Link16ScenarioStep] = Field(default_factory=list)


class Link16EncodeRequest(BaseModel):
    message: Link16MessagePayload


class Link16EncodeResponse(BaseModel):
    hex: str
    length: int
    j_series: str


class Link16SendRequest(BaseModel):
    message: Link16MessagePayload
    host: str = "127.0.0.1"
    port: int = Field(8700, ge=1, le=65535, description="Default Link 16 JREAP port")
    protocol: TransportProtocol = TransportProtocol.UDP


class Link16SendResponse(BaseModel):
    success: bool
    bytes_sent: int
    host: str
    port: int
    protocol: TransportProtocol
    j_series: str
