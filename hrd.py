import argparse
import sys
import heapq

#====================================================================================

char_single = '2'

class Piece:
    """
    This represents a piece on the Hua Rong Dao puzzle.
    """

    def __init__(self, is_2_by_2, is_single, coord_x, coord_y, orientation):
        """
        :param is_2_by_2: True if the piece is a 2x2 piece and False otherwise.
        :type is_2_by_2: bool
        :param is_single: True if this piece is a 1x1 piece and False otherwise.
        :type is_single: bool
        :param coord_x: The x coordinate of the top left corner of the piece.
        :type coord_x: int
        :param coord_y: The y coordinate of the top left corner of the piece.
        :type coord_y: int
        :param orientation: The orientation of the piece (one of 'h' or 'v') 
            if the piece is a 1x2 piece. Otherwise, this is None
        :type orientation: str
        """

        self.is_2_by_2 = is_2_by_2
        self.is_single = is_single
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.orientation = orientation

    def __str__(self):
        if self.is_2_by_2:
            return '2x2 piece at ({}, {})'.format(self.coord_x, self.coord_y)
        elif self.is_single:
            return '1x1 piece at ({}, {})'.format(self.coord_x, self.coord_y)
        else:
            return '1x2 piece at ({}, {}) with orientation {}'.format(self.coord_x, self.coord_y, self.orientation)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__str__())

    def set_coords(self, coord_x, coord_y):
        """
        Move the piece to the new coordinates. 

        :param coord: The new coordinates after moving.
        :type coord: int
        """

        self.coord_x = coord_x
        self.coord_y = coord_y

class Board:
    """
    Board class for setting up the playing board.
    """

    def __init__(self, height, pieces):
        """
        :param pieces: The list of Pieces
        :type pieces: List[Piece]
        """

        self.width = 4
        self.height = height
        self.pieces = pieces

        # self.grid is a 2-d (size * size) array automatically generated
        # using the information on the pieces when a board is being created.
        # A grid contains the symbol for representing the pieces on the board.
        self.grid = []
        self.__construct_grid()

        self.blanks = []

    def __hash__(self):
        return hash(tuple(tuple(row) for row in self.grid))

    def __str__(self):
        return '{}'.format(self.grid)

    def __repr__(self):
        return self.__str__()

    # customized eq for object comparison.
    def __eq__(self, other):
        if isinstance(other, Board):
            return self.grid == other.grid
        return False


    def __construct_grid(self):
        """
        Called in __init__ to set up a 2-d grid based on the piece location information.

        """

        for i in range(self.height):
            line = []
            for j in range(self.width):
                line.append('.')
            self.grid.append(line)

        for piece in self.pieces:
            if piece.is_2_by_2:
                self.grid[piece.coord_y][piece.coord_x] = '1'
                self.grid[piece.coord_y][piece.coord_x + 1] = '1'
                self.grid[piece.coord_y + 1][piece.coord_x] = '1'
                self.grid[piece.coord_y + 1][piece.coord_x + 1] = '1'
            elif piece.is_single:
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                if piece.orientation == 'h':
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'
      
    def display(self):
        """
        Print out the current board.

        """
        for i, line in enumerate(self.grid):
            for ch in line:
                print(ch, end='')
            print()
        

class State:
    """
    State class wrapping a Board with some extra current state information.
    Note that State and Board are different. Board has the locations of the pieces. 
    State has a Board and some extra information that is relevant to the search: 
    heuristic function, f value, current depth and parent.
    """

    def __init__(self, board, hfn, f, depth, parent=None):
        """
        :param board: The board of the state.
        :type board: Board
        :param hfn: The heuristic function.
        :type hfn: Optional[Heuristic]
        :param f: The f value of current state.
        :type f: int
        :param depth: The depth of current state in the search tree.
        :type depth: int
        :param parent: The parent of current state.
        :type parent: Optional[State]
        """
        self.board = board
        self.hfn = hfn
        self.f = f
        self.depth = depth
        self.parent = parent

    def __hash__(self):
        return hash(self.board)

    def __eq__(self, other):
        if isinstance(other, State):
            return self.board == other.board
        return False

    def __lt__(self, other):
        return self.f < other.f

    def __str__(self):
        return self.board.__str__()

    def __repr__(self):
        return self.__str__()


