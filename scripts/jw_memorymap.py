"""jw_memorymap.py - Helper file defining constants for memory locations."""


SIGNS_DATA_POINTERS_START = 0x31E73
SIGNS_DATA_POINTERS_END = 0x31EA0

SIGNS_DATA_ALLOCATED_SPACE = [
    (0x31EA1, 0x320B1),  # Original block
    (0x333FB, 0x33A00),  # Window data block, first part
]

ENNEMIES_DATA_ALLOCATED_SPACE = [
    (0x30086, 0x3082B),  # Original block
    (0x33A01, 0x33FEB),  # Window data block, second part
]
