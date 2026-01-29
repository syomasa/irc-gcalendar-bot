from src.runner import BotRunner
from src.client import IRCClient


def main():
    client = IRCClient()
    runner = BotRunner(client)
    runner.run_forever()


if __name__ == "__main__":
    # main()
    main()
