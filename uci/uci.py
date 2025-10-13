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
        self.move = None
        self.positions_evaluated = 0
        self.foundtranspositions = 0
        self.usedtranspositions = 0
        self.positions_searched = 0
        self.print = True

    def handle_command(self, line):
        #personal use
        if line == "printboard":
            print(self.board.board)
        elif line == "timemove":
            print(self.move_time)
        elif line == "evalpos":
            print(self.positions_evaluated)
        elif line == "transpofound":
            print(self.foundtranspositions)
        elif line == "transpoused":
            print(self.usedtranspositions)
        elif line == "searchpos":
            print(self.positions_searched)
        elif line == "debugmode":
            self.engine.debug = not self.engine.debug
            print(self.engine.debug)
        elif line == "printtree":
            self.engine.print_tree()
        elif line == "testing":
            self.print = False


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
            #self.go()
            self.go_time_management(line)
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
            fen_tokens = line_parts[line_parts.index("fen") + 1: moves_ind]
            fen = " ".join(fen_tokens)
            self.board.set_fen(fen)

        if moves_ind is not None:
            for move in line_parts[moves_ind + 1:]:
                self.board.uci_move(move)

    def go(self):
        start_time = time.time()
        move = self.engine.make_move()
        end_time = time.time()
        self.move_time = end_time - start_time
        self.positions_evaluated = self.engine.nodes_evaluated
        self.foundtranspositions = self.engine.transpositions_found
        self.usedtranspositions = self.engine.transpositions_used
        self.positions_searched = self.engine.nodes_searched
        if move is not None:
            self.board.push(move)
            self.move = move
            print(f"bestmove {self.board.uci(move)}")
        else:
            self.move = None
            print("bestmove 0000")

    def go_time_management(self, line):
        movetime = None
        wtime = btime = winc = binc = None
        depth = None

        parts = line.split()
        for i, token in enumerate(parts):
            if token == "movetime":
                movetime = int(parts[i + 1]) / 1000.0  # ms → s
            elif token == "wtime":
                wtime = int(parts[i + 1]) / 1000.0
            elif token == "btime":
                btime = int(parts[i + 1]) / 1000.0
            elif token == "winc":
                winc = int(parts[i + 1]) / 1000.0
            elif token == "binc":
                binc = int(parts[i + 1]) / 1000.0
            elif token == "depth":
                depth = int(parts[i + 1])
                print(depth)

        # Decide time allocation
        time_limit = self._decide_time(movetime, wtime, btime, winc, binc)

        # set engine with depth + time
        if depth is not None:
            self.engine.depth = depth
            print(self.engine.depth)

        self.engine.time_limit=time_limit


        start_time = time.time()
        best_move = self.engine.make_move()
        end_time = time.time()
        self.move_time = end_time - start_time
        self.positions_evaluated = self.engine.nodes_evaluated
        self.foundtranspositions = self.engine.transpositions_found
        self.usedtranspositions = self.engine.transpositions_used
        self.positions_searched = self.engine.nodes_searched

        if best_move:
            self.board.push(best_move)
            self.move = best_move
            if self.print:
                print(f"bestmove {best_move.uci()}")
        else:
            self.move = None
            if self.print:
                print("bestmove 0000")

    def _decide_time(self, movetime, wtime, btime, winc, binc):
        if movetime:
            return movetime

        total_time = wtime if self.board.board.turn else btime
        increment = winc if self.board.board.turn else binc

        if total_time is None:
            return None

        # Spend 1/50 of remaining time + increment
        time_for_move = total_time / 50.0 + max(0, increment)

        # Cap at 50% of total time at end
        return min(time_for_move, total_time * 0.5)


