from uci.uci import UCI
import chess

puzzle_paths = ["../resources/eigenmann_rapid.epd", "../resources/wacnew_arasan.epd", "../resources/iq4_arasan.epd"]

MAX_TIME = 1000

def parse_epd_line(line):
    if not line.strip() or "bm" not in line:
        return None, None, None
    parts = line.split("bm")
    fen = parts[0].strip()
    best_move = parts[1].split(";")[0].strip()
    id = parts[1].split(";")[1].strip()

    return fen, best_move, id

def test_bot_on_file(uci, puzzle_file):
    print(f"=== Testing {puzzle_file} ===")
    solved = 0
    total = 0

    board=chess.Board()

    with open(puzzle_file) as file:
        lines = file.readlines()


    for line in lines:
        fen, best_move, id = parse_epd_line(line)
        if fen is None:
            continue
        bot_move = None

        print(f"{total+1}: {id}, bm: {best_move},", end=" ")
        uci.handle_command(f"position fen {fen}")
        board.set_fen(fen)

        uci.handle_command(f"go movetime {MAX_TIME}")
        #uci.handle_command("go")

        bot_move = board.san(uci.move)
        print(bot_move, end = " ")
        print(f"time: {uci.move_time}", end = " ")
        #print(f"Nodes eval={uci.positions_evaluated}, Transp found={uci.foundtranspositions}, Transp used={uci.usedtranspositions}, Positions searched={uci.positions_searched}\n")

        if bot_move in best_move.split(" "):
            solved += 1
            print("correct")
        else:
            print("wrong")

        total += 1
    print(f"solved: {solved} total: {total}")






if __name__ == "__main__":
    uci = UCI()
    uci.handle_command("uci")
    uci.handle_command("testing")

    for path in puzzle_paths:
        test_bot_on_file(uci, path)




