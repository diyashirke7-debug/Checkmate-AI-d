import chess

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}
MATE_SCORE = 100_000

class MinimaxAI:
    def __init__(self, depth=2):
        self.depth = max(1, min(int(depth), 4))
        self.nodes = 0

    def evaluate(self, board):
        if board.is_checkmate():
            return -MATE_SCORE if board.turn == chess.WHITE else MATE_SCORE
        if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
            return 0

        score = 0
        for square, piece in board.piece_map().items():
            value = PIECE_VALUES[piece.piece_type]
            file_index = chess.square_file(square)
            rank_index = chess.square_rank(square)
            center_bonus = int(6 - 2 * (abs(3.5 - file_index) + abs(3.5 - rank_index)))
            if piece.piece_type == chess.PAWN:
                advance = rank_index if piece.color == chess.WHITE else 7 - rank_index
                value += advance * 7
            elif piece.piece_type in (chess.KNIGHT, chess.BISHOP):
                value += center_bonus * 3
            score += value if piece.color == chess.WHITE else -value
        return score

    def choose_move(self, board):
        self.nodes = 0
        if board.is_game_over():
            return None, self.evaluate(board)
        maximizing = board.turn == chess.WHITE
        best_move = None
        best_score = float("-inf") if maximizing else float("inf")
        alpha, beta = float("-inf"), float("inf")

        for move in self._ordered_moves(board):
            board.push(move)
            score = self._search(board, self.depth - 1, alpha, beta)
            board.pop()
            if maximizing and score > best_score:
                best_score, best_move = score, move
                alpha = max(alpha, best_score)
            elif not maximizing and score < best_score:
                best_score, best_move = score, move
                beta = min(beta, best_score)
        return best_move, best_score

    def _search(self, board, depth, alpha, beta):
        self.nodes += 1
        if depth <= 0 or board.is_game_over(claim_draw=True):
            return self.evaluate(board)

        maximizing = board.turn == chess.WHITE
        value = float("-inf") if maximizing else float("inf")
        for move in self._ordered_moves(board):
            board.push(move)
            child = self._search(board, depth - 1, alpha, beta)
            board.pop()
            if maximizing:
                value = max(value, child)
                alpha = max(alpha, value)
            else:
                value = min(value, child)
                beta = min(beta, value)
            if alpha >= beta:
                break
        return value

    def _ordered_moves(self, board):
        def priority(move):
            score = 0
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            if board.is_capture(move):
                score += 10_000 + (PIECE_VALUES[victim.piece_type] if victim else 100)
                score -= PIECE_VALUES[attacker.piece_type] if attacker else 0
            if move.promotion:
                score += 8_000 + PIECE_VALUES[move.promotion]
            board.push(move)
            if board.is_check():
                score += 500
            board.pop()
            return score
        return sorted(list(board.legal_moves), key=priority, reverse=True)
