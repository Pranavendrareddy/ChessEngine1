import math
from board.board import ChessBoard
import chess

Piece_values = {chess.PAWN: 100, chess.KNIGHT: 300, chess.BISHOP: 300, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000}

class MinimaxEngine:
    def __init__(self, board: ChessBoard, depth: int=2):
        self.board = board
        self.depth = depth

    def make_move(self):
        best_eval, best_move = self._minimax(self.depth, -math.inf, math.inf, self.board.board.turn)

        return best_move

    def _evaluate(self):
        board = self.board.board
        if board.is_checkmate():
            return -99999 if board.turn else 99999
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        eval = 0
        for piece_type in Piece_values:
            eval += len(board.pieces(piece_type, chess.WHITE)) * Piece_values[piece_type]
            eval -= len(board.pieces(piece_type, chess.BLACK)) * Piece_values[piece_type]
        return eval

    def _minimax(self, depth, alpha, beta, turn):
        board = self.board.board
        if depth == 0 or board.is_game_over():
            return self._evaluate(), None

        best_move = None
        if turn:
            max_eval = -math.inf
            for move in board.legal_moves:
                board.push(move)
                eval, temp_move = self._minimax(depth - 1, alpha, beta, not turn)
                board.pop()
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = math.inf
            for move in board.legal_moves:
                board.push(move)
                eval, temp_move = self._minimax(depth - 1, alpha, beta, not turn)
                board.pop()
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta<=alpha:
                    break
            return min_eval, best_move


