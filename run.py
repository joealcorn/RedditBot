from RedditBot import bot


if __name__ == '__main__':
    from time import time
    bot.data['START_TIME'] = time()
    bot.run()
