from board.board import ChessBoard
from engine.minimax import MinimaxEngine
from engine.random import RandomEngine

class UCI:
    def __init__(self):
        self.board = ChessBoard()
        self.engine = MinimaxEngine(self.board)

    def handle_command(self, line):
        if line == "printboard":
            print(self.board.board)
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
        else:
            pass
            #print(f"Unknown command: {line}")

    def set_position(self, line):
        line_parts = line.split()
        moves_ind = None
        if "moves" in line_parts:
            moves_ind = line_parts.index("moves")
        if "startpos" in line_parts:
            self.board.reset()
        elif "fen" in line_parts:
            self.board.set_fen(line_parts[line_parts.index("fen") + 1: moves_ind])

        if moves_ind is not None:
            for move in line_parts[moves_ind + 1:]:
                self.board.uci_move(move)

    def go(self):
        move = self.engine.make_move()
        if move is not None:
            self.board.push(move)
            print(f"bestmove {self.board.uci(move)}")
        else:
            print("bestmove 0000")

