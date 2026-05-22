import time

import serial
from serial.tools import list_ports

DEFAULT_BAUD = 115200
ARDUINO_RESET_DELAY_SECONDS = 2.0


def find_arduino_port():
    for port in list_ports.comports():
        manufacturer = port.manufacturer or ""
        if "Arduino" in manufacturer or "ACM" in port.device or "USB" in port.device:
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
