# -*- coding: utf-8 -*-
"""translation_table.py - Module handling .tbl files

    .tbl (Table) files are used to translate hex-encoded values into text and other informations.
    This module takes bytes and bytearrays and outputs clear text.
    The module will strive to support the standard format outlined here :
    http://transcorp.romhacking.net/scratchpad/Table%20File%20Format.txt
"""


class TranslationTable(object):

    table = {}

    def __init__(self, filename):
        f = open(filename, 'r')
        for line in f:
            tokens = line.split('=')
            self.table[int(tokens[0], base=16)] = tokens[1].rstrip('\n')
        f.close()

    def convert_byte(self, b):
        if b in self.table:
            return self.table[b]
        else:
            return str(b)

    def convert_bytearray(self, ba):
        result = ""
        for b in ba:
            result += self.convert_byte(b)
        return result
