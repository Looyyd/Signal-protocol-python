# This file is entirely dedicated to cryptographic operations linked to RSA
import numpy
import random
import time

# ca voulait pas import sans le path
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from crypto import first_10000_primes


# Basic encryptio/decryption functions

def encrypt(message: int, priv_key: int, mod: int)-> int:
    # Encrypt a message using RSA scheme
    return pow(message,priv_key,mod)
    
def decrypt(ciphermessage: int, pub_key: int, mod: int)-> int:
    # Decrypt a message using RSA scheme
    return pow(ciphermessage,pub_key,mod)


# To calculate keys, we need 4 steps : 
# S1 : Find to large prime number (in terms of bytes representation) p and q
# S2 : calculate n = p*q
# S3 : create public key (must not be a factor of E(n)) pubkey
# S4 : create private key = pubkey^-1

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


def inv_mod(e: int,n: int)-> int:
    r0, u0, v0 = e, 1, 0
    r1, u1, v1 = n, 0, 1
    while r1 != 0:
        r2 = r0 % r1
        q2 = r0 // r1
        u, v = u0, v0
        r0, u0, v0 = r1, u1, v1
        r1, u1, v1 = r2, u-q2*u1, v-q2*v1
    if u0 < 0:
        u0 = u0 + n
    return u0

# This function generates public and associated private keys
def generate_keys():

    print("generating primes")
    p = large_prime_number()
    q = large_prime_number()
    while p == q :
        q=large_prime_number()

    print("calculating")
    n = p*q
    ind_n = (p-1)*(q-1)

    pub_key = random.randrange(2, ind_n, 1)
    while pgcd(pub_key, ind_n) != 1:
        # last parameter give step 2 to function, that way it only gives odd numbers
        pub_key = random.randrange(2, ind_n, 1)

    #priv_key = inv_mod(pub_key, ind_n)
    priv_key = pow(pub_key,-1,ind_n)

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

