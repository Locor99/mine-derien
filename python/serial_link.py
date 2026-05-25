import time

import serial
from serial.tools import list_ports

DEFAULT_BAUD = 115200
ARDUINO_RESET_DELAY_SECONDS = 2.0

ARDUINO_USB_VENDOR_IDS = {0x2341, 0x2A03, 0x1A86, 0x0403, 0x10C4}
ARDUINO_TEXT_KEYWORDS = ("arduino", "ch340", "ch341", "usb-serial", "usb serial", "wch", "ftdi")
ARDUINO_DEVICE_KEYWORDS = ("ACM", "ttyUSB")


def port_looks_like_arduino(port):
    if port.vid in ARDUINO_USB_VENDOR_IDS:
        return True
    description = f"{port.manufacturer or ''} {port.description or ''} {port.product or ''}".lower()
    if any(keyword in description for keyword in ARDUINO_TEXT_KEYWORDS):
        return True
    return any(keyword in port.device for keyword in ARDUINO_DEVICE_KEYWORDS)


def find_arduino_port():
    for port in list_ports.comports():
        if port_looks_like_arduino(port):
            return port.device
    return None


class SerialLink:
    def __init__(self, port, baud=DEFAULT_BAUD, timeout=2.0):
        self.connection = serial.Serial(port, baud, timeout=timeout)
        time.sleep(ARDUINO_RESET_DELAY_SECONDS)
        self.connection.reset_input_buffer()

    def send(self, command):
        self.connection.write((command + "\n").encode("ascii"))

    def read_reply(self):
        return self.connection.readline().decode("ascii").strip()

    def request(self, command):
        self.send(command)
        return self.read_reply()

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()
