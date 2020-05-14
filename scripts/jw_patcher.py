#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_patcher.py create <romfile> <start> <end> <outputfile>
          jw_patcher.py apply <patchfile> <romfile> <start>
          jw_patcher.py create --font <romfile> <outputfile>
          jw_patcher.py apply --font <patchfile> <romfile>
          jw_patcher.py apply_windows <romfile>
          jw_patcher.py apply_enemies <romfile>

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


def insert_enemies_code(rom_file):
    # Change the bank from which to load
    rom_file.seek(0x0c6e)
    rom_file.write(b'\x1E')

    # Change the enemy loading code
    rom_file.seek(0x0f9e)
    rom_file.write(b'\x3E\x1E')         # ld a, 1E
    rom_file.write(b'\xC7')             # RST 0
    rom_file.write(b'\xC3\x00\x45')     # jp $4500

    rom_file.seek(0x1E * 0x4000 + 0x500)
    rom_file.write(b'\x21\x00\x40')     # ld hl, $4000
    rom_file.write(b'\xCD\x71\x3A')     # call Load_Pointer_Into_HL
    rom_file.write(b'\x3E\x16')         # ld a, $16
    rom_file.write(b'\xEF')             # rst $28
    rom_file.write(b'\xD1')             # pop de
    rom_file.write(b'\x06\x08')         # ld b, $08
    rom_file.write(b'\xCD\x43\x0D')     # call Call_000_0d43
    rom_file.write(b'\xC3\xAD\x0F')     # jp $0FAD


def insert_windows_code(rom_file):

    # Change the bank from which to load
    rom_file.seek(0x0df5)
    rom_file.write(b'\x1F')

    rom_file.seek(0x128d)
    rom_file.write(b'\x1F')

    # Change pointer table address ("gameplay")
    rom_file.seek(0x1297)
    rom_file.write(b'\x00\x45')

    # Change pointer table address ("non gameplay")
    rom_file.seek(0x129c)
    rom_file.write(b'\x00\x40')



    # Change cursor positions
    # ID 0x2A
    rom_file.seek(0x4000 * 0x6 + 0x2510)
    rom_file.write(b'\x48')
    rom_file.seek(0x4000 * 0x6 + 0x270F)
    rom_file.write(b'\x48')

    # Change clearing geometry (?)
    # ID 0x12
    rom_file.seek(0x4000 * 0xc + 0x3713)
    rom_file.write(b'\x09')
    rom_file.seek(0x4000 * 0xc + 0x3715)
    rom_file.write(b'\x08')

    # ID 0x1A
    rom_file.seek(0x338DE)
    rom_file.write(b'\x0a')
    rom_file.seek(0x338E0)
    rom_file.write(b'\xcf')

    # ID 0x2A
    rom_file.seek(0x4000 * 0xc + 0x3ADE)
    rom_file.write(b'\x0c')


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

    elif arguments['apply_windows']:

        rom = open(arguments["<romfile>"], 'rb+')
        insert_windows_code(rom)
        rom.close()

    elif arguments['apply_enemies']:
        rom = open(arguments["<romfile>"], 'rb+')
        insert_enemies_code(rom)
        rom.close()
