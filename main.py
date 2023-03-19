import sys

from music_bot import start_bot


def main():
    token = sys.argv[-1]
    start_bot(token)


if __name__ == "__main__":
    main()
