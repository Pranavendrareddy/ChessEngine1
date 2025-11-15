from engine.minimax import MinimaxEngine
from board.board import ChessBoard
import chess
import time

engine1_tl = 1000
engine2_tl = 1000

puzzle_paths = ["../resources/eigenmann_rapid.epd", "../resources/wacnew_arasan.epd", "../resources/iq4_arasan.epd"]
fen_path = "../resources/match_fens.txt"

def parse_epd_line(line):
    if not line.strip() or "bm" not in line:
        return None, None, None
    parts = line.split("bm")
    fen = parts[0].strip()
    best_move = parts[1].split(";")[0].strip()
    id = parts[1].split(";")[1].strip()

    return fen, best_move, id

def play_game(engine_white, engine_black, fen: str="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
    board_orig = ChessBoard()
    engine_white.reset_engine(time_reset = False)
    engine_black.reset_engine(time_reset = False)
    engine_white.board = board_orig
    engine_black.board = board_orig
    moves_made = 0
    board_orig.set_fen(fen)

    print("Starting game...")
    while not board_orig.board.is_game_over():

        start_time = time.time()
        if board_orig.board.turn:  # White to move
            move = engine_white.make_move()
        else:
            move = engine_black.make_move()

        end_time = time.time()

        if move is None:
            break

        color_str = "White" if board_orig.board.turn else "Black"
        print(f"Move {moves_made + 1}: {move}, Color: {color_str}, Time: {end_time - start_time}")

        board_orig.push(move)
        moves_made += 1

    result = board_orig.board.result()  # '1-0', '0-1', or '*'=draw
    print(f"Result: {result}")
    print(board_orig.board)
    return result, moves_made

def tournament_fen(engine_type1, engine_type2, path, game_limit: int=10):
    results = {"engine1": 0, "engine2": 0, "draw": 0}

    with open(path) as file:
        lines = file.readlines()

    game_counter = 0

    new_lines = []

    for line in lines:
        new_lines.append(line)
        new_lines.append(line)

    for line in new_lines:
        fen = line
        if fen is None:
            continue

        if game_counter % 2 == 0:
            engine_white = engine_type1
            engine_black = engine_type2
        else:
            engine_white = engine_type2
            engine_black = engine_type1

        print(f"Starting game {game_counter}, {id}...")
        result, moves = play_game(engine_white, engine_black, fen=fen)

        if result == '1-0':
            if game_counter % 2 == 0:
                results["engine1"] += 1
                print("Winner: engine1")
            else:
                results["engine2"] += 1
                print("Winner: engine2")
        elif result == '0-1':
            if game_counter % 2 == 0:
                results["engine2"] += 1
                print("Winner: engine2")
            else:
                results["engine1"] += 1
                print("Winner: engine1")
        else:
            results["draw"] += 1

        game_counter+=1

        if game_counter >= 2*game_limit:
            break

    return results

def tournament_epd(engine_type1, engine_type2, path, game_limit: int=10):
    results = {"engine1": 0, "engine2": 0, "draw": 0}

    with open(path) as file:
        lines = file.readlines()

    game_counter = 0

    new_lines = []

    for line in lines:
        new_lines.append(line)
        new_lines.append(line)

    for line in new_lines:
        fen, _, id = parse_epd_line(line)
        if fen is None:
            continue

        if game_counter % 2 == 0:
            engine_white = engine_type1
            engine_black = engine_type2
        else:
            engine_white = engine_type2
            engine_black = engine_type1

        print(f"Starting game {game_counter}, {id}...")
        result, moves = play_game(engine_white, engine_black, fen=fen)

        if result == '1-0':
            if game_counter % 2 == 0:
                results["engine1"] += 1
                print("Winner: engine1")
            else:
                results["engine2"] += 1
                print("Winner: engine2")
        elif result == '0-1':
            if game_counter % 2 == 0:
                results["engine2"] += 1
                print("Winner: engine2")
            else:
                results["engine1"] += 1
                print("Winner: engine1")
        else:
            results["draw"] += 1

        game_counter+=1

        if game_counter >= 2*game_limit:
            break

    return results

def tournament(engine_type1, engine_type2, games: int=10):
    results = {"engine1": 0, "engine2": 0, "draw": 0}

    for i in range(games):
        if i % 2 == 0:
            engine_white = engine_type1
            engine_black = engine_type2
        else:
            engine_white = engine_type2
            engine_black = engine_type1

        print(f"Starting game {i}...")
        result, moves = play_game(engine_white, engine_black)

        if result == '1-0':
            if i % 2 == 0:
                results["engine1"] += 1
                print("Winner: engine1")
            else:
                results["engine2"] += 1
                print("Winner: engine2")
        elif result == '0-1':
            if i % 2 == 0:
                results["engine2"] += 1
                print("Winner: engine2")
            else:
                results["engine1"] += 1
                print("Winner: engine1")
        else:
            results["draw"] += 1

    return results

if __name__ == '__main__':
    board = ChessBoard()
    engine_type1 = MinimaxEngine(board, engine_type=2, quiescence=False, move_ordering=False)
    engine_type2 = MinimaxEngine(board, engine_type=2, quiescence=False, move_ordering=False)
    engine_type1.time_limit = engine1_tl/1000
    engine_type2.time_limit = engine2_tl/1000

    #results = tournament(engine_type1, engine_type2, games=1)
    #print(results)

    results = tournament_fen(engine_type1, engine_type2, fen_path, 3)
    print(results)
    results = tournament_epd(engine_type1, engine_type2, puzzle_paths[1], 2)
    print(results)

