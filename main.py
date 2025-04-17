from uci.uci import UCI
import sys

def main():
    uci = UCI()

    try:
        while True:
            line = sys.stdin.readline().strip()
            if line:
                uci.handle_command(line)
    except EOFError:
        print("Exiting ChessEngine1 UCI")

if __name__ == "__main__":
    print("Engine starting...")
    main()
