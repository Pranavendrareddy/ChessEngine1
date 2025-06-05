import math
from board.board import ChessBoard
from engine.opening_moves_from_book import Book_opening
from engine.piece_maps import Piece_map
import chess

Piece_values = {chess.PAWN: 100, chess.KNIGHT: 300, chess.BISHOP: 300, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000}

class MinimaxEngine:
    def __init__(self, board: ChessBoard, depth: int=2):
        self.board = board
        self.depth = depth
        self.nodes_evaluated = 0
        self.order_moves = False
        self.ending = False
        self.opening = True
        self.book_opening = Book_opening()

    def make_move(self):
        if self.opening:
            opening_move_choice = self.book_opening.opening_move(self.board)
            if opening_move_choice is None:
                self.opening = False
            else:
                return opening_move_choice



        self.order_moves = True
        self.nodes_evaluated = 0

        best_eval, best_move = self._minimax_pruning(self.depth, -math.inf, math.inf, self.board.board.turn)
        #best_eval, best_move = self._minimax(self.depth, self.board.board.turn)
        return best_move

    def _evaluate(self):
        self.nodes_evaluated += 1
        board = self.board.board
        if board.is_checkmate():
            return -math.inf if board.turn else math.inf
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        non_pawn_pieces = sum(
            len(board.pieces(pt, color))
            for pt in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]
            for color in [chess.WHITE, chess.BLACK]
        )

        if non_pawn_pieces <= 5:
            ending = True


        maps = Piece_map()
        eval = 0
        for piece_type in Piece_values:
            for color in [chess.WHITE, chess.BLACK]:
                maps.gen_map(piece_type, self.ending)
                for square in board.pieces(piece_type, color):
                    pst_value = maps.map[chess.square_file(square) + chess.square_rank(square) * 8]
                    if color == chess.WHITE:
                        eval += pst_value + Piece_values[piece_type]
                    else:
                        eval -= pst_value - Piece_values[piece_type]

        return eval

    def _minimax(self, depth, turn):
        board = self.board.board
        if depth == 0 or board.is_game_over():
            return self._evaluate(), None

        legal_moves_ordered = board.legal_moves
        if self.order_moves:
            legal_moves_ordered = self._move_order()

        best_move = None
        if turn:
            max_eval = -math.inf
            for move in legal_moves_ordered:
                board.push(move)
                eval, temp_move = self._minimax(depth - 1, not turn)
                board.pop()
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = math.inf
            for move in board.legal_moves:
                board.push(move)
                eval, temp_move = self._minimax(depth - 1, not turn)
                board.pop()
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
            return min_eval, best_move

    def _minimax_pruning(self, depth, alpha, beta, turn):
        board = self.board.board
        if depth == 0 or board.is_game_over():
            return self._evaluate(), None

        legal_moves_ordered = board.legal_moves
        if self.order_moves:
            legal_moves_ordered = self._move_order()

        best_move = None
        if turn:
            max_eval = -math.inf
            for move in legal_moves_ordered:
                board.push(move)
                eval, temp_move = self._minimax_pruning(depth - 1, alpha, beta, not turn)
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
                eval, temp_move = self._minimax_pruning(depth - 1, alpha, beta, not turn)
                board.pop()
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta<=alpha:
                    break
            return min_eval, best_move

    def _move_order(self):
        board = self.board.board
        moves = board.legal_moves
        moves_scores = []

        for move in moves:
            move_score_guess = 0
            move_piece = board.piece_type_at(move.from_square)
            move_capture_piece = board.piece_type_at(move.to_square)

            #capture high piece with low piece
            if move_capture_piece is not None:
                is_attacking = move.to_square in board.attacks(move.from_square)
                if is_attacking:
                    move_score_guess = 10*Piece_values[move_capture_piece]- Piece_values[move_piece]

            #promoting pawn
            if move.promotion is not None:
                move_score_guess += Piece_values[move.promotion]

            #move attacking own piece
            if board.is_attacked_by(not board.turn, move.to_square):
                move_score_guess -= Piece_values[move_piece]

            moves_scores.append(move_score_guess)

        sorted_moves = [x for _,x in sorted(zip(moves_scores, moves), key=lambda x: x[0], reverse = True)]
        #sorted_moves_scores = sorted(moves_scores)

        #return zip(sorted_moves, sorted_moves_scores)
        return sorted_moves