def copypiece(piece):
    """
    Perform a deepcopy of the given piece.
    Return the copied piece.

    Do not use copy import.
    """
    new_piece = Piece(piece.is_2_by_2, piece.is_single, piece.coord_x, piece.coord_y, piece.orientation)
    return new_piece


def copystate(state):
    """
    Perform a deepcopy of the given state.
    Return the copied state.

    Do not use copy import.
    """
    #copy pieces
    new_pieces = []
    for piece in state.board.pieces:
        new_piece = Piece(piece.is_2_by_2, piece.is_single, piece.coord_x, piece.coord_y, piece.orientation)
        new_pieces.append(new_piece)
    #copy board
    new_board = Board(state.board.height, new_pieces)
    new_board.grid = [row[:] for row in state.board.grid]
    #copy state
    new_state = State(new_board, state.hfn, state.f, state.depth, state.parent)
    return new_state




def move_piece(board, piece, direction):
    """
    Move the piece in the given direction.

    >>> board, goal_board = read_from_file("easy1.txt")
    >>> piece = board.pieces[9]
    >>> move_piece(board, piece, 'right')
    False
    >>> move_piece(board, piece, 'left')
    True
    >>> board, goal_board = read_from_file("easy1.txt")
    >>> piece = board.pieces[0]
    >>> move_piece(board, piece, 'up')
    False
    >>> piece = board.pieces[8]
    >>> move_piece(board, piece, 'left')
    False
    >>> piece.coord_x
    0
    >>> piece.coord_y
    3
    >>> move_piece(board, piece, 'right')
    True
    >>> board.grid[3][2]
    '1'
    >>> board.grid[3][0]
    '.'
    >>> piece.coord_x
    1
    >>> piece.coord_y
    3
    """
    if piece.is_2_by_2:
        if direction == 'up':
            if piece.coord_y - 1 >= 0 and board.grid[piece.coord_y - 1][piece.coord_x] == '.' and board.grid[piece.coord_y - 1][piece.coord_x + 1] == '.':
                board.grid[piece.coord_y][piece.coord_x] = '.'
                board.grid[piece.coord_y][piece.coord_x + 1] = '.'
                board.grid[piece.coord_y + 1][piece.coord_x] = '.'
                board.grid[piece.coord_y + 1][piece.coord_x + 1] = '.'
                piece.set_coords(piece.coord_x, piece.coord_y - 1)
                board.grid[piece.coord_y][piece.coord_x] = '1'
                board.grid[piece.coord_y][piece.coord_x + 1] = '1'
                board.grid[piece.coord_y + 1][piece.coord_x] = '1'
                board.grid[piece.coord_y + 1][piece.coord_x + 1] = '1'
            else:
                return False
        elif direction == 'down':
            if piece.coord_y + 2 < board.height and board.grid[piece.coord_y + 2][piece.coord_x] == '.' and board.grid[piece.coord_y + 2][piece.coord_x + 1] == '.':
                board.grid[piece.coord_y][piece.coord_x] = '.'
                board.grid[piece.coord_y][piece.coord_x + 1] = '.'
                board.grid[piece.coord_y + 1][piece.coord_x] = '.'
                board.grid[piece.coord_y + 1][piece.coord_x + 1] = '.'
                piece.set_coords(piece.coord_x, piece.coord_y + 1)
                board.grid[piece.coord_y][piece.coord_x] = '1'
                board.grid[piece.coord_y][piece.coord_x + 1] = '1'
                board.grid[piece.coord_y + 1][piece.coord_x] = '1'
                board.grid[piece.coord_y + 1][piece.coord_x + 1] = '1'
            else:
                return False
        elif direction == 'left':
            if piece.coord_x - 1 >= 0 and board.grid[piece.coord_y][piece.coord_x - 1] == '.' and board.grid[piece.coord_y + 1][piece.coord_x - 1] == '.':
                board.grid[piece.coord_y][piece.coord_x] = '.'
                board.grid[piece.coord_y][piece.coord_x + 1] = '.'
                board.grid[piece.coord_y + 1][piece.coord_x] = '.'
                board.grid[piece.coord_y + 1][piece.coord_x + 1] = '.'
                piece.set_coords(piece.coord_x - 1, piece.coord_y)
                board.grid[piece.coord_y][piece.coord_x] = '1'
                board.grid[piece.coord_y][piece.coord_x + 1] = '1'
                board.grid[piece.coord_y + 1][piece.coord_x] = '1'
                board.grid[piece.coord_y + 1][piece.coord_x + 1] = '1'
            else:
                return False
        elif direction == 'right':
            if piece.coord_x + 2 < board.width and board.grid[piece.coord_y][piece.coord_x + 2] == '.' and board.grid[piece.coord_y + 1][piece.coord_x + 2] == '.':
                board.grid[piece.coord_y][piece.coord_x] = '.'
                board.grid[piece.coord_y][piece.coord_x + 1] = '.'
                board.grid[piece.coord_y + 1][piece.coord_x] = '.'
                board.grid[piece.coord_y + 1][piece.coord_x + 1] = '.'
                piece.set_coords(piece.coord_x + 1, piece.coord_y)
                board.grid[piece.coord_y][piece.coord_x] = '1'
                board.grid[piece.coord_y][piece.coord_x + 1] = '1'
                board.grid[piece.coord_y + 1][piece.coord_x] = '1'
                board.grid[piece.coord_y + 1][piece.coord_x + 1] = '1'
            else:
                return False
    elif piece.is_single:
        if direction == 'up':
            if piece.coord_y - 1 >= 0 and board.grid[piece.coord_y - 1][piece.coord_x] == '.':
                board.grid[piece.coord_y][piece.coord_x] = '.'
                piece.set_coords(piece.coord_x, piece.coord_y - 1)
                board.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                return False
        elif direction == 'down':
            if piece.coord_y + 1 < board.height and board.grid[piece.coord_y + 1][piece.coord_x] == '.':
                board.grid[piece.coord_y][piece.coord_x] = '.'
                piece.set_coords(piece.coord_x, piece.coord_y + 1)
                board.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                return False
        elif direction == 'left':
            if piece.coord_x - 1 >= 0 and board.grid[piece.coord_y][piece.coord_x - 1] == '.':
                board.grid[piece.coord_y][piece.coord_x] = '.'
                piece.set_coords(piece.coord_x - 1, piece.coord_y)
                board.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                return False
        elif direction == 'right':
            if piece.coord_x + 1 < board.width and board.grid[piece.coord_y][piece.coord_x + 1] == '.':
                board.grid[piece.coord_y][piece.coord_x] = '.'
                piece.set_coords(piece.coord_x + 1, piece.coord_y)
                board.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                return False
    else:
        if piece.orientation == 'h':
            if direction == 'left':
                if piece.coord_x - 1 >= 0 and board.grid[piece.coord_y][piece.coord_x - 1] == '.':
                    board.grid[piece.coord_y][piece.coord_x + 1] = '.'
                    piece.set_coords(piece.coord_x - 1, piece.coord_y)
                    board.grid[piece.coord_y][piece.coord_x] = '<'
                    board.grid[piece.coord_y][piece.coord_x + 1] = '>'
                else:
                    return False
            elif direction == 'right':
                if piece.coord_x + 2 < board.width and board.grid[piece.coord_y][piece.coord_x + 2] == '.':
                    board.grid[piece.coord_y][piece.coord_x] = '.'
                    piece.set_coords(piece.coord_x + 1, piece.coord_y)
                    board.grid[piece.coord_y][piece.coord_x] = '<'
                    board.grid[piece.coord_y][piece.coord_x + 1] = '>'
                else:
                    return False
            elif direction == 'up':
                if piece.coord_y - 1 >= 0 and board.grid[piece.coord_y - 1][piece.coord_x] == '.' and board.grid[piece.coord_y - 1][piece.coord_x + 1] == '.':
                    board.grid[piece.coord_y][piece.coord_x] = '.'
                    board.grid[piece.coord_y][piece.coord_x + 1] = '.'
                    piece.set_coords(piece.coord_x, piece.coord_y - 1)
                    board.grid[piece.coord_y][piece.coord_x] = '<'
                    board.grid[piece.coord_y][piece.coord_x + 1] = '>'
                else:
                    return False
            elif direction == 'down':
                if piece.coord_y + 1 < board.height and board.grid[piece.coord_y + 1][piece.coord_x] == '.' and board.grid[piece.coord_y + 1][piece.coord_x + 1] == '.':
                    board.grid[piece.coord_y][piece.coord_x] = '.'
                    board.grid[piece.coord_y][piece.coord_x + 1] = '.'
                    piece.set_coords(piece.coord_x, piece.coord_y + 1)
                    board.grid[piece.coord_y][piece.coord_x] = '<'
                    board.grid[piece.coord_y][piece.coord_x + 1] = '>'
                else:
                    return False
        else:
            if direction == 'up':
                if piece.coord_y - 1 >= 0 and board.grid[piece.coord_y - 1][piece.coord_x] == '.':
                    board.grid[piece.coord_y + 1][piece.coord_x] = '.'
                    piece.set_coords(piece.coord_x, piece.coord_y - 1)
                    board.grid[piece.coord_y][piece.coord_x] = '^'
                    board.grid[piece.coord_y + 1][piece.coord_x] = 'v'
                else:
                    return False
            elif direction == 'down':
                if piece.coord_y + 2 < board.height and board.grid[piece.coord_y + 2][piece.coord_x] == '.':
                    board.grid[piece.coord_y][piece.coord_x] = '.'
                    piece.set_coords(piece.coord_x, piece.coord_y + 1)
                    board.grid[piece.coord_y][piece.coord_x] = '^'
                    board.grid[piece.coord_y + 1][piece.coord_x] = 'v'
                else:
                    return False
            elif direction == 'left':
                if piece.coord_x - 1 >= 0 and board.grid[piece.coord_y][piece.coord_x - 1] == '.' and board.grid[piece.coord_y + 1][piece.coord_x - 1] == '.':
                    board.grid[piece.coord_y][piece.coord_x] = '.'
                    board.grid[piece.coord_y + 1][piece.coord_x] = '.'
                    piece.set_coords(piece.coord_x - 1, piece.coord_y)
                    board.grid[piece.coord_y][piece.coord_x] = '^'
                    board.grid[piece.coord_y+1][piece.coord_x] = 'v'
                else:
                    return False
            elif direction == 'right':
                if piece.coord_x + 1 < board.width and board.grid[piece.coord_y][piece.coord_x + 1] == '.' and board.grid[piece.coord_y + 1][piece.coord_x + 1] == '.':
                    board.grid[piece.coord_y][piece.coord_x] = '.'
                    board.grid[piece.coord_y + 1][piece.coord_x] = '.'
                    piece.set_coords(piece.coord_x + 1, piece.coord_y)
                    board.grid[piece.coord_y][piece.coord_x] = '^'
                    board.grid[piece.coord_y+1][piece.coord_x] = 'v'
                else:
                    return False
    return True


