from crypto import SHA3_512
import binascii

def xor(x, y):
    return bytearray((x[i]) ^ (y[i]) for i in range(min(len(x), len(y))))

# inspired by https://stackoverflow.com/a/56085727/15403395
def hmad_sha3_512(K, message):
    #TODO, ne correspond pas au vecteurs NIST
    block_len = 72
    type_K = type(K)
    if type_K == str:
        K = bytearray(K, encoding="utf-8")
    else:
        K = bytearray(K)
    if (len(K) > block_len ):
        K = SHA3_512.Sha3_512(K)
    elif (len(K)< block_len):
        # padd with zeroes
        K = bytearray(K) + bytes(b'\x00') * (block_len - len(K))
    if type(message) == str:
        message = bytearray(message,encoding="utf-8")
    else:
        message : bytearray(message)

    ipad =bytearray(block_len * "\x36", encoding="utf-8")
    opad = bytearray(block_len* "\x5c", encoding="utf-8")

    #print("Text is:", binascii.hexlify(message))
    #print("Key is:", binascii.hexlify(K))

    k_ipad = bytearray(xor(ipad, K))
    #print("ipad is:", binascii.hexlify(ipad))
    #print("k_ipad is:", binascii.hexlify(k_ipad))
    k_ipad_msg = k_ipad + message
    #print("k_ipad_msg:", binascii.hexlify(k_ipad_msg))
    h_inner = SHA3_512.Sha3_512(k_ipad + message)
    #print("h_inner is:", binascii.hexlify(h_inner))
    k_opad = bytearray(xor(opad,K))
    #print("k_opad is:", binascii.hexlify(k_opad))
    hmac = SHA3_512.Sha3_512(bytearray(k_opad + h_inner))
    return hmac



if __name__ == "__main__":
    key = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f"
    message = "Sample message for keylen<blocklen"
    hmac = hmad_sha3_512(key, message)
    print("hmac is:",binascii.hexlify(hmac))