import pytest
from crypto.SHA3_512 import *


def test_padding():
    input = "A"*71
    input_bytes = bytearray()
    input_bytes.extend(map(ord, input))
    hash1 = Sha3_512(input_bytes)

    input = "A"*72
    input_bytes = bytearray()
    input_bytes.extend(map(ord, input))
    hash2 = Sha3_512(input_bytes)

    input = "A"*73
    input_bytes = bytearray()
    input_bytes.extend(map(ord, input))
    hash3 = Sha3_512(input_bytes)
    assert len(hash1)%byte_rate == 0
    assert len(hash2)%byte_rate == 0
    assert len(hash3)%byte_rate == 0