def possible_states(state):
    """
    Generate all possible states from the current state.

    :param state: The current state.
    :type state: State
    :return: A list of possible states.
    :rtype: List[State]

    >>> board, goal_board = read_from_file("test.txt")
    >>> state = State(board, None, 0, 0)
    >>> new_states = possible_states(state)
    >>> len(new_states)
    3
    >>> board, goal_board = read_from_file("easy3.txt")
    >>> state = State(board, None, 0, 0)
    >>> new_states = possible_states(state)
    >>> len(new_states)
    4
    >>> board, goal_board = read_from_file("easy2.txt")
    >>> state = State(board, None, 0, 0)
    >>> new_states = possible_states(state)
    >>> len(new_states)
    3
    >>> new_states = possible_states(new_states.pop())
    >>> board, goal_board = read_from_file("easy1.txt")
    >>> state = State(board, None, 0, 0)
    >>> new_states = possible_states(state)
    >>> len(new_states)
    2
    """
    def add_new_states(piece, direction):
        new_state = copystate(state)
        new_piece = copypiece(piece)
        while move_piece(new_state.board, new_piece, direction):
            new_state.parent = state
            new_state.board.pieces[i] = new_piece
            new_states.add(copystate(new_state))

    new_states = set()
    for i, piece in enumerate(state.board.pieces):
        for direction in ['up', 'down', 'left', 'right']:
            add_new_states(piece, direction)
    return new_states


