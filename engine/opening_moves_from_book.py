from board.board import ChessBoard
import random

class Book_opening:
    def __init__(self):
        self.opening_book = self._load_opening_book()

    def _load_opening_book(self, path="resources/opening_book.txt"):
        opening_book = {}
        with open(path, "r") as f:
            lines = f.readlines()

        current_fen = None
        for line in lines:
            line = line.strip()
            if line.startswith("pos"):
                current_fen = line[4:]
                opening_book[current_fen] = []
            elif current_fen and line:
                move, freq = line.split()
                opening_book[current_fen].append((move, int(freq)))

        return opening_book

    def opening_move(self, board):
        fen = board.get_fen()
        if fen in self.opening_book:
            moves = self.opening_book[fen]
            move = random.choice(moves)
            return move
        return None


