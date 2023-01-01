# This file is entirely dedicated to cryptographic operations linked to RSA
import numpy, random, time, os, sys, base64

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from crypto import first_10000_primes
from crypto.SHA3_512 import Sha3_512


# Basic encryption/decryption functions

def encrypt(message: int, priv_key: int, mod: int)-> int:
    # Encrypt a message using RSA scheme
    return pow(message,priv_key,mod)
    
def decrypt(ciphermessage: int, pub_key: int, mod: int)-> int:
    # Decrypt a message using RSA scheme
    return pow(ciphermessage,pub_key,mod)

# Methods for sign and unsign

def HASHING_TO_SIGN(key: int)-> int:

    # From int to bytearray
    str_key = str(key)
    bytearray_str_key = bytearray(str_key, "utf-8")

    # Hash computation
    key_hash = Sha3_512(bytearray_str_key)

    #From bytearray to int
    byte_key_hash = base64.b64encode(key_hash)
    int_key_hash = int.from_bytes(byte_key_hash, "little")

    return int_key_hash

# To calculate keys, we need 4 steps : 
# S1 : Find to large prime number (in terms of bytes representation) p and q
# S2 : calculate n = p*q
# S3 : create public key (must not be a factor of E(n)) pubkey
# S4 : create private key = pubkey^-1

# Number generation is based on the following source : 
# How to Generate Large Prime Numbers, GeeksForGeeks : https://www.geeksforgeeks.org/how-to-generate-large-prime-numbers-for-rsa-algorithm/

def large_odd_number()-> int:
    #Generating a 2048 bits long number
    p = random.randrange(2**(2048-1)+1, 2**2048-1, 2)
    return p

def large_prime_number()-> int:
    isPrime = False
    while isPrime == False:
        p = large_odd_number()
        isPrime = check_primality(p)
    return p

def check_primality(n: int):
    #Use the Rabin-Miller test to check if probabilty of being a prime number is high enough
    #We will use 20 rounds of Rabin-Miller test
    
    #A list of the first primes to test our number
    #Keeping first prime test or direct Rabin-Miller -> keep because it's faster
    #small_primes_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349]
    small_primes_list = first_10000_primes.primes

    # TODO: change later to more ?
    #CHANGED NAME to avoid collision with testing method
    n_rounds = 6
    
    #Test first prime
    if n < 2:
        return False
    for p in small_primes_list:
        if n < p * p: return True
        if n % p == 0: return False
    
    #Rabin-Miller test

    # This Rabin-Miller code has been created with the help of the following sources : 
    # How to Generate Large Prime Numbers, GeeksForGeeks : https://www.geeksforgeeks.org/how-to-generate-large-prime-numbers-for-rsa-algorithm/
    # Rabin-Miller Primality test, Wikipedia : https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test
    # Rabin-Miller implementation won't work, Stack Overflow : https://stackoverflow.com/questions/14613304/rabin-miller-strong-pseudoprime-test-implementation-wont-work

    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2
    for _ in range(n_rounds):
        a = random.randrange(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

#Euclide and Extanded Euclide tests will be necessary to generate keys
#TODO Optimize recursive pgcd might get better results than iterative method. For now pgcd works, not rec_pgcd
def rec_pgcd(m: int, n: int)-> int:
    if n == 0:
        return m
    else:
        r = m % n
        return rec_pgcd(n, r)

def pgcd(m: int, n: int)-> int:
    while m:
        m,n = n%m,m
    return n

# This function generates public and associated private keys
def generate_keys():

    print("Generating prime numbers for RSA keys")
    print("---------------------------------------")
    p = large_prime_number()
    q = large_prime_number()
    while p == q :
        q=large_prime_number()

    print("Calculating keys")
    print("---------------------------------------")
    n = p*q
    ind_n = (p-1)*(q-1)

    pub_key = random.randrange(2, ind_n, 1)
    while pgcd(pub_key, ind_n) != 1:
        # last parameter give step 2 to function, that way it only gives odd numbers
        pub_key = random.randrange(2, ind_n, 1)

    priv_key = pow(pub_key,-1,ind_n)

    print("Public key : ", pub_key, "You won't get the private key... Because it's meant to be secret ;)")
    print("---------------------------------------")
    return pub_key, priv_key, n



if __name__ == "__main__":
    exe_time = []
    moy_el_time = 0
    for i in range (1000):
        start_time = time.time()
        (pub, priv, mod) = generate_keys()
        m = 10
        c = encrypt(m, priv, mod)
        n = decrypt(c, pub, mod)
        print("Message", n)
        print("---------------------------------------------------------------------------------------------")
        print("Public Key", pub)
        print("---------------------------------------------------------------------------------------------")
        print("Private Key",priv)
        elapsed_time = time.time() - start_time
        print("---------------------------------------------------------------------------------------------")
        print("Elapsed time during execution : ", elapsed_time)
        print("---------------------------------------------------------------------------------------------")
        print(i)

        exe_time.append(elapsed_time)
        moy_el_time = moy_el_time + exe_time[i]

    moy_el_time //= 1000
    print("Mean execution time : ", moy_el_time)

