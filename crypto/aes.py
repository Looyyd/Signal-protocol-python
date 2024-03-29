import numpy as np

AES_BLOCK_SIZE = 128
AES_BLOCK_SIZE_BYTES = AES_BLOCK_SIZE//8
AES_KEY_SIZE = 256
AES_KEY_SIZE_BYTES = AES_KEY_SIZE // 8

keysize= 256
bloc_size = 128
n_rounds = 14
N = 8
R = 15

# taken from https://gist.github.com/bonsaiviking/5571001
Sbox = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
)
Sbox_inv = (
    0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
    0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB,
    0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E,
    0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25,
    0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92,
    0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84,
    0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06,
    0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B,
    0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73,
    0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E,
    0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B,
    0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4,
    0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F,
    0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF,
    0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D
)

Rcon = (0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a)


def shift_rows(state):
    out_state = np.zeros((4, 4), dtype=int)
    # state is 4 by 4 array of bytes
    # iterate rows
    for i in range(4):
        #iterate columns
        for j in range(4):
            out_state[i][j]= state[i][(j+i)%4]
    return out_state


def inv_shift_rows(state):
    out_state = np.zeros((4, 4), dtype=int)
    # state is 4 by 4 array of bytes
    # iterate rows
    for i in range(4):
        #iterate columns
        for j in range(4):
            out_state[i][j]= state[i][(j-i)%4]
    return out_state

def multiply_by_2(v):
    s = v << 1
    s &= 0xff
    if (v & 128) != 0:
        s = s ^ 0x1b
    return s


def multiply_by_3(v):
    return multiply_by_2(v) ^ v


def mix_columns(grid):
    new_grid = [[], [], [], []]
    for i in range(4):
        col = [grid[j][i] for j in range(4)]
        col = mix_column(col)
        for i in range(4):
            new_grid[i].append(col[i])
    return new_grid


# taken from https://medium.com/wearesinch/building-aes-128-from-the-ground-up-with-python-8122af44ebf9
def mix_column(column):
    r = [
        multiply_by_2(column[0]) ^ multiply_by_3(
            column[1]) ^ column[2] ^ column[3],
        multiply_by_2(column[1]) ^ multiply_by_3(
            column[2]) ^ column[3] ^ column[0],
        multiply_by_2(column[2]) ^ multiply_by_3(
            column[3]) ^ column[0] ^ column[1],
        multiply_by_2(column[3]) ^ multiply_by_3(
            column[0]) ^ column[1] ^ column[2],
    ]
    return r

def inv_mix_columns(state):
    return mix_columns((mix_columns((mix_columns(state)))))


def sub_bytes(state):
    out_state = np.zeros((4, 4), dtype=int)
    # state is 4 by 4 array of bytes
    for i in range(4):
        for j in range(4):
            out_state[i][j]= Sbox[state[i][j]]
    return out_state


def inv_sub_bytes(state):
    out_state = np.zeros((4, 4), dtype=int)
    # state is 4 by 4 array of bytes
    for i in range(4):
        for j in range(4):
            out_state[i][j]= Sbox_inv[state[i][j]]
    return out_state

def rot_word(word):
    word_out = []
    word_out.append(word[1])
    word_out.append(word[2])
    word_out.append(word[3])
    word_out.append(word[0])
    return word_out

def sub_word(word):
    word_out = []
    for byte in word:
        word_out.append(Sbox[byte])
    return bytes(word_out)

def xor(array1, array2):
    assert len(array2) == len(array1)
    array_out=[]
    for i in range(len(array1)):
        array_out.append(array1[i] ^ array2[i])
    return bytes(array_out)

