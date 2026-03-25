import curses
import threading

from train_controller.control.pwm_loop import run_pwm_loop
from train_controller.control.scan_loop import run_scan_loop
from train_controller.control.shared_state import PwmParameters, SharedState
from train_controller.display.terminal_display import init_screen
from train_controller.ports.ftdi_port import build_ftdi_port

_FREQUENCY_HZ = 15.0
_DUTY_CYCLE_PERCENT = 25.0
_THREAD_JOIN_TIMEOUT_S = 2.0


def main() -> None:
    params = PwmParameters.from_frequency_and_duty(_FREQUENCY_HZ, _DUTY_CYCLE_PERCENT)
    state = SharedState()
    port = build_ftdi_port()

    try:
        curses.wrapper(lambda screen: _run(screen, port, params, state))
    finally:
        port.close()


def _run(
    screen: curses.window,
    port,
    params: PwmParameters,
    state: SharedState,
) -> None:
    init_screen(screen)

    pwm_thread = threading.Thread(
        target=run_pwm_loop,
        args=(port, params, state),
        daemon=True,
    )
    scan_thread = threading.Thread(
        target=run_scan_loop,
        args=(port, screen, state),
        daemon=True,
    )

    pwm_thread.start()
    scan_thread.start()

    pwm_thread.join()
    scan_thread.join(timeout=_THREAD_JOIN_TIMEOUT_S)


if __name__ == "__main__":
    main()
