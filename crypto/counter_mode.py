from crypto import aes
from secrets import token_bytes

# standard https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38a.pdf
AES_BLOCK_SIZE = 128
AES_KEY_SIZE = 256

# returns a stream of length_in_blocks*128
def counter_mode_aes(length_in_blocks, nonce, key):
    stream = bytearray()
    if (type(nonce)== str):
        nonce = bytearray(nonce, encoding="utf-8")
    else:
        nonce = bytearray(nonce)
    # we will take a nonce of size 128 and a counter of size 128
    nonce_size = 128
    counter_size = 128
    if len(nonce)< nonce_size:
        nonce.extend( b"\x00" * (nonce_size - len(nonce)) )
    else:
        nonce = nonce[0:nonce_size]
    counter = 0

    for i in range(0,length_in_blocks):
        bloc = nonce + counter.to_bytes(counter_size//8, byteorder='big')
        stream.extend(aes.aes(bloc,key))
        counter += 1

    return stream

def xor(x, y):
    return bytearray((x[i]) ^ (y[i]) for i in range(min(len(x), len(y))))


if __name__ == "__main__":
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f")
    nonce = token_bytes(16)
    print(counter_mode_aes(3,nonce, key))

    message = bytearray("High how are you", encoding = "utf-8")

    encrypted = xor( message, counter_mode_aes( len(message)*8//128 +1 , nonce, key) )


    decrypted = xor( encrypted,  counter_mode_aes( len(encrypted)*8//128 +1 , nonce, key) )

    print(encrypted)
    print(len(encrypted) == len(message))
    print(decrypted)