def key_to_words(cipherKey):
    words=[]
    for i in range(len(cipherKey) // 4):
        #32 bits words i 4*8=32 4 bytes
        words.append(cipherKey[i*4:(i+1)*4])
    return words

def key_expansion(cipherKey):
    cipherKey=key_to_words(cipherKey)
    expandedKey = []
    for i in range(0, 4*R):
        if(i<N):
            expandedKey.append(cipherKey[i])
        elif(i>=N) and (i%N == 0):
            rotted = rot_word(expandedKey[i-1])
            subbed =  sub_word(rotted)
            rcon = [Rcon[i//N], 0, 0, 0]
            xorWrcon = xor(subbed, rcon)
            keyiminusN = expandedKey[i-N]
            result = xor(keyiminusN,xorWrcon)
            expandedKey.append(result)
            #for debugging
            #print("i:", i, "After rot:", "".join([f'{byte:02x}' for byte in rotted]) , " after sub : ", subbed, "rcon : ", rcon)
            #expandedKey.append( xor(xor(expandedKey[i-N], sub_word(rot_word(expandedKey[i-1]))),[Rcon[i//N], 0, 0, 0]))
            #expandedKey.append( expandedKey[i-N] ^ sub_word(rot_word(expandedKey[i-1])) ^bytes([Rcon[i], 0, 0, 0]))
        elif(i>=N) and (N>6) and (i%N == 4):
            expandedKey.append( xor(expandedKey[i-N],sub_word(expandedKey[i-1])))
        else:
            expandedKey.append(xor(expandedKey[i-N],expandedKey[i-1]))

    #return expanded keys in array of 4*4 arrays
    linear_keys=[]
    for key in expandedKey:
        linear_keys.extend(key)
    keys = np.zeros((R,4,4), dtype=int)
    #TODO not sure about indexing
    for i in range(R):
        for j in range(4):
            for k in range(4):
                keys[i][j][k]=linear_keys[k+j*4+i*4*4]
    return keys





def add_round_key(state,expandedKey):
    # both are 4*4 matrices of bytes
    out_state = np.zeros((4,4), dtype=int)
    #print("k_sch:", "".join([f'{byte:02x}' for array in expandedKey for byte in array]))
    #print("state:", "".join([f'{byte:02x}' for array in state for byte in array]))
    #le key schedule est pas dans le bon ordre par rapport au state donc j'inverse (TODO : reparer)
    for i in range(0,4):
        for j in range(0,4):
            out_state[i][j]= state[i][j] ^ expandedKey[j][i]
    return out_state


def print_state(msg, state):
    print(msg , "".join([f'{state[i%4][i//4]:02x}' for i in range(16)]))


def aes_round(state, expandedKey):
    #print_state("start:", state)
    state= sub_bytes(state)
    #print_state("sbox:", state)
    state = shift_rows(state)
    #print_state("s_rows:", state)
    state = mix_columns(state)
    #print_state("m_col:", state)
    state = add_round_key(state, expandedKey)
    return state


def inv_aes_round(state, expandedKey):
    state = inv_shift_rows(state)
    state = inv_sub_bytes(state)
    state = add_round_key(state, expandedKey)
    state = inv_mix_columns(state)
    return state

def aes_final_round(state,expandedKey):
    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, expandedKey)
    return state


def inv_aes_final_round(state,expandedKey):
    state = inv_shift_rows(state)
    state=  inv_sub_bytes(state)
    state = add_round_key(state, expandedKey)
    return state

def rijndael(state, cipherKey):
    keys = key_expansion(cipherKey)

    # let state be a 4*4 array of bytes
    state = add_round_key(state, keys[0])

    for i in range(1, n_rounds):
        state = aes_round(state,keys[i])
    # Pas sur si n_rounds -1 ou n_rounds
    state = aes_final_round(state, keys[n_rounds])

    #linearalize state
    lin_state = []
    for i in range(16):
        lin_state.append(state[i%4][i//4])
    #for i in state:
        #for j in i:
            #lin_state.append(j)
    #lin_state = bytes(state)
    #lin_state = state
    return bytes(lin_state)


def inv_rijndael(state, cipherKey):
    keys = key_expansion(cipherKey)

    # let state be a 4*4 array of bytes
    state = add_round_key(state, keys[n_rounds])

    for i in reversed(range(1, n_rounds)):
        state = inv_aes_round(state,keys[i])
    # Pas sur si n_rounds -1 ou n_rounds
    state = inv_aes_final_round(state, keys[0])

    #linearalize state
    lin_state = []
    for i in range(16):
        lin_state.append(state[i%4][i//4])
    #for i in state:
    #for j in i:
    #lin_state.append(j)
    #lin_state = bytes(state)
    #lin_state = state
    return bytes(lin_state)
def aes(bloc, key):
    # transform plaintext into state
    state = np.zeros((4,4), dtype=int)
    #print("bloc:", bloc)
    for i in range(4):
        for j in range(4):
            state[i][j]= bloc[i+j*4]
    # Cette facon d'imprimer l'état est correcte
    #print_state("state0:", state)
    return rijndael(state, key)

def inv_aes(bloc, key):
    # transform plaintext into state
    state = np.zeros((4,4), dtype=int)
    #print("bloc:", bloc)
    for i in range(4):
        for j in range(4):
            state[i][j]= bloc[i+j*4]
    # Cette facon d'imprimer l'état est correcte
    #print_state("state0:", state)
    return inv_rijndael(state, key)

def debug_expansion():
    key = bytes.fromhex("603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4")
    print(key)
    expanded = key_expansion(key)
    # print(expanded)
    # print the expanded keys to compare with test vector
    expected = [
        "9ba35411",
        "8e6925af",
        "a51a8b5f",
        "2067fcde",
        "a8b09c1a",
        "93d194cd",
        "be49846e",
        "b75d5b9a",
        "d59aecb8",
        "5bf3c917",
        "fee94248",
        "de8ebe96",
        "b5a9328a",
        "2678a647",
        "98312229",
    ]
    counter = 0
    for i in expanded:
        for j in i:
            for k in j:
                print(f'{k:02x}', end='')
            if (counter >= 8) and counter < 16:
                print(" expected : ", expected[counter - 8])
            counter += 1
            print("")


def debug_aes():
    # taken from https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197.pdf#page=46
    plaintext = bytes.fromhex("00112233445566778899aabbccddeeff")
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f")
    expected = "8ea2b7ca516745bfeafc49904b496089"

    ct = aes(plaintext, key)
    print("ct : ", ct)
    print(len(ct))
    print("expected : ", expected)

    msg = inv_aes(ct, key)
    print(msg)

if __name__ == "__main__":
    #debug_expansion()
    debug_aes()