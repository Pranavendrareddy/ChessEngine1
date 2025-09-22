import chess
from chess.polyglot import zobrist_hash


class RepetitionTable:
    def __init__(self):
        self.positions = {}

    def add_position(self, board):
        key = zobrist_hash(board)
        self.positions[key] = self.positions.get(key, 0) + 1

    def remove_position(self, board):
        key = zobrist_hash(board)
        self.positions[key] = self.positions.get(key, 0) - 1
        if self.positions[key] < 0:
            self.positions.pop(key)

    def is_repetition(self, board):
        key = zobrist_hash(board)
        return self.positions.get(key, 0) >= 3