import argparse
from backtracking import *


def initialize_variables(size):
    variables = set()
    row_list = []
    col_list = [[] for _ in range(size)]  # Initialize the columns

    # Create the variables, assign them to rows and columns
    for i in range(size):
        row = [Variable((i, j), {'.', 'S', '<', '>', '^', 'v', 'M'}) for j in range(size)]
        for j, variable in enumerate(row):
            variables.add(variable)
            col_list[j].append(variable)  # Add to the respective column
        row_list.append(row)  # Add the row to the row_list

    return variables, row_list, col_list


def generate_constraints(v1, v2, relationship, size):
    """
    Generate constraints for Battleship puzzle solver.

    Args:
        v1, v2: Variable objects representing related cells
        relationship: String indicating the relationship ('horizontal', 'vertical', or 'diagonal')
        size: Size of the puzzle grid

    Returns:
        List of valid assignments for the two variables
    """
    i, j = v1.name()

    # For diagonal constraints, we only allow assignments where at least one cell is empty
    if relationship == 'diagonal':
        return [{v1: '.', v2: val} for val in '.<>^vSM'] + \
            [{v1: val, v2: '.'} for val in '.<>^vSM'] + \
            [{v1: '.', v2: '.'}]

    # Base constraints that are always valid regardless of direction
    constraints = [
        {v1: '.', v2: '.'},
        {v1: '.', v2: 'S'},
        {v1: 'S', v2: '.'}
    ]

    is_horizontal = relationship == 'horizontal'

    # Direction-specific ship connection constraint
    constraints.append({v1: '<', v2: '>'} if is_horizontal else {v1: '^', v2: 'v'})

    # Define directional symbols based on orientation
    if is_horizontal:
        primary_dir = ('<', '>')  # Left/Right symbols
        secondary_dir = ('^', 'v')  # Up/Down symbols
        primary_idx = j  # Use column index for horizontal
        max_idx = size - 2 if is_horizontal else size - 1
    else:
        primary_dir = ('^', 'v')  # Up/Down symbols
        secondary_dir = ('<', '>')  # Left/Right symbols
        primary_idx = i  # Use row index for vertical
        max_idx = size - 2 if not is_horizontal else size - 1

    # Primary direction constraints (along the constraint direction)
    if primary_idx > 0:
        constraints.extend([
            {v1: 'M', v2: primary_dir[1]},
            {v1: primary_dir[1], v2: '.'}
        ])
    if primary_idx < max_idx:
        constraints.extend([
            {v1: primary_dir[0], v2: 'M'},
            {v1: '.', v2: primary_dir[0]}
        ])
    if 0 < primary_idx < max_idx:
        constraints.append({v1: 'M', v2: 'M'})

    # Secondary direction constraints (perpendicular to constraint direction)
    secondary_idx = j if not is_horizontal else i
    if secondary_idx > 0:
        constraints.extend([
            {v1: secondary_dir[1], v2: '.'},
            {v1: '.', v2: secondary_dir[1]}
        ])
    if secondary_idx < size - 1:
        constraints.extend([
            {v1: secondary_dir[0], v2: '.'},
            {v1: '.', v2: secondary_dir[0]}
        ])
    if 0 < secondary_idx < size - 1:
        constraints.extend([
            {v1: '.', v2: 'M'},
            {v1: 'M', v2: '.'}
        ])

    return constraints


