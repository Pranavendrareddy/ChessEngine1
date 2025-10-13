import random
import chess
import os

class Book_opening:
    def __init__(self):
        self.startfen = ''
        self.opening_book = self._load_opening_book()

    def _load_opening_book(self, path="../resources/opening_book.txt"):

        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "../resources/opening_book.txt")

        opening_book = {}


        with open(path) as f:
            lines = f.readlines()

        current_fen = None
        for line in lines:
            line = line.strip()

            if line.startswith("pos"):
                current_fen = line[4:]
                opening_book[current_fen] = []
                if self.startfen == '':
                    self.startfen = current_fen
            elif current_fen and line:
                move, freq = line.split()
                opening_book[current_fen].append((move, int(freq)))

        return opening_book

    def opening_move(self, board):

        fen = board.get_fen()[:-4]
        if fen in self.opening_book:
            moves = self.opening_book[fen]
            move_str, freq = random.choice(moves)
            #move_str, freq = max(moves, key=lambda x: x[1])
            return chess.Move.from_uci(move_str)
        return None


