import math
from board.board import ChessBoard
from engine.opening_moves_from_book import Book_opening
from engine.piece_maps import Piece_map
from engine.transposition import TranspositionTable
from engine.move_ordering import MoveOrder
from engine.repetition import RepetitionTable
import chess
import time
import sys

Piece_values = {chess.PAWN: 100, chess.KNIGHT: 300, chess.BISHOP: 300, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000}
MATE_SCORE = 999999
MAX_DEPTH = 32
DEFAULT_DEPTH = 4
NODE_TIME_CHECK = 2048
MAX_TT_SIZE_MB = 64
TIME_ABORT = object()

class MinimaxEngine:
    def __init__(self, board: ChessBoard, depth: int=DEFAULT_DEPTH, time_limit: float=None, engine_type: int=0, move_ordering: bool=True, iterative_deepening: bool=True, quiescence: bool = True, opening: bool=True):
        self.board = board

        self.engine_type = engine_type
        self.quiescence = quiescence
        self.iterative_deepening = iterative_deepening

        self.depth = depth
        self.original_depth = depth
        self.call_depth = depth

        self.nodes_evaluated = 0
        self.nodes_searched = 0
        self.transpositions_found = 0
        self.transpositions_used = 0

        self.order_moves = move_ordering
        self.ending = False
        self.opening = True

        self.pv_move = None
        self.time_limit = time_limit
        self.start_time = None
        self.stop_search = False

        self.book_opening = Book_opening()
        self.ttable = TranspositionTable()
        self.repetition_table = RepetitionTable()

        self.move_order = MoveOrder()

        self.maps = {}
        for piece_type in Piece_values:
            self.maps[piece_type] = {}  # first level: piece_type
            self.maps[piece_type][chess.WHITE] = {}  # second level: color
            self.maps[piece_type][chess.BLACK] = {}  # second level: color

            # White
            self.maps[piece_type][chess.WHITE][False] = Piece_map()
            self.maps[piece_type][chess.WHITE][False].gen_map(piece_type, False, chess.WHITE)
            self.maps[piece_type][chess.WHITE][True] = Piece_map()
            self.maps[piece_type][chess.WHITE][True].gen_map(piece_type, True, chess.WHITE)

            # Black
            self.maps[piece_type][chess.BLACK][False] = Piece_map()
            self.maps[piece_type][chess.BLACK][False].gen_map(piece_type, False, chess.BLACK)
            self.maps[piece_type][chess.BLACK][True] = Piece_map()
            self.maps[piece_type][chess.BLACK][True].gen_map(piece_type, True, chess.BLACK)

        self.debug = False         # turn on to record search tree
        self._tree_lines = []      # collected debug lines


    def make_move(self):
        if self.opening:
            opening_move_choice = self.book_opening.opening_move(self.board)
            if opening_move_choice is None:
                self.opening = False
            else:
                return opening_move_choice


        self.nodes_evaluated = 0
        self.nodes_searched = 0
        self.transpositions_found = 0
        self.transpositions_used = 0
        self.stop_search = False

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
            self.depth = self.original_depth + 4
        elif non_pawn_pieces <= 2:
            self.ending = True
            self.depth = self.original_depth + 2
        elif non_pawn_pieces <= 5:
            self.ending = True
            self.depth = self.original_depth + 1

        #iterative deepening and PV
        best_move = None
        best_eval = -math.inf if self.board.board.turn else math.inf
        self.start_time = time.time()

        #clear repetition table
        self.repetition_table.positions.clear()
        self.repetition_table.add_position(self.board.board)

        #clear transposition table
        #if len(self.ttable.table)>=100000:
        if self.tt_too_large():
            self.ttable.table.clear()

        #clear killer moves table
        #self.move_order.clear_killer_moves()

        if self.time_limit is not None:  # if limit exists, bot should think as much as possible
            self.depth = max(self.depth, MAX_DEPTH)

        if self.iterative_deepening:

            for current_depth in range(1, self.depth+1):

                if self._time_exceeded() or self.stop_search:
                    break

                self.call_depth = current_depth
                eval, move = None, None

                #eval,move = self._minimax(self.depth, self.board.board.turn)
                #eval, move = self._minimax_pruning(current_depth, -math.inf, math.inf, self.board.board.turn)
                #eval, move = self._minimax_pruning_tt(current_depth, -math.inf, math.inf, self.board.board.turn)
                if self.engine_type == 0:
                    eval, move = self._minimax_pruning_tt(current_depth, -math.inf, math.inf, self.board.board.turn)
                elif self.engine_type == 1:
                    eval, move = self._minimax_pruning(current_depth, -math.inf, math.inf, self.board.board.turn)
                elif self.engine_type == 2:
                    eval, move = self._minimax(current_depth, self.board.board.turn)

                #if self.stop_search:
                    #break #normalement pas mais evaluation imprécise


                if move is not None:
                    best_eval = eval
                    best_move = move
                    #print(move)
                    self.pv_move = move


        else:
            if self.engine_type == 0:
                eval, best_move = self._minimax_pruning_tt(self.depth, -math.inf, math.inf, self.board.board.turn)
            elif self.engine_type == 1:
                eval, best_move = self._minimax_pruning(self.depth, -math.inf, math.inf, self.board.board.turn)
            elif self.engine_type == 2:
                eval, best_move = self._minimax(self.depth, self.board.board.turn)


        if self.depth != DEFAULT_DEPTH:
            self.depth = DEFAULT_DEPTH
        return best_move

    def _time_exceeded(self):
        if self.time_limit is None:
            return False
        if (time.time() - self.start_time) >= self.time_limit:
            self.stop_search = True
            return True
        return False

    def _evaluate(self, ply_from_root):
        self.nodes_evaluated += 1
        board = self.board.board
        if board.is_checkmate():
            mate_score = MATE_SCORE - ply_from_root
            return -mate_score if board.turn else mate_score #inf doesn't work, because gives up, can give + depth for faster mate privileges
        if board.is_stalemate() or board.is_insufficient_material():
            return 0


        # initialiser une fois les maps pour accélérer
        eval = 0

        for piece_type in Piece_values:
            for color in [chess.WHITE, chess.BLACK]:
                for square in board.pieces(piece_type, color):
                    pst_value = self.maps[piece_type][color][self.ending].map[chess.square_file(square) + (7-chess.square_rank(square)) * 8]
                    #print(chess.square_file(square), (7-chess.square_rank(square))*8)
                    if color == chess.WHITE:
                        eval += pst_value + Piece_values[piece_type]
                        #print(pst_value, Piece_values[piece_type], "wh")
                    else:
                        eval -= pst_value + Piece_values[piece_type]
                        #print(pst_value, Piece_values[piece_type], "bl")

        return eval

    def _quiescence_search(self, alpha, beta, turn, ply_from_root):

        # if pv_line is None:
        #     pv_line = []

        if self.stop_search:
            return TIME_ABORT

        self.nodes_searched += 1

        if self.nodes_searched % NODE_TIME_CHECK == 0 and self._time_exceeded():
            self.stop_search = True
            self.nodes_searched -= 1
            return TIME_ABORT

        board = self.board.board

        stand_pat = self._evaluate(ply_from_root)

        best_eval = stand_pat

        if not self.quiescence:
            return best_eval

        if turn:
            if best_eval >= beta:
                return best_eval
            elif best_eval > alpha:
                alpha = best_eval

        else:
            if best_eval <= alpha:
                return best_eval
            elif best_eval < beta:
                beta = best_eval


        order_moves = self.move_order.order_quiescence_moves(board, Piece_values)

        # if self.debug:
        #     indent = "  " * (self.original_depth + 1)
        #     self._tree_lines.append(f"{indent}QUIET depth standpat={stand_pat} PV={' '.join(pv_line)}")

        if turn:

            for move in order_moves:
                if self.stop_search:
                    return TIME_ABORT
                board.push(move)
                score = self._quiescence_search(alpha, beta, not turn, ply_from_root+1)
                board.pop()
                if score is TIME_ABORT:
                    self.stop_search = True
                    break

                if score >= beta:
                    return score
                elif score > alpha:
                    alpha = score
                best_eval = max(best_eval, score)
        else:
            for move in order_moves:
                board.push(move)
                score = self._quiescence_search(alpha, beta, not turn, ply_from_root+1)
                board.pop()
                if score is TIME_ABORT:
                    self.stop_search = True
                    break

                if score <= alpha:
                    return score
                elif score < beta:
                    beta = score
                best_eval = min(best_eval, score)

        return best_eval


    def _minimax(self, depth, turn):
        if self.stop_search:
            return TIME_ABORT, None

        self.nodes_searched += 1
        if self.nodes_searched % NODE_TIME_CHECK == 0 and self._time_exceeded():
            self.stop_search = True
            self.nodes_searched -= 1
            return TIME_ABORT, None

        board = self.board.board

        #if self.repetition_table.is_repetition(board):
            #return 0, None #put after next if check

        if depth == 0 or board.is_game_over() or board.is_repetition(3):
            return self._evaluate(self.call_depth-depth), None

        legal_moves_ordered = board.legal_moves
        if self.order_moves:
            legal_moves_ordered = self.move_order.order_moves(board, self.pv_move, Piece_values, depth)

        best_move = None
        if turn:
            max_eval = -math.inf
            for move in legal_moves_ordered:
                board.push(move)
                self.repetition_table.add_position(board)
                eval, temp_move = self._minimax(depth - 1, not turn)
                self.repetition_table.remove_position(board)
                board.pop()
                if eval is TIME_ABORT:
                    self.stop_search = True
                    break
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
            if max_eval == -math.inf:
                return TIME_ABORT, None
            return max_eval, best_move
        else:
            min_eval = math.inf
            for move in legal_moves_ordered:
                board.push(move)
                self.repetition_table.add_position(board)
                eval, temp_move = self._minimax(depth - 1, not turn)
                self.repetition_table.remove_position(board)
                board.pop()
                if eval is TIME_ABORT:
                    self.stop_search = True
                    break
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
            if min_eval == math.inf:
                return TIME_ABORT, None
            return min_eval, best_move

    def _minimax_pruning(self, depth, alpha, beta, turn):
        if self.stop_search:
            return TIME_ABORT, None

        self.nodes_searched += 1
        if self.nodes_searched % NODE_TIME_CHECK == 0 and self._time_exceeded():
            self.stop_search = True
            self.nodes_searched -= 1
            return TIME_ABORT, None

        board = self.board.board

        #print("Depth:", depth, "alpha:", alpha, "beta:", beta, "turn:", board.turn)

        #if self.repetition_table.is_repetition(board):
            #return 0, None
        if board.is_game_over() or board.is_repetition(3):
            return self._evaluate(self.call_depth-depth), None
        if depth == 0:
            return self._quiescence_search(alpha, beta, turn, self.call_depth-depth), None
            #return self._evaluate(self.call_depth-depth), None

        legal_moves_ordered = board.legal_moves
        if self.order_moves:
            legal_moves_ordered = self.move_order.order_moves(board, self.pv_move, Piece_values, depth)

        best_move = None
        if turn:
            max_eval = -math.inf
            for move in legal_moves_ordered:
                board.push(move)
                #self.repetition_table.add_position(board)
                #print("move: ", move, board.turn)
                eval, temp_move = self._minimax_pruning(depth - 1, alpha, beta, not turn)
                #self.repetition_table.remove_position(board)
                board.pop()
                if eval is TIME_ABORT:
                    self.stop_search = True
                    break
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    self.move_order.store_killer_move(depth, move, board)
                    break
            #print("max_eval:", max_eval, "best_move:", best_move)
            if max_eval == -math.inf:
                return TIME_ABORT, None
            return max_eval, best_move
        else:
            min_eval = math.inf
            for move in legal_moves_ordered:
                board.push(move)
                #self.repetition_table.add_position(board)
                #print("move: ", move, board.turn)
                eval, temp_move = self._minimax_pruning(depth - 1, alpha, beta, not turn)
                #self.repetition_table.remove_position(board)
                board.pop()
                if eval is TIME_ABORT:
                    self.stop_search = True
                    break

                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta<=alpha:
                    self.move_order.store_killer_move(depth, move, board)
                    break

            #print("min_eval:", min_eval, "best_move:", best_move)
            if min_eval == math.inf:
                return TIME_ABORT, None
            return min_eval, best_move


    def _minimax_pruning_tt(self, depth, alpha, beta, turn):
        # if pv_line is None:
        #     pv_line = []

        if self.stop_search:
            return TIME_ABORT, None

        self.nodes_searched += 1
        if self.nodes_searched % NODE_TIME_CHECK == 0 and self._time_exceeded():
            self.stop_search = True
            self.nodes_searched -= 1
            return TIME_ABORT, None

        board = self.board.board

        #print("Depth:", depth, "alpha:", alpha, "beta:", beta, "turn:", board.turn)

        if self.repetition_table.is_repetition(board) or board.is_repetition(3):
            return 0, None
        if board.is_game_over():
            return self._evaluate(self.call_depth - depth), None
        if depth == 0:
            return self._quiescence_search(alpha, beta, turn, self.call_depth - depth), None
            # return self._evaluate(self.call_depth-depth), None

        # if self.debug:
        #     indent = "  " * (self.original_depth - depth)
        #     self._tree_lines.append(
        #         f"{indent}D={depth} turn={'W' if turn else 'B'} alpha={alpha} beta={beta} PV={' '.join(pv_line)}")

        alpha_original = alpha
        beta_original = beta
        tt_entry = self.ttable.check_pos_in_table(board, depth, alpha, beta)
        if tt_entry is not None:  # no entry
            self.transpositions_found += 1
            if tt_entry != 0:  # entry useful
                self.transpositions_used += 1
                return tt_entry["score"], tt_entry["bestmove"]

        legal_moves_ordered = board.legal_moves
        if self.order_moves:
            legal_moves_ordered = self.move_order.order_moves(board, self.pv_move, Piece_values, depth)

        best_move = None
        cur_eval = None
        if turn:
            max_eval = -math.inf
            for move in legal_moves_ordered:
                if self.stop_search:
                    return TIME_ABORT, None
                board.push(move)
                self.repetition_table.add_position(board)
                #print("move: ", move, board.turn)

                eval, temp_move = self._minimax_pruning_tt(depth - 1, alpha, beta, not turn)

                self.repetition_table.remove_position(board)
                board.pop()

                if eval is TIME_ABORT:
                    self.stop_search = True
                    break

                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    self.move_order.store_killer_move(depth, move, board)
                    break
            #print("min_eval:", max_eval, "best_move:", best_move)
            if max_eval == -math.inf:
                return TIME_ABORT, None
            cur_eval = max_eval
        else:
            min_eval = math.inf
            for move in legal_moves_ordered:
                if self.stop_search:
                    return TIME_ABORT, None
                board.push(move)
                self.repetition_table.add_position(board)
                #print("move: ", move, board.turn)

                eval, temp_move = self._minimax_pruning_tt(depth - 1, alpha, beta, not turn)

                self.repetition_table.remove_position(board)
                board.pop()

                if eval is TIME_ABORT:
                    self.stop_search = True
                    break

                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    self.move_order.store_killer_move(depth, move, board)
                    break
            #print("min_eval:", min_eval, "best_move:", best_move)
            if min_eval == math.inf:
                return TIME_ABORT, None
            cur_eval = min_eval

        flag = "EXACT"
        if cur_eval <= alpha_original:
            flag = "UPPER"
        elif cur_eval >= beta_original:
            flag = "LOWER"

        self.ttable.store(board, depth, cur_eval, flag, best_move)

        # if self.debug:
        #     indent = "  " * (self.original_depth - depth)
        #     bm = best_move.uci() if best_move else None
        #     self._tree_lines.append(f"{indent}=> score={cur_eval} best={bm} PV={' '.join(pv_line)}")

        return cur_eval, best_move

    def tt_too_large(self):
        size_bytes = sum(sys.getsizeof(k) + sys.getsizeof(v) for k, v in self.ttable.table.items())
        size_mb = size_bytes / (1024 * 1024)
        return size_mb > MAX_TT_SIZE_MB

    def print_tree(self):
        #print("Debug Trees")
        for line in self._tree_lines:
            print(line)

    def reset_engine(self, time_reset: bool = True):

        self.nodes_evaluated = 0
        self.nodes_searched = 0
        self.transpositions_found = 0
        self.transpositions_used = 0

        self.ending = False
        self.opening = True

        self.pv_move = None
        if time_reset:
            self.time_limit = None
        self.start_time = None
        self.stop_search = False

        self.repetition_table.positions.clear()

        self.ttable.table.clear()

        self.move_order.clear_killer_moves()