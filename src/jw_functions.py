def function1():

    a = 0
    hl = 0
    de = 0x90
    bc = 0x00

    while bc != 0:
        carry = bc & 0x01
        bc = bc >> 1

        if carry:
            hl += de

        de = de << 1

    print("hl : " + hex(hl))
    print("de : " + hex(de))


def Call_000_3a51():
    a = 0
    c = 0x03
    b = 0x04

    while c != 0:

        carry = c & 0x01
        c = c >> 1
        if carry:
            a += b

        b = b << 1

    print("a : " + hex(a))
    print("b : " + hex(b))
    print("c : " + hex(c))



def RST_28():
    a = 0x0
    l = 0x01
    h = 0xc4

    a += l
    l = a
    a = h
    


Call_000_3a51()


