#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_map.py read <romfile> <index>

Try and extract world map data.

Arguments
    <romfile>   The rom file to open
    <index>     The index of the map, 999 for whole bank

"""
from docopt import docopt
import os

rom = None

PALETTES_VALUES = {
    b'\x00': 'Jungle dungeon',
    b'\x01': 'Cave with tracks',
    b'\x02': 'Endgame tower',
    b'\x03': 'Town',
    b'\x04': 'Boat',
    b'\x05': 'City',
}


def load_pointer_into_HL(bank, hl, reg_e):
    offset = (1 << 8) + ((reg_e << 1) & 0xFF)
    rom.seek((bank - 1) * 0x4000 + hl + offset)
    pointer = int.from_bytes(rom.read(2), byteorder='little')
    return pointer


def seek_to_pointer(pointer, bank):
    rom.seek(pointer + (bank - 1) * 0x4000)


def read_bytes(n=1):
    return int.from_bytes(rom.read(n), byteorder='little')


def write_to_de(A):
    pass
    # print(format(A, '02x'))


def swap_byte(b):
    return (((b << 4) & 0xF0) | ((b >> 4) & 0x0F))


def read_map(thebytes):
    map_data = {}

    map_data['decoded'] = []

    c = 0
    counter = 0
    while counter < len(thebytes):

        byte_a = thebytes[counter]
        counter += 1
        added = ""

        b_counter = 8

        while b_counter > 0:

            new_a = (byte_a * 2) & 0xFF
            if byte_a * 2 > 0xFF:
                byte_a = new_a
                c += 1
            else:
                byte_a = new_a
                a = thebytes[counter]
                counter += 1
                if c & 0x01 == 0x00:
                    a = swap_byte(a)

                # --- jr_00d_413d
                a = a & 0x0F

                if b_counter == 8:
                    map_data['decoded'].append(a)
                else:
                # --- 0d:4146
                    previous_a = map_data['decoded'][-1]
                    a = swap_byte(previous_a) | a
                    map_data['decoded'][-1] = a
                    added += format(a, 'x') + " "

            b_counter -= 1
            print(added)

    print(map_data)
    return map_data


def Call_007_7a12():
        C586 = 0x2f

        E = C586 & 0x7f
        HL = 0x6d10
        HL = load_pointer_into_HL(0x07, HL, E)

        seek_to_pointer(HL, 0x07)
        E = read_bytes(1)
        D = read_bytes(1)

        FFB5 = read_bytes(1)
        FFB6 = read_bytes(1)

        A = read_bytes(1)
        A += 1

        if A == 0:
            pass
            # jr_007_7a55

        A = C586    # Again, normally read from [RAM at c586]
        C586 = (A & 0x80) | 0x7f

        # jr_007_7a36
        A = read_bytes(1)
        if A == 0xff:
            return

        C = A
        B = 0x00
        BC = A << 3

        pushed_HL = rom.tell()

        HL = BC + (FFB6 << 8) + FFB6
        print(hex(HL))
        seek_to_pointer(HL, 0x07)

        B = 0x01

# jr_007_7a55:
#         inc hl                                    ; $7a55: $23
#         ld a, [$c586]                             ; $7a56: $fa $86 $c5
#         and $80                                   ; $7a59: $e6 $80
#         ld [$c586], a                             ; $7a5b: $ea $86 $c5
#         ld b, [hl]                                ; $7a5e: $46
#         ld hl, $ffb5                              ; $7a5f: $21 $b5 $ff
#         ld a, [hl+]                               ; $7a62: $2a
#         ld h, [hl]                                ; $7a63: $66
#         ld l, a                                   ; $7a64: $6f

        # jr_007_7a65
        C = 0x08

        # jr_007_7a67
        A = C586
        A = A & 0x80

        if A != 0x00:
            pass
            # jr_007_7a75 This writes to VRAM, not important for us
        else:
            # Also write to VRAM ?
            pass


# jr_007_7a7c:
#         inc de                                    ; $7a7c: $13
#         di                                        ; $7a7d: $f3
#         rst $18                                   ; $7a7e: $df
#         ld a, [hl+]                               ; $7a7f: $2a
#         ld [de], a                                ; $7a80: $12
#         ei                                        ; $7a81: $fb
#         inc de                                    ; $7a82: $13
#         dec c                                     ; $7a83: $0d
#         jr nz, jr_007_7a67                        ; $7a84: $20 $e1

#         dec b                                     ; $7a86: $05
#         jr nz, jr_007_7a65                        ; $7a87: $20 $dc

#         ld a, [$c586]                             ; $7a89: $fa $86 $c5
#         and $7f                                   ; $7a8c: $e6 $7f
#         ret z                                     ; $7a8e: $c8

#         pop hl                                    ; $7a8f: $e1
#         jr jr_007_7a36                            ; $7a90: $18 $a4

#         xor a                                     ; $7a92: $af
#         ld [$ff00+$b1], a                         ; $7a93: $e0 $b1
#         ld [$ff00+$b2], a                         ; $7a95: $e0 $b2
#         ld [$ff00+$b3], a                         ; $7a97: $e0 $b3
#         ld de, $a6de                              ; $7a99: $11 $de $a6
#         ld hl, $6108                              ; $7a9c: $21 $08 $61
#         ld a, [hl+]                               ; $7a9f: $2a
#         ld [$ff00+$b4], a                         ; $7aa0: $e0 $b4
#         ld a, [hl+]                               ; $7aa2: $2a
#         ld c, a                                   ; $7aa3: $4f
#         ld a, [hl+]                               ; $7aa4: $2a
#         ld b, a                                   ; $7aa5: $47
#         dec bc                                    ; $7aa6: $0b
#         dec bc                                    ; $7aa7: $0b
#         dec bc                                    ; $7aa8: $0b



# def call_007_7e9f:

#     C1DF = 0x00
#     C2B1 = 0xb4
#     C2B2 = 0xb4
#     C299 = 0x65
#     C29A = 0xab
#     C29B = 0x0c
#     C29C = 0x05
#     C29D = 0xb63b

#     B = C2B1
#     A = C299

#     if B == A:
#         pass
#         # jr_007_7ef9
#     else:
#         C = C2B2
#         A = C29A
#         if C == A:
#             pass
#             # jr_007_7ef9
#         else:
#             A = C1DF
#             if A != 0:
#                 pass
#                 # jr_007_7efd
#             else:
#                 HL = C29D
#                 E = C29B
#                 HL += E

#                 A = C29C
#                 C = A + 1
#                 A = 

 
# Call_007_7e9f:
#         ld a, [$c2b1]                             ; $7e9f: $fa $b1 $c2
#         ld b, a                                   ; $7ea2: $47
#         ld a, [$c299]                             ; $7ea3: $fa $99 $c2
#         cp b                                      ; $7ea6: $b8
#         jr nc, jr_007_7ef9                        ; $7ea7: $30 $50

#         ld a, [$c2b2]                             ; $7ea9: $fa $b2 $c2
#         ld c, a                                   ; $7eac: $4f
#         ld a, [$c29a]                             ; $7ead: $fa $9a $c2
#         cp c                                      ; $7eb0: $b9
#         jr nc, jr_007_7ef9                        ; $7eb1: $30 $46

#         ld a, [$c1df]                             ; $7eb3: $fa $df $c1
#         and a                                     ; $7eb6: $a7
#         jr nz, jr_007_7efd                        ; $7eb7: $20 $44

#         ld hl, $c29d                              ; $7eb9: $21 $9d $c2
#         ld a, [hl+]                               ; $7ebc: $2a
#         ld h, [hl]                                ; $7ebd: $66
#         ld l, a                                   ; $7ebe: $6f
#         ld a, [$c29b]                             ; $7ebf: $fa $9b $c2
#         ld e, a                                   ; $7ec2: $5f
#         ld d, $00                                 ; $7ec3: $16 $00
#         add hl, de                                ; $7ec5: $19
#         ld a, [$c29c]                             ; $7ec6: $fa $9c $c2
#         inc a                                     ; $7ec9: $3c
#         ld c, a                                   ; $7eca: $4f
#         ld a, [hl]                                ; $7ecb: $7e

# jr_007_7ecc:
#         dec c                                     ; $7ecc: $0d
#         jr z, jr_007_7ed2                         ; $7ecd: $28 $03

#         add a                                     ; $7ecf: $87
#         jr jr_007_7ecc                            ; $7ed0: $18 $fa

# jr_007_7ed2:
#         add a                                     ; $7ed2: $87
#         jr c, jr_007_7ef9                         ; $7ed3: $38 $24

#         ld hl, $c29f                              ; $7ed5: $21 $9f $c2
#         ld a, [hl+]                               ; $7ed8: $2a
#         ld h, [hl]                                ; $7ed9: $66
#         ld l, a                                   ; $7eda: $6f
#         ld a, [hl+]                               ; $7edb: $2a
#         ld b, a                                   ; $7edc: $47
#         ld a, h                                   ; $7edd: $7c
#         ld [$c2a0], a                             ; $7ede: $ea $a0 $c2
#         ld a, l                                   ; $7ee1: $7d
#         ld [$c29f], a                             ; $7ee2: $ea $9f $c2
#         ld a, b                                   ; $7ee5: $78

# jr_007_7ee6:
#         ld [$ff00+$b6], a                         ; $7ee6: $e0 $b6
#         ld a, [$c299]                             ; $7ee8: $fa $99 $c2
#         ld b, a                                   ; $7eeb: $47
#         ld a, [$c29a]                             ; $7eec: $fa $9a $c2
#         ld c, a                                   ; $7eef: $4f
#         call $317a                                ; $7ef0: $cd $7a $31
#         call nz, $3196                            ; $7ef3: $c4 $96 $31
#         ld a, [$ff00+$b6]                         ; $7ef6: $f0 $b6
#         ret                                       ; $7ef8: $c9




def extract_world_map_data():

    # First time : B4 / AA, second time B4 / A5

    # B4 / AC | B4 / A7 | A8 / ... B2

    # B4
    # A5 A6 A7 A8 A9 AA

    C = 0xB4  # <-- Numbers of bytes to read
    A = 0xAE  # <-- Place to start reading, in a sense
    HL = None
    E = None

    result = []

    if C == A:
        HL = 0x4468
    else:
        E = A
        HL = 0x4300
        HL = load_pointer_into_HL(7, HL, E)

    while C != 0:
        seek_to_pointer(HL, 7)
        A = read_bytes(1)

        HL += 1

        bit7nonzero = (A >> 7) != 0

        if bit7nonzero:
            A = A & 0x7F
            seek_to_pointer(HL, 7)
            B = read_bytes(1)
            HL += 1

            write_to_de(A)
            result.append(A)
            C -= 1
            if C == 0:
                break

            B -= 1
            while B > 0:
                B -= 1
                write_to_de(A)
                result.append(A)
                C -= 1
                if C == 0:
                    break
        else:
            write_to_de(A)
            result.append(A)
            C -= 1

    return result


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    rom = open(arguments["<romfile>"], 'rb')
    index = int(arguments["<index>"])

    if arguments['read']:
        Call_007_7a12()
        # res = extract_world_map_data()
        # read_map(res)
