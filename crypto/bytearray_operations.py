


# xors 2 bytearrays and returns a bytearray
def xor(x, y):
    return bytearray((x[i]) ^ (y[i]) for i in range(min(len(x), len(y))))

#returns a bytearray of any type of input
def to_bytearray(plaintext):
    if (type(plaintext) == str):
        plaintext = bytearray(plaintext, encoding="utf_8")
    else:
        plaintext = bytearray(plaintext)
    return plaintext