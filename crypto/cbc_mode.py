from crypto import aes
from secrets import token_bytes
from crypto.bytearray_operations import xor, to_bytearray


AES_BLOCK_SIZE = 128
AES_BLOCK_SIZE_BYTES = AES_BLOCK_SIZE//8
AES_KEY_SIZE = 256
AES_KEY_SIZE_BYES = AES_KEY_SIZE//8




def cbc_mode_aes_encrypt(plaintext, iv, key):
    if (type(plaintext) == str):
        plaintext = bytearray(plaintext, encoding="utf_8")
    else:
        plaintext = bytearray(plaintext)

    # needs to be a multiple of block size
    assert(len(plaintext) % (AES_BLOCK_SIZE_BYTES) ==0)
    size = len(plaintext) // (AES_BLOCK_SIZE_BYTES)
    previous_ct = iv
    output = bytearray()
    for i in range(0, size):
        bloc = xor(previous_ct, plaintext[i*(AES_BLOCK_SIZE_BYTES):(i+1) * (AES_BLOCK_SIZE_BYTES)])
        ct = aes.aes(bloc, key)
        output.extend(ct)
        previous_ct = ct

    return output

def cbc_mode_aes_decrypt(ciphertext, iv, key):
    ciphertext = to_bytearray(ciphertext)
    assert (len(ciphertext) % (AES_BLOCK_SIZE_BYTES) == 0)
    size = len(ciphertext) // (AES_BLOCK_SIZE_BYTES)

    previous_ct = iv
    plaintext= bytearray()

    for i in range(0, size):
        bloc= ciphertext[i*(AES_BLOCK_SIZE_BYTES):(i+1) * (AES_BLOCK_SIZE_BYTES)]
        plaintext.extend(xor(previous_ct, aes.inv_aes(bloc, key)))
        previous_ct = bloc
    return plaintext




if __name__ == "__main__":
    plaintext = "Salut Bastien, c'est mon message"
    iv = token_bytes(AES_BLOCK_SIZE_BYTES)
    key = token_bytes(aes.AES_KEY_SIZE_BYTES)

    ct = cbc_mode_aes_encrypt(plaintext, iv, key)
    decrypted = cbc_mode_aes_decrypt(ct,iv, key)

    print("CT = ", ct)
    print("Decrypted =", decrypted)
    print("Plaintext =", to_bytearray((plaintext)))
    print(len(plaintext))
    print(len(ct))
    print(len(decrypted))
    print(len(iv))
    print(len(key))
