import random
from board.board import ChessBoard


class RandomEngine:
    def __init__(self, board: ChessBoard):
        self.board = board

    def make_move(self):
        legal_moves = self.board.legal_moves()
        return self.random_move(legal_moves)

    def random_move(self, legal_moves):
        return random.choice(legal_moves)