def initialization(rowConstraints, colConstraints, rows, cols):
    def add_default_constraints(variables, constraint_set, initial, constraint_name_prefix, constraints):
        """Helper function to add default constraints when bound == 0."""
        for variable in variables:
            variable.setValue('.')
            initial[variable] = '.'
        for i, constraint in enumerate(constraints):
            constraint_set.add(NValuesConstraint(
                f'{constraint_name_prefix}_{i}_{constraints[i]}',
                set(variables),
                {'<', '>', '^', 'v', 'S', 'M'},
                constraints[i],
                constraints[i]
            ))

    def add_directional_constraints(primary_vars, relationship, size, constraints):
        """Helper function to add directional constraints."""
        for i in range(len(primary_vars) - 1):
            v1, v2 = primary_vars[i], primary_vars[i + 1]
            constraints.add(TableConstraint(
                f'{relationship}_{v1.name()}',
                {v1, v2},
                generate_constraints(v1, v2, relationship, size)
            ))

    constraints = set()
    initial = {}

    # Handle row constraints
    for i, row in enumerate(rows):
        bound = int(rowConstraints[i])
        if bound == 0:
            add_default_constraints(row, constraints, initial, 'row', rowConstraints)
        else:
            constraints.add(NValuesConstraint(
                f'row_{i}_{rowConstraints[i]}',
                set(row),
                {'<', '>', '^', 'v', 'S', 'M'},
                bound,
                bound
            ))

    # Handle column constraints
    for j, col in enumerate(cols):
        bound = int(colConstraints[j])
        if bound == 0:
            add_default_constraints(col, constraints, initial, 'col', colConstraints)
        else:
            constraints.add(NValuesConstraint(
                f'col_{j}_{colConstraints[j]}',
                set(col),
                {'<', '>', '^', 'v', 'S', 'M'},
                bound,
                bound
            ))

    # Handle horizontal constraints
    for row in rows:
        add_directional_constraints(row, 'horizontal', len(cols), constraints)

    # Handle vertical constraints
    for col in cols:
        add_directional_constraints(col, 'vertical', len(rows), constraints)

    # Handle diagonal constraints
    for i in range(len(rows) - 1):
        for j, v1 in enumerate(rows[i]):
            if j > 0:
                v2 = rows[i + 1][j - 1]
                constraints.add(TableConstraint(
                    f'diagonal_left_{v1.name()}',
                    {v1, v2},
                    generate_constraints(v1, v2, 'diagonal', len(rows))
                ))
            if j < len(cols) - 1:
                v2 = rows[i + 1][j + 1]
                constraints.add(TableConstraint(
                    f'diagonal_right_{v1.name()}',
                    {v1, v2},
                    generate_constraints(v1, v2, 'diagonal', len(rows))
                ))

    return constraints, initial


def add_starting_ships(rows, lines):
    initial = {}

    # Iterate through each variable in the row_list
    for i, row in enumerate(rows):
        for j, variable in enumerate(row):
            input = lines[i + 3][j]
            if input != '0':
                variable.setValue(input)
                initial[variable] = input  # Direct assignment

    return initial


def output_solution(filename, solution, size):
    output_file = open(filename, "w")
    grid = [['0' for _ in range(size)] for _ in range(size)]
    for i, j in solution:
        grid[i][j] = solution[(i, j)]
    for line in grid:
        output_file.write(''.join(line) + '\n')
    output_file.close()

def get_neighbours(board, i, j):
    """
    >>> get_neighbours([['.', '.', '.'], ['.', '.', '.'], ['.', '.', '.']], 1, 1)
    [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]
    """
    neighbours = []
    for x in range(i - 1, i + 2):
        for y in range(j - 1, j + 2):
            if x >= 0 and y >= 0 and x < len(board) and y < len(board[0]):
                if board[x][y] == '.' and (x, y) != (i, j):
                    neighbours.append((x, y))
    return neighbours


def fix_solution(solution, size):
    board = solution_to_board(solution, size)
    for i in range(size):
        for j in range(size):
            neighbours = get_neighbours(board, i, j)
            if len(neighbours) == 8 and board[i][j] == 'M':
                solution[(i, j)] = 'S'
            elif len(neighbours) == 7 and board[i][j] == 'M':
                if board[i+1][j] != '.':
                    solution[(i, j)] = '^'
                elif board[i-1][j] != '.':
                    solution[(i, j)] = 'v'
                elif board[i][j+1] != '.':
                    solution[(i, j)] = '<'
                elif board[i][j-1] != '.':
                    solution[(i, j)] = '>'
    return solution

