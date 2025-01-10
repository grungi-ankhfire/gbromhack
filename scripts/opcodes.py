"""Gameboy opcodes

See: https://meganesu.github.io/generate-gb-opcodes/
"""

opcodes = {
    "nop": b'\x00',
    "ld b": b'\x06',
    "ld de": b'\x11',
    "jr": b'\x18',
    "ld hl": b'\x21',
    "inc a": b'\x3C',
    "ld a": b'\x3E',
    "jp": b'\xC3',
    "rst 0": b'\xC7',
    "ret": b'\xC9',
    "call": b'\xCD',
}


def nop() -> bytes:
    return b'\x00'

def ld_a(hex8: int) -> bytes:
    return b'\x3E' + hex8.to_bytes(1, 'little')

def ld_b(hex8: int) -> bytes:
    return b'\x06' + hex8.to_bytes(1, 'little')

def ld_de(hex16: int) -> bytes:
    return b'\x11' + hex16.to_bytes(2, 'little')

def ld_hl(hex16: int) -> bytes:
    return b'\x21' + hex16.to_bytes(2, 'little')

def rst_0() -> bytes:
    return b'\xC7'

def jr(hex8: int) -> bytes:
    return b'\x18' + hex8.to_bytes(1, 'little')

def jp(hex16: int) -> bytes:
    return b'\xC3' + hex16.to_bytes(2, 'little')

def call(hex16: int) -> bytes:
    return b'\xCD' + hex16.to_bytes(2, 'little')