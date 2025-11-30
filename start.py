import sys
from src.bot import IRCBot

import sys


def main():
    bot = IRCBot()
    bot.connect()
    bot.send_credentials()

    while True:
        msg = bot.receive_message()
        print(msg)

        if not msg:
            bot.reconnect(delay=30)

        lines = msg.split("\r\n")
        for line in lines:
            if line.startswith("ERROR"):
                bot.close()
                sys.exit(1)

            line_parts = line.split(":")
            if line_parts[0].strip() == "PING":
                bot.pong(line_parts[1])


if __name__ == "__main__":
    main()
