import argparse
import copy
import sys
import time

cache = {} # you can use this to implement state caching

class State:
    # This class is used to represent a state.
    # board : a list of lists that represents the 8*8 board
    def __init__(self, board):
        self.board = board
        self.red_pieces, self.black_pieces = self.get_pieces()
        self.pieces = {**self.red_pieces, **self.black_pieces}
        self.width = 8
        self.height = 8

    def display(self):
        for i in self.board:
            for j in i:
                print(j, end="")
            print("")
        print("")

    def __eq__(self, other):
        return self.board == other.board

    def __hash__(self):
        return hash(str(self.board))

    def __str__(self):
        return str(self.board)

    def check_end(self):
        """
        Check if the game has ended

        >>> board = [['.', 'r', '.', 'r', '.', 'r', '.', 'r'], ['r', '.', 'r', '.', 'r', '.', 'r', '.'], ['.', 'r', '.', 'r', '.', 'r', '.', 'r'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['b', '.', 'b', '.', 'b', '.', 'b', '.'], ['.', 'b', '.', 'b', '.', 'b', '.', 'b'], ['b', '.', 'b', '.', 'b', '.', 'b', '.']]
        >>> state = State(board)
        >>> state.check_end()
        True

        >>> board = [['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', 'b', '.', '.', '.', '.', '.', '.'], ['B', '.', 'R', '.', '.', '.', '.', '.']]
        >>> state = State(board)
        >>> state.check_end()
        True

        >>> board = [['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', 'b', '.', '.', '.', '.', '.', '.'], ['B', '.', '.', '.', '.', '.', '.', '.']]
        >>> state = State(board)
        >>> state.check_end()
        True

        >>> board = [['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', 'r', '.', '.', '.', '.'], ['.', 'b', '.', '.', '.', '.', '.', '.'], ['B', '.', '.', '.', '.', '.', '.', '.']]
        >>> state = State(board)
        >>> state.check_end()
        False

        :return:
        """
        if not self.red_pieces or not self.black_pieces:
            return True

        opponent_color = get_opp_char('r' if self.red_pieces else 'b')
        opponent_moves = get_possible_moves(self, opponent_color)
        if not opponent_moves:
            return True

        return False


    def get_pieces(self):
        red_pieces = {}
        black_pieces = {}
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                piece = self.board[i][j]
                if piece in 'rR':
                    red_pieces[(i, j)] = piece
                elif piece in 'bB':
                    black_pieces[(i, j)] = piece

        return red_pieces, black_pieces

    def copy_board(self):
        return [row[:] for row in self.board]


