from RedditBot import bot

from time import time, sleep
import signal
import sys


def signal_handler(signal, frame):
    bot.irc.send_command('QUIT :CTRL+C at Console')
    sleep(1)
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    bot.data['START_TIME'] = time()
    bot.run()
