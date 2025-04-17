from uci.uci import UCI

def main():
    uci = UCI()

    try:
        while True:
            line = input()
            if line:
                uci.handle_command(line.strip())
    except EOFError:
        print("Exiting ChessEngine1 UCI")

if __name__ == "__main__":
    main()
