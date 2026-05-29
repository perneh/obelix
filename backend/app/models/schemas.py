"""Pydantic models for messages, transport and scenarios."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TransportProtocol(str, Enum):
    UDP = "udp"
    TCP = "tcp"


class MotionMode(str, Enum):
    WAYPOINTS = "waypoints"
    DIRECTION = "direction"


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


class MotionWaypoint(BaseModel):
    """One point on a scenario route (category-specific coordinates)."""

    latitude_deg: float | None = None
    longitude_deg: float | None = None
    x_m: float | None = None
    y_m: float | None = None
    rho_nm: float | None = None
    theta_deg: float | None = None
    azimuth: float | None = None
    geometric_altitude_ft: float | None = None
    flight_level: float | None = None


class StepMotion(BaseModel):
    """Animate position along waypoints or in a fixed direction from the start point."""

    enabled: bool = False
    mode: MotionMode = MotionMode.DIRECTION
    waypoints: list[MotionWaypoint] = Field(default_factory=list)
    heading_deg: float = Field(90.0, description="Direction of travel: 0=North, 90=East")
    step_distance: float = Field(
        1000.0,
        gt=0,
        description="Distance per tick: metres (Cat 62), NM (Cat 48), degrees (Cat 34)",
    )
    ticks: int = Field(10, ge=2, description="Number of messages to send along the route")
    tick_interval_ms: int = Field(1000, ge=0, description="Delay between each message")
    update_time: bool = True
    derive_velocity: bool = True


class ScenarioStep(BaseModel):
    id: str
    name: str = ""
    message: AsterixMessage
    delay_ms: int = Field(0, ge=0, description="Delay before this step relative to previous")
    repeat: int = Field(1, ge=1, description="Number of times to send this step (ignored when motion is enabled)")
    motion: StepMotion | None = None


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


class ConfigurationScope(str, Enum):
    LOCAL = "local"
    SHARED = "shared"


class MessageConfiguration(BaseModel):
    """Saved field values for one ASTERIX category."""

    id: str
    name: str
    description: str = ""
    scope: ConfigurationScope = ConfigurationScope.LOCAL
    message: AsterixMessage

    @property
    def config_id(self) -> str:
        from app.core.configuration_storage import category_dir_name

        return f"{self.scope.value}:{category_dir_name(self.message.category)}:{self.id}"