def check_jumps(board, pieces, player, a, b, chain_num):
    def perform_jump(board, pieces, player, a, b, new_a, new_b, chain_num):
        new_board = copy_board(board)
        new_pieces = pieces.copy()
        new_board[a][b], new_board[(a + new_a) // 2][(b + new_b) // 2] = '.', '.'
        new_board[new_a][new_b] = player.upper() if (player == 'b' and new_a == 7) or (
                    player == 'r' and new_a == 0) else player
        new_pieces.pop((a, b))
        if ((a + new_a) // 2, (b + new_b) // 2) in new_pieces:
            new_pieces.pop(((a + new_a) // 2, (b + new_b) // 2))
        new_pieces[(new_a, new_b)] = new_board[new_a][new_b]
        chain_checked_board = check_jumps(new_board, new_pieces, player, new_a, new_b, chain_num + 1)
        return chain_checked_board if chain_checked_board else [State(new_board)]

    result = []
    directions = {
        'b': [(1, 1), (1, -1)],
        'r': [(-1, 1), (-1, -1)],
        'B': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
        'R': [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    }

    for di, dj in directions[player]:
        new_i, new_j = a + 2 * di, b + 2 * dj
        if 0 <= new_i < 8 and 0 <= new_j < 8 and board[new_i][new_j] == '.' and (a + di, b + dj) in pieces and check_opponent(player, pieces[(a + di, b + dj)]):
            result += perform_jump(board, pieces, player, a, b, new_i, new_j, chain_num)

    if not result and chain_num >= 1:
        result = [State(board)]

    return result


def copy_board(board):
    return [row[:] for row in board]


def get_possible_moves(state, player):
    """
    >>> board = [['.', 'r', '.', 'r', '.', 'r', '.', 'r'], ['r', '.', 'r', '.', 'r', '.', 'r', '.'], ['.', 'r', '.', 'r', '.', 'r', '.', 'r'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'], ['b', '.', 'b', '.', 'b', '.', 'b', '.'], ['.', 'b', '.', 'b', '.', 'b', '.', 'b'], ['b', '.', 'b', '.', 'b', '.', 'b', '.']]
    >>> state = State(board)
    >>> get_possible_moves(state, 'b')

    :param state:
    :param player:
    :return:
    """
    def add_move(moves, cur_board, i, j, new_i, new_j, player):
        suc_board = copy_board(cur_board)
        suc_board[i][j] = '.'
        if (player == 'b' and new_i == 7) or (player == 'r' and new_i == 0):
            player = player.upper()
        suc_board[new_i][new_j] = player
        moves.append(State(suc_board))

    cur_board = state.board
    jump_moves = []
    regular_moves = []

    pieces = state.red_pieces if player in 'rR' else state.black_pieces

    for (i, j), piece in pieces.items():
        jump_moves += check_jumps(cur_board, state.pieces, piece, i, j, 0)

    if jump_moves:
        return jump_moves

    directions = {
        'b': [(1, 1), (1, -1)],
        'r': [(-1, 1), (-1, -1)],
        'B': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
        'R': [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    }

    for (i, j), piece in pieces.items():
        for di, dj in directions[piece]:
            new_i, new_j = i + di, j + dj
            if 0 <= new_i < 8 and 0 <= new_j < 8 and cur_board[new_i][new_j] == '.':
                add_move(regular_moves, cur_board, i, j, new_i, new_j, piece)
    return regular_moves

def check_opponent(color, piece):
    if color.lower() == 'r' and piece in 'bB':
        return True
    if color.lower() == 'b' and piece in 'rR':
        return True
    return False

def get_next_turn(curr_turn):
    if curr_turn == 'r':
        return 'b'
    else:
        return 'r'

def get_opp_char(player):
    return 'r' if player in 'bB' else 'b'

def read_from_file(filename):
    f = open(filename)
    lines = f.readlines()
    board = [[str(x) for x in l.rstrip()] for l in lines]
    f.close()
    return board

def is_piece_under_threat(board, x, y, player):
    opponent = 'r' if player in 'bB' else 'b'
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dx, dy in directions:
        if 0 <= x + 2*dx < 8 and 0 <= y + 2*dy < 8:
            if board[x + dx][y + dy] in opponent and board[x + 2*dx][y + 2*dy] == '.':
                return True
    return False

def get_value(state, color, heuristic=False):
    result = 0
    for i in range(len(state.board)):
        for j in range(len(state.board[0])):
            piece = state.board[i][j]
            if piece.lower() == color:
                piece_value = 1 if piece.islower() else 2
                if heuristic:
                    if (i == 0 or i == 7 or j == 0 or j == 7):
                        piece_value += 1
                    if is_piece_under_threat(state.board, i, j, piece):
                        piece_value -= 1
                result += piece_value
    return result


def evaluate_node(state, color, depth, heuristic=False):
    if state.check_end():
        return 10000 - depth

    user_value = get_value(state, color, heuristic)
    opponent_color = get_opp_char(color)
    opponent_value = get_value(state, opponent_color, heuristic)
    return (user_value - opponent_value) - depth


def minimax_search(current_state, player_color, alpha, beta, depth_limit, is_maximizing_player, current_depth=0, use_caching=0, use_ordering=0, move_path=[]):
    best_move_state = None
    best_utility = float("-inf") if is_maximizing_player else float("inf")
    best_move_path = move_path
    possible_moves = get_possible_moves(current_state, player_color)

    if use_caching and (current_state, player_color) in cache:
        cached_value, cached_depth = cache[(current_state, player_color)]
        if cached_depth >= depth_limit and alpha < cached_value < beta:
            return cached_value, current_state, move_path

    if len(possible_moves) == 0 or current_state.check_end() or depth_limit == 0:
        return evaluate_node(current_state, player_color if is_maximizing_player else get_opp_char(player_color), current_depth, heuristic=use_ordering), current_state, move_path

    if use_ordering:
        possible_moves.sort(key=lambda x: evaluate_node(x, player_color, current_depth, heuristic=True), reverse=is_maximizing_player)

    for next_state in possible_moves:
        next_move_path = move_path + [next_state.board]
        next_utility, _, next_move_path = minimax_search(next_state, get_opp_char(player_color), alpha, beta, depth_limit - 1, not is_maximizing_player, current_depth + 1, use_caching, use_ordering, next_move_path)

        if is_maximizing_player:
            if next_utility > best_utility:
                best_move_state = next_state
                best_utility = next_utility
                best_move_path = next_move_path
            alpha = max(alpha, next_utility)
        else:
            if next_utility < best_utility:
                best_move_state = next_state
                best_utility = next_utility
                best_move_path = next_move_path
            beta = min(beta, next_utility)

        if beta <= alpha:
            break

    if use_caching:
        cache[(current_state, player_color)] = (best_utility, depth_limit)

    return best_utility, best_move_state, best_move_path


def get_best_path(state, color, limit, caching=1, ordering=1):
    path = [state.board]

    # Find optimal solution
    while state.check_end() == False:
        _, state, best_path = minimax_search(state, color, float("-inf"), float("inf"), limit, True, 0, caching, ordering)
        path.extend(best_path)
        state = State(path[-1])

        color = get_opp_char(color)
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzles."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    args = parser.parse_args()
    initial_board = read_from_file(args.inputfile)
    state = State(initial_board)
    turn = 'r'
    ctr = 10
    sys.stdout = open(args.outputfile, 'w')
    sys.stdout = sys.__stdout__

    path = get_best_path(state, turn, ctr)

    # Write the output file
    with open(args.outputfile, 'w') as f:
        for i in range(len(path)):
            for j in range(len(path[i])):
                f.write(''.join(path[i][j]))
                if j != len(path[i]) - 1:
                    f.write('\n')
            if i != len(path) - 1:
                f.write('\n\n')
