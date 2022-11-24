

rate =  576
byte_rate=rate//8
capacity = 1024
output_len = 512


def pad(input: bytearray):
    # To ensure the message can be evenly divided into r-bit blocks, padding is required. SHA-3 uses the pattern 10*1
    # in its padding function: a 1 bit, followed by zero or more 0 bits (maximum r − 1) and a final 1 bit.

    # !!! We suppose that input is multiple of 8 bits(so only whole bytes)
    length = len(input)
    modulo= length%(rate//8)
    pad_length = (rate//8)-modulo

    #pad_length between 1 and rate/8
    if pad_length==1:
        #we append only 1 block
        input.extend(b'\x81')
    #if need to append more than 1 block
    else:
        input.extend(b'\x80')
        for i in range(0, pad_length-2):
            input.extend(b'\x00')
        input.extend(b'\x01')
    return input



def Sha3_512(input: bytearray):
    #Padding
    input = pad(input)
    hash= input
    #Absorbing

    #Squeezing
    return hash

if __name__ == "__main__":
    input = "A"*71
    input_bytes = bytearray()
    input_bytes.extend(map(ord, input))
    print(input_bytes)
    hash = Sha3_512(input_bytes)
    print('len hash:', len(hash))
    print(len(hash)%byte_rate)
    print('hash : ',hash)