from board.board import ChessBoard
from engine.minimax import MinimaxEngine
from engine.random import RandomEngine
import time

class UCI:
    def __init__(self):
        self.board = ChessBoard()
        self.engine = MinimaxEngine(self.board)
        #for the most recent move
        self.move_time = 0
        self.positions_evaluated = 0

    def handle_command(self, line):
        #personal use
        if line == "printboard":
            print(self.board.board)
        elif line == "movetime":
            print(self.move_time)
        elif line == "evalpos":
            print(self.positions_evaluated)

        #uci
        if line == "uci":
            print("id name ChessEngine1")
            print("id author Pranav")
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
        start_time = time.time()
        move = self.engine.make_move()
        end_time = time.time()
        self.move_time = end_time - start_time
        self.positions_evaluated = self.engine.nodes_evaluated
        if move is not None:
            self.board.push(move)
            print(f"bestmove {self.board.uci(move)}")
        else:
            print("bestmove 0000")

