import chess
from chess.polyglot import zobrist_hash
import random

board = chess.Board()
print(board)

# Convert generator to list
moves = list(board.legal_moves)
print(moves)

# Pick a random legal move
move = random.choice(moves)
board.push(move)

# Show new board and zobrist hash
print(board)
print("Zobrist hash:", zobrist_hash(board))
