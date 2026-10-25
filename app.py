import os
import uuid
from flask import Flask, jsonify, render_template, request, session
import chess
from game_service import GameService

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-development-key-change-before-deployment")
games = {}

def get_game():
    game_id = session.get("game_id")
    if not game_id or game_id not in games:
        game_id = str(uuid.uuid4())
        games[game_id] = GameService()
        session["game_id"] = game_id
    return games[game_id]

def state_response(game):
    return jsonify(game.state())

@app.get("/")
def index():
    get_game()
    return render_template("index.html")

@app.get("/learn")
def learn():
    return render_template("learn.html")

@app.get("/about")
def about():
    return render_template("about.html")

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "application": "Checkmate AI"})

@app.get("/api/state")
def state():
    return state_response(get_game())

@app.post("/api/new-game")
def new_game():
    data = request.get_json(silent=True) or {}
    color = data.get("color", "white")
    difficulty = data.get("difficulty", "normal")
    if color not in ("white", "black"):
        return jsonify({"error": "Choose white or black."}), 400
    if difficulty not in ("easy", "normal", "hard"):
        return jsonify({"error": "Choose a valid difficulty."}), 400
    game = GameService()
    game.human_color = chess.WHITE if color == "white" else chess.BLACK
    game.depth = {"easy": 1, "normal": 2, "hard": 3}[difficulty]
    game_id = session.get("game_id")
    if not game_id:
        game_id = str(uuid.uuid4())
        session["game_id"] = game_id
    games[game_id] = game
    if game.human_color == chess.BLACK:
        game.ai_move()
    return state_response(game)

@app.post("/api/move")
def move():
    data = request.get_json(silent=True) or {}
    game = get_game()
    ok, message = game.human_move(data.get("move", ""))
    if not ok:
        return jsonify({"error": message, **game.state()}), 400
    if not game.board.is_game_over() and game.board.turn != game.human_color:
        game.ai_move()
    return state_response(game)

@app.post("/api/hint")
def hint():
    game = get_game()
    if game.board.is_game_over():
        return jsonify({"error": "The game has ended."}), 400
    if game.board.turn != game.human_color:
        return jsonify({"error": "Wait for your turn."}), 400
    return jsonify(game.hint())

@app.post("/api/undo")
def undo():
    game = get_game()
    game.undo_turn()
    return state_response(game)

@app.post("/api/restart")
def restart():
    game = get_game()
    game.restart()
    if game.human_color == chess.BLACK:
        game.ai_move()
    return state_response(game)

@app.post("/api/resign")
def resign():
    game = get_game()
    game.resigned = True
    return state_response(game)

@app.post("/api/load-position")
def load_position():
    data = request.get_json(silent=True) or {}
    try:
        board = chess.Board(data.get("fen", ""))
        if not board.is_valid():
            raise ValueError
        game = get_game()
        game.load_position(board)
        return state_response(game)
    except (ValueError, TypeError):
        return jsonify({"error": "Please provide a valid chess FEN position."}), 400

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=False)
