
from RedditBot import bot

import threading

def delayed_join(channel, delay=10):
    def join():
        bot.irc.send_command('JOIN', channel)
    threading.Timer(delay, join).start()

@bot.event('KICK')
def kick(context):
    if context.line['args'][1] != bot.irc.nick: return
    
    kicked_from = context.line['args'][0]
    bot.log(context, ('KICK'), '{0} ({1})'.format(kicked_from, context.line['args'][-1]))
    
    if context.line['user'].lower() in [x.lower() for x in bot.config['REJOIN_KICKERS']]:
        # for channel keys
        for channel in bot.config['CHANNELS']:
            if channel.lower().split(' ')[0] == kicked_from.lower():
                delayed_join(channel)
                return
        delayed_join(kicked_from)

@bot.event('NICK')
def nick(context):
    if context.line['user'] == bot.irc.nick:
        bot.irc.nick = context.line['args'][-1]
