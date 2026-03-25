import time
from dataclasses import dataclass, field
from threading import Lock

SECTION_COUNT = 37


@dataclass
class PwmParameters:
    on_ms: float
    off_ms: float

    @staticmethod
    def from_frequency_and_duty(frequency_hz: float, duty_percent: float) -> "PwmParameters":
        period_ms = 1000.0 / frequency_hz
        return PwmParameters(
            on_ms=period_ms * duty_percent / 100.0,
            off_ms=period_ms * (100.0 - duty_percent) / 100.0,
        )


@dataclass
class SharedState:
    section_states: list[int] = field(default_factory=lambda: [0] * SECTION_COUNT)
    cycle_count: int = 0
    actual_hz: float = 0.0
    start_time: float = field(default_factory=time.monotonic)
    running: bool = True
    port_lock: Lock = field(default_factory=Lock)
