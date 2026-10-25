import chess
from minimax import MinimaxAI

class GameService:
    def __init__(self):
        self.board = chess.Board()
        self.history = []
        self.human_color = chess.WHITE
        self.depth = 2
        self.resigned = False
        self.last_evaluation = 0
        self.last_nodes = 0
        self.last_ai_move = None

    def state(self):
        return {
            "fen": self.board.fen(),
            "turn": "white" if self.board.turn == chess.WHITE else "black",
            "human_color": "white" if self.human_color == chess.WHITE else "black",
            "difficulty": {1: "easy", 2: "normal", 3: "hard"}.get(self.depth, "hard"),
            "moves": [{"san": san, "uci": uci} for san, uci in self.history],
            "status": self.status_text(),
            "game_over": self.board.is_game_over() or self.resigned,
            "check": self.board.is_check(),
            "last_move": self.history[-1][1] if self.history else None,
            "evaluation": round(self.last_evaluation / 100, 2),
            "nodes": self.last_nodes,
            "ai_move": self.last_ai_move,
            "legal_moves": [move.uci() for move in self.board.legal_moves] if not self.board.is_game_over() else [],
        }

    def status_text(self):
        if self.resigned:
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            return f"Resignation — {winner} wins."
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            return f"Checkmate — {winner} wins."
        if self.board.is_stalemate():
            return "Draw — stalemate."
        if self.board.is_insufficient_material():
            return "Draw — insufficient material."
        if self.board.can_claim_threefold_repetition():
            return "Draw may be claimed by threefold repetition."
        if self.board.can_claim_fifty_moves():
            return "Draw may be claimed by the fifty-move rule."
        return ("White" if self.board.turn == chess.WHITE else "Black") + (" to move — check!" if self.board.is_check() else " to move.")

    def human_move(self, uci):
        if self.resigned or self.board.is_game_over():
            return False, "The game has ended."
        if self.board.turn != self.human_color:
            return False, "Please wait for the AI's turn."
        try:
            move = chess.Move.from_uci(uci)
        except (ValueError, TypeError):
            return False, "That move format is invalid."
        if move not in self.board.legal_moves:
            return False, "That is not a legal move."
        san = self.board.san(move)
        self.board.push(move)
        self.history.append((san, move.uci()))
        return True, "Move accepted."

    def ai_move(self):
        if self.board.is_game_over() or self.resigned:
            return None
        ai = MinimaxAI(self.depth)
        move, score = ai.choose_move(self.board)
        if move is None:
            return None
        san = self.board.san(move)
        self.board.push(move)
        self.history.append((san, move.uci()))
        self.last_evaluation = score
        self.last_nodes = ai.nodes
        self.last_ai_move = move.uci()
        return move.uci()

    def hint(self):
        ai = MinimaxAI(self.depth)
        move, score = ai.choose_move(self.board)
        return {
            "move": move.uci() if move else None,
            "san": self.board.san(move) if move else None,
            "evaluation": round(score / 100, 2),
            "nodes": ai.nodes,
            "explanation": "This suggestion comes from Minimax searching legal continuations and comparing resulting positions."
        }

    def undo_turn(self):
        if not self.history:
            self.resigned = False
            return
        count = 2 if len(self.history) >= 2 else 1
        for _ in range(count):
            self.board.pop()
            self.history.pop()
        self.resigned = False
        self.last_ai_move = self.history[-1][1] if self.history else None

    def restart(self):
        self.board = chess.Board()
        self.history = []
        self.resigned = False
        self.last_evaluation = 0
        self.last_nodes = 0
        self.last_ai_move = None

    def load_position(self, board):
        self.board = board.copy()
        self.history = []
        self.resigned = False
        self.last_evaluation = 0
        self.last_nodes = 0
        self.last_ai_move = None
