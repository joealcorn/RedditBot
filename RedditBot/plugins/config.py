
from RedditBot import bot, utils

import yaml

blacklist = ['REGEX', 'IGNORE', 'EVENTS', 'CHANNELS', 'PLUGINS']

def save_config():
    with open('bot_config.yml', 'w') as f:
        f.write(yaml.dump(dict((key, value) for key, value in bot.config.iteritems() if
            not (key.upper() in blacklist) and
            isinstance(value, list) and
            (not bot.h_config.has_key(key) or bot.h_config[key] != value))))

def load_config():
    with open('bot_config.yml', 'r') as f:
        for key, value in yaml.load(f.read()).iteritems():
            if not key in bot.config:
                bot.config[key] = value
            elif isinstance(bot.config[key], list):
                bot.config[key] = list(set(bot.config[key] + value))

load_config()

@bot.command
def config(context):
    if not utils.isadmin(context.line['prefix'], bot):
        return
    cmd, key, arg = str(context.args).split(' ', 3)
    cmd = cmd.lower()
    if not (cmd in ['add', 'remove']):
        return
    if key.upper() in blacklist or (key in bot.config and not isinstance(bot.config[key], list)):
        return
    if not key in bot.config:
        bot.config[key] = []
    if cmd == 'add' and not arg in bot.config[key]:
        bot.config[key].append(arg)
    elif cmd == 'remove' and (not bot.h_config.has_key(key) or not (arg in bot.h_config[key])):
        bot.config[key].remove(arg)
        if len(bot.config[key]) == 0 and not bot.h_config.has_key(key):
            del bot.config[key]
    save_config()

