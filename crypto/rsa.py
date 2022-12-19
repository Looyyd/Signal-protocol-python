# This file is entirely dedicated to cryptographic operations linked to RSA
import numpy
import random

# Basic encryptio/decryption functions

def encrypt(message: int, ekey: int, mod: int)-> int:
    # Encrypt a message using RSA scheme
    return pow(message,ekey,mod)
    
def decrypt(ciphermessage: int, dkey: int, mod: int)-> int:
    # Decrypt a message using RSA scheme
    return pow(ciphermessage,dkey,mod)


# To calculate keys, we need 4 steps : 
# S1 : Find to large prime number (in terms of bytes representation) p and q
# S2 : calculate n = p*q
# S3 : create public key (must not be a factor of E(n)) pubkey
# S4 : create private key = pubkey^-1

def long_2048_number():
    #Generating a 2048 bits long number
    p = random.randrange(2**(2048-1)+1, 2**2048-1)
    return p

def test_primality(n):
    #Use the Rabin-Miller test to check if probabilty of being a prime number is high enough
    #We will use 20 rounds of Rabin-Miller test
    
    #A list of the first primes to test our number
    small_primes_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349]
    
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
    for _ in range(20):
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


p = long_2048_number()
while test_primality(p) == False:
    p = long_2048_number()
print(p)