def check_initial_ships(initialboard, board, size):
    """
    >>> check_initial_ships([\
    ["0", "0", "0", "0", "0", "0", ">", "0", "0", "0"],\
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],\
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],\
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],\
    ["0", "0", "0", "0", "0", "0", "0", "M", "0", "0"],\
    ["S", "0", "0", "0", "0", "0", "0", "0", "0", "0"],\
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],\
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],\
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],\
    ["v", "0", "0", "0", "0", "0", "0", "0", "0", "0"]\
], \
    [ \
    [".", ".", "<", ">", ".", "<", ">", ".", ".", "."],\
    [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],\
    [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],\
    [".", "<", "M", "M", "M", ">", ".", "^", ".", "."],\
    [".", ".", ".", ".", ".", ".", ".", "v", ".", "."],\
    ["S", ".", ".", ".", ".", ".", ".", ".", ".", "."],\
    [".", ".", "S", ".", ".", ".", ".", "S", ".", "v"],\
    [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],\
    ["^", ".", "<", "M", "M", ">", ".", "<", "M", ">"],\
    ["v", ".", ".", ".", ".", ".", ".", ".", ".", "."]\
], 10)
    False
    """
    for i in range(size):
        for j in range(size):
            if initialboard[i][j] != '.' and initialboard[i][j] != '0':
                if initialboard[i][j] != board[i][j]:
                    return False
    return True



def validate_solution(candidate_solutions, required_ships, initialboard, size):
    for candidate in candidate_solutions:
        candidate = fix_solution(candidate, size)
        board = solution_to_board(candidate, size)
        if not check_initial_ships(initialboard, board, size):
            continue
        ships = {'S': 0, 'D': 0, 'CR': 0, 'B': 0, 'CA': 0}
        for i in range(size):
            for j in range(size):
                if board[i][j] == 'S':
                    ships['S'] += 1
                elif board[i][j] == '^':
                    count = 2
                    for k in range(i + 1, size):
                        if board[k][j] == 'M':
                            count += 1
                        else:
                            break
                    if count == 2:
                        ships['D'] += 1
                    elif count == 3:
                        ships['CR'] += 1
                    elif count == 4:
                        ships['B'] += 1
                    elif count == 5:
                        ships['CA'] += 1
                elif board[i][j] == '<':
                    count = 2
                    for k in range(j + 1, size):
                        if board[i][k] == 'M':
                            count += 1
                        else:
                            break
                    if count == 2:
                        ships['D'] += 1
                    elif count == 3:
                        ships['CR'] += 1
                    elif count == 4:
                        ships['B'] += 1
                    elif count == 5:
                        ships['CA'] += 1
        if ships == required_ships:
            return candidate

def solution_to_board(solution, size):
    board = [['0' for _ in range(size)] for _ in range(size)]
    for i, j in solution:
        board[i][j] = solution[(i, j)]
    return board

def output_solutions(filename, solutions, size):
    output_file = open(filename, "w")
    for solution in solutions:
        grid = [['0' for _ in range(size)] for _ in range(size)]
        for i, j in solution:
            grid[i][j] = solution[(i, j)]
        for line in grid:
            output_file.write(''.join(line) + '\n')
        output_file.write('\n')
    output_file.close()


if __name__ == '__main__':
    import argparse
    import time

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

    start = time.time()

    # Read input file and get puzzle parameters
    with open(args.inputfile, 'r') as f:
        lines = f.readlines()

    size = len(lines[0].strip())
    row_constraints = lines[0].strip()
    col_constraints = lines[1].strip()
    ship_counts = list(map(int, lines[2].strip()))

    # Create initial board state
    initialboard = [list(lines[i].strip()) for i in range(3, size + 3)]

    # Initialize puzzle components
    variables, rows, cols = initialize_variables(size)
    constraints, initial = initialization(row_constraints, col_constraints, rows, cols)
    initial.update(add_starting_ships(rows, lines))

    # Set up ship constraints
    ship_constraints = {
        'S': ship_counts[0],
        'D': ship_counts[1],
        'CR': ship_counts[2],
        'B': ship_counts[3],
        'CA': ship_counts[4]
    }

    # Solve puzzle
    csp = CSP('battleship', variables, constraints)
    solution = validate_solution(solve_csp(csp, initial), ship_constraints, initialboard, size)
    output_solution(args.outputfile, solution, size)

    print(f"Time: {time.time() - start:.3f}s")