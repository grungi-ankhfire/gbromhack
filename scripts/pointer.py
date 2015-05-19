#!/usr/bin/python

import sys

if (len(sys.argv) < 2):
    print('ERROR: Please provide an offset to calculate a pointer to.')
    exit()

pointer = sys.argv[1]
pointer = "0x" + pointer[-4:]
pointer = int(pointer, base=16)

if (pointer >= 0x0000 and pointer <= 0x3FFF):
    pointer += 0x4000
elif(pointer >= 0x8000 and pointer <= 0xBFFF):
    pointer -= 0x4000
elif(pointer >= 0xC000 and pointer <= 0xFFFF):
    pointer -= 0x8000

pointer_str = hex(pointer)
pointer_little_endian = "0x" + pointer_str[4:6] + pointer_str[2:4]

pointer = int(pointer_little_endian, base=16)

print('The pointer is: %s' % hex(pointer))
