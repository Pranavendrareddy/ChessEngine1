import random
from board.board import ChessBoard


def random_move(legal_moves):
    return random.choice(legal_moves)


class RandomEngine:
    def __init__(self, board: ChessBoard):
        self.board = board
        self.nodes_evaluated = 0

    def make_move(self):
        legal_moves = self.board.legal_moves()
        return random_move(legal_moves)
