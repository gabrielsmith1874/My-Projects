def build_huffman_tree2(freq_dict: dict[int, int]) -> HuffmanTree:
    """ Return the Huffman tree corresponding to the frequency dictionary
    <freq_dict>.

    Precondition: freq_dict is not empty.

    >>> freq = {2: 6, 3: 4}
    >>> t = build_huffman_tree2(freq)
    >>> result = HuffmanTree(None, HuffmanTree(3), HuffmanTree(2))
    >>> t == result
    True
    >>> freq = {2: 6, 3: 4, 7: 5}
    >>> t = build_huffman_tree2(freq)
    >>> result = HuffmanTree(None, HuffmanTree(2), \
                             HuffmanTree(None, HuffmanTree(3), HuffmanTree(7)))
    >>> t == result
    True
    >>> import random
    >>> symbol = 133
    >>> freq = {symbol: 6}
    >>> t = build_huffman_tree2(freq)
    >>> any_valid_byte_other_than_symbol = (symbol + 1) % 256
    >>> dummy_tree = HuffmanTree(any_valid_byte_other_than_symbol)
    >>> result = HuffmanTree(None, HuffmanTree(symbol), dummy_tree)
    >>> t.left == result.left or t.right == result.left
    True
    >>> freq = {2: 6}
    >>> t = build_huffman_tree2(freq)
    >>> t
    HuffmanTree(None, HuffmanTree(3, None, None), HuffmanTree(2, None, None))
    >>> freq = {2: 6, 3: 4, 7: 5, 8: 1}
    >>> t = build_huffman_tree2(freq)
    >>> t
    HuffmanTree(None, HuffmanTree(2, None, None), HuffmanTree(None, HuffmanTree(7, None, None), HuffmanTree(None, HuffmanTree(8, None, None), HuffmanTree(3, None, None))))
    >>> freq = {2: 6, 3: 4, 7: 5, 8: 1, 9: 1}
    >>> t = build_huffman_tree2(freq)
    >>> t
    HuffmanTree(None, HuffmanTree(None, HuffmanTree(None, HuffmanTree(8, None, None), HuffmanTree(9, None, None)), HuffmanTree(3, None, None)), HuffmanTree(None, HuffmanTree(7, None, None), HuffmanTree(2, None, None)))
    """
    freq_dict_copy = dict(freq_dict)
    if len(freq_dict_copy) == 1:
        if list(freq_dict.keys())[0] == 255:
            new_key = 254
        else:
            new_key = list(freq_dict.keys())[0] + 1
        freq_dict_copy[new_key] = 0
    node_freq = [(freq_dict_copy[key], HuffmanTree(key)) for key in freq_dict_copy]
    while len(node_freq) > 1:
        node_freq.sort()
        node_freq_left, node_freq_right = node_freq[0], node_freq[1]
        node = HuffmanTree(None, node_freq_left[1], node_freq_right[1])
        node_freq = node_freq[2:] + [(node_freq_left[0] + node_freq_right[0], node)]
    return node_freq[0][1]
