#!/usr/bin/python
"""Usage: rominfo.py <romfile>

Display information about GB roms.
The info is taken from the "PAN Doc" and other sources.

Arguments
    <romfile>   The rom file to open
"""
import click
from jw_config import config

    
def check_nintendo_logo(rom):
    nintendo_logo = 'CE ED 66 66 CC 0D 00 0B 03 73 00 83 00 0C 00 0D '\
                    '00 08 11 1F 88 89 00 0E DC CC 6E E6 DD DD D9 99 '\
                    'BB BB 67 63 6E 0E EC CC DD DC 99 9F BB B9 33 3E'
    nintendo_logo_bytes = bytearray.fromhex(nintendo_logo)

    rom.seek(0x104)
    nintendo_logo_rom = rom.read(48)
    if (nintendo_logo_bytes == nintendo_logo_rom):
        return 'Check'
    else:
        return 'ERROR'


def get_cartridge_name(rom):
    rom.seek(0x0134)
    name = rom.read(16)
    return (name.decode('ascii'))


def get_cartridge_type(rom):
    cartridge_types = {
        b'\x00': 'ROM Only',
        b'\x01': 'MBC1',
        b'\x02': 'MBC1+RAM',
        b'\x03': 'MBC1+RAM+BATTERY',
        b'\x05': 'MBC2',
        b'\x06': 'MBC2+BATTERY',
        b'\x08': 'ROM+RAM',
        b'\x09': 'ROM+RAM+BATTERY',
        b'\x0B': 'MMM01',
        b'\x0C': 'MMM01+RAM',
        b'\x0D': 'MMM01+RAM+BATTERY',
        b'\x0F': 'MBC3+TIMER+BATTERY',
        b'\x10': 'MBC3+TIMER+RAM+BATTERY',
        b'\x11': 'MBC3',
        b'\x12': 'MBC3+RAM',
        b'\x13': 'MBC3+RAM+BATTERY',
        b'\x19': 'MBC5',
        b'\x1A': 'MBC5+RAM',
        b'\x1B': 'MBC5+RAM+BATTERY',
        b'\x1C': 'MBC5+RUMBLE',
        b'\x1D': 'MBC5+RUMBLE+RAM',
        b'\x1E': 'MBC5+RUMBLE+RAM+BATTERY',
        b'\x20': 'MBC6+RAM+BATTERY',
        b'\x22': 'MBC7+RAM+BATTERY+ACCELEROMETER',
        b'\xFC': 'POCKET CAMERA',
        b'\xFD': 'BANDAI TAMA5',
        b'\xFE': 'HuC3',
        b'\xFF': 'HuC1+RAM+BATTERY',
    }
    rom.seek(0x0147)
    return (cartridge_types[rom.read(1)])


def get_rom_size(rom):
    rom_sizes = {
        b'\x00': ' 32KB (no ROM banking)',
        b'\x01': ' 64KB (4 banks)',
        b'\x02': '128KB (8 banks)',
        b'\x03': '256KB (16 banks)',
        b'\x04': '512KB (32 banks)',
        b'\x05': '  1MB (64 banks, only 63 used by MBC1)',
        b'\x06': '  2MB (128 banks, only 125 used by MBC1)',
        b'\x07': '  4MB (256 banks)',
        b'\x52': '1.1MB (72 banks)',
        b'\x53': '1.2MB (80 banks)',
        b'\x54': '1.5MB (96 banks)',
    }
    rom.seek(0x0148)
    return (rom_sizes[rom.read(1)])


def get_ram_size(rom):
    ram_sizes = {
        b'\x00': 'None',
        b'\x01': '2KB',
        b'\x02': '8KB',
        b'\x03': '32KB (4 banks of 8KB)',
    }
    rom.seek(0x0149)
    return (ram_sizes[rom.read(1)])


def get_destination_code(rom):
    destination_codes = {
        b'\x00': 'Japanese',
        b'\x01': 'Non-Japanese',
    }
    rom.seek(0x014A)
    return (destination_codes[rom.read(1)])


def header_checksum(rom):
    rom.seek(0x014D)
    header_rom_checksum = '%X' % int.from_bytes(rom.read(1), byteorder='big')

    rom.seek(0x0134)
    checksum = 0
    for _ in range(25):
        checksum = checksum - int.from_bytes(rom.read(1), byteorder='big') - 1
    header_computed_checksum = '%X' % (checksum & 0xff)
    if (header_rom_checksum == header_computed_checksum):
        header_checksum_result = 'Check'
    else:
        header_checksum_result = 'ERROR'
    return header_rom_checksum, header_computed_checksum, header_checksum_result


@click.command(context_settings={"show_default": True})
@click.argument("romfile", default=config["original_rom"])
def rominfo(romfile):
    with open(romfile, 'rb') as rom:

        print(f'Cartridge name ................ {get_cartridge_name(rom)}')
        print(f'Nintendo logo ................. {check_nintendo_logo(rom)}')
        print(f'Cartridge type ................ {get_cartridge_type(rom)}')
        print(f'ROM size ...................... {get_rom_size(rom)}')
        print(f'RAM size ...................... {get_ram_size(rom)}')
        print(f'Destination code .............. {get_destination_code(rom)}')

        header_rom_checksum, header_computed_checksum, header_checksum_result = header_checksum(rom)
        print(f'Header checksum (ROM) ......... {header_rom_checksum}')
        print(f'Header checksum (computed) .... {header_computed_checksum}')
        print(f'Header checksum result ........ {header_checksum_result}')


if __name__ == '__main__':
    rominfo()