def heuristic(state, goal_board):
    """
    Calculate the heuristic value of the current state.

    :param state: The current state.
    :type state: State
    :param goal_board: The goal board.
    :type goal_board: Board
    :return: The heuristic value of the current state.
    :rtype: int

    >>> board, goal_board = read_from_file("easy1.txt")
    >>> state = State(board, None, 0, 0)
    >>> goal_board = State(goal_board, None, 0, 0)
    >>> heuristic(state, goal_board)
    4
    """
    h = 0
    for i in range(state.board.height):
        for j in range(state.board.width):
            if state.board.grid[i][j] != goal_board.board.grid[i][j]:
                h += 1
    return h

def manhatten_distance(state, goal_board):
    """
    Calculate the manhatten distance of the current state.

    :param state: The current state.
    :type state: State
    :param goal_board: The goal board.
    :type goal_board: Board
    :return: The manhatten distance of the current state.
    :rtype: int

    >>> board, goal_board = read_from_file("easy1.txt")
    >>> state = State(board, None, 0, 0)
    >>> goal_board = State(goal_board, None, 0, 0)
    >>> manhatten_distance(state, goal_board)
    3
    """
    distance = 0
    for i in range(state.board.height):
        for j in range(state.board.width):
            if state.board.grid[i][j] != '.' and state.board.grid[i][j] != goal_board.board.grid[i][j]:
                goal_x, goal_y = [(x, y) for x in range(goal_board.board.height) for y in range(goal_board.board.width) if goal_board.board.grid[x][y] == state.board.grid[i][j]][0]
                distance += abs(goal_x - i) + abs(goal_y - j)
    return distance


