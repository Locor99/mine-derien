import curses
import time

from train_controller.control.section_scanner import scan_all_sections
from train_controller.control.shared_state import SharedState
from train_controller.display.terminal_display import render
from train_controller.ports.port_protocol import PortProtocol

_SCAN_INTERVAL_S = 0.2
_ELAPSED_OFFSET_S = 1.0


def run_scan_loop(
    port: PortProtocol,
    screen: curses.window,
    state: SharedState,
) -> None:
    while state.running:
        loop_start = time.monotonic()
        state.section_states = scan_all_sections(port, state.port_lock)
        _update_actual_hz(state)
        render(screen, state)
        _stop_if_key_pressed(screen, state)
        _sleep_remaining(loop_start)


def _update_actual_hz(state: SharedState) -> None:
    elapsed = time.monotonic() - state.start_time + _ELAPSED_OFFSET_S
    state.actual_hz = state.cycle_count / elapsed


def _stop_if_key_pressed(screen: curses.window, state: SharedState) -> None:
    if screen.getch() != curses.ERR:
        state.running = False


def _sleep_remaining(loop_start: float) -> None:
    remaining = _SCAN_INTERVAL_S - (time.monotonic() - loop_start)
    if remaining > 0:
        time.sleep(remaining)
