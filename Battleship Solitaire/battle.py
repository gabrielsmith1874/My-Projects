import argparse
import math
from csp import *
from backtracking import *

def determine_ship_type(solution, ship_coords):
    i, j = ship_coords
    ship_coords = solution[(i, j)]

    ship_checks = {
        '^': [
            ((i + 1, j), 'v', 'd'),
            ((i + 1, j), 'M', (i + 2, j), 'v', 'c'),
            ((i + 1, j), 'M', (i + 2, j), 'M', (i + 3, j), 'v', 'b')
        ],
        '<': [
            ((i, j + 1), '>', 'd'),
            ((i, j + 1), 'M', (i, j + 2), '>', 'c'),
            ((i, j + 1), 'M', (i, j + 2), 'M', (i, j + 3), '>', 'b')
        ]
    }

    for check in ship_checks.get(ship_coords, []):
        *coords, result = check
        if all(solution.get(coord) == value for coord, value in zip(coords[::2], coords[1::2])):
            return result

    return ''

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


def initialization(rowConstraints, colConstraints, rows, cols):
    def add_default_constraints(variables, constraint_set, initial, constraint_name_prefix, constraints):
        """Helper function to add default constraints when bound == 0."""
        for variable in variables:
            variable.setValue('.')
            initial[variable] = '.'
        for i, constraint in enumerate(constraints):
            constraint_set.add(NValuesConstraint(f'{constraint_name_prefix}_{i}_{constraints[i]}', set(variables), {'<', '>', '^', 'v', 'S', 'M'}, constraints[i], constraints[i]))

    constraints = set()
    initial = {}

    # Handle row constraints
    for i, row in enumerate(rows):
        bound = int(rowConstraints[i])
        if bound == 0:
            add_default_constraints(row, constraints, initial, 'row', rowConstraints)
        else:
            constraints.add(NValuesConstraint(f'row_{i}_{rowConstraints[i]}', set(row), {'<', '>', '^', 'v', 'S', 'M'}, bound, bound))

    # Handle column constraints
    for j, col in enumerate(cols):
        bound = int(colConstraints[j])
        if bound == 0:
            add_default_constraints(col, constraints, initial, 'col', colConstraints)
        else:
            constraints.add(NValuesConstraint(f'col_{j}_{colConstraints[j]}', set(col), {'<', '>', '^', 'v', 'S', 'M'}, bound, bound))

    # Handle horizontal constraints
    for i, row in enumerate(rows):
        for j in range(len(cols) - 1):
            v1, v2 = row[j], row[j + 1]
            constraints.add(TableConstraint(f'horizontal_{v1.name()}', {v1, v2}, horizontal_constraints(v1, v2, len(cols))))

    # Handle vertical constraints
    for j, col in enumerate(cols):
        for i in range(len(rows) - 1):
            v1, v2 = col[i], col[i + 1]
            constraints.add(TableConstraint(f'vertical_{v1.name()}', {v1, v2}, vertical_constraints(v1, v2, len(rows))))

    # Handle diagonal constraints
    for i in range(len(rows) - 1):
        for j, v1 in enumerate(rows[i]):
            if j > 0:
                v2 = rows[i + 1][j - 1]
                constraints.add(OrConstraint(f'diagonal_left_{v1.name()}', {v1, v2}, '.'))
            if j < len(cols) - 1:
                v2 = rows[i + 1][j + 1]
                constraints.add(OrConstraint(f'diagonal_right_{v1.name()}', {v1, v2}, '.'))

    return constraints, initial



def horizontal_constraints(v1, v2, size):
    SatAssignments = [{v1: '.', v2: '.'}, {v1: '.', v2: 'S'},
                              {v1: 'S', v2: '.'}, {v1: '<', v2: '>'}]
    i, j = v1.name()

    # Handle vertical constraints based on position
    if i > 0: SatAssignments.extend([{v1: 'v', v2: '.'}, {v1: '.', v2: 'v'}])
    if i < size - 1: SatAssignments.extend([{v1: '^', v2: '.'}, {v1: '.', v2: '^'}])
    if 0 < i < size - 1: SatAssignments.extend([{v1: '.', v2: 'M'}, {v1: 'M', v2: '.'}])

    # Handle horizontal constraints based on position
    if j > 0: SatAssignments.extend([{v1: 'M', v2: '>'}, {v1: '>', v2: '.'}])
    if j < size - 2: SatAssignments.extend([{v1: '<', v2: 'M'}, {v1: '.', v2: '<'}])
    if 0 < j < size - 2: SatAssignments.append({v1: 'M', v2: 'M'})

    return SatAssignments



def vertical_constraints(v1, v2, size):
    SatAssignments = [{v1: '.', v2: '.'}, {v1: '.', v2: 'S'},
                              {v1: 'S', v2: '.'}, {v1: '^', v2: 'v'}]
    i, j = v1.name()

    # Handle vertical constraints based on position
    if i > 0: SatAssignments.extend([{v1: 'M', v2: 'v'}, {v1: 'v', v2: '.'}])
    if i < size - 2: SatAssignments.extend([{v1: '^', v2: 'M'}, {v1: '.', v2: '^'}])
    if 0 < i < size - 2: SatAssignments.append({v1: 'M', v2: 'M'})

    # Handle horizontal constraints based on position
    if j > 0: SatAssignments.extend([{v1: '>', v2: '.'}, {v1: '.', v2: '>'}])
    if j < size - 1: SatAssignments.extend([{v1: '<', v2: '.'}, {v1: '.', v2: '<'}])
    if 0 < j < size - 1: SatAssignments.extend([{v1: '.', v2: 'M'}, {v1: 'M', v2: '.'}])

    return SatAssignments


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

def validate_solution(candidate_solutions, required_ships):
    for candidate in candidate_solutions:
        # Initialize ship count for the candidate
        ship_count = {'s': 0, 'd': 0, 'c': 0, 'b': 0}

        # Iterate over positions and ships in the candidate solution
        for position, ship in candidate.items():
            if ship == 'S':
                ship_count['s'] += 1
            elif ship in {'^', '<'}:
                ship_kind = determine_ship_type(candidate, position)

                # If the ship type is valid, increment the corresponding ship count
                if ship_kind in ship_count:
                    ship_count[ship_kind] += 1
                else:
                    # Invalid ship type encountered, stop processing further for this candidate
                    break
        else:
            # Only return the candidate if the ship counts match exactly with required_ships
            if ship_count == required_ships:
                return candidate

    # If no valid candidate is found, return None (or handle it differently if needed)
    return None

if __name__ == '__main__':
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

    import time
    start = time.time()

    with open(args.inputfile, 'r') as f:
        lines = f.readlines()
    size = len(lines[0].strip())

    variables, rows, cols = initialize_variables(size)

    constraints, initial = initialization(lines[0].strip(), lines[1].strip(), rows, cols)

    initial.update(add_starting_ships(rows, lines))

    ship_constraints = {'s': int(lines[2][0]), 'd': int(lines[2][1]), 'c': int(lines[2][2]), 'b': int(lines[2][3])}
    csp = CSP('battleship', variables, constraints)

    solutions = solve_csp(csp, initial)
    solution = validate_solution(solutions, ship_constraints)
    output_solution(args.outputfile, solution, size)
    end = time.time()
    print("Time:", end-start)