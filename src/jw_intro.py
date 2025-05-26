#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Script to translate the intro sequence of Jungle Wars
"""

from dataclasses import dataclass
import click
from translation_table import TranslationTable

@dataclass
class JWIntroLine:
    text: str
    location: int

# Config variables
text_start = 0x40020
lines = [
    JWIntroLine("ORIGINAL  WORK", text_start),
    JWIntroLine("KIMURA  HAJIME", text_start + 14),
    JWIntroLine("PRODUCTION", text_start + 28),
    JWIntroLine("ATELIER DOUBLE", text_start + 38),
]

@click.command
@click.argument("romfile")
@click.argument("tablefile")
def insert_intro(romfile, tablefile):
    print("Inserting intro...")
    table = TranslationTable(tablefile)
    with open(romfile, "rb+") as rom_file:
        for line in lines:
            print(f"    Inserting line at {hex(line.location)} : {line.text}")
            msg = table.convert_script(line.text)
            rom_file.seek(line.location)
            rom_file.write(msg)
            


if __name__ == "__main__":
    insert_intro()