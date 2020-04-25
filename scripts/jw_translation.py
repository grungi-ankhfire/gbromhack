#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_translation.py <romfile> [<tablefile>]

Helping script for manipulating Jungle Wars text.

Arguments
    <romfile>    The rom file to open
    <start>      The offset in hex to start the dump
    <end>        The offset in hex to finish the dump
    <tablefile>  Translation table to use
    <scriptfile> File containing a Unicode script
    <outputfile> File in which to dump the script
"""
from docopt import docopt
from translation_table import TranslationTable


MAX_LENGTH = 17


class TextString:

    def __init__(self, pointer_address, text, original_text=""):

        self.pointer_address = pointer_address
        self.text = text
        self.new_bank = None
        self.new_pointer = None
        self.binary_text = None
        self.length = 0
        self.original_text = original_text

    def prepare(self):
        words = self.text.split()
        cur_line_length = 0
        prepared_text = ""
        self.length = 0
        line_num = 0
        for word in words:
            if len(word) + cur_line_length + 1 >= MAX_LENGTH:
                if line_num % 2 == 0:
                    prepared_text += "<FE>"
                else:
                    prepared_text += "<FD>"
                line_num += 1
                self.length += 1
                cur_line_length = 0

            prepared_text += word
            cur_line_length += len(word)
            if(word != words[-1]):
                cur_line_length += 1
                prepared_text += " "
                self.length += 1
            self.length += len(word)

        prepared_text += "<FF>"
        self.length += 1
        return prepared_text


rom = None
table = None

if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    if (arguments['<tablefile>']):
        table = TranslationTable(arguments['<tablefile>'])

    rom = open(arguments["<romfile>"], 'rb+')

    messages = [
        #TextString(0x26C35, '''Aa Bb Cc Dd Ee Ff Gg Hh Ii Jj Kk Ll Mm Nn Oo Pp Qq Rr Ss Tt Uu Vv Ww Xx Yy Zz , . ' " ? !''' )
        TextString(0x1A581, "A morning in the Jungle.<FC>", "ジャングルの あさが きました.<FC>"),
        TextString(0xD90A, "Jungle Dad 「Good morning <var0>!", "ジャングルパパ<FE>「おはよう! <var0>.<FF>"),
        TextString(0xD910, "「Hey hey why do you not at least put on some pants?<FD>「They are in that box check it out!", "「こらこら パンツぐらい<FE> はいて きなさい.<FD>「その ハコの なかに あるから<FE> しらべて ごらん.<FF>"),
        TextString(0xD919, "「Even if you grabbed a pair of pants you cannot just hold on to them you know?<FD>「You also have to wear them!", "「パンツを とってきても<FE> もってるだけじゃ ダメじゃないか.<FD>「そうびして みに つけなくちゃね.<FF>"),
        TextString(0xD922, "「Alright. Then let us walk around the jungle this morning!<FD>「It seems there are bad guys running around. I have got to keep my eyes open and watch out for them.")
    ]

    message_index = 0
    total_length = 0

    for m in messages:
        m.binary_text = table.convert_script(m.prepare())

        m.new_bank = b'\x11'
        m.new_pointer = total_length.to_bytes(2, "little")
        total_length += m.length
        rom.seek(m.pointer_address)
        print("Pointer address : " + str(hex(m.pointer_address)))
        rom.write((message_index * 3).to_bytes(2, "little"))
        print(str((message_index * 3).to_bytes(2, "little")))

        rom.seek(0x10 * 0x4000 + 0x1000 + message_index * 0x03)
        rom.write(m.new_bank)
        rom.write(m.new_pointer)

        rom.seek(int.from_bytes(m.new_bank, "little") * 0x4000 + int.from_bytes(m.new_pointer, "little"))
        rom.write(m.binary_text)
        message_index += 1

    rom.close()
# Need:
#   The old pointer adress (where the pointer is in the ROM)
#   The new script
#  
# Insert the  
# Write new pointer in rom in place of the old one
#