def astar_search(initial_state, goal_board):
    """
    A* search algorithm.

    Return the list of moves to reach the goal state from the initial state.

    :param initial_state: The initial state.
    :type initial_state: State
    :param goal_board: The goal board.
    :type goal_board: Board
    :return: The solution state.
    :rtype: State

    >>> board, goal_board = read_from_file("easy2.txt")
    >>> initial_state = State(board, None, 0, 0)
    >>> goal_board = State(goal_board, None, 0, 0)
    >>> solution = astar_search(initial_state, goal_board)
    >>> solution
    [[['2', '^', '2', '2'], ['2', 'v', '<', '>'], ['2', '2', '2', '2'], ['.', '1', '1', '^'], ['.', '1', '1', 'v']], [['2', '^', '2', '2'], ['2', 'v', '<', '>'], ['.', '2', '2', '2'], ['.', '1', '1', '^'], ['2', '1', '1', 'v']], [['2', '^', '2', '2'], ['.', 'v', '<', '>'], ['2', '2', '2', '2'], ['.', '1', '1', '^'], ['2', '1', '1', 'v']]]
    >>> board, goal_board = read_from_file("easy1.txt")
    >>> initial_state = State(board, None, 0, 0)
    >>> goal_board = State(goal_board, None, 0, 0)
    >>> solution = astar_search(initial_state, goal_board)
    >>> solution
    [[['2', '^', '2', '2'], ['2', 'v', '<', '>'], ['<', '>', '<', '>'], ['1', '1', '.', '^'], ['1', '1', '.', 'v']], [['2', '^', '2', '2'], ['2', 'v', '<', '>'], ['<', '>', '<', '>'], ['.', '1', '1', '^'], ['.', '1', '1', 'v']]]
    """
    open_list = []
    closed_list = set()
    heapq.heappush(open_list, (initial_state.f, initial_state))
    while open_list:
        f, current_state = heapq.heappop(open_list)
        if current_state.board == goal_board.board:
            # Create a list to store the states from the goal state back to the initial state
            path = []
            while current_state is not None:
                path.append(current_state.board.grid)
                current_state = current_state.parent
            # Reverse the list and print it out
            path.reverse()
            return path
        closed_list.add(current_state)
        new_states = possible_states(current_state)
        for new_state in new_states:
            if new_state not in closed_list:
                new_state.f = manhatten_distance(new_state, goal_board) + new_state.depth
                heapq.heappush(open_list, (new_state.f, new_state))
    return None


