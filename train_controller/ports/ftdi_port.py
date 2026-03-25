from pyftdi.gpio import GpioMpsseController

FTDI_URL = "ftdi://ftdi:232h/1"
LATENCY_TIMER_MS = 1
MPSSE_FREQUENCY_HZ = 1_000_000

_DATA_MASK = 0x00FF
_STROBE_PIN = 1 << 9
_AUTOFEED_PIN = 1 << 10
_TRAIN_DETECT_PIN = 1 << 8

_OUTPUT_DIRECTION = _DATA_MASK | _STROBE_PIN | _AUTOFEED_PIN
_IDLE_OUTPUT = _STROBE_PIN | _AUTOFEED_PIN

_CONTROL_BIT_0 = 0x01
_CONTROL_BIT_1 = 0x02
_STATUS_BIT_3_POSITION = 3


def build_ftdi_port(url: str = FTDI_URL) -> "FtdiPort":
    gpio = GpioMpsseController()
    gpio.configure(url, direction=_OUTPUT_DIRECTION, frequency=MPSSE_FREQUENCY_HZ)
    gpio.ftdi.set_latency_timer(LATENCY_TIMER_MS)
    return FtdiPort(gpio)


class FtdiPort:
    def __init__(self, gpio: GpioMpsseController) -> None:
        self._gpio = gpio
        self._current_output = _IDLE_OUTPUT
        self._gpio.write(self._current_output)

    def write_data(self, value: int) -> None:
        self._current_output = (self._current_output & ~_DATA_MASK) | (value & _DATA_MASK)
        self._gpio.write(self._current_output)

    def write_control(self, value: int) -> None:
        strobe = 0 if (value & _CONTROL_BIT_0) else _STROBE_PIN
        autofeed = 0 if (value & _CONTROL_BIT_1) else _AUTOFEED_PIN
        self._current_output = (self._current_output & _DATA_MASK) | strobe | autofeed
        self._gpio.write(self._current_output)

    def read_status(self) -> int:
        raw = self._gpio.read(readlen=1)[0]
        train_detect_pin = (raw & _TRAIN_DETECT_PIN) >> 8
        status_bit3 = 1 - train_detect_pin
        return status_bit3 << _STATUS_BIT_3_POSITION

    def close(self) -> None:
        self._gpio.close()
