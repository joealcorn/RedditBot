from RedditBot import bot


if __name__ == '__main__':
    from time import time
    bot.config['START_TIME'] = time()
    bot.run()
