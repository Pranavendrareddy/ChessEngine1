import chess
from chess.polyglot import zobrist_hash

class TranspositionTable:
    def __init__(self):
        self.table = {}

    def check_pos_in_table(self, board: chess.Board, depth, alpha, beta):
        key = zobrist_hash(board)
        entry = self.table.get(key)
        if entry is None:
            return None

        if entry["depth"] >= depth:
            score, flag, bestmove = entry["score"], entry["flag"], entry["bestmove"]
            loc_alpha, loc_beta = alpha, beta
            if flag == "EXACT":
                return entry
            elif flag == "LOWER" and score > alpha:
                loc_alpha = score
            elif flag == "UPPER" and score < beta:
                loc_beta = score
            if loc_alpha >= loc_beta:
                return entry

        return 0

    def store(self, board: chess.Board, depth, score, flag, bestmove):
        key = zobrist_hash(board)
        self.table[key] = {
            "depth": depth,
            "score": score,
            "flag": flag,
            "bestmove": bestmove
        }
