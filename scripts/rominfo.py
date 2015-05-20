#!/usr/bin/python
"""Usage: rominfo.py <romfile>

Display information about GB roms.
The info is taken from the "PAN Doc".

Arguments
    <romfile>   The rom file to open
"""
from math import floor
from docopt import docopt

rom = None


def check_nintendo_logo():
    nintendo_logo = "CE ED 66 66 CC 0D 00 0B 03 73 00 83 00 0C 00 0D "\
                    "00 08 11 1F 88 89 00 0E DC CC 6E E6 DD DD D9 99 "\
                    "BB BB 67 63 6E 0E EC CC DD DC 99 9F BB B9 33 3E"
    nintendo_logo_bytes = bytes.fromhex(nintendo_logo)    

    rom.seek(0x104)
    nintendo_logo_rom = rom.read(48)
    if (nintendo_logo_bytes == nintendo_logo_rom):
        return "Check"
    else:
        return "ERROR"


def get_cartridge_name():
    rom.seek(0x0134)
    name = rom.read(16)
    return(str(name, 'ascii'))


def get_cartridge_type():
    cartridge_types = {
        b'\x00': "ROM Only",                b'\x13': "MBC3+RAM+BATTERY",
        b'\x01': "MBC1",                    b'\x15': "MBC4",
        b'\x02': "MBC1+RAM",                b'\x16': "MBC4+RAM",
        b'\x03': "MBC1+RAM+BATTERY",        b'\x17': "MBC4+RAM+BATTERY",
        b'\x05': "MBC2",                    b'\x19': "MBC5",
        b'\x06': "MBC2+BATTERY",            b'\x1A': "MBC5+RAM",
        b'\x08': "ROM+RAM",                 b'\x1B': "MBC5+RAM+BATTERY",
        b'\x09': "ROM+RAM+BATTERY",         b'\x1C': "MBC5+RUMBLE",
        b'\x0B': "MMM01",                   b'\x1D': "MBC5+RUMBLE+RAM",
        b'\x0C': "MMM01+RAM",               b'\x1E': "MBC5+RUMBLE+RAM+BATTERY",
        b'\x0D': "MMM01+RAM+BATTERY",       b'\xFC': "POCKET CAMERA",
        b'\x0F': "MBC3+TIMER+BATTERY",      b'\xFD': "BANDAI TAMA5",
        b'\x10': "MBC3+TIMER+RAM+BATTERY",  b'\xFE': "HuC3",
        b'\x11': "MBC3",                    b'\xFF': "HuC1+RAM+BATTERY",
        b'\x12': "MBC3+RAM",
    }
    rom.seek(0x0147)
    return(cartridge_types[rom.read(1)])


def get_rom_size():
    rom_sizes = {
        b'\x00': " 32KB (no ROM banking)",
        b'\x01': " 64KB (4 banks)", 
        b'\x02': "128KB (8 banks)",
        b'\x03': "256KB (16 banks)",
        b'\x04': "512KB (32 banks)",
        b'\x05': "  1MB (64 banks, only 63 used by MBC1)",
        b'\x06': "  2MB (128 banks, only 125 used by MBC1)",
        b'\x07': "  4MB (256 banks)",
        b'\x52': "1.1MB (72 banks)",
        b'\x53': "1.2MB (80 banks)",
        b'\x54': "1.5MB (96 banks)",
    }
    rom.seek(0x0148)
    return(rom_sizes[rom.read(1)])    


def get_ram_size():
    ram_sizes = {
        b'\x00': "None",
        b'\x01': "2KB", 
        b'\x02': "8KB",
        b'\x03': "32KB (4 banks of 8KB)",
    }
    rom.seek(0x0149)
    return(ram_sizes[rom.read(1)])


def get_destination_code():
    destination_codes = {
        b'\x00': 'Japanese',
        b'\x01': 'Non-Japanese',
    }
    rom.seek(0x014A)
    return(destination_codes[rom.read(1)])


def header_checksum():
    rom.seek(0x014D)
    header_rom_checksum = '%X' % int.from_bytes(rom.read(1), byteorder="little")

    rom.seek(0x0134)
    checksum = 0
    for b in range(25):
        checksum = checksum - int.from_bytes(rom.read(1), byteorder="little") - 1
    header_computed_checksum = "%X"%(checksum&0xff)
    if(header_rom_checksum == header_computed_checksum):
        header_checksum_result = "Check"
    else:
        header_checksum_result = "ERROR"
    return header_rom_checksum, header_computed_checksum, header_checksum_result

if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    rom = open(arguments["<romfile>"], 'rb')
    
    print('Cartridge name ................ %s' % get_cartridge_name())
    print('Nintendo logo ................. %s' % check_nintendo_logo())
    print('Cartridge type ................ %s' % get_cartridge_type())
    print('ROM size ...................... %s' % get_rom_size())
    print('RAM size ...................... %s' % get_ram_size())
    print('Destination code .............. %s' % get_destination_code())
    header_rom_checksum, header_computed_checksum, header_checksum_result = header_checksum()
    print('Header checksum (ROM) ......... %s' % header_rom_checksum)
    print('Header checksum (computed) .... %s' % header_computed_checksum)
    print('Header checksum result ........ %s' % header_checksum_result)
