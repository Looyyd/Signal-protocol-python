from crypto import hmac_SHA3_512

# taken from https://en.wikipedia.org/wiki/PBKDF2

def F(Password, Salt, c, i_input):
    U = []
    if type(Salt) == str:
        Salt = bytearray(Salt, encoding="utf-8")
    U.append(hmac_SHA3_512.hmad_sha3_512(Password, Salt + bytearray(i_input)))
    output = U[0]
    for i in range(1,c):
        U.append(hmac_SHA3_512.hmad_sha3_512(Password, U[i-1]))
        output = hmac_SHA3_512.xor(U[i],output)

    return output



def hkdf(length, salt, password, c_iter ):
    #hlen is size of hmac_SHA3_512 hash
    hlen = 512//8
    output = bytearray()
    for i in range(0, length//hlen):
        output.extend(F(password, salt, c_iter, i))
    return output

def session_key_derivation(keys_str):
    # 2 iteration car mon implémentation est giga slow
    return hkdf(512//8, "", keys_str, 2)

if __name__ == "__main__":
    # TODO, normalement le nombre d'itérations c'est 1000 au moins
    # mais nos fonctions sont lentes de oute facon deonc je met moins
    print(hkdf(512//8, "SALT", bytearray("PASS", encoding="utf-8"), 10))