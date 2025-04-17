from board.board import ChessBoard
from engine.random import RandomEngine

class UCI:
    def __init__(self):
        self.board = ChessBoard()
        self.engine = RandomEngine(self.board)

    def handle_command(self, line):
        if line == "uci":
            print("id name Pranav")
            print("id author ChessEngine1")
            print("uciok")
        elif line == "isready":
            print("readyok")
        elif line.startswith("position"):
            self.set_position(line)
        elif line.startswith("go"):
            self.go()
        elif line == "ucinewgame":
            self.board.reset()
        elif line == "quit":
            exit()
        elif line == "d":
            print(self.board)
        else:
            pass

    def set_position(self, line):
        line_parts = line.split()
        moves_ind = None
        if "moves" in line_parts:
            moves_ind = line_parts.index("moves")
        if "startpos" in line_parts:
            self.board.reset()
        elif "fen" in line_parts:
            self.board.set_fen(line_parts[line_parts.index("fen") + 1: moves_ind])

        if moves_ind:
            for move in line_parts[moves_ind + 1:]:
                self.board.uci_move(move)

    def go(self):
        move = self.engine.make_move()
        print(f"bestmove {self.board.uci(move)}")
