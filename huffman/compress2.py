from __future__ import annotations

import time

from huffman import HuffmanTree
from utils import *

def build_frequency_dict(text: bytes) -> dict[int, int]:
    freq_dict = {}
    for bit in text:
        freq_dict[bit] = freq_dict.get(bit, 0) + 1
    return freq_dict


def build_huffman_tree(freq_dict: dict[int, int]) -> HuffmanTree:
    if len(freq_dict) == 0:
        return HuffmanTree(None, HuffmanTree(None), HuffmanTree(None))
    freq_list = sorted([(freq_dict[sym], HuffmanTree(sym))
                        for sym in freq_dict])

    if len(freq_list) == 1:
        symbol = next(iter(freq_dict))
        if symbol == 255:
            return HuffmanTree(None, HuffmanTree(symbol - 1),
                               HuffmanTree(symbol))
        else:
            return HuffmanTree(None, HuffmanTree(symbol + 1),
                               HuffmanTree(symbol))

    while len(freq_list) > 1:
        tree1_freq, tree1 = freq_list.pop(0)
        tree2_freq, tree2 = freq_list.pop(0)

        new_tree = HuffmanTree(None, tree1, tree2)
        freq_list.append((tree1_freq + tree2_freq, new_tree))

        freq_list = sorted(freq_list)

    return freq_list[0][1] if freq_list else HuffmanTree(None)


def get_codes(tree: HuffmanTree) -> dict[int, str]:
    codes = {}
    tree_lst = [{'node': tree, 'code': ''}]

    while tree_lst:
        curr = tree_lst.pop()

        node = curr['node']
        code = curr['code']

        if node.is_leaf():
            codes[node.symbol] = code

        if node.right is not None:
            tree_lst.append({'node': node.right, 'code': code + '1'})

        if node.left is not None:
            tree_lst.append({'node': node.left, 'code': code + '0'})
    return codes


def number_nodes(tree: HuffmanTree) -> None:
    num_list = [tree]
    visited_list = [False]
    num = 0

    while num_list:
        node = num_list.pop()
        visited = visited_list.pop()

        if visited:
            if not node.is_leaf():
                node.number = num
                num += 1
        else:
            num_list.append(node)
            visited_list.append(True)
            if node.right:
                num_list.append(node.right)
                visited_list.append(False)
            if node.left:
                num_list.append(node.left)
                visited_list.append(False)


def avg_length(tree: HuffmanTree, freq_dict: dict[int, int]) -> float:
    if tree.is_leaf() or not freq_dict.values():
        return 0
    dict_codes = get_codes(tree)
    tot_freq = 0
    for key in freq_dict:
        tot_freq += len(dict_codes[key]) * freq_dict[key]
    return tot_freq / sum(freq_dict.values())


def compress_bytes(text: bytes, codes: dict[int, str]) -> bytes:
    bits = ''.join(codes[item] for item in text)

    while len(bits) % 8 != 0:  # pad with 0s
        bits += '0'

    compressed_lst = bytearray()

    for i in range(0, len(bits), 8):
        # int() with base 2 more efficient than bits_to_bytes()
        compressed_lst.append(int(bits[i:i + 8], 2))
    return bytes(compressed_lst)


def tree_to_bytes(tree: HuffmanTree) -> bytes:
    if tree.is_leaf() or not tree:
        return bytes([])

    list_of_bytes = []

    def _postordertraversal(node: HuffmanTree) -> None:
        """
        Traverse the tree in postorder and
        add the appropriate bytes to the list.

        :param node:  HuffmanTree
        :return: None
        """
        nonlocal list_of_bytes

        if node.is_leaf():
            return

        _postordertraversal(node.left)
        _postordertraversal(node.right)

        if node.left.is_leaf():
            list_of_bytes.extend([0, node.left.symbol])
        else:
            list_of_bytes.extend([1, node.left.number])

        if node.right.is_leaf():
            list_of_bytes.extend([0, node.right.symbol])
        else:
            list_of_bytes.extend([1, node.right.number])

    _postordertraversal(tree)
    if None in list_of_bytes:
        return bytes([])

    return bytes(list_of_bytes)


