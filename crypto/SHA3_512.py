import numpy as np

rate =  576
byte_rate=rate//8
capacity = 1024
l = 6
w = 2**l
b = 25*(2**l)  # b = state size (value of b = {25, 50, 100, 200, 400, 800, 1600} )
n_rounds = 12 + 2*l  # 24 rounds
byte_capacity = capacity // 8
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


def array_1Dto3D(state: bytearray):
    state3D = np.zeros((5,5,w))
    for i in range(0,5):
        for j in range(0,5):
            for k in range(0,w):
                # we take bit number (5i + j) × w + k
                n = (5*i + j) * w + k
                byte = state[n//8]
                #we make sure the value is 0*7 + bit
                bit = (byte >> (7 - (n%8))) & 1
                state3D[i][j][k]=bit

    return state3D


def array_3Dto1D(state3D):
    state = bytearray()
    bit_counter = 0
    byte = 0
    for i in range(0,5):
        for j in range(0,5):
            for k in range(0,w):
                #we add the bit to the current byte
                print("bit : ",int(state3D[i][j][k]) << 7-bit_counter)
                byte = byte + (int(state3D[i][j][k]) << 7-bit_counter)
                bit_counter+=1
                if (bit_counter == 8):
                    bit_counter=0
                    print(byte)
                    state.extend(bytes([byte]))
                    byte=0
    return state






def xor_state(state : bytearray, p : bytearray):
    for i in range (0,len(p)):
        state[i] = state[i] ^ p[i]
    return state

def _f(state : bytearray):
#    state3D = _1Dto3D(state)
#    for r in range(n_rounds):
#            state3D = iota(chi(pi(rho(theta(state3D)))), r)
#    state = _3Dto1D(state3D)
#    state = bytearray(state)
    return state

def Sha3_512(input: bytearray):
    #Padding
    input = pad(input)
    #Absorbing
    #break input into n consecutive r-bit pieces P0, ..., Pn−1
    n = len(input)// byte_rate
    #initialize the state S to a string of b zero bits
    state = bytearray(byte_rate+byte_capacity)
    print("State len:", len(state))

    for i in range(0,n):
        #absorb the input into the state: for each block Pi
        state = xor_state(state,input[byte_rate*i:byte_rate*(i+1)])
        #apply the block permutation f to the result, yielding a new state S
        state= _f(state)


    #Squeezing
    #initialize Z to be the empty string
    z = bytearray()
    d= output_len//8
    #while the length of Z is less than d
    while(len(z) < d) :
        z.extend(state[0:byte_rate])
        state = _f(state)

    #truncate Z to d bits
    z=z[0:d]

    return z

if __name__ == "__main__":
    #input = "1"
    #input_bytes = bytearray()
    #input_bytes.extend(map(ord, input))
    #print(input_bytes)
    #hash = Sha3_512(input_bytes)
    #print('hash : ',hash)

    test_state='A'*(1600//8)
    input_bytes = bytearray()
    input_bytes.extend(map(ord, test_state))
    state3D= array_1Dto3D(input_bytes)
    print(state3D)
    state = array_3Dto1D(state3D)
    print(state)



