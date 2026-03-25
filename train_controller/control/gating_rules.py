from train_controller.control.shared_state import SECTION_COUNT

_SPEED_REDUCED_SECTIONS = frozenset({0, 1, 2, 7, 14})
_SECTION_8_STOP_SECTIONS = frozenset({0, 1, 2, 7})
_ALWAYS_SKIPPED_SECTIONS = frozenset({15})
_ENTRY_GUARD_INDICES = range(4)
_SPEED_REDUCTION_MODULO = 9
_SPEED_REDUCTION_REMAINDER = 1
_SECTION_8 = 8
_SECTION_14 = 14
_SECTION_2 = 2
_SECTION_3 = 3


def sections_to_skip(section_states: list[int], cycle_count: int) -> frozenset[int]:
    skipped: set[int] = set(_ALWAYS_SKIPPED_SECTIONS)
    skipped |= _speed_reduction_skips(cycle_count)
    skipped |= _section_8_stop_skips(section_states)
    skipped |= _entry_guard_skips(section_states)
    skipped |= _section_14_skips(section_states)
    return frozenset(skipped)


def _speed_reduction_skips(cycle_count: int) -> set[int]:
    if cycle_count % _SPEED_REDUCTION_MODULO == _SPEED_REDUCTION_REMAINDER:
        return set(_SPEED_REDUCED_SECTIONS)
    return set()


def _section_8_stop_skips(section_states: list[int]) -> set[int]:
    if section_states[_SECTION_8] == 1:
        return set(_SECTION_8_STOP_SECTIONS)
    return set()


def _entry_guard_skips(section_states: list[int]) -> set[int]:
    if any(section_states[i] == 1 for i in _ENTRY_GUARD_INDICES):
        return set(range(SECTION_COUNT))
    return set()


def _section_14_skips(section_states: list[int]) -> set[int]:
    if section_states[_SECTION_2] == 1 or section_states[_SECTION_3] == 1:
        return {_SECTION_14}
    return set()
