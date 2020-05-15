

def load_pointers_into_HL(pointer_addr, reg_e):
    reg_d = 1
    reg_e = reg_e << 1

    offset = (reg_d << 8) + reg_e
    address = pointer_addr + offset