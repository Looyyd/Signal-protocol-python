import numpy as np

rate =  576
byte_rate=rate//8
capacity = 1024
l = 6
#w = 2**l
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


# 1600 bits(1 dimensional array) to 3 dimensional array of 5x5x64
def _1Dto3D(A):
    A_out = np.zeros((5, 5, 64), dtype = int) # Initialize empty 5x5x64 array
    for i in range(5):
        for j in range(5):
            for k in range(64):
                A_out[i][j][k] = A[64*(5*j + i) + k]
    return A_out


def theta(A):
        A_out = np.zeros((5,5,64), dtype = int)  # Initialize empty 5x5x64 array
       #A_out = [[[0 for _ in range(64)] for _ in range(5)] for _ in range(5)] #without numpy
        for i in range(5):
                for j in range(5):
                        for k in range(64):
                            C=sum([A[(i-1)%5][ji][k] for ji in range(5)]) % 2 # XOR=mod2 5 bit column "to the left" of the original bit
                            D=sum([A[((i+1) % 5)][ji][(k-1)%64] for ji in range(5)]) % 2 #XOR=mod2 5 bit column "to the right"  and one position "to the front" of the original bit
                            temp=C+D+A[i][j][k] % 2 #XORing original bit with A and B
                            A_out[i][j][k]=temp
        return A_out

#Rho : Each word is rotated by a fixed number of position according to table.
def rho(A):
    rhomatrix=[[0,36,3,41,18],[1,44,10,45,2],[62,6,43,15,61],[28,55,25,21,56],[27,20,39,8,14]]
    rhom = np.array(rhomatrix, dtype=int)  # Initialize empty 5x5x64 array
    A_out = np.zeros((5,5,64), dtype = int)
    for i in range(5):
        for j in range(5):
            for k in range(64):
                A_out[i][j][k] = A[i][j][k - rhom[i][j]] #  A[i][j][k − (t + 1)(t + 2)/2] so here rhom[i][j] Use lookup table to "calculate" (t + 1)(t + 2)/2
    return A_out

#Pi: Permutate the 64 bit words
def pi(A):
    A_out = np.zeros((5,5,64), dtype = int) # Initialize empty 5x5x64 array
    for i in range(5):
        for j in range(5):
            for k in range(64):
                A_out[j][(2*i+3*j)%5][k] = A[i][j][k]
    return A_out

# A_out [i][j][k] = A[i][j][k] XOR ( (A[i + 1][j][k] XOR 1) AND (ain[i + 2][j][k]) )
def chi(A):
    A_out = np.zeros((5,5,64), dtype = int) # Initialize empty 5x5x64 array
    for i in range(5):
        for j in range(5):
            for k in range(64):
                A_out = (A[i][j][k]+(((A[(i + 1)%5][j][k] + 1 )% 2) * (A[(i + 2)%5][j][k]))) % 2
    return A_out

#iota: add constants  to word (0,0)
# aout[i][j][k] = ain[i][j][k] ⊕ bit[i][j][k]
# for 0 ≤ ℓ ≤ 6, we have bit[0][0][2ℓ − 1] = rc[ℓ + 7ir]
def iota(A, round):
    # Initialize empty arrays
    A_out = A.copy()
    bit = np.zeros((5,5,64), dtype=int)
    rc = np.zeros((168), dtype=int)

    #generation of rc as Linear Feedback Shift Register
    w = np.array([1,0,0,0,0,0,0,0], dtype = int)
    rc[0] = w[0]
    for i in range(1, 168): #7*24
        w = [w[1],w[2],w[3],w[4],w[5],w[6],w[7], (w[0]+w[4]+w[5]+w[6]) % 2]
        rc[i] = w[0]

    # Calculate A_out
    for l in range(7):
        A_out[0][0][2**l - 1] ^=rc[l + 7*round]

# 5x5x64 (three-dimensional array) into 1600 bits(one-dimensional array)
def _3Dto1D(A):
    A_out = np.zeros(1600, dtype = int) # Initialize empty array of size 1600
    for i in range(5):
        for j in range(5):
            for k in range(64):
                A_out[64*(5*j+i)+k] = A[i][j][k]
    return A_out


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
    input = "1"
    input_bytes = bytearray()
    input_bytes.extend(map(ord, input))
    print(input_bytes)
    hash = Sha3_512(input_bytes)
    print('hash : ',hash)