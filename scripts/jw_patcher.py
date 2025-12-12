#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_patcher.py create <romfile> <start> <end> <outputfile>
          jw_patcher.py apply <patchfile> <romfile> <start>
          jw_patcher.py create --font <romfile> <outputfile>
          jw_patcher.py apply --font <patchfile> <romfile>
          jw_patcher.py apply_windows <romfile>
          jw_patcher.py apply_enemies <romfile>
          jw_patcher.py apply_npcs <romfile>

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
from jw_memorymap import FONT_DATA_START, FONT_DATA_END

# python jw_patcher.py create roms\jw_patched.gb 0x1EF0B 0x1EFC5 patches\overworld_font.patch


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


def insert_windows_moved_routine(rom_file):

    # Change bank
    rom_file.seek(0x142f)
    rom_file.write(b'\x1f')

    # Change routine adress
    rom_file.seek(0x1432)
    rom_file.write(b'\x00\x47')


def insert_enemy_name_loading_redirection_code(rom_file):
    # The original routine at 0x0F95 runs from fixed bank but is typically
    # called from banked code (e.g., battle engine). If we change banks and
    # don't restore them, returning to banked code will crash immediately.
    #
    # Fix: trampoline that saves current bank (HRAM $FFA5), switches to bank
    # $1F to run a helper at $4100, then restores the previous bank and jumps
    # back to the original continuation at $0FA4.
    rom_file.seek(0x0F95)
    rom_file.write(
        b'\xF0\xA5'         # ldh a, [$FFA5]
        b'\x47'             # ld b, a
        b'\x3E\x1F'         # ld a, $1F
        b'\xC7'             # rst $00 (switch bank)
        b'\xCD\x00\x41'     # call $4100
        b'\x78'             # ld a, b
        b'\xC7'             # rst $00 (restore bank)
        b'\xC3\xA4\x0F'     # jp $0FA4
        b'\x00'             # nop (pad to overwrite full original block)
    )

    # Bank $1F helper routine at $4100 (file offset 0x7C100).
    # Replays the original bytes we overwrote (increment $C59B, load E from [HL],
    # then set HL=$4000 and call $3A71), then returns to fixed bank trampoline.
    rom_file.seek(0x1F * 0x4000 + 0x100)
    rom_file.write(
        b'\xFA\x9B\xC5'     # ld a, [$c59b]
        b'\x3C'             # inc a
        b'\xEA\x9B\xC5'     # ld [$c59b], a
        b'\x7E'             # ld a, [hl]
        b'\x5F'             # ld e, a
        b'\x21\x00\x40'     # ld hl, $4000
        b'\xCD\x71\x3A'     # call $3A71
        b'\xC9'             # ret
    )


def insert_npc_name_reading_code(rom_file):
    rom_file.seek((0x0D - 1) * 0x4000 + 0x72FB)
    rom_file.write(b'\x3E\x1C')     # ld a, $0D
    rom_file.write(b'\xC7')         # rst $00

    rom_file.seek((0x1C - 1) * 0x4000 + 0x72FE)
    rom_file.write(b'\x18\x01')     # jr $7301
    rom_file.write(b'\xC7')         # rst $00
    rom_file.write(b'\x0A')         # ld a, [bc]
    rom_file.write(b'\x03')         # inc bc
    rom_file.write(b'\x22')         # ldi [hl], a
    rom_file.write(b'\x3C')         # inc a
    rom_file.write(b'\x20\xFA')     # jr nz, $7301
    rom_file.write(b'\x3E\x0D')     # ld a, $0D
    rom_file.write(b'\x18\xF5')     # jr $7300

if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    if arguments['create']:
        offset = 0x00
        end_offset = 0x00

        if arguments['--font']:
            offset = FONT_DATA_START
            end_offset = FONT_DATA_END
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
            offset = FONT_DATA_START
        else:
            offset = int(arguments['<start>'], base=16)

        patch_path = arguments['<patchfile>']

        rom = open(arguments["<romfile>"], 'rb+')
        apply_patch(rom, patch_path, offset)
        rom.close()

    elif arguments['apply_windows']:

        rom = open(arguments["<romfile>"], 'rb+')
        insert_windows_code(rom)
        insert_windows_moved_routine(rom)
        rom.close()

    elif arguments['apply_enemies']:
        rom = open(arguments["<romfile>"], 'rb+')
        insert_enemy_name_loading_redirection_code(rom)
        rom.close()

    elif arguments['apply_npcs']:
        rom = open(arguments["<romfile>"], 'rb+')
        insert_npc_name_reading_code(rom)
        rom.close()
