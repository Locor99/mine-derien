import time
from threading import Lock

from train_controller.control.gating_rules import sections_to_skip
from train_controller.control.overdrive import run_overdrive
from train_controller.control.shared_state import SECTION_COUNT, PwmParameters, SharedState
from train_controller.ports.port_protocol import PortProtocol

_ENERGIZE_OFFSET = 128
_MS_TO_S = 0.001


def run_pwm_loop(port: PortProtocol, params: PwmParameters, state: SharedState) -> None:
    while state.running:
        _energize_active_sections(port, state.port_lock, state.section_states, state.cycle_count)
        time.sleep(params.on_ms * _MS_TO_S)
        _deenergize_all(port, state.port_lock)
        time.sleep(params.off_ms * _MS_TO_S)
        run_overdrive(port, state.port_lock)
        state.cycle_count += 1


def _energize_active_sections(
    port: PortProtocol,
    lock: Lock,
    section_states: list[int],
    cycle_count: int,
) -> None:
    skipped = sections_to_skip(section_states, cycle_count)
    for section in range(SECTION_COUNT):
        if section not in skipped:
            _energize_section(port, lock, section)


def _energize_section(port: PortProtocol, lock: Lock, section: int) -> None:
    with lock:
        port.write_data(_ENERGIZE_OFFSET + section)
        port.write_control(1)
        port.write_control(0)


def _deenergize_all(port: PortProtocol, lock: Lock) -> None:
    with lock:
        port.write_data(0)
        port.write_control(1)
        port.write_control(2)
