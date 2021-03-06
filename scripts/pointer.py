#!/usr/bin/python
"""Usage: pointer.py [-bt] <offset>

Calculates the pointer value for a given offset for Game Boy roms.

Arguments
    <offset>    Offset for which to compute the pointer

Options:
    -b --bigendian   Use big endian mode
    -t --threebyte       Calculate 3 byte pointer

"""
from math import floor
from docopt import docopt


def get_2byte_pointer(offset, big_endian=False):
    offset = "0x" + offset[-4:]
    offset = int(offset, base=16)
    offset = (offset % 0x4000) + 0x4000

    pointer_str = hex(offset)
    if (not big_endian):
        pointer_str = "0x" + pointer_str[4:6] + pointer_str[2:4]

    pointer = int(pointer_str, base=16)
    return pointer


def get_3byte_pointer(offset):
    two_byte_pointer = get_2byte_pointer(offset, big_endian=True)
    offset = int(offset, base=16)
    bank_number = floor(offset / 0x4000)
    pointer = (bank_number * 0x4000) + (two_byte_pointer - 0x4000)
    return int(pointer)


class ROMPointer(object):
    def __init__(self, offset, big_endian=False):
        self.offset = offset
        self.two_bytes = get_2byte_pointer(offset, big_endian=big_endian)
        self.three_bytes = get_3byte_pointer(offset)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    offset = arguments["<offset>"]

    pointer = ROMPointer(offset, big_endian=arguments["--bigendian"])
    if arguments["--threebyte"]:
        print("{0:0{1}X}".format(pointer.three_bytes, 6))
    else:
        print("{0:0{1}X}".format(pointer.two_bytes, 4))
