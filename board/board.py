import chess

class ChessBoard:
    def __init__(self):
        self.board = chess.Board()

    # Tout cela n'est pas forcément utile, la libraire a tout
    def set_fen(self, fen):
        self.board.set_fen(fen) 

    def get_fen(self):
        return self.board.fen()

    def legal_moves(self):
        return list(self.board.legal_moves)

    def push(self, move):
        self.board.push(move)

    def pop(self):
        self.board.pop()

    def is_legal(self, move):
        return self.board.is_legal(move)

    def uci_move(self, move_uci):
        move = chess.Move.from_uci(move_uci)
        if move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False

    def uci(self, move):
        move_uci = move.uci()
        return move_uci

    def reset(self):
        self.board.set_fen(chess.STARTING_FEN)



