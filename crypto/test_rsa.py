from crypto.rsa import *
import pytest

def test_encrypt():
    
    with pytest.raises(TypeError):
        size = 5
        encrypt(2.3, 4, 5)
        encrypt(3, 3.4, 5)
        encrypt(2, 3, 4.5)
        encrypt("Test", 2, 3)
        encrypt(2, "Test", 3)
        encrypt(2, 3, "Test")
        encrypt(2j, 3, 4)
        encrypt(2, 3j, 4)
        encrypt(2, 3, 4j)
        encrypt((2, 3), 4, 5)
        encrypt(2,(3, 4), 5)
        encrypt(2, 3, (4, 5))
        encrypt(range(2), 3, 4)
        encrypt(2, range(3), 4)
        encrypt(2, 3, range(4))
        encrypt([2, 3], 4, 5)
        encrypt(2,[3, 4], 5)
        encrypt(2, 3, [4, 5])
        encrypt({"number": 2}, 3, 4)
        encrypt(2, {"number": 3}, 4)
        encrypt(2, 3, {"number": 4  })
        encrypt({2, 3}, 4, 5)
        encrypt(2, {3, 4}, 5)
        encrypt(2, 3, {4, 5})
        encrypt(frozenset((2, 3)), 4, 5)
        encrypt(2, frozenset((3, 4)), 5)
        encrypt(2, 3, frozenset((4, 5)))
        encrypt(True, 3, 4)
        encrypt(2, True, 4)
        encrypt(2, 3, True)
        encrypt(bytes(size), 3, 4)
        encrypt(2, bytes(size), 4)
        encrypt(2, 3, bytes(size))
        encrypt(bytearray(size), 3, 4)
        encrypt(2, bytearray(size), 4)
        encrypt(2, 3, bytearray(size))
        encrypt(memoryview(bytes(size)), 3, 4)
        encrypt(2, memoryview(bytes(size)), 4)
        encrypt(2, 3, memoryview(bytes(size)))

    m = 3
    e = 8
    mod = 15
    assert encrypt(m, e, mod) == 6
    assert type(encrypt(m, e, mod)) == int

def test_decrypt():
    
    with pytest.raises(TypeError):
        size = 5
        decrypt(2.3, 4, 5)
        decrypt(3, 3.4, 5)
        decrypt(2, 3, 4.5)
        decrypt("Test", 2, 3)
        decrypt(2, "Test", 3)
        decrypt(2, 3, "Test")
        decrypt(2j, 3, 4)
        decrypt(2, 3j, 4)
        decrypt(2, 3, 4j)
        decrypt((2, 3), 4, 5)
        decrypt(2,(3, 4), 5)
        decrypt(2, 3, (4, 5))
        decrypt(range(2), 3, 4)
        decrypt(2, range(3), 4)
        decrypt(2, 3, range(4))
        decrypt([2, 3], 4, 5)
        decrypt(2,[3, 4], 5)
        decrypt(2, 3, [4, 5])
        decrypt({"number": 2}, 3, 4)
        decrypt(2, {"number": 3}, 4)
        decrypt(2, 3, {"number": 4  })
        decrypt({2, 3}, 4, 5)
        decrypt(2, {3, 4}, 5)
        decrypt(2, 3, {4, 5})
        decrypt(frozenset((2, 3)), 4, 5)
        decrypt(2, frozenset((3, 4)), 5)
        decrypt(2, 3, frozenset((4, 5)))
        decrypt(True, 3, 4)
        decrypt(2, True, 4)
        decrypt(2, 3, True)
        decrypt(bytes(size), 3, 4)
        decrypt(2, bytes(size), 4)
        decrypt(2, 3, bytes(size))
        decrypt(bytearray(size), 3, 4)
        decrypt(2, bytearray(size), 4)
        decrypt(2, 3, bytearray(size))
        decrypt(memoryview(bytes(size)), 3, 4)
        decrypt(2, memoryview(bytes(size)), 4)
        decrypt(2, 3, memoryview(bytes(size)))

    m = 6
    e = 2
    mod = 15
    assert decrypt(m, e, mod) == 6
    assert type(decrypt(m, e, mod)) == int

def test_large_odd_number():
    n = large_odd_number()
    assert type(n) == int

def test_large_prime_number():

    n = large_prime_number()
    assert type(n) == int

def test_check_primality():

    with pytest.raises(TypeError):
        check_primality("Test")
        check_primality(2.3)
        check_primality(1j)
        check_primality([2, 3])
        check_primality((2, 3))
        check_primality(range(3))
        check_primality({"number": 2})
        check_primality({2, 3})
        check_primality(frozenset(2, 3))
        check_primality(True)
        check_primality(bytes(2))
        check_primality(bytearray(2))
        check_primality(memoryview(bytes(2)))

    result = check_primality(151)
    assert type(result) == bool

# As rec_pgcd isn't used, we're not implementing a test method for it.

def test_pgcd():

    with pytest.raises(TypeError):
        pgcd(2.3, 4)
        pgcd(2, 3.4)
        pgcd("Test", 3)
        pgcd(2, "Test")
        pgcd(1j, 3)
        pgcd(2, 3j)
        pgcd([2, 3], 4)
        pgcd(2, [3, 4])
        pgcd((2, 3), 4)
        pgcd(2, (3, 4))
        pgcd(range(3), 3)
        pgcd(2, range(3))
        pgcd({"number": 2}, 3)
        pgcd(2, {"number": 2})
        pgcd({2, 3}, 4)
        pgcd(2, {3, 4})
        pgcd(frozenset(2, 3), 4)
        pgcd(2, frozenset(3, 4))
        pgcd(True, 3)
        pgcd(2, True)
        pgcd(bytes(2), 3)
        pgcd(2, bytes(3))
        pgcd(bytearray(2), 3)
        pgcd(2, bytearray(3))
        pgcd(memoryview(bytes(2), 3))
        pgcd(2, memoryview(bytes(2)))

    result = pgcd(10, 15)
    assert type(result) == int
    assert result == 5

def test_HASHING_TO_SIGN():

    with pytest.raises(TypeError):
        HASHING_TO_SIGN("Test")
        HASHING_TO_SIGN(2.3)
        HASHING_TO_SIGN(1j)
        HASHING_TO_SIGN([2, 3])
        HASHING_TO_SIGN((2, 3))
        HASHING_TO_SIGN(range(3))
        HASHING_TO_SIGN({"number": 2})
        HASHING_TO_SIGN({2, 3})
        HASHING_TO_SIGN(frozenset(2, 3))
        HASHING_TO_SIGN(True)
        HASHING_TO_SIGN(bytes(2))
        HASHING_TO_SIGN(bytearray(2))
        HASHING_TO_SIGN(memoryview(bytes(2)))

    result = HASHING_TO_SIGN(151)
    assert type(result) == int

def test_generate_keys():

    pubkey, privkey, n = generate_keys()
    assert type(pubkey) == int
    assert type(privkey) == int 
    assert type(n) == int 

