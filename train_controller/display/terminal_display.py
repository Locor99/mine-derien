import curses
import time

from train_controller.control.shared_state import SharedState

_TITLE = "MINE DERIEN ET PORT RIENAFER"
_SUBTITLE = "MD0809023"
_SEPARATOR = "--------------------------"
_STOP_HINT = "APPUYEZ SUR UNE TOUCHE POUR ARRETER"

_TITLE_COL = 29
_SUBTITLE_COL = 34
_SEPARATOR_COL = 29
_STOP_HINT_ROW = 23
_STOP_HINT_COL = 4

_SECTION_COLUMNS = (
    (range(0, 16), 4),
    (range(16, 32), 23),
    (range(32, 37), 43),
)
_HEADER_ROW = 3
_SECTIONS_START_ROW = 4
_HEADER_LABEL = "BLOC  ETAT"

_STATS_ROW = 20
_TIMING_ROW = 21
_CLOCK_ROW = 22
_STATS_COL = 4
_CLOCK_COL = 68


def init_screen(screen: curses.window) -> None:
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLUE)
    screen.bkgd(" ", curses.color_pair(1))
    screen.nodelay(True)
    screen.clear()
    screen.addstr(0, _TITLE_COL, _TITLE)
    screen.addstr(1, _SUBTITLE_COL, _SUBTITLE)
    screen.addstr(2, _SEPARATOR_COL, _SEPARATOR)
    screen.addstr(_STOP_HINT_ROW, _STOP_HINT_COL, _STOP_HINT)
    screen.refresh()


def render(screen: curses.window, state: SharedState) -> None:
    _render_section_columns(screen, state.section_states)
    _render_stats(screen, state)
    _render_clock(screen)
    screen.refresh()


def _render_section_columns(screen: curses.window, section_states: list[int]) -> None:
    for sections, col in _SECTION_COLUMNS:
        screen.addstr(_HEADER_ROW, col, _HEADER_LABEL)
        for offset, section in enumerate(sections):
            screen.addstr(_SECTIONS_START_ROW + offset, col, f"{section:<4}  {section_states[section]}")


def _render_stats(screen: curses.window, state: SharedState) -> None:
    screen.addstr(
        _STATS_ROW,
        _STATS_COL,
        f"FREQUENCY - ACTUAL: {state.actual_hz:<6.2f} Hz",
    )
    elapsed = time.monotonic() - state.start_time
    screen.addstr(
        _TIMING_ROW,
        _STATS_COL,
        f"ELAPSED: {elapsed:.1f}s   CYCLES: {state.cycle_count}",
    )


def _render_clock(screen: curses.window) -> None:
    screen.addstr(_CLOCK_ROW, _CLOCK_COL, time.strftime("%H:%M:%S"))