def dfs_search(initial_state, goal_board):
    """
    Depth-first search algorithm.
    Return the optimal list of moves to reach the goal state from the initial state.

    :param initial_state: The initial state.
    :type initial_state: State
    :param goal_board: The goal board.
    :type goal_board: Board
    :return: The solution state.
    :rtype: State
    """
    open_list = []
    closed_list = set()
    open_list.append(initial_state)
    best_solution = None

    while open_list:
        current_state = open_list.pop()
        if current_state.board == goal_board.board:
            path = []
            while current_state is not None:
                path.append(current_state.board.grid)
                current_state = current_state.parent
            path.reverse()
            if not best_solution or len(path) < len(best_solution):
                best_solution = path
            continue

        closed_list.add(current_state)
        new_states = possible_states(current_state)
        for new_state in new_states:
            if new_state not in closed_list:
                new_state.parent = current_state
                open_list.append(new_state)

    return best_solution


def bfs_search(initial_state, goal_board):
    """
    Breadth-first search algorithm.
    Return the optimal list of moves to reach the goal state from the initial state.

    :param initial_state: The initial state.
    :type initial_state: State
    :param goal_board: The goal board.
    :type goal_board: Board
    :return: The solution state.
    :rtype: State

    >>> board, goal_board = read_from_file("med1.txt")
    >>> initial_state = State(board, None, 0, 0)
    >>> goal_board = State(goal_board, None, 0, 0)
    >>> solution = bfs_search(initial_state, goal_board)
    >>> len(solution)
    75
    """
    open_list = []
    closed_list = set()
    open_list.append(initial_state)
    best_solution = None

    while open_list:
        current_state = open_list.pop(0)
        if current_state.board == goal_board.board:
            path = []
            while current_state is not None:
                path.append(current_state.board.grid)
                current_state = current_state.parent
            path.reverse()
            if not best_solution or len(path) < len(best_solution):
                best_solution = path
            continue

        closed_list.add(current_state)
        new_states = possible_states(current_state)
        for new_state in new_states:
            if new_state not in closed_list:
                new_state.parent = current_state
                open_list.append(new_state)

    return best_solution



def read_from_file(filename):
    """
    Load initial board from a given file.

    :param filename: The name of the given file.
    :type filename: str
    :return: A loaded board
    :rtype: Board
    """

    puzzle_file = open(filename, "r")

    line_index = 0
    pieces = []
    final_pieces = []
    final = False
    found_2by2 = False
    finalfound_2by2 = False
    height_ = 0

    for line in puzzle_file:
        height_ += 1
        if line == '\n':
            if not final:
                height_ = 0
                final = True
                line_index = 0
            continue
        if not final: #initial board
            for x, ch in enumerate(line):
                if ch == '^': # found vertical piece
                    pieces.append(Piece(False, False, x, line_index, 'v'))
                elif ch == '<': # found horizontal piece
                    pieces.append(Piece(False, False, x, line_index, 'h'))
                elif ch == char_single:
                    pieces.append(Piece(False, True, x, line_index, None))
                elif ch == '1':
                    if found_2by2 == False:
                        pieces.append(Piece(True, False, x, line_index, None))
                        found_2by2 = True
        else: #goal board
            for x, ch in enumerate(line):
                if ch == '^': # found vertical piece
                    final_pieces.append(Piece(False, False, x, line_index, 'v'))
                elif ch == '<': # found horizontal piece
                    final_pieces.append(Piece(False, False, x, line_index, 'h'))
                elif ch == char_single:
                    final_pieces.append(Piece(False, True, x, line_index, None))
                elif ch == '1':
                    if finalfound_2by2 == False:
                        final_pieces.append(Piece(True, False, x, line_index, None))
                        finalfound_2by2 = True
        line_index += 1
        
    puzzle_file.close()
    board = Board(height_, pieces)
    goal_board = Board(height_, final_pieces)
    return board, goal_board


def grid_to_string(grid):
    string = ""
    for i, line in enumerate(grid):
        for ch in line:
            string += ch
        string += "\n"
    return string


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
    parser.add_argument(
        "--algo",
        type=str,
        required=True,
        choices=['astar', 'dfs'],
        help="The searching algorithm."
    )
    args = parser.parse_args()

    # read the board from the file
    board, goal_board = read_from_file(args.inputfile)
    initial_state = State(board, None, 0, 0)
    goal_board = State(goal_board, None, 0, 0)

    if args.algo == 'astar':
        solution = astar_search(initial_state, goal_board)
    else:
        solution = dfs_search(initial_state, goal_board)

    with open(args.outputfile, "w") as output_file:
        for grid in solution:
            output_file.write(grid_to_string(grid))
            output_file.write("\n")
