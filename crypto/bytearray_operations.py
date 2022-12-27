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

if __name__ == "__main__":

    from rsa import *
    from SHA3_512 import Sha3_512
    import base64

    p_key, priv_key, modulo = generate_keys()
    print("------ P KEY -------")
    print(p_key)
    print(type(p_key))

    str_key = str(p_key)
    b_str_key = bytearray(str_key, "utf-8")
    print("------ BYTEARRAY P KEY -------")
    print(b_str_key)
    print(type(b_str_key))

    decoded_str_key = b_str_key.decode()
    print("------ DECODED STR P KEY -------")
    print(decoded_str_key)
    print(type(decoded_str_key))
    decoded_key = int(decoded_str_key)
    print("------ DECODED P KEY -------")
    print(decoded_key)
    print(type(decoded_key))

    str_decoded_key = str(decoded_key)
    b_str_decoded_key = bytearray(str_decoded_key, "utf-8")
    print("------ BYTEARRAY DECODED P KEY -------")
    print(b_str_decoded_key)
    print(type(b_str_decoded_key))


    hash_p_key = Sha3_512(b_str_key)
    hash_decoded_p_key = Sha3_512(b_str_decoded_key)

    if hash_p_key == hash_decoded_p_key:
        print("SUCCESS")
    else:
        print("T'ES NAZE TROUDUC")

    print(hash_p_key)
    print(type(hash_p_key))


    b64_HASH = base64.b64encode(hash_p_key)
    b64_HASH2 = base64.b64encode(hash_p_key)
    if b64_HASH == b64_HASH2:
        print("SUCCESS")
    print(b64_HASH)
    print(type(b64_HASH))


    INT_HASH = int.from_bytes(b64_HASH, "little")
    INT_HASH2 = int.from_bytes(b64_HASH2, "little")
    if INT_HASH == INT_HASH2:
        print("SUCCESS")
    print(INT_HASH)
    print(type(INT_HASH))

    #PROCEDURE SIGNATURE
    # Il faut : Faire hash cle puis chiffre hash
    # 1 : Passer de int cle à bytearray cle
    # 2 : Faire hash
    # 3 : passer de bytearray hash à int hash
    # 4 : chiffrer int hash
    # PASSER DE INT A BYTEARRAY
    # INT => STR => BYTEARRAY
    # PASSER DE BYTEARRAY A INT
    # BYTEARRAY => BYTE (Base64 encoding) => INT
   
