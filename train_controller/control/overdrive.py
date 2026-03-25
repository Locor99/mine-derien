import time
from threading import Lock

from train_controller.ports.port_protocol import PortProtocol

_ENERGIZE_OFFSET = 128
_OVERDRIVE_GROUPS = ((0, 7), (8, 15), (16, 36))
_INTER_GROUP_PAUSE_S = 0.0002


def run_overdrive(port: PortProtocol, lock: Lock) -> None:
    for start, end in _OVERDRIVE_GROUPS:
        _pulse_group(port, lock, start, end)
        time.sleep(_INTER_GROUP_PAUSE_S)
    _reset_port(port, lock)


def _pulse_group(port: PortProtocol, lock: Lock, start: int, end: int) -> None:
    with lock:
        for section in range(start, end + 1):
            port.write_data(_ENERGIZE_OFFSET + section)
            port.write_control(0)
            port.write_control(1)


def _reset_port(port: PortProtocol, lock: Lock) -> None:
    with lock:
        port.write_data(0)
        port.write_control(1)
        port.write_control(2)
