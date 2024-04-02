from __future__ import annotations

from random import shuffle

import pytest
from hypothesis import given, assume, settings
from hypothesis.strategies import binary, integers, dictionaries, text

from compress import *

settings.register_profile("norand", settings(derandomize=True, max_examples=200))
settings.load_profile("norand")


# === Test Byte Utilities ===
# Technically, these utilities are given to you in the starter code, so these
# first 3 tests below are just intended as a sanity check to make sure that you
# did not modify these methods and are therefore using them incorrectly.
# You will not be submitting utils.py anyway, so these first three tests are
# solely for your own benefit, as a sanity check.

@given(integers(0, 255))
def test_byte_to_bits(b: int) -> None:
    """ Test that byte_to_bits produces binary strings of length 8."""
    assert set(byte_to_bits(b)).issubset({"0", "1"})
    assert len(byte_to_bits(b)) == 8


@given(text(["0", "1"], min_size=0, max_size=8))
def test_bits_to_byte(s: str) -> None:
    """ Test that bits_to_byte produces a byte."""
    b = bits_to_byte(s)
    assert isinstance(b, int)
    assert 0 <= b <= 255


@given(integers(0, 255), integers(0, 7))
def test_get_bit(byte: int, bit_pos: int) -> None:
    """ Test that get_bit(byte, bit) produces  bit values."""
    b = get_bit(byte, bit_pos)
    assert isinstance(b, int)
    assert 0 <= b <= 1


# === Test the compression code ===

@given(binary(min_size=0, max_size=1000))
def test_build_frequency_dict(byte_list: bytes) -> None:
    """ Test that build_frequency_dict returns dictionary whose values sum up
    to the number of bytes consumed.
    """
    # creates a copy of byte_list, just in case your implementation of
    # build_frequency_dict modifies the byte_list
    b, d = byte_list, build_frequency_dict(byte_list)
    assert isinstance(d, dict)
    assert sum(d.values()) == len(b)


@given(dictionaries(integers(min_value=0, max_value=255), integers(min_value=1, max_value=1000), dict_class=dict,
                    min_size=2, max_size=256))
def test_build_huffman_tree(d: dict[int, int]) -> None:
    """ Test that build_huffman_tree returns a non-leaf HuffmanTree."""
    t = build_huffman_tree(d)
    assert isinstance(t, HuffmanTree)
    assert not t.is_leaf()


@given(dictionaries(integers(min_value=0, max_value=255), integers(min_value=1, max_value=1000), dict_class=dict,
                    min_size=2, max_size=256))
def test_get_codes(d: dict[int, int]) -> None:
    """ Test that the sum of len(code) * freq_dict[code] is optimal, so it
    must be invariant under permutation of the dictionary.
    Note: This also tests build_huffman_tree indirectly.
    """
    t = build_huffman_tree(d)
    c1 = get_codes(t)
    d2 = list(d.items())
    shuffle(d2)
    d2 = dict(d2)
    t2 = build_huffman_tree(d2)
    c2 = get_codes(t2)
    assert sum([d[k] * len(c1[k]) for k in d]) == \
           sum([d2[k] * len(c2[k]) for k in d2])


@given(dictionaries(integers(min_value=0, max_value=255), integers(min_value=1, max_value=1000), dict_class=dict,
                    min_size=2, max_size=256))
def test_number_nodes(d: dict[int, int]) -> None:
    """ If the root is an interior node, it must be numbered two less than the
    number of symbols, since a complete tree has one fewer interior nodes than
    it has leaves, and we are numbering from 0.
    Note: this also tests build_huffman_tree indirectly.
    """
    t = build_huffman_tree(d)
    assume(not t.is_leaf())
    count = len(d)
    number_nodes(t)
    assert count == t.number + 2


@given(dictionaries(integers(min_value=0, max_value=255), integers(min_value=1, max_value=1000), dict_class=dict,
                    min_size=2, max_size=256))
def test_avg_length(d: dict[int, int]) -> None:
    """ Test that avg_length returns a float in the interval [0, 8], if the max
    number of symbols is 256.
    """
    t = build_huffman_tree(d)
    f = avg_length(t, d)
    assert isinstance(f, float)
    assert 0 <= f <= 8.0


@given(binary(min_size=2, max_size=1000))
def test_compress_bytes(b: bytes) -> None:
    """ Test that compress_bytes returns a bytes object that is no longer
    than the input bytes. Also, the size of the compressed object should be
    invariant under permuting the input.
    Note: this also indirectly tests build_frequency_dict, build_huffman_tree,
    and get_codes.
    """
    d = build_frequency_dict(b)
    t = build_huffman_tree(d)
    c = get_codes(t)
    compressed = compress_bytes(b, c)
    assert isinstance(compressed, bytes)
    assert len(compressed) <= len(b)
    lst = list(b)
    shuffle(lst)
    b = bytes(lst)
    d = build_frequency_dict(b)
    t = build_huffman_tree(d)
    c = get_codes(t)
    compressed2 = compress_bytes(b, c)
    assert len(compressed2) == len(compressed)


@given(binary(min_size=2, max_size=1000))
def test_tree_to_bytes(b: bytes) -> None:
    """ Test that tree_to_bytes generates a bytes representation of a postorder
    traversal of a tree's internal nodes.
    Since each internal node requires 4 bytes to represent, and there are
    1 fewer internal nodes than distinct symbols, the length of the bytes
    produced should be 4 times the length of the frequency dictionary, minus 4.
    Note: also indirectly tests build_frequency_dict, build_huffman_tree, and
    number_nodes.
    """
    d = build_frequency_dict(b)
    assume(len(d) > 1)
    t = build_huffman_tree(d)
    number_nodes(t)
    output_bytes = tree_to_bytes(t)
    dictionary_length = len(d)
    leaf_count = dictionary_length
    assert (4 * (leaf_count - 1)) == len(output_bytes)


