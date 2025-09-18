import chess

class TranspositionTable:
    def __init__(self):
        self.table = {}

    def check_pos_in_table(self, board:chess.Board, depth, alpha, beta):
        zobrist_hash_key = board._transposition_key()
        if zobrist_hash_key not in self.table:
            return None

        tt_entry = self.table[zobrist_hash_key]
        if tt_entry["depth"] >= depth:
            score, flag, bestmove = tt_entry["score"], tt_entry["flag"], tt_entry["bestmove"]
            if flag == "EXACT":
                return tt_entry
            elif flag == "LOWER" and score > alpha:
                alpha = score
            elif flag == "UPPER" and score < beta:
                beta = score
            if alpha >= beta:
                return tt_entry

        return None

    def store(self, board:chess.Board, depth, score, flag, bestmove):

        zobrist_hash_key = board._transposition_key()
        self.table[zobrist_hash_key] = {
            "depth": depth,
            "score": score,
            "flag": flag,
            "bestmove": bestmove
        }