def compress_file(in_file: str, out_file: str) -> None:
    with open(in_file, "rb") as f1:
        text = f1.read()
    freq = build_frequency_dict(text)
    tree = build_huffman_tree(freq)
    codes = get_codes(tree)
    number_nodes(tree)
    print("Bits per symbol:", avg_length(tree, freq))
    result = (tree.num_nodes_to_bytes() + tree_to_bytes(tree)
              + int32_to_bytes(len(text)))
    result += compress_bytes(text, codes)
    with open(out_file, "wb") as f2:
        f2.write(result)


# ====================
# Functions for decompression

def generate_tree_general(t_lst: list[ReadNode],
                          root_index: int) -> HuffmanTree:
    l_t = t_lst[root_index].l_type
    r_t = t_lst[root_index].r_type

    # create the node based on the types of the left and right nodes
    left_node = HuffmanTree(t_lst[root_index].l_data) \
        if l_t == 0 else generate_tree_general(t_lst, t_lst[root_index].l_data)
    right_node = HuffmanTree(t_lst[root_index].r_data) \
        if r_t == 0 else generate_tree_general(t_lst, t_lst[root_index].r_data)

    node = HuffmanTree(None, left_node, right_node)

    # set the node number and return the node
    node.number = root_index
    return node


def generate_tree_postorder(node_lst: list[ReadNode],
                            root_index: int) -> HuffmanTree:
    tree_root = node_lst[root_index]

    if tree_root.l_type == 1:
        if tree_root.r_type == 1:
            # Both left and right nodes exist
            t_left = generate_tree_postorder(node_lst, root_index - 1)
            t_left.number = root_index - 1
            t_left_number_of_nodes = len(get_codes(t_left)) - 1
            left_tree = \
                generate_tree_postorder(node_lst,
                                        root_index - t_left_number_of_nodes - 1)
            right_tree = t_left
        else:
            # Only left node exists
            left_tree = generate_tree_postorder(node_lst, root_index - 1)
            right_tree = HuffmanTree(tree_root.r_data)

    else:
        if tree_root.r_type == 1:
            # Only right node exists
            left_tree = HuffmanTree(tree_root.l_data)
            right_tree = generate_tree_postorder(node_lst, root_index - 1)
        else:
            # No children nodes exist
            left_tree = HuffmanTree(tree_root.l_data)
            right_tree = HuffmanTree(tree_root.r_data)

    # Combine left and right trees into a single tree
    tree = HuffmanTree(None, left_tree, right_tree)
    tree.number = root_index
    return tree


def decompress_bytes(tree: HuffmanTree, text: bytes, size: int) -> bytes:
    bit_str = ''.join(byte_to_bits(byte) for byte in text)
    current_node, list_of_bytes = tree, []
    for bit in bit_str:
        if current_node.symbol is not None:
            list_of_bytes.append(current_node.symbol)
            current_node = tree
            if len(list_of_bytes) == size:
                break
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right
    else:
        if current_node.symbol is not None:
            list_of_bytes.append(current_node.symbol)
    return bytes(list_of_bytes)


def decompress_file(in_file: str, out_file: str) -> None:
    with open(in_file, "rb") as f:
        num_nodes = f.read(1)[0]
        buf = f.read(num_nodes * 4)
        node_lst = bytes_to_nodes(buf)
        # use generate_tree_general or generate_tree_postorder here
        tree = generate_tree_general(node_lst, num_nodes - 1)
        size = bytes_to_int(f.read(4))
        with open(out_file, "wb") as g:
            text = f.read()
            g.write(decompress_bytes(tree, text, size))


# ====================
# Other functions

def improve_tree(tree: HuffmanTree, freq_dict: dict[int, int]) -> None:
    # from lecture on queues and trees (level order traversal)
    sorted_freq_dict = sorted([(freq_dict[key], key) for key in freq_dict])
    tree_list = [tree]

    while tree_list:
        subtree = tree_list.pop(0)
        if subtree.is_leaf():
            subtree.symbol = sorted_freq_dict.pop()[1]
        if subtree.left is not None:
            tree_list.append(subtree.left)
        if subtree.right is not None:
            tree_list.append(subtree.right)
