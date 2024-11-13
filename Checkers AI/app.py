from flask import Flask, render_template, jsonify, request, session
from state import State, get_possible_moves, get_opp_char, minimax_search
import secrets
import copy

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


def initialize_board():
    """Initialize a new checkers board."""
    return [
        ['.', 'b', '.', 'b', '.', 'b', '.', 'b'],
        ['b', '.', 'b', '.', 'b', '.', 'b', '.'],
        ['.', 'b', '.', 'b', '.', 'b', '.', 'b'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['r', '.', 'r', '.', 'r', '.', 'r', '.'],
        ['.', 'r', '.', 'r', '.', 'r', '.', 'r'],
        ['r', '.', 'r', '.', 'r', '.', 'r', '.']
    ]


def init_game_state():
    """Initialize a new game state."""
    game_state = {
        'board': initialize_board(),
        'current_player': 'b',  # b for black (human player)
        'game_over': False,
        'winner': None,
        'ai_thinking': False
    }
    return game_state

@app.route('/api/get-board', methods=['GET'])
def get_board():
    """API endpoint to get the current board state."""
    if 'game_state' not in session:
        session['game_state'] = init_game_state()
    return jsonify(session['game_state'])


@app.route('/')
def home():
    """Render the main game page."""
    if 'game_state' not in session:
        session['game_state'] = init_game_state()
    return render_template('checkers.html')


@app.route('/api/state')
def get_game_state():
    """Get the current game state."""
    if 'game_state' not in session:
        session['game_state'] = init_game_state()

    game_state = session['game_state']
    state = State(game_state['board'])

    # Get valid moves for current player
    valid_moves = []
    if game_state['current_player'] == 'b' and not game_state['game_over']:
        possible_moves = get_possible_moves(state, 'b')
        valid_moves = [{'from': find_move_source(state.board, move.board),
                        'to': find_move_destination(state.board, move.board)}
                       for move in possible_moves]

    return jsonify({
        'board': game_state['board'],
        'currentPlayer': game_state['current_player'],
        'gameOver': game_state['game_over'],
        'winner': game_state['winner'],
        'validMoves': valid_moves,
        'aiThinking': game_state['ai_thinking']
    })

def find_move_source(old_board, new_board):
    """Find the source position of a move."""
    for i in range(8):
        for j in range(8):
            if old_board[i][j] in ['b', 'B'] and new_board[i][j] == '.':
                return [i, j]
    return None


def find_move_destination(old_board, new_board):
    """Find the destination position of a move."""
    for i in range(8):
        for j in range(8):
            if old_board[i][j] == '.' and new_board[i][j] in ['b', 'B']:
                return [i, j]
    return None


@app.route('/api/move', methods=['POST'])
def make_move():
    """Handle a player's move."""
    if 'game_state' not in session:
        return jsonify({'error': 'No game in progress'}), 400

    game_state = session['game_state']
    if game_state['game_over']:
        return jsonify({'error': 'Game is already over'}), 400

    data = request.json
    from_pos = data.get('from')
    to_pos = data.get('to')

    if not from_pos or not to_pos:
        return jsonify({'error': 'Invalid move format'}), 400

    # Validate and make human move
    state = State(game_state['board'])
    possible_moves = get_possible_moves(state, 'b')

    valid_move = None
    for move in possible_moves:
        if (move.board[to_pos[0]][to_pos[1]] in ['b', 'B'] and
                move.board[from_pos[0]][from_pos[1]] == '.' and
                state.board[from_pos[0]][from_pos[1]] in ['b', 'B'] and
                state.board[to_pos[0]][to_pos[1]] == '.'):
            valid_move = move
            break

    if not valid_move:
        return jsonify({'error': 'Invalid move', 'from': from_pos, 'to': to_pos, 'possible_moves': possible_moves}), 400

    # Update game state with human move
    game_state['board'] = valid_move.board
    game_state['current_player'] = 'r'
    game_state['ai_thinking'] = True
    session.modified = True

    # Make AI move
    state = State(game_state['board'])
    if not state.check_end():
        _, ai_move, _ = minimax_search(
            state, 'r', float("-inf"), float("inf"),
            4, True, 0, use_caching=0, use_ordering=1
        )

        if ai_move:
            game_state['board'] = ai_move.board

        # Check for game end
        state = State(game_state['board'])
        if state.check_end():
            game_state['game_over'] = True
            game_state['winner'] = determine_winner(game_state['board'])
    else:
        game_state['game_over'] = True
        game_state['winner'] = determine_winner(game_state['board'])

    game_state['current_player'] = 'b'
    game_state['ai_thinking'] = False
    session.modified = True

    return jsonify({'success': True, 'board': game_state['board'], 'gameOver': game_state['game_over']})


def determine_winner(board):
    """Determine the winner based on piece count."""
    red_pieces = sum(row.count('r') + row.count('R') for row in board)
    black_pieces = sum(row.count('b') + row.count('B') for row in board)

    if red_pieces > black_pieces:
        return 'red'
    elif black_pieces > red_pieces:
        return 'black'
    else:
        return 'tie'


@app.route('/api/new-game', methods=['POST'])
def new_game():
    """Start a new game."""
    global cache  # Ensure you are using the global cache
    cache = {}  # Clear the cache

    session['game_state'] = init_game_state()
    game_state = session['game_state']

    # If AI is supposed to play first, make the AI move
    if game_state['current_player'] == 'r':
        state = State(game_state['board'])
        _, ai_move, _ = minimax_search(
            state, 'r', float("-inf"), float("inf"),
            4, True, 0, use_caching=0, use_ordering=1
        )

        if ai_move:
            game_state['board'] = ai_move.board

        # Check for game end
        state = State(game_state['board'])
        if state.check_end():
            game_state['game_over'] = True
            game_state['winner'] = determine_winner(game_state['board'])
        else:
            game_state['current_player'] = 'b'

    session.modified = True
    return jsonify({'success': True, 'board': game_state['board'], 'gameOver': game_state['game_over']})

def validate_move(from_pos, to_pos, board):
    """Validate if a move is legal."""
    # Check if positions are within bounds
    if not all(0 <= pos[i] < 8 for pos in [from_pos, to_pos] for i in range(2)):
        return False

    # Check if source has a player's piece and destination is empty
    if board[from_pos[0]][from_pos[1]] not in ['b', 'B']:
        return False
    if board[to_pos[0]][to_pos[1]] != '.':
        return False

    return True


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)