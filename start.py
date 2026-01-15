import sys
import time
from src.bot import IRCBot


def main():
    bot = IRCBot()
    bot.connect()
    bot.send_credentials()
    # bot.join_channels()

    while True:
        msg = bot.receive_message().decode("utf-8")
        if not msg:
            bot.reconnect()

        lines = msg.split("\r\n")
        for line in lines:
            line_split = line.split(":")

            # Handle PING message from server
            if line_split[0].strip() == "PING":
                bot.pong(line_split[1])

            # Extract metadata and handle different server replies
            try:
                metadata = line_split[1]

                # When splitting metadata (with " ")
                # index 0: Who sent message, in case of PRIVMSG should be user
                # index 1: response_code
                # index 2: Target (usually username, if waiting placeholder "*" might be used)

                # This can be IRC-numeric or text (e.g 001 for welcome and PRIVMSG for user messages)
                response_code = metadata.split(" ")[1]

            except IndexError:
                # Ignore index errors genereted by splitting
                # This reduces the hassle of catching every possible format
                # that server can send message with
                continue

            else:
                # Add here how you want to handle different server replies
                if response_code == "001":
                    # Join channels only after receiving welcome ("001")
                    bot.join_channels()
                    bot.query_who("#googcaltop-devel")

                if response_code == "352":
                    # parse WHO response based on RFC2812
                    print("I received WHO response")
                    print(line_split)

            if line.startswith("ERROR"):
                bot.close()
                sys.exit(1)


if __name__ == "__main__":
    main()
