from crypto.diffie_hellman import *


def test_DH():
    a = randbits(2048)
    b = randbits(2048)
    A = dh_step1(a)
    B = dh_step1(b)
    key1 = dh_step2(A,b)
    key2 = dh_step2(B,a)
    assert (key1==key2)