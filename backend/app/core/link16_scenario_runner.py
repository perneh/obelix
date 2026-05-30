"""Link 16 scenario execution engine."""

from __future__ import annotations

import asyncio
import uuid

from app.link16.registry import encode_message
from app.models.link16_schemas import Link16Scenario
from app.models.schemas import ScenarioRunState, ScenarioStatus, TransportProtocol
from app.transport.sender import send_tcp, send_udp


class Link16ScenarioRunner:
    def __init__(self) -> None:
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._states: dict[str, ScenarioRunState] = {}
        self._pause_events: dict[str, asyncio.Event] = {}
        self._stop_events: dict[str, asyncio.Event] = {}

    def get_state(self, scenario_id: str) -> ScenarioRunState | None:
        return self._states.get(scenario_id)

    def list_states(self) -> list[ScenarioRunState]:
        return list(self._states.values())

    async def start(self, scenario: Link16Scenario) -> ScenarioRunState:
        scenario_id = scenario.id or str(uuid.uuid4())
        if scenario_id in self._tasks and not self._tasks[scenario_id].done():
            raise RuntimeError(f"Link 16 scenario {scenario_id} is already running")

        pause_event = asyncio.Event()
        pause_event.set()
        stop_event = asyncio.Event()

        state = ScenarioRunState(
            scenario_id=scenario_id,
            status=ScenarioStatus.RUNNING,
            current_step=0,
            current_loop=0,
            messages_sent=0,
        )
        self._states[scenario_id] = state
        self._pause_events[scenario_id] = pause_event
        self._stop_events[scenario_id] = stop_event

        task = asyncio.create_task(
            self._run(scenario, scenario_id, pause_event, stop_event),
            name=f"link16-scenario-{scenario_id}",
        )
        self._tasks[scenario_id] = task
        task.add_done_callback(lambda _: self._finalize(scenario_id))
        return state

    def pause(self, scenario_id: str) -> ScenarioRunState:
        state = self._require_state(scenario_id)
        if state.status != ScenarioStatus.RUNNING:
            raise RuntimeError(f"Scenario {scenario_id} is not running")
        self._pause_events[scenario_id].clear()
        state.status = ScenarioStatus.PAUSED
        return state

    def resume(self, scenario_id: str) -> ScenarioRunState:
        state = self._require_state(scenario_id)
        if state.status != ScenarioStatus.PAUSED:
            raise RuntimeError(f"Scenario {scenario_id} is not paused")
        self._pause_events[scenario_id].set()
        state.status = ScenarioStatus.RUNNING
        return state

    def stop(self, scenario_id: str) -> ScenarioRunState:
        state = self._require_state(scenario_id)
        self._stop_events[scenario_id].set()
        self._pause_events[scenario_id].set()
        state.status = ScenarioStatus.STOPPED
        return state

    def _require_state(self, scenario_id: str) -> ScenarioRunState:
        state = self._states.get(scenario_id)
        if state is None:
            raise KeyError(f"Unknown Link 16 scenario run: {scenario_id}")
        return state

    def _finalize(self, scenario_id: str) -> None:
        state = self._states.get(scenario_id)
        if state and state.status == ScenarioStatus.RUNNING:
            state.status = ScenarioStatus.COMPLETED

    async def _run(
        self,
        scenario: Link16Scenario,
        scenario_id: str,
        pause_event: asyncio.Event,
        stop_event: asyncio.Event,
    ) -> None:
        state = self._states[scenario_id]
        loop_num = 0

        try:
            while not stop_event.is_set():
                if scenario.loop_count > 0 and loop_num >= scenario.loop_count:
                    break

                state.current_loop = loop_num
                for step_index, step in enumerate(scenario.steps):
                    if stop_event.is_set():
                        break

                    state.current_step = step_index
                    await pause_event.wait()
                    if stop_event.is_set():
                        break

                    if step.delay_ms > 0:
                        await self._interruptible_sleep(step.delay_ms, pause_event, stop_event)
                        if stop_event.is_set():
                            break

                    for _ in range(step.repeat):
                        await pause_event.wait()
                        if stop_event.is_set():
                            break

                        data = encode_message(step.message.j_series, step.message.fields)
                        await self._send(
                            data,
                            scenario.transport.host,
                            scenario.transport.port,
                            scenario.transport.protocol,
                        )
                        state.messages_sent += 1

                loop_num += 1
                if scenario.loop_count > 0 and loop_num >= scenario.loop_count:
                    break
                if scenario.interval_ms > 0 and not stop_event.is_set():
                    await self._interruptible_sleep(scenario.interval_ms, pause_event, stop_event)

            if not stop_event.is_set():
                state.status = ScenarioStatus.COMPLETED
        except Exception as exc:
            state.status = ScenarioStatus.ERROR
            state.error = str(exc)

    async def _interruptible_sleep(
        self,
        delay_ms: int,
        pause_event: asyncio.Event,
        stop_event: asyncio.Event,
    ) -> None:
        elapsed = 0
        chunk_ms = 50
        while elapsed < delay_ms:
            if stop_event.is_set():
                return
            await pause_event.wait()
            await asyncio.sleep(min(chunk_ms, delay_ms - elapsed) / 1000)
            elapsed += chunk_ms

    async def _send(
        self,
        data: bytes,
        host: str,
        port: int,
        protocol: TransportProtocol,
    ) -> None:
        if protocol == TransportProtocol.UDP:
            await send_udp(data, host, port)
        else:
            await send_tcp(data, host, port)


link16_scenario_runner = Link16ScenarioRunner()
