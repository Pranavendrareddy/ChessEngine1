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

King = [
    -80, -70, -70, -70, -70, -70, -70, -80,
    -60, -60, -60, -60, -60, -60, -60, -60,
    -40, -50, -50, -60, -60, -50, -50, -40,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, 20, -5, -5, -5, -5, 20, 20,
    20, 30, 10, 0, 0, 10, 30, 20
]

King_flipped = King[::-1]  # reverse the list
print(King_flipped)

