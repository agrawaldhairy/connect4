import json

from flask import Flask, render_template, request, session, jsonify
from flask_session import Session
import random
import string
import time
from Board import Board
from MCTSTreeNode import MCTSTreeNode
from Connect4Game import mcts_n

import glog as logger

app = Flask(__name__)

# Secret key for session management
app.secret_key = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Rate limiting
RATE_LIMIT = 100  # requests per minute
rate_limits = {}

# Placeholder for game state and logic
games = {}


def generate_game_id():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_game", methods=["GET", "POST"])
def get_game():
    """
    Retrieves the current game state.

    This function retrieves the game ID from the session and checks if a game with that ID exists in the games dictionary.
    If a game is found, it returns the game ID and the current game board state as a JSON response.
    If no active game is found, it returns an error message as a JSON response.

    Parameters:
    None

    Returns:
    flask.Response: A JSON response containing the game ID and the current game board state if a game is found.
                    If no active game is found, it returns a JSON response with an error message.
    """
    game_id = session.get("game_id")
    if not game_id or game_id not in games:
        return jsonify({"error": "No active game found."}), 400
    return jsonify({"game_id": game_id, "board": games[game_id]["state"]})


@app.route("/new_game", methods=["POST"])
def new_game():
    """
    Handles the creation of a new game.

    Parameters:
    request (flask.Request): The incoming request object containing the game configuration data.

    Returns:
    flask.Response: A JSON response containing the game ID and the initial game board.
    """

    def validate_new_game_data(data):
        """
        Validates the incoming game configuration data.

        Parameters:
        data (dict): The game configuration data.

        Returns:
        tuple: A tuple containing an error message and the HTTP status code if the data is invalid.
        """
        if "rows" not in data:
            return "Invalid number of rows.", 400
        if "cols" not in data:
            return "Invalid number of columns.", 400

    def initialize_new_game(rows_local, cols_local):
        """
        Initializes a new game with the given number of rows and columns.

        Parameters:
        rows_local (int): The number of rows in the game board.
        cols_local (int): The number of columns in the game board.

        Returns:
        tuple: A tuple containing the game ID and the initial game board.
        """
        new_board_local = Board(rows_local, cols_local)
        game_id_local = generate_game_id()
        games[game_id_local] = {"state": new_board_local, "turn": 0}
        session["game_id"] = game_id_local
        session["rows"] = rows_local
        session["cols"] = cols_local
        return game_id_local, new_board_local

    data = request.get_json()
    error = validate_new_game_data(data)
    if error:
        return jsonify({"error": error[0]}), error[1]

    rows = data["rows"]
    cols = data["cols"]
    game_id, new_board = initialize_new_game(rows, cols)

    return jsonify({"game_id": game_id, "board": new_board.get_board().tolist()}), 200


@app.route("/play", methods=["POST"])
def play():
    data = request.get_json()
    GAME_ID = data.get("game_id")
    game_id = session.get("game_id")
    if game_id != GAME_ID:
        return jsonify({"error": "Invalid game ID."}), 400
    ROWS = session["rows"]
    COLS = session["cols"]
    if not game_id or game_id not in games:
        return jsonify({"error": "No active game found."}), 400
    col = data.get("col")

    if col is None or col < 0 or col >= COLS:
        return jsonify({"error": "Invalid column."}), 400

    game = games[game_id]
    board_state = game["state"]
    board = board_state.get_board()
    turn = game["turn"]

    # Add rate limiting
    user_ip = request.remote_addr
    if user_ip not in rate_limits:
        rate_limits[user_ip] = [time.time()]
    else:
        rate_limits[user_ip].append(time.time())
        rate_limits[user_ip] = [t for t in rate_limits[user_ip] if t > time.time() - 60]
        if len(rate_limits[user_ip]) > RATE_LIMIT:
            return (
                jsonify({"error": "Rate limit exceeded. Please try again later."}),
                429,
            )

    # Human player move
    if board[0, col] == 2:
        for i in range(ROWS):
            if board[ROWS - i - 1, col] == 2:
                board[ROWS - i - 1, col] = turn
                break
        game["turn"] ^= 1

    root_node = MCTSTreeNode(board_state, None, game["turn"], 0)

    # Check for win or draw after human move
    if board_state.check_win() != 2 or root_node.check_draw():
        print(board.get_board())
        return (
            jsonify({"board": board.get_board().tolist(), "turn": str(game["turn"]), "winner": str(board_state.check_win())}),
            200,
        )

    # AI move
    best_move = mcts_n(
        root_node, 200
    )  # You can adjust the number of iterations for AI strength
    board = best_move.state
    game["turn"] ^= 1
    game["state"] = board

    return (
        jsonify({"board": board.get_board().tolist(), "turn": game["turn"], "winner": board.check_win()}),
        200,
    )


if __name__ == "__main__":
    app.run(debug=True)
