from dotenv import dotenv_values


class IRCBot:
    def __init__(self, proxy=False):
        self.config = dotenv_values(".env")

        self.nick = self.config["NICK"]
        self.server = self.config["SERVER"]
        self.port = self.config["PORT"]
        self.ident = self.config["IDENT"]
        self.realname = self.config["REALNAME"]

    def connect(self):
        """Connects to server specified in .env"""
        pass

    def send_msg(self):
        """Sends message to the channel. Only works after bot has joined to a channel"""
        pass

    def change_topic(self):
        """Changes channel topic. Requires bot to have permissions to do so"""
        pass

    def join_channel(self):
        """Joins channel specified in .env"""
        pass
