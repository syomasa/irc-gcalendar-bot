from src.bot import IRCBot


def main():
    bot = IRCBot()
    bot.connect()
    bot.send_credentials()

    while True:
        msg = bot.receive_message()

        # Ignore empty messages
        if not msg:
            continue

        print(msg)
        lines = msg.split("\r\n")
        for line in lines:
            # Handle ping-pong from IRC protocol
            line_parts = line.split(":")
            if line_parts[0].strip() == "PING":
                bot.pong(line_parts[1])


if __name__ == "__main__":
    main()
