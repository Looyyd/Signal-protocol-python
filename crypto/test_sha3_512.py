import pytest
from crypto.SHA3_512 import *


def test_padding():
    input = "A"*71
    input_bytes = bytearray()
    input_bytes.extend(map(ord, input))
    hash1 = pad(input_bytes)

    input = "A"*72
    input_bytes = bytearray()
    input_bytes.extend(map(ord, input))
    hash2 = pad(input_bytes)

    input = "A"*73
    input_bytes = bytearray()
    input_bytes.extend(map(ord, input))
    hash3 = pad(input_bytes)
    assert len(hash1)%byte_rate == 0
    assert len(hash2)%byte_rate == 0
    assert len(hash3)%byte_rate == 0




def test_1Dto3Dto1D():
    test_state='A'*(1600//8)
    input_bytes = bytearray()
    input_bytes.extend(map(ord, test_state))
    state3D= array_1Dto3D(input_bytes)
    state = array_3Dto1D(state3D)
    assert state == input_bytes
