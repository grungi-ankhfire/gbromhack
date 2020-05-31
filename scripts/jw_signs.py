#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_signs.py extract <romfile> <tablefile> [-o <file>] [-s <address> -e <address>] 

Handle the extraction of sign data from the game Jungle Wars (GB).

Options:
    -o <file> --output <file>       Name of the output file to write [default: signs_output.yaml]
    -s <address> --start <address>  Address of the signs pointer table start
    -e <address> --end <address>    Address of the signs pointer table end

Arguments
    <romfile>    The file to extract from
    <tablefile>  The translation table file to use for interpreting the text.
"""

import pyaml
from docopt import docopt
from hexint import HexInt, hexint_representer
from translation_table import TranslationTable
from jw_memorymap import SIGNS_DATA_POINTERS_START, SIGNS_DATA_POINTERS_END

pyaml.add_representer(HexInt, hexint_representer)


class PointerTableExtractor:

    def __init__(self, rom, start, end):
        self.rom = rom
        self.start = start
        self.end = end

        self.pointers = []
        self.pointers_locations = {}

    def read_pointers(self):
        offset = self.start
        self.pointers = []

        bank = offset // 0x4000

        self.rom.seek(offset)
        while offset < self.end:
            raw_pointer = int.from_bytes(self.rom.read(2), "little")
            pointer = raw_pointer + 0x4000 * (bank-1)
            self.pointers.append(pointer)
            self.pointers_locations[pointer] = offset
            offset += 2


def extract_signs(rom, offset_start, offset_end, table):
    pointer_table = PointerTableExtractor(rom, offset_start, offset_end)
    pointer_table.read_pointers()

    result = {}

    sign_id = 0
    for pointer in pointer_table.pointers:
        rom.seek(pointer)

        sign = {}

        # This postulates that all signs have 3 lines, as there is no termination character
        for l in range(3):
            line_length = int.from_bytes(rom.read(1), 'little')
            line_text = bytearray()
            for _ in range(line_length):
                line_text += rom.read(1)

            line_text = table.convert_bytearray(line_text)
            
            sign[f'line{l}_original_length'] = line_length
            sign[f'line{l}_original_text'] = line_text
            sign[f'line{l}_translated_text'] = f'TODO{sign_id:02}{l}'

        sign['pointer_location'] = HexInt(pointer_table.pointers_locations[pointer], digits=5)

        result[HexInt(sign_id, digits=2)] = sign
        sign_id += 1

    return result


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')
    print(arguments)

    if arguments["extract"]:

        pointers_start = SIGNS_DATA_POINTERS_START
        if arguments['--start']:
            pointers_start = int(arguments['--start'], 16)

        pointers_end = SIGNS_DATA_POINTERS_END
        if arguments['--end']:
            pointers_end = int(arguments['--end'], 16)

        table = TranslationTable(arguments['<tablefile>'])

        rom = open(arguments["<romfile>"], 'rb+')

        res = {"signs" : extract_signs(rom, pointers_start, pointers_end, table)}

        rom.close()

        f = open(arguments['--output'], 'w', encoding='utf-8')
        f.write(pyaml.dump(res, indent=2, vspacing=[2, 1], width=float("inf"), string_val_style='"'))
        f.close()
