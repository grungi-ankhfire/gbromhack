# -*- coding: utf-8 -*-
"""translation_table.py - Module handling .tbl files

    .tbl (Table) files are used to translate hex-encoded values into text and other informations.
    This module takes bytes and bytearrays and outputs clear text.
    The module will strive to support the standard format outlined here :
    http://transcorp.romhacking.net/scratchpad/Table%20File%20Format.txt
"""

class TranslationTableEntry:

    def __init__(self, hex_value, text):
        self.hex_value = hex_value
        self.text = text


class TranslationTableV2:

    def __init__(self, filename):
        self.entries = []
        
        with open(filename, 'r', encoding="utf8") as f:
        
            for line in f:
                tokens = line.split('=')
                hex_value = int(tokens[0], base=16)
                symbol = tokens[1].rstrip('\n')
                self.table.entries.append(TranslationTableEntry(hex_value, symbol))

    


class TranslationTable(object):

    def __init__(self, filename):
        self.table = {}
        self.inverse_table = {}

        with open(filename, 'r', encoding="utf8") as f:
        
            for line in f:
                tokens = line.split('=')
                hexcode = int(tokens[0], base=16)
                symbol = tokens[1].rstrip('\n')
                self.table[hexcode] = symbol
                self.inverse_table[symbol] = hexcode

    def convert_byte(self, b):
        if b in self.table:
            print(f"{hex(b)} gives {self.table[b]}")
            return self.table[b]
        else:
            return str(b)

    def convert_bytearray(self, ba):
        result = ""
        for b in ba:
            result += self.convert_byte(b)
        return result

    def convert_script(self, script):
        result = b''
        token = ''
        for character in script:
            token += character
            if token in self.inverse_table:
                result += bytes([self.inverse_table[token]])
                token = ''
        return result
