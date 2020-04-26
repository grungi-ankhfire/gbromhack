#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_patcher.py create <romfile> <start> <end> <outputfile>
          jw_patcher.py apply <patchfile> <romfile> <start>
          jw_patcher.py create --font <romfile> <outputfile>
          jw_patcher.py apply --font <patchfile> <romfile>

Tool to create and apply Jungle Wars patches. This just overrides everything
in the ROM, and is not intended for final patching. The goal is to help during
hacking, before creating proper IPS patches.

Arguments
    <romfile>    The rom file to open
    <patchfile>  The patch file to read from
    <start>      The offset in hex to start the patch from
    <end>        The offset in hex to finish reading the patch at
    <outputfile> Patch file to write to

Options
    --font       Use precomputed Jungle Wars font offsets
"""
from docopt import docopt

FONT_AREA_START = 0x1EDAD
FONT_AREA_END = 0x1F254

rom = None


def create_patch(rom_file, output_path, start, end):
    output_file = open(output_path, 'wb')

    rom_file.seek(start)

    # +1 to include the end offset in the patch
    patch = rom_file.read(end - start + 1)
    output_file.write(patch)

    output_file.close()


def apply_patch(rom_file, patch_path, start):
    patch_file = open(patch_path, 'rb')
    patch = patch_file.read()
    patch_file.close()

    rom_file.seek(start)
    rom_file.write(patch)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    if arguments['create']:
        offset = 0x00
        end_offset = 0x00

        if arguments['--font']:
            offset = FONT_AREA_START
            end_offset = FONT_AREA_END
        else:
            offset = int(arguments["<start>"], base=16)
            end_offset = int(arguments["<end>"], base=16)
        output = arguments["<outputfile>"]

        rom = open(arguments["<romfile>"], 'rb')

        create_patch(rom, output, offset, end_offset)

        rom.close()

    elif arguments['apply']:
        offset = 0x00

        if arguments['--font']:
            offset = FONT_AREA_START
        else:
            offset = int(arguments['<start>'], base=16)
 
        patch_path = arguments['<patchfile>']

        rom = open(arguments["<romfile>"], 'rb+')

        apply_patch(rom, patch_path, offset)

        rom.close()
