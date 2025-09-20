import math
from board.board import ChessBoard
from engine.opening_moves_from_book import Book_opening
from engine.piece_maps import Piece_map
from engine.transposition import TranspositionTable
import chess
import time

Piece_values = {chess.PAWN: 100, chess.KNIGHT: 300, chess.BISHOP: 300, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000}

class MinimaxEngine:
    def __init__(self, board: ChessBoard, depth: int=3, time_limit: float=None):
        self.board = board
        self.depth = depth
        self.olddepth = depth
        self.nodes_evaluated = 0
        self.transpositions_found = 0
        self.transpositions_used = 0
        self.order_moves = True
        self.ending = False
        self.opening = True
        self.pv_move = None
        self.time_limit = time_limit
        self.start_time = None
        self.book_opening = Book_opening()
        self.ttable = TranspositionTable()
        self.maps = {}
        for piece_type in Piece_values:
            self.maps[piece_type] = {}
            self.maps[piece_type][False] = Piece_map()
            self.maps[piece_type][False].gen_map(piece_type, False)
            self.maps[piece_type][True] = Piece_map()
            self.maps[piece_type][True].gen_map(piece_type, True)

    def make_move(self):
        if self.opening:
            opening_move_choice = self.book_opening.opening_move(self.board)
            if opening_move_choice is None:
                self.opening = False
            else:
                return opening_move_choice


        self.nodes_evaluated = 0
        self.transpositions_found = 0

        board = self.board.board
        non_pawn_mask = (
                board.pieces(chess.KNIGHT, chess.WHITE) |
                board.pieces(chess.BISHOP, chess.WHITE) |
                board.pieces(chess.ROOK, chess.WHITE) |
                board.pieces(chess.QUEEN, chess.WHITE) |
                board.pieces(chess.KNIGHT, chess.BLACK) |
                board.pieces(chess.BISHOP, chess.BLACK) |
                board.pieces(chess.ROOK, chess.BLACK) |
                board.pieces(chess.QUEEN, chess.BLACK)
        )
        non_pawn_pieces = bin(non_pawn_mask).count("1")

        if non_pawn_pieces <= 1:
            self.ending = True
            self.depth = self.olddepth + 4
        elif non_pawn_pieces <= 2:
            self.ending = True
            self.depth = self.olddepth + 2
        elif non_pawn_pieces <= 5:
            self.ending = True
            self.depth = self.olddepth + 1

        #iterative deepening and PV
        best_move = None
        best_eval = -math.inf if self.board.board.turn else math.inf
        self.start_time = time.time()

        for current_depth in range(1, self.depth + 1):

            if self._time_exceeded():
                break
            #eval,move = self._minimax(self.depth, self.board.board.turn)
            #eval, move = self._minimax_pruning(current_depth, -math.inf, math.inf, self.board.board.turn)
            eval, move = self._minimax_pruning_tt(current_depth, -math.inf, math.inf, self.board.board.turn)

            if move is not None:
                best_eval = eval
                best_move = move
                self.pv_move = move



        return best_move

    def _time_exceeded(self):
        if self.time_limit is None:
            return False
        return (time.time() - self.start_time) >= self.time_limit

    def _evaluate(self):
        self.nodes_evaluated += 1
        board = self.board.board
        if board.is_checkmate():
            return -99999 if board.turn else 99999 #inf doesn't work, because gives up
        if board.is_stalemate() or board.is_insufficient_material():
            return 0


        # initialiser une fois les maps pour accélérer
        eval = 0

        for piece_type in Piece_values:
            for color in [chess.WHITE, chess.BLACK]:
                for square in board.pieces(piece_type, color):
                    pst_value = self.maps[piece_type][self.ending].map[chess.square_file(square) + chess.square_rank(square) * 8]
                    if color == chess.WHITE:
                        eval += pst_value + Piece_values[piece_type]
                    else:
                        eval -= pst_value + Piece_values[piece_type]

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

    def _minimax_pruning_tt(self, depth, alpha, beta, turn):

        board = self.board.board
        if depth == 0 or board.is_game_over():
            return self._evaluate(), None

        legal_moves_ordered = board.legal_moves
        if self.order_moves:
            legal_moves_ordered = self._move_order()


        alpha_original = alpha
        beta_original = beta
        tt_entry = self.ttable.check_pos_in_table(board, depth, alpha, beta)
        if tt_entry is not None:
            self.transpositions_found += 1
            if tt_entry != 0:
                self.transpositions_used += 1
                return tt_entry["score"], tt_entry["bestmove"]

        best_move = None
        cur_eval = None
        if turn:
            max_eval = -math.inf
            for move in legal_moves_ordered:
                board.push(move)
                eval, temp_move = self._minimax_pruning_tt(depth - 1, alpha, beta, not turn)
                board.pop()
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            cur_eval = max_eval
        else:
            min_eval = math.inf
            for move in board.legal_moves:
                board.push(move)
                eval, temp_move = self._minimax_pruning_tt(depth - 1, alpha, beta, not turn)
                board.pop()
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta<=alpha:
                    break
            cur_eval = min_eval

        flag = "EXACT"
        if cur_eval <= alpha_original:
            flag = "UPPER"
        elif cur_eval >= beta_original:
            flag = "LOWER"


        self.ttable.store(board, depth, cur_eval, flag, best_move)

        return cur_eval, best_move

    def _move_order(self):
        board = self.board.board
        moves = board.legal_moves
        moves_scores = []

        for move in moves:
            move_score_guess = 0
            move_piece = board.piece_type_at(move.from_square)
            move_capture_piece = board.piece_type_at(move.to_square)

            #principle variation first
            if self.pv_move is not None and move==self.pv_move:
                move_score_guess += 100000

            #capture high piece with low piece
            if move_capture_piece is not None:
                is_attacking = move.to_square in board.attacks(move.from_square)
                if is_attacking:
                    move_score_guess = 10*Piece_values[move_capture_piece]- Piece_values[move_piece]

            #promoting pawn
            if move.promotion is not None:
                move_score_guess += Piece_values[move.promotion]

            #move where piece will be attacked
            if board.is_attacked_by(not board.turn, move.to_square):
                move_score_guess -= Piece_values[move_piece]

            moves_scores.append(move_score_guess)

        sorted_moves = [x for _,x in sorted(zip(moves_scores, moves), key=lambda x: x[0], reverse = True)]
        #sorted_moves_scores = sorted(moves_scores)

        #return zip(sorted_moves, sorted_moves_scores)
        return sorted_moves






