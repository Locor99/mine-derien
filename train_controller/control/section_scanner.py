from threading import Lock

from train_controller.control.shared_state import SECTION_COUNT
from train_controller.ports.port_protocol import PortProtocol

_STATUS_BIT_3_POSITION = 3


def scan_all_sections(port: PortProtocol, lock: Lock) -> list[int]:
    return [_scan_section(port, lock, section) for section in range(SECTION_COUNT)]


def _scan_section(port: PortProtocol, lock: Lock, section: int) -> int:
    with lock:
        port.write_data(section)
        port.write_control(1)
        raw = port.read_status()
        port.write_control(0)
        port.write_control(2)
    return (raw >> _STATUS_BIT_3_POSITION) & 1