# === Test a roundtrip conversion

@given(binary(min_size=1, max_size=1000))
def test_round_trip_compress_bytes(b: bytes) -> None:
    """ Test that applying compress_bytes and then decompress_bytes
    will produce the original text.
    """
    text = b
    freq = build_frequency_dict(text)
    assume(len(freq) > 1)
    tree = build_huffman_tree(freq)
    codes = get_codes(tree)
    compressed = compress_bytes(text, codes)
    print(compressed)
    decompressed = decompress_bytes(tree, compressed, len(text))
    print(decompressed)
    assert text == decompressed


"""Below are the specific test cases that I made to test my own work"""


def test_build_freq_dict() -> None:
    # Single case
    x = bytes([1])
    y = build_frequency_dict(x)
    assert len(y) == 1
    assert y[1] == 1
    # Repeating Case
    x = bytes([1, 1])
    y = build_frequency_dict(x)
    assert len(y) == 1
    assert y[1] == 2
    # Non repeating case
    x = bytes([1, 2])
    y = build_frequency_dict(x)
    assert len(y) == 2
    assert y[1] == 1
    assert y[2] == 1


def test_build_huffman_tree_redo() -> None:
    # Dummy tree case -> must pick a value not in the freq_dict **
    x = bytes([1])
    y = build_frequency_dict(x)
    z = build_huffman_tree(y)
    assert z.left == HuffmanTree(1)
    assert z.symbol is None
    assert z.right.symbol is not None
    # Note: this does not check if the dummy is not in the freq_dict In theory,
    # it should be fine otherwise
    x = bytes([1, 2, 2])
    y = build_frequency_dict(x)
    z = build_huffman_tree(y)
    # This one makes sure greater is always on the right
    assert z.symbol is None
    assert z.left == HuffmanTree(1)
    assert z.right == HuffmanTree(2)
    # bigger example, using a bigger tree
    x = {1: 1, 2: 5, 3: 20}
    y = build_huffman_tree(x)
    assert y.symbol is None
    assert y.right == HuffmanTree(3)
    assert y.left.symbol is None
    assert y.left.left == HuffmanTree(1)
    assert y.left.right == HuffmanTree(2)


def test_get_codes_redo() -> None:
    # Test that the accumulator works right to generate the proper code
    x = {1: 1, 2: 5, 3: 20}
    y = build_huffman_tree(x)
    z = get_codes(y)
    assert len(z) == 3
    assert z[3] == '1'
    assert z[2] == '01'
    assert z[1] == '00'
    # In theory, this should work for everything else, no other real specials
    # example with other accumulator
    x = HuffmanTree(None, HuffmanTree(None, HuffmanTree(None, HuffmanTree(2), None), None), None)
    y = get_codes(x)
    assert y[2] == '000'


def test_number_nodes_redo() -> None:
    # Test that only the proper nodes get numbered i.e. the ones without symbols
    # Case 1 base
    x = HuffmanTree(None, HuffmanTree(1), HuffmanTree(2))
    number_nodes(x)
    assert x.number == 0
    assert x.left.number is None
    assert x.right.number is None

    # Case 2 stacked tree, check it goes proper order
    x = HuffmanTree(None, HuffmanTree(1), HuffmanTree(2))
    y = HuffmanTree(None, HuffmanTree(3), HuffmanTree(4))
    z = HuffmanTree(None, y, HuffmanTree(5))
    total = HuffmanTree(None, x, z)
    number_nodes(total)
    assert total.number == 3
    assert total.left.number == 0
    assert total.right.number == 2
    assert total.right.left.number == 1


def test_avg_length_redo() -> None:
    # recall that one weird special case of the dummy tree
    x = HuffmanTree(None, HuffmanTree(1), HuffmanTree(2))
    y = {1:20}
    z = avg_length(x, y)
    assert z == 1
    # Similar test, but with better weighted average
    x = HuffmanTree(None, HuffmanTree(1), HuffmanTree(2))
    y = {1: 1, 2: 1}
    z = avg_length(x, y)
    assert z == 1
    # Final case incorporating the different lengths
    x = HuffmanTree(None, HuffmanTree(5), HuffmanTree(6))
    y = HuffmanTree(None, x, HuffmanTree(7))
    j = {5: 2, 6: 3, 7: 8}
    z = avg_length(y, j)
    assert z == 18 / 13
    # aka ((2x2) + (3x2) + (8x1)) / (2+3+8)


def test_improve_tree() -> None:
    x = HuffmanTree(None, HuffmanTree(2), HuffmanTree(1))
    freq = {1: 1, 2: 2}
    improve_tree(x, freq)
    assert x == HuffmanTree(None, HuffmanTree(2), HuffmanTree(1))

    # Case 2 stacked tree, check it goes proper order
    left = HuffmanTree(None, HuffmanTree(2), HuffmanTree(1))
    x = HuffmanTree(None, left, HuffmanTree(3))
    freq = {1: 7, 2: 2, 3: 2}
    improve_tree(x, freq)
    assert x.right.symbol == 1
    assert x.left.left.symbol == 3
    assert x.left.right.symbol == 2


def test_compress_bytes_redo() -> None:
    pass


if __name__ == "__main__":
    pytest.main(["test_huffman_properties_basic.py"])
