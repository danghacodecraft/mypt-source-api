import binascii

def string_to_int_representation(str):
    utf8_str = str.encode("utf-8")
    b = binascii.hexlify(utf8_str)
    i = int(b, 16)
    
    return i