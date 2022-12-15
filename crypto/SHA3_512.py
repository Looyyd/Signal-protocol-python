import numpy as np
import binascii

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
        input.extend(b'\x61')
    #if need to append more than 1 block
    else:
        input.extend(b'\x60')
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
                #byte = state[n//8]
                byte = state[n//8]
                #we make sure the value is 0*7 + bit
                bit = (byte >> (7 - (n%8))) & 1
                state3D[i][j][k]=bit

    return state3D

def array_1Dto3D_internal(state: bytearray):
    state3D = np.zeros((5,5,w))
    for i in range(0,5):
        for j in range(0,5):
            for k in range(0,w):
                # we take bit number (5i + j) × w + k
                n = (i + 5*j) * w + k
                #byte = state[n//8]
                byte = state[n//8]
                #we make sure the value is 0*7 + bit
                bit = (byte >> (7 - (n%8))) & 1
                state3D[i][j][k]=bit

    return state3D

def theta(state3D):
    out_state3D= np.zeros((5,5,w))
    for i in range(0, 5):
        for j in range(0, 5):
            for k in range(0, w):
                bit = state3D[i][j][k]
                parity1 = sum(state3D[:,(j-1)%5,k])%2
                parity2 = sum(state3D[:,(j+1)%5,k-1])%2
                out_state3D[i][j][k]= (bit + parity1 + parity2) %2

    return out_state3D

def pi(state3D):
    out_state3D= np.zeros((5,5,w))
    for i in range(0, 5):
        for j in range(0, 5):
            out_state3D[(3*i + 2*j)%5,i,:] = state3D[i,j,:]

    return out_state3D

def chi(state3D):
    out_state3D= np.zeros((5,5,w))
    for i in range(0, 5):
        for j in range(0, 5):
            for k in range(0, w):
                x = int(state3D[i,j,k])
                not_y = int((state3D[i,(j+1)%5,k]+1)%2)
                z = int(state3D[i,(j+2)%5,k])
                out_state3D[i,j,k] = x ^(not_y & z)
    return out_state3D

# TODO , dtype = int) dans les array numpy, vour meme char

def rho(state3D):
    # TODO : could precalculate i and j
    out_state3D = np.zeros((5,5,64))
    # method taken from https://math.stackexchange.com/a/366274
    i = 0
    j = 1
    for k in range(0,64):
        out_state3D[0][0][k] = state3D[0][0][k]
    for t in range(0,24):
        for k in range(0,64):
            out_state3D[i][j][k] = state3D[i][j][(k-((t+1)*(t+2))//2)%64]
        i_prev = i
        j_prev = j
        i= (3*i_prev + 2*j_prev)%5
        j=i_prev
    return out_state3D

# linear shift register
def rc(t):
    if t%255 == 0:
        return 1
    else:
        R=[1,0,0,0,0,0,0,0]
        for i in range(0,t%255):
            R.insert(0,0)
            R[0]=(R[0]+R[8]) % 2
            R[4]=(R[4]+R[8]) % 2
            R[5]=(R[5]+R[8]) % 2
            R[6]=(R[6]+R[8]) % 2
            R= R[0:8]
        return R[0]


def iota(state3D, n_round):
    out_state3D = np.array(state3D)
    RC=np.zeros(w)
    # l+1 because it's l included
    for m in range(0,l+1):
        out_state3D[0][0][2**m -1] = (out_state3D[0][0][2**m -1] + rc(m+7*n_round)) %2
#    for m in range(0, l):
#        RC[2**m -1]=rc(m+7*n_round)
#    for z in range(0,w):
#        out_state3D[0][0][z]=(state3D[0][0][z] + RC[z]) %2
    return out_state3D



def array_3Dto1D(state3D):
    state = bytearray()
    bit_counter = 0
    byte = 0
    for i in range(0,5):
        for j in range(0,5):
            for k in range(0,w):
                #we add the bit to the current byte
                # TODO is that the right order? isn't j before i?
                byte = byte + (int(state3D[i][j][k]) << 7-bit_counter)
                bit_counter+=1
                if (bit_counter == 8):
                    bit_counter=0
                    state.extend(bytes([byte]))
                    byte=0
    return state






def xor_state(state : bytearray, p : bytearray):
    for i in range (0,len(p)):
        state[i] = state[i] ^ p[i]
    return state

def array_3Dto1D_final(state3D):
    out_state = bytearray()
    bit_c = 0
    word_c = 0
    n =0
    for i in state3D:
        for j in i:
            for k in j:
                # we take bit number (5i + j) × w + k, when creating
                #                     factor
                k_n = bit_c % w
                factor = ((bit_c - k_n) // w)
                j_n = factor%5
                i_n = (factor - j_n) // 5

                # chinoiserie avec les bits car c'est en big endian dans le doc du NIST
                n = n//2 + state3D[i_n][j_n][k_n]*2**7
                bit_c= bit_c+1
                if(bit_c%8==0):
                    out_state.append(int(n))
                    n=0
    return out_state

def print3D(m, state3D):
    print(m)
    bit_c = 0
    word_c = 0
    n =0
    for i in state3D:
        for j in i:
            for k in j:
                # we take bit number (5i + j) × w + k, when creating
                #                     factor
                k_n = bit_c % w
                factor = ((bit_c - k_n) // w)
                j_n = factor%5
                i_n = (factor - j_n) // 5

                # chinoiserie avec les bits car c'est en big endian dans le doc du NIST
                n = n//2 + state3D[i_n][j_n][k_n]*2**7
                bit_c= bit_c+1
#                if(bit_c%4==0):
#                    print(f'{int(n):1x}', end='')
#                    n=0
                if(bit_c%8==0):
                    #byte =int.from_bytes(int(n).to_bytes(1,'big'),'little')
                    #print(f'{byte:02x}', end='')
                    print(f'{int(n):02x}', end='')
                    n=0
                    print(' ', end='')
                    word_c = word_c +1
                    if(word_c%16==0):
                        print("")
    print("\n")


def _f(state : bytearray, iteration :int):
    #if iteration first iteration then have to convert it to NIST format
    state3D = array_1Dto3D(state)
    for r in range(n_rounds):
            #print("Round : ", r)
            #print3D("Before theta:", state3D)
            state3D = theta(state3D)
            #print3D("After theta :",state3D)
            state3D = rho(state3D)
            #print3D("After rho :",state3D)
            state3D = pi(state3D)
            #print3D("After pi :",state3D)
            state3D = chi(state3D)
            #print3D("After chi :",state3D)
            state3D = iota(state3D, r)
            #print3D("After iota :",state3D)
    #print3D("Last 3D state", state3D)
    state = array_3Dto1D(state3D)
    #print("3D to 1D state", state)
    state = bytearray(state)
    return state

def Sha3_512(input: bytearray):
    # appending a two-bit suffix to M
    # normalement il faut ajouter que 2 bit
    # SHA3-512(M) = KECCAK[1024] (M || 01, 512).
    # j'inclu ca dans le padding, car on fait que des multiples de 8 bits:
    #input.extend(b'\x06')
    #Padding
    # KECCAK[c] = SPONGE[KECCAK-p[1600, 24], pad10*1, 1600 – c].
    #print("input =", input)
    input = pad(input)
    #print("Data to be absorbed")
    #print(input)
    #Absorbing
    #break input into n consecutive r-bit pieces P0, ..., Pn−1
    n = len(input)// byte_rate
    #initialize the state S to a string of b zero bits
    state = bytearray(byte_rate+byte_capacity)

    for i in range(0,n):
        #absorb the input into the state: for each block Pi
        #print("state: ", state)
        state = xor_state(state,input[byte_rate*i:byte_rate*(i+1)])
        #print("xored state: ", state)
        #apply the block permutation f to the result, yielding a new state S
        state= _f(state,i)


    #print("STARTED SQUEEZING")
    #print("State =", state)

    #Squeezing
    #initialize Z to be the empty string
    z = bytearray()
    d= output_len//8
    #the final hash in in little endian like in NIST doc
    state_to_squeeze=array_3Dto1D_final(array_1Dto3D(state))
    #while the length of Z is less than d
    while(len(z) < d) :
        z.extend(state_to_squeeze[0:byte_rate])
        state = _f(state,1)
        #the final hash in in little endian like in NIST doc
        state_to_squeeze=array_3Dto1D_final(array_1Dto3D(state))


    #truncate Z to d bits
    z=z[0:d]

    return z

if __name__ == "__main__":
    # https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Standards-and-Guidelines/documents/examples/SHA3-512_Msg0.pdf
    input = ""
    input_bytes = bytearray()
    input_bytes.extend(map(ord, input))
    print(input_bytes)
    hash = Sha3_512(input_bytes)
    print('hash : ', binascii.hexlify(hash))



    # TEST  1600-bit message
    # https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Standards-and-Guidelines/documents/examples/SHA3-512_1600.pdf

    input="\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5\xc5"
    input_bytes = bytearray()
    input_bytes.extend(map(ord, input))
    print(input_bytes)
    hash = Sha3_512(input_bytes)
    print('hash : ', binascii.hexlify(hash))


#    test_state='A'*(1600//8)
#    input_bytes = bytearray()
#    input_bytes.extend(map(ord, test_state))
#    state3D= array_1Dto3D(input_bytes)
#    state3D = theta(state3D)
#    state3D = pi(state3D)
#    state3D = chi(state3D)
#    state3D = rho(state3D)
#    state3D = iota(state3D, 0)


